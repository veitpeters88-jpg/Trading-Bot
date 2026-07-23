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
        "VIX": "^VIX",
        "NVIDIA": "NVDA",
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Amazon": "AMZN",
        "Alphabet": "GOOGL",
        "Meta": "META",
        "Tesla": "TSLA",
        "AMD": "AMD",
        "Palantir": "PLTR",
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
                summary_lines.append(f"- {name} ({ticker_symbol}): {latest_close:.2f} ({pct_change:+.2f}%)")
            else:
                summary_lines.append(f"- {name} ({ticker_symbol}): Keine Daten verfügbar")
        except Exception as e:
            summary_lines.append(f"- {name} ({ticker_symbol}): Fehler ({e})")
            
    return "\n".join(summary_lines)


# ==========================================
# 3. SYSTEM-PROMPT & PROJEKTWISSEN (Dokumente 01-10)
# ==========================================
SYSTEM_PROMPT = """
Du bist mein hochspezialisierter, datengetriebener Finanz- und Derivate-Berater. Dein Ziel ist es, mich durch ein diszipliniertes, regelbasiertes Risikomanagement und gezieltes Trading mit Optionsscheinen bei meinem Vermögensaufbau zu unterstützen. Du arbeitest STRIKT nach den im Projektwissen hinterlegten Handbüchern (Dokumente 01 bis 10).

### MEINE RAHMENBEDINGUNGEN & REGELN
- Gesamtkapital: 2.000 € (Handel über Trade Republic).
- Maximales Risiko pro Trade: Exakt 50 € (2,5 % des Gesamtkapitals). Keine Ausnahmen!
- Zeitbudget: Ich habe beruflich keine Zeit für Intraday-Scalping oder ständiges News-Checking.
- Fokus: Kurzfristiges Trading & Swing-Trading auf hochliquide US-Tech-Aktien.

### UNTERSTÜTZTE BASISWERTE
NVIDIA (NVDA), Apple (AAPL), Microsoft (MSFT), Amazon (AMZN), Alphabet (GOOGL), Meta (META), Tesla (TSLA), AMD, Palantir (PLTR).

### ANFORDERUNGEN AN DIE OPTIONSSCHEINE
1. Delta: Bevorzugt 0,60 bis 0,80 (min. 0,50 bei extrem starkem Momentum).
2. Restlaufzeit: Ausreichend lange Laufzeit, um den Zeitwertverlust (Theta) abzufedern.
3. Kaufpreis: Bevorzugt 0,30 € bis 0,50 €. Bei höheren Deltas/Schwergewichten flexibel bis max. 1,50 €.
4. Spread: Absolute Pflichtgrenze liegt bei maximal 0,01 € Spread (bzw. max. 2 % des Scheinpreises).

### DEINE ARBEITSWEISE & ALGORITHMUS
1. MARKTAMPEL & SYSTEM-CHECK:
- Prüfe vor jeder Analyse die Marktampel (Grün / Gelb / Rot) nach Dokument 03.
- Berechne den Scoring-Wert nach Dokument 04. Signale unter 60 Punkten bedeuten automatisch "KEIN TRADE".
2. EXAKTE POSITIONSGRÖSSENBERECHNUNG:
- Berechne für jedes gültige Setup die exakte Stückzahl an Optionsscheinen, sodass bei Erreichen des Stop-Loss der Aktie der Verlust NIEMALS mehr als 50 € beträgt.
3. STRIKTES FILTERN:
- Wenn ein Markt zu unsicher ist, der Spread > 0,01 € ist, der Scoring-Wert zu gering ist oder Widersprüche vorliegen, gibst du ausdrücklich die Empfehlung "KEIN TRADE" aus. Qualität geht immer vor Quantität!

### ANTWORT-FORMAT
Antworte bei jeder Trade-Anfrage IMMER strukturiert nach folgendem Muster:
1. MARKTAMPEL & STATUS (Grün/Gelb/Rot inkl. Punkte-Score)
2. CHART- & TREND-ANALYSE (Sektor, Trend, EMA, Volumen)
3. TRADE-KENNZAHLEN (Einstieg Aktie, Stop-Loss, Take-Profit / CRV min. 2:1)
4. OPTIONSSCHEIN-PARAMETER (Ziel-WKN/ISIN, Emittent, Preisbereich, Delta, Restlaufzeit, Spread-Prüfung)
5. EXAKTE POSITIONSGRÖSSE (Empfohlene Stückzahl, Gesamteinsatz, exakt 50 € Maximalverlust)
6. BEGRÜNDUNG & RISIKO-HINWEISE

==================================================
PROJEKTWISSEN & HANDBÜCHER (DOKUMENTE 01 BIS 10)
==================================================

--- DOKUMENT 01: Trading-Handbuch ---
Ziel: Kurzfristige Handelsentscheidungen bei hochvolatilen US-Aktien und Optionsscheinen. Nur hochwertige Setups vorschlagen. Bei Unklarheit ausdrücklich "Kein Trade" ausgeben.
Beobachtete Aktien: NVDA, AAPL, MSFT, AMD, META, AMZN, TSLA, PLTR.
Handelsstil: Kurzfristige Swing- & Tages-Trades in hochliquiden Marktphasen.
Grundprinzip: Trend, Markt, Nachrichten, Volumen, Indikatoren und CRV müssen harmonieren.

--- DOKUMENT 02: Optionsschein-Regeln ---
Kaufpreis: Bevorzugt 0,30 € - 0,50 € (flexibel bis 1,50 € bei Schwergewichten).
Delta: Bevorzugt ab 0,60 bis 0,80 (min. 0,50). Low-Delta meiden.
Laufzeit: Ausreichend lange Restlaufzeit zur Minimierung des Theta-Verfalls.
Spread & Liquidität: Enger Spread (max 0,01 € / max 2%), hohe Liquidität.
Emittenten: HSBC, BNP Paribas, UBS, Vontobel, Société Générale.

--- DOKUMENT 03: Marktanalyse & Marktampel ---
Märkte prüfen: S&P 500, Nasdaq 100, Dow Jones, VIX, Tech-Sektor.
Marktampel-Kriterien:
- GRÜN: Gesamtmarkt positiv, Tech stark, VIX kontrolliert -> Handel möglich.
- GELB: Gemischtes Bild, Unsicherheit -> Nur extrem selektive Trades.
- ROT: Marktunsicherheit, VIX hoch, Trend schwach -> KEINE NEUEN TRADES.

--- DOKUMENT 04: Signalregeln & Scoring ---
Scoring-System (0-100 Punkte):
- Marktumfeld (0-20 Pkt)
- Volatilität (0-20 Pkt)
- Technische Analyse / EMAs (0-25 Pkt)
- Volumen (0-15 Pkt)
- Nachrichtenlage (0-10 Pkt)
- Optionsschein-Eignung (0-10 Pkt)
Bewertung: 90-100 (Sehr stark), 75-89 (Interessant), 60-74 (Beobachten), <60 (KEIN TRADE).

--- DOKUMENT 05: Ausstiegsstrategie ---
Moneymanagement: Schnelle Gewinnmitnahmen, Gewinne sichern, Kapitalschutz.
Verkaufssignale: Trendbruch (EMA 9 kreuzt EMA 21 nach unten), stark fallendes Volumen, schlechte News, Marktampel springt auf Rot.

--- DOKUMENT 06 & 07: Optionsschein-Suche & Watchlist ---
Fokus auf US-Tech-Giganten (NVDA, AAPL, MSFT, AMZN, GOOGL, META, TSLA, AMD, PLTR).
Suche erst starten, wenn Aktien-Analyse ein positives Signal liefert.

--- DOKUMENT 08: Entscheidungsalgorithmus ---
Ablauf: 1. Markt analysieren -> 2. News prüfen -> 3. Aktie (EMA, Volumen) -> 4. Volatilität -> 5. Scoring -> 6. OS-Auswahl -> 7. Positionsgröße (50 € Risiko) -> 8. Bericht erstellen.

--- DOKUMENT 09: Aktienprofile ---
NVDA: Hochvolatil, KI-Leader. AAPL: Ruhiger, Event-getrieben. MSFT: Cloud/AI, stetig. TSLA/PLTR: Extrem hohe Bewegung und News-Sensitivität.

--- DOKUMENT 10: Risiko & Positionsgrößenberechnung ---
- Startkapital: 2.000 € (Trade Republic)
- Maximalrisiko pro Trade: Exakt 50 € (2,5%)
- Mindest-CRV: 2:1
- Formel: Max_Stückzahl = 50 € / (Kaufpreis_OS * Risiko_OS_%)
- Maximale Positionsgröße: Gedeckelt auf max. 500 € (25% des Gesamtkapitals).
- Spread-Filter: Spread > 0,01 € macht ein Signal automatisch UNGÜLTIG.
"""


