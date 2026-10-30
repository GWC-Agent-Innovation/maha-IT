// Thin wrapper around fetch for the portal REST API.
const Api = (function () {
  async function request(path, options = {}) {
    let response;
    try {
      response = await fetch(path, options);
    } catch (e) {
      throw new ApiError("Unable to reach the server. Please check your connection.", 0, null);
    }
    const isJson = (response.headers.get("content-type") || "").includes("application/json");
    const body = isJson ? await response.json() : null;
    if (!response.ok) {
      throw new ApiError(errorMessage(body, response.status), response.status, body);
    }
    return body;
  }

  function errorMessage(body, status) {
    const detail = body && body.detail;
    if (typeof detail === "string") return detail;
    if (detail && detail.message) return detail.message;
    if (status === 422) return "Some details are invalid. Please check the form and try again.";
    if (Array.isArray(detail) && detail.length) {
      return detail.map((d) => d.msg.replace(/^Value error, /, "")).join(" ");
    }
    return "Request failed (" + status + ").";
  }

  class ApiError extends Error {
    constructor(message, status, body) {
      super(message);
      this.status = status;
      this.body = body;
    }
  }

  return {
    listCertificates: () => request("/api/certificates"),
    getCertificate: (id) => request("/api/certificates/" + encodeURIComponent(id)),
    listDistricts: () => request("/api/districts"),
    submitApplication: (data) =>
      request("/api/applications", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }),
    uploadDocument: (reference, docType, file) => {
      const form = new FormData();
      form.append("doc_type", docType);
      form.append("file", file);
      return request("/api/applications/" + encodeURIComponent(reference) + "/documents", {
        method: "POST",
        body: form,
      });
    },
    recordFailedPayment: (data) =>
      request("/api/payments/failed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }),
    myApplications: (mobile) => request("/api/citizens/" + encodeURIComponent(mobile) + "/applications"),
    myPayments: (mobile) => request("/api/citizens/" + encodeURIComponent(mobile) + "/payments"),
    getApplication: (reference) => request("/api/applications/" + encodeURIComponent(reference)),
    getStatus: (reference) =>
      request("/api/applications/" + encodeURIComponent(reference) + "/status"),
    certificateUrl: (reference) =>
      "/api/applications/" + encodeURIComponent(reference) + "/certificate",
    ApiError,
  };
})();
