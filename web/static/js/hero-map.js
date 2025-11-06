// === Terrascan HERO MAP FUNCTIONALITY ===

// Global variables for hero map
let heroMap;
let heroFireLayer, heroAirLayer, heroOceanLayer;
let heroFireData = [], heroAirData = [], heroOceanData = [];

// Initialize hero map when page loads
document.addEventListener('DOMContentLoaded', function () {
    initHeroMap();
});

// Initialize hero map
function initHeroMap() {
    // Create hero map centered on world view
    heroMap = L.map('hero-map', {
        center: [20, 0],
        zoom: 2,
        zoomControl: true,
        attributionControl: false,
        scrollWheelZoom: true,
        doubleClickZoom: true,
        dragging: true
    });

    // Position zoom control
    heroMap.zoomControl.setPosition('topright');

    // Default tile layer (OpenStreetMap)
    const heroOsmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(heroMap);

    // Initialize data layers
    heroFireLayer = L.layerGroup().addTo(heroMap);
    heroAirLayer = L.layerGroup().addTo(heroMap);
    heroOceanLayer = L.layerGroup().addTo(heroMap);

    // Load initial data
    loadHeroEnvironmentalData();

    // Set up layer toggles
    setupHeroLayerToggles();
}

// Setup hero map layer toggle controls
function setupHeroLayerToggles() {
    document.getElementById('hero-fire-layer').addEventListener('change', function () {
        if (this.checked) {
            heroMap.addLayer(heroFireLayer);
        } else {
            heroMap.removeLayer(heroFireLayer);
        }
    });

    document.getElementById('hero-air-layer').addEventListener('change', function () {
        if (this.checked) {
            heroMap.addLayer(heroAirLayer);
        } else {
            heroMap.removeLayer(heroAirLayer);
        }
    });

    document.getElementById('hero-ocean-layer').addEventListener('change', function () {
        if (this.checked) {
            heroMap.addLayer(heroOceanLayer);
        } else {
            heroMap.removeLayer(heroOceanLayer);
        }
    });
}

// Load environmental data for hero map
async function loadHeroEnvironmentalData() {
    try {
        const response = await fetch('/api/map-data');
        const data = await response.json();

        if (data.success) {
            heroFireData = data.fires || [];
            heroAirData = data.air_quality || [];
            heroOceanData = data.ocean || [];

            updateHeroFireLayer();
            updateHeroAirLayer();
            updateHeroOceanLayer();
        }
    } catch (error) {
        console.error('Error loading hero map environmental data:', error);
    }
}

// Update hero fire layer with markers
function updateHeroFireLayer() {
    heroFireLayer.clearLayers();

    // Show fewer fires for hero map (top 50 by brightness)
    const topFires = heroFireData
        .sort((a, b) => b.brightness - a.brightness)
        .slice(0, 50);

    topFires.forEach(fire => {
        const color = getHeroFireColor(fire.brightness);
        const radius = Math.max(4, Math.min(12, fire.brightness / 60));

        const marker = L.circleMarker([fire.latitude, fire.longitude], {
            color: color,
            fillColor: color,
            fillOpacity: 0.7,
            radius: radius,
            weight: 1
        });

        marker.bindPopup(`
            <strong>🔥 Active Fire</strong><br>
            <strong>Brightness:</strong> ${fire.brightness}K<br>
            <strong>Confidence:</strong> ${fire.confidence}%<br>
            <strong>Detected:</strong> ${fire.acq_date}<br>
            <small><em>Source: NASA FIRMS</em></small>
        `);

        heroFireLayer.addLayer(marker);
    });
}

// Update hero air quality layer with markers
function updateHeroAirLayer() {
    heroAirLayer.clearLayers();

    // Show top 50 air quality stations
    const topStations = heroAirData
        .sort((a, b) => b.value - a.value)
        .slice(0, 50);

    topStations.forEach(station => {
        const color = getHeroAirQualityColor(station.value);
        const radius = Math.max(6, Math.min(18, station.value / 3));

        const marker = L.circleMarker([station.latitude, station.longitude], {
            color: color,
            fillColor: color,
            fillOpacity: 0.6,
            radius: radius,
            weight: 2
        });

        marker.bindPopup(`
            <strong>🌬️ Air Quality</strong><br>
            <strong>Location:</strong> ${station.location}<br>
            <strong>PM2.5:</strong> ${station.value} μg/m³<br>
            <strong>Status:</strong> ${getHeroAirQualityStatus(station.value)}<br>
            <small><em>Source: OpenAQ</em></small>
        `);

        heroAirLayer.addLayer(marker);
    });
}

// Update hero ocean layer with markers
function updateHeroOceanLayer() {
    heroOceanLayer.clearLayers();

    heroOceanData.forEach(station => {
        const color = getHeroOceanColor(station.temperature);

        const marker = L.circleMarker([station.latitude, station.longitude], {
            color: color,
            fillColor: color,
            fillOpacity: 0.8,
            radius: 10,
            weight: 2
        });

        marker.bindPopup(`
            <strong>🌊 Ocean Station</strong><br>
            <strong>Location:</strong> ${station.name}<br>
            <strong>Temperature:</strong> ${station.temperature}°C<br>
            <strong>Water Level:</strong> ${station.water_level}m<br>
            <small><em>Source: NOAA</em></small>
        `);

        heroOceanLayer.addLayer(marker);
    });
}

// Color functions for hero map (simplified)
function getHeroFireColor(brightness) {
    if (brightness > 400) return '#ff2222';
    if (brightness > 350) return '#ff4444';
    if (brightness > 300) return '#ff6666';
    return '#ff8888';
}

function getHeroAirQualityColor(pm25) {
    if (pm25 > 55) return '#8B0000';  // Dangerous
    if (pm25 > 35) return '#FF4500';  // Unhealthy
    if (pm25 > 25) return '#FFA500';  // Unhealthy for Sensitive
    if (pm25 > 12) return '#FFFF00';  // Moderate
    return '#00FF00';  // Good
}

function getHeroAirQualityStatus(pm25) {
    if (pm25 > 55) return '🚨 Dangerous';
    if (pm25 > 35) return '🔴 Unhealthy';
    if (pm25 > 25) return '🟠 Unhealthy for Sensitive';
    if (pm25 > 12) return '🟡 Moderate';
    return '🟢 Good';
}

function getHeroOceanColor(temp) {
    if (temp > 28) return '#FF6B35';  // Very warm
    if (temp > 25) return '#F7931E';  // Warm
    if (temp > 20) return '#00BFFF';  // Normal
    if (temp > 15) return '#0080FF';  // Cool
    return '#0040FF';  // Cold
}

// Refresh hero map data
async function refreshHeroMap() {
    const icon = document.getElementById('hero-refresh-icon');
    if (icon) {
        icon.classList.add('fa-spin');
    }

    try {
        await loadHeroEnvironmentalData();
    } catch (error) {
        console.error('Hero map refresh error:', error);
    } finally {
        if (icon) {
            setTimeout(() => {
                icon.classList.remove('fa-spin');
            }, 1000);
        }
    }
}

// Auto-refresh hero map every 15 minutes
setInterval(() => {
    refreshHeroMap();
}, 15 * 60 * 1000); 
