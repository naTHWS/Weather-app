import requests
import pandas as pd
import numpy as np
import datetime


def get_historical_trends(lat: float = 49.7913, lon: float = 9.9534):
    """
    Historische Klimaanalyse via Open-Meteo Historical Archive API.

    Datenquelle: ERA5 Reanalyse (Copernicus Climate Change Service /
    ECMWF), bereitgestellt kostenlos über Open-Meteo.
    Kein API-Key erforderlich.

    Vorteile gegenüber wetterdienst/DWD:
    - Globale Abdeckung (kein Stationsauswahlproblem)
    - Daten von 1940 bis ~5 Tage vor heute
    - Schnelle REST-API, keine externe Bibliothek nötig
    - Konsistente Datenqualität (ERA5 ist der Industriestandard
      für Klimareanalysen)
    """
    today      = datetime.date.today()
    start_date = "1940-01-01"
    # Open-Meteo hat typisch 5 Tage Verzögerung
    end_date   = (today - datetime.timedelta(days=5)).isoformat()

    url    = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude":   lat,
        "longitude":  lon,
        "start_date": start_date,
        "end_date":   end_date,
        "daily":      "temperature_2m_mean",
        "timezone":   "Europe/Berlin",
    }

    print(f"Rufe ERA5/Open-Meteo-Daten für {lat:.4f}, {lon:.4f} ab …")
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    daily = data.get("daily", {})
    times = daily.get("time", [])
    temps = daily.get("temperature_2m_mean", [])

    if not times:
        print("WARNUNG: Keine ERA5-Daten empfangen.")
        return {}

    # ── Tagesdaten → Pandas ──────────────────────────────────────────────
    df = pd.DataFrame({"date": pd.to_datetime(times), "temp": temps})
    df = df.dropna(subset=["temp"])
    df["year"]  = df["date"].dt.year
    df["month"] = df["date"].dt.month

    # ── Jährliche Mitteltemperaturen ─────────────────────────────────────
    agg = (
        df.groupby("year")["temp"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "temp", "count": "n_days"})
    )

    # Abgeschlossene Jahre nur bei nahezu vollständiger Abdeckung (>= 330 Tage),
    # laufendes Jahr ab >= 270 Tagen — identisch zum Filter im Dashboard.
    current_year = today.year
    annual_df = agg[
        ((agg["year"] < current_year) & (agg["n_days"] >= 330)) |
        ((agg["year"] == current_year) & (agg["n_days"] >= 270))
    ].copy()

    if annual_df.empty:
        print("WARNUNG: Keine verwertbaren Jahresdaten.")
        return {}

    # ── Gleitende Durchschnitte ──────────────────────────────────────────
    annual_df["moving_avg_5y"]  = annual_df["temp"].rolling(window=5,  center=True).mean()
    annual_df["moving_avg_10y"] = annual_df["temp"].rolling(window=10, center=True).mean()

    # ── WMO-Referenzperiode 1961–1990 ────────────────────────────────────
    ref_period = annual_df[
        (annual_df["year"] >= 1961) & (annual_df["year"] <= 1990)
    ]
    ref_mean = (
        ref_period["temp"].mean()
        if not ref_period.empty
        else annual_df["temp"].mean()
    )
    annual_df["deviation"] = annual_df["temp"] - ref_mean

    result_df  = annual_df.replace({np.nan: None})
    first_year = int(result_df["year"].iloc[0])
    last_year  = int(result_df["year"].iloc[-1])
    is_partial = (last_year == current_year)

    # ── Monatliche Mittelwerte für Heatmap ───────────────────────────────
    valid_years = set(result_df["year"].tolist())
    monthly_agg = (
        df[df["year"].isin(valid_years)]
        .groupby(["year", "month"])["temp"]
        .mean()
        .reset_index()
    )
    # Format: [[year, month(1-12), temp_gerundet], …]  — chronologisch sortiert
    monthly_data = sorted(
        [
            [int(r.year), int(r.month), round(float(r.temp), 1)]
            for _, r in monthly_agg.iterrows()
        ],
        key=lambda x: (x[0], x[1])
    )

    elevation  = data.get("elevation")
    source     = "Open-Meteo / ERA5 (Copernicus)"
    # Lesbarer Name für das Frontend
    station_name = (
        f"ERA5-Gitterpunkt {lat:.2f}°N {abs(lon):.2f}°{'E' if lon>=0 else 'W'}"
    )

    def safe_round(series, decimals=2):
        return [round(x, decimals) if x is not None else None for x in series.tolist()]

    print(f"ERA5-Analyse abgeschlossen: {first_year}–{last_year} ({len(result_df)} Jahre)")

    return {
        "station":          station_name,
        "station_name":     station_name,
        "station_id":       None,           # kein DWD-Station-ID bei ERA5
        "source":           source,
        "elevation":        elevation,
        "reference_period": "1961-1990",
        "reference_mean":   round(float(ref_mean), 2),
        "first_year":       first_year,
        "last_year":        last_year,
        "is_partial_year":  is_partial,
        "years":            result_df["year"].tolist(),
        "annual_temp":      safe_round(result_df["temp"]),
        "moving_avg_5y":    safe_round(result_df["moving_avg_5y"]),
        "moving_avg_10y":   safe_round(result_df["moving_avg_10y"]),
        "deviation":        safe_round(result_df["deviation"]),
        "monthly_data":     monthly_data,
    }


if __name__ == "__main__":
    import json
    result = get_historical_trends()
    print(json.dumps(
        {k: (v[:3] if isinstance(v, list) else v) for k, v in result.items()},
        indent=2, ensure_ascii=False
    ))
