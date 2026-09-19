# TODO

Pending and in-flight work. When something ships, move it to `CHANGELOG.md` with a date, and commit — do this proactively within a session when applicable, don't wait to be asked each time.

## Git tags

- **Drop the `v` prefix from all tags** (`v3.6.5` → `3.6.5`, etc.) — needs recreating each tag under the new name and deleting the old one; since `origin` is a real GitHub remote, this also needs force-pushing the rename and deleting the old tags there, so confirm before doing it rather than running it unattended.
- **Tags are stale**: newest tag is `v3.6.5` (2026-01-23, commit `5636dfd`); `HEAD` is 16 commits ahead (`git describe` → `v3.6.5-16-g0b40a2c`), including the version bumps to 3.6.6 and 3.6.7 that were never tagged. Tag `3.6.7` (current `HEAD`) and decide whether to backfill `3.6.6`.
- Not a bug, just a landmine for future archaeology: `v3.7.0` (2025-12-30) sits chronologically *before* `v3.6.2` in version-number order — it was a heatmaps/clustering experiment that got reverted same-day and the version line continued as 3.6.x instead.

## Data sources

- **Weather data not collecting** — `openweather` task hasn't been run; status page correctly shows No data. Decide: keep OpenWeatherMap (needs key) or migrate to Open-Meteo (see below).
- **Biodiversity data not collecting** — `gbif` task hasn't been run. Same status: No data on `/status`.
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

## Frontend / UI

- **Map page (`/map`)**: "Score Breakdown" panel overlaps the health score widget; the health score widget overlaps the map controls panel at some viewport sizes. Needs a real positioning/z-index pass, not just nudged offsets.
- **Map page**: shows a page-level scrollbar with nothing to scroll to (likely `#map`/`.stats-banner` height math vs viewport).
- **Map page (Leaflet)**: zooming in/out removes all other `leaflet-interactive` markers (dots) except the last-touched layer, until a manual refresh. Likely a layer redraw/z-index bug in `map.js`, not a data issue.
- **Tasks page (`/tasks`)**: "All Tasks" cards + separate "Recent Task Runs" list are redundant with `/system`'s "Recent Task Executions" table. Combine into one table: per-task row with last-run status/time/records columns and a "View Logs" button, drop the separate recent-runs list.
- **Heading hierarchy**: `/tasks` skips levels (h1 → h3 → h5) per W3C Nu Html Checker — `<h1 class="h2">Task Monitoring</h1>` → `<h3 class="h4">All Tasks</h3>` → `<h5 class="card-title">{{task.name}}</h5>`. Needs a real h2/h3/h4 pass across `tasks.html` (and worth checking other templates), keeping the Bootstrap `.h1`–`.h6` size classes for visual sizing so nothing changes on screen.
- **HTML comments**: strip `<!-- ... -->` comments out of the Jinja templates (`base.html`, `map.html`, `tasks.html`, etc.) — codebase-wide cleanup, not user-facing.

Fixed this pass (see `CHANGELOG.md`): card hover animations removed, heading-color specificity bug (`.h1`–`.h6` utility classes losing to Bootstrap instead of our white override) fixed site-wide, `.modal-title` white-on-white in the Task Logs modal, "NO DATA"/"SYSTEM STATUS & DATA PROVIDERS"/"DATABASE SCHEMA DOCUMENTATION" screaming caps, `.data-source` brown swapped for on-brand sage green, "—" placeholders on `/map` replaced with real `0` vs "No data" (was using Jinja truthiness, so a real `0` count rendered as "—"), invalid `<meta http-equiv>` cache tags removed (already set as real HTTP headers via the `no_cache` decorator), `<div>` inside `<label>` (invalid HTML) on `/map`'s layer toggles fixed.
