"use client";

import { useEffect, useState } from "react";
import { api } from "../../lib/api";

export default function DashboardPage() {
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [sending, setSending] = useState(false);
  const [msg, setMsg] = useState("");
  const [authJson, setAuthJson] = useState("");

  async function load() {
    try {
      const [s, l] = await Promise.all([api.getStatus(), api.getLogs()]);
      setStatus(s);
      setLogs(l);
    } catch (e) {
      setMsg(e.message);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, []);

  async function handleTrigger() {
    setSending(true);
    setMsg("");
    try {
      const res = await api.triggerSend();
      setMsg(res.message);
      setTimeout(load, 6000);
    } catch (e) {
      setMsg(e.message);
    } finally {
      setSending(false);
    }
  }

  async function handleConnect(e) {
    e.preventDefault();
    try {
      await api.connectSession(authJson);
      setMsg("Sesi TikTok berhasil dihubungkan.");
      setAuthJson("");
    } catch (e) {
      setMsg(e.message);
    }
  }

  const isLit = status?.is_lit;

  return (
    <div className="space-y-8">
      {/* Indikator utama */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-8 text-center">
        <div className={`text-7xl transition-all ${isLit ? "" : "grayscale opacity-40"}`}>🔥</div>
        <h2 className="text-xl font-semibold mt-3">
          {isLit ? "Streak hari ini menyala" : "Streak belum dikirim hari ini"}
        </h2>
        {status && (
          <p className="text-ash text-sm mt-1">
            {status.sent_today}/{status.total_friends} teman terkirim
            {status.failed_today > 0 && ` · ${status.failed_today} gagal`}
          </p>
        )}
        <button
          onClick={handleTrigger}
          disabled={sending}
          className="mt-5 bg-ember text-char font-semibold rounded-lg px-5 py-2 hover:brightness-110 transition disabled:opacity-50"
        >
          {sending ? "Mengirim..." : "Kirim Streak Sekarang"}
        </button>
        {msg && <p className="text-sm text-ash mt-3">{msg}</p>}
      </div>

      {/* Hubungkan sesi TikTok */}
      <details className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
        <summary className="cursor-pointer text-sm text-ash">Hubungkan / perbarui sesi TikTok (auth.json)</summary>
        <form onSubmit={handleConnect} className="mt-3 space-y-2">
          <textarea
            className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono h-32 outline-none focus:border-ember"
            placeholder='Tempel isi auth.json (storage_state) di sini...'
            value={authJson}
            onChange={(e) => setAuthJson(e.target.value)}
          />
          <button className="bg-white/10 hover:bg-white/20 rounded-lg px-4 py-2 text-sm transition">
            Simpan Sesi
          </button>
        </form>
      </details>

      {/* Riwayat */}
      <div>
        <h3 className="text-sm text-ash mb-2">Riwayat terakhir</h3>
        <div className="space-y-1">
          {logs.length === 0 && <p className="text-ash text-sm">Belum ada riwayat pengiriman.</p>}
          {logs.map((l) => (
            <div key={l.id} className="flex items-center justify-between text-sm border-b border-white/5 py-2">
              <span>{l.friend_name}</span>
              <span className={l.status === "success" ? "text-green-400" : l.status === "failed" ? "text-red-400" : "text-ash"}>
                {l.status === "success" ? `✓ ${l.message_sent}` : l.status === "failed" ? "✕ gagal" : "– dilewati"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
