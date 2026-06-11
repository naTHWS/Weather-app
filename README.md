# Wetter & Klimaanalyse Würzburg

Ein interaktives Wetter-Dashboard mit 7-Tage-Vorhersage, Deutschlandkarte und
historischer Klimaanalyse (1940–heute). Entstanden als Prüfungsleistung im Modul
**Generative KI** (THWS) – entwickelt mithilfe eines Code-Agenten.

> **Aufgabenstellung:** Auswertung und Visualisierung von Wetterdaten zur
> Identifikation grundlegender Trends und saisonaler Muster.

## Live-Demo

GitHub Pages: https://naTHWS.github.io/Weather-app/

## Funktionen

Das Dashboard ist in drei Tabs gegliedert:

- **Vorhersage** – Aktuelle Bedingungen und stündliche/tägliche 7-Tage-Vorschau
  für den gewählten Ort (Standard: Würzburg).
- **Karte** – Interaktive Deutschlandkarte mit aktuellen Temperaturen
  ausgewählter Städte; Basis für eine spätere Heatmap.
- **Klimaanalyse** – Historische Jahresmitteltemperaturen, gleitende
  10-Jahres-Trends, Abweichung gegenüber der WMO-Referenzperiode 1961–1990 und
  eine Monats-Heatmap.

## Architektur

Das Dashboard ist eine **Single-File-App** (`index.html`) ohne Backend. Die
Wetter- und Klimadaten werden zur Laufzeit direkt im Browser von öffentlichen,
**key-freien** REST-APIs abgerufen.

Bewusst **kein Backend**: Alle genutzten Dienste sind frei und ohne API-Schlüssel
nutzbar. Es gibt daher kein Geheimnis (z. B. einen API-Key), das im Client
versteckt werden müsste – ein Server als Proxy wäre nur dann nötig, wenn ein
geheimer Schlüssel geschützt werden müsste. So bleibt das Deployment minimal
(statisches Hosting via GitHub Pages) und es entsteht keine Angriffsfläche durch
preisgegebene Zugangsdaten.

## Datenquellen (alle ohne API-Key)

- **Open-Meteo Forecast API** – stündliche/tägliche Vorhersage.
- **Open-Meteo Historical Archive (ERA5 / Copernicus, ECMWF)** – historische
  Tagesmitteltemperaturen ab 1940 für die Klimaanalyse.
- **Open-Meteo Geocoding API** – Ortssuche (Stadt → Koordinaten).
- **CARTO Basemaps (OpenStreetMap-Daten)** – dunkle Kartenkacheln.

## Analyse-Methodik

Die historische Klimaauswertung:

1. Lädt Tagesmitteltemperaturen (ERA5) ab 1940 für die gewählten Koordinaten.
2. Aggregiert zu **jährlichen Mitteltemperaturen**.
3. Berechnet einen **gleitenden 10-Jahres-Durchschnitt** zur Trenddarstellung.
4. Bildet die **Abweichung** jedes Jahres gegenüber dem Mittel der
   WMO-Referenzperiode **1961–1990** – dem internationalen Standard für
   Klimavergleiche.
5. Erzeugt monatliche Mittelwerte für die Heatmap.

Dieselbe Auswertung ist zusätzlich als eigenständiges **Python-Skript**
(`analysis.py`, mit pandas/numpy) implementiert und kann zur reproduzierbaren,
dokumentierten Analyse separat ausgeführt werden.

## Projektstruktur

```
.
├── index.html                  # Dashboard (Frontend, Single-File-App, kein Backend)
├── analysis.py                 # Eigenständige Python-Klimaanalyse (pandas/numpy)
├── requirements.txt            # Python-Abhängigkeiten für analysis.py
└── docs/
    ├── PROJECT_STATUS.md       # Entwicklungsdokumentation / Verlauf
    ├── aufgabenstellung.txt    # Original-Aufgabenstellung
    ├── design/
    │   ├── design-guide.html   # Design-Referenz (Farben, Typografie, Tokens)
    │   ├── design-guide.png    # Design-Guide als Bild
    │   └── dashboard-beispiel.png  # Layout-Referenzbild
    └── dev-notes/              # Datierte Entwicklungs-Notizen (Feedback-Runden)
```

## Lokale Ausführung

**Dashboard:** `index.html` ist eigenständig und kann direkt im Browser geöffnet
oder über einen beliebigen statischen Webserver ausgeliefert werden (z. B.
GitHub Pages). Keine Installation, kein Server nötig.

**Python-Analyse (optional, reproduzierbar):**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python analysis.py               # gibt die berechneten Klimatrends aus
```

## Technologie-Stack

HTML/CSS · JavaScript · Apache ECharts · MapLibre GL JS · Python (pandas, numpy)

## Kontext

Prüfungsleistung im Modul *Generative KI*, THWS – Sommersemester 2026.
Schwerpunkt: Datenanalyse und -visualisierung von Wetterdaten,
umgesetzt mithilfe eines Code-Agenten.
