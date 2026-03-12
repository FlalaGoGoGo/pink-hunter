# Methodology And Pitfalls

## What To Review Before Repeating A Workflow
- The relevant ops runbook
- `city-etl-methods.md`
- `city-coverage-tracker.md`
- This file

## Repeated Lessons
- The main source of local chaos was not missing logic; it was duplicated workspaces, duplicated backups, and duplicated intermediate files.
- Official boundary reuse is a force multiplier. Prebuild the boundary layer first, then activate cities on top of it.
- Size gates protect GitHub risk, but product performance also depends on shard granularity. Hotspot cities need tighter shard targets.
- Methods are only reusable if they are written down in docs immediately after they work.

## Capture Rules
- New source family or parser rule: update `city-etl-methods.md`
- New inclusion or exclusion decision: update `city-coverage-tracker.md`
- New workflow or failure mode: update this file or the relevant runbook

## Known Pitfalls
- `GitHub/` backup folders silently consume most local disk space.
- `data/normalized/`, `data/tmp/`, and copied `* 2*` files create false clutter and accidental sync drift.
- GitHub Pages can still feel slow if the runtime falls back to eager coverage loading or large single-city shards.
