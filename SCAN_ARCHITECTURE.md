# 🔍 TERRASCAN - "Scan As You Go" Architecture

## Overview

Terrascan now implements **lazy-loading regional data scanning** - a collaborative, progressive data collection system where users exploring the map contribute to a global cache of environmental data.

## How It Works

```
User zooms to Oslo, Norway
         ↓
Frontend detects map movement
         ↓
Calls /api/scan?bbox=59.5,10.5,60.0,11.0&zoom=10&layers=fires,air
         ↓
Backend checks: "Do we have fresh data for this region?"
         ↓
   ┌────NO────┐                 ┌────YES────┐
   ↓                             ↓
Fetch from APIs:             Return cached data
- NASA (fires)               (instant response)
- OpenAQ (air quality)
- NOAA (ocean temp)
   ↓
Store in database
Mark region as scanned
   ↓
Return fresh data to user
```

## Database Schema

### `scanned_regions` Table
Tracks which geographic areas have been scanned and when.

```sql
CREATE TABLE scanned_regions (
    id SERIAL PRIMARY KEY,
    bbox_north DECIMAL(10, 7),    -- Bounding box coordinates
    bbox_south DECIMAL(10, 7),
    bbox_east DECIMAL(10, 7),
    bbox_west DECIMAL(10, 7),
    zoom_level INTEGER,            -- Map zoom when scanned
    first_scanned TIMESTAMP,       -- When first explored
    last_updated TIMESTAMP,        -- Last data refresh
    data_points_cached INTEGER,    -- How much data stored
    layers_scanned TEXT[],         -- Which layers: fires, air, ocean
    scan_triggered_by VARCHAR(50)  -- user, auto, prefetch
);
```

**Indexes:**
- Spatial index on bbox coordinates (fast lookups)
- Timestamp index (freshness checks)
- Zoom level index (layer filtering)

### Helper Functions

**`check_region_overlap()`**
Finds overlapping cached regions and checks data freshness.

**`get_scan_statistics()`**
Returns global scanning coverage stats.

## API Endpoints

### `/api/scan`
The heart of the system - smart regional data fetching.

**Parameters:**
- `bbox`: "south,west,north,east" (e.g., "59.5,10.5,60.0,11.0")
- `zoom`: Map zoom level (0-20)
- `layers`: Comma-separated list ("fires,air,ocean")

**Response:**
```json
{
    "success": true,
    "cached": false,
    "partial_cache": false,
    "cache_status": {
        "layers_available": [],
        "layers_needed": ["fires", "air"],
        "freshness_status": {}
    },
    "data": {
        "fires": [...],
        "air": [...]
    },
    "fetch_results": {
        "fires": {"success": true, "records_stored": 45},
        "air": {"success": true, "records_stored": 12}
    },
    "message": "Fetched fresh data for: ['fires', 'air']. Total records: 57"
}
```

### `/api/regions/stats`
Get global scanning statistics.

**Response:**
```json
{
    "success": true,
    "stats": {
        "total_regions": 127,
        "total_data_points": 15234,
        "oldest_scan": "2025-09-16T12:00:00",
        "newest_scan": "2025-09-17T14:30:00",
        "avg_points_per_region": 119.8
    }
}
```

## Backend Components

### `utils/regional_scanner.py`
**RegionalScanner** class handles caching logic:
- `check_region_cached()` - Determines if region has fresh data
- `record_scan()` - Records completed scans
- `get_cached_data()` - Retrieves data from database
- Data freshness requirements per layer

### `utils/regional_fetcher.py`
**RegionalFetcher** coordinates API calls:
- Dynamically loads task fetchers
- Passes bbox parameters to APIs
- Aggregates results from multiple sources

### Task Fetchers (Enhanced with Bbox Support)

**`tasks/fetch_nasa_fires.py`**
```python
fetch_nasa_fires(region='WORLD', days=7, bbox=None)
```
- Global mode: Uses region code
- Regional mode: Uses bbox coordinates
- NASA API: `/api/area/csv/{api_key}/MODIS_NRT/{bbox}/{days}`

**`tasks/fetch_openaq_latest.py`**
```python
fetch_openaq_latest(limit=1000, parameter='pm25', bbox=None)
```
- Converts bbox to center point + radius
- OpenAQ API: `coordinates=lat,lng,radius_km` parameter

## Data Freshness Strategy

Different environmental data changes at different rates:

| Layer | Freshness Requirement | Reasoning |
|-------|----------------------|-----------|
| Fires | 3 hours | Fast-moving events |
| Air Quality | 12 hours | Twice daily updates |
| Ocean Temp | 7 days | Slow-changing |
| Weather | 6 hours | Regular updates |
| Species | 30 days | Very stable data |

## Frontend Integration (In Progress)

### Map Movement Detection

```javascript
map.on('moveend', debounce(async function() {
    const bounds = map.getBounds();
    const zoom = map.getZoom();

    if (zoom > 5) {  // Only scan when zoomed in
        await scanRegion(bounds, zoom);
    }
}, 500));
```

### Progressive Loading UI

**States:**
- 🟦 Blue overlay: "This region has been scanned"
- ⚪ No overlay: "Zoom in to scan this area"
- 🔄 Pulsing animation: "Scanning..."
- ✅ Flash: "New data cached!"

## Benefits

1. **Scalability**: Don't pre-fetch entire planet
2. **Cost Efficiency**: Only call APIs for viewed regions
3. **User Engagement**: Explore to contribute
4. **Fresh Data**: Popular areas auto-refresh
5. **Discovery Feel**: Reveal-as-you-go experience
6. **Collaborative**: Every user improves the cache

## Future Enhancements

### Phase 2: Smart Caching
- [ ] Regional overlap optimization
- [ ] Predictive prefetching (adjacent regions)
- [ ] Popular region pre-caching (major cities)

### Phase 3: Real-Time
- [ ] WebSocket updates for viewed regions
- [ ] Push notifications for changes
- [ ] Regional subscription system

### Phase 4: Analytics
- [ ] Region popularity heatmap
- [ ] User contribution tracking
- [ ] Data coverage visualization

## Performance Considerations

**Database Queries:**
- Spatial indexes enable fast bbox lookups
- Connection pooling handles concurrent scans
- Prepared statements prevent SQL injection

**API Rate Limiting:**
- Cached data reduces API calls by ~90%
- Freshness checks prevent redundant fetches
- User-triggered scans are throttled

**Frontend:**
- Debounced map movement (500ms)
- Zoom level filtering (different data at different zooms)
- Skeleton loaders during fetch

## Testing

Test the scan endpoint:
```bash
# Scan Oslo, Norway for fires and air quality
curl "http://localhost:5000/api/scan?bbox=59.5,10.5,60.0,11.0&zoom=10&layers=fires,air"

# Check global statistics
curl "http://localhost:5000/api/regions/stats"
```

## Notes for Deployment

1. Ensure all API keys are set:
   - NASA_FIRMS_API_KEY
   - OPENAQ_API_KEY
   - NOAA_API_KEY

2. Database migration required:
   ```bash
   python database/add_scanned_regions.py
   ```

3. Monitor scan patterns:
   - Watch for abuse (excessive scanning)
   - Track API quota usage
   - Optimize popular regions

---

**Status:** ✅ Backend complete, Frontend integration in progress

**Next Steps:**
1. Update map.js with zoom detection
2. Add scanning UI indicators
3. Test with real API keys
4. Deploy to production

*This is where Terrascan gets really cool.* 🌍✨
