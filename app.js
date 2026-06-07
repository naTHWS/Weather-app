const LAT = 49.7913;
const LON = 9.9534;

const tempChart      = echarts.init(document.getElementById('temp-chart'), 'dark');
const precipChart    = echarts.init(document.getElementById('precip-chart'), 'dark');
const trendChart     = echarts.init(document.getElementById('trend-chart'), 'dark');
const deviationChart = echarts.init(document.getElementById('deviation-chart'), 'dark');

// Design Guide Akzente
const ACCENT_WARM  = '#F7B955';
const ACCENT_COOL  = '#5BC0EB';
const ACCENT_TREND = '#EF6F6C';

const commonOptions = {
    backgroundColor: 'transparent',
    textStyle: { color: '#F5F6F8', fontFamily: 'Inter, Segoe UI, sans-serif' },
    tooltip: { trigger: 'axis' },
    grid: { left: '15%', right: '5%', bottom: '15%', top: '10%' }
};

// Karte
try {
    new maplibregl.Map({
        container: 'map',
        style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        center: [LON, LAT],
        zoom: 13,
        pitch: 50,
        bearing: -10,
        antialias: true
    });
} catch (e) {}

function updateStatus(ok) {
    const dot  = document.getElementById('status-dot');
    const text = document.getElementById('status-text');
    if (!dot || !text) return;
    dot.style.background = ok ? ACCENT_COOL : ACCENT_TREND;
    text.innerText        = ok ? 'Daten geladen' : 'Fehler beim Laden';
}

// 1. Wettervorhersage – Open-Meteo Forecast API (kein Key nötig)
async function updateCurrentWeather() {
    try {
        const url = `https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}`
                  + `&hourly=temperature_2m,precipitation&timezone=Europe%2FBerlin&forecast_days=7`;
        const resp = await fetch(url);
        if (!resp.ok) throw new Error();
        const data = await resp.json();

        updateStatus(true);
        const h      = data.hourly;
        const labels = h.time.slice(0, 48).map(t => {
            const d = new Date(t);
            return d.getHours() === 0
                ? d.toLocaleDateString('de-DE', { weekday: 'short' })
                : d.getHours() + ':00';
        });

        tempChart.setOption({
            ...commonOptions,
            xAxis: { type: 'category', data: labels, axisLabel: { interval: 5 } },
            yAxis: { type: 'value', axisLabel: { formatter: '{value}°' } },
            series: [{ name: 'Temperatur', data: h.temperature_2m.slice(0, 48),
                       type: 'line', smooth: true, color: ACCENT_WARM,
                       areaStyle: { opacity: 0.2 } }]
        });

        precipChart.setOption({
            ...commonOptions,
            xAxis: { type: 'category', data: labels, axisLabel: { interval: 5 } },
            yAxis: { type: 'value', axisLabel: { formatter: '{value}mm' } },
            series: [{ name: 'Niederschlag', data: h.precipitation.slice(0, 48),
                       type: 'bar', color: ACCENT_COOL }]
        });
    } catch {
        updateStatus(false);
    }
}

// 2. Klimatrends – Open-Meteo Historical Archive (ERA5, kein Key nötig)
async function updateClimateTrends() {
    trendChart.showLoading();
    deviationChart.showLoading();
    try {
        const endDate = new Date(Date.now() - 5 * 864e5).toISOString().split('T')[0];
        const url = `https://archive-api.open-meteo.com/v1/archive?latitude=${LAT}&longitude=${LON}`
                  + `&start_date=1940-01-01&end_date=${endDate}&daily=temperature_2m_mean`
                  + `&timezone=Europe%2FBerlin`;
        const resp = await fetch(url);
        if (!resp.ok) throw new Error();
        const data = await resp.json();

        const times = data.daily.time;
        const temps = data.daily.temperature_2m_mean;

        const byYear = {};
        times.forEach((t, i) => {
            if (temps[i] === null) return;
            const yr = parseInt(t.slice(0, 4));
            (byYear[yr] = byYear[yr] || []).push(temps[i]);
        });

        const currentYear = new Date().getFullYear();
        const years = [], annualTemp = [];
        Object.keys(byYear).sort().forEach(y => {
            const yr = parseInt(y), vals = byYear[y];
            if (yr < currentYear  && vals.length < 30)  return;
            if (yr === currentYear && vals.length < 270) return;
            years.push(yr);
            annualTemp.push(+(vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2));
        });

        const refVals = years.flatMap((y, i) => y >= 1961 && y <= 1990 ? [annualTemp[i]] : []);
        const refMean = refVals.reduce((a, b) => a + b, 0) / refVals.length;

        const movingAvg10y = annualTemp.map((_, i) => {
            const s = Math.max(0, i - 4), e = Math.min(annualTemp.length - 1, i + 5);
            const w = annualTemp.slice(s, e + 1);
            return +(w.reduce((a, b) => a + b, 0) / w.length).toFixed(2);
        });

        const deviation = annualTemp.map(t => +((t - refMean).toFixed(2)));

        trendChart.setOption({
            ...commonOptions,
            legend: { data: ['Jahresmittel', '10J Trend'], textStyle: { color: '#F5F6F8' }, bottom: 0 },
            xAxis: { type: 'category', data: years, axisLabel: { interval: 9 } },
            yAxis: { type: 'value', min: 'dataMin', axisLabel: { formatter: '{value}°' } },
            series: [
                { name: 'Jahresmittel', data: annualTemp, type: 'line',
                  symbol: 'none', color: 'rgba(255,255,255,0.3)' },
                { name: '10J Trend', data: movingAvg10y, type: 'line',
                  smooth: true, color: ACCENT_TREND, lineStyle: { width: 3 } }
            ]
        });

        deviationChart.setOption({
            ...commonOptions,
            xAxis: { type: 'category', data: years, axisLabel: { interval: 9 } },
            yAxis: { type: 'value', axisLabel: { formatter: '{value}°' } },
            visualMap: {
                show: false, min: -2, max: 2,
                inRange: { color: ['#313695','#4575b4','#abd9e9','#fee090','#f46d43','#a50026'] }
            },
            series: [{ name: 'Abweichung', data: deviation, type: 'bar', barWidth: '90%' }]
        });

    } catch {
        trendChart.hideLoading();
        deviationChart.hideLoading();
    }
}

updateCurrentWeather();
updateClimateTrends();

window.addEventListener('resize', () => {
    tempChart.resize();
    precipChart.resize();
    trendChart.resize();
    deviationChart.resize();
});
