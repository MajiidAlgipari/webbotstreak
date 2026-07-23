"""
Worker otomasi TikTok, hasil refactor dari skrip 'tes.py' asli.
Sekarang menerima parameter per-user (bukan konstanta global) supaya bisa
dipakai untuk banyak akun dari satu web app.

CATATAN RISIKO: otomasi ini menyerupai perilaku bot dan berpotensi melanggar
Ketentuan Layanan TikTok, yang bisa berujung pembatasan/suspend akun.
Gunakan dengan risiko ditanggung sendiri.
"""
import json
import random
import tempfile
import os
from datetime import datetime
from typing import Optional

import pytz
from playwright.sync_api import sync_playwright

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def _now() -> str:
    return datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M:%S")


def run_streak_job(storage_state_json: str, friend_names: list[str], messages: list[str]) -> dict:
    """
    Menjalankan satu putaran pengiriman streak untuk satu user.

    Args:
        storage_state_json: isi auth.json (string JSON) milik user tsb.
        friend_names: daftar nama tampilan teman yang mau dikirim.
        messages: daftar variasi pesan (dipilih acak per teman).

    Returns:
        dict berisi ringkasan + detail per-teman, contoh:
        {
            "results": [
                {"friend": "chell", "status": "success", "message": "fyr. 🔥", "detail": None},
                {"friend": "Haniff.", "status": "failed", "message": None, "detail": "kontak tidak ditemukan"},
            ],
            "session_invalid": False,
        }
    """
    results = []
    session_invalid = False

    if not friend_names:
        return {"results": [], "session_invalid": False}
    if not messages:
        messages = ["fyr. 🔥"]

    # Tulis storage_state ke file sementara (playwright butuh path atau dict)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp.write(storage_state_json)
        tmp_path = tmp.name

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-infobars",
                    "--ignore-certificate-errors",
                    "--disable-gpu",
                ],
            )
            try:
                context = browser.new_context(
                    storage_state=tmp_path,
                    user_agent=USER_AGENT,
                    viewport={"width": 1920, "height": 1080},
                    locale="id-ID",
                    timezone_id="Asia/Jakarta",
                )
            except Exception:
                browser.close()
                return {"results": [], "session_invalid": True}

            page = context.new_page()
            page.goto("https://www.tiktok.com/messages", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(15000)

            # Deteksi kalau ternyata di-redirect ke halaman login -> sesi expired
            if "/login" in page.url:
                session_invalid = True
                browser.close()
                return {"results": [], "session_invalid": True}

            for target_user in friend_names:
                entry = {"friend": target_user, "status": "failed", "message": None, "detail": None}
                try:
                    chat_item = None
                    selectors = [
                        f'span:has-text("{target_user}")',
                        f'p:has-text("{target_user}")',
                        f'div:has-text("{target_user}")',
                        f'[data-e2e="im-item"]:has-text("{target_user}")',
                    ]
                    for sel in selectors:
                        el = page.locator(sel).first
                        try:
                            if el.is_visible(timeout=1500):
                                chat_item = el
                                break
                        except Exception:
                            continue

                    if not chat_item:
                        entry["status"] = "skipped"
                        entry["detail"] = "Kontak tidak ditemukan di daftar chat"
                        results.append(entry)
                        continue

                    chat_item.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    chat_item.click(force=True)
                    page.wait_for_timeout(500)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(8000)

                    chat_box = None
                    for sel in [
                        'div[contenteditable="true"]',
                        'textarea',
                        'div[role="textbox"]',
                    ]:
                        el = page.locator(sel).first
                        try:
                            if el.is_visible(timeout=1500):
                                chat_box = el
                                break
                        except Exception:
                            continue

                    if not chat_box:
                        entry["detail"] = "Kotak ketik chat tidak ditemukan"
                        results.append(entry)
                        continue

                    pesan_acak = random.choice(messages)
                    chat_box.click(force=True)
                    page.wait_for_timeout(500)
                    chat_box.fill(pesan_acak)
                    page.wait_for_timeout(1000)
                    chat_box.press("Enter")

                    entry["status"] = "success"
                    entry["message"] = pesan_acak
                except Exception as e:
                    entry["detail"] = str(e)

                results.append(entry)
                page.wait_for_timeout(4000)

            browser.close()
    finally:
        os.unlink(tmp_path)

    return {"results": results, "session_invalid": session_invalid}
