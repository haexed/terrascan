# TODO

Pending work. When something ships: move to `CHANGELOG.md`, commit, delete from here.

## Git tags

- Drop `v` prefix from remaining old tags (`v3.6.5` → `3.6.5`, etc.) — needs force-push to `origin`, confirm before running.
- Push new tags to GitHub: `git push origin 3.6.8 3.6.9 3.6.10 3.6.11` (this sandbox can't reach the remote).

## Data sources

- `openweather` task not collecting — decide: keep (needs key) or migrate to Open-Meteo.
- `gbif` task not collecting.
- UCDP backfill: token is wired in, trigger a run to repopulate conflict events.

## Open-Meteo migration (planned)

Replace key-gated weather/air providers with Open-Meteo (free, global, no key). Priority: Air Quality API > Weather Forecast API > expand Marine API coverage > Historical/Climate API. Rationale in git history: `git show HEAD~:OPEN_METEO_INTEGRATION_PLAN.md`.

## Type safety follow-ups

- Python type hints across `web/app.py` formatters and DB helpers.
- Pydantic for API responses; Zod/TS on the JS side.
- Unit tests for `validate*Data` in `web/static/js/map.js`.
- OpenAPI/Swagger doc for `/api/*`.

## Cost / infra watch

- 2026-04-01 cleanup: DB volume ~6GB → ~3GB, but egress jumped same day (`dump_backup.py` one-shot). Confirm egress back to baseline.
- Postgres memory floor ~1GB; further reduction needs cold data out of `metric_data` or sharding by provider.

## Data providers

8 real `provider_key` values in `metric_data`: `nasa_firms`, `openaq`, `noaa_ocean`, `noaa_swpc`, `openweather`, `gbif`, `openmeteo_marine`, `ucdp`. Provider metadata (name, icon, coverage) is hardcoded independently in 4+ places with different subsets each: `base.html` footer (5), `system.html` cards (6, missing UCDP + noaa_swpc entirely), `about.html` (8, complete), `map.html` layer toggles (6), README's API key table.

Fix direction: one provider-metadata source (small DB table or config), `/system` cards → table read from it, reuse for footer/about/map labels.

## Frontend / UI

- `/map`: "Score Breakdown" panel overlaps health score widget; health score widget overlaps map controls at some viewport sizes.
- `/map`: page-level scrollbar with nothing to scroll to.
- `/map` (Leaflet): zooming in/out removes all other `leaflet-interactive` markers until manual refresh.
- `/tasks`: "All Tasks" cards + "Recent Task Runs" list redundant with `/system`'s table. Merge into one table: per-task row, last-run status/time/records, "View Logs" button.
