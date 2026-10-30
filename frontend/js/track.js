// Application tracking: status, history timeline and certificate download.
(function () {
  const e = Layout.escapeHtml;
  const form = document.getElementById("track-form");
  const input = document.getElementById("ref");
  const result = document.getElementById("result");
  const POLL_MS = 10000;

  const STATUS_STEPS = [
    { status: "SUBMITTED", label: "Submitted", hint: "Application received" },
    { status: "APPROVED", label: "Approved", hint: "Verified by issuing officer" },
    { status: "CERTIFICATE_GENERATED", label: "Certificate Ready", hint: "PDF generated" },
  ];
  const STATUS_BADGE = {
    SUBMITTED: "bg-amber-100 text-amber-800",
    APPROVED: "bg-blue-100 text-blue-800",
    CERTIFICATE_GENERATED: "bg-green-100 text-green-800",
  };

  let current = null; // last loaded application
  let pollTimer = null;

  function progressHtml(status) {
    const reached = STATUS_STEPS.findIndex((s) => s.status === status);
    return `
      <ol class="grid grid-cols-3 gap-2 mt-6">
        ${STATUS_STEPS.map((step, i) => {
          const done = i <= reached;
          return `
            <li class="text-center">
              <div class="h-2 rounded ${done ? "bg-green-600" : "bg-slate-200"}"></div>
              <div class="mt-2 text-sm font-semibold ${done ? "text-green-800" : "text-slate-400"}">${step.label}</div>
              <div class="text-xs text-slate-500">${step.hint}</div>
            </li>`;
        }).join("")}
      </ol>`;
  }

  function historyHtml(history) {
    return `
      <ol class="relative border-l-2 border-slate-200 ml-2 space-y-5">
        ${history.slice().reverse().map((h) => `
          <li class="ml-5">
            <span class="absolute -left-[7px] w-3 h-3 rounded-full" style="background: var(--saffron)"></span>
            <div class="text-sm font-semibold">${e(h.status.replace(/_/g, " "))}</div>
            <div class="text-xs text-slate-500">${formatDateTime(h.changed_at)}</div>
            <div class="text-sm text-slate-700">${e(h.note)}</div>
          </li>`).join("")}
      </ol>`;
  }

  function downloadHtml(app) {
    if (app.certificate_ready) {
      return `
        <section class="card p-6 mt-6 border-green-300 bg-green-50">
          <h2 class="font-bold text-lg text-green-800">Certificate Ready for Download</h2>
          <p class="text-sm text-green-900 mt-1">
            Certificate No. <span class="font-mono font-semibold">${e(app.certificate ? app.certificate.certificate_number : "")}</span>
            · Issued by ${e(app.certificate ? app.certificate.officer_name : "")}, ${e(app.certificate ? app.certificate.officer_designation : "")}
          </p>
          <a href="${Api.certificateUrl(app.reference)}" class="btn btn-accent mt-4">Download Certificate (PDF)</a>
        </section>`;
    }
    return `
      <section class="card p-6 mt-6">
        <h2 class="font-bold text-lg" style="color: var(--navy)">Certificate Download</h2>
        <p class="text-sm text-slate-600 mt-1">Your certificate can be downloaded once the application is approved.</p>
        <p class="text-xs bg-blue-50 border border-blue-200 text-blue-900 rounded p-3 mt-3">
          Your application is under verification by the concerned office. This page updates automatically.
        </p>
      </section>`;
  }

  function render(app) {
    const docs = app.documents.length
      ? app.documents.map((d) => `<li>${e(d.doc_type)} – <span class="text-slate-500">${e(d.original_name)}</span></li>`).join("")
      : '<li class="text-slate-500">No documents uploaded.</li>';

    result.innerHTML = `
      <section class="card p-6">
        <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div>
            <div class="text-xs uppercase tracking-wide text-slate-500">Reference Number</div>
            <div class="text-xl font-mono font-bold break-all" style="color: var(--navy)">${e(app.reference)}</div>
          </div>
          <span class="px-3 py-1 rounded-full text-sm font-semibold self-start ${STATUS_BADGE[app.status] || "bg-slate-100"}">${e(app.status.replace(/_/g, " "))}</span>
        </div>
        <dl class="grid sm:grid-cols-2 gap-x-6 gap-y-2 text-sm mt-5">
          <div><dt class="text-slate-500 inline">Certificate:</dt> <dd class="inline font-medium">${e(app.certificate_name)}</dd></div>
          <div><dt class="text-slate-500 inline">Applicant:</dt> <dd class="inline font-medium">${e(app.full_name)}</dd></div>
          <div><dt class="text-slate-500 inline">Submitted:</dt> <dd class="inline font-medium">${formatDateTime(app.created_at)}</dd></div>
          <div><dt class="text-slate-500 inline">District:</dt> <dd class="inline font-medium">${e(app.district)}</dd></div>
        </dl>
        ${progressHtml(app.status)}
      </section>

      <div class="grid gap-6 md:grid-cols-2 mt-6">
        <section class="card p-6">
          <h2 class="font-bold text-lg mb-4" style="color: var(--navy)">Status History</h2>
          ${historyHtml(app.history)}
        </section>
        <section class="card p-6">
          <h2 class="font-bold text-lg mb-4" style="color: var(--navy)">Uploaded Documents</h2>
          <ul class="text-sm space-y-1 list-disc pl-5">${docs}</ul>
          ${app.payment ? `<p class="text-sm mt-4"><span class="text-slate-500">Fee paid:</span> <span class="font-mono">${e(app.payment.transaction_ref)}</span> (${formatCurrency(app.payment.amount)})</p>` : ""}
        </section>
      </div>

      ${downloadHtml(app)}`;
  }

  function schedulePoll() {
    clearTimeout(pollTimer);
    if (current && !current.certificate_ready) {
      pollTimer = setTimeout(poll, POLL_MS);
    }
  }

  async function poll() {
    try {
      const status = await Api.getStatus(current.reference);
      if (status.status !== current.status) {
        // Skip the toast if the layout's background watcher already showed it.
        const known = Session.myApplications().find((a) => a.reference === current.reference);
        if (!known || known.status !== status.status) {
          Layout.notifyStatusChange(current.reference, status.status);
        }
        Session.updateApplicationStatus(current.reference, status.status);
        current = await Api.getApplication(current.reference);
        render(current);
      }
    } catch (err) {
      // Keep polling on transient errors.
    }
    schedulePoll();
  }

  async function lookup(ref) {
    clearTimeout(pollTimer);
    result.innerHTML = '<p class="text-slate-500">Loading…</p>';
    try {
      current = await Api.getApplication(ref);
      history.replaceState(null, "", "track.html?ref=" + encodeURIComponent(current.reference));
      render(current);
      schedulePoll();
    } catch (err) {
      current = null;
      result.innerHTML = `<div class="card p-6 text-red-700">${e(err.message)}</div>`;
    }
  }

  function renderMyApplications() {
    const apps = Session.myApplications();
    if (!apps.length) return;
    document.getElementById("my-apps").innerHTML =
      '<span class="text-slate-500">Your recent applications: </span>' +
      apps.slice(0, 5)
        .map((a) => `<button type="button" class="underline font-mono mr-3" data-ref="${e(a.reference)}">${e(a.reference)}</button>`)
        .join("");
    document.querySelectorAll("#my-apps [data-ref]").forEach((btn) => {
      btn.onclick = () => {
        input.value = btn.dataset.ref;
        lookup(btn.dataset.ref);
      };
    });
  }

  // The layout's background watcher already toasts; just refresh the view.
  document.addEventListener("application-status", (event) => {
    if (current && event.detail.reference === current.reference) lookup(current.reference);
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!Validation.validateAll(form)) return;
    lookup(input.value.trim().toUpperCase());
  });

  renderMyApplications();
  const initial = queryParam("ref");
  if (initial) {
    input.value = initial;
    lookup(initial);
  }
})();
