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

// Scan threshold - show scan button when zoomed in this much (8 = regional level)
const SCAN_ZOOM_THRESHOLD = 8;

// Viewport loading threshold - only load viewport data when zoomed in this much
const VIEWPORT_LOAD_THRESHOLD = 5;

// Debounce timer for map movement
let mapMoveTimeout = null;

// Viewport data is fetched in whole grid cells rather than by the exact
// viewport bbox. An exact bbox is a continuous value, so panning never
// produced the same key twice and every drag paid a fresh round trip. Cells
// are aligned to a per-zoom grid, so panning around an area reuses what is
// already loaded and only the newly exposed cells are fetched.
const TILE_CACHE_TTL = 5 * 60 * 1000;
const TILE_CACHE_MAX = 250;

// Cell size in degrees at a given zoom: 45deg at z=6, halving each level in.
const TILE_BASE_ZOOM = 3;

// Don't fan out into an unbounded number of requests for one viewport
const TILE_MAX_PER_VIEW = 9;

// Neighbour cells are warmed after the visible ones are drawn, and kept few:
// the backend runs one worker, so prefetches compete with the visible fetch.
const TILE_PREFETCH_MAX = 4;
const TILE_PREFETCH_DELAY = 400;

const tileCache = new Map();     // cache key -> {data, time}
const tileRequests = new Map();  // cache key -> in-flight Promise
let prefetchTimeout = null;

// Cell keys currently drawn, so an unchanged viewport doesn't redraw
let renderedKeys = '';

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', function () {
    initMap();
    setInterval(refreshMapData, 15 * 60 * 1000); // Auto-refresh every 15 minutes

    // Create toast element for scan notifications
    createScanToast();
});

