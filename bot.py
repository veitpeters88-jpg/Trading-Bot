import os
import requests
from anthropic import Anthropic

# 1. API-Clients & Umweltvariablen initialisieren
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
telegram_token = os.environ.get("TELEGRAM_TOKEN")
telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

client = Anthropic(api_key=anthropic_key)

# 2. System-Prompt für das Marktupdate im echten Claude-Stil
SYSTEM_PROMPT = """
Du bist ein präziser, erfahrener Finanz-Analyst. Wenn du nach einem Marktupdate gefragt wirst, erstelle eine klare, strukturierte Übersicht im typischen Claude-Stil:

1. **Markt-Überblick (Makro & Indizes):** Wichtige globale Indizes (S&P 500, Nasdaq 100, DAX, Euro Stoxx 50) mit besonderem Fokus auf den europäischen / EUR-Raum.
2. **Tech- & Einzelwerte:** Fokus auf relevante Big-Tech-Entwicklungen (z. B. NVIDIA, Apple, Microsoft) und deren Auswirkung auf den Gesamtmarkt.
3. **Zinsen & Inflation:** Relevante News von ECB/FED und wichtige Makrodaten.
4. **Fazit / Kurzausblick:** Kompakte Zusammenfassung der aktuellen Marktstimmung (Bullisch, Bärisch, Konsolidierung).

WICHTIG:
- Gib Zahlen, Kurse und Preisentwicklungen bevorzugt in Euro (€) an bzw. hebe den EUR/USD-Wechselkurs hervor, wenn US-Aktien thematisiert werden.
- Nutze übersichtliches Markdown (Fettdruck, Bullet Points, saubere Absätze), damit der Bericht schnell und gut lesbar ist.
"""

def generate_market_update():
    """Generiert das Marktupdate über die Anthropic API."""
    try:
        print("🤖 Generiere Marktupdate mit Claude...")
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=2500,
            temperature=0.3,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": "Erstelle mir ein aktuelles, kompaktes Marktupdate für heute. Wie stehen die Märkte und worauf achten Investoren aktuell?"
                }
            ]
        )
        return response.content[0].text

    except Exception as e:
        print(f"❌ Fehler bei der Claude API-Abfrage: {e}")
        return None

def send_telegram_message(text):
    """Sendet die Nachricht via Telegram Bot an deinen Chat."""
    if not telegram_token or not telegram_chat_id:
        print("⚠️ Telegram Token oder Chat ID fehlt in den Umgebungsvariablen!")
        return

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    
    # Telegram unterstützt Nachrichten bis max 4096 Zeichen
    payload = {
        "chat_id": telegram_chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Marktupdate erfolgreich per Telegram verschickt!")
        else:
            # Falls Markdown-Parsing-Fehler auftreten, versuchen wir es unformatiert erneut
            print(f"⚠️ Fehler beim Senden mit Markdown ({response.status_code}), versuche Reintext...")
            payload.pop("parse_mode")
            requests.post(url, json=payload)
            print("✅ Marktupdate als Reintext verschickt!")
            
    except Exception as e:
        print(f"❌ Fehler beim Versenden der Telegram-Nachricht: {e}")

if __name__ == "__main__":
    # Update generieren
    update_text = generate_market_update()

    if update_text:
        print("--- GENERIERTES UPDATE ---")
        print(update_text)
        print("---------------------------")
        
        # An Telegram senden
        send_telegram_message(update_text)
    else:
        print("❌ Es konnte kein Update generiert werden.")
