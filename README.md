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
- Policy doc: [docs/ops/github-sync-policy.md](docs/ops/github-sync-policy.md)
- Preferred helper: `./scripts/sync_github_export.sh "Commit message"`
- Preferred command wrapper: `./scripts/ops_runner.sh sync-release "Commit message"`
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

- Albany
- Buffalo
- Ithaca
- New York City
- Saratoga Springs
- Syracuse
- Troy

</details>

<details>
<summary>Connecticut</summary>

- Greenwich
- Groton
- Hartford
- New Haven
- Stamford
- West Hartford

</details>

<details>
<summary>Virginia</summary>

- Arlington
- Charlottesville
- Fairfax
- Falls Church
- Fredericksburg
- Newport News
- Norfolk
- Richmond
- Virginia Beach

</details>

<details>
<summary>Maryland</summary>

- Annapolis
- Baltimore
- Gaithersburg
- Garrett Park

</details>

<details>
<summary>North Carolina</summary>

- Durham

</details>

<details>
<summary>New Jersey</summary>

- Dumont
- Ho-Ho-Kus
- Hoboken
- Jersey City
- Millburn
- Montclair
- Morristown
- Newark
- Oradell
- Princeton
- River Edge
- Rutherford
- Westwood

</details>

<details>
<summary>Pennsylvania</summary>

- Meadville
- Philadelphia
- Pittsburgh

</details>

<details>
<summary>Massachusetts</summary>

- Belmont
- Boston
- Brookline
- Cambridge
- Dedham
- Longmeadow
- Lynn
- Medford
- New Bedford
- Newton
- Somerville
- Springfield
- Waltham
- Worcester

</details>

<details>
<summary>New Hampshire</summary>

- Manchester

</details>

<details>
<summary>Rhode Island</summary>

- Providence

</details>

<details>
<summary>Vermont</summary>

- Shelburne
- Middlebury
- Winooski
- Northfield
- Milton
- Hinesburg
- Essex
- South Burlington
- Colchester
- Randolph

</details>

<details>
<summary>Texas</summary>

- Austin
- Dallas
- Houston

</details>

<details>
<summary>Colorado</summary>

- Denver

</details>

<details>
<summary>Nevada</summary>

- Las Vegas

</details>

<details>
<summary>Utah</summary>

- Salt Lake City

</details>

<details>
<summary>Alberta</summary>

- Calgary
- Edmonton
- St. Albert
- Chestermere
- Okotoks
- Lethbridge
- Medicine Hat
- Red Deer
- Airdrie

</details>

<details>
<summary>Ontario</summary>

- Ajax
- Barrie
- Burlington
- Cambridge ON
- Guelph
- Halton Hills
- Hamilton
- Kingston
- Kitchener
- London
- Mississauga
- Niagara Falls
- Oakville
- Ottawa
- Peterborough
- Tecumseh
- Thunder Bay
- Toronto
- Waterloo
- Welland
- Whitby
- Windsor

</details>

<details>
<summary>Quebec</summary>

- Gatineau
- Montreal

</details>

<details>
<summary>Manitoba</summary>

- Winnipeg

</details>

<details>
<summary>New Brunswick</summary>

- Fredericton
- Moncton

</details>

<details>
<summary>Nova Scotia</summary>

- Halifax

</details>

<details>
<summary>Saskatchewan</summary>

- Regina
- Saskatoon

</details>

<details>
<summary>Oregon</summary>

- Portland

</details>

<details>
<summary>California</summary>

