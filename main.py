from fastapi import FastAPI, Request, HTTPException
import requests
import os

# These come from Railway → Variables (NOT hardcoded)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

app = FastAPI()

STATUS_MAP = {
    "OUT_FOR_DELIVERY": "🚚 Sortie en livraison",
    "DELIVERED_STOPDESK": "📦 Livré au Stop Desk",
    "DELIVERED_COURIER": "🚚 Livré par le livreur",
    "NO_ANSWER_1": "📞 Client ne répond pas (1)",
    "NO_ANSWER_2": "📞 Client ne répond pas (2)",
    "NO_ANSWER_3": "📞 Client injoignable (final)",
    "REPORTED": "⚠️ Signalé",
    "CANCELLED": "❌ Annulé"
}

def send_telegram(message):
    # Telegram API call
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

@app.post("/webhook/zrexpress")
async def zrexpress_webhook(request: Request):
    # 1️⃣ SECURITY CHECK
    secret = request.headers.get("X-Webhook-Secret")
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2️⃣ READ ZREXPRESS DATA
    data = await request.json()
    order_id = data.get("order_id")
    status = data.get("status")

    # 3️⃣ SEND TELEGRAM MESSAGE
    message = (
        f"{STATUS_MAP.get(status, status)}\n"
        f"📦 Commande: {order_id}\n"
        f"🚛 ZRexpress"
    )

    send_telegram(message)
    return {"ok": True}
