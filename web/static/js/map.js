// === TERRASCAN MAP FUNCTIONALITY ===

// Global variables
let map;
let fireLayer, airLayer, oceanLayer;
let fireData = [], airData = [], oceanData = [];
let osmLayer, satelliteLayer;

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', function () {
    initMap();
    updateTime();
    setInterval(updateTime, 1000);
    setInterval(refreshMapData, 15 * 60 * 1000); // Auto-refresh every 15 minutes
});

// Initialize map
function initMap() {
    // Create map centered on world view
    map = L.map('map', {
        center: [20, 0],
        zoom: 2,
        zoomControl: false,
        attributionControl: false
    });

    // Add zoom control to top right
    L.control.zoom({
        position: 'topright'
    }).addTo(map);

    // Default tile layer (OpenStreetMap)
    osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Satellite layer (Esri World Imagery)
    satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: '© Esri, Maxar, Earthstar Geographics'
    });

    // Initialize data layers
    fireLayer = L.layerGroup().addTo(map);
    airLayer = L.layerGroup().addTo(map);
    oceanLayer = L.layerGroup().addTo(map);

    // Load initial data
    loadEnvironmentalData();

    // Set up layer toggles
    setupLayerToggles();

    // Set up satellite view toggle
    document.getElementById('satellite-view').addEventListener('change', function () {
        if (this.checked) {
            map.removeLayer(osmLayer);
            map.addLayer(satelliteLayer);
        } else {
            map.removeLayer(satelliteLayer);
            map.addLayer(osmLayer);
        }
    });
}

// Setup layer toggle controls
function setupLayerToggles() {
    document.getElementById('fire-layer').addEventListener('change', function () {
        if (this.checked) {
            map.addLayer(fireLayer);
            document.getElementById('fire-legend').style.display = 'block';
        } else {
            map.removeLayer(fireLayer);
            document.getElementById('fire-legend').style.display = 'none';
        }
    });

    document.getElementById('air-layer').addEventListener('change', function () {
        if (this.checked) {
            map.addLayer(airLayer);
            document.getElementById('air-legend').style.display = 'block';
        } else {
            map.removeLayer(airLayer);
            document.getElementById('air-legend').style.display = 'none';
        }
    });

    document.getElementById('ocean-layer').addEventListener('change', function () {
        if (this.checked) {
            map.addLayer(oceanLayer);
            document.getElementById('ocean-legend').style.display = 'block';
        } else {
            map.removeLayer(oceanLayer);
            document.getElementById('ocean-legend').style.display = 'none';
        }
    });
}

// Load environmental data from API
async function loadEnvironmentalData() {
    try {
        const response = await fetch('/api/map-data');
        const data = await response.json();

        if (data.success) {
            fireData = data.fires || [];
            airData = data.air_quality || [];
            oceanData = data.ocean || [];

            updateFireLayer();
            updateAirLayer();
            updateOceanLayer();
        }
    } catch (error) {
        console.error('Error loading environmental data:', error);
    }
}

// Update fire layer with markers
function updateFireLayer() {
    fireLayer.clearLayers();

    fireData.forEach(fire => {
        const color = getFireColor(fire.brightness);
        const radius = Math.max(5, Math.min(20, fire.brightness / 50));

        const marker = L.circleMarker([fire.latitude, fire.longitude], {
            color: color,
            fillColor: color,
            fillOpacity: 0.7,
            radius: radius,
            weight: 1
        });

        marker.bindPopup(`
            <strong>🔥 Active Fire</strong><br>
            <strong>Location:</strong> ${fire.latitude.toFixed(3)}, ${fire.longitude.toFixed(3)}<br>
            <strong>Brightness:</strong> ${fire.brightness}K<br>
            <strong>Confidence:</strong> ${fire.confidence}%<br>
            <strong>Detected:</strong> ${fire.acq_date}<br>
            <em>Source: NASA FIRMS</em>
        `);

        marker.on('click', function () {
            showInfoPopup('🔥 Fire Alert', `
                <strong>Brightness:</strong> ${fire.brightness}K<br>
                <strong>Confidence:</strong> ${fire.confidence}%<br>
                <strong>Location:</strong> ${fire.latitude.toFixed(3)}, ${fire.longitude.toFixed(3)}<br>
                <strong>Detected:</strong> ${fire.acq_date}
            `);
        });

        fireLayer.addLayer(marker);
    });
}

