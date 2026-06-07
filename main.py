from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
from datetime import date, timedelta
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from analysis import get_historical_trends

app = FastAPI(title="Wetter API")

# CORS Konfiguration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Würzburg – Standard-Koordinaten
LATITUDE  = 49.7913
LONGITUDE = 9.9534

# Klimadaten-Cache: Schlüssel = gerundete Koordinaten, damit nahe Städte
# denselben Cache-Eintrag nutzen können.
# Cache löschen nach Code-Änderungen: Server neu starten.
climate_cache: Dict[str, Any] = {}

# ── Deutsche Städte für Temperaturkarte ─────────────────────────────────────
MAP_STATIONS: List[Dict] = [
    # Nord
    {"name":"Hamburg",      "lat":53.55,"lon": 9.99},
    {"name":"Kiel",         "lat":54.32,"lon":10.13},
    {"name":"Rostock",      "lat":54.09,"lon":12.14},
    {"name":"Schwerin",     "lat":53.63,"lon":11.41},
    {"name":"Flensburg",    "lat":54.78,"lon": 9.43},
    {"name":"Lübeck",       "lat":53.87,"lon":10.69},
    {"name":"Greifswald",   "lat":54.09,"lon":13.38},
    # Nordost / Brandenburg
    {"name":"Berlin",       "lat":52.52,"lon":13.40},
    {"name":"Potsdam",      "lat":52.39,"lon":13.06},
    {"name":"Frankfurt/O",  "lat":52.34,"lon":14.55},
    {"name":"Cottbus",      "lat":51.76,"lon":14.33},
    # Ost
    {"name":"Leipzig",      "lat":51.34,"lon":12.37},
    {"name":"Dresden",      "lat":51.05,"lon":13.74},
    {"name":"Chemnitz",     "lat":50.83,"lon":12.92},
    {"name":"Erfurt",       "lat":50.98,"lon":11.03},
    {"name":"Magdeburg",    "lat":52.13,"lon":11.63},
    {"name":"Halle",        "lat":51.48,"lon":11.97},
    {"name":"Jena",         "lat":50.93,"lon":11.59},
    # Mitte
    {"name":"Hannover",     "lat":52.37,"lon": 9.73},
    {"name":"Braunschweig", "lat":52.27,"lon":10.52},
    {"name":"Göttingen",    "lat":51.53,"lon": 9.93},
    {"name":"Kassel",       "lat":51.32,"lon": 9.50},
    {"name":"Paderborn",    "lat":51.72,"lon": 8.75},
    # West
    {"name":"Köln",         "lat":50.93,"lon": 6.95},
    {"name":"Düsseldorf",   "lat":51.22,"lon": 6.78},
    {"name":"Essen",        "lat":51.46,"lon": 7.01},
    {"name":"Dortmund",     "lat":51.51,"lon": 7.46},
    {"name":"Münster",      "lat":51.96,"lon": 7.63},
    {"name":"Bielefeld",    "lat":52.02,"lon": 8.53},
    {"name":"Aachen",       "lat":50.78,"lon": 6.08},
    {"name":"Bonn",         "lat":50.73,"lon": 7.10},
    {"name":"Wuppertal",    "lat":51.26,"lon": 7.15},
    {"name":"Osnabrück",    "lat":52.28,"lon": 8.05},
    # Südwest
    {"name":"Frankfurt/M",  "lat":50.11,"lon": 8.68},
    {"name":"Wiesbaden",    "lat":50.08,"lon": 8.24},
    {"name":"Mainz",        "lat":50.00,"lon": 8.27},
    {"name":"Mannheim",     "lat":49.49,"lon": 8.47},
    {"name":"Karlsruhe",    "lat":49.00,"lon": 8.40},
    {"name":"Freiburg",     "lat":47.99,"lon": 7.84},
    {"name":"Stuttgart",    "lat":48.78,"lon": 9.18},
    {"name":"Heidelberg",   "lat":49.40,"lon": 8.69},
    {"name":"Saarbrücken",  "lat":49.23,"lon": 7.00},
    {"name":"Trier",        "lat":49.75,"lon": 6.64},
    # Süd / Bayern
    {"name":"Würzburg",     "lat":49.79,"lon": 9.95},
    {"name":"Nürnberg",     "lat":49.45,"lon":11.08},
    {"name":"Regensburg",   "lat":49.01,"lon":12.10},
    {"name":"Augsburg",     "lat":48.37,"lon":10.89},
    {"name":"München",      "lat":48.14,"lon":11.58},
    {"name":"Ingolstadt",   "lat":48.76,"lon":11.42},
    {"name":"Passau",       "lat":48.57,"lon":13.47},
    {"name":"Bamberg",      "lat":49.90,"lon":10.90},
    {"name":"Bayreuth",     "lat":49.95,"lon":11.58},
    {"name":"Konstanz",     "lat":47.66,"lon": 9.18},
    {"name":"Ulm",          "lat":48.40,"lon": 9.99},
    {"name":"Garmisch",     "lat":47.49,"lon":11.10},
    {"name":"Rosenheim",    "lat":47.86,"lon":12.12},
]

# Karten-Cache: 30 Minuten TTL
map_cache: Dict[str, Any] = {"data": None, "ts": 0.0}


