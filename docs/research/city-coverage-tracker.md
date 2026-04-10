# City Coverage Tracker

Last updated: 2026-03-29 (America/Los_Angeles)

## Review Order Before Any City Task
1. Review `A2` first. Those cities are the highest publish priority.
2. If `A2` is empty, review `B` next. Those cities have official point-tree data, but a blocker still prevents product publish.
3. Review `C` only when planning gray coverage, source research, or longer-horizon backlog work.
4. Review `A1` when refreshing an existing city, debugging regressions, or comparing methods that already work.

## Classification Model
| Bucket | Meaning | Default Action |
|---|---|---|
| `A1` | Official public point-tree data exists, the 5 in-scope blossom groups are already publishable, and the city is already in product | Maintain, refresh, or reuse as a template |
| `A2` | Official public point-tree data exists, the 5 in-scope blossom groups are already publishable, but the city is not yet in product | Highest expansion priority |
| `B` | Official public point-tree data exists, but the current source is partial, blocked, or not yet stable enough to publish the 5 in-scope blossom groups | Fix blockers and promote to `A2` |
| `C` | No verified official public citywide point-tree dataset is currently usable, or the place is outside the current city workflow | Gray coverage, defer, or re-research later |

## A2 — Official Point-Tree Data Confirmed, In-Scope Trees Present, Not Yet Integrated
Current state: no cities are parked in `A2` right now.

