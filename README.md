# BotStreak Web

Versi web dari bot streak TikTok kamu (`tes.py` awal). Ada 2 bagian:

- **backend/** — FastAPI + SQLite + Playwright (worker otomasi)
- **frontend/** — Next.js (dashboard user + panel admin)

## ⚠️ Sebelum mulai
Otomasi pengiriman pesan seperti ini menyerupai perilaku bot dan berpotensi
melanggar Ketentuan Layanan TikTok — akun bisa kena pembatasan/suspend.
Pakai dengan risiko ditanggung sendiri, terutama kalau dipakai banyak orang
sekaligus (multi-user).

## Menjalankan di lokal (development)

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium --with-deps

# generate secret sekali, simpan hasilnya
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

export JWT_SECRET="ganti-dengan-string-acak-panjang"
export FERNET_KEY="hasil-generate-di-atas"

uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_BASE=http://localhost:8000" > .env.local
npm run dev
```
Buka http://localhost:3000 — user pertama yang daftar otomatis jadi **admin**.

## Cara dapat `auth.json` (sesi TikTok)
File ini adalah hasil `context.storage_state()` Playwright setelah login manual
sekali di TikTok (persis proses yang sudah kamu punya di skrip lama). Isi
file itu ditempel di kolom "Hubungkan sesi TikTok" pada halaman dashboard —
tersimpan terenkripsi di database, bukan sebagai file mentah.

## Alur pemakaian
1. Daftar/login di web.
2. Tempel `auth.json` di dashboard → "Hubungkan sesi TikTok".
3. Tambah teman di halaman **Teman** (nama harus persis seperti di TikTok), centang yang mau dikirimi.
4. Tambah variasi pesan di halaman **Pesan**.
5. Klik **Kirim Streak Sekarang** di dashboard — indikator 🔥 menyala kalau semua teman terpilih sudah terkirim sukses hari itu.
6. Admin bisa pantau semua user & log di halaman **Admin**.

## Otomatis harian (opsional)
Endpoint `POST /api/streak/trigger` bisa dipanggil dari cron job / APScheduler
per user, misalnya lewat `crontab` yang memanggil endpoint itu tiap hari jam
tertentu (butuh token/cookie sesi user yang masih berlaku).

## Deploy ke VPS
Playwright butuh Chromium yang jalan di server sungguhan (bukan serverless).
Rekomendasi: VPS kecil (1 vCPU/2GB RAM cukup), misal DigitalOcean/Contabo/Vultr.

```bash
# di VPS, setelah clone project & install docker + docker compose:
export JWT_SECRET="..."
export FERNET_KEY="..."
export NEXT_PUBLIC_API_BASE="https://api.domainkamu.com"

docker compose up -d --build
```

Lalu pasang reverse proxy (Nginx/Caddy) + HTTPS (Let's Encrypt) di depan
`frontend:3000` dan `backend:8000`, dan set `secure=True` pada cookie di
`app/routers/auth.py` (sudah default True — pastikan situs diakses via HTTPS).

## Catatan keamanan
- `JWT_SECRET` dan `FERNET_KEY` **wajib** diganti dari default dev dan disimpan sebagai secret, jangan di-commit ke git.
- `auth.json` tiap user tersimpan terenkripsi (Fernet) di database — kalau `FERNET_KEY` hilang, semua sesi tersimpan tidak bisa didekripsi lagi (harus connect ulang).