// Throttle utility for continuous map movement
function throttle(func, wait) {
    let last = 0;
    return function throttled(...args) {
        const now = Date.now();
        if (now - last < wait) return;
        last = now;
        func(...args);
    };
}

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

    // Create map centered on world view
    map = L.map('map', {
        center: [20, 0],
        zoom: 2,
        minZoom: 2,
        maxBounds: worldBounds,
        maxBoundsViscosity: 1.0,
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
    });

    // Satellite layer (Esri World Imagery) - DEFAULT VIEW
    satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: '© Esri, Maxar, Earthstar Geographics'
    }).addTo(map);

    // Initialize data layers
    fireLayer = L.layerGroup().addTo(map);
    airLayer = L.layerGroup().addTo(map);
    oceanLayer = L.layerGroup().addTo(map);
    conflictLayer = L.layerGroup().addTo(map);
    biodiversityLayer = L.layerGroup().addTo(map);
    auroraLayer = L.layerGroup().addTo(map);

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

    // Reload when the map moves. This has to run at every zoom level:
    // loadEnvironmentalData() picks viewport or global data itself, and
    // skipping the call when zoomed out left the map showing only the handful
    // of markers from the last zoomed-in fetch. The debounce is short because
    // cells already held render without touching the network.
    const debouncedLoad = debounce(() => loadEnvironmentalData(), 120);

    // While a drag is in progress, fill the leading edge from cells already
    // held. Waiting for the drag to be released left newly exposed ground
    // blank until then. Cache-only: this never touches the network.
    map.on('move', throttle(renderCachedTiles, 200));

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

                // Add new stations to the air layer
                result.stations.forEach(station => {
                    if (!station.lat || !station.lng) return;

                    const color = getAirQualityColor(station.pm25);
                    const marker = L.circleMarker([station.lat, station.lng], {
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.8,
                        radius: 10,
                        weight: 2
                    });

                    marker.bindPopup(`
                        <strong>🌬️ ${station.location || 'Air Quality Station'}</strong><br>
                        <strong>PM2.5:</strong> ${station.pm25} μg/m³<br>
                        <strong>Status:</strong> ${getAirQualityStatus(station.pm25)}<br>
                        <em>📍 Scanned just now</em>
                    `);

                    airLayer.addLayer(marker);

                    // Flash animation for new markers
                    marker._path?.classList.add('new-marker-pulse');
                });

                // Also add to airData for consistency
                airData = [...airData, ...result.stations];

                // A scan stores new rows, so every cached cell is stale
                tileCache.clear();
                renderedKeys = '';
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
            map.addLayer(fireLayer);
        } else {
            map.removeLayer(fireLayer);
        }
    });

    document.getElementById('air-layer').addEventListener('change', function () {
        if (this.checked) {
            map.addLayer(airLayer);
        } else {
            map.removeLayer(airLayer);
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
            map.addLayer(auroraLayer);
        } else {
            map.removeLayer(auroraLayer);
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
 * Cell size in degrees for a zoom level
 * @param {number} zoom - Leaflet zoom level
 * @returns {number} cell width and height in degrees
 */
function tileSize(zoom) {
    return 360 / Math.pow(2, Math.max(0, zoom - TILE_BASE_ZOOM));
}

/**
 * Grid cells covering the current viewport
 * @returns {{key: string, bbox: string}[]} cells, or [] when zoomed out
 */
function viewportTiles() {
    if (!map) return [];

    const zoom = map.getZoom();
    const size = tileSize(zoom);
    const bounds = map.getBounds();

    const south = Math.max(-90, bounds.getSouth());
    const north = Math.min(90, bounds.getNorth());
    const west = Math.max(-180, bounds.getWest());
    const east = Math.min(180, bounds.getEast());

    const tiles = [];
    const x0 = Math.floor((west + 180) / size);
    const x1 = Math.floor((east + 180) / size);
    const y0 = Math.floor((south + 90) / size);
    const y1 = Math.floor((north + 90) / size);

    for (let x = x0; x <= x1; x++) {
        for (let y = y0; y <= y1; y++) {
            tiles.push(makeTile(zoom, x, y, size));
            if (tiles.length > TILE_MAX_PER_VIEW) return tiles.slice(0, TILE_MAX_PER_VIEW);
        }
    }
    return tiles;
}

/**
 * Build a cell descriptor from its grid coordinates
 * @param {number} zoom - Zoom level the grid belongs to
 * @param {number} x - Cell column
 * @param {number} y - Cell row
 * @param {number} size - Cell size in degrees
 * @returns {{key: string, bbox: string}}
 */
function makeTile(zoom, x, y, size) {
    const tileWest = Math.max(-180, x * size - 180);
    const tileEast = Math.min(180, (x + 1) * size - 180);
    const tileSouth = Math.max(-90, y * size - 90);
    const tileNorth = Math.min(90, (y + 1) * size - 90);
    return {
        key: `${zoom}/${x}/${y}`,
        bbox: `${tileSouth},${tileWest},${tileNorth},${tileEast}`
    };
}

/**
 * Cells immediately around the viewport, for prefetching
 * @returns {{key: string, bbox: string}[]}
 */
function neighbourTiles() {
    if (!map) return [];

    const zoom = map.getZoom();
    const size = tileSize(zoom);
    const bounds = map.getBounds();
    const inView = new Set(viewportTiles().map(t => t.key));

    const x0 = Math.floor((Math.max(-180, bounds.getWest()) + 180) / size) - 1;
    const x1 = Math.floor((Math.min(180, bounds.getEast()) + 180) / size) + 1;
    const y0 = Math.floor((Math.max(-90, bounds.getSouth()) + 90) / size) - 1;
    const y1 = Math.floor((Math.min(90, bounds.getNorth()) + 90) / size) + 1;

    const maxIndex = Math.pow(2, Math.max(0, zoom - TILE_BASE_ZOOM));
    const tiles = [];
    for (let x = Math.max(0, x0); x <= Math.min(maxIndex - 1, x1); x++) {
        for (let y = Math.max(0, y0); y <= Math.min(maxIndex - 1, y1); y++) {
            const tile = makeTile(zoom, x, y, size);
            if (!inView.has(tile.key)) tiles.push(tile);
        }
    }
    return tiles;
}

/**
 * Read a cell from cache if it hasn't expired
 * @param {string} key - Cache key
 * @returns {object|null} cached response, or null
 */
function cachedTile(key) {
    const entry = tileCache.get(key);
    if (!entry) return null;
    if (Date.now() - entry.time > TILE_CACHE_TTL) {
        tileCache.delete(key);
        return null;
    }
    return entry.data;
}

/**
 * Fetch one cell, reusing an in-flight request for the same cell
 * @param {{key: string, bbox: string}} tile - Cell to fetch
 * @returns {Promise<object|null>} the response, or null on failure
 */
function fetchTile(tile) {
    const pending = tileRequests.get(tile.key);
    if (pending) return pending;

    const url = tile.bbox
        ? `/api/map-data?bbox=${encodeURIComponent(tile.bbox)}`
        : '/api/map-data';

    const request = fetch(url)
        .then(response => response.json())
        .then(data => {
            if (!data.success) return null;
            tileCache.delete(tile.key);
            tileCache.set(tile.key, { data, time: Date.now() });
            while (tileCache.size > TILE_CACHE_MAX) {
                tileCache.delete(tileCache.keys().next().value);
            }
            return data;
        })
        .catch(error => {
            console.error(`Error loading map data for ${tile.key}:`, error);
            return null;
        })
        .finally(() => tileRequests.delete(tile.key));

    tileRequests.set(tile.key, request);
    return request;
}

/**
 * Load environmental data for the current view
 *
 * Renders whatever is already cached straight away, then fills in the cells
 * that are missing and renders again. Panning back to somewhere already seen
 * therefore draws without waiting on the network.
 *
 * @param {boolean} force - Ignore and refill the cache
 * @returns {Promise<void>}
 */
async function loadEnvironmentalData(force = false) {
    const zoomedIn = map && map.getZoom() >= VIEWPORT_LOAD_THRESHOLD;
    const tiles = zoomedIn ? viewportTiles() : [{ key: 'global', bbox: '' }];

    if (force) {
        tiles.forEach(tile => tileCache.delete(tile.key));
        renderedKeys = '';
    }

    const signature = tiles.map(t => t.key).join('|');
    const cached = tiles.map(tile => cachedTile(tile.key));
    const missing = tiles.filter((tile, i) => cached[i] === null);

    // Draw what we already have before going to the network
    if (cached.some(Boolean) && signature !== renderedKeys) {
        renderTiles(signature, cached.filter(Boolean));
    }

    if (missing.length) {
        await Promise.all(missing.map(fetchTile));
        renderTiles(signature, tiles.map(tile => cachedTile(tile.key)).filter(Boolean));
    } else if (signature !== renderedKeys) {
        renderTiles(signature, cached.filter(Boolean));
    }

    if (zoomedIn) schedulePrefetch();
}

/**
 * Queue a neighbour prefetch once the visible cells have settled
 * @returns {void}
 */
function schedulePrefetch() {
    clearTimeout(prefetchTimeout);
    prefetchTimeout = setTimeout(prefetchNeighbours, TILE_PREFETCH_DELAY);
}

/**
 * Redraw from cache alone, for use while the map is still moving
 * @returns {void}
 */
function renderCachedTiles() {
    if (!map || map.getZoom() < VIEWPORT_LOAD_THRESHOLD) return;

    const tiles = viewportTiles();
    const signature = tiles.map(t => t.key).join('|');
    if (signature === renderedKeys) return;

    const responses = tiles.map(tile => cachedTile(tile.key));
    if (responses.some(response => response === null)) return;

    renderTiles(signature, responses);
}

/**
 * Warm the cells around the viewport so a short pan has data ready
 * @returns {void}
 */
async function prefetchNeighbours() {
    if (tileRequests.size) {
        // Visible cells are still loading; don't compete with them
        schedulePrefetch();
        return;
    }

    const missing = neighbourTiles()
        .filter(tile => !cachedTile(tile.key))
        .slice(0, TILE_PREFETCH_MAX);

    // One at a time. Firing these in parallel put four requests in front of
    // the next visible fetch, and with a 3-connection pool against a remote
    // database that turned a 435ms request into 2s.
    for (const tile of missing) {
        if (tileRequests.size) return;
        await fetchTile(tile);
    }
}

/**
 * Merge cell responses and draw them
 * @param {string} signature - Key list identifying what is being drawn
 * @param {object[]} responses - Cell responses to merge
 * @returns {void}
 */
function renderTiles(signature, responses) {
    if (!responses.length) return;

    fireData = validateFireData(mergeRecords(responses, 'fires', f => `${f.lat},${f.lng},${f.brightness}`));
    airData = validateAirData(mergeRecords(responses, 'air_quality', a => `${a.lat},${a.lng},${a.pm25}`));
    oceanData = validateOceanData(mergeRecords(responses, 'ocean', o => `${o.latitude},${o.longitude},${o.name}`));
    conflictData = mergeRecords(responses, 'conflicts', c => `${c.latitude},${c.longitude},${c.date},${c.conflict_name}`);
    biodiversityData = mergeRecords(responses, 'biodiversity', b => `${b.latitude},${b.longitude},${b.ecosystem}`);

    const auroraPoints = [];
    const seenAurora = new Set();
    let kpIndex = null;
    for (const response of responses) {
        const aurora = response.aurora || {};
        if (kpIndex === null && aurora.kp_index) kpIndex = aurora.kp_index;
        for (const point of aurora.points || []) {
            const id = `${point.latitude},${point.longitude}`;
            if (seenAurora.has(id)) continue;
            seenAurora.add(id);
            auroraPoints.push(point);
        }
    }
    auroraData = { points: auroraPoints, kp_index: kpIndex };

    updateFireLayer();
    updateAirLayer();
    updateOceanLayer();
    updateConflictLayer();
    updateBiodiversityLayer();
    updateAuroraLayer();

    renderedKeys = signature;
}

/**
 * Concatenate one field across cell responses, dropping duplicates
 *
 * A record sitting exactly on a cell boundary comes back from both
 * neighbours, since the API's bbox filter includes both edges.
 *
 * @param {object[]} responses - Cell responses
 * @param {string} field - Response field to merge
 * @param {function(object): string} identify - Record identity
 * @returns {object[]} merged records
 */
function mergeRecords(responses, field, identify) {
    const seen = new Set();
    const merged = [];
    for (const response of responses) {
        for (const record of response[field] || []) {
            const id = identify(record);
            if (seen.has(id)) continue;
            seen.add(id);
            merged.push(record);
        }
    }
    return merged;
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
 * Update fire layer with markers
 * @returns {void}
 */
function updateFireLayer() {
    fireLayer.clearLayers();

    fireData.forEach(fire => {
        // Data is already validated, but double-check to be safe
        if (!fire.lat || !fire.lng) {
            return;
        }

        const color = getFireColor(fire.brightness);
        const radius = Math.max(5, Math.min(20, fire.brightness / 50));

        const marker = L.circleMarker([fire.lat, fire.lng], {
            color: color,
            fillColor: color,
            fillOpacity: 0.7,
            radius: radius,
            weight: 1
        });

        marker.bindPopup(`
            <strong>🔥 Active Fire</strong><br>
            <strong>Location:</strong> ${fire.lat.toFixed(3)}, ${fire.lng.toFixed(3)}<br>
            <strong>Brightness:</strong> ${fire.brightness}K<br>
            <strong>Confidence:</strong> ${fire.confidence}%<br>
            <strong>Detected:</strong> ${fire.acq_date}<br>
            <em>Source: NASA FIRMS</em>
        `);

        fireLayer.addLayer(marker);
    });
}

/**
 * Update air quality layer with markers
 * @returns {void}
 */
function updateAirLayer() {
    airLayer.clearLayers();

    airData.forEach(station => {
        // Data is already validated
        if (!station.lat || !station.lng) {
            return;
        }

        const color = getAirQualityColor(station.pm25);
        const radius = Math.max(8, Math.min(25, station.pm25 / 2));

        const marker = L.circleMarker([station.lat, station.lng], {
            color: color,
            fillColor: color,
            fillOpacity: 0.6,
            radius: radius,
            weight: 2
        });

        marker.bindPopup(`
            <strong>🌬️ Air Quality Station</strong><br>
            <strong>Location:</strong> ${station.lat.toFixed(3)}, ${station.lng.toFixed(3)}<br>
            <strong>PM2.5:</strong> ${station.pm25} μg/m³<br>
            <strong>Status:</strong> ${getAirQualityStatus(station.pm25)}<br>
            <em>Source: OpenAQ</em>
        `);

        airLayer.addLayer(marker);
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

// Update aurora layer with NOAA SWPC data
function updateAuroraLayer() {
    auroraLayer.clearLayers();

    // Update Kp status in the toggle label
    const kpStatusEl = document.getElementById('kp-status');
    if (kpStatusEl && auroraData.kp_index) {
        kpStatusEl.textContent = `Kp ${auroraData.kp_index.value.toFixed(1)} - ${auroraData.kp_index.status}`;
    }

    // Aurora points are rendered as semi-transparent circles
    // Using larger radius and lower opacity for aurora glow effect
    auroraData.points.forEach(point => {
        if (!point.latitude || !point.longitude) return;

        const color = getAuroraColor(point.intensity);
        const radius = Math.min(3 + point.intensity * 0.5, 15);

        const marker = L.circleMarker([point.latitude, point.longitude], {
            radius: radius,
            fillColor: color,
            color: color,
            weight: 0,
            opacity: 0.8,
            fillOpacity: 0.5
        });

        marker.bindPopup(`
            <strong>🌌 Aurora Forecast</strong><br>
            <strong>Intensity:</strong> ${point.intensity}%<br>
            <strong>Location:</strong> ${point.latitude.toFixed(1)}°, ${point.longitude.toFixed(1)}°<br>
            <em>Source: NOAA SWPC OVATION Model</em>
        `);

        auroraLayer.addLayer(marker);
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
        await loadEnvironmentalData(true);

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