## A1 — Official Point-Tree Data Confirmed, In-Scope Trees Present, Already Integrated
| Done | City | Included Trees | Boundary Rule | Notes |
|---|---|---:|---|---|
| ✅ | Burlington IA | 482 | Official jurisdiction boundary | Official City of Burlington, Iowa public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Portland ME | 759 | Official jurisdiction boundary | Official City of Portland public urban-forest ArcGIS layer integrated after clipping to the official Portland, Maine Census boundary |
| ✅ | Baton Rouge | 1,863 | Official jurisdiction boundary | Official City of Baton Rouge public tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Laramie | 1,503 | Official jurisdiction boundary | Official City of Laramie public ArcGIS street-tree, park-tree, and other-tree layers merged and clipped to the official jurisdiction boundary |
| ✅ | Brookings | 343 | Official jurisdiction boundary | Official South Dakota Department of Agriculture and Natural Resources public TreePlotter inventory integrated after clipping to the official Brookings boundary |
| ✅ | Morgantown | 222 | Official jurisdiction boundary | Official West Virginia University TreeScape ArcGIS layer integrated with the official Morgantown boundary |
| ✅ | Bozeman | 185 | Official jurisdiction boundary | Official City of Bozeman public arborist ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Fayetteville AR | 174 | Official jurisdiction boundary | Official University of Arkansas public arboretum ArcGIS layer integrated after clipping to the official Fayetteville, Arkansas boundary |
| ✅ | Oxford | 172 | Official jurisdiction boundary | Official University of Mississippi public TreePlotter inventory integrated via the public TreePlotter page and official Oxford boundary clipping |
| ✅ | Newark DE | 143 | Official jurisdiction boundary | Official City of Newark public parks tree ArcGIS layer integrated after clipping to the official Newark, Delaware boundary |
| ✅ | Juneau | 6 | Official jurisdiction boundary | Official City and Borough of Juneau public cemetery tree ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Honolulu | 1 | Official jurisdiction boundary | Official University of Hawaii at Manoa Campus Tree Finder ArcGIS layer integrated using attribute lon/lat plus the official Honolulu boundary |
| ✅ | Columbia | 1 | Official jurisdiction boundary | Clemson University official South Carolina Champion Tree Database integrated after clipping blossom-tree points to the official Columbia boundary |
| ✅ | Lincoln | 9,063 | Official jurisdiction boundary | Official City of Lincoln public trees ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Coeur d'Alene | 2,954 | Official jurisdiction boundary | Official Idaho Department of Lands public TreePlotter inventory integrated after clipping statewide inventory points to the official Coeur d'Alene boundary |
| ✅ | Fargo | 2,479 | Official jurisdiction boundary | Official City of Fargo public forestry ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Albuquerque | 1,907 | Official jurisdiction boundary | Official City of Albuquerque public TreePlotter inventory integrated via the public TreePlotter page and official jurisdiction boundary clipping |
| ✅ | Moorhead | 1,813 | Official jurisdiction boundary | Official City of Moorhead public TreePlotter inventory integrated via the public TreePlotter page and official jurisdiction boundary clipping |
| ✅ | Covington | 261 | Official jurisdiction boundary | Official City of Covington public tree-inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Grandview Heights | 266 | Official jurisdiction boundary | Official City of Grandview Heights public TreePlotter inventory integrated via the public TreePlotter page and official jurisdiction boundary clipping |
| ✅ | Auburn | 219 | Official jurisdiction boundary | Official City of Auburn public street-tree ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Tulsa | 104 | Official jurisdiction boundary | Official City of Tulsa public tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Andover | 3 | Official jurisdiction boundary | Official City of Andover public street-tree ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Seattle | 46,114 | Official jurisdiction boundary | Includes UW supplemental points; ornamental cherry keyword sweep rerun |
| ✅ | New York City | 40,685 | Official jurisdiction boundary | Official NYC Parks `2015 Street Tree Census - Tree Data` integrated from NYC Open Data; rows are limited to living trees before blossom filtering |
| ✅ | Albany | 2,394 | Official jurisdiction boundary | Official City of Albany public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Saratoga Springs | 586 | Official jurisdiction boundary | Official City of Saratoga Springs public TreePlotter inventory integrated via the public TreePlotter page and official jurisdiction boundary clipping |
| ✅ | Troy | 716 | Official jurisdiction boundary | Official City of Troy public TreePlotter inventory integrated via the public TreePlotter page and official jurisdiction boundary clipping |
| ✅ | Toronto | 36,302 | Official jurisdiction boundary | Official City of Toronto `Street Tree Data` CSV integrated from Toronto Open Data using the official municipal boundary shapefile |
| ✅ | Edmonton | 30,304 | Official jurisdiction boundary | Official City of Edmonton `Boulevard / Open Space Trees` SODA dataset integrated and clipped to the official Statistics Canada CSD boundary |
| ✅ | Philadelphia | 17,717 | Official jurisdiction boundary | Official Philadelphia Parks & Recreation `PPR Tree Inventory 2025` layer integrated from the city's ArcGIS/metadata catalog |
| ✅ | Montreal | 16,258 | Official jurisdiction boundary | Official Ville de Montréal `Arbres publics sur le territoire de la Ville` CSV integrated; official boundary is assembled from arrondissement polygons |
| ✅ | Ottawa | 12,913 | Official jurisdiction boundary | Official City of Ottawa `Tree Inventory / Inventaire des arbres` ArcGIS layer integrated with blossom-side server filtering and official city boundary |
| ✅ | Winnipeg | 12,444 | Official jurisdiction boundary | Official City of Winnipeg open-data `Tree Inventory` integrated from the public SODA dataset and clipped to the official Statistics Canada CSD boundary |
| ✅ | Hamilton | 7,288 | Official jurisdiction boundary | Official City of Hamilton `Public Tree Inventory` ArcGIS layer integrated after restricting to `STATUS = 'Existing'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | Regina | 5,982 | Official jurisdiction boundary | Official City of Regina public tree inventory ArcGIS layer integrated with the official Statistics Canada CSD boundary |
| ✅ | London | 4,708 | Official jurisdiction boundary | Official City of London `Status Active` tree inventory ArcGIS layer integrated with the official Statistics Canada CSD boundary |
| ✅ | Saskatoon | 4,279 | Official jurisdiction boundary | Official City of Saskatoon public tree inventory ArcGIS layer integrated after restricting to `Status = 1` and `Ownership = 1` and clipping to the official Statistics Canada CSD boundary |
| ✅ | Mississauga | 3,177 | Official jurisdiction boundary | Official City of Mississauga `City Owned Tree Inventory` ArcGIS layer integrated after restricting to the official city-maintained statuses and clipping to the official Statistics Canada CSD boundary |
| ✅ | Windsor | 3,045 | Official jurisdiction boundary | Official City of Windsor `City Trees In Park` + `City Trees In Right Of Way` ArcGIS layers integrated and clipped to the official Statistics Canada CSD boundary |
| ✅ | Red Deer | 2,565 | Official jurisdiction boundary | Official City of Red Deer `PARK_Trees_inservice` ArcGIS layer integrated with blossom-side filtering and the official Statistics Canada CSD boundary |
| ✅ | Cambridge ON | 1,940 | Official jurisdiction boundary | Official City of Cambridge, Ontario `Street Trees` open-data layer integrated after restricting to `STATUS = 'EXISTING'` |
| ✅ | Guelph | 1,706 | Official jurisdiction boundary | Official City of Guelph public tree inventory ArcGIS layer integrated with common-name blossom filtering and the official Statistics Canada CSD boundary |
| ✅ | Burlington | 1,621 | Official jurisdiction boundary | Official City of Burlington `City Owned Trees` ArcGIS layer integrated after restricting to `STATUS = 'Alive'` |
| ✅ | Oakville | 1,487 | Official jurisdiction boundary | Official Town of Oakville forestry ArcGIS layer integrated after parsing mixed common/scientific `SPECIES` text and restricting to `STATUS = 'EXISTING'` |
| ✅ | Kitchener | 1,213 | Official jurisdiction boundary | Official City of Kitchener tree inventory ArcGIS layer integrated after restricting to `STATUS = 'ACTIVE'` |
| ✅ | North Vancouver City | 1,098 | Official jurisdiction boundary | Official City of North Vancouver `City Trees` ArcGIS layer integrated and clipped to the official Statistics Canada CSD boundary |
| ✅ | Halifax | 1,022 | Official jurisdiction boundary | Official Halifax Regional Municipality `Public Trees` ArcGIS layer integrated after restricting to `OWNER = 'HRM'` and clipping to the official `NSPW HRM Service Exchange Boundary (2022)` polygon |
| ✅ | Peterborough | 531 | Official jurisdiction boundary | Official City of Peterborough public tree inventory ArcGIS app layer integrated after restricting to `STATUS = 'Active'` and `OWNERSHIP = 'City'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | Whitby | 468 | Official jurisdiction boundary | Official Town of Whitby public tree inventory ArcGIS layer integrated with the official Statistics Canada CSD boundary |
| ✅ | Waterloo | 378 | Official jurisdiction boundary | Official City of Waterloo public street-tree ArcGIS layer integrated after restricting to `STATUS = 'Existing'` |
| ✅ | Calgary | 41,914 | Official jurisdiction boundary | Official City of Calgary `Public Trees` ArcGIS layer integrated after restricting to `LIFE_CYCLE_STATUS = 'ACTIVE'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | St. Albert | 2,948 | Official jurisdiction boundary | Official City of St. Albert public tree inventory ArcGIS layer integrated with the official Statistics Canada CSD boundary |
| ✅ | Thunder Bay | 2,746 | Official jurisdiction boundary | Official City of Thunder Bay public trees ArcGIS layer integrated after restricting to `TREE_CYCLE = 'TREE'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | Lethbridge | 2,119 | Official jurisdiction boundary | Official City of Lethbridge public trees ArcGIS layer integrated after restricting to active rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Maple Ridge | 1,905 | Official jurisdiction boundary | Official City of Maple Ridge public street-tree ArcGIS layer integrated after restricting to `Status = 'Existing'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | Kamloops | 1,453 | Official jurisdiction boundary | Official City of Kamloops public parks tree ArcGIS layer integrated after restricting to `OWNERTYPE = 'PUBLIC'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | Kingston | 1,067 | Official jurisdiction boundary | Official City of Kingston `City Owned Trees` ArcGIS layer integrated after restricting to `OWNERSHIP = 'Municipal'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | Chestermere | 973 | Official jurisdiction boundary | Official City of Chestermere public trees ArcGIS layer integrated after restricting to active rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Okotoks | 940 | Official jurisdiction boundary | Official Town of Okotoks public tree inventory ArcGIS layer integrated after restricting to established rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Abbotsford | 938 | Official jurisdiction boundary | Official City of Abbotsford `Tree Inventory 2019` park + street ArcGIS layers integrated and clipped to the official Statistics Canada CSD boundary |
| ✅ | Ajax | 793 | Official jurisdiction boundary | Official Town of Ajax public town-owned trees ArcGIS layer integrated after restricting to `STATUS = 'TREE'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | Medicine Hat | 677 | Official jurisdiction boundary | Official City of Medicine Hat public tree inventory ArcGIS layer integrated after parsing dash-delimited botanical/common species text and clipping to the official Statistics Canada CSD boundary |
| ✅ | Nanaimo | 645 | Official jurisdiction boundary | Official City of Nanaimo public urban trees ArcGIS layer integrated with the official Statistics Canada CSD boundary |
| ✅ | Niagara Falls | 622 | Official jurisdiction boundary | Official City of Niagara Falls public tree inventory ArcGIS layer integrated after restricting to `AssetOwnership = 'CITY OF NIAGARA FALLS'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | Barrie | 417 | Official jurisdiction boundary | Official City of Barrie public tree ArcGIS layer integrated after restricting to `TREE_STATUS = 'ACTIVE'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | North Vancouver District | 394 | Official jurisdiction boundary | Official District of North Vancouver `Street Trees` downloadable shapefile integrated and clipped to the official Statistics Canada CSD boundary |
| ✅ | Fredericton | 391 | Official jurisdiction boundary | Official City of Fredericton public tree inventory ArcGIS layer integrated with the official Statistics Canada CSD boundary |
| ✅ | Halton Hills | 376 | Official jurisdiction boundary | Official Town of Halton Hills public tree ArcGIS layer integrated after mapping the published common/scientific field aliases and clipping to the official Statistics Canada CSD boundary |
| ✅ | Moncton | 354 | Official jurisdiction boundary | Official City of Moncton public trees ArcGIS layer integrated using the public `BOTNAME` blossom-code mapping and clipped to the official Statistics Canada CSD boundary |
| ✅ | Prince George | 350 | Official jurisdiction boundary | Official City of Prince George public trees ArcGIS layer integrated after restricting to active city-owned rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Tecumseh | 242 | Official jurisdiction boundary | Official Town of Tecumseh municipal trees ArcGIS layer integrated after excluding active `Boundary` rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Welland | 209 | Official jurisdiction boundary | Official City of Welland public trees ArcGIS layer integrated with the official Statistics Canada CSD boundary |
| ✅ | Kelowna | 146 | Official jurisdiction boundary | Official City of Kelowna public tree inventory ArcGIS layer integrated after restricting to active rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Airdrie | 73 | Official jurisdiction boundary | Official City of Airdrie public edible trees ArcGIS layer integrated after restricting to active blossom rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Penticton | 69 | Official jurisdiction boundary | Official City of Penticton public trees ArcGIS layer integrated after restricting to active rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Gatineau | 1 | Official jurisdiction boundary | Official National Capital Commission `Remarkable Trees` ArcGIS layer clipped to the official Gatineau Statistics Canada CSD boundary |
| ✅ | Langley Township | 2,900 | Official jurisdiction boundary | Official Township of Langley public tree inventory ArcGIS layer integrated after clipping to the official Metro Vancouver administrative boundary |
| ✅ | Grande Prairie | 2,034 | Official jurisdiction boundary | Official City of Grande Prairie park trees ArcGIS layer integrated after clipping to the official Statistics Canada CSD boundary |
| ✅ | Strathcona County | 1,128 | Official jurisdiction boundary | Official Strathcona County managed trees ArcGIS layer integrated after clipping to the official Statistics Canada CSD boundary |
| ✅ | Coquitlam | 641 | Official jurisdiction boundary | Official City of Coquitlam maintained trees ArcGIS layer integrated after clipping to the official jurisdiction boundary |
| ✅ | Charlottetown | 461 | Official jurisdiction boundary | Official City of Charlottetown `Tree Sites Public` ArcGIS layer integrated after clipping to the official Statistics Canada CSD boundary |
| ✅ | West Vancouver | 283 | Official jurisdiction boundary | Public District of West Vancouver tree-inventory planning ArcGIS layer clipped to the official Metro Vancouver administrative boundary |
| ✅ | Weyburn | 227 | Official jurisdiction boundary | Public Weyburn urban-forest tree inventory ArcGIS layer clipped to the official Statistics Canada CSD boundary |
| ✅ | Port Coquitlam | 205 | Official jurisdiction boundary | Official City of Port Coquitlam park + street tree ArcGIS layers merged and clipped to the official jurisdiction boundary |
| ✅ | Moose Jaw | 33 | Official jurisdiction boundary | Official City of Moose Jaw public trees ArcGIS layer clipped to the official Statistics Canada CSD boundary |
| ✅ | Saint John | 13 | Official jurisdiction boundary | Official City of Saint John `Urban Forestry Trees` ArcGIS layer clipped to the official Statistics Canada CSD boundary |
| ✅ | Quebec City | 8,879 | Official jurisdiction boundary | Official Ville de Quebec `Arbres repertories` GeoJSON integrated from Donnees Quebec and clipped to the official Statistics Canada CSD boundary |
| ✅ | Longueuil | 2,298 | Official jurisdiction boundary | Official Ville de Longueuil `Arbres` GeoJSON integrated from Donnees Quebec and clipped to the official Statistics Canada CSD boundary |
| ✅ | Saguenay | 1,627 | Official jurisdiction boundary | Official Ville de Saguenay tree-inventory GeoJSON integrated from Donnees Quebec and clipped to the official Statistics Canada CSD boundary |
| ✅ | Brampton | 1,238 | Official jurisdiction boundary | Official City of Brampton public tree inventory ArcGIS layer integrated after restricting to city-owned live-tree rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Leduc | 910 | Official jurisdiction boundary | Official City of Leduc public Cityworks trees layer integrated after restricting to active rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Vaughan | 609 | Official jurisdiction boundary | Official York Region `Street Trees` layer integrated after restricting to active `MUNICIPALITY = 'Vaughan'` rows and clipping to the official Vaughan Statistics Canada CSD boundary |
| ✅ | Repentigny | 529 | Official jurisdiction boundary | Official Ville de Repentigny `Arbres` GeoJSON integrated from Donnees Quebec and clipped to the official Statistics Canada CSD boundary |
| ✅ | Cornwall | 453 | Official jurisdiction boundary | Official City of Cornwall public tree inventory ArcGIS layer integrated after restricting to `Status = 'PRESENT'` and clipping to the official Statistics Canada CSD boundary |
| ✅ | Cobourg | 442 | Official jurisdiction boundary | Official Town of Cobourg virtual arboretum tree inventory integrated from the public ArcGIS service and clipped to the official Statistics Canada CSD boundary |
| ✅ | Orangeville | 99 | Official jurisdiction boundary | Official Town of Orangeville public street-tree inventory ArcGIS layer integrated after excluding removed rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | White Rock | 671 | Official jurisdiction boundary | Official City of White Rock `Trees` open-data map service integrated after excluding removed trees and clipping to the official Metro Vancouver administrative boundary |
| ✅ | Markham | 442 | Official jurisdiction boundary | Official York Region `Street Trees` layer integrated after restricting to active `MUNICIPALITY = 'Markham'` rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Port Moody | 275 | Official jurisdiction boundary | Official City of Port Moody `Street Trees Inventory` ArcGIS layer integrated after restricting to `STATUS = 'OPERATIONAL'` and `TYPE = 'Street Tree'` |
| ✅ | Richmond Hill | 199 | Official jurisdiction boundary | Official York Region `Street Trees` layer integrated after restricting to active `MUNICIPALITY = 'Richmond Hill'` rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Whitchurch-Stouffville | 180 | Official jurisdiction boundary | Official York Region `Street Trees` layer integrated after restricting to active `MUNICIPALITY = 'Whitchurch-Stouffville'` rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | King | 154 | Official jurisdiction boundary | Official York Region `Street Trees` layer integrated after restricting to active `MUNICIPALITY = 'King'` rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Aurora | 115 | Official jurisdiction boundary | Official York Region `Street Trees` layer integrated after restricting to active `MUNICIPALITY = 'Aurora'` rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Newmarket | 110 | Official jurisdiction boundary | Official York Region `Street Trees` layer integrated after restricting to active `MUNICIPALITY = 'Newmarket'` rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | East Gwillimbury | 102 | Official jurisdiction boundary | Official York Region `Street Trees` layer integrated after restricting to active `MUNICIPALITY = 'East Gwillimbury'` rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Georgina | 100 | Official jurisdiction boundary | Official York Region `Street Trees` layer integrated after restricting to active `MUNICIPALITY = 'Georgina'` rows and clipping to the official Statistics Canada CSD boundary |
| ✅ | Mesa | 25 | Official jurisdiction boundary | Official City of Mesa `Mesa AZ iTree Inventory` ArcGIS layer integrated from the city's tree canopy hub and clipped to the official jurisdiction boundary |
| ✅ | Tempe | 32 | Official jurisdiction boundary | Official City of Tempe tree inventory ArcGIS open-data layer integrated with the official jurisdiction boundary |
| ✅ | Johns Creek | 8 | Official jurisdiction boundary | Official City of Johns Creek public `Tree Inventory` ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Sandy Springs | 269 | Official jurisdiction boundary | Official City of Sandy Springs public tree-plantings ArcGIS layer integrated with server-side blossom filtering |
| ✅ | Weaverville | 6 | Official jurisdiction boundary | Official Town of Weaverville public tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Denton | 66 | Official jurisdiction boundary | Official University of North Texas public 2023 tree inventory integrated after clipping blossom rows to the official Denton boundary |
| ✅ | Atlanta | 1,051 | Official jurisdiction boundary | Official Georgia Tech public campus tree inventory integrated after clipping blossom rows to the official Atlanta boundary |
| ✅ | Waco | 68 | Official jurisdiction boundary | Official Baylor University public tree inventory integrated after clipping blossom rows to the official Waco boundary |
| ✅ | Eugene | 8,180 | Official jurisdiction boundary | Official City of Eugene public urban-forest ArcGIS layer integrated with server-side blossom filtering |
| ✅ | Corvallis | 1,359 | Official jurisdiction boundary | Official City of Corvallis public tree inventory ArcGIS layer integrated with server-side blossom filtering |
| ✅ | Chattanooga | 1,286 | Official jurisdiction boundary | Official City of Chattanooga public tree inventory ArcGIS layer integrated with server-side blossom filtering |
| ✅ | Nashville | 39 | Official jurisdiction boundary | Official Nashville public `Cherry Tree Planting Sites` ArcGIS web map integrated from the embedded featureCollection and official jurisdiction boundary |
| ✅ | University City | 299 | Official jurisdiction boundary | Official City of University City public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Brighton | 409 | Official jurisdiction boundary | Official City of Brighton public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Boulder | 3,147 | Official jurisdiction boundary | Official City of Boulder `Tree Inventory Open Data` ArcGIS layer integrated after restricting to `OWNEDBY = 'City'` and clipping to the official jurisdiction boundary |
| ✅ | Denver | 19,900 | Official jurisdiction boundary | Official City and County of Denver `Public Tree Inventory` ArcGIS layer integrated from the city open-data portal and official jurisdiction boundary |
| ✅ | Erie | 411 | Official jurisdiction boundary | Official Town of Erie public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Fort Collins | 4,265 | Official jurisdiction boundary | Official City of Fort Collins public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Longmont | 16 | Official jurisdiction boundary | Official City of Longmont public tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Wheat Ridge | 514 | Official jurisdiction boundary | Official City of Wheat Ridge public TreePlotter inventory integrated via the public TreePlotter page and official jurisdiction boundary clipping |
| ✅ | Cape Coral | 741 | Official jurisdiction boundary | Official City of Cape Coral public tree inventory ArcGIS layer integrated with server-side blossom filtering on `SPECIES` and clipped to the official jurisdiction boundary |
| ✅ | Tallahassee | 758 | Official jurisdiction boundary | Official City of Tallahassee public Cityworks tree inventory ArcGIS layer integrated after restricting to active city-owned rows and clipping to the official jurisdiction boundary |
| ✅ | West Palm Beach | 28 | Official jurisdiction boundary | Official City of West Palm Beach public trees ArcGIS layer integrated after restricting to `Status = 'Alive'` and clipping to the official jurisdiction boundary |
| ✅ | Winter Park | 944 | Official jurisdiction boundary | Official City of Winter Park public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Normal | 1,128 | Official jurisdiction boundary | Official Town of Normal public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Westchester | 108 | Official jurisdiction boundary | Official Village of Westchester public tree inventory ArcGIS layer integrated with server-side blossom filtering on `COMMON_NAME` and clipped to the official jurisdiction boundary |
| ✅ | Danville | 351 | Official jurisdiction boundary | Official City of Danville public tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Evanston | 1,093 | Official jurisdiction boundary | Official City of Evanston public trees ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | O'Fallon | 152 | Official jurisdiction boundary | Official City of O'Fallon public city tree ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Bloomington | 1,206 | Official jurisdiction boundary | Official City of Bloomington public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Pendleton | 170 | Official jurisdiction boundary | Official Town of Pendleton public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Valparaiso | 752 | Official jurisdiction boundary | Official City of Valparaiso public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Branson | 17 | Official jurisdiction boundary | Official City of Branson public trees ArcGIS layer integrated after restricting to `ACTIVE = 1` and clipping to the official jurisdiction boundary |
| ✅ | Brentwood | 184 | Official jurisdiction boundary | Official City of Brentwood public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Carmel | 935 | Official jurisdiction boundary | Official City of Carmel public tree inventory ArcGIS layer integrated with server-side blossom filtering on `COMM_NAME` and clipped to the official jurisdiction boundary |
| ✅ | Clarksville | 404 | Official jurisdiction boundary | Official City of Clarksville public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Ferndale | 496 | Official jurisdiction boundary | Official City of Ferndale public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Kalamazoo | 1,564 | Official jurisdiction boundary | Official City of Kalamazoo public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Ann Arbor | 3,756 | Official jurisdiction boundary | Official City of Ann Arbor public street tree ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Dearborn Heights | 2 | Official jurisdiction boundary | Official City of Dearborn Heights public tree record ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | East Lansing | 521 | Official jurisdiction boundary | Official City of East Lansing public tree status ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Grand Rapids | 13 | Official jurisdiction boundary | Official City of Grand Rapids public street-tree ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Madison | 3,561 | Official jurisdiction boundary | Official City of Madison public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Franklin | 87 | Official jurisdiction boundary | Official Milwaukee County public tree viewer clipped to the official Franklin jurisdiction boundary |
| ✅ | Milwaukee | 680 | Official jurisdiction boundary | Official Milwaukee County public tree viewer clipped to the official Milwaukee jurisdiction boundary |
| ✅ | Wauwatosa | 77 | Official jurisdiction boundary | Official Milwaukee County public tree viewer clipped to the official Wauwatosa jurisdiction boundary |
| ✅ | Maitland | 202 | Official jurisdiction boundary | Official City of Maitland public tree inventory ArcGIS layer integrated with server-side blossom filtering on `COMMON` and clipped to the official jurisdiction boundary |
| ✅ | St. Louis | 4,602 | Official jurisdiction boundary | Official City of St. Louis `City Street Trees` open-data layer integrated after excluding `CONDITION = 'N/A'` rows and clipping to the official jurisdiction boundary |
| ✅ | Michigan City | 526 | Official jurisdiction boundary | Official City of Michigan City public tree inventory ArcGIS layer integrated with server-side blossom filtering on `COMMON_NAME` and clipped to the official jurisdiction boundary |
| ✅ | Springfield | 603 | Official jurisdiction boundary | Official City of Springfield public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Westfield | 1,462 | Official jurisdiction boundary | Official City of Westfield public tree inventory ArcGIS layer integrated with server-side blossom filtering on `Tree` and clipped to the official jurisdiction boundary |
| ✅ | Boston | 4,488 | Official jurisdiction boundary | Official Analyze Boston `BPRD Trees` download integrated; includes both street and park trees published by Boston Parks and Recreation |
| ✅ | Belmont | 221 | Official jurisdiction boundary | Official Town of Belmont public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Brookline | 1,064 | Official jurisdiction boundary | Official Town of Brookline public tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Dedham | 425 | Official jurisdiction boundary | Official Town of Dedham public tree inventory ArcGIS layer integrated with server-side blossom filtering on `Species_bot` / `Species_com` |
| ✅ | Longmeadow | 404 | Official jurisdiction boundary | Official Town of Longmeadow public tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Newton | 2,471 | Official jurisdiction boundary | Official City of Newton public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Pittsburgh | 3,691 | Official jurisdiction boundary | Official public Pittsburgh TreeKeeper inventory domain integrated; blossom names are parsed from `SITE_ATTR6` |
| ✅ | Somerville | 338 | Official jurisdiction boundary | Official City of Somerville public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Worcester | 300 | Official jurisdiction boundary | Official City of Worcester public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Jersey City | 2,148 | Official jurisdiction boundary | Public Jersey City tree inventory service integrated from the city-referenced Urban Forests materials and official jurisdiction boundary |
| ✅ | Cambridge (MA) | 1,954 | Official jurisdiction boundary | Official City of Cambridge `Street Trees` shapefile integrated; only current `SiteType = Tree` rows are included |
| ✅ | Groton | 100 | Official jurisdiction boundary | Official Town of Groton public tree inventory ArcGIS service integrated using the official town boundary from the Census county subdivision rather than the smaller Groton city place |
| ✅ | Gaithersburg | 1,051 | Official jurisdiction boundary | Official City of Gaithersburg `Street Trees View` ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Garrett Park | 109 | Official jurisdiction boundary | Official Town of Garrett Park tree inventory integrated from the published ArcGIS web map featureCollection and clipped to the official jurisdiction boundary |
| ✅ | West Hartford | 210 | Official jurisdiction boundary | Official Town of West Hartford public TreePlotter inventory integrated via the public TreePlotter page and official jurisdiction boundary clipping |
| ✅ | Baltimore | 1,920 | Official jurisdiction boundary | Official Baltimore city forestry tree layer integrated from `gis.baltimorecity.gov`; botanical names come from `SPP` |
| ✅ | Annapolis | 260 | Official jurisdiction boundary | Official City of Annapolis public TreePlotter inventory integrated via the public TreePlotter page and official jurisdiction boundary clipping |
| ✅ | Arlington | 1,882 | Official jurisdiction boundary | Official Arlington County `DPR Trees` layer integrated using the official county-equivalent jurisdiction boundary |
| ✅ | Fairfax | 481 | Official jurisdiction boundary | Official City of Fairfax public TreePlotter inventory integrated via the public TreePlotter page and official jurisdiction boundary clipping |
| ✅ | Norfolk | 1,615 | Official jurisdiction boundary | Official City of Norfolk open-data `City Tree Inventory` integrated with the official jurisdiction boundary and coordinate fallback from `latitude_longitude_point` |
| ✅ | Providence | 1,567 | Official jurisdiction boundary | Official City of Providence open-data `Providence Tree Dataset` integrated with the official jurisdiction boundary |
| ✅ | Shelburne | 232 | Official jurisdiction boundary | Official Vermont ANR `Municipal Tree Inventory` ArcGIS layer integrated with `TOWN = 'SHELBURNE'` and clipped to the official jurisdiction boundary |
| ✅ | Middlebury | 155 | Official jurisdiction boundary | Official Vermont ANR `Municipal Tree Inventory` ArcGIS layer integrated with `TOWN = 'MIDDLEBURY'` and clipped to the official jurisdiction boundary |
| ✅ | Winooski | 99 | Official jurisdiction boundary | Official Vermont ANR `Municipal Tree Inventory` ArcGIS layer integrated with `TOWN = 'WINOOSKI'` and clipped to the official jurisdiction boundary |
| ✅ | Northfield | 85 | Official jurisdiction boundary | Official Vermont ANR `Municipal Tree Inventory` ArcGIS layer integrated with `TOWN = 'NORTHFIELD'` and clipped to the official jurisdiction boundary |
| ✅ | Milton | 70 | Official jurisdiction boundary | Official Vermont ANR `Municipal Tree Inventory` ArcGIS layer integrated with `TOWN = 'MILTON'` and clipped to the official jurisdiction boundary |
| ✅ | Hinesburg | 68 | Official jurisdiction boundary | Official Vermont ANR `Municipal Tree Inventory` ArcGIS layer integrated with `TOWN = 'HINESBURG'` and clipped to the official jurisdiction boundary |
| ✅ | Essex | 57 | Official jurisdiction boundary | Official Vermont ANR `Municipal Tree Inventory` ArcGIS layer integrated with `TOWN = 'ESSEX'` and clipped to the official jurisdiction boundary |
| ✅ | South Burlington | 56 | Official jurisdiction boundary | Official Vermont ANR `Municipal Tree Inventory` ArcGIS layer integrated with `TOWN = 'SOUTH BURLINGTON'` and clipped to the official jurisdiction boundary |
| ✅ | Colchester | 51 | Official jurisdiction boundary | Official Vermont ANR `Municipal Tree Inventory` ArcGIS layer integrated with `TOWN = 'COLCHESTER'` and clipped to the official jurisdiction boundary |
| ✅ | Randolph | 37 | Official jurisdiction boundary | Official Vermont ANR `Municipal Tree Inventory` ArcGIS layer integrated with `TOWN = 'RANDOLPH'` and clipped to the official jurisdiction boundary |
| ✅ | Durham | 1,301 | Official jurisdiction boundary | Official City of Durham `Trees & Planting Sites` ArcGIS layer integrated after restricting to `present = Tree` and clipping to the official jurisdiction boundary |
| ✅ | Fredericksburg | 975 | Official jurisdiction boundary | Official City of Fredericksburg public tree inventory ArcGIS layer integrated after restricting to `spacestatus = Planted` |
| ✅ | Richmond | 2,099 | Official jurisdiction boundary | Official City of Richmond, Virginia public tree inventory ArcGIS layer integrated with `Status = In Service` and server-side botanical blossom filtering on `SPP` |
| ✅ | Virginia Beach | 1,629 | Official jurisdiction boundary | Official City of Virginia Beach `VBTrees` inventory integrated after excluding `Removed`, `Proposed`, `Schedule`, and `Hold` rows |
| ✅ | Meadville | 504 | Official jurisdiction boundary | Official City of Meadville public tree inventory ArcGIS layer integrated after restricting to live trees and clipping to the official jurisdiction boundary |
| ✅ | Charlottesville | 310 | Official jurisdiction boundary | Official City of Charlottesville open-data tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Newport News | 35 | Official jurisdiction boundary | Official City of Newport News public reviewed-tree ArcGIS inventory integrated from the `Public Trees` layer |
| ✅ | Princeton | 1,310 | Official jurisdiction boundary | Official Princeton public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Millburn | 1,133 | Official jurisdiction boundary | Official Millburn public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Hoboken | 397 | Official jurisdiction boundary | Official City of Hoboken public tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Morristown | 10 | Official jurisdiction boundary | Official Morristown public tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Dumont | 284 | Official jurisdiction boundary | Official Dumont public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Lynn | 4 | Official jurisdiction boundary | Official City of Lynn public tree inventory ArcGIS layer integrated after restricting to `STATUS = 'alive'` and clipping to the official jurisdiction boundary |
| ✅ | New Bedford | 678 | Official jurisdiction boundary | Public New Bedford 2023 tree inventory ArcGIS layer integrated with the official jurisdiction boundary and `Longitude` / `Latitude` fallback |
| ✅ | Medford | 250 | Official jurisdiction boundary | Public Medford tree inventory ArcGIS layer referenced by the official City of Medford Forestry materials and clipped to the official jurisdiction boundary |
| ✅ | Manchester | 1 | Official jurisdiction boundary | Official City of Manchester public Parks and Recreation tree inventory ArcGIS layer integrated with the official jurisdiction boundary; current official source publishes one in-scope blossom tree |
| ✅ | Westwood | 192 | Official jurisdiction boundary | Official Westwood public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Rutherford | 126 | Official jurisdiction boundary | Official Rutherford public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | River Edge | 62 | Official jurisdiction boundary | Official River Edge public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Austin | 675 | Official jurisdiction boundary | Official City of Austin `Tree Inventory` Socrata dataset integrated; invalid projected coordinate rows in the blossom subset are repaired by falling back to the dataset `geometry` point before publish |
| ✅ | Montclair | 56 | Official jurisdiction boundary | Official Township of Montclair public tree inventory ArcGIS layer integrated with the official jurisdiction boundary |
| ✅ | Dallas | 53 | Official jurisdiction boundary | Official City of Dallas public TreeKeeper inventory integrated from the city forestry page; blossom rows are filtered from `SITE_ATTR1` and coordinates come from the public lon/lat fields |
| ✅ | Newark | 28 | Official jurisdiction boundary | Official Newark public TreeKeeper inventory integrated with the official jurisdiction boundary |
| ✅ | Houston | 8,623 | Official jurisdiction boundary | Official City of Houston `COH Urban Forestry Trees` ArcGIS layer integrated from the city's public tree inventory web map and official jurisdiction boundary |
| ✅ | Las Vegas | 115 | Official jurisdiction boundary | Official City of Las Vegas `CLV Tree Sites` ArcGIS layer integrated using server-side blossom filtering on `SPP_BOT` / `SPP_COM` |
| ✅ | Boulder City | 3 | Official jurisdiction boundary | Official Nevada Division of Forestry `Clark County Schools Tree Inventory` blossom rows clipped to the official Boulder City boundary |
| ✅ | Henderson | 7 | Official jurisdiction boundary | Official Nevada Division of Forestry `Clark County Schools Tree Inventory` blossom rows clipped to the official Henderson boundary |
| ✅ | North Las Vegas | 16 | Official jurisdiction boundary | Official Nevada Division of Forestry `Clark County Schools Tree Inventory` blossom rows clipped to the official North Las Vegas boundary |
| ✅ | Salt Lake City | 7,810 | Official jurisdiction boundary | Official Salt Lake City Public Lands `Urban Forestry Inventory` ArcGIS layer integrated after excluding vacant sites and classifying `SPP` values |
| ✅ | Lehi | 153 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for the City of Lehi integrated with the official jurisdiction boundary |
| ✅ | Moab | 135 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for the City of Moab integrated with the official jurisdiction boundary |
| ✅ | Murray | 1,178 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for the City of Murray integrated with the official jurisdiction boundary |
| ✅ | Nephi | 337 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for the City of Nephi integrated with the official jurisdiction boundary |
| ✅ | Richfield | 129 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for the City of Richfield integrated with the official jurisdiction boundary |
| ✅ | Riverton | 503 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for the City of Riverton integrated with the official jurisdiction boundary |
| ✅ | Sandy | 738 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for the City of Sandy integrated with the official jurisdiction boundary |
| ✅ | Santa Clara | 178 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for the City of Santa Clara integrated with the official jurisdiction boundary |
| ✅ | South Jordan | 1,328 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for the City of South Jordan integrated with the official jurisdiction boundary |
| ✅ | Taylorsville | 106 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for the City of Taylorsville integrated with the official jurisdiction boundary |
| ✅ | West Valley City | 811 | Official jurisdiction boundary | Official Utah Division of Forestry, Fire & State Lands `Utah Urban Tree Inventory` rows for West Valley City integrated with the official jurisdiction boundary |
| ✅ | San Francisco | 24,099 | Official jurisdiction boundary | Official San Francisco Public Works `Street Tree List` integrated from the city open-data portal |
| ✅ | San Jose | 18,021 | Official jurisdiction boundary | Official City of San Jose `Street Tree` layer integrated from the city open-data ArcGIS service |
| ✅ | Los Angeles | 40,459 | Official jurisdiction boundary | Official StreetsLA public TreeKeeper `Street Sites` inventory integrated using server-side blossom filtering against `SITE_ATTR1` |
| ✅ | Pasadena | 5,770 | Official jurisdiction boundary | Official City of Pasadena `Street ROW Trees` ArcGIS layer integrated from the city's open GIS services and official jurisdiction boundary |
| ✅ | Anaheim | 4,778 | Official jurisdiction boundary | Official City of Anaheim public street-tree inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Costa Mesa | 887 | Official jurisdiction boundary | Official City of Costa Mesa public tree-benefits inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Fontana | 3,732 | Official jurisdiction boundary | Official City of Fontana public i-Tree inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Fullerton | 4,399 | Official jurisdiction boundary | Official City of Fullerton public tree-benefits inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | La Canada Flintridge | 314 | Official jurisdiction boundary | Official City of La Canada Flintridge public tree inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Maywood | 71 | Official jurisdiction boundary | Official City of Maywood public i-Tree inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Mountain View | 2,907 | Official jurisdiction boundary | Official City of Mountain View `Trees` ArcGIS layer integrated from the city Heritage Trees service and official jurisdiction boundary |
| ✅ | Beverly Hills | 1,464 | Official jurisdiction boundary | Official City of Beverly Hills `Trees of Beverly Hills` ArcGIS layer integrated from the city's public GIS services and official jurisdiction boundary |
| ✅ | Monterey Park | 480 | Official jurisdiction boundary | Official City of Monterey Park public i-Tree inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Pomona | 475 | Official jurisdiction boundary | Official City of Pomona public i-Tree inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Rancho Cucamonga | 4,486 | Official jurisdiction boundary | Official City of Rancho Cucamonga public tree-benefits inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Riverside | 5,479 | Official jurisdiction boundary | Official City of Riverside public i-Tree inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | San Diego | 13,310 | Official jurisdiction boundary | Official City of San Diego `Trees (Street Trees)` ArcGIS layer integrated with server-side blossom filtering |
| ✅ | Irvine | 986 | Official jurisdiction boundary | Official City of Irvine `City Trees` layer integrated from the city ArcGIS landscape service and official city boundary |
| ✅ | Azusa | 757 | Official jurisdiction boundary | Official City of Azusa public tree-benefits inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Palo Alto | 4,996 | Official jurisdiction boundary | Official City of Palo Alto `Tree Data` layer integrated from the city open GIS portal; official boundary comes from the city-published boundary shapefile |
| ✅ | Oakland | 3,977 | Official jurisdiction boundary | Official City of Oakland `Oakland Street Trees` Socrata dataset integrated from the city open-data portal |
| ✅ | Berkeley | 3,973 | Official jurisdiction boundary | Official City of Berkeley public shapefile inventory integrated from the city ArcGIS item download |
| ✅ | Cupertino | 1,299 | Official jurisdiction boundary | Official City of Cupertino `Trees` layer integrated from the city GIS portal |
| ✅ | Fremont | 5,555 | Official jurisdiction boundary | Official City of Fremont public TreePlotter inventory integrated from the city urban-forestry portal plus public species lookup table |
| ✅ | Concord | 4,103 | Official jurisdiction boundary | Official City of Concord public TreePlotter inventory integrated from the city tree-inventory portal plus official GIS boundary |
| ✅ | Gilroy | 43 | Official jurisdiction boundary | Official Santa Clara County public `Tree Inventories in Santa Clara County` service integrated using the `City = Gilroy` subset and official jurisdiction boundary |
| ✅ | El Segundo | 348 | Official jurisdiction boundary | Official City of El Segundo public tree inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Los Gatos | 15 | Official jurisdiction boundary | Official Santa Clara County public `Tree Inventories in Santa Clara County` service integrated using the `City = Los Gatos` subset and official jurisdiction boundary |
| ✅ | Morgan Hill | 83 | Official jurisdiction boundary | Official Santa Clara County public `Tree Inventories in Santa Clara County` service integrated using the `City = Morgan Hill` subset and official jurisdiction boundary |
| ✅ | Sacramento | 3,442 | Official jurisdiction boundary | Official City of Sacramento `City Maintained Trees` ArcGIS layer integrated from the city open-data portal and official jurisdiction boundary |
| ✅ | Salinas | 4,535 | Official jurisdiction boundary | Official City of Salinas OpenDataSoft `Tree Inventory` dataset integrated from the city open-data portal |
| ✅ | Santa Clarita | 1,927 | Official jurisdiction boundary | Official City of Santa Clarita public i-Tree inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Saratoga | 6 | Official jurisdiction boundary | Official Santa Clara County public `Tree Inventories in Santa Clara County` service integrated using the `City = Saratoga` subset and official jurisdiction boundary |
| ✅ | South San Francisco | 784 | Official jurisdiction boundary | Official City of South San Francisco public TreeKeeper inventory integrated from the city trees page plus official GIS boundary |
| ✅ | Sunnyvale | 8 | Official jurisdiction boundary | Official Santa Clara County public `Tree Inventories in Santa Clara County` service integrated using the `City = Sunnyvale` subset and official jurisdiction boundary |
| ✅ | West Sacramento | 1,480 | Official jurisdiction boundary | Official City of West Sacramento `Tree Inventory` ArcGIS layer integrated from the city's GIS service and official jurisdiction boundary |
| ✅ | West Hollywood | 438 | Official jurisdiction boundary | Official City of West Hollywood public tree inventory integrated from the city's open-data GIS service and official jurisdiction boundary |
| ✅ | Burbank | 2,134 | Official jurisdiction boundary | Official City of Burbank public TreeKeeper inventory integrated from the city forestry portal and official jurisdiction boundary |
| ✅ | Camarillo | 964 | Official jurisdiction boundary | Official City of Camarillo public `Trees` ArcGIS layer integrated from the city's GIS service and official jurisdiction boundary |
| ✅ | Chino | 580 | Official jurisdiction boundary | Official City of Chino public `CityTrees_ResCityMaintSpecIden` ArcGIS layer integrated from the city's GIS service and official jurisdiction boundary |
| ✅ | Escondido | 1,570 | Official jurisdiction boundary | Official City of Escondido public `TreeInventory` ArcGIS layer integrated from the city's GIS service and official jurisdiction boundary |
| ✅ | Glendora | 665 | Official jurisdiction boundary | Official City of Glendora public tree inventory layer integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | La Mesa | 109 | Official jurisdiction boundary | Official City of La Mesa public `Tree Inventory` ArcGIS layer integrated from the city's GIS service and official jurisdiction boundary |
| ✅ | Redlands | 1,447 | Official jurisdiction boundary | Official City of Redlands public `Street Trees` ArcGIS layer integrated from the city's GIS service and official jurisdiction boundary |
| ✅ | Santee | 305 | Official jurisdiction boundary | Official City of Santee public urban-forest benefits inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Vista | 119 | Official jurisdiction boundary | Official City of Vista public i-Tree benefits inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | West Covina | 1,052 | Official jurisdiction boundary | Official City of West Covina public `Tree Information` ArcGIS layer integrated from the city's GIS service and official jurisdiction boundary |
| ✅ | Bell | 93 | Official jurisdiction boundary | Official City of Bell public tree-benefits inventory integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | San Fernando | 11 | Official jurisdiction boundary | Official City of San Fernando CAL FIRE public tree layer integrated from the city's ArcGIS service and official jurisdiction boundary |
| ✅ | Buena Park | 365 | Official jurisdiction boundary | Integrated from the official City of Buena Park public tree inventory layer and official jurisdiction boundary. |
| ✅ | Citrus Heights | 50 | Official jurisdiction boundary | Integrated from the official City of Citrus Heights urban forestry tree inventory layer and official jurisdiction boundary. |
| ✅ | Corona | 2,691 | Official jurisdiction boundary | Integrated from the official City of Corona public tree sites layer and official jurisdiction boundary. |
| ✅ | Cudahy | 48 | Official jurisdiction boundary | Integrated from the public City of Cudahy tree layers and official jurisdiction boundary. |
| ✅ | Dana Point | 112 | Official jurisdiction boundary | Integrated from the official City of Dana Point public tree inventory layer and official jurisdiction boundary. |
| ✅ | Encinitas | 447 | Official jurisdiction boundary | Integrated from the official City of Encinitas public street and parks tree inventory layers and official jurisdiction boundary. |
| ✅ | Glendale | 35 | Official jurisdiction boundary | Integrated from the public Glendale tree survey layer and official jurisdiction boundary. |
| ✅ | Goleta | 206 | Official jurisdiction boundary | Integrated from the official City of Goleta public tree inventory layer and official jurisdiction boundary. |
| ✅ | Inglewood | 159 | Official jurisdiction boundary | Integrated from the public City of Inglewood tree layers and official jurisdiction boundary. |
| ✅ | La Mirada | 55 | Official jurisdiction boundary | Integrated from the public I-5 corridor tree sites layer filtered to La Mirada and clipped to the official jurisdiction boundary. |
| ✅ | La Verne | 226 | Official jurisdiction boundary | Integrated from the official City of La Verne public tree inventory layer and official jurisdiction boundary. |
| ✅ | Laguna Beach | 9 | Official jurisdiction boundary | Integrated from the official City of Laguna Beach maintained tree inventory layer and official jurisdiction boundary. |
| ✅ | Lodi | 192 | Official jurisdiction boundary | Integrated from the official City of Lodi public tree inventory and official jurisdiction boundary. |
| ✅ | Newport Beach | 2,286 | Official jurisdiction boundary | Integrated from the official City of Newport Beach public tree inventory dashboard layer and official jurisdiction boundary. |
| ✅ | Norwalk | 186 | Official jurisdiction boundary | Integrated from the public I-5 corridor tree sites layer filtered to Norwalk and clipped to the official jurisdiction boundary. |
| ✅ | Oxnard | 5,054 | Official jurisdiction boundary | Integrated from the official City of Oxnard public trees layer and official jurisdiction boundary. |
| ✅ | Pleasanton | 537 | Official jurisdiction boundary | Integrated from the official City of Pleasanton landscape architecture tree inventory map and official jurisdiction boundary. |
| ✅ | Poway | 27 | Official jurisdiction boundary | Integrated from the official City of Poway GIS tree inventory layer and official jurisdiction boundary. |
| ✅ | Rancho Palos Verdes | 657 | Official jurisdiction boundary | Integrated from the official City of Rancho Palos Verdes public tree inventory layer and official jurisdiction boundary. |
| ✅ | Redondo Beach | 1,996 | Official jurisdiction boundary | Integrated from the official City of Redondo Beach GIS tree inventory layer and official jurisdiction boundary. |
| ✅ | San Dimas | 266 | Official jurisdiction boundary | Integrated from the official City of San Dimas public tree inventory layer and official jurisdiction boundary. |
| ✅ | Santa Barbara | 1,249 | Official jurisdiction boundary | Integrated from the official City of Santa Barbara public tree inventory layer and official jurisdiction boundary. |
| ✅ | Santa Fe Springs | 10 | Official jurisdiction boundary | Integrated from the public I-5 corridor tree sites layer filtered to Santa Fe Springs and clipped to the official jurisdiction boundary. |
| ✅ | Santa Monica | 2,253 | Official jurisdiction boundary | Integrated from the official City of Santa Monica public trees feature service and official jurisdiction boundary. |
| ✅ | Solana Beach | 11 | Official jurisdiction boundary | Integrated from the official City of Solana Beach tree inventory application layer and official jurisdiction boundary. |
| ✅ | South Gate | 10 | Official jurisdiction boundary | Integrated from the public South Gate/Cudahy tree layer clipped to the official South Gate jurisdiction boundary. |
| ✅ | Thousand Oaks | 636 | Official jurisdiction boundary | Integrated from the official City of Thousand Oaks landscape trees layer and official jurisdiction boundary. |
| ✅ | Torrance | 24 | Official jurisdiction boundary | Integrated from the public City of Torrance tree layer and official jurisdiction boundary. |
| ✅ | Ventura | 1,322 | Official jurisdiction boundary | Integrated from the official City of Ventura public tree inventory layer and official jurisdiction boundary. |
| ✅ | Yorba Linda | 380 | Official jurisdiction boundary | Integrated from the official City of Yorba Linda public tree inventory layer and official jurisdiction boundary. |
| ✅ | Washington DC | 16,533 | Official jurisdiction boundary | Urban Tree Canopy (DDOT); ornamental cherry cultivar mapping expanded |
| ✅ | Vancouver BC | 34,369 | Official jurisdiction boundary | Official City of Vancouver `public-trees` ODS dataset integrated; boundary polygon derived from official city-boundary line dataset |
| ✅ | New Westminster | 1,786 | Official jurisdiction boundary | Official ArcGIS `Tree Inventory (Active Trees)` integrated with the official Metro Vancouver administrative boundary for the City of New Westminster |
| ✅ | Spokane | 8,472 | Official jurisdiction boundary | City of Spokane Parks tree inventory integrated from official open GIS service; genus-level rows normalized to generic scientific placeholders |
| ✅ | Walla Walla | 1,167 | Official jurisdiction boundary | Official City of Walla Walla `GISBaseMap_TreesVisible` layer integrated from the city ArcGIS service |
| ✅ | Victoria BC | 6,094 | Official jurisdiction boundary | Official City of Victoria Parks tree-species layer integrated; surveyed-trees layer was reviewed separately but excluded because it has no species field |
| ✅ | Burlingame | 1,997 | Official jurisdiction boundary | Official city trees page links to a public guest inventory backed by a queryable feature service; integrated under the city-linked public-source rule |
| ✅ | Milpitas | 1,696 | Official jurisdiction boundary | Official City of Milpitas `Trees RO` layer integrated from the city ArcGIS service |
| ✅ | San Mateo | 1,868 | Official jurisdiction boundary | Official City of San Mateo `Street Trees` layer integrated from the city ArcGIS item/service |
| ✅ | San Rafael | 422 | Official jurisdiction boundary | Official City of San Rafael `Trees` layer integrated from the city ArcGIS service |
| ✅ | Shoreline | 2,244 | Official jurisdiction boundary | Public Tree Inventory public-only layer integrated |
| ✅ | Renton | 1,879 | Official jurisdiction boundary | City Tree Sites source |
| ✅ | Sammamish | 1,163 | Official jurisdiction boundary | TreeKeeper Street + Park public grid endpoints integrated; cultivar keyword rerun recovered more ornamental records |
| ✅ | Snohomish | 856 | Official jurisdiction boundary | Official urban-forestry inventory page + ArcGIS point layer integrated; all included records are tagged `ROW = Yes` |
| ✅ | Bellingham | 645 | Official jurisdiction boundary | Official City of Bellingham tree layer (`maps.cob.org`) integrated |
| ✅ | Yakima | 509 | Official jurisdiction boundary | Official City of Yakima `Trees` layer integrated; common-name-only rows are normalized to generic scientific placeholders when the blossom hint is strong enough |
| ✅ | Everett | 464 | Official jurisdiction boundary | Official TreeKeeper public park-tree endpoint integrated |
| ✅ | Kirkland | 3,122 | Official jurisdiction boundary | 2023-2024 Kirkland Tree Inventory integrated from public TreePlotter session/API |
| ✅ | Bellevue | 342 | Official jurisdiction boundary | Public source count increased under 5-species scope; all fetched rows now fall inside 5-species mapping |
| ✅ | Kenmore | 329 | Official jurisdiction boundary | Public Trees source |
| ✅ | Redmond | 185 | Official jurisdiction boundary | TreeSite source |
| ✅ | Puyallup | 76 | Official jurisdiction boundary | City Maintained Street Trees |
| ✅ | Gig Harbor | 63 | Official jurisdiction boundary | PW Trees Public Viewer |
| ✅ | SeaTac | 38 | Official jurisdiction boundary | Genus/common-name normalization added |
| ✅ | Oak Harbor | 207 | Official jurisdiction boundary | Official City of Oak Harbor `Tree Inventory` layer integrated from the city ArcGIS service |
| ✅ | Olympia | 97 | Official jurisdiction boundary | Official Washington State Capitol Campus urban-forest inventory integrated and clipped to the official Olympia boundary |
| ✅ | Pullman | 477 | Official jurisdiction boundary | Official Washington State University public campus tree inventory integrated and clipped to the official Pullman boundary |
| ✅ | Beaverton | 13 | Official jurisdiction boundary | Official City of Beaverton `Street of Trees` layer integrated from the city ArcGIS service |
| ✅ | Keizer | 31 | Official jurisdiction boundary | Official City of Keizer public tree inventory layer integrated from the city ArcGIS service |
| ✅ | Tualatin | 301 | Official jurisdiction boundary | Official City of Tualatin `Street Trees View` layer integrated from the city ArcGIS service |
| ✅ | West Linn | 393 | Official jurisdiction boundary | Official City of West Linn public street-tree inventory integrated after coded-value domain decoding |
| ✅ | Albany | 1,692 | Official jurisdiction boundary | Official Oregon Department of Forestry public statewide TreePlotter inventory clipped to the official Albany boundary |
| ✅ | Salem | 1,447 | Official jurisdiction boundary | Official Oregon Department of Forestry public statewide TreePlotter inventory clipped to the official Salem boundary |
| ✅ | Wilsonville | 910 | Official jurisdiction boundary | Official Oregon Department of Forestry public statewide TreePlotter inventory clipped to the official Wilsonville boundary |
| ✅ | Grants Pass | 245 | Official jurisdiction boundary | Official Oregon Department of Forestry public statewide TreePlotter inventory clipped to the official Grants Pass boundary |
| ✅ | Springfield | 83 | Official jurisdiction boundary | Official Oregon Department of Forestry public statewide TreePlotter inventory clipped to the official Springfield boundary |
| ✅ | Redmond | 58 | Official jurisdiction boundary | Official Oregon Department of Forestry public statewide TreePlotter inventory clipped to the official Redmond boundary |
| ✅ | Oregon City | 33 | Official jurisdiction boundary | Official Oregon Department of Forestry public statewide TreePlotter inventory clipped to the official Oregon City boundary |
| ✅ | Forest Grove | 25 | Official jurisdiction boundary | Official Oregon Department of Forestry public statewide TreePlotter inventory clipped to the official Forest Grove boundary |
| ✅ | Happy Valley | 12 | Official jurisdiction boundary | Official Oregon Department of Forestry public statewide TreePlotter inventory clipped to the official Happy Valley boundary |
| ✅ | Lake Oswego | 7 | Official jurisdiction boundary | Official Oregon Department of Forestry public statewide TreePlotter inventory clipped to the official Lake Oswego boundary |
| ✅ | Palm Springs | 6 | Official jurisdiction boundary | Official City of Palm Springs public `Tree Inventory 2015` layer integrated from the city ArcGIS service |
| ✅ | Turlock | 3 | Official jurisdiction boundary | Official California State University, Stanislaus public `Turlock Tree Inventory` layer integrated and clipped to the official Turlock boundary |
| ✅ | Watsonville | 3 | Official jurisdiction boundary | Official `Tree Inventories in Santa Clara County` shared ArcGIS service subset to `City = 'Watsonville'` |

