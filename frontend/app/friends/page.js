"use client";

import { useEffect, useState } from "react";
import { api } from "../../lib/api";

export default function FriendsPage() {
  const [friends, setFriends] = useState([]);
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setFriends(await api.getFriends());
  }

  useEffect(() => {
    load();
  }, []);

  async function handleAdd(e) {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      await api.addFriend(name);
      setName("");
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function toggleSelected(friend) {
    await api.updateFriend(friend.id, { is_selected: !friend.is_selected });
    load();
  }

  async function handleDelete(id) {
    await api.deleteFriend(id);
    load();
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Teman</h1>
        <p className="text-ash text-sm mt-1">
          Pilih teman mana yang mau dikirimi streak. Nama harus persis seperti tampilan di TikTok.
        </p>
      </div>

      <form onSubmit={handleAdd} className="flex gap-2">
        <input
          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 outline-none focus:border-ember"
          placeholder="Nama tampilan teman..."
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button className="bg-ember text-char font-semibold rounded-lg px-4 hover:brightness-110 transition">
          Tambah
        </button>
      </form>
      {error && <p className="text-red-400 text-sm">{error}</p>}

      <div className="space-y-1">
        {friends.length === 0 && <p className="text-ash text-sm">Belum ada teman ditambahkan.</p>}
        {friends.map((f) => (
          <div key={f.id} className="flex items-center justify-between border-b border-white/5 py-2">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={f.is_selected}
                onChange={() => toggleSelected(f)}
                className="accent-ember w-4 h-4"
              />
              <span className={f.is_selected ? "" : "text-ash line-through"}>{f.display_name}</span>
            </label>
            <button onClick={() => handleDelete(f.id)} className="text-ash hover:text-red-400 text-sm transition">
              Hapus
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
