#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
import datetime as dt
import hashlib
import json
import os
import re
import ssl
import subprocess
import sys
import tempfile
import io
import shutil
import time
import urllib.request
import requests
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.build_data import (
    ARLINGTON_DATASET_PAGE,
    ARLINGTON_TREES_LAYER,
    BALTIMORE_DATASET_PAGE,
    BALTIMORE_TREES_LAYER,
    BOSTON_DATASET_PAGE,
    BOSTON_TREES_GEOJSON,
    CAMBRIDGE_DATASET_PAGE,
    CAMBRIDGE_STREET_TREES_ZIP,
    CONCORD_BOUNDARY_LAYER,
    CONCORD_DATASET_PAGE,
    CONCORD_TREEPLOTTER_URL,
    FREMONT_BOUNDARY_LAYER,
    FREMONT_DATASET_PAGE,
    FREMONT_TREEPLOTTER_URL,
    NYC_DATASET,
    NYC_DATASET_PAGE,
    NYC_METADATA,
    PHILADELPHIA_DATASET_PAGE,
    PHILADELPHIA_LAYER,
    JERSEY_CITY_DATASET_PAGE,
    JERSEY_CITY_TREES_LAYER,
    MONTREAL_DATASET_PAGE,
    MONTREAL_TREES_CSV,
    MILPITAS_LAYER,
    OTTAWA_DATASET_PAGE,
    OTTAWA_TREES_LAYER,
    PUBLIC_DATA_DIR,
    REGION_LABELS,
    SPECIES_GROUPS,
    MAPPING_PATH,
    NORMALIZED_DIR,
    SAN_MATEO_DATASET_PAGE,
    SAN_MATEO_LAYER,
    SAN_RAFAEL_DATASET_PAGE,
    SAN_RAFAEL_TREES_LAYER,
    SOUTH_SF_BOUNDARY_LAYER,
    SOUTH_SF_DATASET_PAGE,
    SOUTH_SF_GRIDS_ENDPOINT,
    SOUTH_SF_SEARCH_ENDPOINT,
    SUBTYPE_MAPPING_PATH,
    TORONTO_DATASET_PAGE,
    assign_zip_code,
    canonical_ownership,
    classify_tree_record,
    decode_wkb_point_hex,
    expand_abbreviated_botanical_name,
    fetch_all_features,
    fetch_binary,
    fetch_json,
    fetch_ods_export_rows,
    fetch_soda_count,
    fetch_soda_rows,
    fetch_us_city_zip_index,
    generic_scientific_name_for_common_hint,
    iso_from_epoch,
    load_mapping,
    load_city_boundary_geometry,
    load_zipped_point_shapefile_rows,
    load_zipped_shapefile,
    load_subtype_mapping,
    normalize_scientific_name,
    point_in_geometry,
    post_form_with_curl,
    slugify_token,
    title_case_if_upper,
    web_mercator_to_lon_lat,
)

NORMALIZED_HEADER = [
    "id",
    "city",
    "source_dataset",
    "scientific_raw",
    "scientific_normalized",
    "common_name",
    "subtype_name",
    "zip_code",
    "species_group",
    "ownership",
    "ownership_raw",
    "lat",
    "lon",
    "included",
]

MILPITAS_DATASET_PAGE = "https://services8.arcgis.com/OPmRdssd8jj0bT5H/arcgis/rest/services/Trees_RO/FeatureServer/0"
SAN_RAFAEL_BOUNDARY_DATASET_PAGE = "https://www.arcgis.com/home/item.html?id=4c64d7f5f8384283ae83be8fd861afb4"
TREEPLOTTER_CLIENT_VERSION = "v3.9.65"
FREMONT_DB_ENDPOINT = "https://pg-cloud.com/main/server/db.php"
SALINAS_DATASET = "https://cityofsalinas.opendatasoft.com/api/explore/v2.1/catalog/datasets/tree-inventory"
PITTSBURGH_BASE = "https://pittsburghpa.treekeepersoftware.com"
PITTSBURGH_SEARCH_ENDPOINT = f"{PITTSBURGH_BASE}/cffiles/search.cfc"
PITTSBURGH_GRIDS_ENDPOINT = f"{PITTSBURGH_BASE}/cffiles/grids.cfc"
TORONTO_STREET_TREE_ALT_CSV = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/6ac4569e-fd37-4cbc-ac63-db3624c5f6a2/resource/5930412c-408e-4ee3-b473-56a790c9dfb7/download/street-tree-data_csv.csv"
NEW_WESTMINSTER_TREES_LAYER = "https://services3.arcgis.com/A7O8YnTNtzRPIn7T/arcgis/rest/services/Tree_Inventory_(PROD)_4_view/FeatureServer/0"
NEW_WESTMINSTER_DATASET_PAGE = "https://services3.arcgis.com/A7O8YnTNtzRPIn7T/arcgis/rest/services/Tree_Inventory_(PROD)_4_view/FeatureServer"
SAN_DIEGO_TREES_LAYER = "https://webmaps.sandiego.gov/arcgis/rest/services/DSD/Environment/MapServer/20"
SAN_DIEGO_DATASET_PAGE = "https://webmaps.sandiego.gov/arcgis/rest/services/DSD/Environment/MapServer/20"
HOUSTON_TREES_LAYER = "https://services.arcgis.com/NummVBqZSIJKUeVR/arcgis/rest/services/COH_UrbanForestry_Trees_VIEW_ONLY/FeatureServer/0"
HOUSTON_DATASET_PAGE = "https://www.arcgis.com/home/item.html?id=ef3851fa482d41d49cf2d82a399919f5"
DENVER_TREES_LAYER = "https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services/ODC_PARK_TREEINVENTORY_P/FeatureServer/241"
DENVER_DATASET_PAGE = "https://opendata-geospatialdenver.hub.arcgis.com/datasets/public-tree-inventory"
LAS_VEGAS_TREES_LAYER = "https://services1.arcgis.com/F1v0ufATbBQScMtY/ArcGIS/rest/services/CLV_Tree_Sites/FeatureServer/0"
LAS_VEGAS_DATASET_PAGE = "https://services1.arcgis.com/F1v0ufATbBQScMtY/ArcGIS/rest/services/CLV_Tree_Sites/FeatureServer"
SALT_LAKE_CITY_TREES_LAYER = "https://services.arcgis.com/mMBpeYj0vPFotzbe/arcgis/rest/services/Urban_Forestry_Inventory/FeatureServer/0"
SALT_LAKE_CITY_DATASET_PAGE = "https://www.slc.gov/parks/urban-forestry/"
LOS_ANGELES_STREETSLA_PAGE = "https://streetsla.lacity.org/tree-inventory-and-maintenance"
LOS_ANGELES_TREEKEEPER_BASE = "https://losangelesca.treekeepersoftware.com"
LOS_ANGELES_FACILITY_ID = 7
BURBANK_TREEKEEPER_BASE = "https://burbankca.treekeepersoftware.com"
AUSTIN_DATASET = "https://data.austintexas.gov/resource/wrik-xasw.json"
AUSTIN_DATASET_PAGE = "https://data.austintexas.gov/Environment/Tree-Inventory/wrik-xasw"
DALLAS_TREEKEEPER_BASE = "https://dallastx.treekeepersoftware.com"
DALLAS_DATASET_PAGE = "https://dallas.gov/projects/forestry/Pages/inventory.aspx"
IRVINE_TREES_LAYER = "https://gis.cityofirvine.org/arcgis/rest/services/City_Landscape/MapServer/0"
IRVINE_BOUNDARY_LAYER = "https://gis.cityofirvine.org/arcgis/rest/services/City_Landscape/MapServer/3"
IRVINE_DATASET_PAGE = "https://gis.cityofirvine.org/arcgis/rest/services/City_Landscape/MapServer/0"
MOUNTAIN_VIEW_TREES_LAYER = "https://services8.arcgis.com/A76GjgcBUTTcwFGS/arcgis/rest/services/Heritage_Trees_JM/FeatureServer/10"
MOUNTAIN_VIEW_DATASET_PAGE = "https://services8.arcgis.com/A76GjgcBUTTcwFGS/arcgis/rest/services/Heritage_Trees_JM/FeatureServer/10"
SACRAMENTO_TREES_LAYER = "https://services5.arcgis.com/54falWtcpty3V47Z/arcgis/rest/services/City_Maintained_Trees/FeatureServer/0"
SACRAMENTO_DATASET_PAGE = "https://data.cityofsacramento.org/datasets/b9b716e09b5048179ab648bb4518452b_0/explore"
WEST_SACRAMENTO_TREES_LAYER = "https://gis.cityofwestsacramento.org/server/rest/services/Tree_Inventory_MIL1/MapServer/0"
WEST_SACRAMENTO_DATASET_PAGE = "https://gis.cityofwestsacramento.org/server/rest/services/Tree_Inventory_MIL1/MapServer/0"
SUNNYVALE_TREES_LAYER = "https://services.arcgis.com/NkcnS0qk4w2wasOJ/arcgis/rest/services/Tree_Inventories_in_Santa_Clara_County_WFL1/FeatureServer/0"
SUNNYVALE_DATASET_PAGE = "https://www.arcgis.com/home/item.html?id=58f9d735c5b94915ba5374c82415a26f"
SANTA_CLARA_COUNTY_TREES_DATASET_PAGE = SUNNYVALE_DATASET_PAGE
PASADENA_TREES_LAYER = "https://services2.arcgis.com/zNjnZafDYCAJAbN0/arcgis/rest/services/Street_ROW_Trees/FeatureServer/0"
PASADENA_DATASET_PAGE = "https://services2.arcgis.com/zNjnZafDYCAJAbN0/arcgis/rest/services/Street_ROW_Trees/FeatureServer"
BEVERLY_HILLS_TREES_LAYER = "https://services5.arcgis.com/7CXE3aevo18HlHBC/arcgis/rest/services/Trees_of_Beverly_Hills/FeatureServer/0"
BEVERLY_HILLS_DATASET_PAGE = "https://services5.arcgis.com/7CXE3aevo18HlHBC/arcgis/rest/services/Trees_of_Beverly_Hills/FeatureServer"
EL_SEGUNDO_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/TreeInvElSegundo_Public/FeatureServer/0"
EL_SEGUNDO_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/TreeInvElSegundo_Public/FeatureServer"
BELL_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/City_of_Bell_Tree_Inventory_Benefits_WFL1/FeatureServer/0"
BELL_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/City_of_Bell_Tree_Inventory_Benefits_WFL1/FeatureServer"
SAN_FERNANDO_TREES_LAYER = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/San_Fernando_CAL_FIRE_Tree_Layer_view/FeatureServer/0"
SAN_FERNANDO_DATASET_PAGE = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/San_Fernando_CAL_FIRE_Tree_Layer_view/FeatureServer"
AZUSA_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/City_of_Azusa_Tree_Inventory_Benefits_WFL1/FeatureServer/0"
AZUSA_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/City_of_Azusa_Tree_Inventory_Benefits_WFL1/FeatureServer"
FULLERTON_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Fullerton_Tree_Benefits_WFL1/FeatureServer/0"
FULLERTON_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Fullerton_Tree_Benefits_WFL1/FeatureServer"
ANAHEIM_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/WebMap_Anaheim_AllLayers_WFL1/FeatureServer/0"
ANAHEIM_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/WebMap_Anaheim_AllLayers_WFL1/FeatureServer"
POMONA_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/CityOfPomona_iTreeBenefits_CanopyCover_WFL1/FeatureServer/0"
POMONA_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/CityOfPomona_iTreeBenefits_CanopyCover_WFL1/FeatureServer"
SANTA_CLARITA_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/CityofSantaClarita_iTreeBenefits_CanopyCover_WFL1/FeatureServer/0"
SANTA_CLARITA_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/CityofSantaClarita_iTreeBenefits_CanopyCover_WFL1/FeatureServer"
MONTEREY_PARK_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/MontereyParkiTreebenefitsSummary_XYTableToPoint/FeatureServer/0"
MONTEREY_PARK_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/MontereyParkiTreebenefitsSummary_XYTableToPoint/FeatureServer"
RANCHO_CUCAMONGA_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Rancho_Cucamonga_Tree_Benefits_WFL1/FeatureServer/0"
RANCHO_CUCAMONGA_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Rancho_Cucamonga_Tree_Benefits_WFL1/FeatureServer"
MAYWOOD_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Maywood_iTree_Inventory_WFL1/FeatureServer/0"
MAYWOOD_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Maywood_iTree_Inventory_WFL1/FeatureServer"
COSTA_MESA_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Costa_Mesa_Tree_benefits/FeatureServer/0"
COSTA_MESA_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Costa_Mesa_Tree_benefits/FeatureServer"
RIVERSIDE_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/CityOfRiverside_iTreeBenefits_WFL1/FeatureServer/0"
RIVERSIDE_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/CityOfRiverside_iTreeBenefits_WFL1/FeatureServer"
LA_CANADA_FLINTRIDGE_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/LaCanadaFlintrid_Homepage_Inventory/FeatureServer/0"
LA_CANADA_FLINTRIDGE_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/LaCanadaFlintrid_Homepage_Inventory/FeatureServer"
FONTANA_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Fontana_iTree_Inv/FeatureServer/0"
FONTANA_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/Fontana_iTree_Inv/FeatureServer"
WEST_HOLLYWOOD_DATASET_PAGE = "https://data.weho.org/Infrastructure/City-Tree-Inventory/qqwt-wx9z"
WEST_HOLLYWOOD_API = "https://data.weho.org/resource/qqwt-wx9z.json"
HOBOKEN_TREES_LAYER = "https://services8.arcgis.com/LDmC4ZVHdfKcEzxl/arcgis/rest/services/2023_Tree_Inventory_/FeatureServer/0"
HOBOKEN_DATASET_PAGE = "https://services8.arcgis.com/LDmC4ZVHdfKcEzxl/arcgis/rest/services/2023_Tree_Inventory_/FeatureServer"
MORRISTOWN_TREES_LAYER = "https://services.arcgis.com/xhDV83hFoiDFnMbw/arcgis/rest/services/Legacy_Trees_2021/FeatureServer/0"
MORRISTOWN_DATASET_PAGE = "https://services.arcgis.com/xhDV83hFoiDFnMbw/arcgis/rest/services/Legacy_Trees_2021/FeatureServer"
LINDEN_TREES_LAYER = "https://services.arcgis.com/VgmyyKiMPvUPgldo/arcgis/rest/services/Linden_Tree_Survey/FeatureServer/0"
LINDEN_DATASET_PAGE = "https://services.arcgis.com/VgmyyKiMPvUPgldo/arcgis/rest/services/Linden_Tree_Survey/FeatureServer"
MONTCLAIR_TREES_LAYER = "https://services9.arcgis.com/QHXEWAb0pE2rvfbb/arcgis/rest/services/Montclair_Trees_2017_WFL1/FeatureServer/0"
MONTCLAIR_DATASET_PAGE = "https://services9.arcgis.com/QHXEWAb0pE2rvfbb/arcgis/rest/services/Montclair_Trees_2017_WFL1/FeatureServer"
NEWPORT_BEACH_TREES_LAYER = "https://nbgis.newportbeachca.gov/arcgis/rest/services/DashBuildingPermits/MapServer/58"
NEWPORT_BEACH_DATASET_PAGE = "https://nbgis.newportbeachca.gov/gispub/Dashboards/TreeInventoryDash.htm"
THOUSAND_OAKS_TREES_LAYER = "https://gis.toaks.gov/server/rest/services/Landscape/MSLandscapeAssets/MapServer/3"
THOUSAND_OAKS_DATASET_PAGE = "https://gis.toaks.gov/server/rest/services/Landscape/MSLandscapeAssets/MapServer/3"
CORONA_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/WebMap_Corona_AllLayers_WFL1/FeatureServer/0"
CORONA_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/WebMap_Corona_AllLayers_WFL1/FeatureServer"
BUENA_PARK_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/Buena_Park_iTree_Benefits_WFL1/FeatureServer/1"
BUENA_PARK_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/Buena_Park_iTree_Benefits_WFL1/FeatureServer"
LA_VERNE_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/City_of_La_Verne_Tree_Benefits_Map_WFL1/FeatureServer/1"
LA_VERNE_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/City_of_La_Verne_Tree_Benefits_Map_WFL1/FeatureServer"
YORBA_LINDA_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/WebMap_YorbaLinda_AllLayers_WFL1/FeatureServer/0"
YORBA_LINDA_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/WebMap_YorbaLinda_AllLayers_WFL1/FeatureServer"
SAN_DIMAS_TREES_LAYER = "https://arcgis.sandimasca.gov/server/rest/services/City_Owned_Trees/FeatureServer/15"
SAN_DIMAS_DATASET_PAGE = "https://files.sandimasca.gov/departments/parks_and_recreation/trees/index.php"
RANCHO_PALOS_VERDES_TREES_LAYER = "https://gis.rpvca.gov/server/rest/services/Public_Services_Public/MapServer/23"
RANCHO_PALOS_VERDES_DATASET_PAGE = "https://www.rpvca.gov/869/GIS-Services"
SANTA_MONICA_TREES_LAYER = "https://gis.santamonica.gov/server/rest/services/Trees/FeatureServer/0"
SANTA_MONICA_DATASET_PAGE = "https://data.sustainablesm.org/datasets/e82j-fp4t"
OXNARD_TREES_LAYER = "https://maps.oxnard.org/arcgis/rest/services/ParksLayers/MapServer/1"
OXNARD_DATASET_PAGE = "https://maps.oxnard.org/portal/apps/webappviewer/index.html?id=2b5e4c2ecf4a49fa82d3ecf924ff8ad7"
SANTA_BARBARA_TREES_LAYER = "https://gisportal.santabarbaraca.gov/server1/rest/services/CitySantaBarbara/MapServer/246"
SANTA_BARBARA_DATASET_PAGE = "https://www.santabarbaraca.gov/gov/depts/pw/urban_forest/default.asp"
GOLETA_TREES_LAYER = "https://services7.arcgis.com/1sU4ryVt4fUb3UBC/arcgis/rest/services/Street_Tree_Inventory_3_19_2024/FeatureServer/0"
GOLETA_DATASET_PAGE = "https://www.cityofgoleta.org/your-city/public-works/street-trees"
REDONDO_BEACH_TREES_LAYER = "https://services6.arcgis.com/4Y3DUWGj4Rq1ajvv/arcgis/rest/services/WCA_Tree_Inv_Rendondo_Beach/FeatureServer/0"
REDONDO_BEACH_DATASET_PAGE = "https://www.redondo.org/depts/public_works/gis/default.asp"
ARCADIA_TREES_LAYER = "https://services3.arcgis.com/XyWu1kJH1LHR1VkH/arcgis/rest/services/CityOfArcadiaTrees/FeatureServer/0"
ARCADIA_DATASET_PAGE = "https://www.arcgis.com/home/item.html?id=870dee983f2448f8a6438a6f1a8487f3"
DANA_POINT_TREES_LAYER = "https://services7.arcgis.com/mRLEu9cKL0xMY05m/arcgis/rest/services/DP_Trees/FeatureServer/0"
DANA_POINT_DATASET_PAGE = "https://www.cityofdanapoint.org/Home/Components/ServiceDirectory/ServiceDirectory/25/1743"
PLEASANTON_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/TreeInvPleasanton_Public/FeatureServer/0"
PLEASANTON_DATASET_PAGE = "https://www.cityofpleasantonca.gov/our-government/public-works/landscape-architecture/"
LODI_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/TreeInvLodiElectric/FeatureServer/0"
LODI_DATASET_PAGE = "https://www.lodi.gov/552/Trees"
CITRUS_HEIGHTS_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/ArcGIS/rest/services/Citrus_Heights_iTree_Benefits/FeatureServer/0"
CITRUS_HEIGHTS_DATASET_PAGE = "https://www.citrusheights.net/1416/Urban-Forestry"
POWAY_TREES_LAYER = "https://powaygis.poway.org/powaygis/rest/services/Public/PowHUB_Environment_Hydrology_Parks_Layers/MapServer/2"
POWAY_DATASET_PAGE = "https://poway.org/293/GIS-Maps"
TORRANCE_TREES_LAYER = "https://services1.arcgis.com/38fAqAZVRCrVtPUU/arcgis/rest/services/Civic_Center_Master_Plan_Tree_Layer/FeatureServer/0"
TORRANCE_DATASET_PAGE = "https://www.torranceca.gov/our-city/community-development/planning/civic-center-master-plan"
VENTURA_TREES_LAYER = "https://map.cityofventura.net/arcgis/rest/services/CityShift/searchpublic/MapServer/23"
GLENDALE_TREES_LAYER = "https://services2.arcgis.com/B282VrEXeknzSool/arcgis/rest/services/Glendale_Tree_Survey_updated/FeatureServer/0"
GLENDALE_DATASET_PAGE = "https://www.glendaleca.gov/your-government/departments/public-works/urban-forestry/tree-inventory-map"
INGLEWOOD_TREES_LAYER = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/Inglewood_Tree_Layer_view/FeatureServer/0"
INGLEWOOD_DATASET_PAGE = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/Inglewood_Tree_Layer_view/FeatureServer"
INGLEWOOD_FRUIT_TREES_LAYER = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/Inglewood_Fruit_Tree_Recipients_view/FeatureServer/0"
INGLEWOOD_FRUIT_DATASET_PAGE = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/Inglewood_Fruit_Tree_Recipients_view/FeatureServer"
LYNWOOD_TREES_LAYER = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/Lynwood_Public_Trees_(CAL_FIRE)_view/FeatureServer/0"
LYNWOOD_DATASET_PAGE = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/Lynwood_Public_Trees_(CAL_FIRE)_view/FeatureServer"
HUNTINGTON_PARK_TREES_LAYER = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/UFMP_Huntington_Park_Tree_Sites_view/FeatureServer/0"
HUNTINGTON_PARK_DATASET_PAGE = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/UFMP_Huntington_Park_Tree_Sites_view/FeatureServer"
COMMERCE_TREES_LAYER = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/Commerce_Public_Trees_view/FeatureServer/0"
COMMERCE_DATASET_PAGE = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/Commerce_Public_Trees_view/FeatureServer"
PARAMOUNT_TREES_LAYER = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/TreePeople_Paramount_Tree_Site_Layer_view/FeatureServer/0"
PARAMOUNT_DATASET_PAGE = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/TreePeople_Paramount_Tree_Site_Layer_view/FeatureServer"
SOUTH_GATE_CUDAHY_TREES_LAYER = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/South_Gate_Cudahy_Public_Tree_Layer_view/FeatureServer/0"
SOUTH_GATE_CUDAHY_DATASET_PAGE = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/South_Gate_Cudahy_Public_Tree_Layer_view/FeatureServer"
CUDAHY_FRUIT_TREES_LAYER = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/South_Gate_Cudahy_Fruit_Tree_Layer_view/FeatureServer/0"
CUDAHY_FRUIT_DATASET_PAGE = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/South_Gate_Cudahy_Fruit_Tree_Layer_view/FeatureServer"
I5_TREES_LAYER = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/I_5_Project_Data_Tree_Sites/FeatureServer/0"
I5_DATASET_PAGE = "https://services5.arcgis.com/t4zDNzBF9Dot8HEQ/arcgis/rest/services/I_5_Project_Data_Tree_Sites/FeatureServer"
VENTURA_DATASET_PAGE = "https://www.cityofventura.ca.gov/1574/Street-Trees"
LAGUNA_BEACH_TREES_LAYER = "https://services9.arcgis.com/DPQ7yLDIWIyMUXzD/ArcGIS/rest/services/GIS_Map/FeatureServer/13"
LAGUNA_BEACH_DATASET_PAGE = "https://www.lagunabeachcity.net/live-here/trees"
SOLANA_BEACH_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/City_of_Solana_Beach_Tree_Benefits_Map_72525/FeatureServer/0"
SOLANA_BEACH_DATASET_PAGE = "https://www.cityofsolanabeach.org/en/government/public-works/departments/tree-inventory"
ENCINITAS_PUBLIC_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/TreeInvEncinitas_Public/FeatureServer/0"
ENCINITAS_PARKS_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/TreeInvEncinitasParks_Public/FeatureServer/0"
ENCINITAS_DATASET_PAGE = "https://www.encinitasca.gov/residents/parks-beaches-and-trails/trees-in-encinitas"
ESCONDIDO_TREES_LAYER = "https://services2.arcgis.com/eJcVbjTyyZIzZ5Ye/arcgis/rest/services/TreeInventory/FeatureServer/0"
ESCONDIDO_DATASET_PAGE = "https://services2.arcgis.com/eJcVbjTyyZIzZ5Ye/arcgis/rest/services/TreeInventory/FeatureServer"
REDLANDS_TREES_LAYER = "https://services.arcgis.com/FLM8UAw9y5MmuVTV/arcgis/rest/services/Street_Trees/FeatureServer/0"
REDLANDS_DATASET_PAGE = "https://services.arcgis.com/FLM8UAw9y5MmuVTV/arcgis/rest/services/Street_Trees/FeatureServer"
WEST_COVINA_TREES_LAYER = "https://services8.arcgis.com/WV8ogNubjFL2BKPt/arcgis/rest/services/West_Covina_Tree_Information/FeatureServer/0"
WEST_COVINA_DATASET_PAGE = "https://services8.arcgis.com/WV8ogNubjFL2BKPt/arcgis/rest/services/West_Covina_Tree_Information/FeatureServer"
SANTEE_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/CityOfSantee_AllBoundaries_Benefits_Canopy_WFL1/FeatureServer/0"
SANTEE_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/CityOfSantee_AllBoundaries_Benefits_Canopy_WFL1/FeatureServer"
LA_MESA_TREES_LAYER = "https://services3.arcgis.com/iYP51zxNr6TITn6r/arcgis/rest/services/Tree_Inventory/FeatureServer/4"
LA_MESA_DATASET_PAGE = "https://services3.arcgis.com/iYP51zxNr6TITn6r/arcgis/rest/services/Tree_Inventory/FeatureServer"
VISTA_TREES_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/City_of_Vista_iTree_benefits/FeatureServer/0"
VISTA_DATASET_PAGE = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/City_of_Vista_iTree_benefits/FeatureServer"
CAMARILLO_TREES_LAYER = "https://services3.arcgis.com/EKquOdzev2aNwKyB/arcgis/rest/services/Trees/FeatureServer/0"
CAMARILLO_DATASET_PAGE = "https://services3.arcgis.com/EKquOdzev2aNwKyB/arcgis/rest/services/Trees/FeatureServer"
CHINO_TREES_LAYER = "https://services2.arcgis.com/6f07Mm2LapX6mneF/arcgis/rest/services/CityTrees_ResCityMaintSpecIden/FeatureServer/0"
CHINO_DATASET_PAGE = "https://services2.arcgis.com/6f07Mm2LapX6mneF/arcgis/rest/services/CityTrees_ResCityMaintSpecIden/FeatureServer"
GLENDORA_TREES_LAYER = "https://services2.arcgis.com/NQC8oBejgXkIxQpu/arcgis/rest/services/Glendora_Public_Map_WFL1/FeatureServer/5"
GLENDORA_DATASET_PAGE = "https://services2.arcgis.com/NQC8oBejgXkIxQpu/arcgis/rest/services/Glendora_Public_Map_WFL1/FeatureServer"
SAN_DIEGO_BLOSSOM_WHERE = (
    "UPPER(COMMON_NAME) LIKE '%CHERRY%' OR "
    "UPPER(COMMON_NAME) LIKE '%PLUM%' OR "
    "UPPER(COMMON_NAME) LIKE '%PEACH%' OR "
    "UPPER(COMMON_NAME) LIKE '%MAGNOLIA%' OR "
    "UPPER(COMMON_NAME) LIKE '%CRABAPPLE%' OR "
    "UPPER(COMMON_NAME) LIKE '%APPLE%'"
)
LAS_VEGAS_BLOSSOM_WHERE = (
    "ACTIVE = 1 AND STATUS = 'Tree' AND ("
    "UPPER(SPP_BOT) LIKE 'PRUNUS%' OR "
    "UPPER(SPP_BOT) LIKE 'MALUS%' OR "
    "UPPER(SPP_BOT) LIKE 'MAGNOLIA%' OR "
    "UPPER(SPP_COM) LIKE '%CHERRY%' OR "
    "UPPER(SPP_COM) LIKE '%PLUM%' OR "
    "UPPER(SPP_COM) LIKE '%PEACH%' OR "
    "UPPER(SPP_COM) LIKE '%MAGNOLIA%' OR "
    "UPPER(SPP_COM) LIKE '%CRABAPPLE%' OR "
    "UPPER(SPP_COM) LIKE '%APPLE%'"
    ")"
)
SALT_LAKE_CITY_BLOSSOM_WHERE = (
    "(Vacant IS NULL OR Vacant <> 'Yes') AND ("
    "UPPER(SPP) LIKE 'PRUNUS%' OR "
    "UPPER(SPP) LIKE 'MALUS%' OR "
    "UPPER(SPP) LIKE 'MAGNOLIA%' OR "
    "UPPER(SPP) LIKE '%CHERRY%' OR "
    "UPPER(SPP) LIKE '%PLUM%' OR "
    "UPPER(SPP) LIKE '%PEACH%' OR "
    "UPPER(SPP) LIKE '%MAGNOLIA%' OR "
    "UPPER(SPP) LIKE '%CRABAPPLE%' OR "
    "UPPER(SPP) LIKE '%APPLE%'"
    ")"
)
OTTAWA_BLOSSOM_WHERE = (
    "STATUS = 'Active' AND ("
    "UPPER(SPECIES) LIKE '%CHERRY%' OR "
    "UPPER(SPECIES) LIKE '%PLUM%' OR "
    "UPPER(SPECIES) LIKE '%PEACH%' OR "
    "UPPER(SPECIES) LIKE '%MAGNOLIA%' OR "
    "UPPER(SPECIES) LIKE '%CRABAPPLE%' OR "
    "UPPER(SPECIES) LIKE '%APPLE%'"
    ")"
)
IRVINE_BLOSSOM_WHERE = (
    "UPPER(TRG_COMMON) LIKE '%CHERRY%' OR "
    "UPPER(TRG_COMMON) LIKE '%PLUM%' OR "
    "UPPER(TRG_COMMON) LIKE '%PEACH%' OR "
    "UPPER(TRG_COMMON) LIKE '%MAGNOLIA%' OR "
    "UPPER(TRG_COMMON) LIKE '%CRABAPPLE%' OR "
    "UPPER(TRG_COMMON) LIKE '%APPLE%'"
)
MOUNTAIN_VIEW_BLOSSOM_WHERE = (
    "UPPER(SCINAME) LIKE 'PRUNUS%' OR "
    "UPPER(SCINAME) LIKE 'MALUS%' OR "
    "UPPER(SCINAME) LIKE 'MAGNOLIA%' OR "
    "UPPER(BOTNAMEDESCRPT) LIKE '%CHERRY%' OR "
    "UPPER(BOTNAMEDESCRPT) LIKE '%PLUM%' OR "
    "UPPER(BOTNAMEDESCRPT) LIKE '%PEACH%' OR "
    "UPPER(BOTNAMEDESCRPT) LIKE '%MAGNOLIA%' OR "
    "UPPER(BOTNAMEDESCRPT) LIKE '%CRABAPPLE%' OR "
    "UPPER(BOTNAMEDESCRPT) LIKE '%APPLE%'"
)
SACRAMENTO_BLOSSOM_WHERE = (
    "UPPER(BOTANICAL) LIKE 'PRUNUS%' OR "
    "UPPER(BOTANICAL) LIKE 'MALUS%' OR "
    "UPPER(BOTANICAL) LIKE 'MAGNOLIA%' OR "
    "UPPER(SPECIES) LIKE '%CHERRY%' OR "
    "UPPER(SPECIES) LIKE '%PLUM%' OR "
    "UPPER(SPECIES) LIKE '%PEACH%' OR "
    "UPPER(SPECIES) LIKE '%MAGNOLIA%' OR "
    "UPPER(SPECIES) LIKE '%CRABAPPLE%' OR "
    "UPPER(SPECIES) LIKE '%APPLE%'"
)
NEWPORT_BEACH_BLOSSOM_WHERE = (
    "UPPER(Botanical) LIKE 'PRUNUS%' OR "
    "UPPER(Botanical) LIKE 'MALUS%' OR "
    "UPPER(Botanical) LIKE 'MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CHERRY%' OR "
    "UPPER(CommonName) LIKE '%PLUM%' OR "
    "UPPER(CommonName) LIKE '%PEACH%' OR "
    "UPPER(CommonName) LIKE '%MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CRABAPPLE%' OR "
    "UPPER(CommonName) LIKE '%APPLE%'"
)
THOUSAND_OAKS_BLOSSOM_WHERE = (
    "UPPER(Botanical) LIKE 'PRUNUS%' OR "
    "UPPER(Botanical) LIKE 'MALUS%' OR "
    "UPPER(Botanical) LIKE 'MAGNOLIA%' OR "
    "UPPER(Common) LIKE '%CHERRY%' OR "
    "UPPER(Common) LIKE '%PLUM%' OR "
    "UPPER(Common) LIKE '%PEACH%' OR "
    "UPPER(Common) LIKE '%MAGNOLIA%' OR "
    "UPPER(Common) LIKE '%CRABAPPLE%' OR "
    "UPPER(Common) LIKE '%APPLE%'"
)
CORONA_BLOSSOM_WHERE = (
    "UPPER(BotanicalName) LIKE 'PRUNUS%' OR "
    "UPPER(BotanicalName) LIKE 'MALUS%' OR "
    "UPPER(BotanicalName) LIKE 'MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CHERRY%' OR "
    "UPPER(CommonName) LIKE '%PLUM%' OR "
    "UPPER(CommonName) LIKE '%PEACH%' OR "
    "UPPER(CommonName) LIKE '%MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CRABAPPLE%' OR "
    "UPPER(CommonName) LIKE '%APPLE%' OR "
    "UPPER(Species_Name) LIKE 'PRUNUS%' OR "
    "UPPER(Species_Name) LIKE 'MALUS%' OR "
    "UPPER(Species_Name) LIKE 'MAGNOLIA%'"
)
YORBA_LINDA_BLOSSOM_WHERE = (
    "UPPER(Species_Na) LIKE 'PRUNUS%' OR "
    "UPPER(Species_Na) LIKE 'MALUS%' OR "
    "UPPER(Species_Na) LIKE 'MAGNOLIA%'"
)
SAN_DIMAS_BLOSSOM_WHERE = (
    "UPPER(BotanicalName) LIKE 'PRUNUS%' OR "
    "UPPER(BotanicalName) LIKE ' MALUS%' OR "
    "UPPER(BotanicalName) LIKE 'MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CHERRY%' OR "
    "UPPER(CommonName) LIKE '%PLUM%' OR "
    "UPPER(CommonName) LIKE '%PEACH%' OR "
    "UPPER(CommonName) LIKE '%MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CRABAPPLE%' OR "
    "UPPER(CommonName) LIKE '%APPLE%'"
)
RANCHO_PALOS_VERDES_BLOSSOM_WHERE = (
    "UPPER(BOTANICAL) LIKE 'PRUNUS%' OR "
    "UPPER(BOTANICAL) LIKE 'MALUS%' OR "
    "UPPER(BOTANICAL) LIKE 'MAGNOLIA%' OR "
    "UPPER(COMMON) LIKE '%CHERRY%' OR "
    "UPPER(COMMON) LIKE '%PLUM%' OR "
    "UPPER(COMMON) LIKE '%PEACH%' OR "
    "UPPER(COMMON) LIKE '%MAGNOLIA%' OR "
    "UPPER(COMMON) LIKE '%CRABAPPLE%' OR "
    "UPPER(COMMON) LIKE '%APPLE%'"
)
SANTA_MONICA_BLOSSOM_WHERE = (
    "botanicalname LIKE 'Prunus%' OR "
    "botanicalname LIKE 'Malus%' OR "
    "botanicalname LIKE 'Magnolia%' OR "
    "commonname LIKE '%CHERRY%' OR "
    "commonname LIKE '%PLUM%' OR "
    "commonname LIKE '%PEACH%' OR "
    "commonname LIKE '%MAGNOLIA%' OR "
    "commonname LIKE '%CRABAPPLE%' OR "
    "commonname LIKE '%APPLE%'"
)
OXNARD_BLOSSOM_WHERE = (
    "BOTANICALN LIKE 'Prunus%' OR "
    "BOTANICALN LIKE 'Malus%' OR "
    "BOTANICALN LIKE 'Magnolia%' OR "
    "COMMONNAME LIKE '%CHERRY%' OR "
    "COMMONNAME LIKE '%PLUM%' OR "
    "COMMONNAME LIKE '%PEACH%' OR "
    "COMMONNAME LIKE '%MAGNOLIA%' OR "
    "COMMONNAME LIKE '%CRABAPPLE%' OR "
    "COMMONNAME LIKE '%APPLE%'"
)
SOLANA_BEACH_BLOSSOM_WHERE = (
    "UPPER(Species_Name) LIKE 'PRUNUS%' OR "
    "UPPER(Species_Name) LIKE 'MALUS%' OR "
    "UPPER(Species_Name) LIKE 'MAGNOLIA%'"
)
HOUSTON_BLOSSOM_WHERE = (
    "UPPER(SPECIES) LIKE 'PRUNUS%' OR "
    "UPPER(SPECIES) LIKE 'MALUS%' OR "
    "UPPER(SPECIES) LIKE 'MAGNOLIA%' OR "
    "UPPER(SPECIES) LIKE '%CHERRY%' OR "
    "UPPER(SPECIES) LIKE '%PLUM%' OR "
    "UPPER(SPECIES) LIKE '%PEACH%' OR "
    "UPPER(SPECIES) LIKE '%MAGNOLIA%' OR "
    "UPPER(SPECIES) LIKE '%CRABAPPLE%' OR "
    "UPPER(SPECIES) LIKE '%APPLE%'"
)
DENVER_BLOSSOM_WHERE = (
    "UPPER(SPECIES_COMMON) LIKE '%CHERRY%' OR "
    "UPPER(SPECIES_COMMON) LIKE '%PLUM%' OR "
    "UPPER(SPECIES_COMMON) LIKE '%PEACH%' OR "
    "UPPER(SPECIES_COMMON) LIKE '%MAGNOLIA%' OR "
    "UPPER(SPECIES_COMMON) LIKE '%CRABAPPLE%' OR "
    "UPPER(SPECIES_COMMON) LIKE '%APPLE%' OR "
    "UPPER(SPECIES_BOTANIC) LIKE 'PRUNUS%' OR "
    "UPPER(SPECIES_BOTANIC) LIKE 'MALUS%' OR "
    "UPPER(SPECIES_BOTANIC) LIKE 'MAGNOLIA%'"
)
PASADENA_BLOSSOM_WHERE = (
    "Status_Text = 'Active' AND ("
    "UPPER(Genus) LIKE 'PRUNUS%' OR "
    "UPPER(Genus) LIKE 'MALUS%' OR "
    "UPPER(Genus) LIKE 'MAGNOLIA%'"
    ")"
)
BOTANICAL_BLOSSOM_WHERE = (
    "UPPER(BotanicalName) LIKE 'PRUNUS%' OR "
    "UPPER(BotanicalName) LIKE 'MALUS%' OR "
    "UPPER(BotanicalName) LIKE 'MAGNOLIA%'"
)
BOTANICAL_COMMON_BLOSSOM_WHERE = (
    "UPPER(BotanicalName) LIKE 'PRUNUS%' OR "
    "UPPER(BotanicalName) LIKE 'MALUS%' OR "
    "UPPER(BotanicalName) LIKE 'MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CHERRY%' OR "
    "UPPER(CommonName) LIKE '%PLUM%' OR "
    "UPPER(CommonName) LIKE '%PEACH%' OR "
    "UPPER(CommonName) LIKE '%MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CRABAPPLE%' OR "
    "UPPER(CommonName) LIKE '%APPLE%'"
)
ESCONDIDO_BLOSSOM_WHERE = (
    "UPPER(BOTANICAL_NAME) LIKE 'PRUNUS%' OR "
    "UPPER(BOTANICAL_NAME) LIKE 'MALUS%' OR "
    "UPPER(BOTANICAL_NAME) LIKE 'MAGNOLIA%' OR "
    "UPPER(COMMON_NAME) LIKE '%CHERRY%' OR "
    "UPPER(COMMON_NAME) LIKE '%PLUM%' OR "
    "UPPER(COMMON_NAME) LIKE '%PEACH%' OR "
    "UPPER(COMMON_NAME) LIKE '%MAGNOLIA%' OR "
    "UPPER(COMMON_NAME) LIKE '%CRABAPPLE%' OR "
    "UPPER(COMMON_NAME) LIKE '%APPLE%'"
)
REDLANDS_BLOSSOM_WHERE = (
    "UPPER(BOTANICALN) LIKE 'PRUNUS%' OR "
    "UPPER(BOTANICALN) LIKE 'MALUS%' OR "
    "UPPER(BOTANICALN) LIKE 'MAGNOLIA%' OR "
    "UPPER(COMMONNAME) LIKE '%CHERRY%' OR "
    "UPPER(COMMONNAME) LIKE '%PLUM%' OR "
    "UPPER(COMMONNAME) LIKE '%PEACH%' OR "
    "UPPER(COMMONNAME) LIKE '%MAGNOLIA%' OR "
    "UPPER(COMMONNAME) LIKE '%CRABAPPLE%' OR "
    "UPPER(COMMONNAME) LIKE '%APPLE%'"
)
WEST_COVINA_BLOSSOM_WHERE = (
    "UPPER(BOTANICALN) LIKE 'PRUNUS%' OR "
    "UPPER(BOTANICALN) LIKE 'MALUS%' OR "
    "UPPER(BOTANICALN) LIKE 'MAGNOLIA%' OR "
    "UPPER(COMMONNAME) LIKE '%CHERRY%' OR "
    "UPPER(COMMONNAME) LIKE '%PLUM%' OR "
    "UPPER(COMMONNAME) LIKE '%PEACH%' OR "
    "UPPER(COMMONNAME) LIKE '%MAGNOLIA%' OR "
    "UPPER(COMMONNAME) LIKE '%CRABAPPLE%' OR "
    "UPPER(COMMONNAME) LIKE '%APPLE%'"
)
SPECIES_NAME_BLOSSOM_WHERE = (
    "UPPER(Species_Name) LIKE 'PRUNUS%' OR "
    "UPPER(Species_Name) LIKE 'MALUS%' OR "
    "UPPER(Species_Name) LIKE 'MAGNOLIA%'"
)
SPECIES_NAME_COMMON_BLOSSOM_WHERE = (
    "UPPER(Species_Name) LIKE 'PRUNUS%' OR "
    "UPPER(Species_Name) LIKE 'MALUS%' OR "
    "UPPER(Species_Name) LIKE 'MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CHERRY%' OR "
    "UPPER(CommonName) LIKE '%PLUM%' OR "
    "UPPER(CommonName) LIKE '%PEACH%' OR "
    "UPPER(CommonName) LIKE '%MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CRABAPPLE%' OR "
    "UPPER(CommonName) LIKE '%APPLE%'"
)
ANAHEIM_BLOSSOM_WHERE = (
    "UPPER(Species_Name) LIKE 'PRUNUS%' OR "
    "UPPER(Species_Name) LIKE 'MALUS%' OR "
    "UPPER(Species_Name) LIKE 'MAGNOLIA%' OR "
    "UPPER(BOTANICALN) LIKE 'PRUNUS%' OR "
    "UPPER(BOTANICALN) LIKE 'MALUS%' OR "
    "UPPER(BOTANICALN) LIKE 'MAGNOLIA%'"
)
SAN_FERNANDO_BLOSSOM_WHERE = (
    "UPPER(NAME) LIKE 'PRUNUS%' OR "
    "UPPER(NAME) LIKE 'MALUS%' OR "
    "UPPER(NAME) LIKE 'MAGNOLIA%'"
)
SUNNYVALE_BLOSSOM_WHERE = (
    "City = 'Sunnyvale' AND ("
    "UPPER(Scientific) LIKE 'PRUNUS%' OR "
    "UPPER(Scientific) LIKE 'MALUS%' OR "
    "UPPER(Scientific) LIKE 'MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CHERRY%' OR "
    "UPPER(CommonName) LIKE '%PLUM%' OR "
    "UPPER(CommonName) LIKE '%PEACH%' OR "
    "UPPER(CommonName) LIKE '%MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CRABAPPLE%' OR "
    "UPPER(CommonName) LIKE '%APPLE%'"
    ")"
)
AUSTIN_BLOSSOM_WHERE = (
    "lower(species) like '%cherry%' OR "
    "lower(species) like '%plum%' OR "
    "lower(species) like '%peach%' OR "
    "lower(species) like '%magnolia%' OR "
    "lower(species) like '%crabapple%' OR "
    "lower(species) like '%apple%'"
)
WEST_HOLLYWOOD_BLOSSOM_WHERE = (
    "upper(botanicalname) like 'PRUNUS%' OR "
    "upper(botanicalname) like 'MALUS%' OR "
    "upper(botanicalname) like 'MAGNOLIA%' OR "
    "upper(commonname) like '%CHERRY%' OR "
    "upper(commonname) like '%PLUM%' OR "
    "upper(commonname) like '%PEACH%' OR "
    "upper(commonname) like '%MAGNOLIA%' OR "
    "upper(commonname) like '%CRABAPPLE%' OR "
    "upper(commonname) like '%APPLE%'"
)
LA_MESA_BLOSSOM_WHERE = (
    "UPPER(BotanicalName) LIKE 'PRUNUS%' OR "
    "UPPER(BotanicalName) LIKE 'MALUS%' OR "
    "UPPER(BotanicalName) LIKE 'MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CHERRY%' OR "
    "UPPER(CommonName) LIKE '%PLUM%' OR "
    "UPPER(CommonName) LIKE '%PEACH%' OR "
    "UPPER(CommonName) LIKE '%MAGNOLIA%' OR "
    "UPPER(CommonName) LIKE '%CRABAPPLE%' OR "
    "UPPER(CommonName) LIKE '%APPLE%'"
)
CAMARILLO_BLOSSOM_WHERE = (
    "UPPER(BOTANICAL) LIKE 'PRUNUS%' OR "
    "UPPER(BOTANICAL) LIKE 'MALUS%' OR "
    "UPPER(BOTANICAL) LIKE 'MAGNOLIA%' OR "
    "UPPER(COMMON) LIKE '%CHERRY%' OR "
    "UPPER(COMMON) LIKE '%PLUM%' OR "
    "UPPER(COMMON) LIKE '%PEACH%' OR "
    "UPPER(COMMON) LIKE '%MAGNOLIA%' OR "
    "UPPER(COMMON) LIKE '%CRABAPPLE%' OR "
    "UPPER(COMMON) LIKE '%APPLE%'"
)
CHINO_BLOSSOM_WHERE = (
    "UPPER(Species) LIKE 'PRUNUS%' OR "
    "UPPER(Species) LIKE 'MALUS%' OR "
    "UPPER(Species) LIKE 'MAGNOLIA%' OR "
    "UPPER(Species) LIKE '%CHERRY%' OR "
    "UPPER(Species) LIKE '%PLUM%' OR "
    "UPPER(Species) LIKE '%PEACH%' OR "
    "UPPER(Species) LIKE '%MAGNOLIA%' OR "
    "UPPER(Species) LIKE '%CRABAPPLE%' OR "
    "UPPER(Species) LIKE '%APPLE%'"
)
GLENDORA_BLOSSOM_WHERE = CAMARILLO_BLOSSOM_WHERE
LOS_ANGELES_TREEKEEPER_TERMS = ("%cherry%", "%plum%", "%peach%", "%magnolia%", "%crabapple%", "%apple%")
SPECIES_TEXT_PATTERN = re.compile(r"^\s*(?P<common>.+?)\s*\((?P<scientific>[^()]+)\)\s*$")
DISPLAY_NAME_REPLACEMENTS = {
    "Chery": "Cherry",
    "Crab Apple": "Crabapple",
}

