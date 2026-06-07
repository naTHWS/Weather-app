// --- KONFIGURATION ---
const API_BASE_URL = 'https://wetter-api.onrender.com'; // Render-URL – ggf. anpassen

// --- INITIALISIERUNG DER CHARTS ---
const tempChart = echarts.init(document.getElementById('temp-chart'), 'dark');
const precipChart = echarts.init(document.getElementById('precip-chart'), 'dark');
const trendChart = echarts.init(document.getElementById('trend-chart'), 'dark');
const deviationChart = echarts.init(document.getElementById('deviation-chart'), 'dark');

const commonOptions = {
    backgroundColor: 'transparent',
    textStyle: { color: '#fff', fontFamily: 'Segoe UI' },
    tooltip: { trigger: 'axis' },
    grid: { left: '15%', right: '5%', bottom: '15%', top: '10%' }
};

// --- MAPLIBRE SETUP ---
let map;
try {
    map = new maplibregl.Map({
        container: 'map',
        style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        center: [9.9534, 49.7913],
        zoom: 13,
        pitch: 50,
        bearing: -10,
        antialias: true
    });
} catch (e) {
    console.error('MapLibre Fehler:', e);
}

// --- STATUS UPDATE ---
function updateStatus(connected) {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');
    if (dot && text) {
        dot.style.background = connected ? '#4ECDC4' : '#FF6B6B';
        text.innerText = connected ? 'API Online' : 'API Offline';
    }
}

// --- DATEN-FUNKTIONEN ---

// 1. Aktuelle Wettervorhersage (Open-Meteo via API)
async function updateCurrentWeather() {
    try {
        const response = await fetch(`${API_BASE_URL}/weather`);
        if (!response.ok) throw new Error('API unreachable');
        const data = await response.json();
        
        updateStatus(true);
        const weather = data.weather_data;
        const labels = weather.time.slice(0, 24).map(t => new Date(t).getHours() + ':00');
        const temps = weather.temperature_2m.slice(0, 24);
        const precip = weather.precipitation.slice(0, 24);

        tempChart.setOption({
            ...commonOptions,
            xAxis: { type: 'category', data: labels },
            yAxis: { type: 'value', axisLabel: { formatter: '{value}°' } },
            series: [{ name: 'Temperatur', data: temps, type: 'line', smooth: true, color: '#FF6B6B', areaStyle: { opacity: 0.2 } }]
        });

        precipChart.setOption({
            ...commonOptions,
            xAxis: { type: 'category', data: labels },
            yAxis: { type: 'value', axisLabel: { formatter: '{value}mm' } },
            series: [{ name: 'Niederschlag', data: precip, type: 'bar', color: '#4ECDC4' }]
        });
    } catch (error) {
        console.error('Fehler beim Laden des aktuellen Wetters:', error);
        updateStatus(false);
    }
}

// 2. Historische Klimatrends (DWD via API)
async function updateClimateTrends() {
    trendChart.showLoading();
    deviationChart.showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/climate-trends`);
        if (!response.ok) throw new Error('Climate API unreachable');
        const data = await response.json();

        if (!data.years || data.years.length === 0) {
            return;
        }
        trendChart.setOption({
            ...commonOptions,
            legend: { data: ['Jahresmittel', '10J Trend'], textStyle: { color: '#fff' }, bottom: 0 },
            xAxis: { type: 'category', data: data.years },
            yAxis: { type: 'value', min: 'dataMin', axisLabel: { formatter: '{value}°' } },
            series: [
                { name: 'Jahresmittel', data: data.annual_temp, type: 'line', symbol: 'none', color: 'rgba(255,255,255,0.3)' },
                { name: '10J Trend', data: data.moving_avg_10y, type: 'line', smooth: true, color: '#FF6B6B', lineStyle: { width: 3 } }
            ]
        });

        // Abweichungs-Chart (Warming Stripes Style)
        deviationChart.setOption({
            ...commonOptions,
            xAxis: { type: 'category', data: data.years },
            yAxis: { type: 'value', axisLabel: { formatter: '{value}°' } },
            visualMap: {
                show: false,
                min: -2,
                max: 2,
                inRange: { color: ['#313695', '#4575b4', '#abd9e9', '#fee090', '#f46d43', '#a50026'] }
            },
            series: [{
                name: 'Abweichung',
                data: data.deviation,
                type: 'bar',
                barWidth: '90%'
            }]
        });

    } catch (error) {
        console.error('Fehler beim Laden der Klimatrends:', error);
        trendChart.hideLoading();
        deviationChart.hideLoading();
    }
}

// Start
updateCurrentWeather();
updateClimateTrends();

window.addEventListener('resize', () => {
    tempChart.resize();
    precipChart.resize();
    trendChart.resize();
    deviationChart.resize();
});
