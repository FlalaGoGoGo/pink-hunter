# City Coverage Tracker

Last updated: 2026-03-07 (America/Los_Angeles)

## Integrated (In Product)
| Done | City | Included Trees | Boundary Rule | Notes |
|---|---|---:|---|---|
| ✅ | Seattle | 46,114 | Official jurisdiction boundary | Includes UW supplemental points; ornamental cherry keyword sweep rerun |
| ✅ | New York City | 40,685 | Official jurisdiction boundary | Official NYC Parks `2015 Street Tree Census - Tree Data` integrated from NYC Open Data; rows are limited to living trees before blossom filtering |
| ✅ | Toronto | 36,302 | Official jurisdiction boundary | Official City of Toronto `Street Tree Data` CSV integrated from Toronto Open Data using the official municipal boundary shapefile |
| ✅ | Philadelphia | 17,717 | Official jurisdiction boundary | Official Philadelphia Parks & Recreation `PPR Tree Inventory 2025` layer integrated from the city's ArcGIS/metadata catalog |
| ✅ | Montreal | 16,258 | Official jurisdiction boundary | Official Ville de Montréal `Arbres publics sur le territoire de la Ville` CSV integrated; official boundary is assembled from arrondissement polygons |
| ✅ | Ottawa | 12,913 | Official jurisdiction boundary | Official City of Ottawa `Tree Inventory / Inventaire des arbres` ArcGIS layer integrated with blossom-side server filtering and official city boundary |
| ✅ | Boston | 4,488 | Official jurisdiction boundary | Official Analyze Boston `BPRD Trees` download integrated; includes both street and park trees published by Boston Parks and Recreation |
| ✅ | Pittsburgh | 3,691 | Official jurisdiction boundary | Official public Pittsburgh TreeKeeper inventory domain integrated; blossom names are parsed from `SITE_ATTR6` |
| ✅ | Jersey City | 2,148 | Official jurisdiction boundary | Public Jersey City tree inventory service integrated from the city-referenced Urban Forests materials and official jurisdiction boundary |
| ✅ | Cambridge | 1,954 | Official jurisdiction boundary | Official City of Cambridge `Street Trees` shapefile integrated; only current `SiteType = Tree` rows are included |
| ✅ | Baltimore | 1,920 | Official jurisdiction boundary | Official Baltimore city forestry tree layer integrated from `gis.baltimorecity.gov`; botanical names come from `SPP` |
| ✅ | Arlington | 1,882 | Official jurisdiction boundary | Official Arlington County `DPR Trees` layer integrated using the official county-equivalent jurisdiction boundary |
| ✅ | San Francisco | 24,099 | Official jurisdiction boundary | Official San Francisco Public Works `Street Tree List` integrated from the city open-data portal |
| ✅ | San Jose | 18,021 | Official jurisdiction boundary | Official City of San Jose `Street Tree` layer integrated from the city open-data ArcGIS service |
| ✅ | Palo Alto | 4,996 | Official jurisdiction boundary | Official City of Palo Alto `Tree Data` layer integrated from the city open GIS portal; official boundary comes from the city-published boundary shapefile |
| ✅ | Oakland | 3,977 | Official jurisdiction boundary | Official City of Oakland `Oakland Street Trees` Socrata dataset integrated from the city open-data portal |
| ✅ | Berkeley | 3,973 | Official jurisdiction boundary | Official City of Berkeley public shapefile inventory integrated from the city ArcGIS item download |
| ✅ | Cupertino | 1,299 | Official jurisdiction boundary | Official City of Cupertino `Trees` layer integrated from the city GIS portal |
| ✅ | Fremont | 5,555 | Official jurisdiction boundary | Official City of Fremont public TreePlotter inventory integrated from the city urban-forestry portal plus public species lookup table |
| ✅ | Concord | 4,103 | Official jurisdiction boundary | Official City of Concord public TreePlotter inventory integrated from the city tree-inventory portal plus official GIS boundary |
| ✅ | Salinas | 4,535 | Official jurisdiction boundary | Official City of Salinas OpenDataSoft `Tree Inventory` dataset integrated from the city open-data portal |
| ✅ | South San Francisco | 784 | Official jurisdiction boundary | Official City of South San Francisco public TreeKeeper inventory integrated from the city trees page plus official GIS boundary |
| ✅ | Washington DC | 16,533 | Official jurisdiction boundary | Urban Tree Canopy (DDOT); ornamental cherry cultivar mapping expanded |
| ✅ | Vancouver BC | 34,369 | Official jurisdiction boundary | Official City of Vancouver `public-trees` ODS dataset integrated; boundary polygon derived from official city-boundary line dataset |
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

