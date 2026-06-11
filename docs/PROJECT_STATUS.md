# Projekt-Dokumentation: Wetter Dashboard Würzburg

> **⚠️ Aktueller Stand siehe [PHASE 5](#phase-5-vanilla-single-file-app--design-guide-v02-9-juni-2026) am Ende des Dokuments.**
> Die Phasen 1–4 beschreiben frühere Architekturen (Streamlit, FastAPI-Backend + Bright Sky/DWD,
> Glassmorphismus-Frontend mit `style.css`/`app.js`). Diese sind **historisch** und entsprechen
> nicht mehr der aktuellen App. Die Live-App ist seit dem 8./9. Juni 2026 eine einzelne, editierbare
> `index.html` (Vanilla, Open-Meteo direkt, **kein Backend**), die den Design Guide v0.2 umsetzt.

---

## PHASE 1: Prototyping (Streamlit)


### 1. Übersicht
In der ersten Phase wurde ein schneller Prototyp mit dem Streamlit-Framework erstellt. Ziel war es, die Wetterdaten der Open-Meteo API für Würzburg grundlegend zu visualisieren.

---

## PHASE 2: Refactoring & Modernisierung (Decoupled Web-App)

### 1. Übersicht
Das Projekt wurde grundlegend umgestaltet, um eine professionelle Trennung von Backend und Frontend zu erreichen.

### 2. Technischer Stack (Phase 2)
*   **Backend:** FastAPI (Python, Uvicorn)
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
*   **3D-Karte:** MapLibre GL JS
*   **Diagramme:** Apache ECharts
*   **Design:** Glassmorphism-Stil

---

## PHASE 3: Akademische Datenanalyse (DWD & Trends)

### 1. Übersicht
In dieser Phase liegt der Fokus auf der Erfüllung der akademischen Anforderungen: Analyse historischer Wetterdaten zur Identifikation von Klimatrends. Weg von reinen Vorhersagen, hin zur statistischen Auswertung offizieller DWD-Daten.

### 2. Technischer Stack (Phase 3)
*   **Datenquelle:** Deutscher Wetterdienst (DWD) via `wetterdienst` Library.
*   **Analyse:** Pandas & Numpy (Gleitende Durchschnitte, Klimareferenz 1961-1990).
*   **Datenverarbeitung:** Polars.

### 3. Implementierte Features
*   **`analysis.py`:** Automatischer Download und Aufbereitung der DWD-Daten für Würzburg (ID 5705).
*   **API-Endpoint `/climate-trends`:** Liefert jährliche Mitteltemperaturen und 5/10-Jahres-Trends.
*   **Caching:** Die Analyse wird beim ersten Aufruf durchgeführt und zwischengespeichert.

### 4. Nächste Schritte
*   Visualisierung der Langzeittrends im Frontend.
*   Erstellung einer wissenschaftlichen Dokumentation der Ergebnisse.

---
*Zuletzt aktualisiert am: 22. Mai 2026*

---
Claude setup text

Claude desinger --> Desing themplate erstellt für die website !

# Entwicklungsdokumentation – Würzburg Wetter & Klimaanalyse
**Session-Protokoll | 26. Mai 2026**

---

## Inhaltsverzeichnis

1. [Ausgangslage & Zielsetzung](#1-ausgangslage--zielsetzung)
2. [Neues Frontend-Dashboard](#2-neues-frontend-dashboard)
3. [Bugfix: wetterdienst API-Kompatibilität](#3-bugfix-wetterdienst-api-kompatibilität)
4. [Datenmigration: Open-Meteo → Bright Sky / DWD](#4-datenmigration-open-meteo--bright-sky--dwd)
5. [Finaler Technischer Stack](#5-finaler-technischer-stack)
6. [Dateiübersicht & Änderungen](#6-dateiübersicht--änderungen)

---

## 1. Ausgangslage & Zielsetzung

### 1.1 Ausgangszustand

Das Projekt befand sich in **Phase 3** (akademische Klimaanalyse). Das bestehende Frontend (`index.html`, `style.css`, `app.js`) nutzte ein einfaches Glassmorphismus-Layout mit einer MapLibre-Karte im Hintergrund und zwei seitlichen Panels für Diagramme. Der Nutzer war mit dieser Oberfläche **nicht zufrieden**.

**Probleme im Ausgangszustand:**
- Visuell unattraktives Design (leere Panels, keine Hierarchie)
- Keine 7-Tage-Vorschau oder aktuelle Wetterbedingungen sichtbar
- Backend-Endpoint `/climate-trends` lieferte **HTTP 500** (interner Serverfehler)
- Wetter-Endpoint `/weather` lieferte **HTTP 502** (Open-Meteo-Ausfall)
- Keine Fallback-Strategie bei API-Ausfall

### 1.2 Ziele der Session

- Neues, professionelles Dashboard-Design erstellen
- Den 500-Fehler im Klimadaten-Endpoint beheben
- Eine zuverlässigere Datenquelle für aktuelle Wetterdaten finden und einbinden
- Das Dashboard auch bei API-Ausfall vollständig darstellbar machen

---

## 2. Neues Frontend-Dashboard

### 2.1 Design-Konzept

Das neue Dashboard orientiert sich an modernen Wetter-Apps (Referenzbild: `docs/design/dashboard-beispiel.png`) und setzt folgende Design-Prinzipien um:

| Prinzip | Umsetzung |
|---|---|
| **Dark Theme** | Hintergrund `#080c14`, Karten `rgba(17,24,39,.78)` |
| **Atmosphärische Tiefe** | Mehrschichtige Radial-Gradienten (Orange/Blau/Violett) + SVG-Noise-Textur |
| **Glassmorphismus** | `backdrop-filter: blur(18px)` auf allen Karten |
| **Typografie-Hierarchie** | *Space Grotesk* für Zahlen/Headlines, *Inter* für Body-Text |
| **Farbkodierung** | Orange `#f97316` = Temperatur, Blau `#38bdf8` = Niederschlag/Wind, Violett `#a78bfa` = Klimatrends |
| **Responsive** | CSS Grid mit Tailwind-Breakpoints (`md:col-span-*`) |

### 2.2 Architektur: Single-File-App

Das gesamte Frontend wurde als **eine einzige `index.html`** umgesetzt (kein externes CSS, kein externes JS außer CDN-Bibliotheken). Das vereinfacht Deployment und Wartung erheblich.

**Verwendete CDN-Bibliotheken:**
```html
<!-- Layout & Utility-CSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Diagramme -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>

<!-- Schriften -->
<link href="https://fonts.googleapis.com/css2?family=Inter&family=Space+Grotesk&display=swap">
```

### 2.3 Tab-Navigation

Das Dashboard ist in zwei Hauptbereiche gegliedert, die über eine Tab-Navigation umgeschaltet werden:

```javascript
function switchTab(tab) {
  ['forecast', 'climate'].forEach(t => {
    document.getElementById('tab-' + t).classList.toggle('active', t === tab);
    document.getElementById('section-' + t).classList.toggle('active', t === tab);
  });
  // Wichtig: ECharts-Diagramme nach Layout-Wechsel resizen
  setTimeout(() => [cTemp, cPrecip, cWind, cHum, cTrend, cDev].forEach(c => c.resize()), 60);
}
```

### 2.4 Tab „Vorhersage" – Komponenten

#### Hero-Karte (aktuelle Wetterbedingungen)
Zeigt Echtzeit-Temperatur, Tages-Maximum/Minimum, Gesamtniederschlag und Wetterbeschreibung. Die Temperaturzahl nutzt einen CSS-Gradient-Text-Effekt:

```css
.temp-hero {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(3rem, 8vw, 5rem);
  background: linear-gradient(140deg, #fbbf24 0%, #f97316 55%, #ea580c 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

#### 7-Tage-Forecast-Strip
Die stündlichen API-Daten (168 Einträge) werden nach lokalen Datum-Strings gruppiert. Für jeden Tag wird berechnet:
- Tages-Maximum und -Minimum der Temperatur
- Gesamtniederschlag
- Repräsentatives Icon (Mittagsstunde des jeweiligen Tages)

```javascript
// Gruppierung der stündlichen Einträge nach lokalem Datum
const byDay = {};
entries.forEach(e => {
  const d = new Date(e.timestamp).toLocaleDateString('de-DE');
  if (!byDay[d]) byDay[d] = [];
  byDay[d].push(e);
});
```

#### Diagramme (ECharts)
Alle sechs Diagramme nutzen eine gemeinsame Basis-Konfiguration (`BOPT`) und werden mit dem SVG-Renderer initialisiert (besser skalierbar als Canvas):

```javascript
const cTemp = echarts.init(document.getElementById('chart-temp'), null, { renderer: 'svg' });
```

Diagrammtypen im Tab „Vorhersage":

| Diagramm | Typ | Datenfeld | Farbe |
|---|---|---|---|
| Temperaturverlauf 24h | Line mit Area | `temperature` | Orange `#f97316` |
| Niederschlag 24h | Bar | `precipitation` | Blau `#38bdf8` |
| Windgeschwindigkeit 24h | Line (2 Serien: Wind + Böen) | `wind_speed`, `wind_gust_speed` | Blau |
| Luftfeuchtigkeit 24h | Line mit Area | `relative_humidity` | Violett `#a78bfa` |

#### Metrikkarten
Vier kompakte Karten zeigen Momentanwerte der aktuellen Stunde:
- **Wind**: Geschwindigkeit + Böen + Windrichtung (konvertiert aus Grad in Himmelsrichtung)
- **Luftdruck**: Druck auf Meereshöhe in hPa
- **Luftfeuchtigkeit**: Relative Feuchte in %
- **Bewölkung**: Bedeckungsgrad + Sichtweite in km

```javascript
function windDirLabel(deg) {
  const dirs = ['N', 'NO', 'O', 'SO', 'S', 'SW', 'W', 'NW'];
  return dirs[Math.round(deg / 45) % 8];
}
```

#### SVG-Wettericons
Statt einer externen Icon-Bibliothek wurden alle Wettericons als **inline SVG** implementiert. Die `weatherIcon()`-Funktion wählt anhand des `icon`-Felds der Bright Sky API das passende Symbol:

| Bright Sky Icon | Dargestelltes Icon |
|---|---|
| `clear-day` / `clear-night` | Sonne mit Strahlen |
| `partly-cloudy-day/night` | Sonne + Wolke |
| `cloudy` | Wolke |
| `rain` / `drizzle` / `sleet` | Wolke mit Regentropfen |
| `snow` | Wolke mit Schneeflocken |
| `thunderstorm` | Wolke mit Blitz |
| `fog` | Drei horizontale Nebellinien |

### 2.5 Tab „Klimaanalyse" – Komponenten

#### Stationsbanner
Zeigt Metadaten der DWD-Station sowie berechnete Kennwerte:
- Referenzmittel der Periode 1961–1990
- Abweichung des 10-Jahres-Mittels der letzten Dekade vom Referenzwert
- Anzahl der Datenjahre

```javascript
const recent = d.annual_temp.filter(Boolean).slice(-10);
const rm     = recent.reduce((a, b) => a + b, 0) / recent.length;
const diff   = (rm - d.reference_mean).toFixed(2);
```

#### Klimatrend-Diagramm
Dreilinien-Chart mit:
1. **Jahresmittelwerte** (dünne violette Linie mit Punkten)
2. **Gleitender 5-Jahres-Durchschnitt** (violett, mittel)
3. **Gleitender 10-Jahres-Durchschnitt** (orange, breit) – zeigt den Langzeittrend deutlich

#### Warming-Stripes-Diagramm
Balkendiagramm mit ECharts `visualMap`-Komponente. Die Farbe jedes Balkens kodiert die Temperaturabweichung vom Referenzwert:

```javascript
visualMap: {
  show: false,
  min: -2,
  max: 2,
  inRange: {
    color: ['#1d4ed8', '#3b82f6', '#93c5fd', '#e0f2fe',
            '#fef3c7', '#fb923c', '#dc2626', '#7f1d1d']
  }
}
```

Dies entspricht der wissenschaftlichen Warming-Stripes-Darstellung (blau = kälter als Referenz, rot = wärmer).

### 2.6 Fallback-Mechanismus (Demo-Daten)

Da externe APIs temporär ausfallen können, wurde ein vollständiger Fallback implementiert. Bei API-Fehler wird lokal **synthetisch generierte Wetterdaten** für Würzburg erzeugt, sodass alle Diagramme dennoch korrekt gerendert werden:

```javascript
async function loadWeather() {
  let data, isDemo = false;
  try {
    const res = await fetch(`${API}/weather`, { signal: AbortSignal.timeout(9000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
    setStatus('online', 'DWD');
  } catch (err) {
    console.warn('[Weather] Fallback auf Demo-Daten:', err.message);
    setStatus('offline');
    data  = buildDemoWeather();   // <– generiert realistische Musterdaten
    isDemo = true;
  }
  // … Rendering mit data.weather (gleiche Struktur in beiden Fällen)
}
```

Die Demo-Daten simulieren realistische Würzburger Werte:
- Temperatur: Tagesgang mit Sinuskurve (Nacht ~11°C, Tag ~22°C)
- Niederschlag: an 2 von 7 Tagen nachmittags
- Wind: Zufallswerte 8–20 km/h
- Luftfeuchtigkeit: 50–85%

---

## 3. Bugfix: wetterdienst API-Kompatibilität

### 3.1 Fehlerbild

Beim Aufruf von `GET /climate-trends` lieferte der FastAPI-Server **HTTP 500**. Der vollständige Traceback (ermittelt durch direktes Ausführen von `analysis.py`):

```
AttributeError: 'Resolution' object has no attribute 'strip'

File "wetterdienst/model/metadata.py", line 310, in parse
    resolution = resolution and resolution.strip().lower()
                                ^^^^^^^^^^^^^^^^
AttributeError: 'Resolution' object has no attribute 'strip'
```

### 3.2 Ursachenanalyse

Die installierte Version **`wetterdienst 0.121.0`** hatte zwischen dem Zeitpunkt der ursprünglichen Code-Erstellung und der aktuellen Version eine **Breaking Change** in der API eingeführt:

| Aspekt | Alter Code (kaputt) | Neue API (0.121.0) |
|---|---|---|
| Resolution-Übergabe | `Resolution.DAILY` (Enum-Objekt) | `"daily"` (String) |
| Period-Übergabe | `[Period.HISTORICAL]` (Enum-Liste) | `"historical"` (String) |
| Datenabruf-Methode | `.values.all().to_pandas()` | `.values.all().df` → `.to_pandas()` |
| Rückgabetyp | Pandas DataFrame | **Polars DataFrame** (konvertierung nötig) |
| Parameter-Name | `temperature_air_mean_200` | `temperature_air_mean_2m` |

### 3.3 Diagnosevorgehen

```bash
# 1. API-Endpoint direkt testen
GET http://localhost:8000/climate-trends  → HTTP 500

# 2. Analyseskript isoliert ausführen
python -c "from analysis import get_historical_trends; get_historical_trends()"
→ AttributeError: 'Resolution' object has no attribute 'strip'

# 3. Korrekte Signatur ermitteln
python -c "import inspect; from wetterdienst.provider.dwd.observation import DwdObservationRequest; print(inspect.signature(DwdObservationRequest))"
→ (parameters: '_PARAMETER_TYPE', ..., periods: 'str | Period | set[Period] | None' = None)

# 4. Korrektes Parameter-Format durch systematisches Testen ermitteln
→ parameters=[('daily', 'kl')]  # Liste von String-Tupeln

# 5. Rückgabe-API erkunden
→ values.all().df  # Polars DataFrame (nicht .to_pandas())

# 6. Korrekten Parameter-Namen finden
→ 'temperature_air_mean_2m'  (nicht 'temperature_air_mean_200')
```

### 3.4 Lösung in `analysis.py`

```python
# ALT (fehlerhaft):
request = DwdObservationRequest(
    parameters=[(Resolution.DAILY, "kl")],
    periods=[Period.HISTORICAL]
)
values = stations.values.all()
df = values.to_pandas()
df_temp = df[df['parameter'].str.contains('temperature_air_mean_200', ...)]

# NEU (korrekt für wetterdienst 0.121.0):
request = DwdObservationRequest(
    parameters=[("daily", "kl")],   # String-Tupel, kein Enum
    periods="historical"            # String, keine Liste
)
values    = stations.values.all()
df_polars = values.df               # Polars DataFrame
df        = df_polars.to_pandas()   # → Pandas für weitere Verarbeitung
df_temp   = df[df['parameter'].str.contains('temperature_air_mean_2m', ...)]
```

### 3.5 Ergebnis

Nach dem Fix liefert `/climate-trends` korrekte Daten:
```json
{
  "station":          "Würzburg (5705)",
  "reference_period": "1961-1990",
  "reference_mean":   9.1,
  "years":            [1950, 1951, ..., 2024],
  "annual_temp":      [9.47, 9.68, ...],
  "moving_avg_5y":    [9.62, ...],
  "moving_avg_10y":   [null, null, 9.23, ...],
  "deviation":        [0.37, 0.58, ...]
}
```
**75 Datenjahre (1950–2024), Referenzmittel 9.1 °C**

---

## 4. Datenmigration: Open-Meteo → Bright Sky / DWD

### 4.1 Problem mit Open-Meteo

Der bisherige Wetter-Endpoint `GET /weather` rief `api.open-meteo.com` auf. Dieser Dienst ist:
- Extern gehostet (keine Garantie für Verfügbarkeit)
- Nicht offiziell von deutschen Wetterbehörden betrieben
- Während der Session mit **HTTP 502 Bad Gateway** ausgefallen

```bash
# Diagnose:
GET https://api.open-meteo.com/v1/forecast?latitude=49.79&longitude=9.95&...
→ 502 Bad Gateway
```

### 4.2 Auswahl der neuen Datenquelle: Bright Sky

Nach Prüfung mehrerer Alternativen (DWD MOSMIX via wetterdienst, Bright Sky API, wttr.in) fiel die Wahl auf **Bright Sky** (`api.brightsky.dev`):

| Kriterium | Bright Sky |
|---|---|
| **Datengrundlage** | Offizieller DWD (MOSMIX-Prognosen + Beobachtungen) |
| **Hosting** | Deutschland (sehr zuverlässig) |
| **Authentifizierung** | Keine – öffentliche API |
| **Kosten** | Kostenlos |
| **Lizenz** | Open Data (DWD) |
| **Datentiefe** | Temperatur, Niederschlag, Wind, Böen, Luftdruck, Luftfeuchtigkeit, Bewölkung, Sichtweite, Wetter-Icon, Zustand |
| **Konsistenz zum Projekt** | ✅ DWD-Daten – gleiche Quelle wie historische Klimaanalyse |

Der letzte Punkt ist akademisch besonders relevant: **sowohl historische als auch aktuelle Wetterdaten stammen nun aus einer einzigen, offiziellen Quelle (DWD)**.

### 4.3 API-Endpoint-Vergleich

**Open-Meteo (alt):**
```
GET https://api.open-meteo.com/v1/forecast
    ?latitude=49.7913&longitude=9.9534
    &hourly=temperature_2m,precipitation
    &timezone=Europe/Berlin&forecast_days=7

Rückgabe: { hourly: { time: [...], temperature_2m: [...], precipitation: [...] } }
```

**Bright Sky (neu):**
```
GET https://api.brightsky.dev/weather
    ?lat=49.7913&lon=9.9534
    &date=2026-05-26&last_date=2026-06-01
    &tz=Europe/Berlin&units=dwd

Rückgabe: { weather: [ { timestamp, temperature, precipitation, wind_speed,
                          wind_gust_speed, wind_direction, relative_humidity,
                          pressure_msl, cloud_cover, visibility, icon, condition,
                          sunshine, dew_point, ... }, ... ] }
```

### 4.4 Änderungen in `main.py`

```python
from datetime import date, timedelta

@app.get("/weather")
async def get_weather():
    start = date.today().isoformat()
    end   = (date.today() + timedelta(days=6)).isoformat()

    url    = "https://api.brightsky.dev/weather"
    params = {
        "lat":       49.7913,
        "lon":       9.9534,
        "date":      start,
        "last_date": end,
        "tz":        "Europe/Berlin",
        "units":     "dwd",   # SI-Einheiten: °C, km/h, hPa, mm
    }

    resp = requests.get(url, params=params, timeout=12)
    resp.raise_for_status()
    data = resp.json()

    return {
        "location": "Würzburg",
        "source":   "Bright Sky / DWD MOSMIX",
        "weather":  data["weather"],    # Array von stündlichen Objekten
    }
```

### 4.5 Anpassung des Frontends an das neue Datenformat

Das neue Format unterscheidet sich strukturell vom alten:

```javascript
// ALT: parallele Arrays (Open-Meteo)
const temps  = data.weather_data.temperature_2m;  // [18.5, 17.2, ...]
const precips = data.weather_data.precipitation;   // [0, 0, 0.3, ...]
const times  = data.weather_data.time;             // ["2026-05-26T00:00", ...]

// NEU: Array von Objekten (Bright Sky)
const entries = data.weather;
// entries[0] = { timestamp: "2026-05-26T00:00:00+02:00",
//                temperature: 18.6, precipitation: 0,
//                wind_speed: 6.8, relative_humidity: 67,
//                pressure_msl: 1030.3, cloud_cover: 0,
//                icon: "clear-night", condition: "dry", ... }

// Zugriff auf heutige Daten:
const temps  = today.map(e => e.temperature);
const winds  = today.map(e => e.wind_speed);
const hums   = today.map(e => e.relative_humidity);
```

**Gruppierung nach Tagen** (da Bright Sky Timestamps mit Zeitzone zurückgibt):
```javascript
const byDay = {};
entries.forEach(e => {
  const d = new Date(e.timestamp).toLocaleDateString('de-DE');
  if (!byDay[d]) byDay[d] = [];
  byDay[d].push(e);
});
```

### 4.6 Neue Dashboard-Daten durch Bright Sky

Durch den Datenwechsel konnten vier neue Informationsebenen im Dashboard ergänzt werden, die mit Open-Meteo nicht verfügbar waren:

| Neues Datenelement | Bright Sky Feld | Dashboard-Komponente |
|---|---|---|
| Windgeschwindigkeit | `wind_speed` (km/h) | Metrikkarte + 24h-Liniendiagramm |
| Windböen | `wind_gust_speed` (km/h) | Zweite Linie im Wind-Diagramm |
| Windrichtung | `wind_direction` (0–360°) | Metrikkarte (als Himmelsrichtung) |
| Luftdruck | `pressure_msl` (hPa) | Metrikkarte |
| Relative Luftfeuchtigkeit | `relative_humidity` (%) | Metrikkarte + 24h-Liniendiagramm |
| Bewölkungsgrad | `cloud_cover` (%) | Metrikkarte |
| Sichtweite | `visibility` (m) | Metrikkarte (in km) |
| Wetter-Icon | `icon` (String) | SVG-Icons in Forecast-Karten |
| Wetterzustand | `condition` | Textbeschreibung (Hero-Karte) |

---

## 5. Finaler Technischer Stack

### 5.1 Backend (`main.py`)

```
FastAPI + Uvicorn
│
├── GET /weather
│   └── Bright Sky API (api.brightsky.dev)
│       └── Basiert auf: DWD MOSMIX-Prognosen + DWD-Beobachtungen
│
└── GET /climate-trends
    └── analysis.py
        └── wetterdienst 0.121.0
            └── DWD-Beobachtungsstation Würzburg (ID 5705)
                └── Tägliche Klimadaten 1950–heute (Period: historical)
```

### 5.2 Datenanalyse (`analysis.py`)

Verarbeitungsschritte:
1. DWD-Daten abrufen: `parameters=[("daily", "kl")]`, `periods="historical"`
2. Polars DataFrame → Pandas DataFrame konvertieren
3. Filtern auf `temperature_air_mean_2m`
4. Jährliche Durchschnitte berechnen (`groupby('year').mean()`)
5. Gleitende Durchschnitte: 5-Jahres-Fenster, 10-Jahres-Fenster (zentriert)
6. Klimareferenz 1961–1990 berechnen (WMO-Standard)
7. Abweichung vom Referenzwert berechnen
8. Als JSON zurückgeben (NaN → None für JSON-Serialisierbarkeit)

### 5.3 Frontend (`index.html`)

```
Single-Page-App (eine HTML-Datei, alle Styles und Scripts inline)
│
├── Header (sticky)
│   ├── Logo + Ortsname
│   ├── Tab-Navigation (Vorhersage / Klimaanalyse)
│   └── Uhr + API-Status-Indikator + Datenquellen-Badge
│
├── Tab: Vorhersage
│   ├── Hero-Karte (aktuelle Temperatur, Max/Min, Niederschlag)
│   ├── 7-Tage-Forecast-Strip (dynamisch generiert)
│   ├── Temperaturverlauf 24h (ECharts Line)
│   ├── Niederschlag 24h (ECharts Bar)
│   ├── Metrikkarten (Wind, Druck, Feuchtigkeit, Bewölkung)
│   ├── Windverlauf 24h (ECharts Line, 2 Serien)
│   └── Luftfeuchtigkeitsverlauf 24h (ECharts Line)
│
├── Tab: Klimaanalyse
│   ├── Stationsbanner (DWD ID 5705, Referenzmittel, Trend)
│   ├── Jahres-Temperaturen mit Gleitenden Durchschnitten (ECharts Line)
│   └── Warming Stripes – Temperaturabweichung (ECharts Bar + visualMap)
│
└── Footer (Quellenangaben)
```

### 5.4 Datensquellen-Übersicht

| Datentyp | Quelle | Abfrage-Methode | Lizenz |
|---|---|---|---|
| 7-Tage-Vorhersage (stündlich) | DWD MOSMIX via Bright Sky | REST API (HTTP GET) | Open Data |
| Historische Klimadaten 1950–heute | DWD Station 5705 | wetterdienst Python-Library | Open Data |

---

## 6. Dateiübersicht & Änderungen

| Datei | Status | Änderungen |
|---|---|---|
| `index.html` | **Komplett neu** | Vollständig neu erstellt (~900 Zeilen). Ersetzt altes 3-Datei-Layout (`index.html` + `style.css` + `app.js`) |
| `main.py` | **Aktualisiert** | `/weather` Endpoint: Open-Meteo → Bright Sky API. Kommentare und Quellenangaben ergänzt |
| `analysis.py` | **Bugfix** | 3 API-Kompatibilitätsprobleme behoben (siehe Abschnitt 3) |
| `style.css` | **Veraltet** | Wird nicht mehr referenziert, kann gelöscht werden |
| `app.js` | **Veraltet** | Wird nicht mehr referenziert, kann gelöscht werden |
| `find_station.py` | Unverändert | Hilfsskript zur Stationssuche (nutzt veraltete API, nur für Entwicklung) |

---

*Dokumentation erstellt: 26. Mai 2026*
*Projekt: Würzburg Wetter & Klimaanalyse – FWMP Semester 4*

---

## PHASE 4: Interaktiver Tages-Wechsel im Forecast-Strip
*Zeitraum: 3. Juni 2026*

### 1. Problembeschreibung

Im bestehenden Dashboard war der 7-Tage-Forecast-Strip zwar visuell als klickbar gestaltet (CSS `cursor:pointer`, Hover-Effekte), aber ein Klick auf einen der Tage löste **keine Aktion** aus. Hero-Karte, Metrik-Karten und alle Diagramme zeigten immer nur den aktuellen Tag – die anderen sechs Tage waren rein dekorativ und nicht nutzbar.

**Fehlerbild:**
- Tages-Icons klicken → nichts passiert
- Charts und Hero-Karte bleiben statisch auf „heute"
- UX-Versprechen (klickbare Karten) nicht erfüllt

### 2. Technische Ursache

Die Tag-Karten wurden als reines HTML ohne Event-Handler gerendert:
```javascript
// ALT: keine Interaktivität
document.getElementById('forecast-strip').innerHTML = days.map(d => `
  <div class="day${d.today ? ' today' : ''}">
    ...
  </div>`).join('');
```

Zusätzlich wurden alle Wetterdaten nach dem API-Aufruf sofort verarbeitet und lokal in der `loadWeather()`-Funktion gehalten – ohne globale Speicherung. Ein nachträglicher Zugriff auf Daten anderer Tage war architekturell nicht möglich.

### 3. Lösung: Globaler State + `renderDay()` Funktion

#### 3.1 Globaler Wetter-State

Drei neue globale Variablen speichern die geladenen Wetterdaten dauerhaft:

```javascript
let allByDay = {};       // alle Stunden-Einträge, gruppiert nach lokalem Datum
let allDayKeys = [];     // geordnete Datums-Strings (7 Einträge)
let weatherIsDemo = false; // gibt an, ob Demo-Fallback aktiv ist
```

#### 3.2 Refaktorierung von `loadWeather()`

Die Funktion wurde auf ihre Kernaufgaben reduziert:
1. API-Aufruf (oder Demo-Fallback)
2. Gruppierung der Stundendaten nach Datum (`byDay`)
3. **Speicherung in globalen Variablen**
4. Rendering des 7-Tage-Strips (jetzt mit `onclick`)
5. Aufruf von `renderDay(0)` für den aktuellen Tag

```javascript
// NEU: onclick-Handler auf jeder Tageskarte
document.getElementById('forecast-strip').innerHTML = days.map((d, i) => `
  <div class="day${d.today ? ' today' : ''}" onclick="selectDay(${i})">
    ...
  </div>`).join('');

// NEU: nur noch Delegation an renderDay
renderDay(0);
```

#### 3.3 Neue Funktion `renderDay(dayIdx)`

Zentrale Render-Funktion, die den kompletten UI-State für einen beliebigen Tag aktualisiert:

| Bereich | Verhalten bei „heute" | Verhalten bei anderen Tagen |
|---|---|---|
| **Timestamp** | Aktuelle Stunde (`nowH`) | Tagesmitte (`entries.length / 2`) |
| **Wcard-Zeit** | Aktuelle Uhrzeit | „24h Übersicht" |
| **Metriken** | Echtzeit-Werte | Werte zur Tagesmitte |
| **Wind-Mini-Bars** | Aktueller Balken hervorgehoben | Mittags-Balken hervorgehoben |
| **Section-Label** | „Heute — Übersicht" | „Morgen — Übersicht" / „Mo — Übersicht" etc. |
| **Chart-Subtitel** | „24 h · heute" | „24 h · morgen" / „24 h · di. 4.6." etc. |
| **Strip-Highlight** | `.today`-Klasse auf Index 0 | `.today`-Klasse wandert zum geklickten Tag |

```javascript
function renderDay(dayIdx) {
  const dayEntries = allByDay[allDayKeys[dayIdx]];

  // Strip-Highlight wandert zum ausgewählten Tag
  document.querySelectorAll('#forecast-strip .day').forEach((el, i) => {
    el.classList.toggle('today', i === dayIdx);
  });

  // Repräsentativer Zeitpunkt
  const isToday = dayIdx === 0;
  const curIdx = isToday ? Math.min(nowH, dayEntries.length - 1)
                         : Math.floor(dayEntries.length / 2);
  const cur = dayEntries[curIdx];

  // … Update Hero, Metriken, Charts …
}
```

#### 3.4 Neue Funktion `selectDay(idx)`

Schlanker Event-Handler, der lediglich `renderDay` aufruft (Entkoppelung für zukünftige Erweiterungen):

```javascript
function selectDay(idx) {
  renderDay(idx);
}
```

### 4. Änderungen in `index.html`

| Bereich | Änderung |
|---|---|
| **Globale Variablen** | `allByDay`, `allDayKeys`, `weatherIsDemo` hinzugefügt |
| **`loadWeather()`** | Schlanker: speichert Daten global, delegiert Rendering an `renderDay(0)` |
| **Forecast-Strip HTML** | `onclick="selectDay(${i})"` auf jeder Tageskarte |
| **`renderDay(dayIdx)`** | Neue Funktion: vollständiges UI-Update für beliebigen Tag |
| **`selectDay(idx)`** | Neuer Event-Handler für Strip-Klicks |
| **Chart-Sub-Labels** | IDs `chart-temp-sub` und `chart-precip-sub` hinzugefügt (für dynamische Aktualisierung) |

### 5. UX-Verhalten nach dem Fix

- Klick auf einen Tag im Strip → **sofortiges Update** aller sichtbaren Elemente
- Aktiver Tag wird blau hervorgehoben (`.today`-Klasse), vorheriger Highlight verschwindet
- Hero-Karte, Max/Min-Werte, Niederschlag, Windmetriken zeigen Daten des gewählten Tages
- Temperatur-, Niederschlags- und Winddiagramme zeigen den 24h-Verlauf des gewählten Tages
- Chart-Beschriftungen aktualisieren sich: „24 h · heute" → „24 h · morgen" → „24 h · mi. 5.6." etc.
- Bei erneutem Laden der Seite oder Stadtswitch → automatisch wieder „heute" ausgewählt

---

*Zuletzt aktualisiert: 3. Juni 2026*

---

## PHASE 5: Vanilla-Single-File-App & Design Guide v0.2 (9. Juni 2026)

### 1. Ausgangslage

Das bisherige Frontend war ein **kompilierter Figma-Make-Export** (~938 KB minifizierter
React-Bundle, gzip+base64 im `__bundler/manifest`) — **nicht von Hand editierbar**.
Änderungen am Design Guide ließen sich darin nicht nachziehen. Außerdem war das in Phase 2/3
beschriebene FastAPI-Backend nicht zuverlässig erreichbar.

### 2. Entscheidung: Neuaufbau als editierbare Single-File-App

`index.html` wurde **komplett neu** als eine einzige, von Hand wartbare Vanilla-Datei aufgebaut
(Inline-CSS + -JS, nur CDN-Bibliotheken). Sie setzt den **Design Guide v0.2** 1:1 um
(dark, monochrom + Pastell-Wetter-Codierung; Tokens, Icon-System, Tönungsregeln).

| Aspekt | Umsetzung |
|---|---|
| **Stack** | HTML5 + Vanilla-JS + Inline-CSS; ECharts 5.4.3, MapLibre GL 4.7.1 (CDN) |
| **Schriften** | Inter (Interface/Daten), JetBrains Mono (technische Werte) |
| **Datenquelle** | **Open-Meteo direkt, kein Backend, kein API-Key** |
| **Tabs** | Vorhersage · Karte · Klimaanalyse |

### 3. Datenfluss (KEIN Backend)

Alle Daten kommen direkt vom Browser, ohne eigenen Server und ohne Schlüssel:

| Zweck | Endpoint |
|---|---|
| Aktuelles Wetter + 7-Tage + stündlich | `api.open-meteo.com/v1/forecast` |
| Historische Klimadaten (ERA5, ab 1940) | `archive-api.open-meteo.com/v1/archive` |
| Stadtsuche (inkl. Dörfer) | `geocoding-api.open-meteo.com/v1/search` |
| Heatmap-Temperaturen (54 Städte, 1 Call) | `api.open-meteo.com/v1/forecast` (Multi-Location) |
| Karten-Tiles | CARTO Dark Matter (Raster, **key-frei**) |

### 4. Features je Tab

- **Vorhersage:** Hero-Zustandskarte mit Tönung (nie Fläche), 7-Tage-Strip (Wochentage),
  Temperaturverlauf (Punkt markiert „jetzt" konsistent zur Hero-Temperatur), Niederschlag
  (mm = l/m²), Wind-Bars, UV-Bogen, Luftfeuchte/Sicht.
- **Karte:** Umschalter **Temperatur-Heatmap ⇄ Standort**. Die Heatmap holt aktuelle
  Temperaturen für 54 deutsche Städte in *einem* Multi-Location-Aufruf und rendert
  farbcodierte MapLibre-`circle`-Layer (Farbinterpolation = Temperatur-Skala des Guide),
  mit Legende und Hover-Popup. „Standort" zeigt die Detailansicht der gewählten Stadt.
- **Klimaanalyse:** Jahresmittel + 10-Jahres-Trend, Abweichung vs. Referenz 1961–1990,
  Monat×Jahr-Heatmap — alles aus der ERA5-Archive-API.

### 5. Aufgeräumt / Sicherheit

- **Gelöscht** (toter Phase-2/3-Code, von nichts referenziert): `app.js`, `style.css`,
  `climate-fix.js`.
- **Aus Git entfernt:** `wind-global.nc` (1 MB Binärdatei; jetzt via `*.nc` ignoriert).
- **Sicherheit:** der zuvor hartkodierte MapTiler-API-Key wurde entfernt und durch
  key-freie CARTO-Tiles ersetzt.
- Der alte kompilierte Export liegt als `_figma-make-export.index.html.bak` (gitignored).

### 6. Hinweis zum Python-Anteil (`main.py`, `analysis.py`)

Diese Dateien gehören zur akademischen Anforderung („Analyse und Darstellung mit Python")
und bleiben als **eigenständige Analyse-/Backend-Schicht** erhalten. Das aktuelle Frontend
benötigt sie **nicht** (es spricht Open-Meteo direkt an). Wer das Backend nutzen will,
startet es separat (FastAPI/Uvicorn, siehe Phase 2/3 + `render.yaml`).

### 7. Lokal testen

`python -m http.server 4173` im Projektroot (siehe `.claude/launch.json`, Server „static").

---

*Zuletzt aktualisiert: 9. Juni 2026*