// Update air quality layer with markers
function updateAirLayer() {
    airLayer.clearLayers();

    airData.forEach(station => {
        const color = getAirQualityColor(station.value);
        const radius = Math.max(8, Math.min(25, station.value / 2));

        const marker = L.circleMarker([station.latitude, station.longitude], {
            color: color,
            fillColor: color,
            fillOpacity: 0.6,
            radius: radius,
            weight: 2
        });

        marker.bindPopup(`
            <strong>🌬️ Air Quality Station</strong><br>
            <strong>Location:</strong> ${station.location}<br>
            <strong>PM2.5:</strong> ${station.value} μg/m³<br>
            <strong>Status:</strong> ${getAirQualityStatus(station.value)}
            <strong>Updated:</strong> ${station.last_updated}<br>
            <em>Source: OpenAQ</em>
        `);

        marker.on('click', function () {
            showInfoPopup('🌬️ Air Quality', `
                <strong>Location:</strong> ${station.location}<br>
                <strong>PM2.5:</strong> ${station.value} μg/m³<br>
                <strong>Status:</strong> ${getAirQualityStatus(station.value)}
                <strong>Updated:</strong> ${station.last_updated}
            `);
        });

        airLayer.addLayer(marker);
    });
}

// Update ocean layer with markers
function updateOceanLayer() {
    oceanLayer.clearLayers();

    oceanData.forEach(station => {
        const color = getOceanColor(station.temperature);

        const marker = L.circleMarker([station.latitude, station.longitude], {
            color: color,
            fillColor: color,
            fillOpacity: 0.8,
            radius: 12,
            weight: 2
        });

        marker.bindPopup(`
            <strong>🌊 Ocean Monitoring Station</strong><br>
            <strong>Location:</strong> ${station.name}<br>
            <strong>Temperature:</strong> ${station.temperature}°C<br>
            <strong>Water Level:</strong> ${station.water_level}m<br>
            <strong>Updated:</strong> ${station.last_updated}<br>
            <em>Source: NOAA</em>
        `);

        marker.on('click', function () {
            showInfoPopup('🌊 Ocean Station', `
                <strong>Location:</strong> ${station.name}<br>
                <strong>Temperature:</strong> ${station.temperature}°C<br>
                <strong>Water Level:</strong> ${station.water_level}m<br>
                <strong>Updated:</strong> ${station.last_updated}
            `);
        });

        oceanLayer.addLayer(marker);
    });
}

// Color functions for different data types
function getFireColor(brightness) {
    if (brightness > 400) return '#ff2222';
    if (brightness > 350) return '#ff4444';
    if (brightness > 300) return '#ff6666';
    return '#ff8888';
}

function getAirQualityColor(pm25) {
    if (pm25 > 55) return '#8B0000';  // Dangerous
    if (pm25 > 35) return '#FF4500';  // Unhealthy
    if (pm25 > 25) return '#FFA500';  // Unhealthy for Sensitive
    if (pm25 > 12) return '#FFFF00';  // Moderate
    return '#00FF00';  // Good
}

function getAirQualityStatus(pm25) {
    if (pm25 > 55) return '🚨 Dangerous';
    if (pm25 > 35) return '🔴 Unhealthy';
    if (pm25 > 25) return '🟠 Unhealthy for Sensitive';
    if (pm25 > 12) return '🟡 Moderate';
    return '🟢 Good';
}

function getOceanColor(temp) {
    if (temp > 28) return '#FF6B35';  // Very warm
    if (temp > 25) return '#F7931E';  // Warm
    if (temp > 20) return '#00BFFF';  // Normal
    if (temp > 15) return '#0080FF';  // Cool
    return '#0040FF';  // Cold
}

// Show info popup with details
function showInfoPopup(title, content) {
    document.getElementById('popup-title').innerHTML = title;
    document.getElementById('popup-content').innerHTML = content;
    document.getElementById('info-popup').style.display = 'block';
}

// Close info popup
function closeInfoPopup() {
    document.getElementById('info-popup').style.display = 'none';
}

// Refresh map data
async function refreshMapData() {
    const icon = document.getElementById('refresh-icon');
    icon.classList.add('fa-spin');

    try {
        await loadEnvironmentalData();

        // Also refresh health score
        const response = await fetch('/api/refresh');
        const result = await response.json();

        if (result.success) {
            // Update health score widget
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
    } catch (error) {
        console.error('Refresh error:', error);
    } finally {
        setTimeout(() => {
            icon.classList.remove('fa-spin');
        }, 2000);
    }
}

// Update current time display
function updateTime() {
    const now = new Date();
    const timeString = now.toISOString().replace('T', ' ').substr(0, 19) + ' UTC';

    // Update navbar time
    const navTimeElement = document.getElementById('current-time');
    if (navTimeElement) {
        navTimeElement.textContent = timeString;
    }

    // Update map widget time
    const mapTimeElement = document.getElementById('map-current-time');
    if (mapTimeElement) {
        mapTimeElement.textContent = timeString;
    }
} 