## B — Official Point-Tree Data Exists But Is Not Product-Ready
These cities are not in `A2` yet because the official point-tree source is still partial, blocked, or otherwise not publish-ready under the current rules.

| Done | City | Estimated In-Scope Count | Status | Blocker |
|---|---|---:|---|---|
| ⏳ | Mercer Island | 803 (Town Center only) | Partial-only | Official urban-forestry page documents a 2018 Town Center street-tree inventory, but a verified citywide public single-tree endpoint is still not confirmed |
| ⏳ | Bremerton | Unknown | Blocked public map | Official Park Tree Map web map exists under a city account, but the underlying feature service currently returns `403 Forbidden` to direct public queries |
| ⏳ | Poulsbo | 75 | Partial-only | Official `Historic Trees of Poulsbo` feature service is public, but it is a curated historic-tree layer, not a citywide public inventory |
| ⏳ | Pasco | Unknown | Partial-only | Official city content found in this round was a `Volunteer Park Tree Walk` map, not a citywide public single-tree inventory |
| ⏳ | Harrisburg | Unknown | Blocked species codes | Official City of Harrisburg `Street Trees` layer is public, but species values are internal short codes (for example `PRPE2`, `PRSE1`) and this round did not confirm a public mapping table |
| ⏳ | Salisbury | 0 | Zero in-scope rows | Official City of Salisbury public tree inventory layer is citywide, but the current blossom-filtered official source returned no in-scope rows inside the official jurisdiction boundary |
| ⏳ | Fayetteville | 0 | Zero in-scope rows | Official City of Fayetteville `Tree Inventory Phase 1` public layer is citywide, but the current blossom-filtered official source returned no in-scope rows inside the official jurisdiction boundary |
| ⏳ | Jacksonville | 0 | Zero in-scope rows | Official City of Jacksonville public TreePlotter inventory page is live, but the current public inventory returned no in-scope blossom rows inside the official jurisdiction boundary |

