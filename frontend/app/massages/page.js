"use client";

import { useEffect, useState } from "react";
import { api } from "../../lib/api";

export default function MessagesPage() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");

  async function load() {
    setMessages(await api.getMessages());
  }

  useEffect(() => {
    load();
  }, []);

  async function handleAdd(e) {
    e.preventDefault();
    if (!text.trim()) return;
    await api.addMessage(text);
    setText("");
    load();
  }

  async function toggleActive(m) {
    await api.updateMessage(m.id, { is_active: !m.is_active });
    load();
  }

  async function handleDelete(id) {
    await api.deleteMessage(id);
    load();
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Pesan</h1>
        <p className="text-ash text-sm mt-1">
          Daftar variasi pesan. Satu dipilih acak setiap kali streak dikirim ke seorang teman.
        </p>
      </div>

      <form onSubmit={handleAdd} className="flex gap-2">
        <input
          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 outline-none focus:border-ember"
          placeholder="fyr. 🔥"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button className="bg-ember text-char font-semibold rounded-lg px-4 hover:brightness-110 transition">
          Tambah
        </button>
      </form>

      <div className="space-y-1">
        {messages.length === 0 && <p className="text-ash text-sm">Belum ada pesan ditambahkan.</p>}
        {messages.map((m) => (
          <div key={m.id} className="flex items-center justify-between border-b border-white/5 py-2">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={m.is_active}
                onChange={() => toggleActive(m)}
                className="accent-ember w-4 h-4"
              />
              <span className={m.is_active ? "" : "text-ash line-through"}>{m.text}</span>
            </label>
            <button onClick={() => handleDelete(m.id)} className="text-ash hover:text-red-400 text-sm transition">
              Hapus
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
