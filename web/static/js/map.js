// === Terrascan MAP FUNCTIONALITY ===

/**
 * @typedef {Object} FireData
 * @property {number} lat - Latitude
 * @property {number} lng - Longitude
 * @property {number} brightness - Brightness temperature in Kelvin
 * @property {number} confidence - Detection confidence percentage
 * @property {string} acq_date - Acquisition date
 */

/**
 * @typedef {Object} AirQualityData
 * @property {number} lat - Latitude
 * @property {number} lng - Longitude
 * @property {number} pm25 - PM2.5 concentration in μg/m³
 * @property {string} location - Location name
 */

/**
 * @typedef {Object} OceanData
 * @property {number} latitude - Latitude
 * @property {number} longitude - Longitude
 * @property {number|null} temperature - Water temperature in Celsius
 * @property {number|null} water_level - Water level in meters
 * @property {string} last_updated - Last update timestamp
 * @property {string} name - Station name
 */

// Global variables
let map;
let fireLayer, airLayer, oceanLayer, conflictLayer, biodiversityLayer, auroraLayer;
let fireHeatLayer, auroraHeatLayer;  // Heatmap layers
let airClusterLayer;  // Marker cluster for AQ
/** @type {FireData[]} */
let fireData = [];
/** @type {AirQualityData[]} */
let airData = [];
/** @type {OceanData[]} */
let oceanData = [];
let conflictData = [];
let biodiversityData = [];
let auroraData = { points: [], kp_index: null };
let osmLayer, satelliteLayer;

// Track which visualization mode is active
let useHeatmaps = true;

// Scan threshold - show scan button when zoomed in this much (8 = regional level)
const SCAN_ZOOM_THRESHOLD = 8;

// Viewport loading threshold - only load viewport data when zoomed in this much
const VIEWPORT_LOAD_THRESHOLD = 5;

// Debounce timer for map movement
let mapMoveTimeout = null;

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', function () {
    initMap();
    updateTime();
    setInterval(updateTime, 1000);
    setInterval(refreshMapData, 15 * 60 * 1000); // Auto-refresh every 15 minutes

    // Create toast element for scan notifications
    createScanToast();
});

// Debounce utility for map movement
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize map
function initMap() {
    // Define world bounds to prevent panning outside
    const worldBounds = [
        [-85, -180],  // Southwest corner
        [85, 180]     // Northeast corner
    ];

    // Create map centered on world view (no zoom controls - use scroll/pinch)
    map = L.map('map', {
        center: [20, 0],
        zoom: 2,
        minZoom: 2,
        maxBounds: worldBounds,
        maxBoundsViscosity: 1.0,
        zoomControl: false,
        attributionControl: false
    });

    // Default tile layer (OpenStreetMap)
    osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    });

    // Satellite layer (Esri World Imagery) - DEFAULT VIEW
    satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: '© Esri, Maxar, Earthstar Geographics'
    }).addTo(map);

    // Initialize data layers
    // Fire: heatmap (primary) + regular layer (fallback)
    fireHeatLayer = L.heatLayer([], {
        radius: 25,
        blur: 15,
        maxZoom: 10,
        max: 500,
        gradient: {0.2: '#ffeda0', 0.4: '#feb24c', 0.6: '#fd8d3c', 0.8: '#f03b20', 1: '#bd0026'}
    }).addTo(map);
    fireLayer = L.layerGroup();  // Fallback, not added by default

    // Air Quality: marker cluster colored by average PM2.5
    airClusterLayer = L.markerClusterGroup({
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        iconCreateFunction: function(cluster) {
            const markers = cluster.getAllChildMarkers();
            const count = markers.length;

            // Calculate average PM2.5 from marker options
            let totalPm25 = 0;
            markers.forEach(m => {
                totalPm25 += m.options.pm25 || 0;
            });
            const avgPm25 = totalPm25 / count;

            // Color based on average air quality, not count
            const color = getAirQualityColor(avgPm25);
            const status = getAirQualityClass(avgPm25);

            return L.divIcon({
                html: `<div style="background-color: ${color};"><span>${count}</span></div>`,
                className: 'marker-cluster marker-cluster-aq marker-cluster-' + status,
                iconSize: L.point(40, 40)
            });
        }
    }).addTo(map);
    airLayer = L.layerGroup();  // Fallback

    // Ocean: regular markers (few points)
    oceanLayer = L.layerGroup().addTo(map);

    // Conflicts: regular markers
    conflictLayer = L.layerGroup().addTo(map);

    // Biodiversity: regular markers
    biodiversityLayer = L.layerGroup().addTo(map);

    // Aurora: heatmap with aurora-like colors
    auroraHeatLayer = L.heatLayer([], {
        radius: 30,
        blur: 20,
        maxZoom: 8,
        max: 100,
        gradient: {0.2: '#001a00', 0.4: '#00ff7f', 0.6: '#00ff00', 0.8: '#9400d3', 1: '#ff00ff'}
    }).addTo(map);
    auroraLayer = L.layerGroup();  // Fallback

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

    // Show/hide scan button based on zoom level
    map.on('zoomend', updateScanButtonVisibility);
    updateScanButtonVisibility();

    // Reload data when map moves (debounced) - for viewport-based loading
    const debouncedLoad = debounce(() => {
        if (map.getZoom() >= VIEWPORT_LOAD_THRESHOLD) {
            loadEnvironmentalData();
        }
    }, 500);  // 500ms debounce

    map.on('moveend', debouncedLoad);
}

