import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8791725616:AAG3FnlcHyhI4zDX5sQsHF7jixijkVL2430")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5640869130")

EVENT_URL = "https://www.ticketmaster.com.mx/bts-world-tour-arirang-in-mexico-ciudad-de-mexico-07-05-2026/event/1400642AA1B78268"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
}

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
        print(f"❌ Error al enviar a Telegram: {e}")

def check_tickets():
    try:
        resp = requests.get(EVENT_URL, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Error al consultar la página: {e}")
        return False

    soup = BeautifulSoup(resp.text, "html.parser")
    page_text = soup.get_text(separator=" ").lower()

    print(f"🔍 Revisando página... [{datetime.now()}]")

    soldout_signals = [
        "sold out", "agotado", "no hay boletos disponibles",
        "no tickets available", "evento agotado",
    ]
    for signal in soldout_signals:
        if signal in page_text:
            print(f"❌ Sold out detectado: '{signal}'")
            return False

    buy_signals = [
        "comprar boletos", "buy tickets", "find tickets",
        "compra aquí", "añadir al carrito", "add to cart",
        "selecciona tus boletos", "select your tickets",
    ]
    for signal in buy_signals:
        if signal in page_text:
            print(f"🎟️ ¡Boletos disponibles! Señal: '{signal}'")
            return True

    print("⚠️ No se detectó señal clara.")
    return False

def main():
    print("🚀 Bot iniciado — revisión única")
    print(f"TOKEN configurado: {'Sí' if TELEGRAM_TOKEN else 'NO ❌'}")
    print(f"CHAT_ID configurado: {'Sí' if TELEGRAM_CHAT_ID else 'NO ❌'}")
send_telegram(
        "🤖 <b>Bot activo</b>\n"
        "🎤 BTS World Tour – Arirang in Mexico\n"
        "🔍 Revisando disponibilidad..."
    )
    available = check_tickets()

    if available:
        send_telegram(
            "🚨 <b>¡BOLETOS DISPONIBLES!</b> 🚨\n\n"
            "🎤 <b>BTS World Tour – Arirang in Mexico</b>\n"
            "📅 07 Mayo 2026 · Ciudad de México\n\n"
            f"👉 <a href='{EVENT_URL}'>¡COMPRA AHORA!</a>\n\n"
            "⚡ ¡Date prisa antes de que se agoten!"
        )
    else:
        print("😴 Sin disponibilidad por ahora. El workflow volverá a correr en 5 minutos.")

if __name__ == "__main__":
    main()