- Anaheim
- Azusa
- Bell
- Berkeley
- Beverly Hills
- Buena Park
- Burbank
- Burlingame
- Camarillo
- Chino
- Citrus Heights
- Concord
- Corona
- Costa Mesa
- Cudahy
- Cupertino
- Dana Point
- El Segundo
- Encinitas
- Escondido
- Fontana
- Fremont
- Fullerton
- Gilroy
- Glendale
- Glendora
- Goleta
- Inglewood
- Irvine
- La Canada Flintridge
- La Mesa
- La Mirada
- La Verne
- Laguna Beach
- Lodi
- Los Angeles
- Los Gatos
- Maywood
- Milpitas
- Monterey Park
- Morgan Hill
- Mountain View
- Newport Beach
- Norwalk
- Oakland
- Oxnard
- Palo Alto
- Pasadena
- Pleasanton
- Pomona
- Poway
- Rancho Cucamonga
- Rancho Palos Verdes
- Redlands
- Redondo Beach
- Riverside
- Sacramento
- Salinas
- San Diego
- San Dimas
- San Fernando
- San Francisco
- San Jose
- San Mateo
- San Rafael
- Santa Barbara
- Santa Clarita
- Santa Fe Springs
- Santa Monica
- Santee
- Saratoga
- Solana Beach
- South Gate
- South San Francisco
- Sunnyvale
- Thousand Oaks
- Torrance
- Ventura
- Vista
- West Covina
- West Hollywood
- West Sacramento
- Yorba Linda

</details>

<details>
<summary>Washington, DC</summary>

- Washington DC

</details>

<details>
<summary>British Columbia</summary>

- Abbotsford
- Kamloops
- Kelowna
- Maple Ridge
- Nanaimo
- New Westminster
- North Vancouver City
- North Vancouver District
- Penticton
- Prince George
- Vancouver BC
- Victoria BC

</details>

### Gray Coverage
- Gray coverage marks cities whose official boundary is public but whose official public single-tree dataset is not available yet.
- Current gray-coverage examples include `Alexandria`, `Montgomery County`, `Newark`, `Santa Clara`, `Monterey`, `Napa`, `Richmond (CA)`, `Santa Cruz`, `Santa Rosa`, `Stockton`, `Redwood City`, `Alameda`, `Hayward`, `Daly City`, `Long Beach`, `Santa Ana`, `Beaverton`, `Gresham`, `Hillsboro`, `Salem`, `Tigard`, `Burnaby`, `Coquitlam`, `Delta`, `Langley City`, `Richmond BC`, `Saanich`, `Surrey`, `West Vancouver`, and `White Rock`.
- Tracking details: [docs/research/city-coverage-tracker.md](docs/research/city-coverage-tracker.md)

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

