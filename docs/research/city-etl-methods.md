# City ETL Methods

Last updated: 2026-03-28 (America/Los_Angeles)

## Purpose
- Record how each covered city is ingested so future species expansion can reuse the same pipeline.
- Make the per-city extraction method explicit before adding more blossom groups or more cities.

## Shared Rules
- Coverage polygons must use official jurisdiction boundary geometries only.
- Before starting city work, review `docs/research/city-coverage-tracker.md` and identify the city bucket first:
  - `A2`: ready to publish
  - `B`: official point-tree source exists but still blocked
  - `C`: no verified usable official point-tree source yet
- ZIP assignment is spatial:
  - Washington state: state ZIP polygons from `ZIP_LAYER`
  - Washington DC: census ZCTA polygons from `US_CENSUS_ZCTA_LAYER`
- Non-US cities currently keep `zip_code` blank and surface as `unknown` in the UI until a stable official postal-boundary source is added.
- Unincorporated place names are tracked separately; they are not added to coverage until there is an official municipal or explicitly supported jurisdiction boundary/data path.
- Broad taxonomy is scientific-name first, then curated subtype keywords.
- Controlled common-name fallback is allowed when the source exposes either an explicitly generic genus-level scientific value (for example `Prunus sp.` / `Malus sp.` / `Magnolia sp.`) or a strong official blossom common-name label without a cleaner public scientific field.
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

### Downloaded GeoJSON
- Used for official sources that publish a stable GeoJSON or JSON export but not a clean public query API.
- Metadata comes from the official dataset portal page rather than a live REST schema endpoint.
- Geometry is read directly from the published GeoJSON point coordinates, which are already in WGS84.
- Boundary clipping still uses the official jurisdiction geometry before publish.

### Socrata / SODA
- Used for `San Francisco`, `Oakland`, `New York City`, `Norfolk`, and `Providence`.
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

### ArcGIS Web Map featureCollection
- Used for `Garrett Park`.
- Fetch the published web map item JSON from ArcGIS sharing endpoints, then extract features from the embedded `featureCollection`.
- Prefer explicit lon/lat attribute fields when the embedded point geometry is still stored in Web Mercator.

### OSM Supplemental
- Used only for supplemental UW cherry points inside Seattle.
- Source file is cached at `data/supplemental/uw_prunus_overpass.json`.
- Tags of interest:
  - `species`
  - `genus`
  - `species:en`
  - `genus:en`

## Discovery And Recovery Tactics
- Promotion path is explicit: `C -> B -> A2 -> A1`.
- When a source family lands, search for the next cities in this order:
  1. sibling services inside the same ArcGIS org or contractor org
  2. neighboring public sites on the same TreeKeeper or TreePlotter tenancy
  3. shared county or metro layers that expose multiple `City` or `Jurisdiction` values
  4. only then broader web search
