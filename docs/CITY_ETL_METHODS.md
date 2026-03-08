# City ETL Methods

Last updated: 2026-03-07 (America/Los_Angeles)

## Purpose
- Record how each covered city is ingested so future species expansion can reuse the same pipeline.
- Make the per-city extraction method explicit before adding more blossom groups or more cities.

## Shared Rules
- Coverage polygons must use official jurisdiction boundary geometries only.
- ZIP assignment is spatial:
  - Washington state: state ZIP polygons from `ZIP_LAYER`
  - Washington DC: census ZCTA polygons from `US_CENSUS_ZCTA_LAYER`
- Non-US cities currently keep `zip_code` blank and surface as `unknown` in the UI until a stable official postal-boundary source is added.
- Unincorporated place names are tracked separately; they are not added to coverage until there is an official municipal or explicitly supported jurisdiction boundary/data path.
- Broad taxonomy is scientific-name first, then curated subtype keywords.
- Controlled common-name fallback is allowed only when the source exposes an explicitly generic genus-level scientific value (for example `Prunus sp.` / `Malus sp.` / `Magnolia sp.`).
- Output contract is stable:
  - `public/data/trees.<region>.area-index.v2.json`
  - `public/data/trees.<region>.area.<slug>.v2.geojson`
  - `public/data/trees.<region>.area.<slug>.shard-###.v2.geojson`
  - `public/data/coverage.v1.geojson`
  - `public/data/species-guide.v1.json`
  - `public/data/meta.v2.json`
  - `public/data/unknown_scientific_names.v1.json`
  - `data/normalized/trees_normalized.csv`

## Source Families

### ArcGIS REST
- Use `query_arcgis_features()` against official city or jurisdiction `FeatureServer` / `MapServer` layers.
- Pull source metadata from the layer `pjson` endpoint.
- Map raw city-specific field names into:
  - `scientific_raw`
  - `common_name`
  - `ownership_raw`
  - point geometry

### OpenDataSoft (ODS)
- Used for `Vancouver BC` and `Salinas`.
- Metadata comes from the dataset endpoint itself.
- Large filtered pulls should use the `exports/json` endpoint, not the `records` endpoint, because the City of Vancouver ODS API caps `records.limit` at `100`.
- Geometry arrives as GeoJSON-style points inside the `geom` field.
- Boundary data may be published as a legal boundary line; when that happens, the official line is converted into a polygon without manual redraw.

### Socrata / SODA
- Used for `San Francisco`, `Oakland`, and `New York City`.
- Metadata comes from the dataset view endpoint (`/api/views/...`).
- Filtered row pulls use the dataset resource endpoint with SoQL parameters such as:
  - `$where`
  - `$select`
  - `$order`
  - `$limit`
  - `$offset`
- Scientific/common names may be packed into a single text field and need source-specific splitting before taxonomy mapping.

### Downloaded Shapefile
- Used for official sources that publish a stable public shapefile or ArcGIS item download but not a clean public query layer.
- Current ETL uses:
  - `pyshp`
  - `pyproj`
- Shapefile geometry is transformed to WGS84 before taxonomy mapping and ZIP assignment.
- Official item pages or city open-data pages remain the source-of-truth links in metadata.

### TreeKeeper
- Used for `Sammamish`, `Everett`, `South San Francisco`, and `Pittsburgh`.
- Public access comes from `search.cfc` plus `grids.cfc`.
- `SITE_ATTR1` may contain either:
  - `Common (Scientific)` format
  - scientific name only
  - common label only
- Geometry can come from:
  - `LONGITUDE` / `LATITUDE`
  - JSON inside `SITE_GEOMETRY`