// Update scan button visibility based on zoom level
function updateScanButtonVisibility() {
    const scanBtn = document.getElementById('scan-btn');
    if (!scanBtn) return;

    const zoom = map.getZoom();
    if (zoom >= SCAN_ZOOM_THRESHOLD) {
        scanBtn.style.display = 'flex';
    } else {
        scanBtn.style.display = 'none';
    }
}

// Create toast notification element
function createScanToast() {
    const toast = document.createElement('div');
    toast.id = 'scan-toast';
    toast.className = 'scan-toast';
    document.body.appendChild(toast);
}

// Show toast notification
function showScanToast(message, duration = 3000) {
    const toast = document.getElementById('scan-toast');
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

// Scan current map area for air quality stations
async function scanCurrentArea() {
    const scanBtn = document.getElementById('scan-btn');
    const scanIcon = document.getElementById('scan-icon');
    const scanLabel = scanBtn.querySelector('.scan-label');

    // Get current map bounds
    const bounds = map.getBounds();
    const bbox = {
        south: bounds.getSouth(),
        west: bounds.getWest(),
        north: bounds.getNorth(),
        east: bounds.getEast()
    };

    // Show scanning state
    scanBtn.classList.add('scanning');
    scanIcon.classList.add('fa-spin');
    scanLabel.textContent = 'Scanning...';

    try {
        const response = await fetch('/api/scan-area', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ bbox })
        });

        const result = await response.json();

        if (result.success) {
            const stationCount = result.stations?.length || 0;
            const newRecords = result.records_stored || 0;

            if (newRecords > 0) {
                showScanToast(`📍 Loaded ${newRecords} air quality stations`);

                // Add new stations to the cluster layer
                result.stations.forEach(station => {
                    if (!station.lat || !station.lng) return;

                    const color = getAirQualityColor(station.pm25);
                    const marker = L.circleMarker([station.lat, station.lng], {
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.8,
                        radius: 6,
                        weight: 1,
                        pm25: station.pm25  // Store for cluster averaging
                    });

                    marker.bindPopup(`
                        <strong>🌬️ ${station.location || 'Air Quality'}</strong><br>
                        <strong>PM2.5:</strong> ${station.pm25} μg/m³<br>
                        <strong>Status:</strong> ${getAirQualityStatus(station.pm25)}<br>
                        <em>📍 Scanned just now</em>
                    `);

                    airClusterLayer.addLayer(marker);
                });

                // Also add to airData for consistency
                airData = [...airData, ...result.stations];
            } else {
                showScanToast('No new stations found in this area');
            }
        } else {
            showScanToast(`⚠️ ${result.error || 'Scan failed'}`);
        }
    } catch (error) {
        console.error('Scan error:', error);
        showScanToast('⚠️ Scan failed - check connection');
    } finally {
        // Reset button state
        scanBtn.classList.remove('scanning');
        scanIcon.classList.remove('fa-spin');
        scanLabel.textContent = 'Scan Area';
    }
}

