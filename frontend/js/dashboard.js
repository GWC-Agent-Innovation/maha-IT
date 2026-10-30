// My Account: the logged-in citizen's applications, issued certificates and payment history.
(function () {
  if (!Session.requireLogin()) return;

  const e = Layout.escapeHtml;
  const citizen = Session.current();
  const REFRESH_MS = 15000;

  const STATUS_BADGE = {
    SUBMITTED: ["Under Verification", "bg-amber-100 text-amber-800"],
    APPROVED: ["Approved", "bg-blue-100 text-blue-800"],
    CERTIFICATE_GENERATED: ["Certificate Issued", "bg-green-100 text-green-800"],
  };
  const PAYMENT_BADGE = {
    SUCCESS: ["Success", "bg-green-100 text-green-800"],
    FAILED: ["Failed", "bg-red-100 text-red-800"],
  };

  function badge([label, cls]) {
    return `<span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold whitespace-nowrap ${cls}">${label}</span>`;
  }

  function emptyState(message) {
    return `<div class="card p-8 text-center text-slate-500">
      <p>${message}</p>
      <a href="index.html#services" class="btn btn-primary mt-4">Browse Certificate Services</a>
    </div>`;
  }

  function table(headers, rows) {
    return `<div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-left text-slate-600">
          <tr>${headers.map((h) => `<th class="px-4 py-3 font-semibold whitespace-nowrap">${h}</th>`).join("")}</tr>
        </thead>
        <tbody class="divide-y divide-slate-100">${rows.join("")}</tbody>
      </table>
    </div>`;
  }

  function downloadLink(url) {
    return `<a href="${url}" class="inline-flex items-center gap-1 font-semibold whitespace-nowrap" style="color: var(--saffron-dark)">
      <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3v12m0 0-4-4m4 4 4-4M5 21h14"/></svg>Download PDF</a>`;
  }

  function renderApplications(apps) {
    const target = document.getElementById("tab-applications");
    if (!apps.length) {
      target.innerHTML = emptyState("You have not submitted any applications yet.");
      return;
    }
    target.innerHTML = table(
      ["Application No.", "Service", "Submitted On", "Status", "Action"],
      apps.map((a) => `
        <tr>
          <td class="px-4 py-3 font-mono whitespace-nowrap">${e(a.reference)}</td>
          <td class="px-4 py-3">${e(a.certificate_name)}</td>
          <td class="px-4 py-3 whitespace-nowrap">${formatDateTime(a.created_at)}</td>
          <td class="px-4 py-3">${badge(STATUS_BADGE[a.status] || [a.status, "bg-slate-100"])}</td>
          <td class="px-4 py-3 whitespace-nowrap">
            ${a.download_url ? downloadLink(a.download_url) : `<a href="track.html?ref=${encodeURIComponent(a.reference)}" class="font-semibold underline" style="color: var(--navy)">Track</a>`}
          </td>
        </tr>`)
    );
  }

  function renderCertificates(apps) {
    const target = document.getElementById("tab-certificates");
    const issued = apps.filter((a) => a.download_url);
    if (!issued.length) {
      target.innerHTML = emptyState("No certificates have been issued to you yet.");
      return;
    }
    target.innerHTML = `<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">${issued.map((a) => `
      <article class="card p-5 flex flex-col">
        <div class="flex items-start justify-between gap-3">
          <h3 class="font-bold" style="color: var(--navy)">${e(a.certificate_name)}</h3>
          ${badge(STATUS_BADGE.CERTIFICATE_GENERATED)}
        </div>
        <dl class="text-sm mt-3 space-y-1 flex-1">
          <div><dt class="inline text-slate-500">Certificate No.:</dt> <dd class="inline font-mono">${e(a.certificate_number)}</dd></div>
          <div><dt class="inline text-slate-500">Application No.:</dt> <dd class="inline font-mono">${e(a.reference)}</dd></div>
          <div><dt class="inline text-slate-500">Issued On:</dt> <dd class="inline">${formatDateTime(a.issued_at)}</dd></div>
          <div><dt class="inline text-slate-500">Validity:</dt> <dd class="inline font-semibold ${a.validity.startsWith("Expired") ? "text-red-700" : "text-green-700"}">${e(a.validity)}</dd></div>
        </dl>
        <a href="${a.download_url}" class="btn btn-accent mt-4">Download Certificate</a>
      </article>`).join("")}</div>`;
  }

  function renderPayments(payments) {
    const target = document.getElementById("tab-payments");
    if (!payments.length) {
      target.innerHTML = emptyState("No payments found.");
      return;
    }
    target.innerHTML = table(
      ["Date", "Transaction ID", "Service", "Amount", "Mode", "Status", "Application No."],
      payments.map((p) => `
        <tr>
          <td class="px-4 py-3 whitespace-nowrap">${formatDateTime(p.paid_at)}</td>
          <td class="px-4 py-3 font-mono whitespace-nowrap">${e(p.transaction_ref)}</td>
          <td class="px-4 py-3">${e(p.certificate_name)}</td>
          <td class="px-4 py-3 whitespace-nowrap">${formatCurrency(p.amount)}</td>
          <td class="px-4 py-3 whitespace-nowrap">${e(p.method)}</td>
          <td class="px-4 py-3">${badge(PAYMENT_BADGE[p.status] || [p.status, "bg-slate-100"])}</td>
          <td class="px-4 py-3 font-mono whitespace-nowrap">${p.application_reference
            ? `<a href="track.html?ref=${encodeURIComponent(p.application_reference)}" class="underline" style="color: var(--navy)">${e(p.application_reference)}</a>`
            : '<span class="text-slate-400">—</span>'}</td>
        </tr>`)
    );
  }

  function renderSummary(apps, payments) {
    const paid = payments.filter((p) => p.status === "SUCCESS").reduce((sum, p) => sum + p.amount, 0);
    document.getElementById("sum-apps").textContent = apps.length;
    document.getElementById("sum-certs").textContent = apps.filter((a) => a.download_url).length;
    document.getElementById("sum-progress").textContent = apps.filter((a) => !a.download_url).length;
    document.getElementById("sum-paid").textContent = formatCurrency(paid);
  }

  function selectTab(name) {
    document.querySelectorAll(".tab").forEach((tab) => {
      const active = tab.dataset.tab === name;
      tab.setAttribute("aria-selected", active);
      tab.className = "tab px-4 py-2 text-sm font-semibold border-b-2 -mb-px " +
        (active ? "border-orange-500 text-blue-900" : "border-transparent text-slate-500 hover:text-slate-700");
    });
    document.querySelectorAll(".tab-panel").forEach((panel) => {
      panel.classList.toggle("hidden", panel.id !== "tab-" + name);
    });
    history.replaceState(null, "", "#" + name);
  }

  async function load() {
    try {
      const [apps, payments] = await Promise.all([
        Api.myApplications(citizen.mobile),
        Api.myPayments(citizen.mobile),
      ]);
      renderSummary(apps, payments);
      renderApplications(apps);
      renderCertificates(apps);
      renderPayments(payments);
    } catch (err) {
      document.getElementById("tab-applications").innerHTML =
        `<div class="card p-6 text-red-700">${e(err.message)}</div>`;
    }
  }

  document.getElementById("account-line").textContent =
    `${citizen.name} · Mobile ${citizen.mobile.replace(/^(\d{2})\d{4}(\d{4})$/, "$1XXXX$2")}`;
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => selectTab(tab.dataset.tab));
  });
  const initialTab = location.hash.slice(1);
  selectTab(["applications", "certificates", "payments"].includes(initialTab) ? initialTab : "applications");
  load();
  // Status-change toasts come from the layout's background watcher; this just refreshes the tables.
  setInterval(load, REFRESH_MS);
})();
