import os
import requests
import anthropic

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram Daten fehlen!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)

def main():
    send_telegram("🚀 NEUSTART ERFOLGREICH: GitHub-Bot läuft!")

    if not ANTHROPIC_API_KEY:
        send_telegram("❌ API Key fehlt!")
        return

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "Sag kurz Hallo an Veit!"}]
        )
        send_telegram(f"🤖 **CLAUDE ANTWORT:**\n\n{response.content[0].text}")
    except Exception as e:
        send_telegram(f"❌ CLAUDE FEHLER: {e}")

if __name__ == "__main__":
    main()