- Shared layers are often the fastest expansion path. Query distinct city-like field values first; one stable layer can unlock several municipalities with only boundary and mapping updates.
- If a city appears in `data/normalized/trees_normalized.csv` but not in the published area index, assume a classification or publish-refresh issue before assuming the fetcher is broken.
- PDF maps, campus guides, and visitor handouts are QA overlays and labeling aids. Do not treat them as direct production rows unless they expose stable structured per-tree data.
- Supplemental sources such as UW OSM points stay explicitly scoped and labeled. They augment an official city source; they do not replace the canonical inventory.

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
| Annapolis | TreePlotter | `species_latin` / `species_common` with public TreePlotter inventory tables | WKB point hex -> Web Mercator -> lon/lat | Official City of Annapolis public TreePlotter inventory; rows are clipped to the official jurisdiction boundary before publish |
| Fairfax | TreePlotter | `species_latin` / `species_common` with public TreePlotter inventory tables | WKB point hex -> Web Mercator -> lon/lat | Official City of Fairfax public TreePlotter inventory; rows are clipped to the official jurisdiction boundary before publish |
| Saratoga Springs | TreePlotter | `species_latin` / `species_common` with public TreePlotter inventory tables | WKB point hex -> Web Mercator -> lon/lat | Official City of Saratoga Springs public TreePlotter inventory; rows are clipped to the official jurisdiction boundary before publish |
| Troy | TreePlotter | `species_latin` / `species_common` with public TreePlotter inventory tables | WKB point hex -> Web Mercator -> lon/lat | Official City of Troy public TreePlotter inventory; rows are clipped to the official jurisdiction boundary before publish |
| West Hartford | TreePlotter | `species_latin` / `species_common` with public TreePlotter inventory tables | WKB point hex -> Web Mercator -> lon/lat | Official Town of West Hartford public TreePlotter inventory; rows are clipped to the official jurisdiction boundary before publish |
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
| Albany | TreeKeeper | `SITE_ATTR1` parsed by `parse_species_text()` | direct lon/lat or `SITE_GEOMETRY` JSON | Official City of Albany public TreeKeeper inventory |
| Belmont | TreeKeeper | `SITE_ATTR1` parsed by `parse_species_text()` | direct lon/lat or `SITE_GEOMETRY` JSON | Official Town of Belmont public TreeKeeper inventory |
| Cambridge (MA) | Downloaded Shapefile | `Scientific`, `CommonName`, `Cultivar`, `SiteType` | shapefile points transformed to WGS84 | Official City of Cambridge street-tree shapefile; only current `SiteType = Tree` rows are published into the product |
| Brookline | ArcGIS FeatureServer | `ScientificName`, `CommonName` | ArcGIS point geometry | Official Town of Brookline public tree inventory ArcGIS layer |
| Dedham | ArcGIS MapServer | `Species_bot`, `Species_com` | ArcGIS point geometry | Official Town of Dedham public tree inventory; blossom rows are filtered server-side against the public botanical/common fields |
| Longmeadow | ArcGIS FeatureServer | `Genus` + `Species`, `Tree_Type` | ArcGIS point geometry | Official Town of Longmeadow public tree inventory ArcGIS layer |
| Lynn | ArcGIS FeatureServer | `LATIN`, `COMMON`, `STATUS` | ArcGIS point geometry with `X` / `Y` fallback | Official City of Lynn public tree inventory; rows are restricted to `STATUS = 'alive'` before blossom classification |
| Medford | ArcGIS FeatureServer | `SPP_bot`, `SPP_com` | ArcGIS point geometry | Public Medford tree inventory ArcGIS layer referenced by the official City of Medford Forestry page / urban-forest plan materials |
| New Bedford | ArcGIS FeatureServer | `ScientName`, `CommonName` | ArcGIS point geometry with `Longitude` / `Latitude` fallback | Public 2023 New Bedford Bartlett tree inventory ArcGIS layer |
| Newton | TreeKeeper | `SITE_ATTR1` parsed by `parse_species_text()` | direct lon/lat or `SITE_GEOMETRY` JSON | Official City of Newton public TreeKeeper inventory |
| Somerville | TreeKeeper | `SITE_ATTR1` parsed by `parse_species_text()` | direct lon/lat or `SITE_GEOMETRY` JSON | Official City of Somerville public TreeKeeper inventory |
| Worcester | TreeKeeper | `SITE_ATTR1` parsed by `parse_species_text()` | direct lon/lat or `SITE_GEOMETRY` JSON | Official City of Worcester public TreeKeeper inventory |
| Groton | ArcGIS FeatureServer | `Genus` + `Species`, `CommonName` | ArcGIS point geometry with `Longitude` / `Latitude` fallback | Official Town of Groton public tree inventory; the official town boundary is resolved from the Census county subdivision rather than the smaller Groton city place |
| Gaithersburg | ArcGIS FeatureServer | `Botanical_Name`, `Common_Name` | ArcGIS point geometry | Official City of Gaithersburg `Street Trees View`; the public layer includes street trees plus a small number of park trees |
| Garrett Park | ArcGIS Web Map featureCollection | `Latin_Name`, `Common_Name`, `Longitude`, `Latitude` | direct lon/lat from published attribute fields | Official Town of Garrett Park tree inventory is published as an ArcGIS web map featureCollection; ETL ignores the embedded Web Mercator point geometry and uses the explicit `Longitude` / `Latitude` attributes instead |
| Manchester | ArcGIS FeatureServer | `species`, `species_other` | ArcGIS point geometry | Official City of Manchester public Parks and Recreation tree inventory; the public layer is mostly common-name text, so classification relies on controlled common-name fallback |
| Morristown | ArcGIS FeatureServer | `GENUS` + `SPECIES` | ArcGIS point geometry | Official Morristown public tree inventory layer |
| Charlottesville | ArcGIS MapServer | `Genus` + `Species`, `Common_Name`, `Agency` | ArcGIS point geometry | Official City of Charlottesville open-data tree inventory |
| Fredericksburg | ArcGIS FeatureServer | `genus` + `species`, `commonname`, `spacestatus` | ArcGIS point geometry | Official City of Fredericksburg public tree inventory; rows are restricted to `spacestatus = 'Planted'` before blossom classification |
| Richmond | ArcGIS FeatureServer | `SPP`, `Status` | ArcGIS point geometry | Official City of Richmond, Virginia public tree inventory; rows are restricted to `Status = In Service` and filtered server-side on `SPP` |
| Norfolk | SODA | `genus`, `species`, `common_name` | numeric `longitude` / `latitude` with `latitude_longitude_point` fallback | Official City of Norfolk `City Tree Inventory` dataset |
| Newport News | ArcGIS FeatureServer | `genus` + `species`, `commonname` | ArcGIS point geometry | Official City of Newport News public reviewed-tree inventory; the public layer only exposes reviewed trees |
| Virginia Beach | ArcGIS MapServer | `ScientificName`, `CommonName`, `Status` | ArcGIS point geometry with `Latitude` / `Longitude` fallback | Official City of Virginia Beach `VBTrees` service; rows are restricted to `Status in ('Existing', 'Planted')` before blossom classification |
| Meadville | ArcGIS FeatureServer | `GENUS` + `SPECIES`, `NAME`, `Tree_Status` | ArcGIS point geometry | Official City of Meadville public tree inventory; rows are restricted to `Tree_Status = 'Live'` before blossom classification |
| Durham | ArcGIS FeatureServer | `genus` + `species`, `commonname`, `present` | ArcGIS point geometry | Official City of Durham `Trees & Planting Sites`; rows are restricted to `present = 'Tree'` before blossom classification |
| Providence | SODA | `spp`, `the_geom` | GeoJSON point coordinates from `the_geom` | Official City of Providence `Providence Tree Dataset`; ETL synthesizes stable row ids from address/species/coordinates because the public export does not expose a single durable primary key |
| Shelburne | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official Vermont ANR `Municipal Tree Inventory` rows filtered to `TOWN = 'SHELBURNE'` and clipped to the official jurisdiction boundary |
| Middlebury | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official Vermont ANR `Municipal Tree Inventory` rows filtered to `TOWN = 'MIDDLEBURY'` and clipped to the official jurisdiction boundary |
| Winooski | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official Vermont ANR `Municipal Tree Inventory` rows filtered to `TOWN = 'WINOOSKI'` and clipped to the official jurisdiction boundary |
| Northfield | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official Vermont ANR `Municipal Tree Inventory` rows filtered to `TOWN = 'NORTHFIELD'` and clipped to the official jurisdiction boundary |
| Milton | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official Vermont ANR `Municipal Tree Inventory` rows filtered to `TOWN = 'MILTON'` and clipped to the official jurisdiction boundary |
| Hinesburg | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official Vermont ANR `Municipal Tree Inventory` rows filtered to `TOWN = 'HINESBURG'` and clipped to the official jurisdiction boundary |
| Essex | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official Vermont ANR `Municipal Tree Inventory` rows filtered to `TOWN = 'ESSEX'` and clipped to the official jurisdiction boundary |
| South Burlington | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official Vermont ANR `Municipal Tree Inventory` rows filtered to `TOWN = 'SOUTH BURLINGTON'` and clipped to the official jurisdiction boundary |
| Colchester | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official Vermont ANR `Municipal Tree Inventory` rows filtered to `TOWN = 'COLCHESTER'` and clipped to the official jurisdiction boundary |
| Randolph | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official Vermont ANR `Municipal Tree Inventory` rows filtered to `TOWN = 'RANDOLPH'` and clipped to the official jurisdiction boundary |
| Boston | Downloaded GeoJSON | `spp_bot`, `spp_com` | GeoJSON lon/lat coordinates from Analyze Boston | Official Analyze Boston `BPRD Trees` download; includes both street and park trees, so ownership is normalized to public city inventory |
| Brampton | ArcGIS MapServer | `TREE_TYPE`, `SERVICE_STATUS`, `OWNERSHIP` | ArcGIS point geometry | Official City of Brampton public tree inventory ArcGIS layer; rows are restricted to city-owned live-tree rows before blossom classification |
| Burlington | ArcGIS MapServer | `SPECIES_COMMONNAME`, `STATUS` | ArcGIS point geometry | Official City of Burlington `City Owned Trees` layer; rows are restricted to `STATUS = 'Alive'` before blossom classification |
| Cambridge ON | ArcGIS MapServer | `BOTANICAL_NAME`, `COMMON_NAME`, `STATUS` | ArcGIS point geometry | Official City of Cambridge, Ontario `Street Trees` open-data layer; rows are restricted to `STATUS = 'EXISTING'` before blossom classification |
| Cobourg | ArcGIS FeatureServer | `Botanical`, `Common` | ArcGIS point geometry | Official Town of Cobourg virtual arboretum tree inventory; classification relies on the published botanical/common fields and official Statistics Canada CSD clipping |
| Cornwall | ArcGIS FeatureServer | `SPECIES`, `Status` | ArcGIS point geometry | Official City of Cornwall public tree inventory ArcGIS layer; rows are restricted to `Status = 'PRESENT'` before blossom classification |
| Guelph | ArcGIS FeatureServer | `SPECIES` | ArcGIS point geometry | Official City of Guelph public tree inventory ArcGIS layer; classification relies on common-name blossom filtering because the public layer does not expose a cleaner scientific field |
| Halton Hills | ArcGIS MapServer | `A_Make`, `A_Component`, `LC_Status` | ArcGIS point geometry | Official Town of Halton Hills public tree layer; ETL maps the published ArcGIS field aliases back to scientific/common names and restricts rows to `LC_Status = 'In Service'` before blossom classification |
| Mississauga | ArcGIS FeatureServer | `BOTDESC`, `SERVSTAT`, `OWN` | ArcGIS point geometry with `LONGITUDE` / `LATITUDE` fallback | Official City of Mississauga `City Owned Tree Inventory`; rows are restricted to the official city-maintained statuses, and classification relies on controlled common-name fallback because the public `BOTNAME` field is an internal species code |
| Hamilton | ArcGIS FeatureServer | `SPECIES_SCIENTIFIC`, `SPECIES_COMMON`, `STATUS` | ArcGIS point geometry | Official City of Hamilton `Public Tree Inventory`; rows are restricted to `STATUS = 'Existing'` before blossom classification |
| Kitchener | ArcGIS FeatureServer | `SPECIES_LATIN`, `SPECIES_NAME`, `STATUS` | ArcGIS point geometry | Official City of Kitchener tree inventory ArcGIS layer; rows are restricted to `STATUS = 'ACTIVE'` before blossom classification |
| London | ArcGIS MapServer | `Botanical`, `CommonName` | ArcGIS point geometry | Official City of London `Status Active` tree inventory sublayer; blossom rows are filtered server-side against the published botanical/common fields |
| Oakville | ArcGIS MapServer | `SPECIES` parsed by `parse_dash_species()`, `STATUS` | ArcGIS point geometry | Official Town of Oakville forestry ArcGIS layer; the public `SPECIES` field packs common and scientific text together, so ETL parses the dash-delimited value and restricts rows to `STATUS = 'EXISTING'` |
| Orangeville | ArcGIS FeatureServer | `SPCIES`, `Removed` | ArcGIS point geometry | Official Town of Orangeville public street-tree inventory ArcGIS layer; removed rows are excluded before blossom classification |
| Ottawa | ArcGIS MapServer | common-name classification from `SPECIES`, ownership from `OWNERSHIP` | ArcGIS point geometry already requested in `outSR=4326` | Official City of Ottawa tree layer is large, so ETL filters blossom-like common names (`cherry`, `plum`, `peach`, `magnolia`, `crabapple`, `apple`) server-side before classification |
| Peterborough | ArcGIS MapServer | `BOTANICAL`, `COMMON`, `STATUS`, `OWNERSHIP` | ArcGIS point geometry | Official City of Peterborough tree inventory app layer; rows are restricted to `STATUS = 'Active'` and `OWNERSHIP = 'City'` before blossom classification |
| Tecumseh | ArcGIS MapServer | `SPECIES_BO`, `SPECIES_CO`, `ACTIVE`, `OWNERSHIP` | ArcGIS point geometry | Official Town of Tecumseh `Trees Municipal` layer; rows are restricted to active non-`Boundary` trees before blossom classification |
| Toronto | Downloaded CSV | `COMMON_NAME` from the official alternate WGS84 CSV | point geometry parsed from serialized `geometry` text | Official Toronto Open Data CSV is very large; ETL uses the smaller alternate CSV export and classifies by controlled common-name fallback rather than requiring botanical names |
| Vaughan | ArcGIS MapServer | `SPECIES`, `COMMONNAME`, `MUNICIPALITY`, `STATUS` | ArcGIS point geometry | Official York Region `Street Trees` layer; rows are restricted to active `MUNICIPALITY = 'Vaughan'` records before official Statistics Canada CSD clipping |
| Aurora | ArcGIS MapServer | `SPECIES`, `COMMONNAME`, `MUNICIPALITY`, `STATUS` | ArcGIS point geometry | Official York Region `Street Trees` layer; rows are restricted to active `MUNICIPALITY = 'Aurora'` records before official Statistics Canada CSD clipping |
| East Gwillimbury | ArcGIS MapServer | `SPECIES`, `COMMONNAME`, `MUNICIPALITY`, `STATUS` | ArcGIS point geometry | Official York Region `Street Trees` layer; rows are restricted to active `MUNICIPALITY = 'East Gwillimbury'` records before official Statistics Canada CSD clipping |
| Georgina | ArcGIS MapServer | `SPECIES`, `COMMONNAME`, `MUNICIPALITY`, `STATUS` | ArcGIS point geometry | Official York Region `Street Trees` layer; rows are restricted to active `MUNICIPALITY = 'Georgina'` records before official Statistics Canada CSD clipping |
| King | ArcGIS MapServer | `SPECIES`, `COMMONNAME`, `MUNICIPALITY`, `STATUS` | ArcGIS point geometry | Official York Region `Street Trees` layer; rows are restricted to active `MUNICIPALITY = 'King'` records before official Statistics Canada CSD clipping |
| Markham | ArcGIS MapServer | `SPECIES`, `COMMONNAME`, `MUNICIPALITY`, `STATUS` | ArcGIS point geometry | Official York Region `Street Trees` layer; rows are restricted to active `MUNICIPALITY = 'Markham'` records before official Statistics Canada CSD clipping |
| Newmarket | ArcGIS MapServer | `SPECIES`, `COMMONNAME`, `MUNICIPALITY`, `STATUS` | ArcGIS point geometry | Official York Region `Street Trees` layer; rows are restricted to active `MUNICIPALITY = 'Newmarket'` records before official Statistics Canada CSD clipping |
| Richmond Hill | ArcGIS MapServer | `SPECIES`, `COMMONNAME`, `MUNICIPALITY`, `STATUS` | ArcGIS point geometry | Official York Region `Street Trees` layer; rows are restricted to active `MUNICIPALITY = 'Richmond Hill'` records before official Statistics Canada CSD clipping |
| Whitchurch-Stouffville | ArcGIS MapServer | `SPECIES`, `COMMONNAME`, `MUNICIPALITY`, `STATUS` | ArcGIS point geometry | Official York Region `Street Trees` layer; rows are restricted to active `MUNICIPALITY = 'Whitchurch-Stouffville'` records before official Statistics Canada CSD clipping |
| Waterloo | ArcGIS FeatureServer | `LATIN_NAME`, `COM_NAME`, `STATUS` | ArcGIS point geometry | Official City of Waterloo public street-tree ArcGIS layer; rows are restricted to `STATUS = 'Existing'` before blossom classification |
| Whitby | ArcGIS FeatureServer | `LATIN_NAME`, `COMMON_NAME` | ArcGIS point geometry | Official Town of Whitby public tree inventory ArcGIS layer |
| Windsor | ArcGIS MapServer | `species`, `status` | ArcGIS point geometry | Official City of Windsor `City Trees In Park` and `City Trees In Right Of Way` layers are loaded separately, restricted to `status = 'ACTIVE'`, and then merged into one city result |
| Ajax | ArcGIS MapServer | `TYPE`, `STATUS` | ArcGIS point geometry | Official Town of Ajax `Town Owned Trees` layer; rows are restricted to `STATUS = 'TREE'` before blossom classification |
| Barrie | ArcGIS MapServer | `GENUS` + `SPECIES`, `COMMONNAME`, `TREE_STATUS` | ArcGIS point geometry | Official City of Barrie public tree layer; rows are restricted to `TREE_STATUS = 'ACTIVE'` before blossom classification |
| Kingston | ArcGIS FeatureServer | `SCIENTIFIC_NAME`, `COMMON_NAME`, `OWNERSHIP` | ArcGIS point geometry | Official City of Kingston `City Owned Trees` layer; rows are restricted to `OWNERSHIP = 'Municipal'` before blossom classification |
| Niagara Falls | ArcGIS FeatureServer | `TreeSpecies`, `AssetOwnership` | ArcGIS point geometry | Official City of Niagara Falls trees inventory; rows are restricted to `AssetOwnership = 'CITY OF NIAGARA FALLS'` before blossom classification |
| Welland | ArcGIS MapServer | `Genus` + `Species`, `Species` | ArcGIS point geometry | Official City of Welland public trees layer; classification uses both the public genus and species text |
| Thunder Bay | ArcGIS FeatureServer | `COMMON`, `TREE_CYCLE` | ArcGIS point geometry | Official City of Thunder Bay public trees layer; rows are restricted to `TREE_CYCLE = 'TREE'`, and classification relies on the public common-name field because the public botanical abbreviations are not consistently expanded |
| Calgary | ArcGIS FeatureServer | `GENUS` + `SPECIES`, `COMMON_NAME`, `LIFE_CYCLE_STATUS` | ArcGIS point geometry | Official City of Calgary `Public Trees` layer; rows are restricted to `LIFE_CYCLE_STATUS = 'ACTIVE'` before blossom classification |
| Edmonton | SODA | `species_botanical`, `species`, `owner` | numeric `longitude` / `latitude` columns | Official City of Edmonton `Boulevard / Open Space Trees`; rows are filtered server-side with SoQL blossom predicates and clipped to the official Statistics Canada CSD boundary |
| St. Albert | ArcGIS FeatureServer | `LatinName`, `SpeciesCommon` | ArcGIS point geometry | Official City of St. Albert public tree inventory ArcGIS layer |
| Chestermere | ArcGIS FeatureServer | `Species_Scientific`, `Species`, `TreeStatus` | ArcGIS point geometry | Official City of Chestermere public trees ArcGIS layer; rows are restricted to `TreeStatus = 'Active'` before blossom classification |
| Okotoks | ArcGIS FeatureServer | `Tree_Speci`, `Tree_XXXX` | ArcGIS point geometry | Official Town of Okotoks public tree inventory ArcGIS layer; rows are restricted to `Tree_XXXX = 'Established'` before blossom classification |
| Lethbridge | ArcGIS MapServer | `genus` + `species`, `cultivar`, `status` | ArcGIS point geometry | Official City of Lethbridge public trees layer; rows are restricted to `status = 'Active'`, and cultivar text is retained as the common-name fallback for ornamental selections |
| Leduc | ArcGIS MapServer | `BOTANICAL_COMMON_NAME`, `CWSTATUS` | ArcGIS point geometry | Official City of Leduc public Cityworks trees layer; rows are restricted to `CWSTATUS = 'Active'` before blossom classification |
| Medicine Hat | ArcGIS MapServer | `SPECIES` parsed by `parse_dash_species()`, `TREE_ALIVE_DEAD` | ArcGIS point geometry | Official City of Medicine Hat public tree inventory layer; rows are restricted to living trees, and the public `SPECIES` field packs botanical/common text into one dash-delimited string |
| Red Deer | ArcGIS MapServer | `CmnNameSpecies` plus `Species` fallback | ArcGIS point geometry | Official City of Red Deer `PARK_Trees_inservice` layer; the public `CmnNameSpecies` field often packs common text plus a botanical tail in parentheses, so ETL parses the botanical suffix before classification |
| Airdrie | ArcGIS MapServer | `COMMENTS_1`, `COMMON_NAME`, `ASSETSTATUS` | ArcGIS point geometry | Official City of Airdrie public edible-trees layer; rows are restricted to `ASSETSTATUS = 'Active'`, and classification relies on the published cultivar/common text because no cleaner public scientific field is exposed |
| Abbotsford | ArcGIS FeatureServer | `SPP` | ArcGIS point geometry with `LATITUDE` / `LONGITUDE` fallback | Official City of Abbotsford `Tree Inventory 2019` park and street layers are loaded separately, merged into one city result, and clipped to the official Statistics Canada CSD boundary |
| Kelowna | ArcGIS MapServer | `Genus` + `Species`, `CommonName`, `Status` | ArcGIS point geometry | Official City of Kelowna public tree inventory ArcGIS layer; rows are restricted to `Status = 'A'` before blossom classification |
| Kamloops | ArcGIS MapServer | `COMMONFULLNAME`, `OWNERTYPE` | ArcGIS point geometry | Official City of Kamloops public parks tree layer; rows are restricted to `OWNERTYPE = 'PUBLIC'` before blossom classification |
| Prince George | ArcGIS FeatureServer | `GenusName` + `SpeciesName`, `CommonName`, `LifeCycleStatus`, `AssetOwner` | ArcGIS point geometry | Official City of Prince George public trees ArcGIS layer; rows are restricted to active city-owned trees before blossom classification |
| Penticton | ArcGIS FeatureServer | `GENUS` + `SPECIES`, `Status` | ArcGIS point geometry | Official City of Penticton public trees ArcGIS layer; rows are restricted to `Status = 'ACT'` before blossom classification |
| Maple Ridge | ArcGIS MapServer | `Genus` + `Species`, `CommonName`, `Status` | ArcGIS point geometry | Official City of Maple Ridge public street-tree ArcGIS layer; rows are restricted to `Status = 'Existing'` before blossom classification |
| Nanaimo | ArcGIS MapServer | `Species` | ArcGIS point geometry | Official City of Nanaimo public `Urban Trees` layer; classification relies on the single published species text field and official Statistics Canada CSD clipping |
| North Vancouver City | ArcGIS MapServer | `GENUS` + `SPECIES` | ArcGIS point geometry | Official City of North Vancouver `City Trees` layer clipped to the official Statistics Canada CSD boundary |
| North Vancouver District | Downloaded Shapefile | `COMMONNAME`, `GENUS`, `SPECIES`, `REMOVED` | shapefile points transformed to WGS84 | Official District of North Vancouver `Street Trees` shapefile; removed rows are excluded before blossom classification and official Statistics Canada CSD clipping |
| Fredericton | ArcGIS FeatureServer | `Genus_Spec`, `COMMON_NAM` | ArcGIS point geometry | Official City of Fredericton public tree inventory ArcGIS layer |
| Moncton | ArcGIS FeatureServer | public `BOTNAME` codes mapped into synthetic `PH_SCIENTIFIC_NAME` / `PH_COMMON_NAME` fields | ArcGIS point geometry | Official City of Moncton public trees ArcGIS layer; ETL applies a small public blossom-code mapping because the published layer exposes only short species codes |
| Gatineau | ArcGIS FeatureServer | `SPECIES`, `NAME_EN`, `NAME_FR` | ArcGIS point geometry | Official National Capital Commission `Remarkable Trees` layer; blossom rows are clipped to the official Gatineau Statistics Canada CSD boundary before publish |
| Longueuil | Downloaded GeoJSON | `Espece` | GeoJSON point coordinates from Données Québec | Official Ville de Longueuil `Arbres` GeoJSON; classification relies on the published species text and official Statistics Canada CSD clipping |
| Montreal | Downloaded CSV | `Essence_latin`, `Essence_ang`, `Essence_fr` | direct `Longitude` / `Latitude` columns | Official Ville de Montréal tree CSV; boundary is assembled by merging arrondissement polygons from the official administrative-limits dataset |
| Quebec City | Downloaded GeoJSON | `NOM_LATIN`, `NOM_FRANCAIS`, `TYPE_PROP` | GeoJSON point coordinates from Données Québec | Official Ville de Québec `Arbres répertoriés` GeoJSON clipped to the official Statistics Canada CSD boundary |
| Repentigny | Downloaded GeoJSON | `ESSENCE_LATIN`, `ESSENCE_FR`, `PROPRIETE` | GeoJSON point coordinates from Données Québec | Official Ville de Repentigny `Arbres` GeoJSON clipped to the official Statistics Canada CSD boundary |
| Saguenay | Downloaded GeoJSON | `essence_latin`, `essence_fr`, `propriete` | GeoJSON point coordinates from Données Québec | Official Ville de Saguenay tree-inventory GeoJSON; classification relies on the published species text and official Statistics Canada CSD clipping |
| Halifax | ArcGIS FeatureServer | `SP_SCIEN`, `SP_COMM`, `OWNER` | ArcGIS point geometry | Official Halifax Regional Municipality `Public Trees` layer; rows are restricted to `OWNER = 'HRM'`, and the jurisdiction boundary comes from the official `NSPW HRM Service Exchange Boundary (2022)` polygon |
| Regina | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official City of Regina public tree inventory layer; blossom filtering relies on the published species text and official Statistics Canada CSD clipping |
| Saskatoon | ArcGIS MapServer | `Latin_Name`, `Common_Name`, `Status`, `Ownership` | ArcGIS point geometry | Official City of Saskatoon public tree inventory layer; rows are restricted to `Status = 1` and `Ownership = 1` before blossom classification |
| Winnipeg | SODA | `botanical_name`, `common_name`, `point` | GeoJSON point coordinates from `point` | Official City of Winnipeg `Tree Inventory`; rows are filtered server-side with SoQL blossom predicates and clipped to the official Statistics Canada CSD boundary |
| Charlottetown | ArcGIS FeatureServer | `Species_Bot`, `Species_Com`, `Ownership` | ArcGIS point geometry | Official City of Charlottetown `Tree Sites Public` layer clipped to the official Prince Edward Island Statistics Canada CSD boundary |
| Grande Prairie | ArcGIS FeatureServer | `BOTANICAL_NAME`, `ASSET_NAME` | ArcGIS point geometry | Official City of Grande Prairie park trees layer; classification relies on the published common-name species text and official Statistics Canada CSD clipping |
| Strathcona County | ArcGIS FeatureServer | `species` | ArcGIS point geometry | Official Strathcona County managed trees layer; classification relies on the published common-name species field and official Statistics Canada CSD clipping |
| Saint John | ArcGIS FeatureServer | `Species`, `Cultivar` | ArcGIS point geometry | Official City of Saint John `Urban Forestry Trees` layer; classification relies on the published common-name species values and official Statistics Canada CSD clipping |
| Moose Jaw | ArcGIS MapServer | `GENUS` + `SPECIES`, `NAME`, `TREETYPE` | ArcGIS point geometry | Official City of Moose Jaw public trees layer clipped to the official Statistics Canada CSD boundary |
| Weyburn | ArcGIS FeatureServer | `SciName`, `Species` | ArcGIS point geometry | Public Weyburn urban-forest tree inventory service clipped to the official Statistics Canada CSD boundary |
| Coquitlam | ArcGIS MapServer | `SPECIES`, `TYPE` | ArcGIS point geometry | Official City of Coquitlam maintained trees layer clipped to the official jurisdiction boundary |
| Langley Township | ArcGIS FeatureServer | `TreeName_t`, `CommonName`, `Genera` | ArcGIS point geometry | Official Township of Langley tree inventory clipped to the official Metro Vancouver administrative boundary |
| Port Coquitlam | ArcGIS MapServer | `Species` from park + street layers | ArcGIS point geometry | Official City of Port Coquitlam public park-tree and street-tree layers are loaded separately, merged into one city result, and clipped to the official jurisdiction boundary |
| Port Moody | ArcGIS FeatureServer | `SCIENTIFIC`, `COMMON_NAM`, `STATUS`, `TYPE` | ArcGIS point geometry | Official City of Port Moody `Street Trees Inventory` layer; rows are restricted to `STATUS = 'OPERATIONAL'` and `TYPE = 'Street Tree'` before blossom classification |
| West Vancouver | ArcGIS FeatureServer | `SpeciesName` with `CommonName` / `ScientificName` fallback | ArcGIS point geometry | Public District of West Vancouver tree-inventory planning layer clipped to the official Metro Vancouver administrative boundary |
| White Rock | ArcGIS MapServer | `SpeciesNam`, `CommName`, `Removed` | ArcGIS point geometry | Official City of White Rock `Trees` layer; removed rows are excluded before blossom classification and official Metro Vancouver administrative clipping |
| Austin | SODA | `species`, `longtitude`, `latitude` with GeoJSON `geometry` fallback | numeric lon/lat when valid; otherwise point from the row `geometry` object | Official City of Austin `Tree Inventory` dataset; some blossom rows expose projected numeric coordinates, so ETL validates WGS84 ranges and falls back to the GeoJSON point when necessary |
| Dallas | TreeKeeper | `SITE_ATTR1` parsed by `parse_species_text()` | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Dallas public TreeKeeper inventory linked from the city forestry page |
| Mesa | ArcGIS FeatureServer | `BOTANICAL_NAME`, `COMMON_NAME`, `ISACTIVE` | ArcGIS point geometry with `Longitude` / `Latitude` fallback | Official City of Mesa `Mesa AZ iTree Inventory` layer; rows are restricted to `ISACTIVE = 1` before blossom classification |
| Tempe | ArcGIS FeatureServer | `Species_Name` | ArcGIS point geometry with `xCoordinate` / `yCoordinate` fallback | Official City of Tempe tree inventory dataset published on the city ArcGIS open-data portal |
| Johns Creek | ArcGIS FeatureServer | `TreeSpeciesFromML` | ArcGIS point geometry | Official City of Johns Creek public `Tree Inventory` ArcGIS layer; classification relies on the published species label field |
| Brighton | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Brighton public TreeKeeper inventory linked from the city's Open Space & Forestry page |
| Boulder | ArcGIS MapServer | `LATINNAME`, `COMMONNAME`, `OWNEDBY` | ArcGIS point geometry | Official City of Boulder `Tree Inventory Open Data` layer; rows are restricted to `OWNEDBY = 'City'` before blossom classification |
| Denver | ArcGIS FeatureServer | `SPECIES_BOTANIC`, `SPECIES_COMMON` | ArcGIS point geometry requested in `outSR=4326`, with `X_LONG` / `Y_LAT` fallback | Official City and County of Denver public tree inventory service; blossom rows are filtered server-side against the public common/botanical species fields |
| Erie | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official Town of Erie public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Fort Collins | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Fort Collins public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Longmont | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry | Official City of Longmont public tree inventory layer; blossom rows are filtered server-side against the published `SPECIES` field |
| Wheat Ridge | TreePlotter | `species_latin` / `species_common` with public TreePlotter inventory tables | WKB point hex -> Web Mercator -> lon/lat | Official City of Wheat Ridge public TreePlotter inventory; rows are clipped to the official jurisdiction boundary before publish |
| Cape Coral | ArcGIS MapServer | `SPECIES` | ArcGIS point geometry with `X` / `Y` fallback | Official City of Cape Coral public tree inventory layer; blossom rows are filtered server-side against `SPECIES` before official jurisdiction clipping |
| Tallahassee | ArcGIS MapServer | `BOTANICAL`, `COMMON`, `LIFECYCLE`, `OWNER` | ArcGIS point geometry | Official City of Tallahassee public Cityworks tree inventory layer; rows are restricted to active city-owned trees before blossom classification |
| West Palm Beach | ArcGIS FeatureServer | `LatinName`, `CommonName`, `Status` | ArcGIS point geometry with `Longitude` / `Latitude` fallback | Official City of West Palm Beach public trees layer; rows are restricted to `Status = 'Alive'` before blossom classification |
| Winter Park | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Winter Park public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Normal | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official Town of Normal public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Westchester | ArcGIS FeatureServer | `COMMON_NAME`, `LATIN_NAME` | ArcGIS point geometry with `X` / `Y` fallback | Official Village of Westchester public tree inventory layer; blossom rows are filtered server-side against `COMMON_NAME` before official jurisdiction clipping |
| Danville | ArcGIS FeatureServer | `TreeCommonName` | ArcGIS point geometry | Official City of Danville public tree inventory ArcGIS layer |
| Evanston | ArcGIS MapServer | `Common`, `Genus`, `SPP` | ArcGIS point geometry | Official City of Evanston public trees ArcGIS layer |
| O'Fallon | ArcGIS FeatureServer | `COMMON_NAME`, `TREESPECIES` | ArcGIS point geometry with `LONGITUDE` / `LATITUDE` fallback | Official City of O'Fallon public city-tree ArcGIS layer |
| Bloomington | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Bloomington public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Pendleton | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official Town of Pendleton public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Valparaiso | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Valparaiso public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Branson | ArcGIS FeatureServer | `SPP`, `NAME`, `ACTIVE` | ArcGIS point geometry | Official City of Branson public trees layer; rows are restricted to `ACTIVE = 1` before blossom classification |
| Brentwood | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Brentwood public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Clarksville | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Clarksville public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Ferndale | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Ferndale public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Kalamazoo | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Kalamazoo public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Ann Arbor | ArcGIS FeatureServer | `COMMONNAME`, `BOTANICAL` | ArcGIS point geometry | Official City of Ann Arbor street-tree inventory ArcGIS layer |
| Dearborn Heights | ArcGIS FeatureServer | `USER_Type` | ArcGIS point geometry | Public City of Dearborn Heights tree record ArcGIS layer |
| East Lansing | ArcGIS FeatureServer | `Tree_Name`, `dvSPP` | ArcGIS point geometry | Official City of East Lansing public tree status ArcGIS service |
| Grand Rapids | ArcGIS FeatureServer | `COMMON`, `BOTANICAL` | ArcGIS point geometry | Official City of Grand Rapids public street-tree ArcGIS layer |
| Madison | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Madison public TreeKeeper inventory integrated with the official jurisdiction boundary |
| Franklin | ArcGIS FeatureServer | `Spp_Common`, `Spp_Latin` | ArcGIS point geometry | Official Milwaukee County public tree viewer clipped to the official Franklin jurisdiction boundary |
| Milwaukee | ArcGIS FeatureServer | `Spp_Common`, `Spp_Latin` | ArcGIS point geometry | Official Milwaukee County public tree viewer clipped to the official Milwaukee jurisdiction boundary |
| Wauwatosa | ArcGIS FeatureServer | `Spp_Common`, `Spp_Latin` | ArcGIS point geometry | Official Milwaukee County public tree viewer clipped to the official Wauwatosa jurisdiction boundary |
| Springfield | TreeKeeper | detected blossom species field from public `SITE_ATTR*` columns | direct `LONGITUDE` / `LATITUDE` with `SITE_GEOMETRY` fallback | Official City of Springfield public TreeKeeper inventory integrated with the official jurisdiction boundary |
| St. Louis | ArcGIS MapServer | `COMMON`, `CONDITION` | ArcGIS point geometry | Official City of St. Louis `City Street Trees` layer; rows exclude `CONDITION = 'N/A'` before blossom classification |
| Carmel | ArcGIS FeatureServer | `COMM_NAME`, `SPP` | ArcGIS point geometry with `X` / `Y` fallback | Official City of Carmel public tree inventory layer; blossom rows are filtered server-side against `COMM_NAME` before official jurisdiction clipping |
| Maitland | ArcGIS FeatureServer | `COMMON`, `BOTANICAL` | ArcGIS point geometry with `X` / `Y` fallback | Official City of Maitland public tree inventory layer; blossom rows are filtered server-side against `COMMON` before official jurisdiction clipping |
| Michigan City | ArcGIS FeatureServer | `COMMON_NAME`, `LATIN_NAME` | ArcGIS point geometry with `X` / `Y` fallback | Official City of Michigan City public tree inventory layer; blossom rows are filtered server-side against `COMMON_NAME` before official jurisdiction clipping |
| Westfield | ArcGIS MapServer | `Tree` | ArcGIS point geometry requested in `outSR=4326` | Official City of Westfield public tree inventory layer; blossom rows are filtered server-side against the published `Tree` common-name field before official jurisdiction clipping |
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
6. Assign ZIP by point-in-polygon lookup for US cities only; Canadian cities currently publish blank ZIP fields.
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
6. Rerun ETL and update `docs/research/city-coverage-tracker.md`.
7. Do not add coverage polygons for a city unless the official boundary geometry is resolved.