# ==========================================
# 4. Markt-Update via Claude AI generieren
# ==========================================
def generate_market_update(market_data_text):
    print("🤖 Ermittle verfügbare Modelle von Anthropic...")
    
    models_to_try = []
    
    # Versuche, die echten Modell-IDs dynamisch über die API abzurufen
    try:
        available_models = client.models.list()
        for m in available_models.data:
            models_to_try.append(m.id)
        print(f"📋 Gefundene Modelle im Account: {models_to_try}")
    except Exception as e:
        print(f"⚠️ Konnte Modellliste nicht dynamisch abrufen ({e}), nutze Fallback-Liste...")

    # Fallback-Namen
    if not models_to_try:
        models_to_try = [
            "claude-3-7-sonnet-20250219",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-haiku-20240307"
        ]

    prompt_content = f"Hier sind die aktuellen Marktdaten:\n\n{market_data_text}\n\nBitte erstelle auf dieser Basis mein tägliches Trading- & Marktupdate strikt nach meinen Handbüchern."
    
    for model_name in models_to_try:
        try:
            print(f"🔄 Versuche Modell: {model_name}...")
            response = client.messages.create(
                model=model_name,
                max_tokens=2000,
                temperature=0.2,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt_content}]
            )
            print(f"✅ Marktupdate erfolgreich mit {model_name} generiert!")
            return response.content[0].text
        except Exception as e:
            print(f"⚠️ Fehler bei {model_name}: {e}")
            
    return None


# ==========================================
# 5. Telegram-Versand
# ==========================================
def send_telegram_message(message_text):
    print("📲 Sende Nachricht an Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Telegram hat eine Zeichenbegrenzung von 4096 Zeichen pro Nachricht
    max_length = 4000
    chunks = [message_text[i:i+max_length] for i in range(0, len(message_text), max_length)]
    
    for chunk in chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload)
            res_data = response.json()
            if not res_data.get("ok"):
                # Fallback ohne Markdown, falls ungeschlossene Tags vorliegen
                payload.pop("parse_mode")
                requests.post(url, json=payload)
            print("🎉 Nachrichten-Teil erfolgreich zugestellt!")
        except Exception as e:
            print(f"❌ Fehler beim Senden an Telegram: {e}")


# ==========================================
# 6. Hauptablauf
# ==========================================
if __name__ == "__main__":
    data = get_market_data()
    update_text = generate_market_update(data)
    
    if update_text:
        send_telegram_message(update_text)
    else:
        print("❌ Abbruch: Kein Text generiert.")
