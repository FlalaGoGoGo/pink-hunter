# City ETL Methods

Last updated: 2026-03-06 (America/Los_Angeles)

## Purpose
- Record how each covered city is ingested so future species expansion can reuse the same pipeline.
- Make the per-city extraction method explicit before adding more blossom groups or more cities.

## Shared Rules
- Coverage polygons must use official city boundary geometries only.
- ZIP assignment is spatial:
  - Washington state: state ZIP polygons from `ZIP_LAYER`
  - Washington DC: census ZCTA polygons from `US_CENSUS_ZCTA_LAYER`
- Non-US cities currently keep `zip_code` blank and surface as `unknown` in the UI until a stable official postal-boundary source is added.
- Unincorporated place names are tracked separately; they are not added to coverage until there is an official municipal or explicitly supported jurisdiction boundary/data path.
- Broad taxonomy is scientific-name first, then curated subtype keywords.
- Controlled common-name fallback is allowed only when the source exposes an explicitly generic genus-level scientific value (for example `Prunus sp.` / `Malus sp.` / `Magnolia sp.`).
- Output contract is stable:
  - `public/data/trees.v1.geojson`
  - `public/data/coverage.v1.geojson`
  - `public/data/species-guide.v1.json`
  - `public/data/meta.v1.json`
  - `public/data/unknown_scientific_names.v1.json`
  - `data/normalized/trees_normalized.csv`

## Source Families

### ArcGIS REST
- Use `query_arcgis_features()` against official city `FeatureServer` or `MapServer` layers.
- Pull source metadata from the layer `pjson` endpoint.
- Map raw city-specific field names into:
  - `scientific_raw`
  - `common_name`
  - `ownership_raw`
  - point geometry

### OpenDataSoft (ODS)
- Used for `Vancouver BC`.
- Metadata comes from the dataset endpoint itself.
- Large filtered pulls should use the `exports/json` endpoint, not the `records` endpoint, because the City of Vancouver ODS API caps `records.limit` at `100`.
- Geometry arrives as GeoJSON-style points inside the `geom` field.
- Boundary data may be published as a legal boundary line; when that happens, the official line is converted into a polygon without manual redraw.

### Socrata / SODA
- Used for `San Francisco`.
- Metadata comes from the dataset view endpoint (`/api/views/...`).
- Filtered row pulls use the dataset resource endpoint with SoQL parameters such as:
  - `$where`
  - `$select`
  - `$order`
  - `$limit`
  - `$offset`
- Scientific/common names may be packed into a single text field and need source-specific splitting before taxonomy mapping.

### TreeKeeper
- Used for `Sammamish` and `Everett`.
- Public access comes from `search.cfc` plus `grids.cfc`.
- `SITE_ATTR1` may contain either:
  - `Common (Scientific)` format
  - scientific name only
  - common label only
- Geometry can come from:
  - `LONGITUDE` / `LATITUDE`
  - JSON inside `SITE_GEOMETRY`

### TreePlotter
- Used for `Kirkland`.
- Requires public session bootstrap at `https://pg-cloud.com/KirklandWA/`.
- Data retrieval goes through `retrieveDataAlias` on `db.php`.
- Geometry is WKB point hex in Web Mercator and must be decoded then converted to lon/lat.
- Scientific names may be abbreviated and need genus expansion from common-name hints.

### OSM Supplemental
- Used only for supplemental UW cherry points inside Seattle.
- Source file is cached at `data/supplemental/uw_prunus_overpass.json`.
- Tags of interest:
  - `species`
  - `genus`
  - `species:en`
  - `genus:en`