NYC_METRO_TREEKEEPER_CONFIGS: dict[str, dict[str, str]] = {
    "Newark": {"base_url": "https://newarknj.treekeepersoftware.com", "uid": "pinkhunter-newark-nj"},
    "Millburn": {"base_url": "https://millburnnj.treekeepersoftware.com", "uid": "pinkhunter-millburn-nj"},
    "Princeton": {"base_url": "https://princetonnj.treekeepersoftware.com", "uid": "pinkhunter-princeton-nj"},
    "Ho-Ho-Kus": {"base_url": "https://hohokusnj.treekeepersoftware.com", "uid": "pinkhunter-hohokus-nj"},
    "Oradell": {"base_url": "https://oradellnj.treekeepersoftware.com", "uid": "pinkhunter-oradell-nj"},
    "Rutherford": {"base_url": "https://rutherfordnj.treekeepersoftware.com", "uid": "pinkhunter-rutherford-nj"},
    "River Edge": {"base_url": "https://riveredgenj.treekeepersoftware.com", "uid": "pinkhunter-river-edge-nj"},
    "Dumont": {"base_url": "https://dumontnj.treekeepersoftware.com", "uid": "pinkhunter-dumont-nj"},
    "Westwood": {"base_url": "https://westwoodnj.treekeepersoftware.com", "uid": "pinkhunter-westwood-nj"},
    "Tenafly": {"base_url": "https://tenaflynj.treekeepersoftware.com", "uid": "pinkhunter-tenafly-nj"},
    "Teaneck": {"base_url": "https://teanecknj.treekeepersoftware.com", "uid": "pinkhunter-teaneck-nj"},
    "Ridgewood": {"base_url": "https://ridgewoodnj.treekeepersoftware.com", "uid": "pinkhunter-ridgewood-nj"},
    "Bergenfield": {"base_url": "https://bergenfieldnj.treekeepersoftware.com", "uid": "pinkhunter-bergenfield-nj"},
    "Montvale": {"base_url": "https://montvalenj.treekeepersoftware.com", "uid": "pinkhunter-montvale-nj"},
    "Glen Rock": {"base_url": "https://glenrocknj.treekeepersoftware.com", "uid": "pinkhunter-glen-rock-nj"},
    "Englewood": {"base_url": "https://englewoodnj.treekeepersoftware.com", "uid": "pinkhunter-englewood-nj"},
    "Franklin Lakes": {"base_url": "https://franklinlakesnj.treekeepersoftware.com", "uid": "pinkhunter-franklin-lakes-nj"},
    "Demarest": {"base_url": "https://demarestnj.treekeepersoftware.com", "uid": "pinkhunter-demarest-nj"},
    "Haworth": {"base_url": "https://haworthnj.treekeepersoftware.com", "uid": "pinkhunter-haworth-nj"},
    "New Milford": {"base_url": "https://newmilfordnj.treekeepersoftware.com", "uid": "pinkhunter-new-milford-nj"},
    "Ramsey": {"base_url": "https://ramseynj.treekeepersoftware.com", "uid": "pinkhunter-ramsey-nj"},
    "Wyckoff": {"base_url": "https://wyckoffnj.treekeepersoftware.com", "uid": "pinkhunter-wyckoff-nj"},
    "Fair Lawn": {"base_url": "https://fairlawnnj.treekeepersoftware.com", "uid": "pinkhunter-fair-lawn-nj"},
    "Allendale": {"base_url": "https://allendalenj.treekeepersoftware.com", "uid": "pinkhunter-allendale-nj"},
    "Mahwah": {"base_url": "https://mahwahnj.treekeepersoftware.com", "uid": "pinkhunter-mahwah-nj"},
    "Fort Lee": {"base_url": "https://fortleenj.treekeepersoftware.com", "uid": "pinkhunter-fort-lee-nj"},
}

