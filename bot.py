import os
import requests
import yfinance as yf
import anthropic

# 1. Umweltvariablen / Secrets laden
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()

def send_telegram_message(text):
    """Hilfsfunktion zum Senden von Telegram-Nachrichten"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram Credentials fehlen.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    res = requests.post(url, json=payload, timeout=10)
    print(f"Telegram Status: {res.status_code}")

def main():
    print("--- TRADING BOT START ---")
    
    # 2. Aktiendaten abrufen (Beispiel: Big Tech & Markt-Indizes)
    tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN"]
    market_data = []

    print("Hole Aktiendaten...")
    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            current_price = info.last_price
            prev_close = info.previous_close
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            market_data.append(f"{symbol}: {current_price:.2f} USD ({change_pct:+.2f}%)")
        except Exception as e:
            print(f"Fehler beim Laden von {symbol}: {e}")

    data_summary = "\n".join(market_data)
    print("Daten geladen:\n", data_summary)

    # 3. Analyse durch Claude (Anthropic) anfordern
    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY fehlt!")
        send_telegram_message(f"📊 *Markt-Update (Ohne KI)*:\n\n{data_summary}")
        return

    print("Sende Daten an Claude für KI-Analyse...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""
    Du bist ein erfahrener Trading-Assistent. Hier sind die aktuellen Marktdaten für ausgewählte Tech-Aktien:

    {data_summary}

    Erstelle ein kurzes, knackiges Update für den Trader auf Deutsch:
    1. Kurze Zusammenfassung der aktuellen Stimmung.
    2. Auffällige Gewinner/Verlierer.
    3. Ein kurzer, pragmatischer Fazit-Satz.
    Halte die Nachricht übersichtlich und ideal nutzbar für eine schnelle Telegram-Nachricht (Nutze Emojis & Markdown-Formatierung).
    """

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        ki_analysis = response.content[0].text
        
        # 4. Gesamte Nachricht zusammenstellen und an Telegram senden
        full_message = f"🤖 *Warren Buffet KI - Markt-Update*\n\n{ki_analysis}"
        send_telegram_message(full_message)
        print("✅ Erfolgreich gesendet!")

    except Exception as e:
        print(f"❌ Fehler bei der Anthropic-API: {e}")
        # Fallback: Sende zumindest die Rohdaten
        send_telegram_message(f"📊 *Markt-Update (KI-Fehler)*:\n\n{data_summary}")

if __name__ == "__main__":
    main()
