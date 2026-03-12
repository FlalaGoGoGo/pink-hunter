# Factory Expansion Roadmap

## Goal
- Scale Pink Hunter coverage across the United States and Canada with repeatable state or province batches instead of ad hoc city-by-city work.

## Cycle Order
- Cycle A: California + British Columbia
- Cycle B: Ontario + Washington
- Cycle C: New York / New Jersey / Pennsylvania / Massachusetts
- Cycle D: Michigan / Illinois / Wisconsin

## Standard Cycle Sequence
1. Prebuild official state or province boundaries.
2. Produce a candidate city queue.
3. Validate official public single-tree datasets.
4. Publish cities incrementally.
5. Refresh shards, coverage, and metadata.
6. Pass the size gate.
7. Sync release to GitHub.
8. Smoke-check GitHub Pages.
9. Smoke-check AWS if that path changed.

## Capacity Rule
- Any newly validated source family, classification trick, or boundary exception must be written back into the research docs before the cycle is considered complete.
