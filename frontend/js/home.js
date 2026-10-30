// Landing page: certificate catalogue, search and quick tracking.
(function () {
  const grid = document.getElementById("service-grid");
  const search = document.getElementById("service-search");
  const noResults = document.getElementById("no-results");
  let certificates = [];

  const ICONS = {
    income: "₹",
    caste: "◆",
    domicile: "⌂",
    residence: "▣",
    "non-creamy-layer": "✓",
  };

  function cardHtml(cert) {
    const e = Layout.escapeHtml;
    return `
      <article class="card p-5 flex flex-col">
        <div class="flex items-center gap-3">
          <div class="w-11 h-11 rounded-full flex items-center justify-center text-white text-lg font-bold" style="background: var(--saffron)">${ICONS[cert.id] || "★"}</div>
          <h3 class="font-bold text-lg" style="color: var(--navy)">${e(cert.name)}</h3>
        </div>
        <p class="text-sm text-slate-600 mt-3 flex-1">${e(cert.description)}</p>
        <dl class="text-xs text-slate-500 mt-4 space-y-1">
          <div class="flex justify-between"><dt>Fee</dt><dd class="font-semibold text-slate-700">${formatCurrency(cert.fee)}</dd></div>
          <div class="flex justify-between"><dt>Documents</dt><dd class="font-semibold text-slate-700">${cert.documents.length} required</dd></div>
        </dl>
        <div class="mt-4 flex gap-2">
          <a href="certificate.html?id=${encodeURIComponent(cert.id)}" class="btn btn-secondary flex-1 !px-3">View Details</a>
          <a href="apply.html?id=${encodeURIComponent(cert.id)}" class="btn btn-primary flex-1 !px-3">Apply Now</a>
        </div>
      </article>`;
  }

  function render() {
    const term = search.value.trim().toLowerCase();
    const matches = certificates.filter(
      (c) => !term || c.name.toLowerCase().includes(term) || c.description.toLowerCase().includes(term)
    );
    grid.innerHTML = matches.map(cardHtml).join("");
    noResults.classList.toggle("hidden", matches.length > 0);
  }

  async function load() {
    try {
      certificates = await Api.listCertificates();
      render();
    } catch (e) {
      grid.innerHTML = `<p class="text-red-700">${Layout.escapeHtml(e.message)}</p>`;
    }
  }

  search.addEventListener("input", render);

  const trackForm = document.getElementById("track-form");
  trackForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!Validation.validateAll(trackForm)) return;
    const ref = document.getElementById("track-ref").value.trim().toUpperCase();
    location.href = "track.html?ref=" + encodeURIComponent(ref);
  });

  load();
})();