NYC_METRO_ARCGIS_CONFIGS: dict[str, dict[str, Any]] = {
    "Hoboken": {
        "layer_url": HOBOKEN_TREES_LAYER,
        "dataset_page": HOBOKEN_DATASET_PAGE,
        "object_id_field": "FID",
        "common_field": "CommonName",
        "genus_field": "Genus",
        "species_field": "Species",
        "source_department": "City of Hoboken",
        "note": "Integrated from the official City of Hoboken public tree inventory ArcGIS layer.",
    },
    "Morristown": {
        "layer_url": MORRISTOWN_TREES_LAYER,
        "dataset_page": MORRISTOWN_DATASET_PAGE,
        "object_id_field": "FID",
        "genus_field": "GENUS",
        "species_field": "SPECIES",
        "source_department": "Town of Morristown",
        "note": "Integrated from the official Morristown public tree inventory ArcGIS layer.",
    },
    "Linden": {
        "layer_url": LINDEN_TREES_LAYER,
        "dataset_page": LINDEN_DATASET_PAGE,
        "object_id_field": "F__OBJECTID",
        "common_field": "Tree_Species",
        "lon_field": "x",
        "lat_field": "y",
        "source_department": "City of Linden",
        "note": "Integrated from the official City of Linden tree survey ArcGIS layer.",
    },
    "Montclair": {
        "layer_url": MONTCLAIR_TREES_LAYER,
        "dataset_page": MONTCLAIR_DATASET_PAGE,
        "object_id_field": "OBJECTID",
        "common_field": "COMMON_NAME",
        "scientific_field": "SCIENTIFIC_NAME",
        "source_department": "Township of Montclair",
        "note": "Integrated from the official Township of Montclair public tree inventory ArcGIS layer.",
    },
}

