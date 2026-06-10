# Wetter & Klimaanalyse Würzburg

Ein interaktives Wetter-Dashboard mit 7-Tage-Vorhersage, Deutschlandkarte und
historischer Klimaanalyse (1940–heute). Entstanden als Prüfungsleistung im Modul
**Generative KI** (THWS) – entwickelt mithilfe eines Code-Agenten.

> **Aufgabenstellung:** Auswertung und Visualisierung von Wetterdaten zur
> Identifikation grundlegender Trends und saisonaler Muster. Die statistische
> Analyse erfolgt in **Python**; das Dashboard stellt die Ergebnisse dar.

## Live-Demo

Frontend (GitHub Pages): https://naTHWS.github.io/Weather-app/

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

Das Projekt besteht aus zwei Schichten:

| Schicht | Technologie | Aufgabe |
|---|---|---|
| **Analyse-Layer (Python)** | FastAPI, pandas, numpy | Lädt historische Klimadaten, berechnet Jahresmittel, gleitende Durchschnitte und Referenzabweichungen. Stellt das Ergebnis über die REST-API `/climate-trends` bereit. |
| **Dashboard (Frontend)** | HTML, Vanilla JS, ECharts, MapLibre GL | Single-File-App (`index.html`). Visualisiert Vorhersage, Karte und die vom Python-Layer gelieferten Klimatrends. |

Die **Vorhersage** und die **Kartentemperaturen** werden direkt von öffentlichen
Wetter-APIs (siehe unten) bezogen; die **historische Klimaanalyse** ist der in
Python implementierte Kern der Auswertung (`analysis.py`).

## Datenquellen

- **Open-Meteo Forecast API** – stündliche/tägliche Vorhersage (kein API-Key).
- **Open-Meteo Historical Archive (ERA5 / Copernicus, ECMWF)** – historische
  Tagesmitteltemperaturen ab 1940 für die Klimaanalyse.
- **Bright Sky / DWD MOSMIX** – offizielle DWD-Daten (im Python-Backend genutzt).
- **Open-Meteo Geocoding API** – Ortssuche (Stadt → Koordinaten).

## Analyse-Methodik

Die Klimaauswertung in `analysis.py`:

1. Lädt Tagesmitteltemperaturen (ERA5) ab 1940 für die gewählten Koordinaten.
2. Aggregiert zu **jährlichen Mitteltemperaturen** (mit Mindest-Datenabdeckung
   pro Jahr, damit unvollständige Jahre die Statistik nicht verzerren).
3. Berechnet **gleitende 5- und 10-Jahres-Durchschnitte** zur Trenddarstellung.
4. Bildet die **Abweichung** jedes Jahres gegenüber dem Mittel der
   WMO-Referenzperiode **1961–1990** – der internationale Standard für
   Klimavergleiche.
5. Erzeugt monatliche Mittelwerte für die Heatmap.

## Projektstruktur

```
.
├── index.html        # Dashboard (Frontend, Single-File-App)
├── main.py           # FastAPI-Server: API-Endpunkte
├── analysis.py       # Python-Klimaanalyse (pandas/numpy)
├── find_station.py   # Hilfsskript: DWD-Stationssuche
├── requirements.txt  # Python-Abhängigkeiten
├── render.yaml       # Deployment-Konfiguration (Render)
├── Design Guide.html # Design-Referenz (Farben, Typografie, Tokens)
└── PROJECT_STATUS.md # Entwicklungsdokumentation / Verlauf
```

## Lokale Ausführung

**Backend (Python-Analyse):**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload        # läuft auf http://localhost:8000
```

Endpunkte:
- `GET /weather?lat=..&lon=..` – 7-Tage-Vorhersage
- `GET /climate-trends?lat=..&lon=..` – historische Klimatrends
- `GET /map-weather` – aktuelle Temperaturen deutscher Städte

**Frontend:**

`index.html` ist eine eigenständige Datei und kann direkt im Browser geöffnet
oder über einen beliebigen statischen Webserver ausgeliefert werden (z. B.
GitHub Pages).

## Technologie-Stack

Python · FastAPI · pandas · numpy · HTML/CSS · JavaScript · Apache ECharts ·
MapLibre GL JS

## Kontext

Prüfungsleistung im Modul *Generative KI*, THWS – Sommersemester 2026.
Schwerpunkt: Datenanalyse und -visualisierung von Wetterdaten mit Python,
umgesetzt mithilfe eines Code-Agenten.