## C — No Verified Official Public Point-Tree Dataset Or Outside Current Workflow

### Gray Coverage (Official Boundary Resolved, No Official Public Tree Dataset)
| Done | City | Status | Boundary Rule | Notes |
|---|---|---|---|---|
| 🩶 | St. John's (NL) | Research blocker | Official jurisdiction boundary | Government of Newfoundland and Labrador GeoHub, City of St. John's official GIS, St. John's ArcGIS Online public items (`Tree Requests`, `Re-Leaf Application`, `Parks_Data`), and Memorial University official public map endpoints (`campus_map` Concept3D and Botanical Garden audio-tour pages) were reviewed; the accessible public layers are forms, park polygons, roads/buildings, or garden/tour stops, but no verified official public blossom-scope single-tree dataset is currently publishable |
| 🩶 | Mount Pearl (NL) | In gray coverage | Official jurisdiction boundary | Official City of Mount Pearl GIS / ArcGIS Online public maps and REST services were reviewed, but the accessible public layers are roads, buildings, parcels, and infrastructure only; no verified public single-tree species inventory was confirmed |
| 🩶 | Alexandria | In gray coverage | Official jurisdiction boundary | Official City of Alexandria urban-forestry and GIS pages were reviewed, but no public single-tree species inventory was confirmed |
| 🩶 | Burnaby | In gray coverage | Official jurisdiction boundary | Official Burnaby GIS/open-data sources were reviewed; no public single-tree species inventory was confirmed |
| 🩶 | Delta | In gray coverage | Official jurisdiction boundary | Official Delta GIS/open-data sources were reviewed; no public single-tree species inventory was confirmed |
| 🩶 | Alameda | In gray coverage | Official jurisdiction boundary | Official city tree and urban-forest materials were reviewed, but no verified public citywide single-tree dataset was confirmed in this round |
| 🩶 | Daly City | In gray coverage | Official jurisdiction boundary | Official city urban-forestry and GIS entry points were reviewed, but no verified public citywide single-tree species dataset was confirmed in this round |
| 🩶 | Davis | In gray coverage | Official jurisdiction boundary | Official City of Davis GIS and urban-forest materials were reviewed, but no public citywide single-tree species inventory was confirmed in this round |
| 🩶 | Elk Grove | In gray coverage | Official jurisdiction boundary | Official City of Elk Grove GIS and open-data entry points were reviewed, but no public citywide single-tree species inventory was confirmed in this round |
| 🩶 | Folsom | In gray coverage | Official jurisdiction boundary | Official City of Folsom GIS and open-data entry points were reviewed, but no public citywide single-tree species inventory was confirmed in this round |
| 🩶 | Gresham | In gray coverage | Official jurisdiction boundary | Official ArcGIS search and city-site checks did not confirm a public citywide single-tree species dataset |
| 🩶 | Hayward | In gray coverage | Official jurisdiction boundary | Official city urban-forestry and GIS entry points were reviewed, but no verified public citywide single-tree species dataset was confirmed in this round |
| 🩶 | Hillsboro | In gray coverage | Official jurisdiction boundary | Official ArcGIS search and city-site checks did not confirm a public citywide single-tree species dataset |
| 🩶 | Long Beach | In gray coverage | Official jurisdiction boundary | Official Long Beach open-data materials expose a partial `Public Trees Planted Since 2018` dataset, but not a citywide public single-tree species inventory |
| 🩶 | Monterey | In gray coverage | Official jurisdiction boundary | Official city tree standards and GIS entry points were reviewed, but no public citywide single-tree species dataset was confirmed |
| 🩶 | Montgomery County, MD | In gray coverage | Official jurisdiction boundary | Official Montgomery County GIS layers were reviewed; the public `Tree Planting Locations` layer is a planting-program dataset rather than a countywide single-tree inventory |
| 🩶 | Napa | In gray coverage | Official jurisdiction boundary | Official ArcGIS and city data portal searches did not confirm a public citywide single-tree species dataset |
| 🩶 | Redwood City | In gray coverage | Official jurisdiction boundary | Official city GIS and public-works materials were reviewed, but no verified public citywide single-tree dataset was confirmed in this round |
| 🩶 | Roseville | In gray coverage | Official jurisdiction boundary | Official City of Roseville GIS and open-data entry points were reviewed, but no public citywide single-tree species inventory was confirmed in this round |
| 🩶 | Richmond (CA) | In gray coverage | Official jurisdiction boundary | Official Richmond, CA ArcGIS and city data searches did not confirm a public citywide public single-tree species dataset |
| 🩶 | Richmond BC | In gray coverage | Official jurisdiction boundary | Official City of Richmond GIS boundary services were confirmed, but no public citywide single-tree species inventory was confirmed in this round |
| 🩶 | Saanich | In gray coverage | Official jurisdiction boundary | Official Saanich GIS/open-data sources were reviewed; no public single-tree species inventory was confirmed |
| 🩶 | Santa Ana | In gray coverage | Official jurisdiction boundary | Official City of Santa Ana public tree resources expose neighborhood street-tree species maps, but not a public citywide single-tree species inventory |
| 🩶 | Santa Cruz | In gray coverage | Official jurisdiction boundary | Official ArcGIS and city GIS searches did not confirm a public citywide single-tree species dataset |
| 🩶 | Santa Clara | In gray coverage | Official jurisdiction boundary | Official city urban-forest materials were reviewed, but no public citywide single-tree species dataset was confirmed |
| 🩶 | Santa Rosa | In gray coverage | Official jurisdiction boundary | Official city GIS results found fire-damaged tree-removal layers, not a citywide public single-tree inventory |
| 🩶 | Stockton | In gray coverage | Official jurisdiction boundary | Official ArcGIS and city GIS searches did not confirm a public citywide single-tree species dataset |
| 🩶 | Surrey | In gray coverage | Official jurisdiction boundary | Official Surrey Open Data exposes `Important Trees` and `Park Specimen Trees`, but no citywide public single-tree species inventory was confirmed |
| 🩶 | Tigard | In gray coverage | Official jurisdiction boundary | Official ArcGIS results exposed an ash-tree inventory, not a citywide public single-tree species inventory |
| 🩶 | Langley City | In gray coverage | Official jurisdiction boundary | Official City of Langley / Metro Vancouver public GIS entry points were reviewed; the official jurisdiction boundary is available, but no public citywide single-tree species inventory was confirmed |