EAST_COAST_TREEKEEPER_CONFIGS: dict[str, dict[str, Any]] = {
    "Belmont": {
        "base_url": "https://belmontma.treekeepersoftware.com",
        "uid": "pinkhunter-belmont-ma",
        "region": "ma",
        "source_department": "Town of Belmont",
        "note": "Integrated from the official Town of Belmont public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Albany": {
        "base_url": "https://albanyny.treekeepersoftware.com",
        "uid": "pinkhunter-albany-ny",
        "region": "ny",
        "source_department": "City of Albany",
        "note": "Integrated from the official City of Albany public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Buffalo": {
        "base_url": "https://buffalony.treekeepersoftware.com",
        "uid": "pinkhunter-buffalo-ny",
        "region": "ny",
        "source_department": "City of Buffalo",
        "note": "Integrated from the official City of Buffalo public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Falls Church": {
        "base_url": "https://fallschurchva.treekeepersoftware.com",
        "uid": "pinkhunter-falls-church-va",
        "region": "va",
        "source_department": "City of Falls Church",
        "note": "Integrated from the official City of Falls Church public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Greenwich": {
        "base_url": "https://greenwichct.treekeepersoftware.com",
        "uid": "pinkhunter-greenwich-ct",
        "region": "ct",
        "source_department": "Town of Greenwich",
        "note": "Integrated from the official Town of Greenwich public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Hartford": {
        "base_url": "https://hartfordct.treekeepersoftware.com",
        "uid": "pinkhunter-hartford-ct",
        "region": "ct",
        "source_department": "City of Hartford",
        "note": "Integrated from the official City of Hartford public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Ithaca": {
        "base_url": "https://ithacany.treekeepersoftware.com",
        "uid": "pinkhunter-ithaca-ny",
        "region": "ny",
        "source_department": "City of Ithaca",
        "note": "Integrated from the official City of Ithaca public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "New Haven": {
        "base_url": "https://newhavenct.treekeepersoftware.com",
        "uid": "pinkhunter-new-haven-ct",
        "region": "ct",
        "source_department": "City of New Haven",
        "note": "Integrated from the official City of New Haven public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Newton": {
        "base_url": "https://newtonma.treekeepersoftware.com",
        "uid": "pinkhunter-newton-ma",
        "region": "ma",
        "source_department": "City of Newton",
        "note": "Integrated from the official City of Newton public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Somerville": {
        "base_url": "https://somervillema.treekeepersoftware.com",
        "uid": "pinkhunter-somerville-ma",
        "region": "ma",
        "source_department": "City of Somerville",
        "note": "Integrated from the official City of Somerville public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Springfield": {
        "base_url": "https://springfieldma.treekeepersoftware.com",
        "uid": "pinkhunter-springfield-ma",
        "region": "ma",
        "source_department": "City of Springfield",
        "note": "Integrated from the official City of Springfield public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Syracuse": {
        "base_url": "https://syracuseny.treekeepersoftware.com",
        "uid": "pinkhunter-syracuse-ny",
        "region": "ny",
        "source_department": "City of Syracuse",
        "note": "Integrated from the official City of Syracuse public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Stamford": {
        "base_url": "https://stamfordct.treekeepersoftware.com",
        "uid": "pinkhunter-stamford-ct",
        "region": "ct",
        "source_department": "City of Stamford",
        "note": "Integrated from the official City of Stamford public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Waltham": {
        "base_url": "https://walthamma.treekeepersoftware.com",
        "uid": "pinkhunter-waltham-ma",
        "region": "ma",
        "source_department": "City of Waltham",
        "note": "Integrated from the official City of Waltham public TreeKeeper inventory.",
        "use_zip_index": False,
    },
    "Worcester": {
        "base_url": "https://worcesterma.treekeepersoftware.com",
        "uid": "pinkhunter-worcester-ma",
        "region": "ma",
        "source_department": "City of Worcester",
        "note": "Integrated from the official City of Worcester public TreeKeeper inventory.",
        "use_zip_index": False,
    },
}

EAST_COAST_TREEPLOTTER_CONFIGS: dict[str, dict[str, Any]] = {
    "Annapolis": {
        "folder": "AnnapolisMD",
        "landing_url": "https://pg-cloud.com/AnnapolisMD/",
        "region": "md",
        "source_department": "City of Annapolis",
        "note": "Integrated via the public Annapolis TreePlotter inventory page and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "Fairfax": {
        "folder": "FairfaxVA",
        "landing_url": "https://pg-cloud.com/FairfaxVA/",
        "region": "va",
        "source_department": "City of Fairfax",
        "note": "Integrated via the public Fairfax TreePlotter inventory page and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "Saratoga Springs": {
        "folder": "SaratogaSpringsNY",
        "landing_url": "https://pg-cloud.com/SaratogaSpringsNY/",
        "region": "ny",
        "source_department": "City of Saratoga Springs",
        "note": "Integrated via the public Saratoga Springs TreePlotter inventory page and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "Troy": {
        "folder": "TroyNY",
        "landing_url": "https://pg-cloud.com/TroyNY/",
        "region": "ny",
        "source_department": "City of Troy",
        "note": "Integrated via the public Troy TreePlotter inventory page and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "West Hartford": {
        "folder": "WestHartfordCT",
        "landing_url": "https://pg-cloud.com/WestHartfordCT/",
        "region": "ct",
        "source_department": "Town of West Hartford",
        "note": "Integrated via the public West Hartford TreePlotter inventory page and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
}

UNCOVERED_STATE_ARCGIS_CONFIGS: dict[str, dict[str, Any]] = {
    "Ann Arbor": {
        "region": "mi",
        "layer_url": "https://a2maps.a2gov.org/a2arcgis/rest/services/TreeInventory/FeatureServer/0",
        "dataset_page": "https://data.a2gov.org/city-of-ann-arbor/street-trees-inventory",
        "object_id_field": "OBJECTID",
        "common_field": "COMMONNAME",
        "scientific_field": "BOTANICAL",
        "source_name": "Tree Inventory",
        "source_department": "City of Ann Arbor",
        "ownership_raw": "City of Ann Arbor",
        "note": "Integrated from the official City of Ann Arbor street tree inventory dashboard backed by the city ArcGIS service.",
        "clip_to_boundary": True,
    },
    "Danville": {
        "region": "il",
        "layer_url": "https://gis.cityofdanville.org/arcgis/rest/services/PublicWorks/Tree_Inventory/FeatureServer/0",
        "dataset_page": "https://gis.cityofdanville.org/arcgis/rest/services/PublicWorks/Tree_Inventory/FeatureServer",
        "object_id_field": "OBJECTID",
        "common_field": "TreeCommonName",
        "source_name": "Tree Inventory",
        "source_department": "City of Danville",
        "ownership_raw": "City of Danville",
        "note": "Integrated from the official City of Danville public tree inventory ArcGIS layer.",
        "clip_to_boundary": True,
    },
    "Dearborn Heights": {
        "region": "mi",
        "layer_url": "https://services2.arcgis.com/B35lXgJgukVwqV28/arcgis/rest/services/Tree_Record/FeatureServer/0",
        "dataset_page": "https://www.arcgis.com/home/item.html?id=d3f2d45e2a024faf911a8af033eb769a",
        "object_id_field": "FID",
        "common_field": "USER_Type",
        "source_name": "Tree Record",
        "source_department": "City of Dearborn Heights",
        "ownership_raw": "City of Dearborn Heights",
        "note": "Integrated from the public City of Dearborn Heights tree record ArcGIS layer.",
        "clip_to_boundary": True,
    },
    "East Lansing": {
        "region": "mi",
        "layer_url": "https://gis2.cityofeastlansing.com/arcgis/rest/services/TREES_STATUS/FeatureServer/0",
        "dataset_page": "https://www.arcgis.com/home/item.html?id=0166cb5e3a124abfa845e26a15a10a13",
        "object_id_field": "OBJECTID",
        "common_field": "Tree_Name",
        "scientific_field": "dvSPP",
        "source_name": "TREES - CURRENT STATUS",
        "source_department": "City of East Lansing",
        "ownership_raw": "City of East Lansing",
        "note": "Integrated from the official City of East Lansing public tree status ArcGIS service.",
        "clip_to_boundary": True,
    },
    "Evanston": {
        "region": "il",
        "layer_url": "https://maps.cityofevanston.org/arcgis/rest/services/OpenData/ArcGISOpenData/MapServer/8",
        "dataset_page": "https://data.cityofevanston.org/datasets/evanston::trees",
        "object_id_field": "OBJECTID",
        "common_field": "Common",
        "genus_field": "Genus",
        "species_field": "SPP",
        "source_name": "Trees",
        "source_department": "City of Evanston",
        "ownership_raw": "City of Evanston",
        "note": "Integrated from the official City of Evanston public trees ArcGIS layer.",
        "clip_to_boundary": True,
    },
    "Grand Rapids": {
        "region": "mi",
        "layer_url": "https://services2.arcgis.com/L81TiOwAPO1ZvU9b/arcgis/rest/services/P2StreetTrees/FeatureServer/0",
        "dataset_page": "https://www.arcgis.com/home/item.html?id=8dd6632e710243d4b3620f2304e8e409",
        "object_id_field": "OBJECTID",
        "common_field": "COMMON",
        "scientific_field": "BOTANICAL",
        "source_name": "P2StreetTrees",
        "source_department": "City of Grand Rapids",
        "ownership_raw": "City of Grand Rapids",
        "note": "Integrated from the official City of Grand Rapids public street tree ArcGIS layer.",
        "clip_to_boundary": True,
    },
    "Johns Creek": {
        "region": "ga",
        "layer_url": "https://services1.arcgis.com/bqfNVPUK3HOnCFmA/arcgis/rest/services/Tree_Inventory/FeatureServer/0",
        "dataset_page": "https://services1.arcgis.com/bqfNVPUK3HOnCFmA/arcgis/rest/services/Tree_Inventory/FeatureServer",
        "object_id_field": "OBJECTID",
        "common_field": "TreeSpeciesFromML",
        "source_name": "Tree Inventory",
        "source_department": "City of Johns Creek",
        "ownership_raw": "City of Johns Creek",
        "note": "Integrated from the official City of Johns Creek public Tree Inventory ArcGIS layer using the published species labels.",
        "clip_to_boundary": True,
    },
    "Novi": {
        "region": "mi",
        "layer_url": "https://services1.arcgis.com/jwbgoAzqzCbiJmg4/arcgis/rest/services/Tree_Sites_public_view/FeatureServer/2",
        "dataset_page": "https://www.arcgis.com/home/item.html?id=7970c336e3814e789c4f7a9393db930c",
        "object_id_field": "OBJECTID",
        "common_field": "COMMONNAME",
        "scientific_field": "SPECIES",
        "source_name": "Tree Sites public view",
        "source_department": "City of Novi",
        "ownership_raw": "City of Novi",
        "note": "Integrated from the public City of Novi tree sites ArcGIS layer.",
        "clip_to_boundary": True,
    },
    "Franklin": {
        "region": "wi",
        "layer_url": "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0",
        "dataset_page": "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935",
        "object_id_field": "OBJECTID",
        "common_field": "Spp_Common",
        "scientific_field": "Spp_Latin",
        "source_name": "Tree Points - All (view)",
        "source_department": "Milwaukee County",
        "ownership_raw": "Milwaukee County",
        "note": "Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "Greenfield": {
        "region": "wi",
        "layer_url": "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0",
        "dataset_page": "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935",
        "object_id_field": "OBJECTID",
        "common_field": "Spp_Common",
        "scientific_field": "Spp_Latin",
        "source_name": "Tree Points - All (view)",
        "source_department": "Milwaukee County",
        "ownership_raw": "Milwaukee County",
        "note": "Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "Greendale": {
        "region": "wi",
        "layer_url": "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0",
        "dataset_page": "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935",
        "object_id_field": "OBJECTID",
        "common_field": "Spp_Common",
        "scientific_field": "Spp_Latin",
        "source_name": "Tree Points - All (view)",
        "source_department": "Milwaukee County",
        "ownership_raw": "Milwaukee County",
        "note": "Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "Milwaukee": {
        "region": "wi",
        "layer_url": "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0",
        "dataset_page": "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935",
        "object_id_field": "OBJECTID",
        "common_field": "Spp_Common",
        "scientific_field": "Spp_Latin",
        "source_name": "Tree Points - All (view)",
        "source_department": "Milwaukee County",
        "ownership_raw": "Milwaukee County",
        "note": "Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "Oak Creek": {
        "region": "wi",
        "layer_url": "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0",
        "dataset_page": "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935",
        "object_id_field": "OBJECTID",
        "common_field": "Spp_Common",
        "scientific_field": "Spp_Latin",
        "source_name": "Tree Points - All (view)",
        "source_department": "Milwaukee County",
        "ownership_raw": "Milwaukee County",
        "note": "Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "O'Fallon": {
        "region": "il",
        "layer_url": "https://services.arcgis.com/K8hCj4l2z1EMabnx/arcgis/rest/services/CityTrees/FeatureServer/1",
        "dataset_page": "https://services.arcgis.com/K8hCj4l2z1EMabnx/arcgis/rest/services/CityTrees/FeatureServer",
        "object_id_field": "OBJECTID",
        "common_field": "COMMON_NAME",
        "scientific_field": "TREESPECIES",
        "lon_field": "LONGITUDE",
        "lat_field": "LATITUDE",
        "source_name": "City Trees",
        "source_department": "City of O'Fallon",
        "ownership_raw": "City of O'Fallon",
        "note": "Integrated from the official City of O'Fallon public city tree ArcGIS service.",
        "clip_to_boundary": True,
    },
    "Shorewood": {
        "region": "wi",
        "layer_url": "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0",
        "dataset_page": "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935",
        "object_id_field": "OBJECTID",
        "common_field": "Spp_Common",
        "scientific_field": "Spp_Latin",
        "source_name": "Tree Points - All (view)",
        "source_department": "Milwaukee County",
        "ownership_raw": "Milwaukee County",
        "note": "Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "South Milwaukee": {
        "region": "wi",
        "layer_url": "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0",
        "dataset_page": "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935",
        "object_id_field": "OBJECTID",
        "common_field": "Spp_Common",
        "scientific_field": "Spp_Latin",
        "source_name": "Tree Points - All (view)",
        "source_department": "Milwaukee County",
        "ownership_raw": "Milwaukee County",
        "note": "Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "St. Francis": {
        "region": "wi",
        "layer_url": "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0",
        "dataset_page": "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935",
        "object_id_field": "OBJECTID",
        "common_field": "Spp_Common",
        "scientific_field": "Spp_Latin",
        "source_name": "Tree Points - All (view)",
        "source_department": "Milwaukee County",
        "ownership_raw": "Milwaukee County",
        "note": "Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "Tempe": {
        "region": "az",
        "layer_url": "https://services.arcgis.com/lQySeXwbBg53XWDi/arcgis/rest/services/TempeGuadalupe_CanopyCover2019_TreeInv_2021_Tempe_iTreeResults_TempeAZOct_2021_1/FeatureServer/0",
        "dataset_page": "https://data.tempe.gov/datasets/tempegov::tree-inventory",
        "object_id_field": "OBJECTID",
        "scientific_field": "Species_Name",
        "lon_field": "xCoordinate",
        "lat_field": "yCoordinate",
        "source_name": "Tree Inventory",
        "source_department": "City of Tempe",
        "ownership_raw": "City of Tempe",
        "note": "Integrated from the official City of Tempe tree inventory dataset published on the city ArcGIS open-data portal.",
        "clip_to_boundary": True,
    },
    "Wauwatosa": {
        "region": "wi",
        "layer_url": "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0",
        "dataset_page": "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935",
        "object_id_field": "OBJECTID",
        "common_field": "Spp_Common",
        "scientific_field": "Spp_Latin",
        "source_name": "Tree Points - All (view)",
        "source_department": "Milwaukee County",
        "ownership_raw": "Milwaukee County",
        "note": "Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
    "West Allis": {
        "region": "wi",
        "layer_url": "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0",
        "dataset_page": "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935",
        "object_id_field": "OBJECTID",
        "common_field": "Spp_Common",
        "scientific_field": "Spp_Latin",
        "source_name": "Tree Points - All (view)",
        "source_department": "Milwaukee County",
        "ownership_raw": "Milwaukee County",
        "note": "Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
        "clip_to_boundary": True,
    },
}

MILWAUKEE_COUNTY_TREE_VIEW_LAYER = (
    "https://utility.arcgis.com/usrsvcs/servers/18874e6d99b242878288adc0cf478841/rest/services/Environmental/Trees_View/FeatureServer/0"
)
MILWAUKEE_COUNTY_TREE_VIEW_PAGE = "https://experience.arcgis.com/experience/b1d9ccfd3a2949728e5b445bfdc78935"
MILWAUKEE_COUNTY_SUPPORTED_CITIES = (
    "Cudahy WI",
    "Fox Point",
    "Franklin",
    "Glendale WI",
    "Greenfield",
    "Greendale",
    "Hales Corners",
    "Milwaukee",
    "Oak Creek",
    "Shorewood",
    "South Milwaukee",
    "St. Francis",
    "Wauwatosa",
    "West Allis",
    "Whitefish Bay",
)

SUPPORTED_CITIES = (
    "Ann Arbor",
    "Albany",
    "Anaheim",
    "Annapolis",
    "Arlington",
    "Austin",
    "Azusa",
    "Baltimore",
    "Belmont",
    "Bell",
    "Beverly Hills",
    "Boston",
    "Buffalo",
    "Burbank",
    "Buena Park",
    "Camarillo",
    "Cambridge",
    "Chino",
    "Citrus Heights",
    "Concord",
    "Corona",
    "Costa Mesa",
    "Cudahy",
    "Cudahy WI",
    "Dana Point",
    "Dallas",
    "Danville",
    "Dearborn Heights",
    "Denver",
    "East Lansing",
    "El Segundo",
    "Encinitas",
    "Escondido",
    "Evanston",
    "Fairfax",
    "Falls Church",
    "Fox Point",
    "Franklin",
    "Fontana",
    "Fort Lee",
    "Greenfield",
    "Greenwich",
    "Glendale",
    "Glendale WI",
    "Greendale",
    "Goleta",
    "Grand Rapids",
    "Franklin Lakes",
    "Fremont",
    "Fullerton",
    "Gilroy",
    "Glen Rock",
    "Glendora",
    "Haworth",
    "Hales Corners",
    "Hartford",
    "Ho-Ho-Kus",
    "Hoboken",
    "Houston",
    "Huntington Park",
    "Inglewood",
    "Irvine",
    "Ithaca",
    "Johns Creek",
    "Jersey City",
    "La Mirada",
    "La Canada Flintridge",
    "La Verne",
    "Laguna Beach",
    "Las Vegas",
    "La Mesa",
    "Lodi",
    "Lynwood",
    "Linden",
    "Los Angeles",
    "Los Gatos",
    "Mahwah",
    "Maywood",
    "Millburn",
    "Milpitas",
    "Milwaukee",
    "Monterey Park",
    "Montclair",
    "Montreal",
    "Montvale",
    "Morgan Hill",
    "Morristown",
    "Mountain View",
    "New Haven",
    "New Milford",
    "New Westminster",
    "New York City",
    "Newark",
    "Newton",
    "Novi",
    "Newport Beach",
    "Norwalk",
    "Oradell",
    "Ottawa",
    "O'Fallon",
    "Oak Creek",
    "Oxnard",
    "Paramount",
    "Pasadena",
    "Philadelphia",
    "Pleasanton",
    "Pittsburgh",
    "Pomona",
    "Princeton",
    "Poway",
    "Ramsey",
    "Rancho Cucamonga",
    "Rancho Palos Verdes",
    "Redlands",
    "Redondo Beach",
    "Ridgewood",
    "River Edge",
    "Riverside",
    "Rutherford",
    "Sacramento",
    "Salinas",
    "Salt Lake City",
    "Saratoga Springs",
    "San Diego",
    "San Dimas",
    "San Fernando",
    "San Mateo",
    "San Rafael",
    "Santa Fe Springs",
    "Santa Barbara",
    "Santa Clarita",
    "Santa Monica",
    "Saratoga",
    "Santee",
    "Shorewood",
    "Somerville",
    "South Gate",
    "South Milwaukee",
    "Solana Beach",
    "South San Francisco",
    "Springfield",
    "Stamford",
    "St. Francis",
    "Sunnyvale",
    "Syracuse",
    "Tempe",
    "Teaneck",
    "Tenafly",
    "Thousand Oaks",
    "Torrance",
    "Toronto",
    "Troy",
    "Ventura",
    "Vista",
    "Wauwatosa",
    "Waltham",
    "West Allis",
    "West Hartford",
    "West Hollywood",
    "West Sacramento",
    "West Covina",
    "Westwood",
    "Whitefish Bay",
    "Worcester",
    "Wyckoff",
    "Yorba Linda",
    "Arcadia",
    "Commerce",
    "Downey",
)


def clean_display_name(raw_value: str | None) -> str | None:
    text = (raw_value or "").strip()
    if not text or text in {"<Null>", "N/A"}:
        return None
    text = re.sub(r"\s+", " ", text)
    for source, replacement in DISPLAY_NAME_REPLACEMENTS.items():
        text = text.replace(source, replacement)
    titled = title_case_if_upper(text)
    text = titled or text
    if text.count(",") == 1:
        left, right = [part.strip() for part in text.split(",", 1)]
        if left and right:
            text = f"{right} {left}"
    return text.strip()


def parse_species_text(raw_value: str | None) -> tuple[str, str | None]:
    text = clean_display_name(raw_value)
    if not text:
        return "", None
    match = SPECIES_TEXT_PATTERN.match(text)
    if match:
        common_name = clean_display_name(match.group("common"))
        scientific_raw = expand_abbreviated_botanical_name(match.group("scientific"), common_name)
        return scientific_raw, common_name
    return generic_scientific_name_for_common_hint(text), text


def clean_common_name(raw_value: str | None) -> str | None:
    text = clean_display_name(raw_value)
    if not text:
        return None
    letters = [character for character in text if character.isalpha()]
    if letters and all(character.islower() for character in letters):
        return text.title()
    return text


def format_scientific_display_name(raw_value: str | None, common_name: str | None = None) -> str:
    text = expand_abbreviated_botanical_name(raw_value, common_name).strip()
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text.replace("×", "x"))
    tokens = text.split(" ")
    formatted: list[str] = []
    lower_tokens = {"x", "sp", "sp.", "spp", "spp.", "species", "var", "var.", "subsp", "subsp.", "ssp", "ssp."}
    for index, token in enumerate(tokens):
        if not token:
            continue
        if index == 0 and re.search(r"[A-Za-z]", token):
            formatted.append(token.capitalize())
            continue
        if token.lower() in lower_tokens:
            formatted.append(token.lower())
            continue
        if token.startswith("'") and token.endswith("'"):
            formatted.append(token)
            continue
        if re.fullmatch(r"[A-Z][a-z]+", token):
            formatted.append(token)
            continue
        if re.search(r"[A-Za-z]", token):
            formatted.append(token.lower())
            continue
        formatted.append(token)
    return " ".join(formatted)


def parse_dash_species(raw_value: str | None) -> tuple[str, str | None]:
    text = (raw_value or "").strip()
    if not text:
        return "", None
    if " - " not in text:
        common_name = clean_common_name(text)
        return format_scientific_display_name(text, common_name), common_name
    scientific_part, common_part = text.split(" - ", 1)
    common_name = clean_common_name(common_part)
    scientific_raw = format_scientific_display_name(scientific_part, common_name)
    return scientific_raw, common_name


def classify_scientific_first(
    scientific_raw: str,
    common_name: str | None,
    mapping_rows: list[dict[str, str]],
    subtype_rows: list[dict[str, str]],
) -> tuple[str | None, str | None]:
    normalized = normalize_scientific_name(scientific_raw).lower()
    if normalized.startswith("prunus") or normalized.startswith("malus") or normalized.startswith("magnolia"):
        return classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
    if not scientific_raw:
        return classify_tree_record("", common_name, mapping_rows, subtype_rows)
    return None, None


def fetch_arcgis_inventory_city(
    *,
    city: str,
    region: str,
    layer_url: str,
    dataset_page: str,
    where: str,
    out_fields: list[str],
    object_id_field: str,
    source_name: str,
    source_department: str,
    ownership_raw: str,
    note: str,
    common_field: str | None = None,
    botanical_field: str | None = None,
    scientific_field: str | None = None,
    genus_field: str | None = None,
    species_field: str | None = None,
    lon_field: str | None = None,
    lat_field: str | None = None,
    zip_field: str | None = None,
) -> dict[str, Any]:
    layer_info = fetch_json(layer_url, {"f": "pjson"})
    total_payload = fetch_json(
        f"{layer_url}/query",
        {"where": where, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(layer_url, where, out_fields, object_id_field)
    zip_index = fetch_us_city_zip_index(city)
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    city_slug = slugify_token(city)
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        if (lon_raw is None or lat_raw is None) and lon_field and lat_field:
            lon_raw = attrs.get(lon_field)
            lat_raw = attrs.get(lat_field)
        try:
            lon = float(lon_raw) if lon_raw is not None else None
            lat = float(lat_raw) if lat_raw is not None else None
        except (TypeError, ValueError):
            lon = None
            lat = None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get(common_field)) if common_field else None
        if botanical_field and attrs.get(botanical_field):
            scientific_raw = format_scientific_display_name(attrs.get(botanical_field), common_name)
        elif scientific_field and attrs.get(scientific_field):
            scientific_raw = format_scientific_display_name(attrs.get(scientific_field), common_name)
        elif genus_field and attrs.get(genus_field):
            scientific_raw = format_scientific_display_name(
                f"{attrs.get(genus_field) or ''} {attrs.get(species_field) or ''}",
                common_name,
            )
        else:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_scientific_first(scientific_raw, common_name, mapping_rows, subtype_rows)
        zip_code = clean_display_name(attrs.get(zip_field)) if zip_field else None
        if not zip_code:
            zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"{city_slug}-{attrs.get(object_id_field)}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": city,
                "source_dataset": source_name,
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": city,
                    "source_dataset": source_name,
                    "source_department": source_department,
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": city,
        "region": region,
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": source_name,
            "city": city,
            "endpoint": dataset_page,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": note,
        },
    }


def clip_features_to_city_boundary(city: str, region: str, features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    boundary = load_city_boundary_geometry(city, state_id=region)
    clipped: list[dict[str, Any]] = []
    for feature in features:
        geom = feature.get("geometry", {})
        try:
            lon = float(geom.get("x"))
            lat = float(geom.get("y"))
        except (TypeError, ValueError):
            continue
        if point_in_geometry(lon, lat, boundary):
            clipped.append(feature)
    return clipped


def fetch_arcgis_inventory_city_result(
    *,
    city: str,
    region: str,
    layer_url: str,
    dataset_page: str,
    where: str,
    out_fields: list[str],
    object_id_field: str,
    source_name: str,
    source_department: str,
    ownership_raw: str,
    note: str,
    clip_to_boundary: bool = False,
    common_field: str | None = None,
    botanical_field: str | None = None,
    scientific_field: str | None = None,
    genus_field: str | None = None,
    species_field: str | None = None,
    lon_field: str | None = None,
    lat_field: str | None = None,
    zip_field: str | None = None,
) -> dict[str, Any]:
    layer_info = fetch_json(layer_url, {"f": "pjson"})
    features = fetch_arcgis_features_by_object_ids(
        layer_url,
        where=where,
        out_fields=out_fields,
        object_id_field=object_id_field,
    )
    if clip_to_boundary:
        features = clip_features_to_city_boundary(city, region, features)
    return build_arcgis_inventory_result(
        city=city,
        region=region,
        features=features,
        total_records=len(features),
        last_edit_at=iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate")),
        source_name=source_name,
        source_department=source_department,
        dataset_page=dataset_page,
        ownership_raw=ownership_raw,
        note=note,
        object_id_field=object_id_field,
        common_field=common_field,
        botanical_field=botanical_field,
        scientific_field=scientific_field,
        genus_field=genus_field,
        species_field=species_field,
        lon_field=lon_field,
        lat_field=lat_field,
        zip_field=zip_field,
    )


def build_arcgis_inventory_result(
    *,
    city: str,
    region: str,
    features: list[dict[str, Any]],
    total_records: int,
    last_edit_at: str,
    source_name: str,
    source_department: str,
    dataset_page: str,
    ownership_raw: str,
    note: str,
    object_id_field: str,
    common_field: str | None = None,
    botanical_field: str | None = None,
    scientific_field: str | None = None,
    genus_field: str | None = None,
    species_field: str | None = None,
    lon_field: str | None = None,
    lat_field: str | None = None,
    zip_field: str | None = None,
) -> dict[str, Any]:
    zip_index = fetch_us_city_zip_index(city, state_id=region)
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    city_slug = slugify_token(city)

    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        if (lon_raw is None or lat_raw is None) and lon_field and lat_field:
            lon_raw = attrs.get(lon_field)
            lat_raw = attrs.get(lat_field)
        try:
            lon = float(lon_raw) if lon_raw is not None else None
            lat = float(lat_raw) if lat_raw is not None else None
        except (TypeError, ValueError):
            lon = None
            lat = None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get(common_field)) if common_field else None
        if botanical_field and attrs.get(botanical_field):
            scientific_raw = format_scientific_display_name(attrs.get(botanical_field), common_name)
        elif scientific_field and attrs.get(scientific_field):
            scientific_raw = format_scientific_display_name(attrs.get(scientific_field), common_name)
        elif genus_field and attrs.get(genus_field):
            scientific_raw = format_scientific_display_name(
                f"{attrs.get(genus_field) or ''} {attrs.get(species_field) or ''}",
                common_name,
            )
        else:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_scientific_first(scientific_raw, common_name, mapping_rows, subtype_rows)
        zip_code = clean_display_name(attrs.get(zip_field)) if zip_field else None
        if not zip_code:
            zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"{city_slug}-{attrs.get(object_id_field)}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": city,
                "source_dataset": source_name,
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": city,
                    "source_dataset": source_name,
                    "source_department": source_department,
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": city,
        "region": region,
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": source_name,
            "city": city,
            "endpoint": dataset_page,
            "last_edit_at": last_edit_at,
            "records_fetched": total_records,
            "records_included": len(output_features),
            "note": note,
        },
    }


def fetch_arcgis_features_by_object_ids(
    layer_url: str,
    *,
    where: str,
    out_fields: list[str],
    object_id_field: str,
    chunk_size: int = 250,
) -> list[dict[str, Any]]:
    ids_payload = requests.get(
        f"{layer_url}/query",
        params={"where": where, "returnIdsOnly": "true", "f": "pjson"},
        timeout=60,
    ).json()
    if "error" in ids_payload:
        raise RuntimeError(f"ArcGIS error for {layer_url}: {ids_payload['error']}")
    object_ids = ids_payload.get("objectIds") or []
    features: list[dict[str, Any]] = []
    for start in range(0, len(object_ids), chunk_size):
        chunk = object_ids[start : start + chunk_size]
        response = requests.post(
            f"{layer_url}/query",
            data={
                "where": where,
                "objectIds": ",".join(str(value) for value in chunk),
                "outFields": ",".join(out_fields),
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "pjson",
            },
            timeout=60,
        )
        payload = response.json()
        if "error" in payload:
            raise RuntimeError(f"ArcGIS error for {layer_url}: {payload['error']}")
        features.extend(payload.get("features") or [])
    return features


def merge_city_results(
    *,
    city: str,
    region: str,
    dataset_page: str,
    source_name: str,
    source_department: str,
    note: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    total_records = 0
    last_edit_candidates: list[str] = []
    for result in results:
        features.extend(result["features"])
        normalized_rows.extend(result["normalized_rows"])
        source = result["source"]
        total_records += int(source.get("records_fetched") or 0)
        if source.get("last_edit_at"):
            last_edit_candidates.append(source["last_edit_at"])
    last_edit_at = max(last_edit_candidates) if last_edit_candidates else ""
    return {
        "city": city,
        "region": region,
        "features": features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": source_name,
            "city": city,
            "endpoint": dataset_page,
            "last_edit_at": last_edit_at,
            "records_fetched": total_records,
            "records_included": len(features),
            "note": note,
        },
    }


def domain_lookup(layer_info: dict[str, Any], field_name: str) -> dict[Any, str]:
    for field in layer_info.get("fields") or []:
        if field.get("name") != field_name:
            continue
        coded_values = ((field.get("domain") or {}).get("codedValues")) or []
        return {item.get("code"): str(item.get("name") or "") for item in coded_values}
    return {}


def load_remote_geojson(url: str) -> dict[str, Any]:
    response = subprocess.run(["curl", "-sL", url], capture_output=True, text=True, check=False)
    if response.returncode != 0:
        raise RuntimeError(f"Failed to download GeoJSON from {url}: {response.stderr.strip()}")
    return json.loads(response.stdout.lstrip("\ufeff"))


def iter_remote_csv_rows(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            text_stream = io.TextIOWrapper(response, encoding="utf-8-sig", newline="")
            yield from csv.DictReader(text_stream)
            return
    except Exception:
        pass

    insecure_context = ssl.create_default_context()
    insecure_context.check_hostname = False
    insecure_context.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(request, timeout=180, context=insecure_context) as response:
            text_stream = io.TextIOWrapper(response, encoding="utf-8-sig", newline="")
            yield from csv.DictReader(text_stream)
            return
    except Exception:
        pass

    with tempfile.NamedTemporaryFile("wb", suffix=".csv") as handle:
        result = subprocess.run(
            ["curl", "-sL", "-k", "--max-time", "600", "-o", handle.name, url],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to download CSV from {url}: {result.stderr.strip()}")
        with open(handle.name, "r", encoding="utf-8-sig", newline="") as csv_handle:
            yield from csv.DictReader(csv_handle)


def parse_point_geometry_text(raw_value: str | None) -> tuple[float | None, float | None]:
    text = (raw_value or "").strip()
    if not text:
        return None, None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        try:
            payload = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return None, None
    coordinates = payload.get("coordinates") or []
    if payload.get("type") == "MultiPoint" and coordinates and coordinates[0]:
        lon, lat = coordinates[0][:2]
        return float(lon), float(lat)
    if payload.get("type") == "Point" and len(coordinates) >= 2:
        lon, lat = coordinates[:2]
        return float(lon), float(lat)
    return None, None


def write_city_geojson(region: str, city: str, features: list[dict[str, Any]]) -> Path:
    path = PUBLIC_DATA_DIR / f"trees.{region}.city.{slugify_token(city)}.v1.geojson"
    payload = {"type": "FeatureCollection", "features": sorted(features, key=lambda item: item["properties"]["id"])}
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def load_normalized_rows() -> list[dict[str, str]]:
    path = NORMALIZED_DIR / "trees_normalized.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_row_for_csv(row: dict[str, Any]) -> dict[str, str]:
    return {column: str(row.get(column, "")) for column in NORMALIZED_HEADER}


def write_normalized_rows(rows: list[dict[str, Any]]) -> None:
    path = NORMALIZED_DIR / "trees_normalized.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized_rows = []
    for row in rows:
        normalized_rows.append(normalize_row_for_csv(row))
    normalized_rows.sort(key=lambda item: item["id"])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=NORMALIZED_HEADER)
        writer.writeheader()
        writer.writerows(normalized_rows)


def rewrite_normalized_rows(target_cities: set[str], new_rows: list[dict[str, Any]]) -> Path:
    path = NORMALIZED_DIR / "trees_normalized.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized_new_rows = [normalize_row_for_csv(row) for row in new_rows]
    normalized_new_rows.sort(key=lambda item: item["id"])

    for attempt in range(3):
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                newline="",
                dir=path.parent,
                prefix=f"{path.stem}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temp_path = Path(handle.name)
                writer = csv.DictWriter(handle, fieldnames=NORMALIZED_HEADER)
                writer.writeheader()
                if path.exists():
                    with path.open("r", encoding="utf-8", newline="") as source_handle:
                        reader = csv.DictReader(source_handle)
                        for row in reader:
                            if row.get("city") in target_cities:
                                continue
                            writer.writerow({column: str(row.get(column, "")) for column in NORMALIZED_HEADER})
                writer.writerows(normalized_new_rows)
            temp_path.replace(path)
            break
        except TimeoutError:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            if attempt == 2:
                raise
            time.sleep(1)
    return path


def recompute_unknown_items(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for row in rows:
        if row.get("included") == "1":
            continue
        scientific = (row.get("scientific_normalized") or "").strip()
        if scientific:
            counter[scientific] += 1
    return [
        {"scientific_name_normalized": name, "count": count}
        for name, count in counter.most_common()
    ]


def recompute_unknown_items_from_path(path: Path) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("included") == "1":
                continue
            scientific = (row.get("scientific_normalized") or "").strip()
            if scientific:
                counter[scientific] += 1
    return [
        {"scientific_name_normalized": name, "count": count}
        for name, count in counter.most_common()
    ]


def merge_unknown_items(
    existing_items: list[dict[str, Any]],
    new_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for item in existing_items:
        scientific = str(item.get("scientific_name_normalized") or "").strip()
        if scientific:
            counter[scientific] += int(item.get("count") or 0)
    for item in new_items:
        scientific = str(item.get("scientific_name_normalized") or "").strip()
        if scientific:
            counter[scientific] += int(item.get("count") or 0)
    return [
        {"scientific_name_normalized": name, "count": count}
        for name, count in counter.most_common()
    ]


def load_meta() -> dict[str, Any]:
    return json.loads((PUBLIC_DATA_DIR / "meta.v2.json").read_text(encoding="utf-8"))


def write_json_atomic(path: Path, payload: Any) -> None:
    tmp_path = path.with_name(f"{path.name}.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def save_meta(meta: dict[str, Any]) -> None:
    write_json_atomic(PUBLIC_DATA_DIR / "meta.v2.json", meta)


def ensure_region_entries(meta: dict[str, Any], regions: set[str]) -> None:
    existing = {region_entry.get("id") for region_entry in meta.get("regions", [])}
    for region_id in sorted(regions):
        if region_id in existing:
            continue
        meta.setdefault("regions", []).append(
            {
                "id": region_id,
                "label": REGION_LABELS[region_id],
                "available": True,
                "bounds": [[-123.08, 47.02], [-121.55, 48.08]],
                "data_path": None,
                "tree_count": 0,
                "city_count": 0,
                "cities": [],
                "species_counts": {species: 0 for species in SPECIES_GROUPS},
                "ownership_groups": [],
                "raw_bytes": 0,
                "gzip_bytes": 0,
                "warning_level": "none",
                "aggregate_raw_bytes": 0,
                "aggregate_gzip_bytes": 0,
                "aggregate_warning_level": "none",
                "largest_shard_raw_bytes": 0,
                "largest_shard_gzip_bytes": 0,
                "largest_shard_area": None,
                "area_split": {
                    "strategy": "area_shard",
                    "index_path": f"/data/trees.{region_id}.area-index.v2.json",
                    "area_count": 0,
                    "shard_count": 0,
                    "ready": False,
                },
            }
        )
    meta["regions"].sort(key=lambda item: item.get("id", ""))


def refresh_publish_indexes(target_regions: set[str], *, skip_global_refresh: bool = False) -> None:
    for region in sorted(target_regions):
        subprocess.run(
            ["python3", "scripts/refresh_region_area_shards.py", "--data-dir", "public/data", "--region", region],
            check=True,
        )
    if skip_global_refresh:
        return
    subprocess.run(
        ["python3", "scripts/refresh_coverage_metadata.py", "--data-dir", "public/data"],
        check=True,
    )
    subprocess.run(
        ["python3", "scripts/refresh_meta_species_summary.py", "--data-dir", "public/data"],
        check=True,
    )


def fetch_arlington() -> dict[str, Any]:
    layer_info = fetch_json(ARLINGTON_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{ARLINGTON_TREES_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        ARLINGTON_TREES_LAYER,
        "1=1",
        ["OBJECTID", "ID", "CommonName", "CultivarVariety", "Ownership", "Jurisdiction"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("Arlington")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon = geom.get("x")
        lat = geom.get("y")
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("CommonName"))
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("CultivarVariety"))
        if cultivar and not subtype_name:
            subtype_name = cultivar
        ownership_raw = (
            clean_display_name(attrs.get("Jurisdiction"))
            or clean_display_name(attrs.get("Ownership"))
            or "Arlington County"
        )
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"arlington-{attrs.get('ID') or attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Arlington",
                "source_dataset": "DPR Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Arlington",
                    "source_dataset": "DPR Trees",
                    "source_department": "Arlington County",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Arlington",
        "region": "va",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "DPR Trees",
            "city": "Arlington",
            "endpoint": ARLINGTON_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from Arlington County's official public DPR Trees layer using the official county jurisdiction boundary.",
        },
    }


def fetch_austin() -> dict[str, Any]:
    rows = fetch_soda_rows(AUSTIN_DATASET, where=AUSTIN_BLOSSOM_WHERE, order="species")
    total_records = fetch_soda_count(AUSTIN_DATASET, where=AUSTIN_BLOSSOM_WHERE)
    zip_index = fetch_us_city_zip_index("Austin")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        lon: float | None = None
        lat: float | None = None
        try:
            lon = float(row.get("longtitude"))
            lat = float(row.get("latitude"))
        except (TypeError, ValueError):
            lon = None
            lat = None
        if lon is None or lat is None or not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
            geometry = row.get("geometry") or {}
            coordinates = geometry.get("coordinates") or []
            if len(coordinates) >= 2:
                try:
                    geometry_lon = float(coordinates[0])
                    geometry_lat = float(coordinates[1])
                except (TypeError, ValueError):
                    geometry_lon = None
                    geometry_lat = None
                if (
                    geometry_lon is not None
                    and geometry_lat is not None
                    and -180.0 <= geometry_lon <= 180.0
                    and -90.0 <= geometry_lat <= 90.0
                ):
                    lon = geometry_lon
                    lat = geometry_lat
        if lon is None or lat is None or not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
            continue

        scientific_raw, common_name = parse_species_text(row.get("species"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Austin"
        zip_code = assign_zip_code(lon, lat, zip_index)
        fingerprint = hashlib.md5(
            f"{common_name or scientific_raw}|{lat:.6f}|{lon:.6f}".encode("utf-8")
        ).hexdigest()[:12]
        row_id = f"austin-{fingerprint}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Austin",
                "source_dataset": "Tree Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Austin",
                    "source_dataset": "Tree Inventory",
                    "source_department": "City of Austin",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Austin",
        "region": "tx",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventory",
            "city": "Austin",
            "endpoint": AUSTIN_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": total_records,
            "records_included": len(output_features),
            "note": "Integrated from the official City of Austin Tree Inventory dataset using blossom-side Socrata filtering.",
        },
    }


def fetch_boston() -> dict[str, Any]:
    payload = load_remote_geojson(BOSTON_TREES_GEOJSON)
    features = payload.get("features", [])
    zip_index = fetch_us_city_zip_index("Boston")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates") or []
        if len(coordinates) != 2:
            continue
        lon, lat = coordinates

        common_name = clean_common_name(attrs.get("spp_com"))
        scientific_raw = format_scientific_display_name(attrs.get("spp_bot"), common_name)
        if not scientific_raw:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Boston"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"boston-{attrs.get('id') or attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Boston",
                "source_dataset": "BPRD Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Boston",
                    "source_dataset": "BPRD Trees",
                    "source_department": "Boston Parks and Recreation Department",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Boston",
        "region": "ma",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "BPRD Trees",
            "city": "Boston",
            "endpoint": BOSTON_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": len(features),
            "records_included": len(output_features),
            "note": "Integrated from the official Analyze Boston BPRD Trees download, which includes both street and park trees.",
        },
    }


def fetch_baltimore() -> dict[str, Any]:
    layer_info = fetch_json(BALTIMORE_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{BALTIMORE_TREES_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        BALTIMORE_TREES_LAYER,
        "SPP LIKE 'Prunus%' OR SPP LIKE 'Malus%' OR SPP LIKE 'Magnolia%'",
        ["OBJECTID", "ID", "UniqueID", "Address", "Street", "SPP", "CULTIVAR", "CONDITION", "DBH"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("Baltimore")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon = geom.get("x")
        lat = geom.get("y")
        if lon is None or lat is None:
            continue

        common_name = None
        scientific_raw = format_scientific_display_name(attrs.get("SPP"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("CULTIVAR"))
        if cultivar and not subtype_name:
            subtype_name = cultivar
        ownership_raw = "City of Baltimore"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"baltimore-{attrs.get('UniqueID') or attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Baltimore",
                "source_dataset": "Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Baltimore",
                    "source_dataset": "Trees",
                    "source_department": "Baltimore City Forestry",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Baltimore",
        "region": "md",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Trees",
            "city": "Baltimore",
            "endpoint": BALTIMORE_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official Baltimore city forestry ArcGIS tree layer on gis.baltimorecity.gov.",
        },
    }


def fetch_dallas() -> dict[str, Any]:
    summary_payload, rows = fetch_treekeeper_rows(
        f"{DALLAS_TREEKEEPER_BASE}/cffiles/search.cfc",
        f"{DALLAS_TREEKEEPER_BASE}/cffiles/grids.cfc",
        uid="pinkhunter-dallas",
        fac_id=1,
    )
    zip_index = fetch_us_city_zip_index("Dallas")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        lon = row.get("LONGITUDE")
        lat = row.get("LATITUDE")
        if lon is None or lat is None:
            geometry_raw = row.get("SITE_GEOMETRY")
            if isinstance(geometry_raw, str) and geometry_raw.strip():
                try:
                    geometry_payload = json.loads(geometry_raw)
                    coordinates = geometry_payload.get("coordinates") or []
                    lon, lat = coordinates[0], coordinates[1]
                except Exception:
                    lon = None
                    lat = None
        if lon is None or lat is None:
            continue

        scientific_raw, common_name = parse_species_text(row.get("SITE_ATTR1"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = clean_display_name(row.get("SITE_ATTR33")) or clean_display_name(row.get("SITE_ATTR32")) or "City of Dallas"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"dallas-{row.get('SITE_ID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Dallas",
                "source_dataset": "Public Tree Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Dallas",
                    "source_dataset": "Public Tree Inventory",
                    "source_department": "City of Dallas",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Dallas",
        "region": "tx",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Public Tree Inventory",
            "city": "Dallas",
            "endpoint": DALLAS_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": int(summary_payload.get("siteCount") or len(rows)),
            "records_included": len(output_features),
            "note": "Integrated from the official Dallas Public Tree Inventory TreeKeeper page linked by the city forestry page.",
        },
    }


def fetch_jersey_city() -> dict[str, Any]:
    layer_info = fetch_json(JERSEY_CITY_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{JERSEY_CITY_TREES_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        JERSEY_CITY_TREES_LAYER,
        "1=1",
        ["FID", "site_id", "species", "species_1", "species_1_", "site_comme", "condition", "address"],
        "FID",
    )
    zip_index = fetch_us_city_zip_index("Jersey City")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon = geom.get("x")
        lat = geom.get("y")
        if lon is None or lat is None:
            continue

        species_text = attrs.get("species") or attrs.get("species_1")
        scientific_raw, common_name = parse_species_text(species_text)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("species_1_"))
        if cultivar and not subtype_name:
            subtype_name = cultivar
        ownership_raw = "City of Jersey City"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"jersey-city-{attrs.get('site_id') or attrs.get('FID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Jersey City",
                "source_dataset": "City of Jersey City Tree Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Jersey City",
                    "source_dataset": "City of Jersey City Tree Inventory",
                    "source_department": "City of Jersey City",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Jersey City",
        "region": "nj",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "City of Jersey City Tree Inventory",
            "city": "Jersey City",
            "endpoint": JERSEY_CITY_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the public Jersey City Tree Inventory service referenced by the city's Urban Forests materials.",
        },
    }


def fetch_milpitas() -> dict[str, Any]:
    info = fetch_json(MILPITAS_LAYER, {"f": "pjson"})
    features = fetch_all_features(
        MILPITAS_LAYER,
        "1=1",
        ["OBJECTID", "Name", "Genus", "Species", "OwnedBy", "MaintBy"],
        "OBJECTID",
    )
    owner_domain = domain_lookup(info, "OwnedBy")
    zip_index = fetch_us_city_zip_index("Milpitas")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("Species") or "").strip()
        common_name = title_case_if_upper(attrs.get("Name")) or None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        owned_by = owner_domain.get(attrs.get("OwnedBy")) or ""
        if owned_by == "<null>":
            owned_by = ""
        maintained_by = title_case_if_upper(attrs.get("MaintBy")) or ""
        ownership_raw = owned_by or maintained_by or "Unknown"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)
        row_id = f"milpitas-{attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Milpitas",
                "source_dataset": "Trees RO",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": geom.get("y"),
                "lon": geom.get("x"),
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Milpitas",
                    "source_dataset": "Trees RO",
                    "source_department": "City of Milpitas",
                    "source_last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
                },
            }
        )

    return {
        "city": "Milpitas",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Trees RO",
            "city": "Milpitas",
            "endpoint": MILPITAS_DATASET_PAGE,
            "last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
            "records_fetched": len(features),
            "records_included": len(output_features),
        },
    }


def fetch_san_mateo() -> dict[str, Any]:
    info = fetch_json(SAN_MATEO_LAYER, {"f": "pjson"})
    features = fetch_all_features(
        SAN_MATEO_LAYER,
        "ACTIVE=1",
        ["OBJECTID", "ACTIVE", "SPP", "ID", "UNIQUEID"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("San Mateo")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("SPP") or "").strip()
        common_name = None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of San Mateo"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)
        row_id = f"san-mateo-{attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "San Mateo",
                "source_dataset": "Street Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": geom.get("y"),
                "lon": geom.get("x"),
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "San Mateo",
                    "source_dataset": "Street Trees",
                    "source_department": "City of San Mateo Public Works",
                    "source_last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
                },
            }
        )

    return {
        "city": "San Mateo",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Street Trees",
            "city": "San Mateo",
            "endpoint": SAN_MATEO_DATASET_PAGE,
            "last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
            "records_fetched": len(features),
            "records_included": len(output_features),
        },
    }


def fetch_san_rafael() -> dict[str, Any]:
    info = fetch_json(SAN_RAFAEL_TREES_LAYER, {"f": "pjson"})
    features = fetch_all_features(
        SAN_RAFAEL_TREES_LAYER,
        "1=1",
        ["ObjectId", "UniqueID", "Species_Name", "Condition", "Species_Type"],
        "ObjectId",
    )
    zip_index = fetch_us_city_zip_index("San Rafael")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        common_name = title_case_if_upper(attrs.get("Species_Name")) or None
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of San Rafael"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)
        row_id = f"san-rafael-{attrs.get('UniqueID') or attrs.get('ObjectId')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "San Rafael",
                "source_dataset": "Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": geom.get("y"),
                "lon": geom.get("x"),
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw or "",
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "San Rafael",
                    "source_dataset": "Trees",
                    "source_department": "City of San Rafael",
                    "source_last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
                },
            }
        )

    return {
        "city": "San Rafael",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Trees",
            "city": "San Rafael",
            "endpoint": SAN_RAFAEL_DATASET_PAGE,
            "last_edit_at": iso_from_epoch(info.get("editingInfo", {}).get("lastEditDate")),
            "records_fetched": len(features),
            "records_included": len(output_features),
        },
    }