## Incremental Publish Fallback
- Full `npm run etl` remains the canonical path.
- `npm run etl` now chains the stable targeted-publish refresh for `Arlington`, `Austin`, `Baltimore`, `Boston`, `Dallas`, `Jersey City`, `Las Vegas`, `Milpitas`, `Salt Lake City`, `San Mateo`, `San Rafael`, `Salinas`, `Fremont`, `Concord`, `South San Francisco`, `New York City`, `Philadelphia`, `Pittsburgh`, and `Cambridge` after the full ETL, so those published area/shard files are regenerated as part of the normal publish path.
- When upstream sources are too slow and the already-published local region files are still current, refresh area-shard outputs without rerunning the full ETL:
  - `python3 scripts/refresh_region_area_shards.py --data-dir public/data --region all`
- When a new city source has been validated but is not yet folded into the main full ETL path, publish it incrementally with:
  - `python3 scripts/publish_targeted_city_updates.py --city <City Name>`
- When preparing a whole state in advance so future city activation can reuse stored boundaries, prebuild the state city/place boundaries with:
  - `python3 scripts/prebuild_state_boundaries.py --country us --state ca`
- If gray-coverage rules or official-boundary hints changed without rebuilding all tree rows, refresh coverage and meta bounds with:
  - `python3 scripts/refresh_coverage_metadata.py --data-dir public/data`
- After that, rerun `python3 scripts/check_region_data_sizes.py --data-dir public/data` so `meta.v2.json` and area-shard artifacts stay internally consistent.