### TreePlotter
- Used for `Kirkland`, `Fremont`, and `Concord`.
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
| Palo Alto | ArcGIS FeatureServer | `Botanical_Name`, `Common_Name`, `JURISDICTION` | ArcGIS point geometry | Official City of Palo Alto Open GIS tree layer; city boundary comes from the city-published shapefile |
| Berkeley | Downloaded Shapefile | `SCINAME`, `COMMONNAME`, `AGENCY` | shapefile points transformed to WGS84 | Official public inventory is published as a downloadable shapefile/ArcGIS item rather than a clean query layer |
| Cupertino | ArcGIS MapServer | `BotanicalName`, `CommonName`, `OwnedBy`, `MaintainedBy` | ArcGIS point geometry | Official City of Cupertino GIS tree layer |
| Fremont | TreePlotter | `species_latin` / `species_common` integer foreign keys resolved through the public `species` lookup table | EWKB hex with `SRID=3857` -> Web Mercator -> lon/lat | Official City of Fremont public TreePlotter inventory; unlike Kirkland, the `trees` table stores species references as integer keys and the geometry is EWKB rather than plain WKB |
| Concord | TreePlotter | `species_latin` / `species_common` with public TreePlotter inventory tables | WKB point hex -> Web Mercator -> lon/lat | Official City of Concord public TreePlotter inventory exposed from the city tree-inventory page |
| Irvine | ArcGIS MapServer | `TRG_COMMON`, `CITYMAINTAINED` | ArcGIS point geometry requested in `outSR=4326` | Official City of Irvine `City Trees` layer; blossom rows are filtered server-side from the public ArcGIS landscape service |
| Milpitas | ArcGIS FeatureServer | `Species`, `Name`, `OwnedBy`, `MaintBy` | ArcGIS point geometry | Official City of Milpitas `Trees RO` service; ownership codes are decoded from field domains |
| Oakland | SODA | `scientific_name`, `common_name`, `address`, `stewardship` | `location` point from Socrata rows | Official City of Oakland street-tree dataset; ownership is normalized from city stewardship fields |
| Los Angeles | TreeKeeper | `SITE_ATTR1` parsed by `parse_species_text()` | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official StreetsLA public TreeKeeper street-tree inventory; ETL boots a guest session, submits a map search, then pages server-side blossom filters against `SITE_ATTR1` to avoid pulling the full citywide dataset |
| Salinas | OpenDataSoft | `spp`, `geo_point_2d`, `active` | lon/lat from `geo_point_2d` | Official City of Salinas `Tree Inventory` dataset; current published path uses ODS export rows with `active=1` |
| San Mateo | ArcGIS FeatureServer | `SPP`, `ACTIVE`, `OBJECTID` | ArcGIS point geometry | Official City of San Mateo `Street Trees` service; rows are filtered to `ACTIVE=1` |
| San Rafael | ArcGIS FeatureServer | `Species_Name`, `Species_Type`, `UniqueID` | ArcGIS point geometry | Official City of San Rafael `Trees` service; common-name-heavy source, so classification relies on controlled common-name fallback |
| Everett | TreeKeeper | `SITE_ATTR1` parsed by `parse_sammamish_species()` | direct lon/lat or `SITE_GEOMETRY` JSON | Park-tree public endpoint |
| South San Francisco | TreeKeeper | `SITE_ATTR1` parsed by `parse_species_text()` plus ownership from `SITE_ATTR23` | direct lon/lat or `SITE_GEOMETRY` JSON | Official city-linked TreeKeeper inventory published from the city trees page |
| San Diego | ArcGIS MapServer | `COMMON_NAME` with fallback to `SPECIES_NAME` | ArcGIS point geometry requested in `outSR=4326` | Official City of San Diego `Trees (Street Trees)` layer; blossom rows are filtered server-side with `COMMON_NAME` before local taxonomy classification |
| New York City | SODA | `spc_latin`, `spc_common`, `zipcode`, `status` | lat/lon columns in dataset rows | Official NYC Parks street-tree census dataset; rows are restricted to `status = Alive` before blossom classification |
| Philadelphia | ArcGIS FeatureServer | `tree_name` parsed by `parse_dash_species()` | ArcGIS point geometry | Official Philadelphia Parks & Recreation tree inventory layer; botanical/common names are packed into one uppercase text field |
| Pittsburgh | TreeKeeper | `SITE_ATTR6` parsed by `parse_species_text()` | direct lon/lat or `SITE_GEOMETRY` JSON | Official public Pittsburgh TreeKeeper inventory domain; no public ownership field is published, so ownership is normalized to public |
| Cambridge | Downloaded Shapefile | `Scientific`, `CommonName`, `Cultivar`, `SiteType` | shapefile points transformed to WGS84 | Official City of Cambridge street-tree shapefile; only current `SiteType = Tree` rows are published into the product |
| Boston | Downloaded GeoJSON | `spp_bot`, `spp_com` | GeoJSON lon/lat coordinates from Analyze Boston | Official Analyze Boston `BPRD Trees` download; includes both street and park trees, so ownership is normalized to public city inventory |
| Ottawa | ArcGIS MapServer | common-name classification from `SPECIES`, ownership from `OWNERSHIP` | ArcGIS point geometry already requested in `outSR=4326` | Official City of Ottawa tree layer is large, so ETL filters blossom-like common names (`cherry`, `plum`, `peach`, `magnolia`, `crabapple`, `apple`) server-side before classification |
| Toronto | Downloaded CSV | `COMMON_NAME` from the official alternate WGS84 CSV | point geometry parsed from serialized `geometry` text | Official Toronto Open Data CSV is very large; ETL uses the smaller alternate CSV export and classifies by controlled common-name fallback rather than requiring botanical names |
| Montreal | Downloaded CSV | `Essence_latin`, `Essence_ang`, `Essence_fr` | direct `Longitude` / `Latitude` columns | Official Ville de Montréal tree CSV; boundary is assembled by merging arrondissement polygons from the official administrative-limits dataset |
| Austin | SODA | `species`, `longtitude`, `latitude` with GeoJSON `geometry` fallback | numeric lon/lat when valid; otherwise point from the row `geometry` object | Official City of Austin `Tree Inventory` dataset; some blossom rows expose projected numeric coordinates, so ETL validates WGS84 ranges and falls back to the GeoJSON point when necessary |
| Dallas | TreeKeeper | `SITE_ATTR1` parsed by `parse_species_text()` | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Dallas public TreeKeeper inventory linked from the city forestry page |
| Denver | ArcGIS FeatureServer | `SPECIES_BOTANIC`, `SPECIES_COMMON` | ArcGIS point geometry requested in `outSR=4326`, with `X_LONG` / `Y_LAT` fallback | Official City and County of Denver public tree inventory service; blossom rows are filtered server-side against the public common/botanical species fields |
| Las Vegas | ArcGIS FeatureServer | `SPP_COM`, `SPP_BOT` | ArcGIS point geometry requested in `outSR=4326`, with `LONGITUDE` / `LATITUDE` fallback | Official City of Las Vegas `CLV Tree Sites` layer; blossom rows are filtered server-side against the public common/botanical species fields |
| Salt Lake City | ArcGIS FeatureServer | `SPP` botanical species name, `Vacant` vacancy flag | ArcGIS point geometry requested in `outSR=4326` | Official Salt Lake City Public Lands `Urban Forestry Inventory`; ETL excludes vacant planting sites before blossom classification |
| New Westminster | ArcGIS FeatureServer | `FULL_NAME` as scientific display name, cultivar fallback from `CULTIVAR`, ownership from `OWNEDBY` / `MAINTBY` | ArcGIS point geometry requested in `outSR=4326` | Official City of New Westminster `Tree Inventory (Active Trees)` layer; official jurisdiction boundary comes from the Metro Vancouver administrative boundary service (`FullName = 'City of New Westminster'`) |
| Arlington | ArcGIS FeatureServer | `CommonName`, `CultivarVariety`, `Ownership`, `Jurisdiction` | ArcGIS point geometry | Official Arlington County `DPR Trees` layer; classification relies on controlled common-name fallback because no public scientific-name field is exposed |
| Baltimore | ArcGIS MapServer | `SPP`, `CULTIVAR` | ArcGIS point geometry | Official Baltimore city forestry tree layer on `gis.baltimorecity.gov`; `SPP` already carries botanical names for blossom filtering |
| Jersey City | ArcGIS FeatureServer | `species` parsed by `parse_species_text()`, optional cultivar from `species_1_` | ArcGIS point geometry | Public Jersey City tree inventory service referenced by the city's Urban Forests materials; ownership is normalized to public city inventory |
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
   - area counts in `public/data/meta.v2.json`
   - missed names in `public/data/unknown_scientific_names.v1.json`
   - card fields in the relevant published `public/data/trees.<region>.area.*.v2.geojson`