## Integrated Cities And Extraction Notes
| City | Source family | Key fields / parser | Geometry handling | Notes |
|---|---|---|---|---|
| Seattle | ArcGIS FeatureServer | `SCIENTIFIC_NAME`, `COMMON_NAME`, `OWNERSHIP` | ArcGIS point geometry | Also merges UW supplemental points |
| Bellevue | ArcGIS FeatureServer | `SpeciesDesc` parsed by `parse_bellevue_species()` | ArcGIS point geometry | Scientific/common are packed into one text field |
| Redmond | ArcGIS FeatureServer | `GenusSpecies`, `CommonName` | ArcGIS point geometry | Ownership normalized from `d_Ownership` |
| Renton | ArcGIS MapServer | `GENUS` + `SPECIES`, `COMMONNAME` | ArcGIS point geometry | Has cached fallback when live source is unavailable |
| Kenmore | ArcGIS FeatureServer | `SciName`, `CommonName` | ArcGIS point geometry | Public tree inventory |
| SeaTac | ArcGIS FeatureServer | `GenusType` + `SpeciesType`, `CommonName` | ArcGIS point geometry | Scientific name reconstructed from split fields |
| Puyallup | ArcGIS FeatureServer | `SCIENTIFIC`, `COMMON_NAM` | ArcGIS point geometry | City-maintained street trees only |
| Gig Harbor | ArcGIS FeatureServer | `Latin_Name` | ArcGIS point geometry | No public common-name field |
| Sammamish | TreeKeeper | `SITE_ATTR1` parsed by `parse_sammamish_species()` | direct lon/lat or `SITE_GEOMETRY` JSON | Street and park sites are loaded separately then merged |
| Shoreline | ArcGIS MapServer | `Scientific_Nm`, `Common_Nm`, `Jurisdiction` | ArcGIS point geometry | Public tree inventory layer |
| Snohomish | ArcGIS FeatureServer | `BotanicalN`, `CommonName`, `ROW`, `Location_L` | ArcGIS point geometry | Official city urban-forestry inventory; included blossom rows are all tagged `ROW = Yes` |
| Bellingham | ArcGIS MapServer | `ScientificName`, `CommonName`, `Ownership` | ArcGIS point geometry | Official `maps.cob.org` tree layer |
| Spokane | ArcGIS FeatureServer | `Genus`, `CommonName`, `species` | ArcGIS point geometry | Source is genus-level; ETL converts genus into generic scientific placeholders before controlled common-name fallback |
| Yakima | ArcGIS MapServer | `NAME`, `GENUS`, `SPECIES`, `OWNEDBY`, `MAINTBY` | ArcGIS point geometry | Common-name-only blossom rows are promoted to generic scientific placeholders when `NAME` strongly indicates a target blossom group; ownership codes are decoded from official field domains |
| Walla Walla | ArcGIS MapServer | `Botanical`, `Common`, `Property` | ArcGIS point geometry | Official city tree viewer layer; botanical/common fields are both public and queryable |
| Vancouver BC | OpenDataSoft | `genus_name`, `species_name`, `common_name`, `cultivar_name` | point geometry inside ODS `geom` field | Uses official `public-trees` dataset; filtered pulls use ODS export endpoint because records API page size is capped |
| Victoria BC | ArcGIS MapServer | `BotanicalName`, `CommonName`, `Species`, `TreeCategory`, `Parks` | ArcGIS point geometry | Official parks-tree species layer only; `Surveyed Trees` reviewed separately but excluded because it lacks species fields |
| San Jose | ArcGIS MapServer | `NAMESCIENTIFIC`, `OWNEDBY`, `MAINTBY` | ArcGIS point geometry | Official `Street Tree` city layer; public scientific-name field is clean enough for direct taxonomy mapping |
| San Francisco | SODA | `qspecies` parsed by `parse_san_francisco_species()`, `qcaretaker`, `qlegalstatus` | lat/lon columns in dataset rows | Official San Francisco Public Works open-data table; scientific/common are packed into one field |
| Burlingame | ArcGIS FeatureServer | `BotanicalName`, `CommonName`, `Tree_ID` | ArcGIS point geometry | Public city-linked guest inventory hosted on a contractor ArcGIS org; accepted because the official City of Burlingame trees page explicitly publishes the inventory link |
| Everett | TreeKeeper | `SITE_ATTR1` parsed by `parse_sammamish_species()` | direct lon/lat or `SITE_GEOMETRY` JSON | Park-tree public endpoint |
| Kirkland | TreePlotter | `species_bo`, `species_la` with `expand_abbreviated_botanical_name()` | WKB hex -> Web Mercator -> lon/lat | Public TreePlotter session/API |
| Washington DC | ArcGIS MapServer | `SCI_NM`, `CMMN_NM`, `OWNERSHIP` | ArcGIS point geometry | DDOT Urban Tree Canopy layer |

## Universal Classification Pipeline
1. Normalize scientific text with `normalize_scientific_name()`.
2. If a source is genus-only but official and public (current example: Spokane), convert `Genus` into a generic scientific placeholder such as `Prunus sp.` before classification.
3. Classify into one of the 5 product groups with `config/prunus_mapping.csv`.
4. Recover missed ornamentals and derive card-ready detail labels with `config/blossom_subtypes.csv`.
5. Canonicalize ownership into `public / private / unknown`.
6. Assign ZIP by point-in-polygon lookup.
7. Emit:
   - GeoJSON feature for included rows
   - normalized CSV row for every fetched record
   - unknown-scientific counter entry for excluded rows with meaningful scientific text

## How To Add More Species Later
1. Decide whether the new taxon belongs inside an existing top-level group or needs a new product group.
2. If it belongs to an existing group:
   - add scientific patterns to `config/prunus_mapping.csv`
   - add subtype keywords to `config/blossom_subtypes.csv`
   - update guide copy in `etl/build_data.py`
3. If it needs a new top-level group:
   - extend frontend types in `src/types.ts`
   - extend labels in `src/i18n.ts`
   - extend map colors / filters / cards in `src/App.tsx`
   - extend both ETL config files
4. Run `npm run etl`.
5. Validate:
   - city counts in `public/data/meta.v1.json`
   - missed names in `public/data/unknown_scientific_names.v1.json`
   - card fields in `public/data/trees.v1.geojson`

## How To Add More Cities Later
1. Verify the city has an official public single-tree dataset with point geometry.
2. Identify the source family:
   - ArcGIS REST
   - TreeKeeper
   - TreePlotter
   - another public source with stable API
3. Add parsing logic to `etl/build_data.py`.
4. Add official city-boundary mapping if the city name needs explicit disambiguation.
5. If the source family is ODS, test both `records` and `exports/json`; some portals impose a hard `records.limit` cap.
6. Rerun ETL and update `docs/CITY_COVERAGE_TRACKER.md`.
7. Do not add coverage polygons for a city unless the official boundary geometry is resolved.