- Albany: [TreeKeeper Inventory](https://albanyny.treekeepersoftware.com/)
- New York City: [2015 Street Tree Census - Tree Data](https://data.cityofnewyork.us/Environment/2015-Street-Tree-Census-Tree-Data/uvpi-gqnh)
- Saratoga Springs: [Tree Inventory](https://pg-cloud.com/SaratogaSpringsNY/)
- Troy: [Tree Inventory](https://pg-cloud.com/TroyNY/)

</details>

<details>
<summary>Connecticut</summary>

- Groton: [Groton Tree Inventory](https://experience.arcgis.com/experience/d06d9f14108945d097d879d724d4cf56)
- West Hartford: [Tree Inventory](https://pg-cloud.com/WestHartfordCT/)

</details>

<details>
<summary>Virginia</summary>

- Arlington: [Open Data Portal](https://www.arlingtonva.us/About-Arlington/Data-and-Research/Open-Data-Portal)
- Charlottesville: [OpenData Trees](https://www.arcgis.com/home/item.html?id=e7c856379492408e9543a25d684b8311)
- Fairfax: [Tree Inventory](https://pg-cloud.com/FairfaxVA/)
- Fredericksburg: [Trees Public](https://experience.arcgis.com/experience/367d494216d844179620057d78c168d7)
- Newport News: [Newport News Tree Inventory](https://www.arcgis.com/home/item.html?id=9d10ce6b9f0e4d29ac48285037193138)
- Norfolk: [City Tree Inventory](https://data.norfolk.gov/Government/City-Tree-Inventory/cmvv-agyb)
- Richmond: [Tree Inventory, City of Richmond, Virginia](https://cor.maps.arcgis.com/apps/webappviewer/index.html?id=3dda2aa7521941d8a48dc91f5014a5c8)
- Virginia Beach: [VBTrees](https://geo.vbgov.com/mapservices/rest/services/Parks_and_Recreation/VBTrees/MapServer)

</details>

<details>
<summary>Maryland</summary>

- Annapolis: [Tree Inventory](https://pg-cloud.com/AnnapolisMD/)
- Baltimore: [Open Baltimore](https://data.baltimorecity.gov/)
- Gaithersburg: [Street Trees View](https://www.arcgis.com/home/item.html?id=8450e6c3992d4e8e9d0f3df4fd2722dd)
- Garrett Park: [Garrett Park Tree Inventory](https://www.arcgis.com/home/item.html?id=f487ba0469f74cc098e8dc6f37736073)

</details>

<details>
<summary>North Carolina</summary>

- Durham: [Trees & Planting Sites](https://experience.arcgis.com/experience/b3e98203c9fe458896f3699042d17617/)

</details>

<details>
<summary>New Jersey</summary>

- Jersey City: [Urban Forests](https://www.jerseycitynj.gov/cityhall/infrastructure/division_of_sustainability/urbanforests)
- Morristown: [Legacy Trees 2021](https://services.arcgis.com/xhDV83hFoiDFnMbw/arcgis/rest/services/Legacy_Trees_2021/FeatureServer)

</details>

<details>
<summary>Pennsylvania</summary>

- Meadville: [Trees View](https://www.arcgis.com/home/item.html?id=90b39f1a1a044eec9ea590ff48339e64)
- Philadelphia: [PPR Tree Inventory 2025](https://metadata.phila.gov/#home/datasetdetails/57a0e1d5aa8882104134830e/representationdetails/690a4183ef9cba032bd11d00/)
- Pittsburgh: [TreeKeeper Inventory](https://pittsburghpa.treekeepersoftware.com/)

</details>

<details>
<summary>Massachusetts</summary>

- Belmont: [TreeKeeper Inventory](https://belmontma.treekeepersoftware.com/)
- Boston: [BPRD Trees](https://data.boston.gov/dataset/bprd-trees)
- Brookline: [Brookline Tree Inventory](https://www.arcgis.com/home/item.html?id=4500c14f85d846d6924c7f8cb532763f)
- Cambridge: [Street Trees](https://www.cambridgema.gov/GIS/gisdatadictionary/Environmental/ENVIRONMENTAL_StreetTrees)
- Dedham: [Tree Inventory](https://gis.dedham-ma.gov/arcgis/rest/services/public/TreeInventory/MapServer)
- Longmeadow: [Tree Inv noedit](https://www.arcgis.com/home/item.html?id=202e5932c7d544288e2970b9f321948e)
- Lynn: [Tree Inventory](https://www.arcgis.com/home/item.html?id=c1d88b9e29594016898fb9d2699067cc)
- Medford: [Forestry](https://www.medfordma.org/departments/forestry)
- New Bedford: [NewBedfordTreeInventory2023](https://www.arcgis.com/home/item.html?id=c80392f7b4bf4a2ebd5617776d508721)
- Newton: [TreeKeeper Inventory](https://newtonma.treekeepersoftware.com/)
- Somerville: [TreeKeeper Inventory](https://somervillema.treekeepersoftware.com/)
- Worcester: [TreeKeeper Inventory](https://worcesterma.treekeepersoftware.com/)

</details>

<details>
<summary>New Hampshire</summary>

- Manchester: [Manchester Trees 2022](https://www.arcgis.com/home/item.html?id=880d1fd2f9404a0381814565f5ee4cd7)

</details>

<details>
<summary>Rhode Island</summary>

- Providence: [Providence Tree Dataset](https://data.providenceri.gov/Neighborhoods/Providence-Tree-Dataset/b77h-59tz)

</details>

<details>
<summary>Vermont</summary>

- Shelburne: [Municipal Tree Inventory](https://www.arcgis.com/home/item.html?id=2d0401a0ac9d449784ed9b31daabed60)
- Middlebury: [Municipal Tree Inventory](https://www.arcgis.com/home/item.html?id=2d0401a0ac9d449784ed9b31daabed60)
- Winooski: [Municipal Tree Inventory](https://www.arcgis.com/home/item.html?id=2d0401a0ac9d449784ed9b31daabed60)
- Northfield: [Municipal Tree Inventory](https://www.arcgis.com/home/item.html?id=2d0401a0ac9d449784ed9b31daabed60)
- Milton: [Municipal Tree Inventory](https://www.arcgis.com/home/item.html?id=2d0401a0ac9d449784ed9b31daabed60)
- Hinesburg: [Municipal Tree Inventory](https://www.arcgis.com/home/item.html?id=2d0401a0ac9d449784ed9b31daabed60)
- Essex: [Municipal Tree Inventory](https://www.arcgis.com/home/item.html?id=2d0401a0ac9d449784ed9b31daabed60)
- South Burlington: [Municipal Tree Inventory](https://www.arcgis.com/home/item.html?id=2d0401a0ac9d449784ed9b31daabed60)
- Colchester: [Municipal Tree Inventory](https://www.arcgis.com/home/item.html?id=2d0401a0ac9d449784ed9b31daabed60)
- Randolph: [Municipal Tree Inventory](https://www.arcgis.com/home/item.html?id=2d0401a0ac9d449784ed9b31daabed60)

</details>

<details>
<summary>Texas</summary>

- Austin: [Tree Inventory](https://data.austintexas.gov/Environment/Tree-Inventory/wrik-xasw)
- Dallas: [Dallas Public Tree Inventory](https://dallas.gov/projects/forestry/Pages/inventory.aspx)
- Houston: [City of Houston Tree Inventory - PUBLIC](https://www.arcgis.com/home/item.html?id=ef3851fa482d41d49cf2d82a399919f5)

</details>

<details>
<summary>Colorado</summary>

- Denver: [Public Tree Inventory](https://opendata-geospatialdenver.hub.arcgis.com/datasets/public-tree-inventory)

</details>

<details>
<summary>Nevada</summary>

- Las Vegas: [CLV Tree Sites](https://services1.arcgis.com/F1v0ufATbBQScMtY/ArcGIS/rest/services/CLV_Tree_Sites/FeatureServer)

</details>

<details>
<summary>Utah</summary>

- Salt Lake City: [Urban Forestry Inventory](https://www.slc.gov/parks/urban-forestry/)

</details>

<details>
<summary>Alberta</summary>

- Calgary: [Public Trees](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/arcgis/rest/services/Public_Trees/FeatureServer/0)
- Edmonton: [Boulevard & Open Space Trees](https://data.edmonton.ca/Environmental-Services/Boulevard-Open-Space-Trees/eecg-fc54)
- St. Albert: [Tree Inventory](https://services1.arcgis.com/fyyY0cNXvmUWvX1x/arcgis/rest/services/Tree_Inventory/FeatureServer/0)
- Chestermere: [Trees Open](https://gis.chestermere.ca/serversite/rest/services/Trees_Open/FeatureServer/0)
- Okotoks: [Tree Inventory](https://services3.arcgis.com/Fl5sQFvYY7w7mPQj/arcgis/rest/services/Tree_Inventory/FeatureServer)
- Lethbridge: [Trees](https://gis.lethbridge.ca/gisopendata/rest/services/OpenData/odl_trees/MapServer/0)
- Medicine Hat: [Tree Inventory](https://gis.medicinehat.ca/arcgis/rest/services/Parks/Trees_RFP_Tree_Inventory_Collection_FS4/MapServer)
- Red Deer: [PARK_Trees_inservice](https://arcgis.reddeer.ca/arcgis/rest/services/CoRD_View_Layers/PARK_Trees_inservice/MapServer)
- Airdrie: [Edible Trees](https://map.airdrie.ca:6443/arcgis/rest/services/pk_EdibleTrees_ap/MapServer/0)

</details>

<details>
<summary>Ontario</summary>

- Ajax: [Town Owned Trees](https://ajaxmaps.ajax.ca/gisernie/rest/services/Public/Ajax_Open_Data/MapServer/8)
- Barrie: [Tree](https://gispublic.barrie.ca/arcgis/rest/services/Open_Data/FacilitiesStreets/MapServer/37)
- Burlington: [City Owned Trees](https://www.arcgis.com/home/item.html?id=41412ef3188942c7abbe14035004273d)
- Cambridge ON: [Street Trees](https://www.arcgis.com/home/item.html?id=93f699f0aeba49f1acb582cf26b90ed7)
- Guelph: [TreeInventory](https://servicesdev.arcgis.com/LkFyxb9zDq7vAOAm/ArcGIS/rest/services/TreeInventory_Guelph/FeatureServer)
- Halton Hills: [Tree](https://map.haltonhills.ca/awse/rest/services/eP/MapServer/5)
- Hamilton: [Public Tree Inventory](https://open.hamilton.ca/datasets/08e50c6cbb2545b4897d613a817fa4d4_0/explore)
- Kingston: [City Owned Trees](https://utility.arcgis.com/usrsvcs/servers/511fd5299053486daf48c6466332320c/rest/services/Eng/City_Owned_Trees/FeatureServer/0)
- Kitchener: [Forestry Gallery](https://open-kitchenergis.opendata.arcgis.com/pages/forestry-gallery)
- London: [Public_TreeInventory](https://maps.london.ca/arcgisa/rest/services/Public_TreeInventory/MapServer)
- Mississauga: [City trees](https://mississauga.ca/services-and-programs/forestry-and-environment/trees/)
- Niagara Falls: [Niagara Falls Trees Inventory](https://open.niagarafalls.ca/datasets/niagarafalls::niagara-falls-trees-inventory)
- Oakville: [Public tree inventory](https://www.oakville.ca/home-environment/trees-woodlands/public-tree-inventory/)
- Ottawa: [Canopy cover and tree inventory](https://ottawa.ca/en/canopy-cover-and-tree-inventory)
- Peterborough: [Tree Inventory & EAB Status in the City of Peterborough](https://ptbo.maps.arcgis.com/apps/webappviewer/index.html?id=be8a9500cdca44af86860046e651cb96)
- Tecumseh: [Trees Municipal](https://gisweb.tecumseh.ca/arcgis/rest/services/GeocortexEssentialsMapping/MapServer/75)
- Thunder Bay: [City of Thunder Bay Trees](https://services5.arcgis.com/h9xShea49ZANgOtx/arcgis/rest/services/City_of_Thunder_Bay_Trees/FeatureServer)
- Toronto: [Street Tree Data](https://open.toronto.ca/dataset/street-tree-data/)
- Waterloo: [Waterloo Street Trees](https://services1.arcgis.com/DwLTn0u9VBSZvUPe/ArcGIS/rest/services/Waterloo_Street_Trees/FeatureServer)
- Welland: [Welland Trees](https://open.welland.ca/datasets/welland-trees)
- Whitby: [Whitby Tree Inventory](https://whitby.maps.arcgis.com/apps/instant/sidebar/index.html?appid=3e192ad13b7940b98684e8dadaa94c54)
- Windsor: [City Trees In Park](https://mappmycity.ca/arcgis/rest/services/OpenDataServices/ParksEnvironment/MapServer/0), [City Trees In Right Of Way](https://mappmycity.ca/arcgis/rest/services/OpenDataServices/ParksEnvironment/MapServer/1)

</details>

<details>
<summary>Quebec</summary>

- Gatineau: [Remarkable Trees](https://ncc-ccn.gc.ca/places/remarkable-trees)
- Montreal: [Arbres publics sur le territoire de la Ville](https://donnees.montreal.ca/fr/dataset/arbres)

</details>

<details>
<summary>Manitoba</summary>

- Winnipeg: [Tree Inventory](https://data.winnipeg.ca/Parks/Tree-Inventory-Map/hfwk-jp4h)

</details>

<details>
<summary>New Brunswick</summary>

- Fredericton: [Tree Inventory](https://services2.arcgis.com/iLWAxhpxafhOza2U/arcgis/rest/services/Fredericton__FREDERICTON_SCHIFKEE__TreeInventory/FeatureServer/1)
- Moncton: [Trees](https://services1.arcgis.com/E26PuSoie2Y7bbyI/arcgis/rest/services/Trees/FeatureServer/0)

</details>

<details>
<summary>Nova Scotia</summary>

- Halifax: [Public Trees](https://data-hrm.hub.arcgis.com/datasets/33a4e9b6c7e9439abcd2b20ac50c5a4d_0/explore)

</details>

<details>
<summary>Saskatchewan</summary>

- Regina: [TreeWebApp](https://opengis.regina.ca/arcgis/rest/services/CGISViewer/TreeWebApp/MapServer)
- Saskatoon: [Tree Inventory](https://www.saskatoon.ca/treeinventory)

</details>

<details>
<summary>Oregon</summary>

- Portland: [Street Tree Inventory - Active Records](https://www.portlandmaps.com/od/rest/services/COP_OpenData_Environment/MapServer/1415)

</details>

<details>
<summary>California</summary>

- Burlingame: [City Street Tree Inventory](https://www.burlingame.org/466/Trees-Urban-Forest)
- Anaheim: [Anaheim All Layers Tree Inventory](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/WebMap_Anaheim_AllLayers_WFL1/FeatureServer/0)
- Azusa: [City of Azusa Tree Inventory Benefits](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/City_of_Azusa_Tree_Inventory_Benefits_WFL1/FeatureServer/0)
- Bell: [City of Bell Tree Inventory Benefits](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/City_of_Bell_Tree_Inventory_Benefits_WFL1/FeatureServer/0)
- Beverly Hills: [Trees of Beverly Hills](https://services5.arcgis.com/7CXE3aevo18HlHBC/arcgis/rest/services/Trees_of_Beverly_Hills/FeatureServer/0)
- Concord: [Tree Inventory](https://www.cityofconcord.org/1249/Tree-Inventory)
- Costa Mesa: [Costa Mesa Tree Benefits](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Costa_Mesa_TreeBenefits_WFL1/FeatureServer/0)
- Palo Alto: [City of Palo Alto Open GIS](https://opengis.cityofpaloalto.org/)
- Berkeley: [Tree_Berkeley20191107](https://www.arcgis.com/home/item.html?id=88829f4ae7254b5280732e88e65e6df5)
- Cupertino: [Cupertino Open Data GIS](https://gis-cupertino.opendata.arcgis.com/)
- El Segundo: [El Segundo Tree Inventory](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/TreeInvElSegundo_Public/FeatureServer/0)
- Fontana: [Fontana i-Tree Inventory](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Fontana_iTree_Inv/FeatureServer/0)
- Fremont: [Tree Inventory / Tree Value](https://www.fremont.gov/government/departments/maintenance-operations/urban-forestry/tree-inventory-tree-value)
- Fullerton: [Fullerton Tree Benefits](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Fullerton_Tree_Benefits_WFL1/FeatureServer/0)
- Gilroy: [Tree Inventories in Santa Clara County](https://www.arcgis.com/home/item.html?id=58f9d735c5b94915ba5374c82415a26f)
- Irvine: [City Trees](https://gis.cityofirvine.org/arcgis/rest/services/City_Landscape/MapServer/0)
- La Canada Flintridge: [Homepage Inventory](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/LACanadaFlintridge_HomepageInventory_WFL1/FeatureServer/0)
- Los Angeles: [Tree Inventory and Maintenance](https://streetsla.lacity.org/tree-inventory-and-maintenance)
- Los Gatos: [Tree Inventories in Santa Clara County](https://www.arcgis.com/home/item.html?id=58f9d735c5b94915ba5374c82415a26f)
- Maywood: [Maywood i-Tree Inventory](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Maywood_iTree_Inventory_WFL1/FeatureServer/0)
- Mountain View: [Trees](https://services8.arcgis.com/A76GjgcBUTTcwFGS/arcgis/rest/services/Heritage_Trees_JM/FeatureServer/10)
- Milpitas: [Trees RO](https://services8.arcgis.com/OPmRdssd8jj0bT5H/arcgis/rest/services/Trees_RO/FeatureServer/0)
- Monterey Park: [i-Tree Benefits Summary](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Monterey_Park_iTree_Benefits_Summary_WFL1/FeatureServer/0)
- Morgan Hill: [Tree Inventories in Santa Clara County](https://www.arcgis.com/home/item.html?id=58f9d735c5b94915ba5374c82415a26f)
- Newport Beach: [Tree Inventory Dashboard](https://nbgis.newportbeachca.gov/gispub/Dashboards/TreeInventoryDash.htm)
- Oakland: [Oakland Street Trees](https://data.oaklandca.gov/Environmental/Oakland-Street-Trees/4jcx-enxf)
- Oxnard: [Trees](https://maps.oxnard.org/arcgis/rest/services/ParksLayers/MapServer/1)
- Pasadena: [Street ROW Trees](https://services2.arcgis.com/zNjnZafDYCAJAbN0/arcgis/rest/services/Street_ROW_Trees/FeatureServer/0)
- Pomona: [CityOfPomona i-Tree Benefits Canopy Cover](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/CityOfPomona_iTreeBenefits_CanopyCover_WFL1/FeatureServer/0)
- Rancho Cucamonga: [Rancho Cucamonga Tree Benefits](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/RanchoCucamonga_TreeBenefits_WFL1/FeatureServer/0)
- Rancho Palos Verdes: [GIS Services](https://www.rpvca.gov/869/GIS-Services)
- Riverside: [CityOfRiverside i-Tree Benefits](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/CityOfRiverside_iTreeBenefits_WFL1/FeatureServer/0)
- Salinas: [Tree Inventory](https://cityofsalinas.opendatasoft.com/explore/dataset/tree-inventory/)
- Sacramento: [City Maintained Trees](https://data.cityofsacramento.org/datasets/b9b716e09b5048179ab648bb4518452b_0/explore)
- San Dimas: [City Owned Trees](https://files.sandimasca.gov/departments/parks_and_recreation/trees/index.php)
- Santa Clarita: [City of Santa Clarita i-Tree Benefits Canopy Cover](https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/City_of_Santa_Clarita_iTreeBenefits_CanopyCover_WFL1/FeatureServer/0)
- Santa Monica: [Trees](https://gis.santamonica.gov/server/rest/services/Trees/FeatureServer/0)
- San Diego: [Trees (Street Trees)](https://webmaps.sandiego.gov/arcgis/rest/services/DSD/Environment/MapServer/20)
- San Fernando: [San Fernando CAL FIRE Tree Layer](https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/San_Fernando_CAL_FIRE_Tree_Layer_view/FeatureServer/0)
- San Francisco: [Street Tree List](https://data.sfgov.org/City-Infrastructure/Street-Tree-List/tkzw-k3nq)
- San Jose: [Street Tree](https://data.sanjoseca.gov/dataset/street-tree)
- San Mateo: [Street Trees](https://www.arcgis.com/home/item.html?id=67c8b57d2d91459c9f951df9de961a06)
- San Rafael: [Trees](https://www.arcgis.com/home/item.html?id=8a236959df6f438ba38bdf5db85ce54a)
- Saratoga: [Tree Inventories in Santa Clara County](https://www.arcgis.com/home/item.html?id=58f9d735c5b94915ba5374c82415a26f)
- South San Francisco: [City Trees](https://www.ssfca.gov/Departments/Parks-Recreation/Divisions/Parks-Division/Trees)
- Sunnyvale: [Tree Inventories in Santa Clara County](https://www.arcgis.com/home/item.html?id=58f9d735c5b94915ba5374c82415a26f)
- West Sacramento: [Tree Inventory](https://gis.cityofwestsacramento.org/server/rest/services/Tree_Inventory_MIL1/MapServer/0)
- West Hollywood: [West Hollywood Public Tree Inventory](https://services6.arcgis.com/hAiivxtZsKcvN4Sa/arcgis/rest/services/Public_Tree_Inventory_WFL1/FeatureServer/0)

</details>

<details>
<summary>Washington, DC</summary>

- Washington DC: [Urban Tree Canopy](https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Urban_Tree_Canopy/MapServer/23)

</details>

<details>
<summary>British Columbia</summary>

- Abbotsford: [Tree Management](https://www.abbotsford.ca/tree-management)
- Kamloops: [TreeSite](https://maps.kamloops.ca/arcgis/rest/services/OpenData/OpenDataParks/MapServer/12)
- Kelowna: [Tree Inventory](https://geoportal.kelowna.ca/arcgis/rest/services/ArcGISOnline/OpenData_Environment/MapServer/17)
- Maple Ridge: [Street Tree](https://geoservices.mapleridge.ca/server/rest/services/DataCatalog/Environment/MapServer/5)
- Nanaimo: [Urban Trees](https://nanmap.nanaimo.ca/Geocortex/Essentials/REST/sites/Nanaimo_Map/map/mapservices)
- New Westminster: [Tree Inventory (Active Trees)](https://services3.arcgis.com/A7O8YnTNtzRPIn7T/arcgis/rest/services/Tree_Inventory_(PROD)_4_view/FeatureServer)
- North Vancouver City: [Public Trees](https://www.cnv.org/Community-Environment/Trees/Public-Trees)
- North Vancouver District: [Street Trees](https://geoweb.dnv.org/data/)
- Penticton: [Trees](https://services1.arcgis.com/ZMQyarkhNAnn8lip/ArcGIS/rest/services/Parks_PRD/FeatureServer/1355)
- Prince George: [Trees](https://services2.arcgis.com/CnkB6jCzAsyli34z/arcgis/rest/services/OpenData_ParkData/FeatureServer/0)
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
- `public/data/trees.<region>.area-index.v2.json`
- `public/data/trees.<region>.area.<slug>.v2.geojson`
- `public/data/trees.<region>.area.<slug>.shard-###.v2.geojson` (for larger areas)
- `public/data/coverage.v1.geojson`
- `public/data/species-guide.v1.json`
- `public/data/jump-index.v1.json`
- `public/data/meta.v2.json`
- `public/data/unknown_scientific_names.v1.json`

### Local ETL Audit
- `data/normalized/trees_normalized.csv`

## Region Publishing
- Tree points are now published by `area + shard` for every region, not as region-wide GeoJSON files.
- Current regional groups:
  - `AB`
  - `AZ`
  - `BC`
  - `CA`
  - `CO`
  - `CT`
  - `DC`
  - `GA`
  - `IL`
  - `MA`
  - `MB`
  - `MD`
  - `MI`
  - `NB`
  - `NC`
  - `NH`
  - `NJ`
  - `NS`
  - `NV`
  - `NY`
  - `ON`
  - `WA`
  - `OR`
  - `PA`
  - `QC`
  - `RI`
  - `SK`
  - `TX`
  - `UT`
  - `VA`
  - `WI`
- Local-only ETL audit outputs such as `data/normalized/trees_normalized.csv` and `data/tmp/*` are not part of the GitHub export repo.
- `public/data/meta.v2.json` contains the region index, region bounds, species-count summaries, aggregate size metadata, and area-shard publish metadata for the full site, each region, and each published area.
- `public/data/jump-index.v1.json` provides lightweight `country -> state/province -> city/county` navigation bounds for the `Show -> Jump` workflow without coupling navigation to tree payload loading.
- All published tree-point files now follow the same area-shard contract:
  - `public/data/trees.<region>.area-index.v2.json`
  - `public/data/trees.<region>.area.<slug>.v2.geojson`
  - `public/data/trees.<region>.area.<slug>.shard-###.v2.geojson`
- If a full ETL run is blocked but current published region files are still available locally, refresh area-shard outputs with:
  - `python3 scripts/refresh_region_area_shards.py --data-dir public/data --region all`
- If coverage or gray-coverage rules changed without rebuilding all tree data, refresh coverage and bounds with:
  - `python3 scripts/refresh_coverage_metadata.py --data-dir public/data`
- Publish safety thresholds for each shard:
  - `target_split`: `>= 20 MiB raw`
  - `must_split`: `>= 25 MiB raw`
  - `hard_fail`: `>= 30 MiB raw`
- Region aggregate size is still tracked, but only as advisory scale metadata and not as a GitHub single-file risk.

## Docs
- Docs index: [docs/README.md](docs/README.md)
- Ops: [docs/ops/README.md](docs/ops/README.md)
- Architecture: [docs/architecture/README.md](docs/architecture/README.md)
- Strategy: [docs/strategy/README.md](docs/strategy/README.md)
- Research: [docs/research/README.md](docs/research/README.md)
- Public data interfaces: [docs/architecture/public-data-interfaces.md](docs/architecture/public-data-interfaces.md)
- Coverage tracker: [docs/research/city-coverage-tracker.md](docs/research/city-coverage-tracker.md)
- ETL methods: [docs/research/city-etl-methods.md](docs/research/city-etl-methods.md)
- GitHub sync policy: [docs/ops/github-sync-policy.md](docs/ops/github-sync-policy.md)
