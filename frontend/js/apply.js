// Application wizard: details form, document selection, review, mock payment and submission.
//
// Selected files are kept in memory (File objects cannot survive a page reload),
// so all four steps live on this one page. The application is submitted to the
// API only after the mock payment, then each document is uploaded against the
// returned reference number.
(function () {
  if (!Session.requireLogin()) return;

  const e = Layout.escapeHtml;
  const ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"];
  const MAX_FILE_BYTES = 5 * 1024 * 1024;
  const COMMON_FIELDS = [
    ["full_name", "Full Name"],
    ["date_of_birth", "Date of Birth"],
    ["gender", "Gender"],
    ["mobile", "Mobile Number"],
    ["email", "Email"],
    ["address", "Address"],
    ["district", "District"],
    ["taluka", "Taluka"],
    ["pin_code", "PIN Code"],
  ];

  const state = {
    cert: null,
    step: 1,
    files: {}, // doc type -> File
    payment: null,
  };

  const detailsForm = document.getElementById("details-form");
  const draftKey = () => "mh_portal_draft_" + state.cert.id;

  // ---------- Step navigation ----------

  function showStep(step) {
    state.step = step;
    for (let i = 1; i <= 4; i++) {
      document.getElementById("step-" + i).classList.toggle("hidden", i !== step);
    }
    document.querySelectorAll("#stepper li").forEach((li) => {
      const n = Number(li.dataset.step);
      const base = "rounded px-2 py-2 text-center border font-semibold ";
      if (n === step) li.className = base + "text-white border-transparent";
      else if (n < step) li.className = base + "bg-green-50 text-green-800 border-green-200";
      else li.className = base + "bg-white text-slate-500 border-slate-200";
      li.style.background = n === step ? "var(--navy)" : "";
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  document.querySelectorAll("[data-goto]").forEach((btn) => {
    btn.addEventListener("click", () => showStep(Number(btn.dataset.goto)));
  });

  // ---------- Step 1: details form ----------

  function fieldHtml(field) {
    const id = "spec_" + field.name;
    const rules = [field.required ? "required" : "", field.type === "number" ? "number" : ""].join(" ").trim();
    const star = field.required ? ' <span class="req">*</span>' : "";
    let control;
    if (field.type === "select") {
      const options = field.options.map((o) => `<option>${e(o)}</option>`).join("");
      control = `<select id="${id}" name="${e(field.name)}" class="input" data-rules="${rules}"><option value="">Select</option>${options}</select>`;
    } else if (field.type === "textarea") {
      control = `<textarea id="${id}" name="${e(field.name)}" rows="2" class="input" data-rules="${rules}"></textarea>`;
    } else {
      const extra = field.type === "number" ? ' type="number" min="0" step="1"' : "";
      control = `<input id="${id}" name="${e(field.name)}" class="input"${extra} data-rules="${rules}">`;
    }
    return `<div data-field><label for="${id}" class="label">${e(field.label)}${star}</label>${control}</div>`;
  }

  function collectDetails() {
    const data = {};
    COMMON_FIELDS.forEach(([name]) => {
      data[name] = document.getElementById(name).value.trim();
    });
    data.specific_data = {};
    state.cert.fields.forEach((field) => {
      const value = document.getElementById("spec_" + field.name).value.trim();
      if (value !== "") data.specific_data[field.name] = field.type === "number" ? Number(value) : value;
    });
    return data;
  }

  function saveDraft() {
    try {
      sessionStorage.setItem(draftKey(), JSON.stringify(collectDetails()));
    } catch (err) {
      // Draft saving is best effort.
    }
  }

  function restoreDraft() {
    const citizen = Session.current() || {};
    let draft = null;
    try {
      draft = JSON.parse(sessionStorage.getItem(draftKey()) || "null");
    } catch (err) {
      draft = null;
    }
    const values = draft || { full_name: citizen.name, mobile: citizen.mobile, email: citizen.email, specific_data: {} };
    COMMON_FIELDS.forEach(([name]) => {
      if (values[name]) document.getElementById(name).value = values[name];
    });
    Object.entries(values.specific_data || {}).forEach(([name, value]) => {
      const input = document.getElementById("spec_" + name);
      if (input) input.value = value;
    });
  }

  detailsForm.addEventListener("input", saveDraft);
  Validation.attachLive(detailsForm);

  detailsForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!Validation.validateAll(detailsForm)) {
      Toast.show("Please correct the highlighted fields.", "error");
      return;
    }
    saveDraft();
    showStep(2);
  });

  // ---------- Step 2: documents ----------

  function renderDocuments() {
    const list = document.getElementById("document-list");
    list.innerHTML = state.cert.documents
      .map((doc, i) => `
        <div class="border rounded-md p-4" data-field data-doc="${e(doc)}">
          <label for="doc_${i}" class="label">${e(doc)} <span class="req">*</span></label>
          <input id="doc_${i}" type="file" accept=".pdf,.jpg,.jpeg,.png" class="block w-full text-sm file:mr-3 file:border file:border-blue-900 file:bg-white file:text-blue-900 file:font-semibold file:rounded file:px-3 file:py-1.5 file:cursor-pointer">
          <p class="file-info text-xs text-slate-500 mt-1"></p>
        </div>`)
      .join("");

    list.querySelectorAll("input[type=file]").forEach((input) => {
      input.addEventListener("change", () => onFileSelected(input));
    });
  }

  function checkFile(file) {
    const ext = (file.name.split(".").pop() || "").toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) return "Only PDF, JPG and PNG files are allowed.";
    if (file.size === 0) return "The selected file is empty.";
    if (file.size > MAX_FILE_BYTES) return "File must be 5 MB or smaller.";
    return null;
  }

  function onFileSelected(input) {
    const wrapper = input.closest("[data-doc]");
    const docType = wrapper.dataset.doc;
    const info = wrapper.querySelector(".file-info");
    const file = input.files[0];
    delete state.files[docType];
    info.textContent = "";
    if (!file) return;
    const error = checkFile(file);
    if (error) {
      Validation.setError(input, error);
      input.value = "";
      return;
    }
    Validation.setError(input, null);
    state.files[docType] = file;
    info.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
  }

  document.getElementById("documents-next").addEventListener("click", () => {
    let missing = 0;
    document.querySelectorAll("#document-list [data-doc]").forEach((wrapper) => {
      const input = wrapper.querySelector("input[type=file]");
      if (!state.files[wrapper.dataset.doc]) {
        Validation.setError(input, "Please upload this document.");
        missing++;
      }
    });
    if (missing) {
      Toast.show("Please upload all required documents.", "error");
      return;
    }
    renderReview();
    showStep(3);
  });

  // ---------- Step 3: review ----------

  function rowsHtml(rows) {
    return rows
      .map(([label, value]) => `
        <div class="grid grid-cols-3 gap-2 py-1.5 border-b border-slate-100 text-sm">
          <dt class="text-slate-500">${e(label)}</dt>
          <dd class="col-span-2 font-medium break-words">${e(value)}</dd>
        </div>`)
      .join("");
  }

  function renderReview() {
    const data = collectDetails();
    const common = COMMON_FIELDS.map(([name, label]) => [label, data[name]]);
    const specific = state.cert.fields
      .filter((f) => data.specific_data[f.name] !== undefined)
      .map((f) => [f.label, data.specific_data[f.name]]);
    const docs = Object.entries(state.files).map(([type, file]) => [type, file.name]);

    document.getElementById("review").innerHTML = `
      <div class="space-y-6">
        <section>
          <div class="flex justify-between items-center mb-2">
            <h3 class="font-semibold" style="color: var(--navy)">Applicant Details</h3>
            <button type="button" class="text-sm underline" data-edit="1">Edit</button>
          </div>
          <dl>${rowsHtml([["Certificate", state.cert.name], ...common])}</dl>
        </section>
        <section>
          <div class="flex justify-between items-center mb-2">
            <h3 class="font-semibold" style="color: var(--navy)">${e(state.cert.name)} Details</h3>
            <button type="button" class="text-sm underline" data-edit="1">Edit</button>
          </div>
          <dl>${rowsHtml(specific)}</dl>
        </section>
        <section>
          <div class="flex justify-between items-center mb-2">
            <h3 class="font-semibold" style="color: var(--navy)">Documents</h3>
            <button type="button" class="text-sm underline" data-edit="2">Edit</button>
          </div>
          <dl>${rowsHtml(docs)}</dl>
        </section>
      </div>`;

    document.querySelectorAll("[data-edit]").forEach((btn) => {
      btn.addEventListener("click", () => showStep(Number(btn.dataset.edit)));
    });
  }

  document.getElementById("review-next").addEventListener("click", () => {
    const declaration = document.getElementById("declaration");
    if (!declaration.checked) {
      Validation.setError(declaration, "Please accept the declaration to continue.");
      return;
    }
    Validation.setError(declaration, null);
    document.getElementById("pay-name").textContent = document.getElementById("full_name").value;
    showPaymentPanel(state.payment ? "payment-done-panel" : "payment-form-panel");
    showStep(4);
  });

  // ---------- Step 4: payment (simulated in the browser) and submission ----------

  const PAYMENT_PANELS = ["payment-form-panel", "payment-processing-panel", "payment-failed-panel", "payment-done-panel"];

  function showPaymentPanel(id) {
    PAYMENT_PANELS.forEach((panel) => document.getElementById(panel).classList.toggle("hidden", panel !== id));
  }

  function setProcessing(title, text) {
    document.getElementById("processing-title").textContent = title;
    document.getElementById("processing-text").textContent = text;
    showPaymentPanel("payment-processing-panel");
  }

  function selectedMethod() {
    return document.querySelector("input[name=pay-method]:checked").value;
  }

  document.querySelectorAll("input[name=pay-method]").forEach((radio) => {
    radio.addEventListener("change", () => {
      document.querySelectorAll(".pay-fields").forEach((panel) => {
        panel.classList.toggle("hidden", panel.dataset.method !== selectedMethod());
      });
    });
  });

  function validatePayment() {
    const method = selectedMethod();
    const checks = [];
    if (method === "UPI") {
      checks.push(["upi-id", /^[\w.-]{2,}@[a-zA-Z]{2,}$/, "Enter a valid UPI ID, e.g. name@bank."]);
    } else if (method === "Card") {
      checks.push(["card-number", /^\d{16}$/, "Enter a 16-digit card number.", (v) => v.replace(/\s/g, "")]);
      checks.push(["card-expiry", /^(0[1-9]|1[0-2])\/\d{2}$/, "Enter expiry as MM/YY."]);
      checks.push(["card-cvv", /^\d{3}$/, "Enter the 3-digit CVV."]);
    } else {
      checks.push(["bank", /.+/, "Please select a bank."]);
    }
    let valid = true;
    checks.forEach(([id, pattern, message, clean]) => {
      const input = document.getElementById(id);
      const value = clean ? clean(input.value) : input.value.trim();
      const ok = pattern.test(value);
      Validation.setError(input, ok ? null : message);
      if (!ok) valid = false;
    });
    return valid;
  }

  // Transaction IDs look like gateway references, e.g. TXN2610301245307421.
  function newTransactionRef() {
    const stamp = new Date().toISOString().replace(/\D/g, "").slice(2, 14);
    return "TXN" + stamp + Math.floor(1000 + Math.random() * 9000);
  }

  function accountMobile() {
    const citizen = Session.current();
    return citizen ? citizen.mobile : document.getElementById("mobile").value.trim();
  }

  document.getElementById("pay-btn").addEventListener("click", () => {
    if (!validatePayment()) return;
    setProcessing("Processing payment…", "Please do not refresh the page or press back.");
    // Gateway processing delay; payment always succeeds unless cancelled.
    setTimeout(() => {
      state.payment = {
        transaction_ref: newTransactionRef(),
        amount: state.cert.fee,
        method: selectedMethod(),
      };
      Toast.show("Payment successful.", "success");
      submitApplication();
    }, 2000);
  });

  document.getElementById("cancel-pay-btn").addEventListener("click", async () => {
    const attempt = {
      account_mobile: accountMobile(),
      certificate_type: state.cert.id,
      transaction_ref: newTransactionRef(),
      amount: state.cert.fee,
      method: selectedMethod(),
    };
    setProcessing("Cancelling transaction…", "Please wait.");
    try {
      await Api.recordFailedPayment(attempt);
    } catch (err) {
      // The failed attempt is shown even if it could not be recorded.
    }
    document.getElementById("failed-txn-ref").textContent = attempt.transaction_ref;
    document.getElementById("failed-txn-amount").textContent = formatCurrency(attempt.amount);
    showPaymentPanel("payment-failed-panel");
    Toast.show("Payment failed. No amount was debited.", "error");
  });

  document.getElementById("retry-pay-btn").addEventListener("click", () => showPaymentPanel("payment-form-panel"));
  document.getElementById("submit-btn").addEventListener("click", () => submitApplication());

  // Called after a successful payment, and again if the citizen retries a failed submission.
  async function submitApplication() {
    setProcessing("Submitting your application…", "Please do not refresh the page or press back.");
    const payload = {
      certificate_type: state.cert.id,
      account_mobile: accountMobile(),
      ...collectDetails(),
      payment: state.payment,
    };
    let created;
    try {
      created = await Api.submitApplication(payload);
    } catch (err) {
      // Payment is kept, so the citizen can correct details and submit without paying again.
      document.getElementById("done-txn-ref").textContent = state.payment.transaction_ref;
      document.getElementById("submit-error").textContent = err.message;
      showPaymentPanel("payment-done-panel");
      const fields = err.body && err.body.detail && err.body.detail.fields;
      if (fields && Object.keys(fields).length) {
        showStep(1);
        Toast.show(err.message + " Your payment is saved; correct the details and continue.", "error", 9000);
        Object.entries(fields).forEach(([name, message]) => {
          const input = document.getElementById("spec_" + name) || document.getElementById(name);
          if (input) Validation.setError(input, message);
        });
      } else {
        Toast.show(err.message, "error", 8000);
      }
      return;
    }

    // Upload each document against the new reference number.
    const entries = Object.entries(state.files);
    let failed = 0;
    for (let i = 0; i < entries.length; i++) {
      const [docType, file] = entries[i];
      setProcessing("Uploading documents…", `Document ${i + 1} of ${entries.length}: ${docType}`);
      try {
        await Api.uploadDocument(created.reference, docType, file);
      } catch (err) {
        failed++;
      }
    }

    Session.rememberApplication(created.reference, state.cert.name, created.status);
    sessionStorage.removeItem(draftKey());
    if (failed) {
      Toast.queue(`Application submitted, but ${failed} document(s) failed to upload.`, "warning");
    } else {
      Toast.queue("Application submitted successfully.", "success");
    }
    location.href = "confirmation.html?ref=" + encodeURIComponent(created.reference);
  }

  // ---------- Initial load ----------

  function showNotEligible(cert, message) {
    document.title = "Apply – " + cert.name + " | Citizen Certificate Portal";
    document.querySelector("main").innerHTML = `
      <div class="card p-6 max-w-2xl mx-auto">
        <h1 class="text-xl font-bold" style="color: var(--navy)">${e(cert.name)}</h1>
        <div class="mt-4 rounded-md border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">${e(message)}</div>
        <p class="mt-3 text-sm text-slate-600"><span class="font-semibold">Validity:</span> ${e(cert.validity)}. ${e(cert.reapply_note)}</p>
        <div class="mt-5 flex flex-wrap gap-3">
          <a href="dashboard.html" class="btn btn-primary">Go to My Account</a>
          <a href="index.html#services" class="btn btn-secondary">Back to Services</a>
        </div>
      </div>`;
  }

  async function init() {
    const id = queryParam("id");
    try {
      const [cert, districts] = await Promise.all([Api.getCertificate(id || ""), Api.listDistricts()]);
      state.cert = cert;
      // Stop before the form and payment if the citizen cannot apply again yet.
      const eligibility = await Api.checkEligibility(Session.current().mobile, cert.id);
      if (!eligibility.eligible) {
        showNotEligible(cert, eligibility.message);
        return;
      }
      document.title = "Apply – " + cert.name + " | Citizen Certificate Portal";
      document.getElementById("cert-name").textContent = cert.name;
      document.getElementById("specific-title").textContent = cert.name;
      document.getElementById("certificate_type_display").value = cert.name;
      document.getElementById("back-to-details").href = "certificate.html?id=" + encodeURIComponent(cert.id);
      document.getElementById("district").insertAdjacentHTML(
        "beforeend",
        districts.map((d) => `<option>${e(d)}</option>`).join("")
      );
      document.getElementById("specific-fields").innerHTML = cert.fields.map(fieldHtml).join("");
      document.getElementById("pay-cert").textContent = cert.name;
      document.getElementById("pay-fee").textContent = formatCurrency(cert.fee);
      document.getElementById("pay-total").textContent = formatCurrency(cert.fee);
      document.getElementById("pay-btn").textContent = "Pay " + formatCurrency(cert.fee);
      document.getElementById("date_of_birth").max = new Date().toISOString().slice(0, 10);
      restoreDraft();
      renderDocuments();
      showStep(1);
    } catch (err) {
      document.querySelector("main").innerHTML = `
        <div class="card p-6">
          <p class="text-red-700">${e(err.status === 404 ? "Certificate service not found." : err.message)}</p>
          <a href="index.html#services" class="btn btn-secondary mt-4">Back to Services</a>
        </div>`;
    }
  }

  init();
})();