## Gray Coverage (Official Boundary Resolved, No Official Public Tree Dataset)
| Done | City | Status | Boundary Rule | Notes |
|---|---|---|---|---|
| 🩶 | Alexandria | In gray coverage | Official jurisdiction boundary | Official City of Alexandria urban-forestry and GIS pages were reviewed, but no public single-tree species inventory was confirmed |
| 🩶 | Burnaby | In gray coverage | Official jurisdiction boundary | Official Burnaby GIS/open-data sources were reviewed; no public single-tree species inventory was confirmed |
| 🩶 | Beaverton | In gray coverage | Official jurisdiction boundary | Official inventory web maps exist, but the raw city tree inventory service currently requires a token and is not publicly queryable for stable ETL access |
| 🩶 | Delta | In gray coverage | Official jurisdiction boundary | Official Delta GIS/open-data sources were reviewed; no public single-tree species inventory was confirmed |
| 🩶 | Alameda | In gray coverage | Official jurisdiction boundary | Official city tree and urban-forest materials were reviewed, but no verified public citywide single-tree dataset was confirmed in this round |
| 🩶 | Daly City | In gray coverage | Official jurisdiction boundary | Official city urban-forestry and GIS entry points were reviewed, but no verified public citywide single-tree species dataset was confirmed in this round |
| 🩶 | Gresham | In gray coverage | Official jurisdiction boundary | Official ArcGIS search and city-site checks did not confirm a public citywide single-tree species dataset |
| 🩶 | Hayward | In gray coverage | Official jurisdiction boundary | Official city urban-forestry and GIS entry points were reviewed, but no verified public citywide single-tree species dataset was confirmed in this round |
| 🩶 | Hillsboro | In gray coverage | Official jurisdiction boundary | Official ArcGIS search and city-site checks did not confirm a public citywide single-tree species dataset |
| 🩶 | Monterey | In gray coverage | Official jurisdiction boundary | Official city tree standards and GIS entry points were reviewed, but no public citywide single-tree species dataset was confirmed |
| 🩶 | Montgomery County, MD | In gray coverage | Official jurisdiction boundary | Official Montgomery County GIS layers were reviewed; the public `Tree Planting Locations` layer is a planting-program dataset rather than a countywide single-tree inventory |
| 🩶 | Mountain View | In gray coverage | Official jurisdiction boundary | Official city forestry materials were reviewed, but no public citywide single-tree species dataset was confirmed |
| 🩶 | Napa | In gray coverage | Official jurisdiction boundary | Official ArcGIS and city data portal searches did not confirm a public citywide single-tree species dataset |
| 🩶 | Redwood City | In gray coverage | Official jurisdiction boundary | Official city GIS and public-works materials were reviewed, but no verified public citywide single-tree dataset was confirmed in this round |
| 🩶 | Richmond | In gray coverage | Official jurisdiction boundary | Official Richmond, CA ArcGIS and city data searches did not confirm a public citywide public single-tree species dataset |
| 🩶 | Richmond BC | In gray coverage | Official jurisdiction boundary | Official City of Richmond GIS boundary services were confirmed, but no public citywide single-tree species inventory was confirmed in this round |
| 🩶 | Sacramento | In gray coverage | Official jurisdiction boundary | Official city pages and open-data entry points were checked, but no public citywide single-tree species dataset was confirmed |
| 🩶 | Saanich | In gray coverage | Official jurisdiction boundary | Official Saanich GIS/open-data sources were reviewed; no public single-tree species inventory was confirmed |
| 🩶 | Salem | In gray coverage | Official jurisdiction boundary | Official ArcGIS and city GIS searches did not confirm a public citywide single-tree species dataset |
| 🩶 | Santa Cruz | In gray coverage | Official jurisdiction boundary | Official ArcGIS and city GIS searches did not confirm a public citywide single-tree species dataset |
| 🩶 | Santa Clara | In gray coverage | Official jurisdiction boundary | Official city urban-forest materials were reviewed, but no public citywide single-tree species dataset was confirmed |
| 🩶 | Santa Rosa | In gray coverage | Official jurisdiction boundary | Official city GIS results found fire-damaged tree-removal layers, not a citywide public single-tree inventory |
| 🩶 | Stockton | In gray coverage | Official jurisdiction boundary | Official ArcGIS and city GIS searches did not confirm a public citywide single-tree species dataset |
| 🩶 | Sunnyvale | In gray coverage | Official jurisdiction boundary | County and city GIS sources were reviewed, but no verified public citywide single-tree species dataset was confirmed |
| 🩶 | Tigard | In gray coverage | Official jurisdiction boundary | Official ArcGIS results exposed an ash-tree inventory, not a citywide public single-tree species inventory |