## How To Add More Cities Later
1. Verify the city has an official public single-tree dataset with point geometry.
2. Identify the source family:
   - ArcGIS REST
   - TreeKeeper
   - TreePlotter
   - another public source with stable API
3. Add parsing logic to `etl/build_data.py`.
4. Add official jurisdiction-boundary mapping if the city name needs explicit disambiguation or if the source is county-equivalent.
5. If the source family is ODS, test both `records` and `exports/json`; some portals impose a hard `records.limit` cap.
6. Rerun ETL and update `docs/CITY_COVERAGE_TRACKER.md`.
7. Do not add coverage polygons for a city unless the official boundary geometry is resolved.

## Incremental Publish Fallback
- Full `npm run etl` remains the canonical path.
- `npm run etl` now chains the stable targeted-publish refresh for `Arlington`, `Austin`, `Baltimore`, `Boston`, `Dallas`, `Jersey City`, `Las Vegas`, `Milpitas`, `Salt Lake City`, `San Mateo`, `San Rafael`, `Salinas`, `Fremont`, `Concord`, `South San Francisco`, `New York City`, `Philadelphia`, `Pittsburgh`, and `Cambridge` after the full ETL, so those published area/shard files are regenerated as part of the normal publish path.
- When upstream sources are too slow and the already-published local region files are still current, refresh area-shard outputs without rerunning the full ETL:
  - `python3 scripts/refresh_region_area_shards.py --data-dir public/data --region all`
- When a new city source has been validated but is not yet folded into the main full ETL path, publish it incrementally with:
  - `python3 scripts/publish_targeted_city_updates.py --city <City Name>`
- If gray-coverage rules or official-boundary hints changed without rebuilding all tree rows, refresh coverage and meta bounds with:
  - `python3 scripts/refresh_coverage_metadata.py --data-dir public/data`
- After that, rerun `python3 scripts/check_region_data_sizes.py --data-dir public/data` so `meta.v2.json` and area-shard artifacts stay internally consistent.
