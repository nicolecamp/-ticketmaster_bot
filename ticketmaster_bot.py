import os
import asyncio
from playwright.async_api import async_playwright
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8791725616:AAG3FnlcHyhI4zDX5sQsHF7jixijkVL2430")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5640869130")

EVENT_URL = "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-07-05-2026/event/1400642AA1B78268"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("✅ Mensaje enviado a Telegram.")
    except Exception as e:
        print(f"❌ Error Telegram: {e}")

async def check_tickets():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )

        print(f"🌐 Abriendo página del evento...")
        await page.goto(EVENT_URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        content = (await page.content()).lower()
        print("📄 Página cargada correctamente.")

        await browser.close()

        # Señales de sold out
        soldout_signals = [
            "sold out", "agotado", "no hay boletos",
            "no tickets available", "evento agotado",
        ]
        for signal in soldout_signals:
            if signal in content:
                print(f"❌ Sold out: '{signal}'")
                return False

        # Señales de disponibilidad
        buy_signals = [
            "comprar boletos", "buy tickets", "find tickets",
            "compra aquí", "añadir al carrito", "add to cart",
            "selecciona tus boletos", "select your tickets",
            "get tickets",
        ]
        for signal in buy_signals:
            if signal in content:
                print(f"🎟️ ¡DISPONIBLE! Señal: '{signal}'")
                return True

        print("⚠️ Sin señal clara.")
        return False

async def main():
    print("🚀 Bot Playwright iniciado")
    print(f"TOKEN: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"CHAT_ID: {'✅' if TELEGRAM_CHAT_ID else '❌'}")

    available = await check_tickets()

    if available:
        send_telegram(
            "🚨 <b>¡BOLETOS DISPONIBLES!</b> 🚨\n\n"
            "🎤 <b>BTS World Tour – Arirang in Mexico</b>\n"
            "📅 07 Mayo 2026 · Ciudad de México\n\n"
            f"👉 <a href='{EVENT_URL}'>¡COMPRA AHORA!</a>\n\n"
            "⚡ ¡Corre antes de que se agoten!"
        )
    else:
        print("😴 Sin disponibilidad aún.")

if __name__ == "__main__":
    asyncio.run(main())
