// Payment receipt and submission confirmation, showing the application (tracking) number.
(function () {
  const target = document.getElementById("confirmation");
  const e = Layout.escapeHtml;

  function copyButton(id, label) {
    return `<button type="button" id="${id}" class="inline-flex items-center gap-1 text-sm font-semibold px-3 py-1.5 rounded border border-blue-900 text-blue-900 bg-white hover:bg-blue-50 print:hidden">
      <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
      ${label}</button>`;
  }

  async function copy(text, button) {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      // Fallback for browsers that block the async clipboard API.
      const area = document.createElement("textarea");
      area.value = text;
      document.body.appendChild(area);
      area.select();
      const ok = document.execCommand("copy");
      area.remove();
      if (!ok) {
        Toast.show("Could not copy. Please note the number manually.", "warning");
        return;
      }
    }
    const original = button.innerHTML;
    button.textContent = "✓ Copied";
    Toast.show("Copied to clipboard.", "info", 2500);
    setTimeout(() => (button.innerHTML = original), 2000);
  }

  function row(label, value, mono) {
    return `<div class="flex justify-between gap-4 py-2 border-b border-slate-100">
      <dt class="text-slate-500">${label}</dt>
      <dd class="font-medium text-right ${mono ? "font-mono" : ""}">${value}</dd>
    </div>`;
  }

  async function load() {
    const ref = queryParam("ref");
    if (!ref) {
      target.innerHTML = '<p class="text-red-700 p-8">No application reference provided.</p>';
      return;
    }
    try {
      const app = await Api.getApplication(ref);
      const pay = app.payment;
      document.title = "Payment Receipt – " + app.reference + " | Citizen Certificate Portal";

      target.innerHTML = `
        <div class="bg-green-700 text-white px-6 py-5 flex items-center gap-4">
          <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center text-2xl shrink-0">✓</div>
          <div>
            <h1 class="text-xl font-bold">Payment Successful</h1>
            <p class="text-green-100 text-sm">Your application for ${e(app.certificate_name)} has been submitted.</p>
          </div>
        </div>

        <div class="p-6">
          <div class="rounded-lg border-2 p-5 text-center" style="border-color: var(--saffron); background: #fff8f1">
            <div class="text-xs uppercase tracking-wide text-slate-600 font-semibold">Application Number</div>
            <div id="app-number" class="text-2xl sm:text-3xl font-mono font-bold mt-1 break-all" style="color: var(--navy)">${e(app.reference)}</div>
            <p class="text-xs text-slate-600 mt-1">Use this number to track your application.</p>
            <div class="mt-3">${copyButton("copy-ref", "Copy Application Number")}</div>
          </div>

          <h2 class="font-bold mt-6 mb-1" style="color: var(--navy)">Payment Details</h2>
          <dl class="text-sm">
            ${pay ? `
            <div class="flex justify-between gap-4 py-2 border-b border-slate-100 items-center">
              <dt class="text-slate-500">Transaction ID</dt>
              <dd class="text-right flex items-center gap-2 justify-end flex-wrap">
                <span class="font-mono font-medium">${e(pay.transaction_ref)}</span>
                <button type="button" id="copy-txn" class="text-xs underline print:hidden" style="color: var(--navy)">Copy</button>
              </dd>
            </div>
            ${row("Amount Paid", formatCurrency(pay.amount))}
            ${row("Payment Mode", e(pay.method))}
            ${row("Payment Date", formatDateTime(pay.paid_at))}
            ${row("Payment Status", '<span class="text-green-700 font-semibold">Success</span>')}` : ""}
          </dl>

          <h2 class="font-bold mt-6 mb-1" style="color: var(--navy)">Application Details</h2>
          <dl class="text-sm">
            ${row("Applicant Name", e(app.full_name))}
            ${row("Service", e(app.certificate_name))}
            ${row("District / Taluka", e(app.district + " / " + app.taluka))}
            ${row("Submitted On", formatDateTime(app.created_at))}
            ${row("Documents Uploaded", app.documents.length)}
            ${row("Current Status", e(app.status.replace(/_/g, " ")))}
          </dl>

          <p class="text-sm bg-blue-50 border border-blue-200 text-blue-900 rounded p-3 mt-6">
            Your application has been forwarded to the concerned office for verification.
            You will be notified here when the certificate is issued. You can also check the status from My Account.
          </p>

          <div class="mt-6 flex flex-col sm:flex-row gap-3 justify-center print:hidden">
            <a href="track.html?ref=${encodeURIComponent(app.reference)}" class="btn btn-primary">Track Application</a>
            <button type="button" id="print-btn" class="btn btn-secondary">Print Receipt</button>
            <a href="dashboard.html" class="btn btn-secondary">My Account</a>
          </div>
        </div>`;

      const copyRef = document.getElementById("copy-ref");
      copyRef.onclick = () => copy(app.reference, copyRef);
      const copyTxn = document.getElementById("copy-txn");
      if (copyTxn) copyTxn.onclick = () => copy(pay.transaction_ref, copyTxn);
      document.getElementById("print-btn").onclick = () => window.print();
    } catch (err) {
      target.innerHTML = `<p class="text-red-700 p-8">${e(err.message)}</p>`;
    }
  }

  load();
})();