### Investigated / Blocked / Out Of Scope
| Done | City | Status | Reason |
|---|---|---|---|
| ⚠️ | Vashon | Unincorporated place | Not an incorporated city under the current official city-boundary rule, so there is no municipal city dataset/boundary target in the present workflow |
| ⚠️ | Kingston | Unincorporated place | Not an incorporated city under the current official city-boundary rule, so there is no municipal city dataset/boundary target in the present workflow |
| ⚠️ | Silverdale | Unincorporated place | Not an incorporated city under the current official city-boundary rule, so there is no municipal city dataset/boundary target in the present workflow |
| ⚠️ | Cottage Lake | Unincorporated place | Not an incorporated city under the current official city-boundary rule, so there is no municipal city dataset/boundary target in the present workflow |
| ⚠️ | Silver Firs | Unincorporated place | Not an incorporated city under the current official city-boundary rule, so there is no municipal city dataset/boundary target in the present workflow |
| ⚠️ | Issaquah | Not yet public | Official Urban Forestry page says “Public tree inventory” is still a 2025/2026 implementation item |
| ⚠️ | Kent | Not found yet | Official sustainability pages did not expose a city single-tree species layer; ArcGIS hits found during research were Kent County parks data, not City of Kent inventory |
| ⚠️ | Tacoma | Not usable yet | Official city ArcGIS content found in this round was canopy-height mapping, not a public single-tree species point inventory |
| ⚠️ | Burien | Not usable | Species values are internal codes (e.g. `ULFR`) without public mapping table |
| ⚠️ | Lynnwood | Not usable yet | Official ArcGIS content found in this round was a South Lynnwood urban-forest project web map, not a citywide single-tree species inventory |
| ⚠️ | Ontario (CA) | Not found yet | Official city site and GIS entry points reviewed in this round did not confirm a public citywide single-tree species inventory |
| ⚠️ | Chicago | Official unavailable (gray coverage) | Official City of Chicago open-data and ArcGIS entry points reviewed in this round did not confirm a public citywide single-tree species inventory |
| ⚠️ | Phoenix | Official unavailable (gray coverage) | Official City of Phoenix open-data CKAN catalog, ArcGIS entries, and urban-forest materials reviewed in this round did not confirm a public citywide single-tree species inventory |
| ⚠️ | Detroit | Official unavailable (gray coverage) | Official Detroit open-data and ArcGIS Hub searches reviewed in this round did not confirm a public citywide single-tree species inventory |
| ⚠️ | Atlanta | Official unavailable (gray coverage) | Official City of Atlanta GIS and open-data entry points reviewed in this round did not confirm a public citywide single-tree species inventory |
| ⚠️ | Bothell | Not usable yet | Official Urban Forest Management Plan references a street-tree inventory summary PDF, but no public raw single-tree species endpoint was confirmed |
| ⚠️ | Medina | Not found yet | The previously guessed GIS page path now resolves to 404 and no official public tree inventory layer was confirmed |
| ⚠️ | Lake Forest Park | Not found yet | Official city pages and ArcGIS search did not confirm a city-owned public single-tree species layer |
| ⚠️ | Langford | Boundary query unsupported | Official public base-map service exposes a `Boundary` layer, but the service currently supports `Map` capability only and rejects standard public feature queries, so coverage cannot be drawn under the hard rule |
| ⚠️ | Woodinville | Not found yet | Official city pages did not confirm a public single-tree species point inventory |
| ⚠️ | Newcastle | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Snoqualmie | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | North Bend | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Black Diamond | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Carnation | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Duvall | False positive search hit | ArcGIS search result found a Lower Columbia dams layer, not a City of Duvall tree inventory |
| ⚠️ | Enumclaw | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Ferndale, WA | False positive search hit | Public ArcGIS result in this round was City of Ferndale, Michigan tree data, not a verified Ferndale, WA city inventory |
| ⚠️ | Clyde Hill | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Granite Falls | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Hunts Point | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Lynden | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Yarrow Point | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Beaux Arts Village | Non-official public map | Public ArcGIS web map exists, but it is published by a contractor (`TreeSolutionsInc`), not a verified official city-hosted public dataset |
| ⚠️ | Normandy Park | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Port Orchard | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Richland | False positive / non-city hits | Public search results in this round pointed to non-city or non-Washington Richland datasets, not a verified City of Richland inventory |
| ⚠️ | Skykomish | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Brier | False positive search hit | ArcGIS result was a single-address tree inventory experience, not a city inventory |
| ⚠️ | Woodway | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Monroe | False positive search hit | ArcGIS result belonged to an unrelated non-Washington owner, not the City of Monroe, WA |
| ⚠️ | Marysville | False positive search hit | ArcGIS results found Marysville, Ohio forestry layers, not City of Marysville, WA |
| ⚠️ | Lake Stevens | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Arlington | False positive search hit | ArcGIS results found Arlington, Texas tree layers, not Arlington, WA |
| ⚠️ | Wenatchee | Campus-only false positive | Public search results in this round surfaced Wenatchee Valley College campus tree maps, not a verified City of Wenatchee inventory |
| ⚠️ | Federal Way | False positive retired | The previously accessible hosted layer reviewed in this round is a street-light inventory (`Federal_Way_20221201`), not a tree dataset; no official public single-tree species layer was confirmed after portal search |
| ⚠️ | Lakewood | Plans / reports only | Official city materials reference inventory / assessment work, but current public city pages still do not expose a raw single-tree species point layer |
| ⚠️ | University Place | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Fife | Not found yet | ArcGIS public search and city-site spot-check did not confirm an official public single-tree inventory |
| ⚠️ | Davenport | False positive search hit | Public ArcGIS results in this round were Davenport, Iowa layers, not Davenport, WA tree data |
| ⚠️ | Sumner | False positive search hit | ArcGIS result was Bonney Lake’s public portal, not a Sumner tree inventory |
| ⚠️ | Bonney Lake | No tree layer in public portal | Official `BL_Public_Portal_WFL1` was checked and does not expose a tree inventory layer |
| ⚠️ | Lacey | Open data searched, no tree layer found | Official `data.cityoflacey.org` search in this round did not surface a public single-tree species dataset |
| ⚠️ | Tumwater | GIS pages found, no tree layer found | Official GIS/open-data entry points were reviewed in this round, but no public single-tree species point layer was confirmed |
| ⚠️ | Vancouver WA | Outside official city boundary | Official Washington State University Vancouver public campus tree inventory is queryable, but clipping it to the official Vancouver, Washington boundary currently yields 0 in-scope city rows |
| ⚠️ | Essex County, NJ | Not found yet | Official county open-data entry points were reviewed, but no verified countywide single-tree species inventory was confirmed |
| ⚠️ | Mount Vernon | Not found yet | Official city GIS / urban-forestry entry points reviewed in this round did not confirm a public citywide single-tree inventory |
| ⚠️ | Burlington, WA | Not found yet | Official city pages reviewed in this round did not confirm a public citywide single-tree inventory |
| ⚠️ | Anacortes | Not found yet | Official city GIS pages reviewed in this round did not confirm a public citywide single-tree inventory |
| ⚠️ | Edmonds / Mukilteo / Mountlake Terrace / Mill Creek | Not found yet | No reliable official public single-tree species point layers confirmed yet |
| ⚠️ | Tukwila / Des Moines / Maple Valley | Not found or rejected | No reliable official city-level single-tree + species point layers, or false-geography matches |

