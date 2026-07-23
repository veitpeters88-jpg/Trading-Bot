import os
import sys
import requests
import yfinance as yf
from anthropic import Anthropic

# ==========================================
# 1. API-Keys & Umgebungsvariablen prüfen
# ==========================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not ANTHROPIC_API_KEY:
    print("❌ FEHLER: ANTHROPIC_API_KEY ist nicht gesetzt!")
    sys.exit(1)

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ FEHLER: TELEGRAM_TOKEN oder TELEGRAM_CHAT_ID fehlt!")
    sys.exit(1)

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# ==========================================
# 2. Finanzdaten über yfinance abrufen
# ==========================================
def get_market_data():
    print("📊 Lade aktuelle Markt- und Aktiendaten...")
    tickers = {
        "S&P 500": "^GSPC",
        "Nasdaq 100": "^NDX",
        "DAX": "^GDAXI",
        "MSCI World": "URTH",
        "NVIDIA": "NVDA",
        "Bitcoin": "BTC-USD"
    }
    
    summary_lines = []
    for name, ticker_symbol in tickers.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                latest_close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                pct_change = ((latest_close - prev_close) / prev_close) * 100
                summary_lines.append(f"- {name}: {latest_close:.2f} ({pct_change:+.2f}%)")
            else:
                summary_lines.append(f"- {name}: Keine Daten verfügbar")
        except Exception as e:
            summary_lines.append(f"- {name}: Fehler ({e})")
            
    return "\n".join(summary_lines)

# ==========================================
# 3. Markt-Update via Claude AI generieren
# ==========================================
SYSTEM_PROMPT = """
Du bist ein erfahrener Finanzanalyst. Deine Aufgabe ist es, aus den gelieferten Marktdaten ein prägnantes, leicht verständliches Börsen-Update auf Deutsch zu verfassen.
Gliedere den Text klar mit Aufzählungspunkten und Emojis. Gib Werte bevorzugt in Euro an bzw. ordne Währungseffekte bei US-Titeln sauber ein.
"""

def generate_market_update(market_data_text):
    print("🤖 Generiere Marktupdate mit Claude...")
    prompt_content = f"Hier sind die aktuellen Marktdaten:\n\n{market_data_text}\n\nBitte erstelle daraus mein tägliches Marktupdate."
    
    # Neue Modelle der Generationen 4 und 5 laut deinem Dashboard
    models_to_try = [
        "claude-5-sonnet-latest",
        "claude-5-fable-latest",
        "claude-4-5-sonnet-latest",
        "claude-4-sonnet-latest",
        "claude-4-haiku-latest"
    ]
    
    for model_name in models_to_try:
        try:
            print(f"🔄 Versuche Modell: {model_name}...")
            response = client.messages.create(
                model=model_name,
                max_tokens=1500,
                temperature=0.3,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt_content}]
            )
            print(f"✅ Marktupdate erfolgreich mit {model_name} generiert!")
            return response.content[0].text
        except Exception as e:
            print(f"⚠️ Fehler bei {model_name}: {e}")
            
    return None

# ==========================================
# 4. Telegram-Versand
# ==========================================
def send_telegram_message(message_text):
    print("📲 Sende Nachricht an Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        res_data = response.json()
        if res_data.get("ok"):
            print("🎉 Telegram-Nachricht erfolgreich zugestellt!")
        else:
            print("⚠️ Versuche Plain-Text-Versand wegen Markdown-Formatierung...")
            payload.pop("parse_mode")
            requests.post(url, json=payload)
            print("🎉 Telegram-Nachricht als Plain-Text zugestellt!")
    except Exception as e:
        print(f"❌ Fehler beim Senden an Telegram: {e}")

# ==========================================
# 5. Hauptablauf
# ==========================================
if __name__ == "__main__":
    data = get_market_data()
    update_text = generate_market_update(data)
    
    if update_text:
        send_telegram_message(update_text)
    else:
        print("❌ Abbruch: Kein Text generiert.")
