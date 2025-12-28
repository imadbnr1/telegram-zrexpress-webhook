from fastapi import FastAPI, Request, HTTPException
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

app = FastAPI()

# Map ZRexpress statuses to human-readable messages
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

LAST_STATUS = {}  # Prevent duplicate notifications

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data, timeout=5)

@app.post("/webhook/zrexpress")
async def zrexpress_webhook(request: Request):
    secret = request.headers.get("X-Webhook-Secret")
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()
    order_id = data.get("order_id")
    status = data.get("status")

    if not order_id or not status:
        return {"ok": False}

    if LAST_STATUS.get(order_id) == status:
        return {"ok": True}

    LAST_STATUS[order_id] = status

    message = (
        f"{STATUS_MAP.get(status, status)}\n"
        f"📦 Commande: {order_id}\n"
        f"🚛 ZRexpress"
    )
    send_telegram(message)
    return {"ok": True}