## Hard Rules
- Coverage polygons must use official jurisdiction boundary geometries only.
- Any legacy non-official boundary cache must be replaced; OSM/Nominatim-style boundaries are not allowed in product outputs.
- If an official jurisdiction boundary cannot be resolved, that place is excluded from coverage polygons (no convex hull fallback).
- Boundary matching for special names (for example, `Washington DC` or county-equivalent `Arlington`) must use explicit state + basename mapping or an official jurisdiction layer, never manual polygons.
- Source-of-truth for classification remains scientific name first, with controlled common-name fallback only for explicitly generic genus-level rows (for example `Prunus sp.`, `Malus sp.`, `Magnolia sp.`).

## Bellevue Data Note
- Bellevue’s official `City Trees` public source currently returns `10,478` total tree rows.
- Under the current 5-species scope (`cherry / plum / peach / magnolia / crabapple`), `342` rows are included after normalization and mapping.

## Kirkland Data Note
- Kirkland’s public TreePlotter inventory currently returns `39,014` total tree rows through the public session/API flow.
- Under the current 5-species scope (`cherry / plum / peach / magnolia / crabapple`), `3,122` rows are included after abbreviation expansion and ornamental cultivar mapping.

## March 2026 Taxonomy Sweep
- Added card-ready `subtype_name` output for all integrated cities.
- Added curated subtype keyword recovery for ornamental cherry / plum / peach / magnolia / crabapple names.
- Latest rerun increased included rows from `72,082` to `72,552` (`+470`), led by `Sammamish (+233)` and `Seattle (+174)`.

## March 2026 Expansion Sweep
- Integrated `Snohomish`, `Bellingham`, and `Spokane` from official ArcGIS public layers.
- Confirmed `Mercer Island` only has a documented Town Center inventory so far, not a verified citywide public endpoint.
- Confirmed `Bremerton` has a public Park Tree Map web map, but the backing feature service is still blocked for direct public ETL use.
- Integrated `Yakima` and `Walla Walla` from official city ArcGIS tree layers.
- Confirmed `Poulsbo` and `Pasco` only expose partial public tree content in this round (`Historic Trees` / `Volunteer Park Tree Walk`), not citywide inventories.
- Confirmed `Vashon`, `Kingston`, `Silverdale`, `Cottage Lake`, and `Silver Firs` are not incorporated cities in the current city-boundary workflow.

