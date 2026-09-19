# TODO

Pending work. When something ships: move to `CHANGELOG.md`, commit, delete from here.

## Verbatim todos from session (2026-09-19)

Every message this session prefixed "todo" / "todo:", quoted exactly as written. Status noted after each; still-open ones are also folded into the topical sections below.

1. `todo: "Score Breakdown" overlapping health box.` — done (3.6.13)
2. `todo: health box overlapping map controls.` — done (3.6.13)
3. `todo: front page shows scrollbars without effect.` — **open**
4. `todo remove all "—". e.g. Active Fires. should be 0 (zero) or no data.` — done
5. `todo: zooming in map and out removes all other leaflet-interactive (dots) until refresh, broken.` — **open**
6. `todo: tasks: combine "all tasks" and recents tasks into one table, where some columns contain info on last run (per task), with logs button. system shows last tasks run its redundant` — **open**
7. `todo: delete all html comments` — done (3.6.9)
8. `todo drop all "v" prefix in all git tags.` — **open**, needs confirmation (force-push to a real remote)
9. `todo: check if newest tags are set on commits.` — answered + fixed (tagged 3.6.8-3.6.14)
10. `todo: chlog+commit when applicable in session` — adopted as ongoing practice
11. `todo: theres a v3.7.0 in github, doesnt seem right` — answered (abandoned heatmaps experiment) + deleted per follow-up "tag deleted in github"
12. `todo: fix data sources info: e.g. system open-meteo says 0 records, but also says 6283 records further down.` — done (3.6.10)
13. `todo: collects data providers in system in a nicer table than the huge 6 cards.` — **open**
14. `todo: get a hold of the actual data providers, website shows different providers everywhere, make sure none are hardcoded, should be pure data in db.` — **open**, investigated and documented under "Data providers" below
15. `todo replace ugly data-source brown color to a normal terrascan color` — done (3.6.8, `.data-source` → `var(--infp-sage)`, a new palette color introduced then). This landed in the earlier non-WCAG commit, not the one reverted in 3.6.14, so it's still live — flag if this should've been reverted too as a "forced random color."
16. `todo move planetary health box above "Live Environmental Layers" and let "Live Environmental Layers" be the pullup, solving the blocking of map-controls. no need for the dupe control-header h5` — done (3.6.13)
17. `todo: still ugly brown, e.g. on .eco-card a:not(.btn):hover . links have no unity no more` — **open**, folded into the link/hover-color entry below
18. `todo remove css .pulse` — done: removed `.pulse` class + its two badge usages (`dashboard.html`, `index.html`)
19. `todo remove css .pulse and its usage` — done: previous pass missed the two other direct users of the `pulse` keyframe (`.task-running .status-badge` in `style.css`, `.stat-item.scan-status` in `map.css`) — removed both rules and both `@keyframes pulse` definitions. `scan-pulse` (different name, map scan button) and `new-marker-pulse` (different name, `map.js`) left alone — not literally "pulse".

## Git tags

- Drop `v` prefix from remaining old tags (`v3.6.5` → `3.6.5`, etc.) — needs force-push to `origin`, confirm before running.
- Push new tags to GitHub: `git push origin 3.6.8 3.6.9 3.6.10 3.6.11 3.6.12 3.6.13 3.6.14` (this sandbox can't reach the remote).
- WCAG/axe-core audit was run (2026-09-19): violations found and documented, but the auto-applied fixes were reverted per feedback (ask was to report, not change rules). If a real fix pass is wanted, do it as a reviewed, incremental PR-style set of changes instead of a single sweep.

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

- `/map`: page-level scrollbar with nothing to scroll to.
- `/map` (Leaflet): zooming in/out removes all other `leaflet-interactive` markers until manual refresh.
- `/tasks`: "All Tasks" cards + "Recent Task Runs" list redundant with `/system`'s table. Merge into one table: per-task row, last-run status/time/records, "View Logs" button.
- Link/hover colors: `--infp-brown` (used for `a:hover`, `.eco-card a:hover`) called out as ugly; link styling generally feels inconsistent. Needs an actual design pass, not a color swap guessed by Claude.
