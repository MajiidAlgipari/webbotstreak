"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { api } from "../lib/api";

const LINKS = [
  { href: "/dashboard", label: "Beranda" },
  { href: "/friends", label: "Teman" },
  { href: "/messages", label: "Pesan" },
  { href: "/admin", label: "Admin" },
];

export default function Nav() {
  const pathname = usePathname();
  const router = useRouter();

  if (pathname === "/login") return null;

  async function handleLogout() {
    await api.logout().catch(() => {});
    router.push("/login");
  }

  return (
    <nav className="border-b border-white/10">
      <div className="max-w-3xl mx-auto px-4 h-14 flex items-center justify-between">
        <span className="text-ember font-bold tracking-tight">🔥 BotStreak</span>
        <div className="flex items-center gap-5 text-sm text-ash">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={pathname === l.href ? "text-white" : "hover:text-white transition-colors"}
            >
              {l.label}
            </Link>
          ))}
          <button onClick={handleLogout} className="hover:text-white transition-colors">
            Keluar
          </button>
        </div>
      </div>
    </nav>
  );
}