## March 2026 California Expansion
- Integrated `San Francisco` from the official San Francisco Public Works `Street Tree List` open-data dataset.
- Integrated `San Jose` from the official City of San Jose `Street Tree` ArcGIS open-data layer.
- Integrated `Burlingame` from the public city-linked `City Street Tree Inventory`; the source is contractor-hosted but explicitly published on the official City of Burlingame trees page and exposes a public queryable feature service.
- Integrated `Palo Alto` from the official City of Palo Alto Open GIS `Tree Data` layer and city-published boundary shapefile.
- Integrated `Berkeley` from the official public inventory shapefile published through the City of Berkeley ArcGIS item.
- Integrated the Los Angeles ring cities `Pasadena`, `Anaheim`, `Fullerton`, `Beverly Hills`, `Azusa`, `El Segundo`, `Bell`, and `San Fernando` from official ArcGIS public tree inventories, bringing the LA-area covered-city count to at least ten (`Los Angeles`, `Irvine`, plus those eight new cities).
- Integrated `Cupertino` from the official City of Cupertino GIS `Trees` layer.
- Integrated `Oakland` from the official City of Oakland `Oakland Street Trees` open-data dataset.
- Integrated `Mountain View` from the official City of Mountain View `Trees` ArcGIS layer published through the city Heritage Trees service.
- Integrated `Sacramento` from the official City of Sacramento `City Maintained Trees` ArcGIS layer published through the city open-data portal.
- Integrated `Pleasanton`, `Lodi`, `Poway`, `Redondo Beach`, and `Citrus Heights` from official public ArcGIS tree inventories by reusing the existing California ArcGIS single-tree publish path.
- Integrated `Sunnyvale` from the official Santa Clara County public `Tree Inventories in Santa Clara County` service using the `City = Sunnyvale` subset and the official jurisdiction boundary.
- Added gray coverage for `Santa Clara`, `Napa`, `Richmond (CA)`, `Santa Cruz`, `Santa Rosa`, and `Stockton` after city-site and official data portal review did not confirm a public citywide single-tree species dataset.
- Fixed a bad legacy `Palo Alto` boundary cache by switching the city boundary back to the official Census place geometry; this removed the incorrect East Bay pink polygon that had been covering Hayward / Livermore / Fremont in the map UI.

## April 2026 Oregon TreePlotter Expansion
- Integrated `Albany`, `Salem`, `Wilsonville`, `Grants Pass`, `Springfield`, `Redmond`, `Oregon City`, `Forest Grove`, `Happy Valley`, and `Lake Oswego` from the official Oregon Department of Forestry public TreePlotter inventory, clipped to official city boundaries.
- The statewide Oregon public TreePlotter returned `318,543` raw rows and `10,487` blossom-scope rows in this pass; the newly published city counts are `Albany 1,692`, `Salem 1,447`, `Wilsonville 910`, `Grants Pass 245`, `Springfield 83`, `Redmond 58`, `Oregon City 33`, `Forest Grove 25`, `Happy Valley 12`, and `Lake Oswego 7`.
- `Portland`, `Gresham`, `Hillsboro`, and `Tigard` were rechecked against the same official statewide source in this round and still returned `0` in-scope blossom rows under the current species mapping.

## April 2026 West Coast Expansion
- Integrated `Watsonville`, `Palm Springs`, and `Turlock` from official California ArcGIS inventories.
- Integrated `Beaverton`, `Keizer`, `Tualatin`, and `West Linn` from official Oregon ArcGIS street-tree inventories; `West Linn` required coded-value domain decoding and `Beaverton` moved out of gray coverage after the official public `Street of Trees` feature service became queryable.
- Integrated `Oak Harbor`, `Olympia`, and `Pullman` from official Washington inventories, including state-campus and university inventories clipped to official city boundaries.

## March 2026 BC Expansion
- Integrated `Vancouver BC` from the official City of Vancouver OpenDataSoft `public-trees` dataset.
- Integrated `Victoria BC` from the official City of Victoria `Tree Species (Parks trees database)` layer.
- `Vancouver BC` boundary is sourced from the official City of Vancouver `city-boundary` dataset and converted from the published legal boundary line into a polygon for coverage rendering.
- `Federal Way` was rechecked and downgraded from candidate status after the accessible hosted service turned out to be street lights, not trees.
- Added gray-coverage boundary support for `Burnaby`, `Delta`, and `Saanich` where official city boundaries are public but no official public single-tree species dataset is currently available.
- Rechecked `Richmond (CA)`; official boundary resolution now works, so the city moved into gray coverage rather than remaining excluded.

## March 2026 California / Oregon Expansion
- Integrated `Milpitas`, `San Mateo`, `San Rafael`, `Salinas`, and `Fremont` from official city-published public tree datasets.
- Integrated `Concord` from the official City of Concord TreePlotter inventory and official city GIS boundary.
- Integrated `South San Francisco` from the official city-linked TreeKeeper inventory and official city GIS boundary.
- `Fremont` required two specific parser fixes before product rows could be emitted:
  - EWKB point decoding with `SRID=3857`
  - species-name resolution through the public `species` lookup table rather than integer foreign keys in `trees`
- Added gray coverage for `Redwood City`, `Alameda`, `Hayward`, and `Daly City` after official-source review did not confirm a public citywide single-tree species dataset.
- Added gray coverage for `Gresham`, `Hillsboro`, `Salem`, and `Tigard` after official-source review did not confirm a public citywide single-tree species dataset or raw public endpoint.

## March 2026 Texas / South Bay Expansion
- Integrated `Houston` from the official City of Houston public `COH Urban Forestry Trees` web-map service using blossom filtering on `SPECIES` and the official jurisdiction boundary.
- Integrated `Los Gatos`, `Morgan Hill`, `Gilroy`, and `Saratoga` from the official Santa Clara County public `Tree Inventories in Santa Clara County` service using city-specific subsets and official jurisdiction boundaries.

## March 2026 Sacramento Ring Expansion
- Integrated `West Sacramento` from the official City of West Sacramento `Tree Inventory` ArcGIS layer and official jurisdiction boundary.
- Added gray coverage for `Elk Grove`, `Roseville`, `Folsom`, and `Davis` after reviewing official GIS and open-data entry points without confirming a public citywide single-tree species inventory.

## March 2026 Northeast Expansion
- Integrated `New York City` from the official NYC Parks `2015 Street Tree Census - Tree Data` dataset on NYC Open Data.
- Integrated `Philadelphia` from the official Philadelphia Parks & Recreation `PPR Tree Inventory 2025` layer.
- Integrated `Pittsburgh` from the official public Pittsburgh TreeKeeper inventory domain.
- Integrated `Cambridge (MA)` from the official City of Cambridge `Street Trees` shapefile download.
- Integrated `Boston` from the official Analyze Boston `BPRD Trees` download.
- Integrated `Baltimore` from the official city forestry tree layer on `gis.baltimorecity.gov`.
- Integrated `Jersey City` from the public tree inventory service referenced by the city's Urban Forests materials.
- Integrated `Arlington` from the official Arlington County `DPR Trees` layer using the county-equivalent jurisdiction boundary.
- Added gray coverage for `Alexandria` after reviewing the official urban-forestry and GIS pages without finding a public single-tree inventory.
- Confirmed `Montgomery County, MD` currently exposes `Tree Planting Locations`, not a countywide single-tree species inventory.
- Official Essex County open-data entry points were reviewed without confirming a verified countywide single-tree species inventory.

## March 2026 New Jersey Municipal Expansion
- Integrated `Hoboken` from the official City of Hoboken public tree inventory ArcGIS layer.
- Integrated `Montclair` from the official Township of Montclair public tree inventory ArcGIS layer.
- Integrated `Newark` from the official Newark public TreeKeeper inventory.
- Integrated `Princeton` from the official Princeton public TreeKeeper inventory.
- Integrated `Millburn`, `Dumont`, `Westwood`, `Rutherford`, and `River Edge` from official municipal public TreeKeeper inventories.

## March 2026 Seattle-Vancouver Corridor Sweep
- Rechecked the Seattle-to-Vancouver corridor beyond already-covered cities.
- Promoted `Surrey` into gray coverage after confirming the official city boundary and re-confirming that the official public tree layers are still partial-only (`Important Trees`, `Park Specimen Trees`), not a citywide single-tree inventory.
- Added gray coverage for `Coquitlam` after confirming the official city boundary and re-checking official GIS services without finding a citywide public single-tree inventory.
- Official site / GIS checks in this round did not confirm citywide public single-tree inventories for `Mount Vernon`, `Burlington`, or `Anacortes`.

## March 2026 Metro Vancouver Follow-up
- `New Westminster`: integrated from the official `Tree Inventory (Active Trees)` ArcGIS layer after confirming the official Metro Vancouver administrative boundary for the City of New Westminster.
- `West Vancouver`: promoted into gray coverage after confirming an official administrative boundary source and re-checking urban-forest materials that still do not expose a public citywide single-tree inventory.
- `Langley City`: promoted into gray coverage after confirming the official Metro Vancouver administrative boundary for the City of Langley, while official tree-data searches still did not confirm a public citywide single-tree inventory.
- `White Rock`: promoted into gray coverage after confirming the official Metro Vancouver administrative boundary for the City of White Rock without finding a public citywide single-tree inventory.

## March 2026 Ontario-Quebec / Mid-Atlantic Sweep
- Integrated `Ottawa` from the official City of Ottawa `Tree Inventory / Inventaire des arbres` ArcGIS layer and official city boundary.
- Integrated `Toronto` from the official Toronto Open Data `Street Tree Data` CSV and official Toronto municipal boundary.
- Integrated `Montreal` from the official Ville de Montréal `Arbres publics sur le territoire de la Ville` CSV; the official jurisdiction boundary is assembled from arrondissement polygons.
- Confirmed `Montgomery County, MD` should remain gray coverage because the official public `Tree Planting Locations` layer is a planting-program dataset, not a countywide single-tree inventory.
- Added gray coverage for `Richmond BC` after confirming the official City of Richmond boundary but not a public citywide single-tree species inventory.

## March 2026 Ontario ArcGIS Expansion
- Integrated `Burlington`, `Cambridge ON`, `Guelph`, `Hamilton`, `Kitchener`, `London`, `Oakville`, `Waterloo`, `Whitby`, and `Windsor` from official Ontario ArcGIS tree inventories.
- Added a reusable Statistics Canada 2024 Census Subdivision boundary path for Ontario municipalities so new Canadian ArcGIS cities can reuse the same official-jurisdiction clipping flow.
- `Oakville` required parsing mixed common/scientific `SPECIES` text, and `Windsor` merges the official `City Trees In Park` and `City Trees In Right Of Way` layers into one city publish result.

## March 2026 Canada Prairie / Atlantic Expansion
- Integrated `Mississauga` and `Peterborough` from official Ontario public ArcGIS tree inventories by reusing the Statistics Canada CSD boundary path added earlier in March.
- Integrated `Saskatoon` from the official City of Saskatoon public tree inventory ArcGIS layer after restricting to the active city-owned `Trees` sublayer rows.
- Integrated `Halifax` from the official Halifax Regional Municipality `Public Trees` ArcGIS layer and added a reusable official HRM polygon path through the published `NSPW HRM Service Exchange Boundary (2022)` service.
- Integrated `Winnipeg` from the official City of Winnipeg `Tree Inventory` SODA dataset and clipped the resulting blossom rows to the official Statistics Canada CSD boundary.

## March 2026 Canada 20-City Expansion
- Integrated `Ajax`, `Barrie`, `Kingston`, `Niagara Falls`, `Thunder Bay`, and `Welland` from official Ontario ArcGIS tree inventories and clipped them to the official Statistics Canada CSD boundaries.
- Added reusable `AB` and `NB` region publishing support plus Statistics Canada 2024 Census Subdivision boundary hints so Alberta and New Brunswick ArcGIS cities can reuse the same official-jurisdiction clipping path.
- Integrated `Calgary`, `St. Albert`, `Chestermere`, `Okotoks`, `Lethbridge`, and `Airdrie` from official Alberta public ArcGIS tree layers.
- Integrated `Kelowna`, `Kamloops`, `Prince George`, `Penticton`, and `Maple Ridge` from official British Columbia public ArcGIS tree layers and clipped them to official Statistics Canada CSD boundaries.
- Integrated `Fredericton` and `Moncton` from official New Brunswick ArcGIS tree inventories; `Moncton` required a small public `BOTNAME` blossom-code mapping because the public layer does not expose readable species text.
- Integrated `Gatineau` from the official National Capital Commission `Remarkable Trees` ArcGIS layer after clipping to the official Gatineau Statistics Canada CSD boundary.

## March 2026 Canada 10-City Follow-up
- Integrated `Edmonton` from the official City of Edmonton `Boulevard / Open Space Trees` SODA dataset after clipping blossom rows to the official Statistics Canada CSD boundary.
- Integrated `Regina`, `Medicine Hat`, `Red Deer`, `Halton Hills`, `Tecumseh`, `Nanaimo`, and `North Vancouver City` from official public ArcGIS single-tree inventories.
- Integrated `Abbotsford` by merging the official city `Tree Inventory 2019` park and street ArcGIS layers, then clipping to the official Statistics Canada CSD boundary.
- Integrated `North Vancouver District` from the official district `Street Trees` downloadable shapefile after clipping the published points to the official Statistics Canada CSD boundary.
- Rechecked `Surrey`; the official public `Important Trees` / `Park Specimen Trees` sources remain partial-only, so it stays gray coverage.

