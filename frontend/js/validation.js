// Field-level validation helpers shared by the forms.
const Validation = (function () {
  const RULES = {
    required: (v) => (v && String(v).trim() ? null : "This field is required."),
    name: (v) => (/^[A-Za-z .']{3,120}$/.test(v.trim()) ? null : "Enter a valid full name (letters only, min 3 characters)."),
    mobile: (v) => (/^[6-9]\d{9}$/.test(v) ? null : "Enter a valid 10-digit mobile number starting with 6–9."),
    email: (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? null : "Enter a valid email address."),
    pin: (v) => (/^4\d{5}$/.test(v) ? null : "Enter a valid 6-digit Maharashtra PIN code (starts with 4)."),
    pastDate: (v) => (v && new Date(v) < new Date() ? null : "Date must be in the past."),
    number: (v) => (v === "" || (!isNaN(v) && Number(v) >= 0) ? null : "Enter a valid non-negative number."),
    password: (v) => (v && v.length >= 6 ? null : "Password must be at least 6 characters."),
    otp: (v) => (/^\d{6}$/.test(v) ? null : "Enter the 6-digit OTP."),
  };

  function setError(input, message) {
    const wrapper = input.closest("[data-field]") || input.parentElement;
    let el = wrapper.querySelector(".error-text");
    if (message) {
      input.classList.add("has-error");
      input.setAttribute("aria-invalid", "true");
      if (!el) {
        el = document.createElement("p");
        el.className = "error-text";
        wrapper.appendChild(el);
      }
      el.textContent = message;
    } else {
      input.classList.remove("has-error");
      input.removeAttribute("aria-invalid");
      if (el) el.remove();
    }
  }

  // Validate one input using its data-rules attribute, e.g. data-rules="required mobile".
  function validateInput(input) {
    const rules = (input.dataset.rules || "").split(/\s+/).filter(Boolean);
    const value = input.value;
    for (const rule of rules) {
      if (rule !== "required" && !String(value).trim()) continue;
      const message = RULES[rule] && RULES[rule](value);
      if (message) {
        setError(input, message);
        return false;
      }
    }
    // Optional minimum length, e.g. data-minlength="5" (mirrors the server rules).
    const min = Number(input.dataset.minlength || 0);
    if (min && String(value).trim() && String(value).trim().length < min) {
      setError(input, `Must be at least ${min} characters.`);
      return false;
    }
    setError(input, null);
    return true;
  }

  // Validate every [data-rules] input inside a container. Focuses the first invalid one.
  function validateAll(container) {
    let firstInvalid = null;
    container.querySelectorAll("[data-rules]").forEach((input) => {
      if (!validateInput(input) && !firstInvalid) firstInvalid = input;
    });
    if (firstInvalid) firstInvalid.focus();
    return !firstInvalid;
  }

  // Re-validate fields as the citizen corrects them.
  function attachLive(container) {
    container.addEventListener("blur", (e) => {
      if (e.target.dataset && e.target.dataset.rules) validateInput(e.target);
    }, true);
    container.addEventListener("input", (e) => {
      if (e.target.classList && e.target.classList.contains("has-error")) validateInput(e.target);
    });
  }

  return { validateInput, validateAll, attachLive, setError };
})();
