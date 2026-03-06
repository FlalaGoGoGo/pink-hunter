# Pink Hunter

Mobile-first blooming tree map for Cherry / Plum / Peach / Magnolia / Crabapple.

Live domain:
- [pinkhunter.flalaz.com](http://pinkhunter.flalaz.com/)

## Highlights
- Official-city-boundary coverage only.
- Mobile-first map UI with desktop split layout.
- Five blossom groups: `cherry`, `plum`, `peach`, `magnolia`, `crabapple`.
- Dual-language UI: `en-US`, `zh-CN`.
- Covered areas and gray researched areas are both shown on the map.

## Hard Repo Rule
- Every accepted local change must also be synchronized into `/Users/zhangziling/Documents/Project-Pink-Hunter/GitHub/pink-hunter`.
- After sync, the GitHub export repo must be committed and pushed to [FlalaGoGoGo/pink-hunter](https://github.com/FlalaGoGoGo/pink-hunter).
- Policy doc: [docs/GITHUB_SYNC_POLICY.md](docs/GITHUB_SYNC_POLICY.md)
- Preferred helper: `./scripts/sync_github_export.sh "Commit message"`

## Coverage Areas

### Washington
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

### Oregon
- Portland

### Washington, DC
- Washington DC

### British Columbia
- Vancouver BC
- Victoria BC

### Gray Coverage
- Gray coverage marks cities whose official boundary is public but whose official public single-tree dataset is not available yet.
- Tracking details: [docs/CITY_COVERAGE_TRACKER.md](docs/CITY_COVERAGE_TRACKER.md)

## Official Data Sources
- Seattle: [Combined Tree Point](https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Combined_Tree_Point/FeatureServer/0)
- Seattle supplemental: [UW OSM supplemental cache](data/supplemental/uw_prunus_overpass.json)
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
- Portland: [Street Tree Inventory - Active Records](https://www.portlandmaps.com/od/rest/services/COP_OpenData_Environment/MapServer/1415)
- Washington DC: [Urban Tree Canopy](https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Urban_Tree_Canopy/MapServer/23)
- Vancouver BC: [Public trees](https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/public-trees)
- Victoria BC: [Tree Species (Parks trees database)](https://maps.victoria.ca/server/rest/services/OpenData/OpenData_Parks/MapServer/15)

## Local Development
1. Install dependencies
   - `npm install`
2. Build data
   - `npm run etl`
3. Run the app
   - `npm run dev`
4. Build for production
   - `npm run build`

## Data Outputs
- `public/data/trees.v1.geojson`
- `public/data/coverage.v1.geojson`
- `public/data/species-guide.v1.json`
- `public/data/meta.v1.json`
- `public/data/unknown_scientific_names.v1.json`
- `data/normalized/trees_normalized.csv`

## Docs
- API: [docs/API.md](docs/API.md)
- Coverage tracker: [docs/CITY_COVERAGE_TRACKER.md](docs/CITY_COVERAGE_TRACKER.md)
- ETL methods: [docs/CITY_ETL_METHODS.md](docs/CITY_ETL_METHODS.md)
- Taxonomy keywords: [docs/TAXONOMY_KEYWORDS.md](docs/TAXONOMY_KEYWORDS.md)
- GitHub Pages subdomain setup: [docs/GITHUB_PAGES_SUBDOMAIN_SETUP.md](docs/GITHUB_PAGES_SUBDOMAIN_SETUP.md)
- GitHub sync policy: [docs/GITHUB_SYNC_POLICY.md](docs/GITHUB_SYNC_POLICY.md)