## Validated, Not Yet Integrated
| Done | City | Estimated In-Scope Count | Status | Blocker |
|---|---|---:|---|---|
| ⏳ | Mercer Island | 803 (Town Center only) | Partial-only | Official urban-forestry page documents a 2018 Town Center street-tree inventory, but a verified citywide public single-tree endpoint is still not confirmed |
| ⏳ | Bremerton | Unknown | Blocked public map | Official Park Tree Map web map exists under a city account, but the underlying feature service currently returns `403 Forbidden` to direct public queries |
| ⏳ | Poulsbo | 75 | Partial-only | Official `Historic Trees of Poulsbo` feature service is public, but it is a curated historic-tree layer, not a citywide public inventory |
| ⏳ | Pasco | Unknown | Partial-only | Official city content found in this round was a `Volunteer Park Tree Walk` map, not a citywide public single-tree inventory |

## Investigated (Blocked / Not Usable Yet)
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
| ⚠️ | Olympia | Not usable yet | Search turned up a 2007 street-tree layer owned by a non-city account; no current official city single-tree species layer was confirmed |
| ⚠️ | Bothell | Not usable yet | Official Urban Forest Management Plan references a street-tree inventory summary PDF, but no public raw single-tree species endpoint was confirmed |
| ⚠️ | West Vancouver | Boundary blocked | Official mapping entry points exist, but the public portal is currently blocked by Cloudflare from this ETL environment, so an official boundary geometry could not be resolved |
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
| ⚠️ | Ferndale | False positive search hit | Public ArcGIS result in this round was City of Ferndale, Michigan tree data, not a verified Ferndale, WA city inventory |
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
| ⚠️ | Vancouver WA | Not usable yet | Official city geohub search in this round surfaced urban-tree-canopy and signage inventory layers, but not a public single-tree species inventory |
| ⚠️ | Newark / Essex County, NJ | Not found yet | Official city and county open-data entry points were reviewed, but no verified public citywide/countywide single-tree species inventory was confirmed |
| ⚠️ | Mount Vernon | Not found yet | Official city GIS / urban-forestry entry points reviewed in this round did not confirm a public citywide single-tree inventory |
| ⚠️ | Burlington, WA | Not found yet | Official city pages reviewed in this round did not confirm a public citywide single-tree inventory |
| ⚠️ | Anacortes | Not found yet | Official city GIS pages reviewed in this round did not confirm a public citywide single-tree inventory |
| ⚠️ | Surrey | Partial-only | Official Surrey Open Data exposes `Important Trees` and `Park Specimen Trees`, but not a citywide public single-tree inventory |
| ⚠️ | White Rock | Not found yet | Official city open-data entry points were checked in this round, but no public citywide single-tree inventory was confirmed |
| ⚠️ | New Westminster | Not found yet | Official ArcGIS Hub search did not confirm a public citywide single-tree inventory in this round |
| ⚠️ | Coquitlam | Not found yet | Official open-data / ArcGIS searches did not confirm a public citywide single-tree inventory in this round |
| ⚠️ | Abbotsford | Not found yet | Official city maps / GIS entry points reviewed in this round did not confirm a public citywide single-tree inventory |
| ⚠️ | Edmonds / Mukilteo / Mountlake Terrace / Mill Creek | Not found yet | No reliable official public single-tree species point layers confirmed yet |
| ⚠️ | Tukwila / Des Moines / Maple Valley / Covington / Auburn | Not found or rejected | No reliable official city-level single-tree + species point layers, or false-geography matches |

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
- Integrated `Cupertino` from the official City of Cupertino GIS `Trees` layer.
- Integrated `Oakland` from the official City of Oakland `Oakland Street Trees` open-data dataset.
- Added gray coverage for `Mountain View`, `Sacramento`, `Santa Clara`, `Sunnyvale`, `Napa`, `Richmond`, `Santa Cruz`, `Santa Rosa`, and `Stockton` after city-site and official data portal review did not confirm a public citywide single-tree species dataset.
- Fixed a bad legacy `Palo Alto` boundary cache by switching the city boundary back to the official Census place geometry; this removed the incorrect East Bay pink polygon that had been covering Hayward / Livermore / Fremont in the map UI.

