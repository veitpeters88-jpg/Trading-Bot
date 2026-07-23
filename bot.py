import os
import requests

token = os.getenv("TELEGRAM_TOKEN", "").strip()
chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

print(f"Token Länge: {len(token)}")
print(f"Chat ID Länge: {len(chat_id)}")

if not token or not chat_id:
    print("❌ FEHLER: Token oder Chat-ID fehlt in den Secrets!")
else:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    res = requests.post(url, json={"chat_id": chat_id, "text": "🚀 TEST: Telegram Verbindungsaufbau erfolgreich!"})
    
    print(f"Telegram HTTP Status: {res.status_code}")
    print(f"Telegram Antwort: {res.text}")
