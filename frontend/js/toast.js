// Small, non-blocking toast notifications.
const Toast = (function () {
  const STYLES = {
    success: "bg-green-700",
    info: "bg-blue-800",
    warning: "bg-amber-600",
    error: "bg-red-700",
  };

  function container() {
    let box = document.getElementById("toast-container");
    if (!box) {
      box = document.createElement("div");
      box.id = "toast-container";
      box.className = "fixed top-24 right-4 z-50 flex flex-col gap-2 w-80 max-w-[calc(100vw-2rem)]";
      box.setAttribute("aria-live", "polite");
      document.body.appendChild(box);
    }
    return box;
  }

  function show(message, type = "info", timeoutMs = 5000) {
    const toast = document.createElement("div");
    toast.className =
      (STYLES[type] || STYLES.info) +
      " text-white text-sm rounded-md shadow-lg px-4 py-3 flex items-start gap-3 transition-opacity duration-300";
    const text = document.createElement("span");
    text.className = "flex-1";
    text.textContent = message;
    const close = document.createElement("button");
    close.type = "button";
    close.className = "font-bold opacity-80 hover:opacity-100";
    close.setAttribute("aria-label", "Dismiss");
    close.textContent = "×";
    close.onclick = () => toast.remove();
    toast.append(text, close);
    container().appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 300);
    }, timeoutMs);
  }

  // Lets one page queue a toast that the next page displays.
  function queue(message, type = "info") {
    sessionStorage.setItem("mh_portal_toast", JSON.stringify({ message, type }));
  }

  function flushQueued() {
    const raw = sessionStorage.getItem("mh_portal_toast");
    if (!raw) return;
    sessionStorage.removeItem("mh_portal_toast");
    const { message, type } = JSON.parse(raw);
    show(message, type);
  }

  return { show, queue, flushQueued };
})();
