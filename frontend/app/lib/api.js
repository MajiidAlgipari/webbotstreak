const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include", // wajib: supaya cookie sesi ikut terkirim
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    let detail = "Terjadi kesalahan";
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  login: (username, password) =>
    request("/api/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  register: (username, password) =>
    request("/api/auth/register", { method: "POST", body: JSON.stringify({ username, password }) }),
  logout: () => request("/api/auth/logout", { method: "POST" }),
  me: () => request("/api/auth/me"),

  getFriends: () => request("/api/friends"),
  addFriend: (display_name) => request("/api/friends", { method: "POST", body: JSON.stringify({ display_name }) }),
  updateFriend: (id, payload) => request(`/api/friends/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteFriend: (id) => request(`/api/friends/${id}`, { method: "DELETE" }),

  getMessages: () => request("/api/messages"),
  addMessage: (text) => request("/api/messages", { method: "POST", body: JSON.stringify({ text }) }),
  updateMessage: (id, payload) => request(`/api/messages/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteMessage: (id) => request(`/api/messages/${id}`, { method: "DELETE" }),

  getStatus: () => request("/api/streak/status"),
  getLogs: () => request("/api/streak/logs"),
  triggerSend: () => request("/api/streak/trigger", { method: "POST" }),
  connectSession: (auth_json) => request("/api/streak/connect", { method: "POST", body: JSON.stringify({ auth_json }) }),

  adminUsers: () => request("/api/admin/users"),
  adminToggleActive: (id) => request(`/api/admin/users/${id}/toggle-active`, { method: "PATCH" }),
  adminLogs: () => request("/api/admin/logs"),
};