def init_treeplotter_session(folder: str, landing_url: str) -> str:
    fd, cookie_path = tempfile.mkstemp(prefix=f"{slugify_token(folder)}_", suffix=".cookies")
    os.close(fd)
    landing = subprocess.run(["curl", "-sL", "-c", cookie_path, landing_url], capture_output=True, text=True, check=False)
    if landing.returncode != 0:
        raise RuntimeError(f"Failed to open TreePlotter landing page for {folder}: {landing.stderr.strip()}")
    payload = post_form_with_curl(
        FREMONT_DB_ENDPOINT,
        [("action", "sessionCheck"), ("params[folder]", folder)],
        headers={"X-Client-Version": TREEPLOTTER_CLIENT_VERSION},
        cookie_path=cookie_path,
    )
    if payload.get("status") != "OK":
        raise RuntimeError(f"TreePlotter sessionCheck failed for {folder}: {payload}")
    return cookie_path


def retrieve_treeplotter_rows(
    folder: str,
    table: str,
    fields: dict[str, dict[str, str]],
    *,
    cookie_path: str,
    limit: int = 2000,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        form = [
            ("action", "retrieveDataAlias"),
            ("params[folder]", folder),
            ("params[table]", table),
            ("params[firstIndex]", offset),
            ("params[limit]", limit),
            ("params[sortBy]", "pid"),
            ("params[sortOrder]", "asc"),
            ("params[timezoneOffset]", 0),
        ]
        for field_name, details in fields.items():
            form.extend(
                [
                    (f"params[fields][{field_name}][data_type]", details["data_type"]),
                    (f"params[fields][{field_name}][input_type]", details["input_type"]),
                    (f"params[fields][{field_name}][name]", field_name),
                    (f"params[fields][{field_name}][referencer]", table),
                ]
            )
        payload = post_form_with_curl(
            FREMONT_DB_ENDPOINT,
            form,
            headers={"X-Client-Version": TREEPLOTTER_CLIENT_VERSION},
            cookie_path=cookie_path,
        )
        if payload.get("status") != "OK":
            raise RuntimeError(f"TreePlotter retrieveDataAlias failed for {folder}/{table} at offset {offset}: {payload}")
        batch = payload.get("resultsArray") or []
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < limit:
            break
        offset += len(batch)
    return rows


def fetch_treeplotter_inventory(
    *,
    city: str,
    folder: str,
    landing_url: str,
    dataset_page: str,
    source_note: str,
    region: str = "ca",
    source_name: str = "Tree Inventory",
    source_department: str | None = None,
    ownership_raw: str = "Not published in public inventory",
    boundary_layer: str | None = None,
    clip_to_boundary: bool = False,
) -> dict[str, Any]:
    source_last_edit_at = ""
    if boundary_layer:
        boundary_info = fetch_json(boundary_layer, {"f": "pjson"})
        source_last_edit_at = iso_from_epoch((boundary_info.get("editingInfo") or {}).get("lastEditDate"))
    zip_index = fetch_us_city_zip_index(city)
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    boundary_geometry = load_city_boundary_geometry(city, state_id=region) if clip_to_boundary else None

    cookie_path = init_treeplotter_session(folder, landing_url)
    try:
        lookup_rows = retrieve_treeplotter_rows(
            folder,
            "species",
            {
                "pid": {"data_type": "integer", "input_type": "number"},
                "sp_code": {"data_type": "character varying", "input_type": "text"},
                "genus": {"data_type": "character varying", "input_type": "text"},
                "latin_name": {"data_type": "character varying", "input_type": "text"},
                "common_name": {"data_type": "character varying", "input_type": "text"},
                "cultivar": {"data_type": "character varying", "input_type": "text"},
            },
            cookie_path=cookie_path,
        )
        species_lookup: dict[Any, dict[str, str]] = {}
        for row in lookup_rows:
            pid = row["pid"]["val"]
            species_lookup[pid] = {
                "latin_name": row["latin_name"]["alias"] or row["latin_name"]["val"] or "",
                "common_name": row["common_name"]["alias"] or row["common_name"]["val"] or "",
                "cultivar": row["cultivar"]["alias"] or row["cultivar"]["val"] or "",
            }

        tree_rows = retrieve_treeplotter_rows(
            folder,
            "trees",
            {
                "pid": {"data_type": "integer", "input_type": "number"},
                "geom": {"data_type": "geometry", "input_type": "hidden"},
                "species_common": {"data_type": "integer", "input_type": "select"},
                "species_latin": {"data_type": "integer", "input_type": "select"},
                "species_code": {"data_type": "integer", "input_type": "select"},
                "species_cultivar": {"data_type": "integer", "input_type": "select"},
                "organization": {"data_type": "character varying", "input_type": "text"},
                "park_name": {"data_type": "character varying", "input_type": "text"},
                "status": {"data_type": "integer", "input_type": "select"},
            },
            cookie_path=cookie_path,
            limit=5000,
        )
    finally:
        Path(cookie_path).unlink(missing_ok=True)

    city_slug = slugify_token(city)
    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in tree_rows:
        geom_hex = row.get("geom", {}).get("val") or row.get("geom", {}).get("alias")
        point = decode_wkb_point_hex(geom_hex)
        if not point:
            continue
        lon, lat = web_mercator_to_lon_lat(*point)
        if boundary_geometry and not point_in_geometry(lon, lat, boundary_geometry):
            continue
        species_id = (
            row.get("species_latin", {}).get("val")
            or row.get("species_common", {}).get("val")
            or row.get("species_code", {}).get("val")
        )
        species_info = species_lookup.get(species_id, {})
        common_name = clean_display_name(species_info.get("common_name"))
        latin_name = species_info.get("latin_name") or ""
        scientific_raw = expand_abbreviated_botanical_name(latin_name, common_name)
        if not scientific_raw:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar_name = clean_display_name(species_info.get("cultivar"))
        if cultivar_name and not subtype_name:
            subtype_name = cultivar_name
        ownership_raw = "Not published in public inventory"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"{city_slug}-{row.get('pid', {}).get('val')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": city,
                "source_dataset": source_name,
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": city,
                    "source_dataset": source_name,
                    "source_department": source_department or f"City of {city}",
                    "source_last_edit_at": source_last_edit_at,
                },
            }
        )

    return {
        "city": city,
        "region": region,
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": source_name,
            "city": city,
            "endpoint": dataset_page,
            "last_edit_at": source_last_edit_at,
            "records_fetched": len(tree_rows),
            "records_included": len(output_features),
            "note": source_note,
        },
    }


def fetch_treekeeper_rows(search_endpoint: str, grids_endpoint: str, uid: str, fac_id: int = 1) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summary_payload = fetch_json(
        search_endpoint,
        {
            "method": "submitMapSearch",
            "uid": uid,
            "facID": fac_id,
            "searchCurrentSelection": "false",
            "returnFormat": "json",
        },
        method="POST",
        body={},
    )

    rows: list[dict[str, Any]] = []
    limit = 5000
    offset = 0
    total_rows = int(summary_payload.get("siteCount") or 0)
    while True:
        rows_payload = fetch_json(
            grids_endpoint,
            {
                "method": "getTreeKeeperGridOptionsData",
                "session_id": uid,
                "layer_id": fac_id,
                "gridType": "sites",
                "calls_search": "true",
                "limit": limit,
                "offset": offset,
                "stopCache": int(dt.datetime.now(tz=dt.timezone.utc).timestamp() * 1000),
            },
            method="POST",
            body={"filters": "[]", "sorts": "[]"},
        )
        batch = rows_payload.get("data") or []
        if isinstance(batch, str):
            batch = json.loads(batch)
        if not batch:
            break
        rows.extend(batch)
        if total_rows and len(rows) >= total_rows:
            break
        if len(batch) < limit:
            break
        offset += limit

    return summary_payload if isinstance(summary_payload, dict) else {}, rows


def treekeeper_point_from_row(row: dict[str, Any]) -> tuple[float | None, float | None]:
    lon = row.get("LONGITUDE")
    lat = row.get("LATITUDE")
    try:
        if lon is not None and lat is not None:
            return float(lon), float(lat)
    except (TypeError, ValueError):
        pass

    geometry_raw = row.get("SITE_GEOMETRY")
    if isinstance(geometry_raw, str) and geometry_raw.strip():
        try:
            geometry_payload = json.loads(geometry_raw)
            coordinates = geometry_payload.get("coordinates") or []
            if len(coordinates) >= 2:
                return float(coordinates[0]), float(coordinates[1])
        except Exception:
            return None, None
    return None, None


def detect_treekeeper_species_field(
    rows: list[dict[str, Any]],
    mapping_rows: list[dict[str, str]],
    subtype_rows: list[dict[str, str]],
) -> str | None:
    sample_rows = rows[: min(len(rows), 400)]
    candidate_keys = sorted(
        {
            key
            for row in sample_rows
            for key, value in row.items()
            if re.fullmatch(r"SITE_ATTR\d+", key)
            and value not in (None, "")
            and re.search(r"[A-Za-z]", str(value))
        }
    )
    best_key: str | None = None
    best_score = -1
    best_nonempty = -1

    for key in candidate_keys:
        score = 0
        nonempty = 0
        for row in sample_rows:
            raw_value = row.get(key)
            text = clean_display_name(str(raw_value) if raw_value is not None else None)
            if not text:
                continue
            nonempty += 1
            scientific_raw, common_name = parse_species_text(text)
            species_group, _ = classify_scientific_first(scientific_raw, common_name, mapping_rows, subtype_rows)
            if species_group:
                score += 1
        if score > best_score or (score == best_score and nonempty > best_nonempty):
            best_key = key
            best_score = score
            best_nonempty = nonempty

    return best_key


def fetch_treekeeper_inventory_city(
    *,
    city: str,
    base_url: str,
    uid: str,
    region: str = "nj",
    fac_id: int = 1,
    source_name: str = "TreeKeeper Inventory",
    source_department: str | None = None,
    ownership_raw: str | None = None,
    note: str | None = None,
    use_zip_index: bool = True,
) -> dict[str, Any]:
    summary_payload, rows = fetch_treekeeper_rows(
        f"{base_url.rstrip('/')}/cffiles/search.cfc",
        f"{base_url.rstrip('/')}/cffiles/grids.cfc",
        uid=uid,
        fac_id=fac_id,
    )
    boundary_geometry = load_city_boundary_geometry(city, state_id=region)
    zip_index = fetch_us_city_zip_index(city, state_id=region) if use_zip_index else []
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    species_field = detect_treekeeper_species_field(rows, mapping_rows, subtype_rows) or "SITE_ATTR1"
    owner_label = ownership_raw or f"City of {city}"
    department_label = source_department or city
    city_slug = slugify_token(city)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        lon, lat = treekeeper_point_from_row(row)
        if lon is None or lat is None:
            continue
        if boundary_geometry and not point_in_geometry(lon, lat, boundary_geometry):
            continue
        scientific_raw, common_name = parse_species_text(row.get(species_field))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_scientific_first(scientific_raw, common_name, mapping_rows, subtype_rows)
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"{city_slug}-{row.get('SITE_ID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": city,
                "source_dataset": source_name,
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(owner_label),
                "ownership_raw": owner_label,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(owner_label),
                    "ownership_raw": owner_label,
                    "city": city,
                    "source_dataset": source_name,
                    "source_department": department_label,
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": city,
        "region": region,
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": source_name,
            "city": city,
            "endpoint": base_url,
            "last_edit_at": "",
            "records_fetched": int(summary_payload.get("siteCount") or len(rows)),
            "records_included": len(output_features),
            "note": note
            or f"Integrated from the official {city} public TreeKeeper inventory and jurisdiction boundary.",
        },
    }


def build_nyc_metro_treekeeper_fetcher(city: str, config: dict[str, str]) -> Any:
    return lambda city=city, config=config: fetch_treekeeper_inventory_city(
        city=city,
        base_url=config["base_url"],
        uid=config["uid"],
        region="nj",
        source_department=city,
        use_zip_index=False,
    )


def build_treekeeper_fetcher(city: str, config: dict[str, Any]) -> Any:
    return lambda city=city, config=config: fetch_treekeeper_inventory_city(
        city=city,
        base_url=config["base_url"],
        uid=config["uid"],
        region=str(config["region"]),
        source_department=config.get("source_department"),
        note=config.get("note"),
        use_zip_index=bool(config.get("use_zip_index", True)),
    )


def build_nyc_metro_arcgis_fetcher(city: str, config: dict[str, Any]) -> Any:
    return lambda city=city, config=config: fetch_arcgis_inventory_city(
        city=city,
        region="nj",
        layer_url=config["layer_url"],
        dataset_page=config["dataset_page"],
        where="1=1",
        out_fields=["*"],
        object_id_field=config["object_id_field"],
        source_name="Tree Inventory",
        source_department=config["source_department"],
        ownership_raw=f"City of {city}",
        note=config["note"],
        common_field=config.get("common_field"),
        botanical_field=config.get("botanical_field"),
        scientific_field=config.get("scientific_field"),
        genus_field=config.get("genus_field"),
        species_field=config.get("species_field"),
        lon_field=config.get("lon_field"),
        lat_field=config.get("lat_field"),
        zip_field=config.get("zip_field"),
    )


def build_arcgis_fetcher(city: str, config: dict[str, Any]) -> Any:
    return lambda city=city, config=config: fetch_arcgis_inventory_city_result(
        city=city,
        region=str(config["region"]),
        layer_url=str(config["layer_url"]),
        dataset_page=str(config["dataset_page"]),
        where=str(config.get("where", "1=1")),
        out_fields=list(config.get("out_fields", ["*"])),
        object_id_field=str(config["object_id_field"]),
        source_name=str(config.get("source_name", "Tree Inventory")),
        source_department=str(config["source_department"]),
        ownership_raw=str(config.get("ownership_raw", config["source_department"])),
        note=str(config["note"]),
        clip_to_boundary=bool(config.get("clip_to_boundary", False)),
        common_field=config.get("common_field"),
        botanical_field=config.get("botanical_field"),
        scientific_field=config.get("scientific_field"),
        genus_field=config.get("genus_field"),
        species_field=config.get("species_field"),
        lon_field=config.get("lon_field"),
        lat_field=config.get("lat_field"),
        zip_field=config.get("zip_field"),
    )


@lru_cache(maxsize=1)
def load_milwaukee_county_tree_view() -> tuple[list[dict[str, Any]], str]:
    layer_info = fetch_json(MILWAUKEE_COUNTY_TREE_VIEW_LAYER, {"f": "pjson"})
    features = fetch_arcgis_features_by_object_ids(
        MILWAUKEE_COUNTY_TREE_VIEW_LAYER,
        where="1=1",
        out_fields=["OBJECTID", "OwnedBy", "MaintainedBy", "Spp_Latin", "Spp_Common"],
        object_id_field="OBJECTID",
        chunk_size=2000,
    )
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))
    return features, last_edit_at


def build_milwaukee_county_fetcher(city: str) -> Any:
    def fetcher(city: str = city) -> dict[str, Any]:
        features, last_edit_at = load_milwaukee_county_tree_view()
        clipped_features = clip_features_to_city_boundary(city, "wi", features)
        return build_arcgis_inventory_result(
            city=city,
            region="wi",
            features=clipped_features,
            total_records=len(clipped_features),
            last_edit_at=last_edit_at,
            source_name="Tree Points - All (view)",
            source_department="Milwaukee County",
            dataset_page=MILWAUKEE_COUNTY_TREE_VIEW_PAGE,
            ownership_raw="Milwaukee County",
            note="Integrated from the official Milwaukee County public tree viewer and official jurisdiction boundary clipping.",
            object_id_field="OBJECTID",
            common_field="Spp_Common",
            scientific_field="Spp_Latin",
        )

    return fetcher


