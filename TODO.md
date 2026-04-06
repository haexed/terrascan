# TODO

Pending and in-flight work. When something ships, move it to `CHANGELOG.md` with a date.

## Data sources

- **Weather data not collecting** — `openweather` task hasn't been run; status page correctly shows NO DATA. Decide: keep OpenWeatherMap (needs key) or migrate to Open-Meteo (see below).
- **Biodiversity data not collecting** — `gbif` task hasn't been run. Same status: NO DATA on `/status`.
- **UCDP backfill** — token is now wired in (`UCDP_API_TOKEN` set in Railway + local `.env`). Trigger a run to repopulate conflict events on the map; the cleanup script already exempts `provider_key='ucdp'` so they will not be wiped by retention.

## Open-Meteo migration (planned)

Replace key-gated weather/air providers with Open-Meteo (free, global, no key, CC-BY 4.0). Priority order:

1. **Air Quality API** — global PM2.5/PM10/NO2/SO2/CO/O3 at 11–25km, supersedes OpenAQ's ~65-city coverage.
2. **Weather Forecast API** — replaces OpenWeatherMap, no key required, higher resolution.
3. **Marine API** — already integrated as `fetch_openmeteo_marine.py`; expand coverage.
4. **Historical / Climate API** — long-term trend overlays.

(Detailed rationale and endpoints lived in the old `OPEN_METEO_INTEGRATION_PLAN.md`; pull from git history `git show HEAD~:OPEN_METEO_INTEGRATION_PLAN.md` if needed.)

## Type safety follow-ups

- Add Python type hints across `web/app.py` formatters and DB helpers.
- Consider Pydantic for API response schemas; Zod or TypeScript on the JS side.
- Unit tests for the `validate*Data` functions in `web/static/js/map.js`.
- OpenAPI/Swagger doc for `/api/*`.

## Cost / infra watch

- 2026-04-01: cleanup landed — DB volume dropped ~6GB → ~3GB, but **network egress jumped** the same day (the one-shot `dump_backup.py` streamed the full table out). Watch next billing cycle to confirm egress returns to baseline.
- Memory floor on Railway is still ~1GB postgres-side; further reduction likely requires moving cold data out of `metric_data` or sharding by provider.
