// Mock citizen session stored in the browser (no real authentication).
const Session = (function () {
  const SESSION_KEY = "mh_portal_session";
  const USERS_KEY = "mh_portal_users";
  const APPS_KEY = "mh_portal_my_applications";

  function read(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch (e) {
      return fallback;
    }
  }

  function write(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      // Storage unavailable (private mode); session simply won't persist.
    }
  }

  function current() {
    return read(SESSION_KEY, null);
  }

  function login(citizen) {
    write(SESSION_KEY, { ...citizen, loggedInAt: new Date().toISOString() });
  }

  function logout() {
    localStorage.removeItem(SESSION_KEY);
  }

  // Registered sample citizens are kept only so login can greet them by name.
  function register(citizen) {
    const users = read(USERS_KEY, {});
    users[citizen.mobile] = citizen;
    write(USERS_KEY, users);
  }

  function findUser(mobile) {
    return read(USERS_KEY, {})[mobile] || null;
  }

  // Redirect to the login page if no mock session exists.
  function requireLogin() {
    if (current()) return true;
    const next = encodeURIComponent(location.pathname.replace(/^\//, "") + location.search);
    location.href = "login.html?next=" + next;
    return false;
  }

  // Applications submitted from this browser, used for background notifications.
  function myApplications() {
    return read(APPS_KEY, []);
  }

  function rememberApplication(reference, certificateName, status) {
    const apps = myApplications().filter((a) => a.reference !== reference);
    apps.unshift({ reference, certificateName, status, savedAt: new Date().toISOString() });
    write(APPS_KEY, apps.slice(0, 20));
  }

  function updateApplicationStatus(reference, status) {
    const apps = myApplications();
    const app = apps.find((a) => a.reference === reference);
    if (app) {
      app.status = status;
      write(APPS_KEY, apps);
    }
  }

  return {
    current,
    login,
    logout,
    register,
    findUser,
    requireLogin,
    myApplications,
    rememberApplication,
    updateApplicationStatus,
  };
})();