def fetch_los_angeles_filtered_rows() -> list[dict[str, Any]]:
    uid = "pinkhunter-los-angeles"
    search_url = (
        f"{LOS_ANGELES_TREEKEEPER_BASE}/cffiles/search.cfc"
        f"?method=submitMapSearch&uid={uid}&facID={LOS_ANGELES_FACILITY_ID}&searchCurrentSelection=false&returnFormat=json"
    )
    grids_url = (
        f"{LOS_ANGELES_TREEKEEPER_BASE}/cffiles/grids.cfc"
        f"?method=getTreeKeeperGridOptionsData&session_id={uid}&layer_id={LOS_ANGELES_FACILITY_ID}"
        "&gridType=sites&calls_search=true"
    )
    rows_by_site_id: dict[str, dict[str, Any]] = {}

    with tempfile.NamedTemporaryFile(prefix="la_tk_", suffix=".cookies", delete=False) as handle:
        cookie_path = handle.name

    try:
        bootstrap = subprocess.run(
            [
                "curl",
                "-k",
                "-sL",
                "-c",
                cookie_path,
                "-b",
                cookie_path,
                f"{LOS_ANGELES_TREEKEEPER_BASE}/index.cfm?deviceWidth=1440",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if bootstrap.returncode != 0:
            raise RuntimeError(f"Failed to open Los Angeles TreeKeeper landing page: {bootstrap.stderr.strip()}")

        start_search = subprocess.run(
            [
                "curl",
                "-k",
                "-sL",
                "-c",
                cookie_path,
                "-b",
                cookie_path,
                "-H",
                "Content-Type: application/json",
                "-X",
                "POST",
                "--data",
                "{}",
                search_url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if start_search.returncode != 0:
            raise RuntimeError(f"Los Angeles submitMapSearch failed: {start_search.stderr.strip()}")

        for term in LOS_ANGELES_TREEKEEPER_TERMS:
            offset = 0
            limit = 5000
            total_rows = None
            while True:
                body = json.dumps(
                    {
                        "filters": json.dumps([{"name": "SITE_ATTR1", "term": term}]),
                        "sorts": "[]",
                    }
                )
                response = subprocess.run(
                    [
                        "curl",
                        "-k",
                        "-sL",
                        "-c",
                        cookie_path,
                        "-b",
                        cookie_path,
                        "-H",
                        "Content-Type: application/json",
                        "-X",
                        "POST",
                        "--data",
                        body,
                        f"{grids_url}&limit={limit}&offset={offset}&stopCache={int(dt.datetime.now(tz=dt.timezone.utc).timestamp() * 1000)}",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if response.returncode != 0:
                    raise RuntimeError(
                        f"Los Angeles TreeKeeper filtered grid fetch failed for term {term}: {response.stderr.strip()}"
                    )
                payload = json.loads(response.stdout or "{}")
                batch = payload.get("data") or []
                if isinstance(batch, str):
                    batch = json.loads(batch)
                if total_rows is None:
                    try:
                        total_rows = int(payload.get("rowCount") or 0)
                    except Exception:
                        total_rows = 0
                if not batch:
                    break
                for row in batch:
                    site_id = str(row.get("SITE_ID") or row.get("SITE_ATTR40") or "").strip()
                    if site_id:
                        rows_by_site_id[site_id] = row
                if total_rows and offset + len(batch) >= total_rows:
                    break
                if len(batch) < limit:
                    break
                offset += len(batch)
        return list(rows_by_site_id.values())
    finally:
        Path(cookie_path).unlink(missing_ok=True)


def fetch_fremont() -> dict[str, Any]:
    return fetch_treeplotter_inventory(
        city="Fremont",
        folder="FremontCA",
        landing_url=FREMONT_TREEPLOTTER_URL,
        boundary_layer=FREMONT_BOUNDARY_LAYER,
        dataset_page=FREMONT_DATASET_PAGE,
        source_note="Integrated via public TreePlotter session + official species lookup table.",
    )


def fetch_concord() -> dict[str, Any]:
    return fetch_treeplotter_inventory(
        city="Concord",
        folder="ConcordCA",
        landing_url=CONCORD_TREEPLOTTER_URL,
        boundary_layer=CONCORD_BOUNDARY_LAYER,
        dataset_page=CONCORD_DATASET_PAGE,
        source_note="Integrated via the official Concord TreePlotter page and city GIS boundary.",
    )


def build_treeplotter_fetcher(city: str, config: dict[str, Any]) -> Any:
    return lambda city=city, config=config: fetch_treeplotter_inventory(
        city=city,
        folder=str(config["folder"]),
        landing_url=str(config["landing_url"]),
        dataset_page=str(config.get("dataset_page") or config["landing_url"]),
        source_note=str(config["note"]),
        region=str(config.get("region", "ca")),
        source_name=str(config.get("source_name", "Tree Inventory")),
        source_department=config.get("source_department"),
        ownership_raw=str(config.get("ownership_raw", "Not published in public inventory")),
        boundary_layer=config.get("boundary_layer"),
        clip_to_boundary=bool(config.get("clip_to_boundary", False)),
    )


def fetch_south_san_francisco() -> dict[str, Any]:
    _boundary_info = fetch_json(SOUTH_SF_BOUNDARY_LAYER, {"f": "pjson"})
    summary_payload, rows = fetch_treekeeper_rows(
        SOUTH_SF_SEARCH_ENDPOINT,
        SOUTH_SF_GRIDS_ENDPOINT,
        uid="pinkhunter-south-san-francisco",
        fac_id=1,
    )
    zip_index = fetch_us_city_zip_index("South San Francisco")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        lon = row.get("LONGITUDE")
        lat = row.get("LATITUDE")
        if lon is None or lat is None:
            geometry_raw = row.get("SITE_GEOMETRY")
            if isinstance(geometry_raw, str) and geometry_raw.strip():
                try:
                    geometry_payload = json.loads(geometry_raw)
                    coordinates = geometry_payload.get("coordinates") or []
                    lon, lat = coordinates[0], coordinates[1]
                except Exception:
                    lon = None
                    lat = None
        if lon is None or lat is None:
            continue

        scientific_raw, common_name = parse_species_text(row.get("SITE_ATTR1"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = clean_display_name(row.get("SITE_ATTR23")) or "City of South San Francisco"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"south-san-francisco-{row.get('SITE_ID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "South San Francisco",
                "source_dataset": "TreeKeeper Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "South San Francisco",
                    "source_dataset": "TreeKeeper Inventory",
                    "source_department": "City of South San Francisco",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "South San Francisco",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "TreeKeeper Inventory",
            "city": "South San Francisco",
            "endpoint": SOUTH_SF_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": len(rows),
            "records_included": len(output_features),
            "note": "Integrated from the official public TreeKeeper inventory linked from the city's Trees page.",
        },
    }


def fetch_salinas() -> dict[str, Any]:
    dataset_info = fetch_json(SALINAS_DATASET)
    rows = fetch_ods_export_rows(SALINAS_DATASET, where="active=1")
    zip_index = fetch_us_city_zip_index("Salinas")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = (
        dataset_info.get("metas", {}).get("default", {}).get("modified")
        or dataset_info.get("metas", {}).get("data_processed")
        or ""
    )

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        point = (row.get("geo_point_2d") or {}) if isinstance(row.get("geo_point_2d"), dict) else {}
        lon = point.get("lon")
        lat = point.get("lat")
        if lon is None or lat is None:
            continue

        scientific_raw = (row.get("spp") or "").strip()
        common_name = None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Salinas"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"salinas-{row.get('objectid')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Salinas",
                "source_dataset": "Tree Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Salinas",
                    "source_dataset": "Tree Inventory",
                    "source_department": "City of Salinas",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Salinas",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventory",
            "city": "Salinas",
            "endpoint": "https://cityofsalinas.opendatasoft.com/explore/dataset/tree-inventory/",
            "last_edit_at": last_edit_at,
            "records_fetched": len(rows),
            "records_included": len(output_features),
            "note": "Integrated from the official City of Salinas OpenDataSoft tree inventory dataset.",
        },
    }


def fetch_pittsburgh() -> dict[str, Any]:
    summary_payload, rows = fetch_treekeeper_rows(
        PITTSBURGH_SEARCH_ENDPOINT,
        PITTSBURGH_GRIDS_ENDPOINT,
        uid="pinkhunter-pittsburgh",
        fac_id=1,
    )
    zip_index = fetch_us_city_zip_index("Pittsburgh")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        lon = row.get("LONGITUDE")
        lat = row.get("LATITUDE")
        if lon is None or lat is None:
            geometry_raw = row.get("SITE_GEOMETRY")
            if isinstance(geometry_raw, str) and geometry_raw.strip():
                try:
                    geometry_payload = json.loads(geometry_raw)
                    coordinates = geometry_payload.get("coordinates") or []
                    lon, lat = coordinates[0], coordinates[1]
                except Exception:
                    lon = None
                    lat = None
        if lon is None or lat is None:
            continue

        scientific_raw, common_name = parse_species_text(row.get("SITE_ATTR6"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Pittsburgh"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"pittsburgh-{row.get('SITE_ID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Pittsburgh",
                "source_dataset": "TreeKeeper Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Pittsburgh",
                    "source_dataset": "TreeKeeper Inventory",
                    "source_department": "City of Pittsburgh",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Pittsburgh",
        "region": "pa",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "TreeKeeper Inventory",
            "city": "Pittsburgh",
            "endpoint": PITTSBURGH_BASE,
            "last_edit_at": "",
            "records_fetched": int(summary_payload.get("siteCount") or len(rows)),
            "records_included": len(output_features),
            "note": "Integrated from the official public Pittsburgh TreeKeeper inventory domain.",
        },
    }


def fetch_new_york_city() -> dict[str, Any]:
    metadata = fetch_json(NYC_METADATA)
    rows = fetch_soda_rows(
        NYC_DATASET,
        where="status='Alive' AND (lower(spc_latin) like 'prunus%' OR lower(spc_latin) like 'malus%' OR lower(spc_latin) like 'magnolia%')",
        order="tree_id",
    )
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch(metadata.get("rowsUpdatedAt") or metadata.get("viewLastModified"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        try:
            lon = float(row.get("longitude"))
            lat = float(row.get("latitude"))
        except (TypeError, ValueError):
            continue

        common_name = clean_common_name(row.get("spc_common"))
        scientific_raw = format_scientific_display_name(row.get("spc_latin"), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "New York City Department of Parks & Recreation"
        zip_code = (row.get("zipcode") or "").strip() or None
        row_id = f"new-york-city-{row.get('tree_id')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "New York City",
                "source_dataset": "2015 Street Tree Census - Tree Data",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "New York City",
                    "source_dataset": "2015 Street Tree Census - Tree Data",
                    "source_department": "Department of Parks & Recreation (DPR)",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "New York City",
        "region": "ny",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "2015 Street Tree Census - Tree Data",
            "city": "New York City",
            "endpoint": NYC_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": fetch_soda_count(NYC_DATASET, where="status='Alive'"),
            "records_included": len(output_features),
            "note": "Integrated from the official NYC Open Data street tree census dataset published by NYC Parks.",
        },
    }


def fetch_philadelphia() -> dict[str, Any]:
    layer_info = fetch_json(PHILADELPHIA_LAYER, {"f": "pjson"})
    rows = fetch_all_features(
        PHILADELPHIA_LAYER,
        "tree_name LIKE 'PRUNUS%' OR tree_name LIKE 'MALUS%' OR tree_name LIKE 'MAGNOLIA%'",
        ["objectid", "tree_name", "year"],
        "objectid",
    )
    total_payload = fetch_json(
        f"{PHILADELPHIA_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    zip_index = fetch_us_city_zip_index("Philadelphia")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in rows:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon = geom.get("x")
        lat = geom.get("y")
        if lon is None or lat is None:
            continue
        scientific_raw, common_name = parse_dash_species(attrs.get("tree_name"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "Philadelphia Parks & Recreation"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"philadelphia-{attrs.get('objectid')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Philadelphia",
                "source_dataset": "PPR Tree Inventory 2025",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Philadelphia",
                    "source_dataset": "PPR Tree Inventory 2025",
                    "source_department": "Philadelphia Parks & Recreation",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Philadelphia",
        "region": "pa",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "PPR Tree Inventory 2025",
            "city": "Philadelphia",
            "endpoint": PHILADELPHIA_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(rows)),
            "records_included": len(output_features),
            "note": "Integrated from the official Philadelphia Parks & Recreation tree inventory layer.",
        },
    }


def fetch_cambridge() -> dict[str, Any]:
    reader, _prj_text = load_zipped_shapefile(CAMBRIDGE_STREET_TREES_ZIP)
    total_records = len(reader)
    point_rows = load_zipped_point_shapefile_rows(CAMBRIDGE_STREET_TREES_ZIP)
    zip_index = fetch_us_city_zip_index("Cambridge")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in point_rows:
        attrs = row.get("attributes", {})
        geom = row.get("geometry", {})
        if (attrs.get("SiteType") or "").strip() != "Tree":
            continue

        common_name = clean_common_name(attrs.get("CommonName"))
        scientific_raw = format_scientific_display_name(attrs.get("Scientific"), common_name)
        if not scientific_raw:
            scientific_raw = format_scientific_display_name(attrs.get("Genus"), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("Cultivar"))
        if not subtype_name and cultivar:
            subtype_name = cultivar
        ownership_raw = clean_display_name(attrs.get("Ownership")) or "City of Cambridge"
        lon = geom.get("x")
        lat = geom.get("y")
        if lon is None or lat is None:
            continue
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"cambridge-{attrs.get('TreeID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Cambridge",
                "source_dataset": "Street Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Cambridge",
                    "source_dataset": "Street Trees",
                    "source_department": "City of Cambridge GIS",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Cambridge",
        "region": "ma",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Street Trees",
            "city": "Cambridge",
            "endpoint": CAMBRIDGE_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": total_records,
            "records_included": len(output_features),
            "note": "Integrated from the official City of Cambridge street-tree shapefile download.",
        },
    }


def fetch_ottawa() -> dict[str, Any]:
    layer_info = fetch_json(OTTAWA_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{OTTAWA_TREES_LAYER}/query",
        {"where": OTTAWA_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        OTTAWA_TREES_LAYER,
        OTTAWA_BLOSSOM_WHERE,
        ["OBJECTID", "TREEID", "SPECIES", "OWNERSHIP", "STATUS", "PROGRAM", "TREATMENT"],
        "OBJECTID",
    )
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue
        common_name = clean_common_name(attrs.get("SPECIES"))
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = clean_display_name(attrs.get("OWNERSHIP")) or "City of Ottawa"
        row_id = f"ottawa-{attrs.get('TREEID') or attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Ottawa",
                "source_dataset": "Tree Inventory / Inventaire des arbres",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": None,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Ottawa",
                    "source_dataset": "Tree Inventory / Inventaire des arbres",
                    "source_department": "City of Ottawa",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Ottawa",
        "region": "on",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventory / Inventaire des arbres",
            "city": "Ottawa",
            "endpoint": OTTAWA_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of Ottawa Tree Inventory ArcGIS layer and official city boundary.",
        },
    }


def fetch_toronto() -> dict[str, Any]:
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    total_records = 0
    for row in iter_remote_csv_rows(TORONTO_STREET_TREE_ALT_CSV):
        total_records += 1
        lon, lat = parse_point_geometry_text(row.get("geometry"))
        if lon is None or lat is None:
            continue
        common_name = clean_common_name(row.get("COMMON_NAME"))
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Toronto"
        row_id = f"toronto-{row.get('_id') or row.get('OBJECTID') or total_records}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Toronto",
                "source_dataset": "Street Tree Data",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": None,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Toronto",
                    "source_dataset": "Street Tree Data",
                    "source_department": "City of Toronto Urban Forestry",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Toronto",
        "region": "on",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Street Tree Data",
            "city": "Toronto",
            "endpoint": TORONTO_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": total_records,
            "records_included": len(output_features),
            "note": "Integrated from the official City of Toronto Street Tree Data CSV and official municipal boundary.",
        },
    }


def fetch_montreal() -> dict[str, Any]:
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    total_records = 0
    for row in iter_remote_csv_rows(MONTREAL_TREES_CSV):
        total_records += 1
        lon_raw = row.get("Longitude")
        lat_raw = row.get("Latitude")
        if lon_raw in (None, "") or lat_raw in (None, ""):
            continue
        lon = float(lon_raw)
        lat = float(lat_raw)
        common_name = clean_common_name(row.get("Essence_ang") or row.get("Essence_fr"))
        scientific_raw = format_scientific_display_name(row.get("Essence_latin"), common_name)
        if not scientific_raw:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "Ville de Montréal"
        row_id = f"montreal-{total_records}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Montreal",
                "source_dataset": "Arbres publics sur le territoire de la Ville",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": None,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Montreal",
                    "source_dataset": "Arbres publics sur le territoire de la Ville",
                    "source_department": "Ville de Montréal",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Montreal",
        "region": "qc",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Arbres publics sur le territoire de la Ville",
            "city": "Montreal",
            "endpoint": MONTREAL_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": total_records,
            "records_included": len(output_features),
            "note": "Integrated from the official Ville de Montréal public-trees consolidated CSV and arrondissement-derived city boundary.",
        },
    }


def fetch_new_westminster() -> dict[str, Any]:
    layer_info = fetch_json(NEW_WESTMINSTER_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{NEW_WESTMINSTER_TREES_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        NEW_WESTMINSTER_TREES_LAYER,
        "1=1",
        ["objectid", "ADDRESS", "MAINTBY", "OWNEDBY", "SPECIES", "CULTIVAR", "GENUS", "FULL_NAME"],
        "objectid",
    )
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        scientific_raw = format_scientific_display_name(attrs.get("FULL_NAME"))
        if not scientific_raw:
            genus = clean_display_name(attrs.get("GENUS")) or ""
            species = clean_display_name(attrs.get("SPECIES")) or ""
            scientific_raw = format_scientific_display_name(" ".join(part for part in [genus, species] if part))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, None, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("CULTIVAR"))
        if not subtype_name and cultivar:
            subtype_name = cultivar
        ownership_raw = clean_display_name(attrs.get("OWNEDBY")) or clean_display_name(attrs.get("MAINTBY")) or "City of New Westminster"
        row_id = f"new-westminster-{attrs.get('objectid')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "New Westminster",
                "source_dataset": "Tree Inventory (Active Trees)",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": "",
                "subtype_name": subtype_name or "",
                "zip_code": "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": None,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "New Westminster",
                    "source_dataset": "Tree Inventory (Active Trees)",
                    "source_department": "City of New Westminster",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "New Westminster",
        "region": "bc",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventory (Active Trees)",
            "city": "New Westminster",
            "endpoint": NEW_WESTMINSTER_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of New Westminster Tree Inventory ArcGIS layer and official Metro Vancouver administrative boundary.",
        },
    }


def fetch_las_vegas() -> dict[str, Any]:
    layer_info = fetch_json(LAS_VEGAS_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{LAS_VEGAS_TREES_LAYER}/query",
        {"where": LAS_VEGAS_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        LAS_VEGAS_TREES_LAYER,
        LAS_VEGAS_BLOSSOM_WHERE,
        ["FID", "UNIQUEID", "SPP_COM", "SPP_BOT", "FAC_NAME", "LOCATION", "STATUS", "LATITUDE", "LONGITUDE"],
        "FID",
    )
    zip_index = fetch_us_city_zip_index("Las Vegas")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            try:
                lon = float(attrs.get("LONGITUDE"))
                lat = float(attrs.get("LATITUDE"))
            except (TypeError, ValueError):
                lon = None
                lat = None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("SPP_COM"))
        scientific_raw = format_scientific_display_name(attrs.get("SPP_BOT"), common_name)
        if not scientific_raw:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Las Vegas"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"las-vegas-{attrs.get('UNIQUEID') or attrs.get('FID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Las Vegas",
                "source_dataset": "CLV Tree Sites",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Las Vegas",
                    "source_dataset": "CLV Tree Sites",
                    "source_department": "City of Las Vegas",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Las Vegas",
        "region": "nv",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "CLV Tree Sites",
            "city": "Las Vegas",
            "endpoint": LAS_VEGAS_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of Las Vegas CLV_Tree_Sites ArcGIS layer.",
        },
    }


def fetch_salt_lake_city() -> dict[str, Any]:
    layer_info = fetch_json(SALT_LAKE_CITY_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{SALT_LAKE_CITY_TREES_LAYER}/query",
        {"where": SALT_LAKE_CITY_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        SALT_LAKE_CITY_TREES_LAYER,
        SALT_LAKE_CITY_BLOSSOM_WHERE,
        ["FID", "SPP", "DBH", "ADDRESS", "STREET", "SIDE", "SITE", "Vacant"],
        "FID",
    )
    zip_index = fetch_us_city_zip_index("Salt Lake City")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        scientific_raw = format_scientific_display_name(attrs.get("SPP"))
        common_name = None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "Salt Lake City Public Lands"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"salt-lake-city-{attrs.get('FID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Salt Lake City",
                "source_dataset": "Urban Forestry Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Salt Lake City",
                    "source_dataset": "Urban Forestry Inventory",
                    "source_department": "Salt Lake City Public Lands Department",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Salt Lake City",
        "region": "ut",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Urban Forestry Inventory",
            "city": "Salt Lake City",
            "endpoint": SALT_LAKE_CITY_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official Salt Lake City Urban Forestry Inventory ArcGIS layer.",
        },
    }


def fetch_san_diego() -> dict[str, Any]:
    layer_info = fetch_json(SAN_DIEGO_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{SAN_DIEGO_TREES_LAYER}/query",
        {"where": SAN_DIEGO_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        SAN_DIEGO_TREES_LAYER,
        SAN_DIEGO_BLOSSOM_WHERE,
        ["OBJECTID", "COMMON_NAME", "SPECIES_NAME", "LOCATION", "NBHD"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("San Diego")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("COMMON_NAME") or attrs.get("SPECIES_NAME"))
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of San Diego"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"san-diego-{attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "San Diego",
                "source_dataset": "Trees (Street Trees)",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "San Diego",
                    "source_dataset": "Trees (Street Trees)",
                    "source_department": "City of San Diego",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "San Diego",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Trees (Street Trees)",
            "city": "San Diego",
            "endpoint": SAN_DIEGO_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of San Diego street-trees ArcGIS layer with server-side blossom filtering.",
        },
    }


def fetch_los_angeles() -> dict[str, Any]:
    rows = fetch_los_angeles_filtered_rows()
    zip_index = fetch_us_city_zip_index("Los Angeles")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        lon_raw = row.get("LONGITUDE")
        lat_raw = row.get("LATITUDE")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            geometry_raw = row.get("SITE_GEOMETRY")
            if isinstance(geometry_raw, str) and geometry_raw.strip():
                try:
                    geometry_payload = json.loads(geometry_raw)
                    coordinates = geometry_payload.get("coordinates") or []
                    lon = float(coordinates[0])
                    lat = float(coordinates[1])
                except Exception:
                    lon = None
                    lat = None
        if lon is None or lat is None:
            continue

        scientific_raw, common_name = parse_species_text(row.get("SITE_ATTR1"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Los Angeles"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"los-angeles-{row.get('SITE_ID') or row.get('SITE_ATTR40')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Los Angeles",
                "source_dataset": "TreeKeeper Street Sites",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Los Angeles",
                    "source_dataset": "TreeKeeper Street Sites",
                    "source_department": "StreetsLA",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "Los Angeles",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "TreeKeeper Street Sites",
            "city": "Los Angeles",
            "endpoint": LOS_ANGELES_STREETSLA_PAGE,
            "last_edit_at": "",
            "records_fetched": len(rows),
            "records_included": len(output_features),
            "note": "Integrated from the official StreetsLA public TreeKeeper street-tree inventory using server-side blossom filtering.",
        },
    }


def fetch_irvine() -> dict[str, Any]:
    layer_info = fetch_json(IRVINE_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{IRVINE_TREES_LAYER}/query",
        {"where": IRVINE_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        IRVINE_TREES_LAYER,
        IRVINE_BLOSSOM_WHERE,
        ["OBJECTID", "TRG_COMMON", "CITYMAINTAINED"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("Irvine")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("TRG_COMMON"))
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Irvine" if str(attrs.get("CITYMAINTAINED") or "").upper() == "TRUE" else "Private / non-city maintained"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"irvine-{attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Irvine",
                "source_dataset": "City Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Irvine",
                    "source_dataset": "City Trees",
                    "source_department": "City of Irvine",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Irvine",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "City Trees",
            "city": "Irvine",
            "endpoint": IRVINE_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of Irvine City Trees layer and official city boundary.",
        },
    }


def fetch_mountain_view() -> dict[str, Any]:
    layer_info = fetch_json(MOUNTAIN_VIEW_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{MOUNTAIN_VIEW_TREES_LAYER}/query",
        {"where": MOUNTAIN_VIEW_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        MOUNTAIN_VIEW_TREES_LAYER,
        MOUNTAIN_VIEW_BLOSSOM_WHERE,
        ["OBJECTID", "BOTNAMEDESCRPT", "SCINAME", "HERITAGE", "ADDRESS", "UNITID"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("Mountain View")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("BOTNAMEDESCRPT"))
        scientific_raw = format_scientific_display_name(attrs.get("SCINAME"), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Mountain View"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"mountain-view-{attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Mountain View",
                "source_dataset": "Heritage Trees / Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Mountain View",
                    "source_dataset": "Heritage Trees / Trees",
                    "source_department": "City of Mountain View",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Mountain View",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Trees",
            "city": "Mountain View",
            "endpoint": MOUNTAIN_VIEW_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of Mountain View Trees ArcGIS layer and official city boundary.",
        },
    }


def fetch_sacramento() -> dict[str, Any]:
    layer_info = fetch_json(SACRAMENTO_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{SACRAMENTO_TREES_LAYER}/query",
        {"where": SACRAMENTO_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        SACRAMENTO_TREES_LAYER,
        SACRAMENTO_BLOSSOM_WHERE,
        ["ASSET_ID", "SPECIES", "BOTANICAL", "CULTIVAR"],
        "ASSET_ID",
    )
    zip_index = fetch_us_city_zip_index("Sacramento")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("SPECIES"))
        scientific_raw = format_scientific_display_name(attrs.get("BOTANICAL"), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        cultivar = clean_display_name(attrs.get("CULTIVAR"))
        if not subtype_name and cultivar:
            subtype_name = cultivar
        ownership_raw = "City of Sacramento"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"sacramento-{attrs.get('ASSET_ID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Sacramento",
                "source_dataset": "City Maintained Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Sacramento",
                    "source_dataset": "City Maintained Trees",
                    "source_department": "City of Sacramento",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Sacramento",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "City Maintained Trees",
            "city": "Sacramento",
            "endpoint": SACRAMENTO_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of Sacramento City Maintained Trees ArcGIS layer and official jurisdiction boundary.",
        },
    }


def fetch_west_sacramento() -> dict[str, Any]:
    layer_info = fetch_json(WEST_SACRAMENTO_TREES_LAYER, {"f": "pjson"})
    where = (
        "UPPER(BotanicalN) LIKE 'PRUNUS%' OR "
        "UPPER(BotanicalN) LIKE 'MALUS%' OR "
        "UPPER(BotanicalN) LIKE 'MAGNOLIA%' OR "
        "UPPER(CommonName) LIKE '%CHERRY%' OR "
        "UPPER(CommonName) LIKE '%PLUM%' OR "
        "UPPER(CommonName) LIKE '%PEACH%' OR "
        "UPPER(CommonName) LIKE '%MAGNOLIA%' OR "
        "UPPER(CommonName) LIKE '%CRABAPPLE%' OR "
        "UPPER(CommonName) LIKE '%APPLE%'"
    )
    total_payload = fetch_json(
        f"{WEST_SACRAMENTO_TREES_LAYER}/query",
        {"where": where, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        WEST_SACRAMENTO_TREES_LAYER,
        where,
        ["OBJECTID", "CommonName", "BotanicalN", "Latitude", "Longitude"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("West Sacramento")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        if lon_raw is None or lat_raw is None:
            lon_raw = attrs.get("Longitude")
            lat_raw = attrs.get("Latitude")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("CommonName"))
        scientific_raw = format_scientific_display_name(attrs.get("BotanicalN"), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of West Sacramento"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"west-sacramento-{attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "West Sacramento",
                "source_dataset": "Tree Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "West Sacramento",
                    "source_dataset": "Tree Inventory",
                    "source_department": "City of West Sacramento",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "West Sacramento",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventory",
            "city": "West Sacramento",
            "endpoint": WEST_SACRAMENTO_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of West Sacramento Tree Inventory ArcGIS layer and official jurisdiction boundary.",
        },
    }


def fetch_sunnyvale() -> dict[str, Any]:
    layer_info = fetch_json(SUNNYVALE_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{SUNNYVALE_TREES_LAYER}/query",
        {"where": SUNNYVALE_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        SUNNYVALE_TREES_LAYER,
        SUNNYVALE_BLOSSOM_WHERE,
        ["FID", "City", "CommonName", "Scientific", "Address", "SiteName", "SiteID"],
        "FID",
    )
    zip_index = fetch_us_city_zip_index("Sunnyvale")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("CommonName"))
        scientific_raw = format_scientific_display_name(attrs.get("Scientific"), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "Public / Santa Clara County tree inventory"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"sunnyvale-{attrs.get('FID') or attrs.get('SiteID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Sunnyvale",
                "source_dataset": "Tree Inventories in Santa Clara County",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Sunnyvale",
                    "source_dataset": "Tree Inventories in Santa Clara County",
                    "source_department": "County of Santa Clara / Santa Clara Valley Urban Forestry Alliance",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Sunnyvale",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventories in Santa Clara County",
            "city": "Sunnyvale",
            "endpoint": SUNNYVALE_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official Santa Clara County public tree inventory service using the city = Sunnyvale subset and the official jurisdiction boundary.",
        },
    }


def fetch_santa_clara_county_city(city: str) -> dict[str, Any]:
    layer_info = fetch_json(SUNNYVALE_TREES_LAYER, {"f": "pjson"})
    escaped_city = city.replace("'", "''")
    where = (
        f"City = '{escaped_city}' AND ("
        "UPPER(Scientific) LIKE 'PRUNUS%' OR "
        "UPPER(Scientific) LIKE 'MALUS%' OR "
        "UPPER(Scientific) LIKE 'MAGNOLIA%' OR "
        "UPPER(CommonName) LIKE '%CHERRY%' OR "
        "UPPER(CommonName) LIKE '%PLUM%' OR "
        "UPPER(CommonName) LIKE '%PEACH%' OR "
        "UPPER(CommonName) LIKE '%MAGNOLIA%' OR "
        "UPPER(CommonName) LIKE '%CRABAPPLE%' OR "
        "UPPER(CommonName) LIKE '%APPLE%'"
        ")"
    )
    total_payload = fetch_json(
        f"{SUNNYVALE_TREES_LAYER}/query",
        {"where": where, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        SUNNYVALE_TREES_LAYER,
        where,
        ["FID", "City", "CommonName", "Scientific", "Address", "SiteName", "SiteID"],
        "FID",
    )
    zip_index = fetch_us_city_zip_index(city)
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("CommonName"))
        scientific_raw = format_scientific_display_name(attrs.get("Scientific"), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "Public / Santa Clara County tree inventory"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"{slugify_token(city)}-{attrs.get('FID') or attrs.get('SiteID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": city,
                "source_dataset": "Tree Inventories in Santa Clara County",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": city,
                    "source_dataset": "Tree Inventories in Santa Clara County",
                    "source_department": "County of Santa Clara / Santa Clara Valley Urban Forestry Alliance",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": city,
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Tree Inventories in Santa Clara County",
            "city": city,
            "endpoint": SANTA_CLARA_COUNTY_TREES_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": f"Integrated from the official Santa Clara County public tree inventory service using the City = {city} subset and official jurisdiction boundary.",
        },
    }


def fetch_los_gatos() -> dict[str, Any]:
    return fetch_santa_clara_county_city("Los Gatos")


def fetch_morgan_hill() -> dict[str, Any]:
    return fetch_santa_clara_county_city("Morgan Hill")


def fetch_gilroy() -> dict[str, Any]:
    return fetch_santa_clara_county_city("Gilroy")


def fetch_saratoga() -> dict[str, Any]:
    return fetch_santa_clara_county_city("Saratoga")


def fetch_pasadena() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Pasadena",
        region="ca",
        layer_url=PASADENA_TREES_LAYER,
        dataset_page=PASADENA_DATASET_PAGE,
        where=PASADENA_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Common_Name", "Genus", "Species", "Status_Text"],
        object_id_field="OBJECTID",
        source_name="Street ROW Trees",
        source_department="City of Pasadena",
        ownership_raw="City of Pasadena",
        note="Integrated from the official City of Pasadena Street ROW Trees layer and official jurisdiction boundary.",
        common_field="Common_Name",
        genus_field="Genus",
        species_field="Species",
    )


def fetch_beverly_hills() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Beverly Hills",
        region="ca",
        layer_url=BEVERLY_HILLS_TREES_LAYER,
        dataset_page=BEVERLY_HILLS_DATASET_PAGE,
        where=BOTANICAL_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "CommonName", "BotanicalName", "Latitude", "Longitude"],
        object_id_field="OBJECTID",
        source_name="Trees of Beverly Hills",
        source_department="City of Beverly Hills",
        ownership_raw="City of Beverly Hills",
        note="Integrated from the official City of Beverly Hills public tree inventory and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
        lon_field="Longitude",
        lat_field="Latitude",
    )


def fetch_el_segundo() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="El Segundo",
        region="ca",
        layer_url=EL_SEGUNDO_TREES_LAYER,
        dataset_page=EL_SEGUNDO_DATASET_PAGE,
        where=BOTANICAL_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "CommonName", "BotanicalName", "Latitude", "Longitude"],
        object_id_field="OBJECTID",
        source_name="Tree Inventory Public",
        source_department="City of El Segundo",
        ownership_raw="City of El Segundo",
        note="Integrated from the City of El Segundo public tree inventory feature layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
        lon_field="Longitude",
        lat_field="Latitude",
    )


def fetch_bell() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Bell",
        region="ca",
        layer_url=BELL_TREES_LAYER,
        dataset_page=BELL_DATASET_PAGE,
        where=SPECIES_NAME_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName", "Latitude", "Longitude"],
        object_id_field="OBJECTID",
        source_name="City of Bell Tree Inventory Benefits",
        source_department="City of Bell",
        ownership_raw="City of Bell",
        note="Integrated from the City of Bell public tree inventory benefits layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
        scientific_field="Species_Name",
        lon_field="Longitude",
        lat_field="Latitude",
    )


def fetch_san_fernando() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="San Fernando",
        region="ca",
        layer_url=SAN_FERNANDO_TREES_LAYER,
        dataset_page=SAN_FERNANDO_DATASET_PAGE,
        where=SAN_FERNANDO_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "NAME", "Address", "Zipcode"],
        object_id_field="OBJECTID",
        source_name="San Fernando Public Trees",
        source_department="City of San Fernando",
        ownership_raw="City of San Fernando",
        note="Integrated from the City of San Fernando public tree inventory layer and official jurisdiction boundary.",
        scientific_field="NAME",
        zip_field="Zipcode",
    )


