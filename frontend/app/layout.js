import "./globals.css";
import Nav from "./nav";

export const metadata = {
  title: "BotStreak",
  description: "Kelola pengiriman streak otomatis",
};

export default function RootLayout({ children }) {
  return (
    <html lang="id">
      <body className="min-h-screen font-sans">
        <Nav />
        <main className="max-w-3xl mx-auto px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
