"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";

export default function LoginPage() {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await api.register(username, password);
      }
      await api.login(username, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="text-5xl mb-2">🔥</div>
          <h1 className="text-2xl font-bold">BotStreak</h1>
          <p className="text-ash text-sm mt-1">Jaga api tetap menyala, otomatis.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-ash mb-1">Username</label>
            <input
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 outline-none focus:border-ember"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm text-ash mb-1">Password</label>
            <input
              type="password"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 outline-none focus:border-ember"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-ember text-char font-semibold rounded-lg py-2 hover:brightness-110 transition disabled:opacity-50"
          >
            {loading ? "Memproses..." : mode === "login" ? "Masuk" : "Daftar & Masuk"}
          </button>
        </form>

        <button
          className="w-full text-center text-sm text-ash hover:text-white mt-4"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
        >
          {mode === "login" ? "Belum punya akun? Daftar" : "Sudah punya akun? Masuk"}
        </button>
      </div>
    </div>
  );
}
