// Certificate details page: description, eligibility, documents and fee.
(function () {
  const target = document.getElementById("detail");
  const e = Layout.escapeHtml;

  function listHtml(items) {
    return items.map((item) => `<li>${e(item)}</li>`).join("");
  }

  function render(cert) {
    document.title = cert.name + " | Citizen Certificate Portal";
    document.getElementById("crumb").textContent = cert.name;
    target.innerHTML = `
      <div class="card overflow-hidden">
        <div class="p-6 text-white" style="background: var(--navy)">
          <h1 class="text-2xl font-bold">${e(cert.name)}</h1>
          <p class="mt-2 text-blue-100">${e(cert.description)}</p>
        </div>
        <div class="p-6 grid gap-6 md:grid-cols-2">
          <section>
            <h2 class="font-bold text-lg mb-2" style="color: var(--navy)">Eligibility</h2>
            <ul class="list-disc pl-5 space-y-1 text-sm">${listHtml(cert.eligibility)}</ul>
          </section>
          <section>
            <h2 class="font-bold text-lg mb-2" style="color: var(--navy)">Required Documents</h2>
            <ul class="list-disc pl-5 space-y-1 text-sm">${listHtml(cert.documents)}</ul>
            <p class="text-xs text-slate-500 mt-2">Accepted formats: PDF, JPG, PNG (max 5 MB each).</p>
          </section>
          <section>
            <h2 class="font-bold text-lg mb-2" style="color: var(--navy)">Fee</h2>
            <p class="text-2xl font-bold">${formatCurrency(cert.fee)}</p>
            <p class="text-xs text-slate-500">Payable online at the time of application.</p>
          </section>
          <section>
            <h2 class="font-bold text-lg mb-2" style="color: var(--navy)">Processing Time</h2>
            <p class="text-sm">${e(cert.processing_time)}</p>
          </section>
          <section class="md:col-span-2">
            <h2 class="font-bold text-lg mb-2" style="color: var(--navy)">Validity</h2>
            <p class="text-sm font-semibold">${e(cert.validity)}</p>
            <p class="text-sm text-slate-600 mt-1">${e(cert.reapply_note)}</p>
          </section>
        </div>
        <div class="px-6 pb-6">
          <div class="flex flex-wrap gap-3">
            <a href="apply.html?id=${encodeURIComponent(cert.id)}" class="btn btn-accent">Apply Now</a>
            <a href="index.html#services" class="btn btn-secondary">Back to Services</a>
          </div>
        </div>
      </div>`;
  }

  async function load() {
    const id = queryParam("id");
    if (!id) {
      target.innerHTML = '<p class="text-red-700">No certificate selected.</p>';
      return;
    }
    try {
      render(await Api.getCertificate(id));
    } catch (err) {
      target.innerHTML = `<p class="text-red-700">${e(err.message)}</p>
        <a href="index.html#services" class="btn btn-secondary mt-4">Back to Services</a>`;
    }
  }

  load();
})();