// Setup layer toggle controls
function setupLayerToggles() {
    document.getElementById('fire-layer').addEventListener('change', function () {
        if (this.checked) {
            map.addLayer(fireHeatLayer);
        } else {
            map.removeLayer(fireHeatLayer);
        }
    });

    document.getElementById('air-layer').addEventListener('change', function () {
        if (this.checked) {
            map.addLayer(airClusterLayer);
        } else {
            map.removeLayer(airClusterLayer);
        }
    });

    document.getElementById('ocean-layer').addEventListener('change', function () {
        if (this.checked) {
            map.addLayer(oceanLayer);
        } else {
            map.removeLayer(oceanLayer);
        }
    });

    document.getElementById('conflict-layer').addEventListener('change', function () {
        if (this.checked) {
            map.addLayer(conflictLayer);
        } else {
            map.removeLayer(conflictLayer);
        }
    });

    document.getElementById('biodiversity-layer').addEventListener('change', function () {
        if (this.checked) {
            map.addLayer(biodiversityLayer);
        } else {
            map.removeLayer(biodiversityLayer);
        }
    });

    document.getElementById('aurora-layer').addEventListener('change', function () {
        if (this.checked) {
            map.addLayer(auroraHeatLayer);
        } else {
            map.removeLayer(auroraHeatLayer);
        }
    });
}

/**
 * Get current map viewport as bbox string
 * @returns {string} bbox in format "south,west,north,east"
 */
function getViewportBbox() {
    if (!map) return '';
    const bounds = map.getBounds();
    return `${bounds.getSouth()},${bounds.getWest()},${bounds.getNorth()},${bounds.getEast()}`;
}

/**
 * Load environmental data from API
 * Uses viewport-based loading when zoomed in for better local coverage
 * @returns {Promise<void>}
 */
