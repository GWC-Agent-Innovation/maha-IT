// Shared header, footer and background status notifications for every page.
const Layout = (function () {
  const EMBLEM_SVG =
    '<svg viewBox="0 0 48 48" class="w-12 h-12" aria-hidden="true">' +
    '<circle cx="24" cy="24" r="22" fill="#fff" stroke="#e8711a" stroke-width="2"/>' +
    '<circle cx="24" cy="24" r="12" fill="none" stroke="#1e3a8a" stroke-width="2"/>' +
    '<circle cx="24" cy="24" r="3" fill="#1e3a8a"/>' +
    Array.from({ length: 12 }, (_, i) => {
      const a = (i * Math.PI) / 6;
      const x1 = 24 + 5 * Math.cos(a), y1 = 24 + 5 * Math.sin(a);
      const x2 = 24 + 11 * Math.cos(a), y2 = 24 + 11 * Math.sin(a);
      return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#1e3a8a" stroke-width="1.5"/>`;
    }).join("") +
    "</svg>";

  const NAV_LINKS = [
    { href: "index.html", label: "Home" },
    { href: "index.html#services", label: "Services" },
    { href: "track.html", label: "Track Application" },
    { href: "index.html#help", label: "Help" },
  ];

  const FINAL_STATUS = "CERTIFICATE_GENERATED";

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function renderHeader() {
    const target = document.getElementById("site-header");
    if (!target) return;
    const citizen = Session.current();
    const page = location.pathname.split("/").pop() || "index.html";

    const links = citizen ? [...NAV_LINKS.slice(0, 3), { href: "dashboard.html", label: "My Account" }, NAV_LINKS[3]] : NAV_LINKS;
    const navHtml = links.map((link) => {
      const active = link.href === page ? " bg-white/15" : "";
      return `<a href="${link.href}" class="px-3 py-2 rounded hover:bg-white/10${active}">${link.label}</a>`;
    }).join("");

    const accountHtml = citizen
      ? `<a href="dashboard.html" class="hidden sm:inline text-sm hover:underline">Welcome, <strong>${escapeHtml(citizen.name)}</strong></a>
         <button id="logout-btn" class="btn btn-secondary !py-1 !px-3 text-sm">Logout</button>`
      : `<a href="login.html" class="btn btn-primary !py-1 !px-3 text-sm">Login</a>
         <a href="register.html" class="btn btn-secondary !py-1 !px-3 text-sm">Register</a>`;

    target.innerHTML = `
      <div class="bg-white border-b-4" style="border-color: var(--saffron)">
        <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <a href="index.html" class="flex items-center gap-3">
            ${EMBLEM_SVG}
            <div>
              <div class="text-xs uppercase tracking-wide text-slate-500">Government of Maharashtra</div>
              <div class="text-lg sm:text-xl font-bold" style="color: var(--navy)">Citizen Certificate Portal</div>
              <div class="text-xs text-slate-500">नागरिक प्रमाणपत्र सेवा</div>
            </div>
          </a>
          <div class="flex items-center gap-2">${accountHtml}</div>
        </div>
      </div>
      <nav class="text-white text-sm" style="background: var(--navy)">
        <div class="max-w-6xl mx-auto px-2 flex flex-wrap">${navHtml}</div>
      </nav>`;

    const logout = document.getElementById("logout-btn");
    if (logout) {
      logout.onclick = () => {
        Session.logout();
        Toast.queue("You have been logged out.", "info");
        location.href = "index.html";
      };
    }
  }

  function renderFooter() {
    const target = document.getElementById("site-footer");
    if (!target) return;
    target.innerHTML = `
      <footer class="mt-12 text-slate-300 text-sm" style="background: #0f1d47">
        <div class="max-w-6xl mx-auto px-4 py-8 grid gap-6 sm:grid-cols-3">
          <div>
            <div class="font-semibold text-white mb-2">Citizen Certificate Portal</div>
            <p>Apply for revenue certificates online, track your application and download issued certificates.</p>
          </div>
          <div>
            <div class="font-semibold text-white mb-2">Quick Links</div>
            <ul class="space-y-1">
              <li><a class="hover:text-white" href="index.html#services">Certificate Services</a></li>
              <li><a class="hover:text-white" href="track.html">Track Application</a></li>
              <li><a class="hover:text-white" href="login.html">Citizen Login</a></li>
            </ul>
          </div>
          <div>
            <div class="font-semibold text-white mb-2">Helpdesk</div>
            <p>Toll free: 1800-000-0000<br>Mon–Sat, 10:00–18:00</p>
          </div>
        </div>
        <div class="text-center text-xs py-3 border-t border-white/10">
          © ${new Date().getFullYear()} Citizen Certificate Portal · Prototype developed for evaluation by the Government of Maharashtra.
        </div>
      </footer>`;
  }

  // Poll applications submitted from this browser and notify on status changes.
  function watchMyApplications() {
    const pending = Session.myApplications().filter((a) => a.status !== FINAL_STATUS);
    if (!pending.length) return;
    pending.forEach(async (app) => {
      try {
        const status = await Api.getStatus(app.reference);
        if (status.status !== app.status) {
          Session.updateApplicationStatus(app.reference, status.status);
          notifyStatusChange(app.reference, status.status);
          document.dispatchEvent(new CustomEvent("application-status", { detail: status }));
        }
      } catch (e) {
        // Ignore background polling failures.
      }
    });
  }

  function notifyStatusChange(reference, status) {
    if (status === "APPROVED") {
      Toast.show(`Application ${reference} has been approved.`, "success", 7000);
    } else if (status === FINAL_STATUS) {
      Toast.show(`Certificate generated for ${reference}. It is ready for download.`, "success", 9000);
    }
  }

  function init() {
    renderHeader();
    renderFooter();
    Toast.flushQueued();
    watchMyApplications();
    setInterval(watchMyApplications, 15000);
  }

  document.addEventListener("DOMContentLoaded", init);

  return { escapeHtml, notifyStatusChange };
})();

// Shared formatting helpers.
function formatDateTime(value) {
  // API datetimes are UTC without a timezone suffix.
  const date = new Date(/Z|[+-]\d\d:\d\d$/.test(value) ? value : value + "Z");
  return date.toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}

function formatCurrency(amount) {
  return "₹" + Number(amount).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function queryParam(name) {
  return new URLSearchParams(location.search).get(name);
}
