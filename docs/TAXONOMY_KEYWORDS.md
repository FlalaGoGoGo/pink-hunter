# Blossom Taxonomy Keywords

Last updated: 2026-03-06 (America/Los_Angeles)

## Purpose
- Keep the product's top-level taxonomy fixed at `cherry / plum / peach / magnolia / crabapple`.
- Track the finer subtype or cultivar keywords that should surface on cards as `subtype_name`.
- Reuse the same keyword list when rerunning ETL to recover ornamental rows that broad scientific-name mapping missed.

## Hard Rules
- `species_group` stays limited to the current 5 groups. Subtypes do not become new top-level filters.
- Broad classification remains scientific-name first.
- `subtype_name` may come from a curated keyword hit or a safe fallback common/scientific label, but only after the row is in-scope for the 5 groups.
- Excluded Prunus groups such as laurel, chokecherry, black cherry, bitter cherry, and other non-target lookalikes remain excluded unless product scope changes.

## Source Files
- Broad-group mapping: `config/prunus_mapping.csv`
- Subtype keyword mapping: `config/blossom_subtypes.csv`
- Missed-name review: `public/data/unknown_scientific_names.v1.json`
- Row-level normalization audit: `data/normalized/trees_normalized.csv`

## Matching Order
1. Match scientific names against `config/prunus_mapping.csv`.
2. Match curated subtype keywords against combined scientific/common text.
3. If the subtype keyword implies one of the 5 groups, use it to recover missed ornamental rows.
4. If no curated subtype keyword is found, use a safe non-generic common/scientific fallback for `subtype_name`.

## Observed Subtype Keywords By Group

### Cherry
- Core keywords: `kwanzan`, `yoshino`, `akebono`, `okame`, `higan`, `snow goose`, `accolade`, `amanogawa`, `shiro-fugen`, `snow fountain`, `spire`, `autumnalis`, `sargent`, `mazzard`, `cascade snow`
- High-signal observed labels after rerun:
  - `Kwanzan` (`5,602`)
  - `Double Chinese Cherry` (`4,292`)
  - `Yoshino` (`3,263`)
  - `Snow Goose` (`2,070`)
  - `Mazzard` (`1,573`)
  - `Okame` (`1,441`)
  - `Higan` (`1,268`)
- Recovery examples from this round:
  - `Prunus shrubs` + `Cherry, Kwanzan` -> `cherry / Kwanzan`
  - `Prunus yedoensis` + `Prunus x yedoensis` -> `cherry / Yoshino`
  - `Prunus Snow Fountains` -> `cherry / Snow Fountains`

### Plum
- Core keywords: `thundercloud`, `blireiana`, `newport`, `vesuvius`, `purpleleaf plum`, `cherry plum`, `flowering plum`, `mume`, `prunus triloba`
- High-signal observed labels after rerun:
  - `Purpleleaf Plum` (`6,014`)
  - `Thundercloud` (`3,790`)
  - `Blireiana` (`1,919`)
  - `Cherry Plum` (`1,282`)
  - `European (Fruiting) Plum` (`873`)
  - `Flowering Plum` (`583`)
- Recovery examples from this round:
  - `Prunus triloba` + `Plum, Flowering` -> `plum / Flowering Almond / Prunus triloba`
  - `Prunus cerasifera 'Thundercloud'` -> `plum / Thundercloud`

### Peach
- Core keywords: `frost peach`, `flowering peach`, `prunus persica`
- Current data reality:
  - Peach remains sparse in public inventories.
  - Most records stay at generic `Prunus persica` (`221`) rather than cultivar level.
  - `Frost Peach` is currently the only repeated cultivar-level hit (`4`).

### Magnolia
- Core keywords: `galaxy`, `little gem`, `moonglow`, `brackens brown beauty`, `ann`, `jane`, `betty`, `loebner`, `star magnolia`, `saucer magnolia`, `kobus`, `southern magnolia`, `sweetbay magnolia`
- High-signal observed labels after rerun:
  - `Southern Magnolia` (`2,723`)
  - `Sweetbay Magnolia` (`1,348`)
  - `Saucer Magnolia` (`571`)
  - `Galaxy Magnolia` (`493`)
  - `Moonglow` (`386`)
  - `Kobus Magnolia` (`357`)
  - `Little Gem Magnolia` (`354`)
  - `Star Magnolia` (`280`)
- Quality improvement examples from this round:
  - `Magnolia kobus var. stellata` + `Star Magnolia` now stays `Star Magnolia`
  - `Magnolia, Little Gem` now stays `Little Gem Magnolia`

### Crabapple
- Core keywords: `prairifire`, `royal raindrops`, `golden raindrops`, `snowdrift`, `adirondack`, `profusion`, `harvest gold`, `donald wyman`, `sugar tyme`, `coralburst`, `radiant`, `sargent crabapple`, `japanese crabapple`, `oregon crabapple`, `largeleaf crabapple`
- High-signal observed labels after rerun:
  - `Orchard (Common) Apple` (`1,330`)
  - `Malus domestica` (`382`)
  - `Golden Raindrops Crabapple` (`371`)
  - `Adirondack Crabapple` (`362`)
  - `Snowdrift Crabapple` (`350`)
  - `Prairifire Crabapple` (`326`)

## What This Round Recovered
- Included records increased from `72,082` to `72,552` (`+470`).
- Largest city gains:
  - `Sammamish +233`
  - `Seattle +174`
  - `Everett +33`
  - `Shoreline +18`
  - `Kirkland +6`
  - `Kenmore +5`
- Species gains:
  - `cherry +463`
  - `plum +5`
  - `magnolia +2`

## Update Procedure
1. Add broad scientific-name patterns to `config/prunus_mapping.csv` when a new in-scope taxon is confirmed.
2. Add subtype/cultivar keywords to `config/blossom_subtypes.csv`.
3. Run `npm run etl`.
4. Review `public/data/unknown_scientific_names.v1.json` for remaining missed in-scope names.
5. Spot-check `public/data/trees.v1.geojson` for card-ready `subtype_name` values in at least one city per affected group.
6. Update guide copy in `etl/build_data.py` if a new subtype family becomes common enough to mention publicly.
