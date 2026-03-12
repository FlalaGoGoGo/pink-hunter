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

## Discovery Heuristic
- Once one city works in a cycle, look for neighboring cities that share the same source family, schema, vendor, or ArcGIS org before starting a fresh open-web search.
- Prefer batches that reuse an existing boundary cache and parser shape, even if the first tree counts are smaller. Reusable throughput matters more than one-off wins.

## Pilot Rule
- Prediction work should launch as `Featured Areas` pilots, not as region-wide ML promises.
- A pilot is ready when it has:
  - reliable local tree completeness
  - a clearly highlighted viewing area
  - simple public forecast output (`start / peak / end`)
  - weather context that is separate from the canonical tree inventory
- Campus PDFs or seasonal guides can support manual QA and cultivar labeling for those pilots, but they are not the canonical training table.

## Capacity Rule
- Any newly validated source family, classification trick, or boundary exception must be written back into the research docs before the cycle is considered complete.
