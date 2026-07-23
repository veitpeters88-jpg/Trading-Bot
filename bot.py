import os
import sys
import requests
import yfinance as yf
from anthropic import Anthropic

# ---------------------------------------------------------
# 1. API-Keys & Umgebungsvariablen prüfen
# ---------------------------------------------------------
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not ANTHROPIC_API_KEY:
    print("❌ FEHLER: ANTHROPIC_API_KEY ist nicht in den GitHub Secrets gesetzt!")
    sys.exit(1)

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ FEHLER: TELEGRAM_TOKEN oder TELEGRAM_CHAT_ID fehlt in den Secrets!")
    sys.exit(1)

# Anthropic Client initialisieren
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# ---------------------------------------------------------
# 2. Finanzdaten über yfinance abrufen
# ---------------------------------------------------------
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
            # 5 Tage Daten abfragen, um den letzten Schlusskurs und die Veränderung zu berechnen
            hist = ticker.history(period="5d")
            
            if len(hist) >= 2:
                latest_close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                pct_change = ((latest_close - prev_close) / prev_close) * 100
                summary_lines.append(f"- {name}: {latest_close:.2f} USD/Punkte ({pct_change:+.2f}%)")
            else:
                summary_lines.append(f"- {name}: Keine ausreichenden Kurse gefunden")
        except Exception as e:
            summary_lines.append(f"- {name}: Fehler beim Laden ({e})")
            
    return "\n".join(summary_lines)

# ---------------------------------------------------------
# 3. Markt-Update via Claude AI generieren (mit Modell-Fallback)
# ---------------------------------------------------------
SYSTEM_PROMPT = """
Du bist ein erfahrener Finanzanalyst. Deine Aufgabe ist es, aus den gelieferten Marktdaten ein prägnantes, leicht verständliches Börsen-Update auf Deutsch zu verfassen.
Nutze Emojis, gliedere den Text klar mit Aufzählungspunkten und halte den Ton professionell, aber zugänglich.
Achte darauf, Aktienkurse und Prozentveränderungen korrekt einzuordnen.
"""

def generate_market_update(market_data_text):
    print("🤖 Generiere Marktupdate mit Anthropic Claude...")
    
    # Liste gängiger Modell-Bezeichnungen zum automatischen Testen
    TEST_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-7-sonnet-20250219",
        "claude-3-5-haiku-20241022",
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229"
    ]
    
    prompt_content = f"Hier sind die aktuellen Marktdaten:\n\n{market_data_text}\n\nBitte erstelle daraus mein tägliches Marktupdate."
    
    for model_name in TEST_MODELS:
        try:
            print(f"🔄 Teste Modell: {model_name}...")
            response = client.messages.create(
                model=model_name,
                max_tokens=1000,
                temperature=0.3,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt_content}
                ]
            )
            print(f"✅ ERFOLG mit Modell: {model_name}!")
            return response.content[0].text
        except Exception as e:
            print(f"⚠️ Fehlgeschlagen mit {model_name}: {e}")
            
    print("❌ KEIN Modell hat funktioniert. Bitte prüfe deinen API-Key auf console.anthropic.com!")
    return None

# ---------------------------------------------------------
# 4. Nachricht per Telegram versenden
# ---------------------------------------------------------
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
            print(f"❌ Fehler von Telegram API: {res_data}")
    except Exception as e:
        print(f"❌ Netzwerkfehler beim Senden an Telegram: {e}")

# ---------------------------------------------------------
# Hauptablauf
# ---------------------------------------------------------
if __name__ == "__main__":
    # Step 1: Daten abfragen
    data = get_market_data()
    print("\n--- GELADENE DATEN ---")
    print(data)
    print("----------------------\n")
    
    # Step 2: Claude Analyse anfordern
    update_text = generate_market_update(data)
    
    # Step 3: An Telegram schicken
    if update_text:
        send_telegram_message(update_text)
    else:
        print("❌ Abbruch: Kein Text zum Versenden vorhanden.")