def fetch_azusa() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Azusa",
        region="ca",
        layer_url=AZUSA_TREES_LAYER,
        dataset_page=AZUSA_DATASET_PAGE,
        where=SPECIES_NAME_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName", "Latitude", "Longitude"],
        object_id_field="OBJECTID",
        source_name="City of Azusa Tree Inventory Benefits",
        source_department="City of Azusa",
        ownership_raw="City of Azusa",
        note="Integrated from the City of Azusa public tree inventory benefits layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
        scientific_field="Species_Name",
        lon_field="Longitude",
        lat_field="Latitude",
    )


def fetch_fullerton() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Fullerton",
        region="ca",
        layer_url=FULLERTON_TREES_LAYER,
        dataset_page=FULLERTON_DATASET_PAGE,
        where=SPECIES_NAME_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="Fullerton Tree Benefits",
        source_department="City of Fullerton",
        ownership_raw="City of Fullerton",
        note="Integrated from the City of Fullerton public tree inventory layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
        scientific_field="Species_Name",
    )


def fetch_anaheim() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Anaheim",
        region="ca",
        layer_url=ANAHEIM_TREES_LAYER,
        dataset_page=ANAHEIM_DATASET_PAGE,
        where=ANAHEIM_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "COMMONNAME", "BOTANICALN"],
        object_id_field="OBJECTID",
        source_name="City of Anaheim Public Works Tree Sites",
        source_department="City of Anaheim",
        ownership_raw="City of Anaheim",
        note="Integrated from the City of Anaheim public works tree sites layer and official jurisdiction boundary.",
        common_field="COMMONNAME",
        botanical_field="BOTANICALN",
        scientific_field="Species_Name",
    )


def fetch_houston() -> dict[str, Any]:
    layer_info = fetch_json(HOUSTON_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{HOUSTON_TREES_LAYER}/query",
        {"where": HOUSTON_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        HOUSTON_TREES_LAYER,
        HOUSTON_BLOSSOM_WHERE,
        ["OBJECTID", "SPECIES", "ADDRESS", "STATUS", "LOCATION"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("Houston")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("SPECIES"))
        scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City of Houston"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"houston-{attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Houston",
                "source_dataset": "COH Urban Forestry Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Houston",
                    "source_dataset": "COH Urban Forestry Trees",
                    "source_department": "City of Houston",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Houston",
        "region": "tx",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "COH Urban Forestry Trees",
            "city": "Houston",
            "endpoint": HOUSTON_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City of Houston public Urban Forestry tree inventory web map and official jurisdiction boundary.",
        },
    }


def fetch_denver() -> dict[str, Any]:
    layer_info = fetch_json(DENVER_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{DENVER_TREES_LAYER}/query",
        {"where": DENVER_BLOSSOM_WHERE, "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_all_features(
        DENVER_TREES_LAYER,
        DENVER_BLOSSOM_WHERE,
        ["OBJECTID", "SPECIES_COMMON", "SPECIES_BOTANIC", "LOCATION_NAME", "ADDRESS", "X_LONG", "Y_LAT"],
        "OBJECTID",
    )
    zip_index = fetch_us_city_zip_index("Denver")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for feature in features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        lon_raw = geom.get("x")
        lat_raw = geom.get("y")
        if lon_raw is None or lat_raw is None:
            lon_raw = attrs.get("X_LONG")
            lat_raw = attrs.get("Y_LAT")
        lon = float(lon_raw) if lon_raw is not None else None
        lat = float(lat_raw) if lat_raw is not None else None
        if lon is None or lat is None:
            continue

        common_name = clean_common_name(attrs.get("SPECIES_COMMON"))
        scientific_raw = format_scientific_display_name(attrs.get("SPECIES_BOTANIC"), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        ownership_raw = "City and County of Denver"
        zip_code = assign_zip_code(lon, lat, zip_index)
        row_id = f"denver-{attrs.get('OBJECTID')}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "Denver",
                "source_dataset": "Public Tree Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Denver",
                    "source_dataset": "Public Tree Inventory",
                    "source_department": "City and County of Denver Department of Parks and Recreation",
                    "source_last_edit_at": last_edit_at,
                },
            }
        )

    return {
        "city": "Denver",
        "region": "co",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "Public Tree Inventory",
            "city": "Denver",
            "endpoint": DENVER_DATASET_PAGE,
            "last_edit_at": last_edit_at,
            "records_fetched": int(total_payload.get("count") or len(features)),
            "records_included": len(output_features),
            "note": "Integrated from the official City and County of Denver public tree inventory and official jurisdiction boundary.",
        },
    }


def fetch_pomona() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Pomona",
        region="ca",
        layer_url=POMONA_TREES_LAYER,
        dataset_page=POMONA_DATASET_PAGE,
        where=SPECIES_NAME_COMMON_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="CityOfPomona i-Tree Benefits Canopy Cover",
        source_department="City of Pomona",
        ownership_raw="City of Pomona",
        note="Integrated from the official City of Pomona public i-Tree tree inventory layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_santa_clarita() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Santa Clarita",
        region="ca",
        layer_url=SANTA_CLARITA_TREES_LAYER,
        dataset_page=SANTA_CLARITA_DATASET_PAGE,
        where=SPECIES_NAME_COMMON_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="City of Santa Clarita i-Tree Benefits Canopy Cover",
        source_department="City of Santa Clarita",
        ownership_raw="City of Santa Clarita",
        note="Integrated from the official City of Santa Clarita public i-Tree inventory layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_monterey_park() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Monterey Park",
        region="ca",
        layer_url=MONTEREY_PARK_TREES_LAYER,
        dataset_page=MONTEREY_PARK_DATASET_PAGE,
        where=SPECIES_NAME_COMMON_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="Monterey Park i-Tree Benefits Summary",
        source_department="City of Monterey Park",
        ownership_raw="City of Monterey Park",
        note="Integrated from the official City of Monterey Park public i-Tree inventory layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_rancho_cucamonga() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Rancho Cucamonga",
        region="ca",
        layer_url=RANCHO_CUCAMONGA_TREES_LAYER,
        dataset_page=RANCHO_CUCAMONGA_DATASET_PAGE,
        where=SPECIES_NAME_COMMON_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName", "iTree_Species"],
        object_id_field="OBJECTID",
        source_name="Rancho Cucamonga Tree Benefits",
        source_department="City of Rancho Cucamonga",
        ownership_raw="City of Rancho Cucamonga",
        note="Integrated from the official City of Rancho Cucamonga public tree benefits inventory layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_maywood() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Maywood",
        region="ca",
        layer_url=MAYWOOD_TREES_LAYER,
        dataset_page=MAYWOOD_DATASET_PAGE,
        where=SPECIES_NAME_COMMON_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="Maywood i-Tree Inventory",
        source_department="City of Maywood",
        ownership_raw="City of Maywood",
        note="Integrated from the official City of Maywood public i-Tree inventory layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_costa_mesa() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Costa Mesa",
        region="ca",
        layer_url=COSTA_MESA_TREES_LAYER,
        dataset_page=COSTA_MESA_DATASET_PAGE,
        where=SPECIES_NAME_COMMON_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="Costa Mesa Tree Benefits",
        source_department="City of Costa Mesa",
        ownership_raw="City of Costa Mesa",
        note="Integrated from the official City of Costa Mesa public tree benefits inventory layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_riverside() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Riverside",
        region="ca",
        layer_url=RIVERSIDE_TREES_LAYER,
        dataset_page=RIVERSIDE_DATASET_PAGE,
        where=SPECIES_NAME_COMMON_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="CityOfRiverside i-Tree Benefits",
        source_department="City of Riverside",
        ownership_raw="City of Riverside",
        note="Integrated from the official City of Riverside public i-Tree inventory layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_la_canada_flintridge() -> dict[str, Any]:
    blossom_where = (
        "UPPER(T_La_Canada_Flintridge_Inv_0_13) LIKE 'PRUNUS%' OR "
        "UPPER(T_La_Canada_Flintridge_Inv_0_13) LIKE 'MALUS%' OR "
        "UPPER(T_La_Canada_Flintridge_Inv_0_13) LIKE 'MAGNOLIA%' OR "
        "UPPER(T_La_Canada_Flintridge_Inv_0_12) LIKE '%CHERRY%' OR "
        "UPPER(T_La_Canada_Flintridge_Inv_0_12) LIKE '%PLUM%' OR "
        "UPPER(T_La_Canada_Flintridge_Inv_0_12) LIKE '%PEACH%' OR "
        "UPPER(T_La_Canada_Flintridge_Inv_0_12) LIKE '%MAGNOLIA%' OR "
        "UPPER(T_La_Canada_Flintridge_Inv_0_12) LIKE '%CRABAPPLE%' OR "
        "UPPER(T_La_Canada_Flintridge_Inv_0_12) LIKE '%APPLE%'"
    )
    return fetch_arcgis_inventory_city(
        city="La Canada Flintridge",
        region="ca",
        layer_url=LA_CANADA_FLINTRIDGE_TREES_LAYER,
        dataset_page=LA_CANADA_FLINTRIDGE_DATASET_PAGE,
        where=blossom_where,
        out_fields=["OBJECTID", "T_La_Canada_Flintridge_Inv_0_12", "T_La_Canada_Flintridge_Inv_0_13"],
        object_id_field="OBJECTID",
        source_name="La Canada Flintridge Homepage Inventory",
        source_department="City of La Canada Flintridge",
        ownership_raw="City of La Canada Flintridge",
        note="Integrated from the official City of La Canada Flintridge public tree inventory layer and official jurisdiction boundary.",
        common_field="T_La_Canada_Flintridge_Inv_0_12",
        botanical_field="T_La_Canada_Flintridge_Inv_0_13",
    )


def fetch_fontana() -> dict[str, Any]:
    blossom_where = (
        "UPPER(T_Fontanainventory__XYTableT_11) LIKE 'PRUNUS%' OR "
        "UPPER(T_Fontanainventory__XYTableT_11) LIKE 'MALUS%' OR "
        "UPPER(T_Fontanainventory__XYTableT_11) LIKE 'MAGNOLIA%' OR "
        "UPPER(T_Fontanainventory__XYTableT_10) LIKE '%CHERRY%' OR "
        "UPPER(T_Fontanainventory__XYTableT_10) LIKE '%PLUM%' OR "
        "UPPER(T_Fontanainventory__XYTableT_10) LIKE '%PEACH%' OR "
        "UPPER(T_Fontanainventory__XYTableT_10) LIKE '%MAGNOLIA%' OR "
        "UPPER(T_Fontanainventory__XYTableT_10) LIKE '%CRABAPPLE%' OR "
        "UPPER(T_Fontanainventory__XYTableT_10) LIKE '%APPLE%'"
    )
    return fetch_arcgis_inventory_city(
        city="Fontana",
        region="ca",
        layer_url=FONTANA_TREES_LAYER,
        dataset_page=FONTANA_DATASET_PAGE,
        where=blossom_where,
        out_fields=["OBJECTID", "T_Fontanainventory__XYTableT_10", "T_Fontanainventory__XYTableT_11"],
        object_id_field="OBJECTID",
        source_name="Fontana i-Tree Inventory",
        source_department="City of Fontana",
        ownership_raw="City of Fontana",
        note="Integrated from the official City of Fontana public tree inventory layer and official jurisdiction boundary.",
        common_field="T_Fontanainventory__XYTableT_10",
        botanical_field="T_Fontanainventory__XYTableT_11",
    )


def fetch_west_hollywood() -> dict[str, Any]:
    rows = fetch_soda_rows(WEST_HOLLYWOOD_API, where=WEST_HOLLYWOOD_BLOSSOM_WHERE, order="botanicalname")
    total_records = fetch_soda_count(WEST_HOLLYWOOD_API, where=WEST_HOLLYWOOD_BLOSSOM_WHERE)
    zip_index = fetch_us_city_zip_index("West Hollywood")
    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        location = row.get("location_1") or {}
        if isinstance(location, str):
            try:
                location = json.loads(location)
            except json.JSONDecodeError:
                location = {}
        lon = lat = None
        if isinstance(location, dict):
            try:
                lon = float(location.get("longitude"))
                lat = float(location.get("latitude"))
            except (TypeError, ValueError):
                lon = None
                lat = None
        if lon is None or lat is None or lon == 0.0 or lat == 0.0:
            continue
        if not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
            continue

        common_name = clean_common_name(row.get("commonname"))
        scientific_raw = format_scientific_display_name(row.get("botanicalname"), common_name)
        if not scientific_raw:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        zip_code = assign_zip_code(lon, lat, zip_index)
        ownership_raw = "City of West Hollywood"
        row_seed = f"{row.get('tree') or ''}|{common_name or ''}|{scientific_raw}|{lat:.6f}|{lon:.6f}"
        row_id = f"west-hollywood-{hashlib.md5(row_seed.encode('utf-8')).hexdigest()[:12]}"

        normalized_rows.append(
            {
                "id": row_id,
                "city": "West Hollywood",
                "source_dataset": "City Tree Inventory",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": lat,
                "lon": lon,
                "included": "1" if species_group else "0",
            }
        )
        if not species_group:
            continue
        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": row_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "West Hollywood",
                    "source_dataset": "City Tree Inventory",
                    "source_department": "City of West Hollywood",
                    "source_last_edit_at": "",
                },
            }
        )

    return {
        "city": "West Hollywood",
        "region": "ca",
        "features": output_features,
        "normalized_rows": normalized_rows,
        "source": {
            "name": "City Tree Inventory",
            "city": "West Hollywood",
            "endpoint": WEST_HOLLYWOOD_DATASET_PAGE,
            "last_edit_at": "",
            "records_fetched": total_records,
            "records_included": len(output_features),
            "note": "Integrated from the official City of West Hollywood public tree inventory dataset and official jurisdiction boundary.",
        },
    }


def fetch_newport_beach() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Newport Beach",
        region="ca",
        layer_url=NEWPORT_BEACH_TREES_LAYER,
        dataset_page=NEWPORT_BEACH_DATASET_PAGE,
        where=NEWPORT_BEACH_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Botanical", "CommonName", "Latitude", "Longitude"],
        object_id_field="OBJECTID",
        source_name="Tree Inventory",
        source_department="City of Newport Beach",
        ownership_raw="City of Newport Beach",
        note="Integrated from the official City of Newport Beach public tree inventory dashboard layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="Botanical",
        lon_field="Longitude",
        lat_field="Latitude",
    )


def fetch_burbank() -> dict[str, Any]:
    return fetch_treekeeper_inventory_city(
        city="Burbank",
        base_url=BURBANK_TREEKEEPER_BASE,
        uid="pinkhunter-burbank-ca",
        region="ca",
        source_name="TreeKeeper Inventory",
        source_department="City of Burbank",
        ownership_raw="City of Burbank",
        note="Integrated from the official City of Burbank public TreeKeeper inventory and official jurisdiction boundary.",
    )


def fetch_escondido() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Escondido",
        region="ca",
        layer_url=ESCONDIDO_TREES_LAYER,
        dataset_page=ESCONDIDO_DATASET_PAGE,
        where=ESCONDIDO_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "COMMON_NAME", "BOTANICAL_NAME", "LATITUDE", "LONGITUDE"],
        object_id_field="OBJECTID",
        source_name="Tree Inventory",
        source_department="City of Escondido",
        ownership_raw="City of Escondido",
        note="Integrated from the official City of Escondido public tree inventory layer and official jurisdiction boundary.",
        common_field="COMMON_NAME",
        botanical_field="BOTANICAL_NAME",
        lon_field="LONGITUDE",
        lat_field="LATITUDE",
    )


def fetch_redlands() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Redlands",
        region="ca",
        layer_url=REDLANDS_TREES_LAYER,
        dataset_page=REDLANDS_DATASET_PAGE,
        where=REDLANDS_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "COMMONNAME", "BOTANICALN"],
        object_id_field="OBJECTID",
        source_name="Street Trees",
        source_department="City of Redlands",
        ownership_raw="City of Redlands",
        note="Integrated from the official City of Redlands public street trees layer and official jurisdiction boundary.",
        common_field="COMMONNAME",
        botanical_field="BOTANICALN",
    )


def fetch_west_covina() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="West Covina",
        region="ca",
        layer_url=WEST_COVINA_TREES_LAYER,
        dataset_page=WEST_COVINA_DATASET_PAGE,
        where=WEST_COVINA_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "COMMONNAME", "BOTANICALN"],
        object_id_field="OBJECTID",
        source_name="West Covina Tree Information",
        source_department="City of West Covina",
        ownership_raw="City of West Covina",
        note="Integrated from the official City of West Covina public tree inventory layer and official jurisdiction boundary.",
        common_field="COMMONNAME",
        botanical_field="BOTANICALN",
    )


def fetch_santee() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Santee",
        region="ca",
        layer_url=SANTEE_TREES_LAYER,
        dataset_page=SANTEE_DATASET_PAGE,
        where=SPECIES_NAME_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "xCoordinate", "yCoordinate"],
        object_id_field="OBJECTID",
        source_name="All Boundaries Benefits Canopy",
        source_department="City of Santee",
        ownership_raw="City of Santee",
        note="Integrated from the official City of Santee public tree inventory layer and official jurisdiction boundary.",
        scientific_field="Species_Name",
        lon_field="xCoordinate",
        lat_field="yCoordinate",
    )


def fetch_la_mesa() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="La Mesa",
        region="ca",
        layer_url=LA_MESA_TREES_LAYER,
        dataset_page=LA_MESA_DATASET_PAGE,
        where=LA_MESA_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="Tree Inventory",
        source_department="City of La Mesa",
        ownership_raw="City of La Mesa",
        note="Integrated from the official City of La Mesa public tree inventory layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_vista() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Vista",
        region="ca",
        layer_url=VISTA_TREES_LAYER,
        dataset_page=VISTA_DATASET_PAGE,
        where=SPECIES_NAME_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "xCoordinate", "yCoordinate"],
        object_id_field="OBJECTID",
        source_name="Vista i-Tree Benefits",
        source_department="City of Vista",
        ownership_raw="City of Vista",
        note="Integrated from the official City of Vista public tree inventory layer and official jurisdiction boundary.",
        scientific_field="Species_Name",
        lon_field="xCoordinate",
        lat_field="yCoordinate",
    )


def fetch_camarillo() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Camarillo",
        region="ca",
        layer_url=CAMARILLO_TREES_LAYER,
        dataset_page=CAMARILLO_DATASET_PAGE,
        where=CAMARILLO_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "COMMON", "BOTANICAL"],
        object_id_field="OBJECTID",
        source_name="Trees",
        source_department="City of Camarillo",
        ownership_raw="City of Camarillo",
        note="Integrated from the official City of Camarillo public tree inventory layer and official jurisdiction boundary.",
        common_field="COMMON",
        botanical_field="BOTANICAL",
    )


def fetch_chino() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Chino",
        region="ca",
        layer_url=CHINO_TREES_LAYER,
        dataset_page=CHINO_DATASET_PAGE,
        where=CHINO_BLOSSOM_WHERE,
        out_fields=["FID", "Species"],
        object_id_field="FID",
        source_name="City Trees",
        source_department="City of Chino",
        ownership_raw="City of Chino",
        note="Integrated from the official City of Chino public tree inventory layer and official jurisdiction boundary.",
        common_field="Species",
    )


def fetch_glendora() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Glendora",
        region="ca",
        layer_url=GLENDORA_TREES_LAYER,
        dataset_page=GLENDORA_DATASET_PAGE,
        where=GLENDORA_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "COMMON", "BOTANICAL"],
        object_id_field="OBJECTID",
        source_name="Glendora Public Map Trees",
        source_department="City of Glendora",
        ownership_raw="City of Glendora",
        note="Integrated from the official City of Glendora public tree inventory layer and official jurisdiction boundary.",
        common_field="COMMON",
        botanical_field="BOTANICAL",
    )


def fetch_citrus_heights() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Citrus Heights",
        region="ca",
        layer_url=CITRUS_HEIGHTS_TREES_LAYER,
        dataset_page=CITRUS_HEIGHTS_DATASET_PAGE,
        where=BOTANICAL_COMMON_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="Citrus Heights i-Tree Benefits",
        source_department="City of Citrus Heights",
        ownership_raw="City of Citrus Heights",
        note="Integrated from the official City of Citrus Heights urban forestry tree inventory layer and official jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_lodi() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Lodi",
        region="ca",
        layer_url=LODI_TREES_LAYER,
        dataset_page=LODI_DATASET_PAGE,
        where=BOTANICAL_COMMON_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "CustomerName", "Address", "Street", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="Tree Inventory",
        source_department="City of Lodi",
        ownership_raw="City of Lodi",
        note="Integrated from the official City of Lodi public tree inventory and official jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_pleasanton() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Pleasanton",
        region="ca",
        layer_url=PLEASANTON_TREES_LAYER,
        dataset_page=PLEASANTON_DATASET_PAGE,
        where=BOTANICAL_COMMON_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "CustomerName", "Address", "Street", "CommonName", "BotanicalName"],
        object_id_field="OBJECTID",
        source_name="Tree Inventory",
        source_department="City of Pleasanton",
        ownership_raw="City of Pleasanton",
        note="Integrated from the official City of Pleasanton landscape architecture tree inventory map and official jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="CommonName",
        botanical_field="BotanicalName",
    )


def fetch_poway() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Poway",
        region="ca",
        layer_url=POWAY_TREES_LAYER,
        dataset_page=POWAY_DATASET_PAGE,
        where=REDLANDS_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "COMMONNAME", "BOTANICALN", "ADDRESS", "STREET"],
        object_id_field="OBJECTID",
        source_name="Tree",
        source_department="City of Poway",
        ownership_raw="City of Poway",
        note="Integrated from the official City of Poway GIS tree inventory layer and official jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="COMMONNAME",
        botanical_field="BOTANICALN",
    )


def fetch_redondo_beach() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Redondo Beach",
        region="ca",
        layer_url=REDONDO_BEACH_TREES_LAYER,
        dataset_page=REDONDO_BEACH_DATASET_PAGE,
        where=REDLANDS_BLOSSOM_WHERE,
        out_fields=["FID", "COMMONNAME", "BOTANICALN", "ADDRESS", "STREET"],
        object_id_field="FID",
        source_name="WCA Tree Inv Rendondo Beach",
        source_department="City of Redondo Beach",
        ownership_raw="City of Redondo Beach",
        note="Integrated from the official City of Redondo Beach GIS tree inventory layer and official jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="COMMONNAME",
        botanical_field="BOTANICALN",
    )


def fetch_thousand_oaks() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Thousand Oaks",
        region="ca",
        layer_url=THOUSAND_OAKS_TREES_LAYER,
        dataset_page=THOUSAND_OAKS_DATASET_PAGE,
        where=THOUSAND_OAKS_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Botanical", "Common", "X", "Y"],
        object_id_field="OBJECTID",
        source_name="Landscape Trees",
        source_department="City of Thousand Oaks",
        ownership_raw="City of Thousand Oaks",
        note="Integrated from the official City of Thousand Oaks landscape trees layer and official jurisdiction boundary.",
        common_field="Common",
        botanical_field="Botanical",
        lon_field="X",
        lat_field="Y",
    )


def fetch_corona() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Corona",
        region="ca",
        layer_url=CORONA_TREES_LAYER,
        dataset_page=CORONA_DATASET_PAGE,
        where=CORONA_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "CommonName", "BotanicalName", "xCoordinate", "yCoordinate"],
        object_id_field="OBJECTID",
        source_name="Corona Tree Sites",
        source_department="City of Corona",
        ownership_raw="City of Corona",
        note="Integrated from the official City of Corona public tree sites layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
        scientific_field="Species_Name",
        lon_field="xCoordinate",
        lat_field="yCoordinate",
    )


def fetch_buena_park() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Buena Park",
        region="ca",
        layer_url=BUENA_PARK_TREES_LAYER,
        dataset_page=BUENA_PARK_DATASET_PAGE,
        where=SPECIES_NAME_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "xCoordinate", "yCoordinate"],
        object_id_field="OBJECTID",
        source_name="Buena Park i-Tree Benefits",
        source_department="City of Buena Park",
        ownership_raw="City of Buena Park",
        note="Integrated from the official City of Buena Park public tree inventory layer and official jurisdiction boundary.",
        scientific_field="Species_Name",
        lon_field="xCoordinate",
        lat_field="yCoordinate",
    )


def fetch_la_verne() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="La Verne",
        region="ca",
        layer_url=LA_VERNE_TREES_LAYER,
        dataset_page=LA_VERNE_DATASET_PAGE,
        where=SPECIES_NAME_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name", "xCoordinate", "yCoordinate"],
        object_id_field="OBJECTID",
        source_name="La Verne Tree Benefits Map",
        source_department="City of La Verne",
        ownership_raw="City of La Verne",
        note="Integrated from the official City of La Verne public tree inventory layer and official jurisdiction boundary.",
        scientific_field="Species_Name",
        lon_field="xCoordinate",
        lat_field="yCoordinate",
    )


def fetch_yorba_linda() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Yorba Linda",
        region="ca",
        layer_url=YORBA_LINDA_TREES_LAYER,
        dataset_page=YORBA_LINDA_DATASET_PAGE,
        where=YORBA_LINDA_BLOSSOM_WHERE,
        out_fields=["FID", "Species_Na", "xCoordinat", "yCoordinat"],
        object_id_field="FID",
        source_name="Yorba Linda i-Tree Results",
        source_department="City of Yorba Linda",
        ownership_raw="City of Yorba Linda",
        note="Integrated from the official City of Yorba Linda public tree inventory layer and official jurisdiction boundary.",
        scientific_field="Species_Na",
        lon_field="xCoordinat",
        lat_field="yCoordinat",
    )


