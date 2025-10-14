from rq import Queue
from redis import Redis
import time, json, requests
from app.config import settings

redis = Redis.from_url(settings.REDIS_URL)
queue = Queue(settings.RQ_QUEUE, connection=redis)

def enqueue(fn, *args, **kwargs):
    return queue.enqueue(fn, *args, **kwargs)

# ==== Example background jobs ====
def enrich_lead_job(lead_id: int):
    # Здесь можно звать внешние API для обогащения (Clearbit/ ваш CRM / RegExp по сайту)
    time.sleep(0.2)
    return {"lead_id": lead_id, "status": "enriched"}

def notify_slack_job(text: str):
    if not settings.SLACK_WEBHOOK_URL:
        return {"status": "skipped", "reason": "no webhook"}
    try:
        r = requests.post(settings.SLACK_WEBHOOK_URL, json={"text": text}, timeout=5)
        return {"status": "ok", "code": r.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def notify_telegram_job(text: str):
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        return {"status": "skipped", "reason": "no telegram config"}
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": settings.TELEGRAM_CHAT_ID, "text": text}, timeout=5)
        return {"status": "ok", "code": r.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}
