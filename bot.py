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
    
    # 2. Aktiendaten abrufen
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

    # 3. Prüfen ob Key vorhanden
    if not ANTHROPIC_API_KEY:
        print("❌ FEHLER: ANTHROPIC_API_KEY ist in GitHub Secrets nicht gesetzt!")
        send_telegram_message(f"📊 *Markt-Update (Key fehlt)*:\n\n{data_summary}")
        return

    print("Sende Daten an Claude für KI-Analyse...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Ausführlicher Prompt für mehr Tiefgang
    prompt = f"""
    Du bist 'Warren Buffet KI', ein hochqualifizierter Trading- und Marktanalyst.
    Hier sind die aktuellen Daten zu den wichtigsten US-Tech-Aktien:

    {data_summary}

    Erstelle eine ausführliche, fundierte und übersichtliche Marktanalyse auf Deutsch für Telegram:

    📌 **1. Gesamtstimmung & Marktlage**
    Analysiere die Bewegungen im Tech-Sektor auf Basis der vorliegenden Zahlen. Was fällt im Gesamtbild auf?

    📈 **2. Einzelwert-Analyse (Top & Flop)**
    Gehe gezielt auf die stärksten Gewinner und Verlierer ein und ordne die Prozentbewegungen kurz ein.

    🎯 **3. Pragmatisches Fazit & Ausblick**
    Gib dem Trader 2-3 konkrete Beobachtungspunkte an die Hand, worauf in den nächsten Handelsstunden / Tagen geachtet werden sollte.

    Formatiere die Nachricht lesefreundlich mit Emojis, Fettgedrucktem und Aufzählungspunkten.
    """

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        ki_analysis = response.content[0].text
        
        full_message = f"🤖 *Warren Buffet KI - Ausführliche Analyse*\n\n{ki_analysis}"
        send_telegram_message(full_message)
        print("✅ KI-Analyse erfolgreich gesendet!")

    except Exception as e:
        print(f"❌ Exakter Fehler bei der Anthropic-API: {e}")
        send_telegram_message(f"📊 *Markt-Update (KI-Fehler)*:\n\n{data_summary}\n\n_Hinweis: KI-Schnittstelle hat einen Fehler gemeldet. Prüfe die GitHub-Logs._")

if __name__ == "__main__":
    main()