async function loadEnvironmentalData() {
    try {
        // Build URL with optional bbox for viewport-based loading
        let url = '/api/map-data';
        if (map && map.getZoom() >= VIEWPORT_LOAD_THRESHOLD) {
            const bbox = getViewportBbox();
            url += `?bbox=${encodeURIComponent(bbox)}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            // Validate and sanitize data
            fireData = validateFireData(data.fires || []);
            airData = validateAirData(data.air_quality || []);
            oceanData = validateOceanData(data.ocean || []);
            conflictData = data.conflicts || [];
            biodiversityData = data.biodiversity || [];
            auroraData = data.aurora || { points: [], kp_index: null };

            updateFireLayer();
            updateAirLayer();
            updateOceanLayer();
            updateConflictLayer();
            updateBiodiversityLayer();
            updateAuroraLayer();
        }
    } catch (error) {
        console.error('Error loading environmental data:', error);
    }
}

/**
 * Validate and sanitize fire data
 * @param {any[]} fires - Raw fire data from API
 * @returns {FireData[]} - Validated fire data
 */
function validateFireData(fires) {
    return fires.filter(fire => {
        if (!fire || typeof fire !== 'object') {
            console.warn('Invalid fire data object:', fire);
            return false;
        }

        const lat = parseFloat(fire.lat);
        const lng = parseFloat(fire.lng);
        const brightness = parseFloat(fire.brightness);

        if (isNaN(lat) || isNaN(lng) || isNaN(brightness)) {
            console.warn('Invalid fire coordinates or brightness:', fire);
            return false;
        }

        // Ensure numeric types
        fire.lat = lat;
        fire.lng = lng;
        fire.brightness = brightness;
        fire.confidence = parseFloat(fire.confidence) || 0;

        return true;
    });
}

/**
 * Validate and sanitize air quality data
 * @param {any[]} stations - Raw air quality data from API
 * @returns {AirQualityData[]} - Validated air quality data
 */
function validateAirData(stations) {
    return stations.filter(station => {
        if (!station || typeof station !== 'object') {
            console.warn('Invalid air quality data object:', station);
            return false;
        }

        const lat = parseFloat(station.lat);
        const lng = parseFloat(station.lng);
        const pm25 = parseFloat(station.pm25);

        if (isNaN(lat) || isNaN(lng) || isNaN(pm25)) {
            console.warn('Invalid air quality coordinates or PM2.5:', station);
            return false;
        }

        // Ensure numeric types
        station.lat = lat;
        station.lng = lng;
        station.pm25 = pm25;

        return true;
    });
}

/**
 * Validate and sanitize ocean data
 * @param {any[]} stations - Raw ocean data from API
 * @returns {OceanData[]} - Validated ocean data
 */
function validateOceanData(stations) {
    return stations.filter(station => {
        if (!station || typeof station !== 'object') {
            console.warn('Invalid ocean data object:', station);
            return false;
        }

        const lat = parseFloat(station.latitude);
        const lng = parseFloat(station.longitude);

        if (isNaN(lat) || isNaN(lng)) {
            console.warn('Invalid ocean coordinates:', station);
            return false;
        }

        // Ensure numeric types
        station.latitude = lat;
        station.longitude = lng;
        station.temperature = station.temperature != null ? parseFloat(station.temperature) : null;
        station.water_level = station.water_level != null ? parseFloat(station.water_level) : null;

        return true;
    });
}

/**
 * Update fire layer with heatmap
 * @returns {void}
 */
function updateFireLayer() {
    // Convert fire data to heatmap format: [lat, lng, intensity]
    const heatData = fireData
        .filter(fire => fire.lat && fire.lng)
        .map(fire => {
            // Normalize brightness to 0-1 range (300-500K typical range)
            const intensity = Math.min(1, Math.max(0, (fire.brightness - 300) / 200));
            return [fire.lat, fire.lng, intensity];
        });

    fireHeatLayer.setLatLngs(heatData);
}

/**
 * Update air quality layer with clustered markers
 * @returns {void}
 */
function updateAirLayer() {
    airClusterLayer.clearLayers();

    airData.forEach(station => {
        // Data is already validated
        if (!station.lat || !station.lng) {
            return;
        }

        const color = getAirQualityColor(station.pm25);

        // Use smaller circle markers for clustering, store pm25 for cluster averaging
        const marker = L.circleMarker([station.lat, station.lng], {
            color: color,
            fillColor: color,
            fillOpacity: 0.8,
            radius: 6,
            weight: 1,
            pm25: station.pm25  // Store for cluster color calculation
        });

        marker.bindPopup(`
            <strong>🌬️ Air Quality</strong><br>
            <strong>PM2.5:</strong> ${station.pm25} μg/m³<br>
            <strong>Status:</strong> ${getAirQualityStatus(station.pm25)}<br>
            <em>Source: OpenAQ</em>
        `);

        airClusterLayer.addLayer(marker);
    });
}

/**
 * Update ocean layer with markers
 * @returns {void}
 */
function updateOceanLayer() {
    oceanLayer.clearLayers();

    oceanData.forEach(station => {
        // Data is already validated
        if (!station.latitude || !station.longitude) {
            return;
        }

        const color = getOceanColor(station.temperature);

        const marker = L.circleMarker([station.latitude, station.longitude], {
            color: color,
            fillColor: color,
            fillOpacity: 0.8,
            radius: 12,
            weight: 2
        });

        // Format values safely
        const tempDisplay = station.temperature != null ? `${station.temperature.toFixed(1)}°C` : 'N/A';
        const waterLevelDisplay = station.water_level != null ? `${station.water_level.toFixed(2)}m` : 'N/A';

        marker.bindPopup(`
            <strong>🌊 Ocean Temperature</strong><br>
            <strong>Location:</strong> ${station.name}<br>
            <strong>Temperature:</strong> ${tempDisplay}<br>
            <strong>Updated:</strong> ${station.last_updated}<br>
            <em>Source: Open-Meteo</em>
        `);

        oceanLayer.addLayer(marker);
    });
}

// Update conflict layer with UCDP data
function updateConflictLayer() {
    conflictLayer.clearLayers();

    conflictData.forEach(conflict => {
        if (!conflict.latitude || !conflict.longitude) return;

        const color = getConflictColor(conflict.deaths);
        const marker = L.circleMarker([conflict.latitude, conflict.longitude], {
            radius: Math.min(4 + Math.sqrt(conflict.deaths), 15),
            fillColor: color,
            color: '#000',
            weight: 1,
            opacity: 0.8,
            fillOpacity: 0.7
        });

        marker.bindPopup(`
            <strong>⚔️ ${conflict.conflict_name}</strong><br>
            <strong>Location:</strong> ${conflict.location}<br>
            <strong>Deaths:</strong> ${conflict.deaths}<br>
            <strong>Type:</strong> ${conflict.violence_type.replace('_', ' ')}<br>
            <strong>Parties:</strong> ${conflict.side_a} vs ${conflict.side_b}<br>
            <strong>Date:</strong> ${conflict.date}
        `);

        conflictLayer.addLayer(marker);
    });
}

// Update biodiversity layer with GBIF data
function updateBiodiversityLayer() {
    biodiversityLayer.clearLayers();

    biodiversityData.forEach(bio => {
        if (!bio.latitude || !bio.longitude) return;

        const color = getBiodiversityColor(bio.observations);
        const marker = L.circleMarker([bio.latitude, bio.longitude], {
            radius: Math.min(6 + Math.log10(bio.observations + 1) * 3, 20),
            fillColor: color,
            color: '#006400',
            weight: 2,
            opacity: 0.9,
            fillOpacity: 0.6
        });

        marker.bindPopup(`
            <strong>🦋 ${bio.location}</strong><br>
            <strong>Ecosystem:</strong> ${bio.ecosystem.replace('_', ' ')}<br>
            <strong>Observations:</strong> ${bio.observations.toLocaleString()}<br>
            <strong>Unique Species:</strong> ${bio.unique_species}
        `);

        biodiversityLayer.addLayer(marker);
    });
}

// Update aurora layer with heatmap
function updateAuroraLayer() {
    // Update Kp status in the toggle label
    const kpStatusEl = document.getElementById('kp-status');
    if (kpStatusEl && auroraData.kp_index) {
        kpStatusEl.textContent = `Kp ${auroraData.kp_index.value.toFixed(1)} - ${auroraData.kp_index.status}`;
    }

    // Convert aurora data to heatmap format: [lat, lng, intensity]
    const heatData = auroraData.points
        .filter(point => point.latitude && point.longitude && point.intensity > 5)  // Filter low intensity
        .map(point => {
            // Normalize intensity to 0-1 range
            const intensity = Math.min(1, point.intensity / 100);
            return [point.latitude, point.longitude, intensity];
        });

    auroraHeatLayer.setLatLngs(heatData);
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

// Get CSS class for air quality (used in clusters)
function getAirQualityClass(pm25) {
    if (pm25 > 55) return 'dangerous';
    if (pm25 > 35) return 'unhealthy';
    if (pm25 > 25) return 'sensitive';
    if (pm25 > 12) return 'moderate';
    return 'good';
}

function getConflictColor(deaths) {
    if (deaths >= 50) return '#8B0000';  // High fatalities
    if (deaths >= 10) return '#DC143C';  // Medium
    return '#FF6B6B';  // Low
}

function getBiodiversityColor(observations) {
    if (observations >= 1000) return '#228B22';  // High diversity
    if (observations >= 100) return '#32CD32';   // Medium
    return '#90EE90';  // Low
}

function getOceanColor(temp) {
    if (temp > 28) return '#FF6B35';  // Very warm
    if (temp > 25) return '#F7931E';  // Warm
    if (temp > 20) return '#00BFFF';  // Normal
    if (temp > 15) return '#0080FF';  // Cool
    return '#0040FF';  // Cold
}

function getAuroraColor(intensity) {
    // Aurora colors - green to purple gradient based on intensity
    if (intensity >= 50) return '#FF00FF';  // Bright purple - intense aurora
    if (intensity >= 30) return '#9400D3';  // Dark violet
    if (intensity >= 20) return '#00FF7F';  // Spring green
    if (intensity >= 10) return '#00FF00';  // Green - typical aurora
    return '#98FB98';  // Pale green - faint aurora
}

// Toggle control panel collapse state
function toggleControlPanel() {
    const panel = document.getElementById('control-panel');
    panel.classList.toggle('collapsed');
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

// Toggle health score breakdown panel
function toggleHealthBreakdown() {
    const panel = document.getElementById('health-breakdown');
    if (!panel) return;

    if (panel.style.display === 'none' || !panel.style.display) {
        panel.style.display = 'block';
        // Add slight animation
        panel.style.opacity = '0';
        setTimeout(() => {
            panel.style.opacity = '1';
        }, 10);
    } else {
        panel.style.opacity = '0';
        setTimeout(() => {
            panel.style.display = 'none';
        }, 200);
    }
} 