@app.get("/weather")
async def get_weather(
    lat: float = Query(default=LATITUDE, ge=-90.0,  le=90.0),
    lon: float = Query(default=LONGITUDE, ge=-180.0, le=180.0),
) -> Dict[str, Any]:
    """
    Stündliche Wetterdaten für die nächsten 7 Tage.
    Datenquelle: Bright Sky API (https://brightsky.dev)
    Basiert auf offiziellen DWD MOSMIX-Prognosen.
    Kein API-Key erforderlich.

    Parameter:
        lat  – Breitengrad  (Standard: Würzburg)
        lon  – Längengrad   (Standard: Würzburg)
    """
    start = date.today().isoformat()
    end   = (date.today() + timedelta(days=6)).isoformat()

    url    = "https://api.brightsky.dev/weather"
    params = {
        "lat":       lat,
        "lon":       lon,
        "date":      start,
        "last_date": end,
        "tz":        "Europe/Berlin",
        "units":     "dwd",   # SI-Einheiten: °C, km/h, hPa, mm
    }

    try:
        resp = requests.get(url, params=params, timeout=12)
        resp.raise_for_status()
        data = resp.json()

        weather_entries = data.get("weather", [])
        if not weather_entries:
            raise HTTPException(
                status_code=404,
                detail="Keine Wetterdaten von Bright Sky erhalten – "
                       "Standort wird möglicherweise nicht abgedeckt."
            )

        return {
            "coordinates": {"lat": lat, "lon": lon},
            "source":      "Bright Sky / DWD MOSMIX",
            "unit_info": {
                "temperature":        "°C",
                "precipitation":      "mm",
                "wind_speed":         "km/h",
                "wind_gust_speed":    "km/h",
                "pressure_msl":       "hPa",
                "relative_humidity":  "%",
                "visibility":         "m",
                "cloud_cover":        "%",
                "sunshine":           "min",
            },
            "weather": weather_entries,
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Bright Sky / DWD-Dienst nicht erreichbar: {str(e)}"
        )


@app.get("/climate-trends")
async def get_climate_trends(
    lat: float = Query(default=LATITUDE, ge=-90.0,  le=90.0),
    lon: float = Query(default=LONGITUDE, ge=-180.0, le=180.0),
) -> Dict[str, Any]:
    """
    Historische Klimatrends vom DWD (1950–heute).
    Sucht automatisch die nächstgelegene DWD-Station im Umkreis von 150 km.

    Parameter:
        lat  – Breitengrad  (Standard: Würzburg)
        lon  – Längengrad   (Standard: Würzburg)
    """
    # Cache-Schlüssel auf 1 Dezimalstelle runden (~11 km Genauigkeit)
    cache_key = f"{round(lat, 1)}_{round(lon, 1)}"
    if cache_key in climate_cache:
        return climate_cache[cache_key]

    try:
        print(f"Starte DWD-Klimaanalyse für {lat:.4f}, {lon:.4f} …")
        trends = get_historical_trends(lat=lat, lon=lon)
        if not trends:
            raise HTTPException(
                status_code=404,
                detail="Keine DWD-Klimadaten für diesen Standort gefunden."
            )
        climate_cache[cache_key] = trends
        return trends

    except Exception as e:
        import traceback
        print(f"FEHLER in /climate-trends: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Fehler bei der DWD-Analyse: {str(e)}"
        )


@app.get("/map-weather")
async def get_map_weather() -> Dict[str, Any]:
    """
    Aktuelle Temperaturen für ~55 deutsche Städte (Temperaturkarte).
    Datenquelle: Bright Sky current_weather – parallele Abfragen.
    Cache: 30 Minuten TTL.
    """
    if map_cache["data"] and (time.time() - map_cache["ts"]) < 1800:
        return map_cache["data"]

    def fetch_station(s: Dict) -> Dict:
        try:
            r = requests.get(
                "https://api.brightsky.dev/current_weather",
                params={"lat": s["lat"], "lon": s["lon"], "units": "dwd"},
                timeout=8,
            )
            r.raise_for_status()
            w = r.json().get("weather", {})
            return {
                "name":           s["name"],
                "lat":            s["lat"],
                "lon":            s["lon"],
                "temperature":    w.get("temperature"),
                "wind_speed":     w.get("wind_speed"),
                "wind_direction": w.get("wind_direction"),
                "condition":      w.get("condition"),
                "icon":           w.get("icon"),
            }
        except Exception:
            return {"name": s["name"], "lat": s["lat"], "lon": s["lon"],
                    "temperature": None}

    with ThreadPoolExecutor(max_workers=15) as ex:
        results = list(ex.map(fetch_station, MAP_STATIONS))

    valid = [r for r in results if r.get("temperature") is not None]
    result: Dict[str, Any] = {
        "stations":  results,
        "count":     len(valid),
        "timestamp": date.today().isoformat(),
    }
    map_cache["data"] = result
    map_cache["ts"]   = time.time()
    return result


@app.get("/")
async def root():
    return {
        "message": "Wetter API (Bright Sky / DWD)",
        "endpoints": {
            "/weather":        "7-Tage-Vorhersage – ?lat=...&lon=...",
            "/climate-trends": "Historische Klimadaten 1950–heute – ?lat=...&lon=...",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)