def fetch_san_dimas() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="San Dimas",
        region="ca",
        layer_url=SAN_DIMAS_TREES_LAYER,
        dataset_page=SAN_DIMAS_DATASET_PAGE,
        where=SAN_DIMAS_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "CommonName", "BotanicalName", "Latitude", "Longitude"],
        object_id_field="OBJECTID",
        source_name="City Owned Tree",
        source_department="City of San Dimas",
        ownership_raw="City of San Dimas",
        note="Integrated from the official City of San Dimas public tree inventory layer and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
        lon_field="Longitude",
        lat_field="Latitude",
    )


def fetch_rancho_palos_verdes() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Rancho Palos Verdes",
        region="ca",
        layer_url=RANCHO_PALOS_VERDES_TREES_LAYER,
        dataset_page=RANCHO_PALOS_VERDES_DATASET_PAGE,
        where=RANCHO_PALOS_VERDES_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "BOTANICAL", "COMMON", "ADDRESS", "STREET"],
        object_id_field="OBJECTID",
        source_name="Tree Inventory and Trimming Schedule",
        source_department="City of Rancho Palos Verdes",
        ownership_raw="City of Rancho Palos Verdes",
        note="Integrated from the official City of Rancho Palos Verdes public tree inventory layer and official jurisdiction boundary.",
        common_field="COMMON",
        botanical_field="BOTANICAL",
    )


def fetch_santa_monica() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Santa Monica",
        region="ca",
        layer_url=SANTA_MONICA_TREES_LAYER,
        dataset_page=SANTA_MONICA_DATASET_PAGE,
        where=SANTA_MONICA_BLOSSOM_WHERE,
        out_fields=["objectid", "commonname", "botanicalname", "latitude", "longitude"],
        object_id_field="objectid",
        source_name="Trees",
        source_department="City of Santa Monica",
        ownership_raw="City of Santa Monica",
        note="Integrated from the official City of Santa Monica public trees feature service and official jurisdiction boundary.",
        common_field="commonname",
        botanical_field="botanicalname",
        lon_field="longitude",
        lat_field="latitude",
    )


def fetch_oxnard() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Oxnard",
        region="ca",
        layer_url=OXNARD_TREES_LAYER,
        dataset_page=OXNARD_DATASET_PAGE,
        where=OXNARD_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "BOTANICALN", "COMMONNAME", "OwnedBy", "MaintainedBy"],
        object_id_field="OBJECTID",
        source_name="Trees",
        source_department="City of Oxnard",
        ownership_raw="City of Oxnard",
        note="Integrated from the official City of Oxnard public trees layer and official jurisdiction boundary.",
        common_field="COMMONNAME",
        botanical_field="BOTANICALN",
    )


def fetch_santa_barbara() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Santa Barbara",
        region="ca",
        layer_url=SANTA_BARBARA_TREES_LAYER,
        dataset_page=SANTA_BARBARA_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "BOTANICALN", "COMMONNAME"],
        object_id_field="OBJECTID",
        source_name="Tree Inventory (April 2017)",
        source_department="City of Santa Barbara",
        ownership_raw="City of Santa Barbara",
        note="Integrated from the official City of Santa Barbara public tree inventory layer and official jurisdiction boundary.",
        common_field="COMMONNAME",
        botanical_field="BOTANICALN",
    )


def fetch_goleta() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Goleta",
        region="ca",
        layer_url=GOLETA_TREES_LAYER,
        dataset_page=GOLETA_DATASET_PAGE,
        where="1=1",
        out_fields=["FID", "BOTANICALN", "COMMONNAME"],
        object_id_field="FID",
        source_name="Street Tree Inventory 3.19.2024",
        source_department="City of Goleta",
        ownership_raw="City of Goleta",
        note="Integrated from the official City of Goleta public tree inventory layer and official jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="COMMONNAME",
        botanical_field="BOTANICALN",
    )


def fetch_dana_point() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Dana Point",
        region="ca",
        layer_url=DANA_POINT_TREES_LAYER,
        dataset_page=DANA_POINT_DATASET_PAGE,
        where="1=1",
        out_fields=["FID", "BOTANICALN", "COMMONNAME"],
        object_id_field="FID",
        source_name="DP Trees",
        source_department="City of Dana Point",
        ownership_raw="City of Dana Point",
        note="Integrated from the official City of Dana Point public tree inventory layer and official jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="COMMONNAME",
        botanical_field="BOTANICALN",
    )


def fetch_arcadia() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Arcadia",
        region="ca",
        layer_url=ARCADIA_TREES_LAYER,
        dataset_page=ARCADIA_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "TreeSpecies", "CommonName"],
        object_id_field="OBJECTID",
        source_name="CityOfArcadiaTrees",
        source_department="City of Arcadia",
        ownership_raw="City of Arcadia",
        note="Integrated from the public City of Arcadia trees layer and official jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="CommonName",
        scientific_field="TreeSpecies",
    )


def fetch_torrance() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Torrance",
        region="ca",
        layer_url=TORRANCE_TREES_LAYER,
        dataset_page=TORRANCE_DATASET_PAGE,
        where="1=1",
        out_fields=["FID", "BOTANICALN", "COMMONNAME"],
        object_id_field="FID",
        source_name="Civic Center Master Plan Tree Layer",
        source_department="City of Torrance",
        ownership_raw="City of Torrance",
        note="Integrated from the public City of Torrance tree layer and official jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="COMMONNAME",
        botanical_field="BOTANICALN",
    )


def fetch_glendale() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Glendale",
        region="ca",
        layer_url=GLENDALE_TREES_LAYER,
        dataset_page=GLENDALE_DATASET_PAGE,
        where="1=1",
        out_fields=["FID", "Species"],
        object_id_field="FID",
        source_name="Glendale Tree Survey Updated",
        source_department="City of Glendale",
        ownership_raw="City of Glendale",
        note="Integrated from the public Glendale tree survey layer and official jurisdiction boundary.",
        scientific_field="Species",
    )


def fetch_inglewood() -> dict[str, Any]:
    main_result = fetch_arcgis_inventory_city_result(
        city="Inglewood",
        region="ca",
        layer_url=INGLEWOOD_TREES_LAYER,
        dataset_page=INGLEWOOD_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "NAME", "Street", "Zipcode", "CONDITION"],
        object_id_field="OBJECTID",
        source_name="Inglewood Tree Layer",
        source_department="City of Inglewood",
        ownership_raw="City of Inglewood",
        note="Integrated from the public Inglewood tree layer and official jurisdiction boundary.",
        common_field="NAME",
        zip_field="Zipcode",
        clip_to_boundary=True,
    )
    fruit_result = fetch_arcgis_inventory_city_result(
        city="Inglewood",
        region="ca",
        layer_url=INGLEWOOD_FRUIT_TREES_LAYER,
        dataset_page=INGLEWOOD_FRUIT_DATASET_PAGE,
        where="1=1",
        out_fields=["FID", "Fruit_Tree_Species", "Address"],
        object_id_field="FID",
        source_name="Inglewood Fruit Tree Recipients",
        source_department="City of Inglewood",
        ownership_raw="City of Inglewood",
        note="Integrated from the public Inglewood fruit tree recipients layer and official jurisdiction boundary.",
        scientific_field="Fruit_Tree_Species",
        clip_to_boundary=True,
    )
    return merge_city_results(
        city="Inglewood",
        region="ca",
        dataset_page=INGLEWOOD_FRUIT_DATASET_PAGE,
        source_name="Inglewood Tree Layers",
        source_department="City of Inglewood",
        note="Integrated from the public City of Inglewood tree layers and official jurisdiction boundary.",
        results=[main_result, fruit_result],
    )


def fetch_lynwood() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Lynwood",
        region="ca",
        layer_url=LYNWOOD_TREES_LAYER,
        dataset_page=LYNWOOD_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "NAME", "Street", "Zipcode", "CONDITION"],
        object_id_field="OBJECTID",
        source_name="Lynwood Public Trees (CAL FIRE)",
        source_department="City of Lynwood",
        ownership_raw="City of Lynwood",
        note="Integrated from the public Lynwood tree inventory layer and official jurisdiction boundary.",
        common_field="NAME",
        zip_field="Zipcode",
    )


def fetch_huntington_park() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Huntington Park",
        region="ca",
        layer_url=HUNTINGTON_PARK_TREES_LAYER,
        dataset_page=HUNTINGTON_PARK_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "NAME", "Street", "Zipcode", "CONDITION"],
        object_id_field="OBJECTID",
        source_name="UFMP Huntington Park Tree Sites",
        source_department="City of Huntington Park",
        ownership_raw="City of Huntington Park",
        note="Integrated from the public Huntington Park UFMP tree sites layer and official jurisdiction boundary.",
        common_field="NAME",
        zip_field="Zipcode",
    )


def fetch_commerce() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Commerce",
        region="ca",
        layer_url=COMMERCE_TREES_LAYER,
        dataset_page=COMMERCE_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "NAME", "Street", "Zipcode", "CONDITION"],
        object_id_field="OBJECTID",
        source_name="Commerce Public Trees",
        source_department="City of Commerce",
        ownership_raw="City of Commerce",
        note="Integrated from the public Commerce tree inventory layer and official jurisdiction boundary.",
        common_field="NAME",
        zip_field="Zipcode",
    )


def fetch_paramount() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="Paramount",
        region="ca",
        layer_url=PARAMOUNT_TREES_LAYER,
        dataset_page=PARAMOUNT_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "NAME", "Street", "CONDITION"],
        object_id_field="OBJECTID",
        source_name="TreePeople Paramount Tree Site Layer",
        source_department="City of Paramount",
        ownership_raw="City of Paramount",
        note="Integrated from the public Paramount tree site layer and official jurisdiction boundary.",
        common_field="NAME",
    )


def fetch_south_gate() -> dict[str, Any]:
    return fetch_arcgis_inventory_city_result(
        city="South Gate",
        region="ca",
        layer_url=SOUTH_GATE_CUDAHY_TREES_LAYER,
        dataset_page=SOUTH_GATE_CUDAHY_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "NAME", "Address", "CONDITION"],
        object_id_field="OBJECTID",
        source_name="South Gate Cudahy Public Tree Layer",
        source_department="City of South Gate",
        ownership_raw="City of South Gate",
        note="Integrated from the public South Gate/Cudahy tree layer clipped to the official South Gate jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="NAME",
    )


def fetch_cudahy() -> dict[str, Any]:
    public_result = fetch_arcgis_inventory_city_result(
        city="Cudahy",
        region="ca",
        layer_url=SOUTH_GATE_CUDAHY_TREES_LAYER,
        dataset_page=SOUTH_GATE_CUDAHY_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "NAME", "Address", "CONDITION"],
        object_id_field="OBJECTID",
        source_name="South Gate Cudahy Public Tree Layer",
        source_department="City of Cudahy",
        ownership_raw="City of Cudahy",
        note="Integrated from the public South Gate/Cudahy tree layer clipped to the official Cudahy jurisdiction boundary.",
        clip_to_boundary=True,
        scientific_field="NAME",
    )
    fruit_result = fetch_arcgis_inventory_city_result(
        city="Cudahy",
        region="ca",
        layer_url=CUDAHY_FRUIT_TREES_LAYER,
        dataset_page=CUDAHY_FRUIT_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "NAME", "Address", "CONDITION"],
        object_id_field="OBJECTID",
        source_name="South Gate Cudahy Fruit Tree Layer",
        source_department="City of Cudahy",
        ownership_raw="City of Cudahy",
        note="Integrated from the public South Gate/Cudahy fruit tree layer clipped to the official Cudahy jurisdiction boundary.",
        clip_to_boundary=True,
        scientific_field="NAME",
    )
    return merge_city_results(
        city="Cudahy",
        region="ca",
        dataset_page=CUDAHY_FRUIT_DATASET_PAGE,
        source_name="Cudahy Tree Layers",
        source_department="City of Cudahy",
        note="Integrated from the public City of Cudahy tree layers and official jurisdiction boundary.",
        results=[public_result, fruit_result],
    )


def fetch_i5_corridor_city(city: str) -> dict[str, Any]:
    escaped_city = city.replace("'", "''")
    where = f"City = '{escaped_city}'"
    return fetch_arcgis_inventory_city_result(
        city=city,
        region="ca",
        layer_url=I5_TREES_LAYER,
        dataset_page=I5_DATASET_PAGE,
        where=where,
        out_fields=["FID", "SPP_com", "SPP_bot", "City", "address"],
        object_id_field="FID",
        source_name="I-5 Project Data Tree Sites",
        source_department=f"City of {city}",
        ownership_raw=f"City of {city}",
        note=f"Integrated from the public I-5 corridor tree sites layer filtered to {city} and clipped to the official jurisdiction boundary.",
        clip_to_boundary=True,
        common_field="SPP_com",
        scientific_field="SPP_bot",
    )


def fetch_downey() -> dict[str, Any]:
    return fetch_i5_corridor_city("Downey")


def fetch_norwalk() -> dict[str, Any]:
    return fetch_i5_corridor_city("Norwalk")


def fetch_santa_fe_springs() -> dict[str, Any]:
    return fetch_i5_corridor_city("Santa Fe Springs")


def fetch_la_mirada() -> dict[str, Any]:
    return fetch_i5_corridor_city("La Mirada")


def fetch_ventura() -> dict[str, Any]:
    layer_info = fetch_json(VENTURA_TREES_LAYER, {"f": "pjson"})
    total_payload = fetch_json(
        f"{VENTURA_TREES_LAYER}/query",
        {"where": "1=1", "returnCountOnly": "true", "f": "json"},
    )
    features = fetch_arcgis_features_by_object_ids(
        VENTURA_TREES_LAYER,
        where="1=1",
        out_fields=["FID", "COMMON", "LATITUDE"],
        object_id_field="FID",
    )
    last_edit_at = iso_from_epoch((layer_info.get("editingInfo") or {}).get("lastEditDate"))
    return build_arcgis_inventory_result(
        city="Ventura",
        region="ca",
        features=features,
        total_records=int(total_payload.get("count") or len(features)),
        last_edit_at=last_edit_at,
        source_name="ARBOR ACCESS - City Tree Inventory",
        source_department="City of Ventura",
        dataset_page=VENTURA_DATASET_PAGE,
        ownership_raw="City of Ventura",
        note="Integrated from the official City of Ventura public tree inventory layer and official jurisdiction boundary.",
        object_id_field="FID",
        common_field="COMMON",
    )


def fetch_laguna_beach() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Laguna Beach",
        region="ca",
        layer_url=LAGUNA_BEACH_TREES_LAYER,
        dataset_page=LAGUNA_BEACH_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "BOTANICAL", "COMMON"],
        object_id_field="OBJECTID",
        source_name="City Maintained Tree Inventory",
        source_department="City of Laguna Beach",
        ownership_raw="City of Laguna Beach",
        note="Integrated from the official City of Laguna Beach maintained tree inventory layer and official jurisdiction boundary.",
        common_field="COMMON",
        botanical_field="BOTANICAL",
    )


def fetch_solana_beach() -> dict[str, Any]:
    return fetch_arcgis_inventory_city(
        city="Solana Beach",
        region="ca",
        layer_url=SOLANA_BEACH_TREES_LAYER,
        dataset_page=SOLANA_BEACH_DATASET_PAGE,
        where=SOLANA_BEACH_BLOSSOM_WHERE,
        out_fields=["OBJECTID", "Species_Name"],
        object_id_field="OBJECTID",
        source_name="City Maintained Tree Benefits July 2025",
        source_department="City of Solana Beach",
        ownership_raw="City of Solana Beach",
        note="Integrated from the official City of Solana Beach tree inventory application layer and official jurisdiction boundary.",
        scientific_field="Species_Name",
    )


def fetch_encinitas() -> dict[str, Any]:
    public_result = fetch_arcgis_inventory_city(
        city="Encinitas",
        region="ca",
        layer_url=ENCINITAS_PUBLIC_TREES_LAYER,
        dataset_page=ENCINITAS_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "CommonName", "BotanicalName", "Latitude", "Longitude"],
        object_id_field="OBJECTID",
        source_name="Tree Inventory Public",
        source_department="City of Encinitas",
        ownership_raw="City of Encinitas",
        note="Integrated from the official City of Encinitas public tree inventory layers and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
        lon_field="Longitude",
        lat_field="Latitude",
    )
    parks_result = fetch_arcgis_inventory_city(
        city="Encinitas",
        region="ca",
        layer_url=ENCINITAS_PARKS_TREES_LAYER,
        dataset_page=ENCINITAS_DATASET_PAGE,
        where="1=1",
        out_fields=["OBJECTID", "CommonName", "BotanicalName", "Latitude", "Longitude"],
        object_id_field="OBJECTID",
        source_name="Tree Inventory Parks Public",
        source_department="City of Encinitas",
        ownership_raw="City of Encinitas",
        note="Integrated from the official City of Encinitas public tree inventory layers and official jurisdiction boundary.",
        common_field="CommonName",
        botanical_field="BotanicalName",
        lon_field="Longitude",
        lat_field="Latitude",
    )
    return merge_city_results(
        city="Encinitas",
        region="ca",
        dataset_page=ENCINITAS_DATASET_PAGE,
        source_name="Trees in Encinitas",
        source_department="City of Encinitas",
        note="Integrated from the official City of Encinitas public street and parks tree inventory layers and official jurisdiction boundary.",
        results=[public_result, parks_result],
    )


CITY_FETCHERS = {
    "Anaheim": fetch_anaheim,
    "Arlington": fetch_arlington,
    "Austin": fetch_austin,
    "Azusa": fetch_azusa,
    "Baltimore": fetch_baltimore,
    "Bell": fetch_bell,
    "Beverly Hills": fetch_beverly_hills,
    "Boston": fetch_boston,
    "Burbank": fetch_burbank,
    "Buena Park": fetch_buena_park,
    "Camarillo": fetch_camarillo,
    "Cambridge": fetch_cambridge,
    "Chino": fetch_chino,
    "Citrus Heights": fetch_citrus_heights,
    "Concord": fetch_concord,
    "Costa Mesa": fetch_costa_mesa,
    "Corona": fetch_corona,
    "Dana Point": fetch_dana_point,
    "Commerce": fetch_commerce,
    "Cudahy": fetch_cudahy,
    "Dallas": fetch_dallas,
    "Denver": fetch_denver,
    "Downey": fetch_downey,
    "Encinitas": fetch_encinitas,
    "El Segundo": fetch_el_segundo,
    "Escondido": fetch_escondido,
    "Fontana": fetch_fontana,
    "Fremont": fetch_fremont,
    "Fullerton": fetch_fullerton,
    "Gilroy": fetch_gilroy,
    "Glendale": fetch_glendale,
    "Glendora": fetch_glendora,
    "Goleta": fetch_goleta,
    "Houston": fetch_houston,
    "Huntington Park": fetch_huntington_park,
    "Inglewood": fetch_inglewood,
    "Irvine": fetch_irvine,
    "Jersey City": fetch_jersey_city,
    "La Canada Flintridge": fetch_la_canada_flintridge,
    "La Mirada": fetch_la_mirada,
    "La Mesa": fetch_la_mesa,
    "La Verne": fetch_la_verne,
    "Laguna Beach": fetch_laguna_beach,
    "Las Vegas": fetch_las_vegas,
    "Lodi": fetch_lodi,
    "Lynwood": fetch_lynwood,
    "Los Angeles": fetch_los_angeles,
    "Los Gatos": fetch_los_gatos,
    "Maywood": fetch_maywood,
    "Milpitas": fetch_milpitas,
    "Monterey Park": fetch_monterey_park,
    "Mountain View": fetch_mountain_view,
    "Morgan Hill": fetch_morgan_hill,
    "Newport Beach": fetch_newport_beach,
    "Norwalk": fetch_norwalk,
    "Paramount": fetch_paramount,
    "Pleasanton": fetch_pleasanton,
    "Pomona": fetch_pomona,
    "Poway": fetch_poway,
    "Rancho Cucamonga": fetch_rancho_cucamonga,
    "Rancho Palos Verdes": fetch_rancho_palos_verdes,
    "Redlands": fetch_redlands,
    "Redondo Beach": fetch_redondo_beach,
    "Riverside": fetch_riverside,
    "Sacramento": fetch_sacramento,
    "Salinas": fetch_salinas,
    "San Dimas": fetch_san_dimas,
    "San Diego": fetch_san_diego,
    "San Fernando": fetch_san_fernando,
    "San Mateo": fetch_san_mateo,
    "San Rafael": fetch_san_rafael,
    "Santa Barbara": fetch_santa_barbara,
    "Santa Clarita": fetch_santa_clarita,
    "Santa Fe Springs": fetch_santa_fe_springs,
    "Santa Monica": fetch_santa_monica,
    "Santee": fetch_santee,
    "Saratoga": fetch_saratoga,
    "Solana Beach": fetch_solana_beach,
    "South Gate": fetch_south_gate,
    "South San Francisco": fetch_south_san_francisco,
    "Sunnyvale": fetch_sunnyvale,
    "Thousand Oaks": fetch_thousand_oaks,
    "Torrance": fetch_torrance,
    "Ventura": fetch_ventura,
    "Vista": fetch_vista,
    "West Covina": fetch_west_covina,
    "West Hollywood": fetch_west_hollywood,
    "West Sacramento": fetch_west_sacramento,
    "Yorba Linda": fetch_yorba_linda,
    "Oxnard": fetch_oxnard,
    "Arcadia": fetch_arcadia,
    "Pittsburgh": fetch_pittsburgh,
    "New York City": fetch_new_york_city,
    "Philadelphia": fetch_philadelphia,
    "Pasadena": fetch_pasadena,
    "Ottawa": fetch_ottawa,
    "Salt Lake City": fetch_salt_lake_city,
    "Toronto": fetch_toronto,
    "Montreal": fetch_montreal,
    "New Westminster": fetch_new_westminster,
}

CITY_FETCHERS.update({city: build_nyc_metro_treekeeper_fetcher(city, config) for city, config in NYC_METRO_TREEKEEPER_CONFIGS.items()})
CITY_FETCHERS.update({city: build_treekeeper_fetcher(city, config) for city, config in EAST_COAST_TREEKEEPER_CONFIGS.items()})
CITY_FETCHERS.update({city: build_treeplotter_fetcher(city, config) for city, config in EAST_COAST_TREEPLOTTER_CONFIGS.items()})
CITY_FETCHERS.update({city: build_nyc_metro_arcgis_fetcher(city, config) for city, config in NYC_METRO_ARCGIS_CONFIGS.items()})
CITY_FETCHERS.update({city: build_arcgis_fetcher(city, config) for city, config in UNCOVERED_STATE_ARCGIS_CONFIGS.items()})
CITY_FETCHERS.update({city: build_milwaukee_county_fetcher(city) for city in MILWAUKEE_COUNTY_SUPPORTED_CITIES})


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish targeted city updates into existing city-split public data.")
    parser.add_argument("--city", action="append", choices=SUPPORTED_CITIES, help="City to refresh. Repeat for multiple cities.")
    parser.add_argument(
        "--skip-global-refresh",
        action="store_true",
        help="Skip global coverage/meta refresh. Useful when publishing several batches and refreshing once at the end.",
    )
    args = parser.parse_args()

    target_cities = args.city or list(SUPPORTED_CITIES)
    results = [CITY_FETCHERS[city]() for city in target_cities]
    target_regions = {result["region"] for result in results}
    target_city_set = set(target_cities)
    next_rows: list[dict[str, Any]] = []
    normalized_path = NORMALIZED_DIR / "trees_normalized.csv"
    has_normalized_baseline = normalized_path.exists()
    existing_meta = load_meta()
    existing_area_cities = {
        str(area.get("jurisdiction") or "")
        for region in existing_meta.get("regions", [])
        for area in region.get("areas", [])
        if area.get("jurisdiction")
    }
    if not has_normalized_baseline:
        overlapping_cities = sorted(existing_area_cities & target_city_set)
        if overlapping_cities:
            raise RuntimeError(
                "Missing data/normalized/trees_normalized.csv baseline; refusing to republish existing cities "
                f"without full normalized context: {', '.join(overlapping_cities)}"
            )

    for result in results:
        write_city_geojson(result["region"], result["city"], result["features"])
        next_rows.extend(result["normalized_rows"])

    if has_normalized_baseline:
        normalized_path = rewrite_normalized_rows(target_city_set, next_rows)
    meta = existing_meta
    meta["generated_at"] = dt.datetime.now(tz=dt.timezone.utc).isoformat()
    ensure_region_entries(meta, target_regions)
    save_meta(meta)
    refresh_publish_indexes(target_regions, skip_global_refresh=args.skip_global_refresh)

    if has_normalized_baseline:
        unknown_items = recompute_unknown_items_from_path(normalized_path)
    else:
        existing_unknown_items = json.loads((PUBLIC_DATA_DIR / "unknown_scientific_names.v1.json").read_text(encoding="utf-8"))
        unknown_items = merge_unknown_items(
            existing_unknown_items,
            recompute_unknown_items([normalize_row_for_csv(row) for row in next_rows]),
        )
    write_json_atomic(PUBLIC_DATA_DIR / "unknown_scientific_names.v1.json", unknown_items)

    meta = load_meta()
    meta["generated_at"] = dt.datetime.now(tz=dt.timezone.utc).isoformat()
    existing_sources = [source for source in meta.get("sources", []) if source.get("city") not in target_cities]
    existing_sources.extend(result["source"] for result in results)
    existing_sources.sort(key=lambda source: (source.get("city", ""), source.get("name", "")))
    meta["sources"] = existing_sources
    meta["source_count"] = len(existing_sources)

    if has_normalized_baseline:
        latest_rows = load_normalized_rows()
        meta["total_records"] = len(latest_rows)
    else:
        meta["total_records"] = int(existing_meta.get("total_records") or 0) + len(next_rows)
    meta["included_records"] = sum(int(region.get("tree_count", 0)) for region in meta.get("regions", []))
    meta["unknown_records"] = sum(item["count"] for item in unknown_items)
    save_meta(meta)
    subprocess.run(["python3", "scripts/check_region_data_sizes.py", "--data-dir", "public/data"], check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
