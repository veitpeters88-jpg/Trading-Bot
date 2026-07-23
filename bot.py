import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """
Du bist ein präziser Finanz-Analyst. Wenn du nach einem Marktupdate gefragt wirst, erstelle eine klare, strukturierte Übersicht im typischen Claude-Stil:

1. **Markt-Überblick (Makro & Indices):** Wichtige globale Indizes (S&P 500, Nasdaq 100, DAX, Euro Stoxx 50) mit Fokus auf den europäischen / EUR-Raum.
2. **Tech- & Einzelwerte:** Fokus auf relevante Big-Tech-Entwicklungen (z. B. NVIDIA, Apple, Microsoft) und deren Auswirkung auf den Gesamtmarkt.
3. **Zinsen & Inflation:** Relevante News von ECB/FED und Makrodaten.
4. **Fazit / Kurzausblick:** Kompakte Zusammenfassung der aktuellen Marktstimmung.

WICHTIG: 
- Gib Zahlen und Kurse bevorzugt in Euro (€) an bzw. hebe den EUR/USD-Wechselkurs hervor, wenn US-Aktien thematisiert werden.
- Nutze Markdown (Fettdruck, Aufzählungspunkte, Tabellen), um das Update extrem übersichtlich und leicht lesbar zu gestalten.
"""

def generate_market_update():
    try:
        response = client.messages.create(
            # Verwende 'claude-3-5-sonnet-latest' (oder 'claude-3-7-sonnet-latest')
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
        
        market_update_text = response.content[0].text
        return market_update_text

    except Exception as e:
        print(f"❌ Fehler bei der API-Abfrage: {e}")
        return None

if __name__ == "__main__":
    update = generate_market_update()
    if update:
        print(update)
