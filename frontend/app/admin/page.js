"use client";

import { useEffect, useState } from "react";
import { api } from "../../lib/api";

export default function AdminPage() {
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");

  async function load() {
    try {
      const [u, l] = await Promise.all([api.adminUsers(), api.adminLogs()]);
      setUsers(u);
      setLogs(l);
    } catch (e) {
      setError(e.message); // biasanya 403 kalau bukan admin
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleToggle(id) {
    await api.adminToggleActive(id);
    load();
  }

  if (error) {
    return <p className="text-ash text-sm">Halaman ini khusus admin. ({error})</p>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold">Admin</h1>
        <p className="text-ash text-sm mt-1">Kelola pengguna dan pantau seluruh aktivitas pengiriman.</p>
      </div>

      <div>
        <h3 className="text-sm text-ash mb-2">Pengguna</h3>
        <div className="space-y-1">
          {users.map((u) => (
            <div key={u.id} className="flex items-center justify-between border-b border-white/5 py-2">
              <span>
                {u.username} <span className="text-ash text-xs">({u.role})</span>
              </span>
              <button
                onClick={() => handleToggle(u.id)}
                className={`text-sm transition ${u.is_active ? "text-ash hover:text-red-400" : "text-green-400"}`}
              >
                {u.is_active ? "Nonaktifkan" : "Aktifkan"}
              </button>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm text-ash mb-2">Log semua pengiriman</h3>
        <div className="space-y-1 max-h-96 overflow-y-auto">
          {logs.map((l) => (
            <div key={l.id} className="flex items-center justify-between text-sm border-b border-white/5 py-2">
              <span>{l.friend_name}</span>
              <span className={l.status === "success" ? "text-green-400" : l.status === "failed" ? "text-red-400" : "text-ash"}>
                {l.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
