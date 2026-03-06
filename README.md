# Pink Hunter

Mobile-first blooming tree map for Cherry / Plum / Peach / Magnolia / Crabapple.

## Highlights
- Coverage overlay strictly uses official city boundaries for covered cities.
- Gray coverage highlights cities whose official boundary is public but whose official public single-tree dataset is not available.
- Strict scientific-name classification (`cherry`, `plum`, `peach`, `magnolia`, `crabapple`).
- Current data coverage: Seattle, Bellevue, Redmond, Renton, Kenmore, SeaTac, Sammamish, Shoreline, Snohomish, Everett, Kirkland, Bellingham, Spokane, Yakima, Walla Walla, Puyallup, Gig Harbor, Washington DC, Vancouver BC, Victoria BC (+ UW supplemental points).
- Bilingual UI (`zh-CN`, `en-US`) with species education cards.
- Weekly refresh workflow with atomic data outputs.

## Quick Start
1. Install dependencies
   - `npm install`
2. Build data
   - `npm run etl`
3. Run app
   - `npm run dev`

## Data Outputs
- `/public/data/trees.v1.geojson`
- `/public/data/coverage.v1.geojson`
- `/public/data/species-guide.v1.json`
- `/public/data/meta.v1.json`
- `/public/data/unknown_scientific_names.v1.json`
- `/data/normalized/trees_normalized.csv`

## Classification
Classification rules are configured in:
- `config/prunus_mapping.csv` for broad 5-group mapping
- `config/blossom_subtypes.csv` for cultivar / subtype keywords shown on cards
- `match_type=prefix|exact`
- `species_group=cherry|plum|peach|magnolia|crabapple|exclude`

## Taxonomy And ETL Docs
- Taxonomy keywords and subtype methodology: `/docs/TAXONOMY_KEYWORDS.md`
- Covered-city ingestion methods: `/docs/CITY_ETL_METHODS.md`

## Weekly Refresh
GitHub Actions workflow: `.github/workflows/weekly-data-refresh.yml`
- Runs every Monday at 16:00 UTC.
- Rebuilds data with `python3 etl/build_data.py`.
- Commits changes only when output files changed.

## Art Assets
- Manifest: `/public/assets/ui/manifest.v1.json`
- Prompt guide: `/docs/AI_ASSET_PROMPTS.md`

## GitHub Pages
- Deployment workflow: `.github/workflows/deploy-pages.yml`
- Custom subdomain setup: `docs/GITHUB_PAGES_SUBDOMAIN_SETUP.md`
- Add your real subdomain in `public/CNAME` before enabling custom-domain routing.
