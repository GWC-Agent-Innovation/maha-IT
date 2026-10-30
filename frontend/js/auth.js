// Mock login and registration. Everything happens in the browser; nothing is sent to the server.
(function () {
  // Only allow redirects to pages on this site.
  function nextPage() {
    const next = queryParam("next");
    return next && /^[\w-]+\.html(\?[\w=&%.-]*)?$/.test(next) ? next : "dashboard.html";
  }

  function keepNextOnLinks() {
    const next = queryParam("next");
    if (!next) return;
    ["register-link", "login-link"].forEach((id) => {
      const link = document.getElementById(id);
      if (link) link.href += "?next=" + encodeURIComponent(next);
    });
  }


  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    Validation.attachLive(loginForm);

    loginForm.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!Validation.validateAll(loginForm)) return;
      const mobile = document.getElementById("mobile").value.trim();
      const known = Session.findUser(mobile);
      const btn = document.getElementById("login-btn");
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Signing in…';
      // Short delay to simulate a server round trip.
      setTimeout(() => {
        Session.login({
          name: known ? known.name : "Citizen " + mobile.slice(-4),
          mobile,
          email: known ? known.email : "",
        });
        Toast.queue("Login successful.", "success");
        location.href = nextPage();
      }, 700);
    });
  }

  const registerForm = document.getElementById("register-form");
  if (registerForm) {
    Validation.attachLive(registerForm);

    registerForm.addEventListener("submit", (event) => {
      event.preventDefault();
      let valid = Validation.validateAll(registerForm);
      const password = document.getElementById("password");
      const confirm = document.getElementById("confirm");
      if (confirm.value && confirm.value !== password.value) {
        Validation.setError(confirm, "Passwords do not match.");
        valid = false;
      }
      const consent = document.getElementById("consent");
      Validation.setError(consent, consent.checked ? null : "Please accept to continue.");
      if (!valid || !consent.checked) return;

      const citizen = {
        name: document.getElementById("name").value.trim(),
        mobile: document.getElementById("mobile").value.trim(),
        email: document.getElementById("email").value.trim(),
      };
      Session.register(citizen);
      Session.login(citizen);
      Toast.queue("Registration successful. You are now logged in.", "success");
      location.href = nextPage();
    });
  }

  keepNextOnLinks();
})();