## March 2026 Canada BC / Prairie / Atlantic Follow-up
- Added reusable `PE` region publishing support plus official-boundary hints so `Charlottetown` can reuse the existing Canada publish flow.
- Integrated `Coquitlam`, `Langley Township`, `Port Coquitlam`, and `West Vancouver` from public British Columbia tree layers after clipping to official municipal or Metro Vancouver administrative boundaries.
- Integrated `Grande Prairie` and `Strathcona County` from official Alberta public tree inventories.
- Integrated `Moose Jaw` and `Weyburn` from Saskatchewan public tree inventory services after clipping to the official Statistics Canada CSD boundaries.
- Integrated `Saint John` and `Charlottetown` from Atlantic public ArcGIS tree inventories.
- `Port Coquitlam` merges separate official public park-tree and street-tree layers into one city publish result.

## March 2026 Canada Ontario / Quebec GeoJSON Follow-up
- Integrated `Brampton`, `Cobourg`, `Cornwall`, and `Orangeville` from official Ontario public ArcGIS single-tree inventories and clipped them to the official Statistics Canada CSD boundaries.
- Integrated `Vaughan` from the official York Region `Street Trees` layer after restricting to active `MUNICIPALITY = 'Vaughan'` rows and clipping to the official Vaughan Statistics Canada CSD boundary.
- Integrated `Leduc` from the official City of Leduc public Cityworks trees layer after restricting to active rows and clipping to the official Statistics Canada CSD boundary.
- Integrated `Longueuil`, `Quebec City`, `Repentigny`, and `Saguenay` from official Donnees Quebec GeoJSON tree inventories and clipped them to the official Statistics Canada CSD boundaries.
- Rechecked `County of Brant`; the official public source is valid, but the blossom-filtered publish path currently returns zero in-scope rows inside the official boundary, so it remains out of product for now.

## March 2026 Canada York Region / Metro Vancouver Follow-up
- Integrated `Aurora`, `East Gwillimbury`, `Georgina`, `King`, `Markham`, `Newmarket`, `Richmond Hill`, and `Whitchurch-Stouffville` from the official York Region `Street Trees` ArcGIS layer by reusing municipality-specific filters and official Statistics Canada CSD boundaries.
- Integrated `Port Moody` from the official City of Port Moody `Street Trees Inventory` ArcGIS layer after restricting to operational street trees.
- Integrated `White Rock` from the official City of White Rock `Trees` open-data map service after excluding removed rows and clipping to the official Metro Vancouver administrative boundary.

## March 2026 East Coast / Southern California Follow-up
- Rechecked `Alexandria, VA`; official city urban-forestry and GIS materials still do not expose a verified public single-tree inventory, so it remains gray coverage.
- Rechecked `Montgomery County, MD`; the official public `Tree Planting Locations` layer remains a planting-program dataset rather than a countywide single-tree inventory, so it remains gray coverage.
- Official Essex County open-data entry points were reviewed again without confirming a countywide public single-tree inventory.
- Integrated `Dedham` from the official Town of Dedham public tree inventory ArcGIS layer.
- Integrated `Groton` from the official Town of Groton public tree inventory ArcGIS service after switching the boundary match to the official town county subdivision instead of the smaller Groton city place.
- Integrated `Morristown` from the official Morristown public tree inventory ArcGIS layer.
- Integrated `Richmond, VA` from the official City of Richmond public tree inventory ArcGIS layer while keeping `Richmond (CA)` in gray coverage.
- Integrated `Virginia Beach` from the official City of Virginia Beach `VBTrees` ArcGIS service after excluding non-live status rows.
- Integrated `San Diego` from the official City of San Diego `Trees (Street Trees)` ArcGIS layer using server-side blossom filtering on `COMMON_NAME`.
- Confirmed that official public `Los Angeles` TreeKeeper inventory is available at city scale, but it currently remains not integrated because the blossom-filter path for a ~925k-tree public dataset has not yet been safely implemented.

## March 2026 East Coast ArcGIS Expansion
- Integrated `Brookline` from the official Town of Brookline public tree inventory ArcGIS layer.
- Integrated `Gaithersburg` from the official City of Gaithersburg `Street Trees View` ArcGIS layer.
- Integrated `Newport News` from the official City of Newport News public reviewed-tree ArcGIS layer.
- Integrated `New Bedford` from the public 2023 New Bedford Bartlett tree inventory ArcGIS layer.
- Integrated `Medford` from the public tree inventory ArcGIS layer referenced by the official City of Medford Forestry urban-forest materials.
- Rechecked `Harrisburg`; the official public `Street Trees` layer remains blocked from product publish because species values are short internal codes without a confirmed public lookup table.

## March 2026 East Coast 10-City Expansion
- Integrated `Longmeadow` and `Lynn` from official Massachusetts public tree inventory ArcGIS layers.
- Integrated `Manchester` from the official City of Manchester public Parks and Recreation tree inventory ArcGIS layer.
- Integrated `Providence` from the official City of Providence open-data `Providence Tree Dataset`.
- Integrated `Garrett Park` by parsing the official town-published ArcGIS web map featureCollection and using the explicit `Longitude` / `Latitude` attributes.
- Integrated `Charlottesville`, `Fredericksburg`, and `Norfolk` from official Virginia public tree inventories.
- Integrated `Meadville` from the official City of Meadville public tree inventory ArcGIS layer.
- Integrated `Durham` from the official City of Durham `Trees & Planting Sites` ArcGIS layer after restricting to `present = Tree` rows.
- Rechecked `Salisbury`; the official citywide source is public, but the blossom-filter path returned zero in-scope rows inside the official jurisdiction boundary.
- Rechecked `Fayetteville`; the official citywide `Tree Inventory Phase 1` layer is public, but the blossom-filter path returned zero in-scope rows inside the official jurisdiction boundary.

## March 2026 East Coast TreeKeeper / TreePlotter Expansion
- Integrated `Albany`, `Belmont`, `Newton`, `Somerville`, and `Worcester` from official public TreeKeeper inventories using the existing jurisdiction-boundary clipping path.
- Integrated `Annapolis`, `Fairfax`, `Saratoga Springs`, `Troy`, and `West Hartford` from official public TreePlotter inventories and clipped the resulting blossom rows to official jurisdiction boundaries.
- Reused the existing `ma`, `md`, `ny`, `ct`, and `va` publish flows without database or schema changes.

## March 2026 Vermont Municipal Inventory Expansion
- Integrated `Shelburne`, `Middlebury`, `Winooski`, `Northfield`, `Milton`, `Hinesburg`, `Essex`, `South Burlington`, `Colchester`, and `Randolph` from the official Vermont ANR `Municipal Tree Inventory` ArcGIS layer.
- Added `VT` region and state-FIPS routing so Vermont municipalities can reuse the existing ArcGIS jurisdiction-boundary clipping flow without database changes.
- Reused one statewide official source with municipality-level `TOWN` filters as the fastest east-region expansion path under the current official-source rules.

## March 2026 Texas / Large-City Follow-up
- Integrated `Los Angeles` after implementing the city-scale blossom-filter path against the official public StreetsLA TreeKeeper inventory.
- Integrated `Irvine` from the official City of Irvine `City Trees` ArcGIS layer and official city boundary.
- Integrated `Austin` from the official City of Austin `Tree Inventory` Socrata dataset; blossom rows with projected `longtitude/latitude` values now fall back to the valid GeoJSON `geometry` point before publish.
- Integrated `Dallas` from the official City of Dallas public TreeKeeper inventory linked from the city forestry page.
- Rechecked `Chicago`; official City of Chicago open-data and ArcGIS entry points reviewed in this round did not confirm a public citywide single-tree species inventory.
- Integrated `Houston` from the official City of Houston public `COH Urban Forestry Trees` ArcGIS layer after confirming a stable blossom-filter path on `SPECIES`.

## March 2026 Japan Municipality Pilot
- Integrated `Adachi Ward` from the official Tokyo Metropolitan Government `Street Trees / 街路樹` shapefile, using the published `区部都道（単木単位）` point layer and filtering rows to `足立区`.
- Clipped the Tokyo rows to the official MLIT 2024 administrative boundary (`N03`) for `東京都 / 足立区` before publish.
- Extended the publish and jump pipeline so Japan can be modeled as `country = jp`, `prefecture = tokyo`, and municipality-level `ward` areas without changing the database schema.

## April 2026 Tokyo Ward Expansion
- Reused the same official Tokyo Metropolitan Government `Street Trees / 街路樹` single-tree shapefile and the existing MLIT 2024 administrative-boundary clipping path to add 10 more Tokyo wards without any schema changes.
- Integrated `Chiyoda Ward (379)`, `Edogawa Ward (1518)`, `Kita Ward (410)`, `Koto Ward (1203)`, `Nakano Ward (459)`, `Nerima Ward (1114)`, `Ota Ward (406)`, `Setagaya Ward (463)`, `Shinagawa Ward (293)`, and `Shinjuku Ward (751)`.
- Tokyo now covers `11` wards and `9,152` in-scope blossom trees from the official `区部都道（単木単位）` source.

## April 2026 Japan Municipality Expansion
- Reused the same official Tokyo Metropolitan Government `Street Trees / 街路樹` single-tree shapefile plus MLIT 2024 administrative boundaries to add the remaining `12` Tokyo special wards: `Arakawa Ward (255)`, `Bunkyo Ward (186)`, `Chuo Ward (288)`, `Itabashi Ward (130)`, `Katsushika Ward (232)`, `Meguro Ward (86)`, `Minato Ward (86)`, `Shibuya Ward (186)`, `Suginami Ward (211)`, `Sumida Ward (247)`, `Taito Ward (186)`, and `Toshima Ward (263)`.
- Added `Hino (1)` from the official Tokyo Metropolitan Government `保存樹木・生垣` point shapefile, again clipped to the official MLIT 2024 municipal boundary.
- Added `Inagi (8)`, `Kodaira (6)`, and `Kunitachi (4)` from official Tokyo municipal protected-tree CSVs; direct coordinates were reused when published, and incomplete address rows were geocoded through the official GSI `AddressSearch` endpoint.
- Added `Ebetsu (10)`, `Iwaki (8)`, `Hadano (1)`, and `Chikuma (4)` from official municipal protected-tree pages and CSV/HTML tables, with structured per-tree rows geocoded via the official GSI address-search service when no point coordinates were published.
- Japan now covers `31` municipalities across `5` prefectures and `11,550` in-scope blossom trees, while keeping the same `country -> prefecture -> municipality` publish contract and no schema changes.

## March 2026 Intermountain / Great Lakes Follow-up
- Integrated `Las Vegas` from the official City of Las Vegas `CLV Tree Sites` ArcGIS layer using blossom filtering on `SPP_BOT` / `SPP_COM`.
- Integrated `Salt Lake City` from the official Salt Lake City Public Lands `Urban Forestry Inventory` ArcGIS layer; `Vacant = Yes` rows are excluded before blossom classification.
- Rechecked `Phoenix`; official city tree-map style materials were found, but this round did not confirm a public citywide single-tree species inventory.
- Rechecked `Boise`; a public ArcGIS result labeled `City Maintained Tree Inventory` was found, but its published geometry resolves outside Boise and is treated as a false positive rather than a safe official Boise source.
- Rechecked `Detroit`; official Detroit open-data entry points reviewed in this round did not confirm a public citywide single-tree species inventory.

## March 2026 Zero-Coverage State Expansion
- Integrated `Auburn` from the official City of Auburn public street-tree ArcGIS layer.
- Integrated `Coeur d'Alene` from the official Idaho Department of Lands statewide TreePlotter inventory after clipping points to the official city boundary.
- Integrated `Andover`, `Covington`, `Fargo`, `Lincoln`, and `Tulsa` from official public ArcGIS single-tree inventories.
- Integrated `Albuquerque`, `Grandview Heights`, and `Moorhead` from official public TreePlotter inventories with official jurisdiction-boundary clipping.
- Added `AL / ID / KS / KY / MN / ND / NE / NM / OH / OK` region publish support so these formerly zero-city states can now reuse the standard release path.

## March 2026 Southern California Coastal Corridor
- Integrated `Newport Beach` from the official Newport Beach tree inventory dashboard / ArcGIS layer.
- Integrated `San Dimas` from the official City Owned Trees ArcGIS layer published by the City of San Dimas.
- Integrated `Rancho Palos Verdes` from the official public tree inventory layer linked from the city's GIS services.
- Integrated `Santa Monica` from the official City of Santa Monica `Trees` FeatureServer.
- Integrated `Oxnard` from the official City of Oxnard `Trees` ArcGIS layer.
