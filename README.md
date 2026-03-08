# Pink Hunter

Mobile-first pink blossom tree map for Cherry / Plum / Peach / Magnolia / Crabapple.

Live domain:
- [pinkhunter.flalaz.com](http://pinkhunter.flalaz.com/)

## Highlights
- Official-jurisdiction-boundary coverage only.
- Mobile-first map UI with desktop split layout.
- Five blossom groups: `cherry`, `plum`, `peach`, `magnolia`, `crabapple`.
- Multilingual UI: `en-US`, `zh-CN`, `zh-TW`, `es-ES`, `ko-KR`, `ja-JP`, `fr-FR`, `vi-VN`.
- Covered areas and gray researched areas are both shown on the map.

## Hard Repo Rule
- Every accepted local change must also be synchronized into `/Users/zhangziling/Documents/Project-Pink-Hunter/GitHub/pink-hunter`.
- After sync, the GitHub export repo must be committed and pushed to [FlalaGoGoGo/pink-hunter](https://github.com/FlalaGoGoGo/pink-hunter).
- Policy doc: [docs/GITHUB_SYNC_POLICY.md](docs/GITHUB_SYNC_POLICY.md)
- Preferred helper: `./scripts/sync_github_export.sh "Commit message"`
- Published region data must pass `./scripts/check_region_data_sizes.py --data-dir public/data` before sync/push.

## Coverage Areas
<details>
<summary>Washington</summary>

- Seattle
- Bellevue
- Redmond
- Renton
- Kenmore
- SeaTac
- Sammamish
- Shoreline
- Snohomish
- Everett
- Kirkland
- Bellingham
- Spokane
- Yakima
- Walla Walla
- Puyallup
- Gig Harbor

</details>

<details>
<summary>New York</summary>

- New York City

</details>

<details>
<summary>Virginia</summary>

- Arlington

</details>

<details>
<summary>Maryland</summary>

- Baltimore

</details>

<details>
<summary>New Jersey</summary>

- Jersey City

</details>

<details>
<summary>Pennsylvania</summary>

- Philadelphia
- Pittsburgh

</details>

<details>
<summary>Massachusetts</summary>

- Boston
- Cambridge

</details>

<details>
<summary>Ontario</summary>

- Ottawa
- Toronto

</details>

<details>
<summary>Quebec</summary>

- Montreal

</details>

<details>
<summary>Oregon</summary>

- Portland

</details>

<details>
<summary>California</summary>

- Berkeley
- Burlingame
- Concord
- Cupertino
- Fremont
- Milpitas
- Oakland
- Palo Alto
- Salinas
- San Francisco
- San Jose
- San Mateo
- San Rafael
- South San Francisco

</details>

<details>
<summary>Washington, DC</summary>

- Washington DC

</details>

<details>
<summary>British Columbia</summary>

- New Westminster
- Vancouver BC
- Victoria BC

</details>

### Gray Coverage
- Gray coverage marks cities whose official boundary is public but whose official public single-tree dataset is not available yet.
- Current gray-coverage examples include `Alexandria`, `Montgomery County`, `Mountain View`, `Sunnyvale`, `Santa Clara`, `Monterey`, `Sacramento`, `Napa`, `Richmond`, `Santa Cruz`, `Santa Rosa`, `Stockton`, `Redwood City`, `Alameda`, `Hayward`, `Daly City`, `Beaverton`, `Gresham`, `Hillsboro`, `Salem`, `Tigard`, `Burnaby`, `Coquitlam`, `Delta`, `Langley City`, `North Vancouver City`, `North Vancouver District`, `Richmond BC`, `Saanich`, `Surrey`, `West Vancouver`, and `White Rock`.
- Tracking details: [docs/CITY_COVERAGE_TRACKER.md](docs/CITY_COVERAGE_TRACKER.md)

## Official Data Sources
<details>
<summary>Washington</summary>

- Seattle: [Combined Tree Point](https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Combined_Tree_Point/FeatureServer/0)
- Bellevue: [City Trees](https://services1.arcgis.com/EYzEZbDhXZjURPbP/arcgis/rest/services/City_Trees/FeatureServer/29)
- Redmond: [TreeSite](https://services7.arcgis.com/9u5SMK7jcrQbBJIC/arcgis/rest/services/TreeSite/FeatureServer/0)
- Renton: [Tree Sites](https://webmaps.rentonwa.gov/as03/rest/services/Cityworks/proCSParkAsset/MapServer/24)
- Kenmore: [Public Trees](https://gwa.kenmorewa.gov/arcgis/rest/services/Public_Trees/FeatureServer/22)
- SeaTac: [Trees](https://services3.arcgis.com/DLryYCwhA8W7Jq7Q/arcgis/rest/services/Trees/FeatureServer/1)
- Sammamish: [TreeKeeper Street Sites](https://sammamishwa.treekeepersoftware.com/cffiles/grids.cfc), [TreeKeeper Park Sites](https://sammamishwa.treekeepersoftware.com/cffiles/grids.cfc)
- Shoreline: [Public Tree Inventory](https://gis.shorelinewa.gov/server/rest/services/PublicFacing/Parks/MapServer/7)
- Snohomish: [Snohomish Tree Inventory](https://services9.arcgis.com/hUiJ0kKwHN6Cf0DY/arcgis/rest/services/Tree_Inventory_Canopy_2024_WFL1/FeatureServer/3)
- Everett: [Everett TreeKeeper Park Sites](https://everettwa.treekeepersoftware.com/cffiles/grids.cfc)
- Kirkland: [2023-2024 Kirkland Tree Inventory](https://pg-cloud.com/main/server/db.php)
- Bellingham: [Bellingham Trees](https://maps.cob.org/arcgis3/rest/services/Parks/NotableTrees/MapServer/0)
- Spokane: [Spokane Tree Inventory](https://services.arcgis.com/3PDwyTturHqnGCu0/arcgis/rest/services/Tree_Inventory/FeatureServer/7)
- Yakima: [Yakima Trees](https://gis.yakimawa.gov/arcgis/rest/services/Parks/Trees/MapServer/0)
- Walla Walla: [City of Walla Walla Trees](https://gis2.ci.walla-walla.wa.us/arcgis/rest/services/Basemap/GISBaseMap_TreesVisible/MapServer/0)
- Puyallup: [City Maintained Street Trees](https://services8.arcgis.com/5K6vnOH0GkPyJs6A/arcgis/rest/services/City_Maintained_Street_Trees/FeatureServer/0)
- Gig Harbor: [PW Trees Public Viewer](https://services3.arcgis.com/FjNT4j1knnY5Wsw5/arcgis/rest/services/PW_Trees_Public_Viewer/FeatureServer/0)

</details>

<details>
<summary>New York</summary>

- New York City: [2015 Street Tree Census - Tree Data](https://data.cityofnewyork.us/Environment/2015-Street-Tree-Census-Tree-Data/uvpi-gqnh)

</details>

<details>
<summary>Virginia</summary>

- Arlington: [Open Data Portal](https://www.arlingtonva.us/About-Arlington/Data-and-Research/Open-Data-Portal)

</details>

<details>
<summary>Maryland</summary>

- Baltimore: [Open Baltimore](https://data.baltimorecity.gov/)

</details>

<details>
<summary>New Jersey</summary>

- Jersey City: [Urban Forests](https://www.jerseycitynj.gov/cityhall/infrastructure/division_of_sustainability/urbanforests)

</details>

<details>
<summary>Pennsylvania</summary>

- Philadelphia: [PPR Tree Inventory 2025](https://metadata.phila.gov/#home/datasetdetails/57a0e1d5aa8882104134830e/representationdetails/690a4183ef9cba032bd11d00/)
- Pittsburgh: [TreeKeeper Inventory](https://pittsburghpa.treekeepersoftware.com/)

</details>

<details>
<summary>Massachusetts</summary>

- Boston: [BPRD Trees](https://data.boston.gov/dataset/bprd-trees)
- Cambridge: [Street Trees](https://www.cambridgema.gov/GIS/gisdatadictionary/Environmental/ENVIRONMENTAL_StreetTrees)

</details>

<details>
<summary>Ontario</summary>

- Ottawa: [Canopy cover and tree inventory](https://ottawa.ca/en/canopy-cover-and-tree-inventory)
- Toronto: [Street Tree Data](https://open.toronto.ca/dataset/street-tree-data/)

</details>

<details>
<summary>Quebec</summary>

- Montreal: [Arbres publics sur le territoire de la Ville](https://donnees.montreal.ca/fr/dataset/arbres)

</details>

<details>
<summary>Oregon</summary>

- Portland: [Street Tree Inventory - Active Records](https://www.portlandmaps.com/od/rest/services/COP_OpenData_Environment/MapServer/1415)

</details>

<details>
<summary>California</summary>

- Burlingame: [City Street Tree Inventory](https://www.burlingame.org/466/Trees-Urban-Forest)
- Concord: [Tree Inventory](https://www.cityofconcord.org/1249/Tree-Inventory)
- Palo Alto: [City of Palo Alto Open GIS](https://opengis.cityofpaloalto.org/)
- Berkeley: [Tree_Berkeley20191107](https://www.arcgis.com/home/item.html?id=88829f4ae7254b5280732e88e65e6df5)
- Cupertino: [Cupertino Open Data GIS](https://gis-cupertino.opendata.arcgis.com/)
- Fremont: [Tree Inventory / Tree Value](https://www.fremont.gov/government/departments/maintenance-operations/urban-forestry/tree-inventory-tree-value)
- Milpitas: [Trees RO](https://services8.arcgis.com/OPmRdssd8jj0bT5H/arcgis/rest/services/Trees_RO/FeatureServer/0)
- Oakland: [Oakland Street Trees](https://data.oaklandca.gov/Environmental/Oakland-Street-Trees/4jcx-enxf)
- Salinas: [Tree Inventory](https://cityofsalinas.opendatasoft.com/explore/dataset/tree-inventory/)
- San Francisco: [Street Tree List](https://data.sfgov.org/City-Infrastructure/Street-Tree-List/tkzw-k3nq)
- San Jose: [Street Tree](https://data.sanjoseca.gov/dataset/street-tree)
- San Mateo: [Street Trees](https://www.arcgis.com/home/item.html?id=67c8b57d2d91459c9f951df9de961a06)
- San Rafael: [Trees](https://www.arcgis.com/home/item.html?id=8a236959df6f438ba38bdf5db85ce54a)
- South San Francisco: [City Trees](https://www.ssfca.gov/Departments/Parks-Recreation/Divisions/Parks-Division/Trees)

</details>

<details>
<summary>Washington, DC</summary>

- Washington DC: [Urban Tree Canopy](https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Urban_Tree_Canopy/MapServer/23)

</details>

<details>
<summary>British Columbia</summary>

- New Westminster: [Tree Inventory (Active Trees)](https://services3.arcgis.com/A7O8YnTNtzRPIn7T/arcgis/rest/services/Tree_Inventory_(PROD)_4_view/FeatureServer)
- Vancouver BC: [Public trees](https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/public-trees)
- Victoria BC: [Tree Species (Parks trees database)](https://maps.victoria.ca/server/rest/services/OpenData/OpenData_Parks/MapServer/15)

</details>

<details>
<summary>Supplemental</summary>

- Seattle supplemental: [UW OSM supplemental cache](data/supplemental/uw_prunus_overpass.json)

</details>

## Local Development
1. Install dependencies
   - `npm install`
2. Install ETL dependencies
   - `python3 -m pip install -r requirements.txt`
3. Build data
   - `npm run etl`
4. Run the app
   - `npm run dev`
5. Build for production
   - `npm run build`

## Data Outputs
### Published
- `public/data/trees.<region>.city-index.v1.json`
- `public/data/trees.<region>.city.<slug>.v1.geojson`
- `public/data/coverage.v1.geojson`
- `public/data/species-guide.v1.json`
- `public/data/meta.v2.json`
- `public/data/unknown_scientific_names.v1.json`

### Local ETL Audit
- `data/normalized/trees_normalized.csv`

## Region Publishing
- Tree points are now published by city for every region, not as region-wide GeoJSON files.
- Current regional groups:
  - `WA`
  - `CA`
  - `OR`
  - `DC`
  - `BC`
  - `VA`
  - `MD`
  - `NJ`
  - `NY`
  - `PA`
  - `MA`
- Local-only ETL audit outputs such as `data/normalized/trees_normalized.csv` and `data/tmp/*` are not part of the GitHub export repo.
- `public/data/meta.v2.json` contains the region index, region bounds, aggregate size metadata, city-split index paths, and species-count summaries for the full site, each region, and each published area.
- All published tree-point files now follow the same city-split contract:
  - `public/data/trees.<region>.city-index.v1.json`
  - `public/data/trees.<region>.city.<slug>.v1.geojson`
- If a full ETL run is blocked but current published region files are still available locally, refresh city-split outputs with:
  - `python3 scripts/refresh_region_city_splits.py --data-dir public/data --region all`
- If coverage or gray-coverage rules changed without rebuilding all tree data, refresh coverage and bounds with:
  - `python3 scripts/refresh_coverage_metadata.py --data-dir public/data`
- Aggregate warning thresholds for each region:
  - `warning`: `>= 35 MiB raw`
  - `high_warning`: `>= 45 MiB raw`
  - `hard_fail`: `>= 50 MiB raw`

## Docs
- API: [docs/API.md](docs/API.md)
- Coverage tracker: [docs/CITY_COVERAGE_TRACKER.md](docs/CITY_COVERAGE_TRACKER.md)
- ETL methods: [docs/CITY_ETL_METHODS.md](docs/CITY_ETL_METHODS.md)
- Taxonomy keywords: [docs/TAXONOMY_KEYWORDS.md](docs/TAXONOMY_KEYWORDS.md)
- GitHub Pages subdomain setup: [docs/GITHUB_PAGES_SUBDOMAIN_SETUP.md](docs/GITHUB_PAGES_SUBDOMAIN_SETUP.md)
- GitHub sync policy: [docs/GITHUB_SYNC_POLICY.md](docs/GITHUB_SYNC_POLICY.md)
- Nano Banana prompts: [docs/NANO_BANANA_PROMPTS.md](docs/NANO_BANANA_PROMPTS.md)
