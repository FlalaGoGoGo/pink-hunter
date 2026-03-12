# Runbook: Boundary Prebuild

## Purpose
- Prebuild official jurisdiction boundary caches for a state or province before city-by-city activation.

## Command
```bash
./scripts/ops_runner.sh prebuild-boundaries --country us --state ca
```

## When To Use
- Starting a new state or province cycle.
- Refreshing stale official boundary caches before a major city batch.

## Expected Output
- Canonical files under `data/reference/boundaries/<country>/<state>/`
- Updated boundary catalog metadata

## Afterward
- Review candidate cities for that cycle.
- Record any boundary exceptions or naming overrides in the research docs.