## March 2026 BC Expansion
- Integrated `Vancouver BC` from the official City of Vancouver OpenDataSoft `public-trees` dataset.
- Integrated `Victoria BC` from the official City of Victoria `Tree Species (Parks trees database)` layer.
- `Vancouver BC` boundary is sourced from the official City of Vancouver `city-boundary` dataset and converted from the published legal boundary line into a polygon for coverage rendering.
- `Federal Way` was rechecked and downgraded from candidate status after the accessible hosted service turned out to be street lights, not trees.
- Added gray-coverage boundary support for `Burnaby`, `Delta`, and `Saanich` where official city boundaries are public but no official public single-tree species dataset is currently available.
- Rechecked `Richmond`, `West Vancouver`, and `Langford`; they remain excluded from coverage because the official boundary geometry is not publicly queryable in a stable ETL path yet.
- Rechecked `Richmond`; official boundary resolution now works, so the city moved into gray coverage rather than remaining excluded.

## March 2026 California / Oregon Expansion
- Integrated `Milpitas`, `San Mateo`, `San Rafael`, `Salinas`, and `Fremont` from official city-published public tree datasets.
- Integrated `Concord` from the official City of Concord TreePlotter inventory and official city GIS boundary.
- Integrated `South San Francisco` from the official city-linked TreeKeeper inventory and official city GIS boundary.
- `Fremont` required two specific parser fixes before product rows could be emitted:
  - EWKB point decoding with `SRID=3857`
  - species-name resolution through the public `species` lookup table rather than integer foreign keys in `trees`
- Added gray coverage for `Redwood City`, `Alameda`, `Hayward`, and `Daly City` after official-source review did not confirm a public citywide single-tree species dataset.
- Added gray coverage for `Beaverton`, `Gresham`, `Hillsboro`, `Salem`, and `Tigard` after official-source review did not confirm a public citywide single-tree species dataset or raw public endpoint.

## March 2026 Northeast Expansion
- Integrated `New York City` from the official NYC Parks `2015 Street Tree Census - Tree Data` dataset on NYC Open Data.
- Integrated `Philadelphia` from the official Philadelphia Parks & Recreation `PPR Tree Inventory 2025` layer.
- Integrated `Pittsburgh` from the official public Pittsburgh TreeKeeper inventory domain.
- Integrated `Cambridge` from the official City of Cambridge `Street Trees` shapefile download.
- Integrated `Boston` from the official Analyze Boston `BPRD Trees` download.
- Integrated `Baltimore` from the official city forestry tree layer on `gis.baltimorecity.gov`.
- Integrated `Jersey City` from the public tree inventory service referenced by the city's Urban Forests materials.
- Integrated `Arlington` from the official Arlington County `DPR Trees` layer using the county-equivalent jurisdiction boundary.
- Added gray coverage for `Alexandria` after reviewing the official urban-forestry and GIS pages without finding a public single-tree inventory.
- Confirmed `Montgomery County, MD` currently exposes `Tree Planting Locations`, not a countywide single-tree species inventory.
- Official Newark / Essex County open-data entry points were reviewed without confirming a verified public citywide/countywide single-tree species inventory.

## March 2026 Seattle-Vancouver Corridor Sweep
- Rechecked the Seattle-to-Vancouver corridor beyond already-covered cities.
- Confirmed `Surrey` has official partial tree layers (`Important Trees`, `Park Specimen Trees`) but not a citywide public single-tree inventory.
- Official site / GIS checks in this round did not confirm citywide public single-tree inventories for `Mount Vernon`, `Burlington`, `Anacortes`, `White Rock`, `New Westminster`, `Coquitlam`, or `Abbotsford`.

## March 2026 Ontario-Quebec / Mid-Atlantic Sweep
- Integrated `Ottawa` from the official City of Ottawa `Tree Inventory / Inventaire des arbres` ArcGIS layer and official city boundary.
- Integrated `Toronto` from the official Toronto Open Data `Street Tree Data` CSV and official Toronto municipal boundary.
- Integrated `Montreal` from the official Ville de Montréal `Arbres publics sur le territoire de la Ville` CSV; the official jurisdiction boundary is assembled from arrondissement polygons.
- Confirmed `Montgomery County, MD` should remain gray coverage because the official public `Tree Planting Locations` layer is a planting-program dataset, not a countywide single-tree inventory.
- Added gray coverage for `Richmond BC` after confirming the official City of Richmond boundary but not a public citywide single-tree species inventory.
