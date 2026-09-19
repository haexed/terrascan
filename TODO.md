# TODO

Pending work. When something ships: move to `CHANGELOG.md`, commit, delete from here.

**Design/visual status convention (per explicit instruction, 2026-09-19):** Claude does not have visual judgment on this project and must not claim a design/visual fix is "done." Such items get marked **tried fix — needs QA** (a change was made and is functionally verified — page loads, no console/HTTP errors — but whether it looks right is for the human to confirm) instead of "done." Only mechanical/factual fixes (data bugs, dead code removal, doc corrections, etc.) get marked "done."

## Verbatim todos from session (2026-09-19)

Every message this session prefixed "todo" / "todo:" (plus a couple of other explicit asks), quoted exactly as written, one per numbered item. Any explanation is a sub-bullet underneath, never merged into the quote. Still-open ones are also folded into the topical sections below.

1. `todo: "Score Breakdown" overlapping health box.`
   - tried fix, needs QA (3.6.13)
2. `todo: health box overlapping map controls.`
   - tried fix, needs QA (3.6.13)
3. `todo: front page shows scrollbars without effect.`
   - **open**
4. `todo remove all "—". e.g. Active Fires. should be 0 (zero) or no data.`
   - done
5. `todo: zooming in map and out removes all other leaflet-interactive (dots) until refresh, broken.`
   - **open**
6. `todo: tasks: combine "all tasks" and recents tasks into one table, where some columns contain info on last run (per task), with logs button. system shows last tasks run its redundant`
   - **open**
7. `todo: delete all html comments`
   - done (3.6.9)
8. `todo drop all "v" prefix in all git tags.`
   - **open**, needs confirmation (force-push to a real remote)
9. `todo: check if newest tags are set on commits.`
   - answered + fixed (tagged 3.6.8-3.6.14)
10. `todo: chlog+commit when applicable in session`
    - adopted as ongoing practice
11. `todo: theres a v3.7.0 in github, doesnt seem right`
    - answered (abandoned heatmaps experiment) + deleted per follow-up "tag deleted in github"
12. `todo: fix data sources info: e.g. system open-meteo says 0 records, but also says 6283 records further down.`
    - done (3.6.10)
13. `todo: collects data providers in system in a nicer table than the huge 6 cards.`
    - **open**
14. `todo: get a hold of the actual data providers, website shows different providers everywhere, make sure none are hardcoded, should be pure data in db.`
    - **open**, investigated and documented under "Data providers" below
15. `todo replace ugly data-source brown color to a normal terrascan color`
    - tried fix, needs QA (3.6.8, `.data-source` → `var(--infp-sage)`, a new palette color). Landed in the earlier non-WCAG commit, not the one reverted in 3.6.14, so it's still live.
16. `todo move planetary health box above "Live Environmental Layers" and let "Live Environmental Layers" be the pullup, solving the blocking of map-controls. no need for the dupe control-header h5`
    - tried fix, needs QA (3.6.13)
17. `todo: still ugly brown, e.g. on .eco-card a:not(.btn):hover . links have no unity no more`
    - tried fix, needs QA (3.6.17): removed `--infp-brown` entirely, dropped the `.eco-card a:hover`/`a:hover` color changes rather than guess a replacement — hover now only changes decoration style, not color.
18. `todo remove css .pulse`
    - done: removed `.pulse` class + its two badge usages (`dashboard.html`, `index.html`).
19. `todo remove css .pulse and its usage`
    - done: previous pass missed two other direct users of the `pulse` keyframe (`.task-running .status-badge`, `.stat-item.scan-status`). Removed both rules and both `@keyframes pulse` definitions. Left `scan-pulse` and `new-marker-pulse` alone — different names, not literally "pulse".
20. `todo remove/replace all dotted decor on anchors. solid green is plenty. infp-brown still in use. continue cleaning.`
    - tried fix, needs QA (3.6.17): every dotted underline → `underline solid var(--infp-green)`. `--infp-brown` variable and all its usages removed entirely, not replaced with a guessed color.
21. `tofo footer yellow links on green bg cant have green underline`
    - fixed: footer link underline now follows the link's own color instead of a fixed green.
22. `todo remove underline decor on all btn/links in btn`
    - fixed: `.eco-card a` had lost its `:not(.btn)` exclusion during #20's edit, so `.btn` anchors inside cards showed an underline. Restored the exclusion, verified `text-decoration: none` via computed style.
23. `todo find everything like "✨ No stale tasks found". it's a popup which are blocking, and it's factually wrong, and it looks like magic hurray when it's an error message, just do a normal toast.`
    - first pass wrong: assumed this specific message wasn't the target since it's not a native `alert()`, fixed 7 actual `alert()` calls elsewhere instead.
    - user reported it was still blocking. Reproduced with Selenium: `.toast-notification` at `top:100px; right:20px` measurably overlapped the "Cleanup Stale"/"Refresh Status" buttons on `/tasks`. Moved to `bottom:20px; right:20px`, re-measured, no overlap on any page.
24. `"Running now: 2". "✨ No stale tasks found". it's wrong. and the stars just looks stupid, looks based on assumptions`
    - checked the actual data: both "running" tasks were `openaq_latest` running concurrently (18min and 3min old), neither past the 30-min stale threshold — technically accurate, but "no stale tasks found" implied nothing was wrong. Reworded to state the actual criteria ("No tasks running longer than 30 minutes"), dropped the ✨.
25. `todo add version arg to all linked local files (js+css) for easy cache bust per version`
    - done: `?v={{ version }}` added to all 4 local static includes.
26. `keep mine verbatim in todo. add your prose if needed as sub bullets`
    - done: reformatted this whole list to this structure.
27. `next: fix tasks page table as mentioned earlier`
    - done: `/tasks` "All Tasks" cards + "Recent Task Runs" list replaced with one table, one row per task (Task, Status, Schedule, Last Run, Result, View Logs). Schedule column now honestly shows "No data" instead of silently hiding the badge — every task in the DB currently has `cron_schedule = null` (matches the README's "on-demand, not cron" design), the old cards version just hid this instead of showing it.
28. `todo: no single tasks should be able to start while it's already running, creating dupes.`
    - done: `TaskRunner.run_task()` now checks `get_running_tasks()` before starting a run and returns `{success: false, error: "Task '<name>' is already running"}` instead of calling `start_task_run()`. Verified directly against the DB: `openaq_latest` (which had 2 concurrent stuck runs from earlier in this session) is correctly blocked, `nasa_fires_global` is correctly allowed. Confirmed no new `task_log` row gets created when blocked.
    - along the way, fixed two response-building bugs that would've swallowed the new error message before it reached the user: `/api/collect-biodiversity` and `/api/tasks/<name>/run` both hardcoded a "completed" message regardless of actual success/failure and never included `result['error']`.
    - the 2 pre-existing stuck `openaq_latest` runs from earlier in this session are untouched — they'll clear via the existing 30-min stale cleanup once they cross the threshold, didn't intervene manually.

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
- Link/hover colors: tried fix, needs QA (3.6.17) — `--infp-brown` removed, anchors now just solid-green-underline with no color change on hover. Whether this reads as "unified" is for a human to judge; needs an actual design pass if not, not another guess from Claude.
