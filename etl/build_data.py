#!/usr/bin/env python3
"""Build public dataset files for the Pink Hunter map.

Outputs:
- public/data/trees.<region>.city-index.v1.json
- public/data/trees.<region>.city.<slug>.v1.geojson
- public/data/coverage.v1.geojson
- public/data/species-guide.v1.json
- public/data/meta.v2.json
- public/data/unknown_scientific_names.v1.json
- data/normalized/trees_normalized.csv
"""

from __future__ import annotations

import csv
import datetime as dt
import gzip
import io
import json
import math
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import shapefile
    from pyproj import CRS, Transformer
except ImportError as exc:  # pragma: no cover - runtime dependency guard
    raise RuntimeError(
        "Missing Python ETL dependencies. Install them with `python3 -m pip install -r requirements.txt`."
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA_DIR = ROOT / "public" / "data"
NORMALIZED_DIR = ROOT / "data" / "normalized"
MAPPING_PATH = ROOT / "config" / "prunus_mapping.csv"
SUBTYPE_MAPPING_PATH = ROOT / "config" / "blossom_subtypes.csv"
SPECIES_GUIDE_CONTENT_PATH = ROOT / "config" / "species_guide_content.v1.json"
REFERENCE_DIR = ROOT / "data" / "reference"
SUPPLEMENTAL_DIR = ROOT / "data" / "supplemental"

SEATTLE_LAYER = "https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Combined_Tree_Point/FeatureServer/0"
BELLEVUE_LAYER = "https://services1.arcgis.com/EYzEZbDhXZjURPbP/arcgis/rest/services/City_Trees/FeatureServer/29"
REDMOND_LAYER = "https://services7.arcgis.com/9u5SMK7jcrQbBJIC/arcgis/rest/services/TreeSite/FeatureServer/0"
RENTON_LAYER = "https://webmaps.rentonwa.gov/as03/rest/services/Cityworks/proCSParkAsset/MapServer/24"
KENMORE_LAYER = "https://gwa.kenmorewa.gov/arcgis/rest/services/Public_Trees/FeatureServer/22"
SEATAC_LAYER = "https://services3.arcgis.com/DLryYCwhA8W7Jq7Q/arcgis/rest/services/Trees/FeatureServer/1"
PUYALLUP_LAYER = "https://services8.arcgis.com/5K6vnOH0GkPyJs6A/arcgis/rest/services/City_Maintained_Street_Trees/FeatureServer/0"
GIG_HARBOR_LAYER = "https://services3.arcgis.com/FjNT4j1knnY5Wsw5/arcgis/rest/services/PW_Trees_Public_Viewer/FeatureServer/0"
SAMMAMISH_BASE = "https://sammamishwa.treekeepersoftware.com"
SAMMAMISH_SEARCH_ENDPOINT = f"{SAMMAMISH_BASE}/cffiles/search.cfc"
SAMMAMISH_GRIDS_ENDPOINT = f"{SAMMAMISH_BASE}/cffiles/grids.cfc"
EVERETT_BASE = "https://everettwa.treekeepersoftware.com"
EVERETT_SEARCH_ENDPOINT = f"{EVERETT_BASE}/cffiles/search.cfc"
EVERETT_GRIDS_ENDPOINT = f"{EVERETT_BASE}/cffiles/grids.cfc"
KIRKLAND_TREEPLOTTER_URL = "https://pg-cloud.com/KirklandWA/"
KIRKLAND_DB_ENDPOINT = "https://pg-cloud.com/main/server/db.php"
KIRKLAND_CLIENT_VERSION = "v3.9.65"
SHORELINE_LAYER = "https://gis.shorelinewa.gov/server/rest/services/PublicFacing/Parks/MapServer/7"
SNOHOMISH_LAYER = "https://services9.arcgis.com/hUiJ0kKwHN6Cf0DY/arcgis/rest/services/Tree_Inventory_Canopy_2024_WFL1/FeatureServer/3"
BELLINGHAM_LAYER = "https://maps.cob.org/arcgis3/rest/services/Parks/NotableTrees/MapServer/0"
SPOKANE_LAYER = "https://services.arcgis.com/3PDwyTturHqnGCu0/arcgis/rest/services/Tree_Inventory/FeatureServer/7"
YAKIMA_LAYER = "https://gis.yakimawa.gov/arcgis/rest/services/Parks/Trees/MapServer/0"
WALLA_WALLA_LAYER = "https://gis2.ci.walla-walla.wa.us/arcgis/rest/services/Basemap/GISBaseMap_TreesVisible/MapServer/0"
BOSTON_TREES_GEOJSON = "https://data.boston.gov/dataset/e4c76e72-dcf1-40a0-b426-97c52214a9fe/resource/2f575489-e721-45ec-865a-e98f10d2ee85/download/bprd_trees.geojson"
BOSTON_DATASET_PAGE = "https://data.boston.gov/dataset/bprd-trees"
ARLINGTON_TREES_LAYER = "https://arlgis.arlingtonva.us/arcgis/rest/services/Open_Data/od_DPR_Tree_Points/FeatureServer/0"
ARLINGTON_BOUNDARY_LAYER = "https://arlgis.arlingtonva.us/arcgis/rest/services/Open_Data/od_County_Polygon/FeatureServer/0"
ARLINGTON_DATASET_PAGE = "https://www.arlingtonva.us/About-Arlington/Data-and-Research/Open-Data-Portal"
MONTGOMERY_TREE_POINTS_LAYER = "https://gis4.montgomerycountymd.gov/arcgis/rest/services/DEP/DEPTreePoints_MapOnly/MapServer/0"
MONTGOMERY_BOUNDARY_LAYER = "https://gis4.montgomerycountymd.gov/arcgis/rest/services/general/MoCo_boundary/FeatureServer/0"
MONTGOMERY_DATASET_PAGE = "https://data.montgomerycountymd.gov/"
BALTIMORE_TREES_LAYER = "https://gis.baltimorecity.gov/egis/rest/services/Foresty/Trees/MapServer/0"
BALTIMORE_DATASET_PAGE = "https://data.baltimorecity.gov/"
JERSEY_CITY_TREES_LAYER = "https://services2.arcgis.com/UXbywc7dSkfgdPp4/arcgis/rest/services/City_of_Jersey_City_Tree_WFL1/FeatureServer/0"
JERSEY_CITY_DATASET_PAGE = "https://www.jerseycitynj.gov/cityhall/infrastructure/division_of_sustainability/urbanforests"
DC_LAYER = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Urban_Tree_Canopy/MapServer/23"
PORTLAND_LAYER = "https://www.portlandmaps.com/od/rest/services/COP_OpenData_Environment/MapServer/1415"
PORTLAND_BOUNDARY_LAYER = "https://www.portlandmaps.com/od/rest/services/COP_OpenData_Boundary/MapServer/10"
SAN_JOSE_LAYER = "https://geo.sanjoseca.gov/server/rest/services/OPN/OPN_OpenDataService/MapServer/510"
SAN_JOSE_DATASET_PAGE = "https://data.sanjoseca.gov/dataset/street-tree"
SAN_FRANCISCO_DATASET = "https://data.sfgov.org/resource/tkzw-k3nq.json"
SAN_FRANCISCO_METADATA = "https://data.sfgov.org/api/views/tkzw-k3nq"
SAN_FRANCISCO_DATASET_PAGE = "https://data.sfgov.org/City-Infrastructure/Street-Tree-List/tkzw-k3nq"
BURLINGAME_LAYER = "https://services2.arcgis.com/yrktbS5Xw87hJQvs/arcgis/rest/services/WebMap_Burlingame_AllLayers_WFL1/FeatureServer/0"
BURLINGAME_DATASET_PAGE = "https://www.burlingame.org/466/Trees-Urban-Forest"
PALO_ALTO_TREES_LAYER = "https://services6.arcgis.com/evmyRZRrsopdeog7/ArcGIS/rest/services/TreeData/FeatureServer/0"
PALO_ALTO_TREES_ZIP = "https://opengis.cityofpaloalto.org/OGDShapes/TreeData.zip"
PALO_ALTO_BOUNDARY_ZIP = "https://opengis.cityofpaloalto.org/OGDShapes/CPAboundary.zip"
PALO_ALTO_DATASET_PAGE = "https://opengis.cityofpaloalto.org/"
BERKELEY_TREES_ZIP = "https://www.arcgis.com/sharing/rest/content/items/88829f4ae7254b5280732e88e65e6df5/data"
BERKELEY_TREES_ITEM = "https://www.arcgis.com/home/item.html?id=88829f4ae7254b5280732e88e65e6df5"
BERKELEY_BOUNDARY_LAYER = "https://services1.arcgis.com/IYiCpZoSIq9lAxi8/arcgis/rest/services/Land_Boundary/FeatureServer/0"
CUPERTINO_TREES_LAYER = "https://gis.cupertino.org/cupgis/rest/services/Public/AmazonData/MapServer/29"
CUPERTINO_BOUNDARY_LAYER = "https://gis.cupertino.org/cupgis/rest/services/Public/AmazonData/MapServer/14"
CUPERTINO_DATASET_PAGE = "https://gis-cupertino.opendata.arcgis.com/"
OAKLAND_TREES_DATASET = "https://data.oaklandca.gov/resource/4jcx-enxf.json"
OAKLAND_METADATA = "https://data.oaklandca.gov/api/views/4jcx-enxf"
OAKLAND_DATASET_PAGE = "https://data.oaklandca.gov/Environmental/Oakland-Street-Trees/4jcx-enxf"
MILPITAS_LAYER = "https://services8.arcgis.com/OPmRdssd8jj0bT5H/arcgis/rest/services/Trees_RO/FeatureServer/0"
MILPITAS_BOUNDARY_LAYER = "https://services8.arcgis.com/OPmRdssd8jj0bT5H/arcgis/rest/services/City%20Boundary/FeatureServer/0"
SAN_MATEO_LAYER = "https://services2.arcgis.com/g26Y0m7OCdjU0ObA/arcgis/rest/services/Street_Trees/FeatureServer/0"
SAN_MATEO_DATASET_PAGE = "https://www.arcgis.com/home/item.html?id=67c8b57d2d91459c9f951df9de961a06"
FREMONT_TREEPLOTTER_URL = "https://pg-cloud.com/FremontCA/"
FREMONT_BOUNDARY_LAYER = "https://services2.arcgis.com/AVso4yDITKsybTJg/arcgis/rest/services/COF_Boundary/FeatureServer/0"
FREMONT_DATASET_PAGE = "https://www.fremont.gov/government/departments/maintenance-operations/urban-forestry/tree-inventory-tree-value"
CONCORD_TREEPLOTTER_URL = "https://pg-cloud.com/ConcordCA/"
CONCORD_BOUNDARY_LAYER = "https://gis.cityofconcord.org/gsrv1/rest/services/BaseMap/MapServer/17"
CONCORD_DATASET_PAGE = "https://www.cityofconcord.org/1249/Tree-Inventory"
SOUTH_SF_BASE = "https://ssfca.treekeepersoftware.com"
SOUTH_SF_SEARCH_ENDPOINT = f"{SOUTH_SF_BASE}/cffiles/search.cfc"
SOUTH_SF_GRIDS_ENDPOINT = f"{SOUTH_SF_BASE}/cffiles/grids.cfc"
SOUTH_SF_BOUNDARY_LAYER = (
    "https://services5.arcgis.com/inY93B27l4TSbT7h/arcgis/rest/services/cityowned_service/FeatureServer/0"
)
SOUTH_SF_DATASET_PAGE = "https://www.ssfca.gov/Departments/Parks-Recreation/Divisions/Parks-Division/Trees"
SAN_RAFAEL_TREES_LAYER = "https://services5.arcgis.com/sruoiBDPu8SihcGN/arcgis/rest/services/Trees/FeatureServer/0"
SAN_RAFAEL_BOUNDARY_LAYER = "https://services5.arcgis.com/sruoiBDPu8SihcGN/arcgis/rest/services/sanrafael2/FeatureServer/0"
SAN_RAFAEL_DATASET_PAGE = "https://www.arcgis.com/home/item.html?id=8a236959df6f438ba38bdf5db85ce54a"
BEAVERTON_BOUNDARY_LAYER = (
    "https://gisweb.beavertonoregon.gov/server/rest/services/Public_SharedServices/pubAdministrativeBoundaries/MapServer/0"
)
NYC_DATASET = "https://data.cityofnewyork.us/resource/uvpi-gqnh.json"
NYC_METADATA = "https://data.cityofnewyork.us/api/views/uvpi-gqnh.json"
NYC_DATASET_PAGE = "https://data.cityofnewyork.us/Environment/2015-Street-Tree-Census-Tree-Data/uvpi-gqnh"
PHILADELPHIA_LAYER = (
    "https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/ppr_tree_inventory_2025/FeatureServer/0"
)
PHILADELPHIA_DATASET_PAGE = (
    "https://metadata.phila.gov/#home/datasetdetails/57a0e1d5aa8882104134830e/representationdetails/690a4183ef9cba032bd11d00/"
)
CAMBRIDGE_STREET_TREES_ZIP = "https://gis.cambridgema.gov/download/shp/ENVIRONMENTAL_StreetTrees.shp.zip"
CAMBRIDGE_DATASET_PAGE = "https://www.cambridgema.gov/GIS/gisdatadictionary/Environmental/ENVIRONMENTAL_StreetTrees"
VANCOUVER_BC_DATASET = "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/public-trees"
VANCOUVER_BC_BOUNDARY_DATASET = "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/city-boundary"
VICTORIA_PARK_TREES_LAYER = "https://maps.victoria.ca/server/rest/services/OpenData/OpenData_Parks/MapServer/15"
VICTORIA_BOUNDARY_LAYER = "https://maps.victoria.ca/server/rest/services/OpenData/OpenData_Land/MapServer/2"
VICTORIA_PARK_TREES_ITEM = "https://www.arcgis.com/sharing/rest/content/items/36e90771770542baaa89afddce69195a"
BURNABY_BOUNDARY_LAYER = "https://gis.burnaby.ca/arcgis/rest/services/OpenData/OpenData3/MapServer/12"
DELTA_BOUNDARY_LAYER = "https://maps.delta.ca/arcgis/rest/services/DeltaMap/PropertyBasemap/MapServer/13"
SAANICH_BOUNDARY_LAYER = "https://map.saanich.ca/server/rest/services/MAPS/SaanichBaseMap/MapServer/6"
SURREY_BOUNDARY_LAYER = "https://gisservices.surrey.ca/arcgis/rest/services/OpenData/MapServer/133"
RICHMOND_BC_BOUNDARY_LAYER = "https://maps.richmond.ca/internal/rest/services/Hansen/Hansen_Base/MapServer/5"
OTTAWA_TREES_LAYER = "https://maps.ottawa.ca/arcgis/rest/services/Forestry/MapServer/0"
OTTAWA_BOUNDARY_LAYER = "https://maps.ottawa.ca/arcgis/rest/services/OfficialPlan/MapServer/71"
OTTAWA_DATASET_PAGE = "https://ottawa.ca/en/canopy-cover-and-tree-inventory"
MONTREAL_TREES_CSV = "https://donnees.montreal.ca/dataset/b89fd27d-4b49-461b-8e54-fa2b34a628c4/resource/64e28fe6-ef37-437a-972d-d1d3f1f7d891/download/arbres-publics.csv"
MONTREAL_BOUNDARY_GEOJSON = "https://donnees.montreal.ca/dataset/9797a946-9da8-41ec-8815-f6b276dec7e9/resource/e18bfd07-edc8-4ce8-8a5a-3b617662a794/download/limites-administratives-agglomeration.geojson"
MONTREAL_DATASET_PAGE = "https://donnees.montreal.ca/fr/dataset/arbres"
TORONTO_STREET_TREE_CSV = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/6ac4569e-fd37-4cbc-ac63-db3624c5f6a2/resource/b65cd31d-fabc-4222-83ef-8ddd11295d2b/download/street-tree-data-4326.csv"
TORONTO_BOUNDARY_ZIP = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/841fb820-46d0-46ac-8dcb-d20f27e57bcc/resource/41bf97f0-da1a-46a9-ac25-5ce0078d6760/download/toronto-boundary-wgs84.zip"
TORONTO_DATASET_PAGE = "https://open.toronto.ca/dataset/street-tree-data/"
ZIP_LAYER = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/ZIPCODE_AREA_113/FeatureServer/0"
US_CENSUS_CITIES_LAYER = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer/18"
)
US_CENSUS_ZCTA_LAYER = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/PUMA_TAD_TAZ_UGA_ZCTA/MapServer/11"
)

# Hard rule from product requirements:
# Coverage geometry must come from official jurisdiction boundaries only.
# City governments still use official city boundaries; county-equivalent
# jurisdictions such as Arlington use their official county boundary.
STRICT_OFFICIAL_JURISDICTION_BOUNDARY_ONLY = True
DEFAULT_REGION = "wa"
WA_METRO_OVERVIEW_BOUNDS: list[list[float]] = [[-123.08, 47.02], [-121.55, 48.08]]
WARNING_BYTES = 35 * 1024 * 1024
HIGH_WARNING_BYTES = 45 * 1024 * 1024
HARD_FAIL_BYTES = 50 * 1024 * 1024
REGION_LABELS: dict[str, str] = {
    "wa": "WA",
    "ca": "CA",
    "or": "OR",
    "dc": "DC",
    "bc": "BC",
    "on": "ON",
    "qc": "QC",
    "va": "VA",
    "md": "MD",
    "nj": "NJ",
    "ny": "NY",
    "pa": "PA",
    "ma": "MA",
}
SPECIES_GROUPS: list[str] = ["cherry", "plum", "peach", "magnolia", "crabapple"]
REGION_CITY_OVERRIDES: dict[str, str] = {
    "Arlington": "va",
    "Alexandria": "va",
    "Montgomery County": "md",
    "Baltimore": "md",
    "Jersey City": "nj",
    "Boston": "ma",
    "New York City": "ny",
    "Pittsburgh": "pa",
    "Philadelphia": "pa",
    "Cambridge": "ma",
    "Ottawa": "on",
    "Toronto": "on",
    "Montreal": "qc",
    "Washington DC": "dc",
    "Burnaby": "bc",
    "Delta": "bc",
    "Richmond BC": "bc",
    "Saanich": "bc",
    "Surrey": "bc",
    "Vancouver BC": "bc",
    "Victoria BC": "bc",
    "Portland": "or",
    "Mountain View": "ca",
    "Milpitas": "ca",
    "Monterey": "ca",
    "Napa": "ca",
    "Sacramento": "ca",
    "Salinas": "ca",
    "San Mateo": "ca",
    "San Rafael": "ca",
    "Santa Clara": "ca",
    "Santa Cruz": "ca",
    "Santa Rosa": "ca",
    "Stockton": "ca",
    "Sunnyvale": "ca",
    "Burlingame": "ca",
    "Daly City": "ca",
    "Concord": "ca",
    "Fremont": "ca",
    "Hayward": "ca",
    "Alameda": "ca",
    "Palo Alto": "ca",
    "Berkeley": "ca",
    "Cupertino": "ca",
    "Oakland": "ca",
    "Redwood City": "ca",
    "Richmond": "ca",
    "San Francisco": "ca",
    "San Jose": "ca",
    "South San Francisco": "ca",
    "Beaverton": "or",
    "Gresham": "or",
    "Hillsboro": "or",
    "Salem": "or",
    "Tigard": "or",
}

CITY_BOUNDARY_HINTS: dict[str, dict[str, str]] = {
    "Arlington": {"state": "51", "basename": "Arlington", "boundary_source": "arlington_county_arcgis"},
    "Alexandria": {"state": "51"},
    "Montgomery County": {"boundary_source": "montgomery_county_arcgis"},
    "Baltimore": {"state": "24"},
    "Jersey City": {"state": "34"},
    "Boston": {"state": "25"},
    "New York City": {"state": "36", "basename": "New York"},
    "Pittsburgh": {"state": "42"},
    "Philadelphia": {"state": "42"},
    "Cambridge": {"state": "25"},
    "Ottawa": {"boundary_source": "ottawa_arcgis"},
    "Toronto": {"boundary_source": "toronto_zip"},
    "Montreal": {"boundary_source": "montreal_arrondissements_geojson"},
    "Washington DC": {"state": "11", "basename": "Washington"},
    "Portland": {"boundary_source": "portland_or_arcgis"},
    "Beaverton": {"state": "41", "boundary_source": "beaverton_arcgis"},
    "Gresham": {"state": "41"},
    "Hillsboro": {"state": "41"},
    "Mountain View": {"state": "06"},
    "Milpitas": {"state": "06", "boundary_source": "milpitas_arcgis"},
    "Monterey": {"state": "06"},
    "Napa": {"state": "06"},
    "Sacramento": {"state": "06"},
    "Salinas": {"state": "06"},
    "Salem": {"state": "41"},
    "San Mateo": {"state": "06"},
    "San Rafael": {"state": "06", "boundary_source": "san_rafael_arcgis"},
    "Santa Clara": {"state": "06"},
    "Santa Cruz": {"state": "06"},
    "Santa Rosa": {"state": "06"},
    "Stockton": {"state": "06"},
    "Sunnyvale": {"state": "06"},
    "Tigard": {"state": "41"},
    "Burlingame": {"state": "06"},
    "Daly City": {"state": "06"},
    "Concord": {"state": "06", "boundary_source": "concord_arcgis"},
    "Fremont": {"state": "06", "boundary_source": "fremont_arcgis"},
    "Hayward": {"state": "06"},
    "Alameda": {"state": "06"},
    "Palo Alto": {"state": "06", "boundary_source": "us_census_place"},
    "Berkeley": {"boundary_source": "berkeley_arcgis"},
    "Cupertino": {"boundary_source": "cupertino_arcgis"},
    "Oakland": {"state": "06"},
    "Redwood City": {"state": "06"},
    "Richmond": {"state": "06"},
    "San Francisco": {"state": "06"},
    "San Jose": {"state": "06"},
    "South San Francisco": {"state": "06", "boundary_source": "south_sf_arcgis"},
    "Vancouver BC": {"boundary_source": "vancouver_bc_ods"},
    "Richmond BC": {"boundary_source": "richmond_bc_arcgis"},
    "Vancouver WA": {"state": "53", "basename": "Vancouver"},
    "Victoria BC": {"boundary_source": "victoria_bc_arcgis"},
    "Burnaby": {"boundary_source": "burnaby_arcgis"},
    "Delta": {"boundary_source": "delta_arcgis"},
    "Saanich": {"boundary_source": "saanich_arcgis"},
    "Surrey": {"boundary_source": "surrey_arcgis"},
}

ALLOWED_CENSUS_PLACE_LSADC = {"25", "43"}

OFFICIAL_DATA_UNAVAILABLE_CITIES: dict[str, str] = {
    "Alexandria": "The official City of Alexandria urban-forestry and GIS pages were reviewed, but no public single-tree species inventory was confirmed.",
    "Auburn": "City investigated; no reliable official public single-tree species dataset was confirmed.",
    "Alameda": "Official city tree and urban-forest materials were reviewed, but no verified public citywide single-tree species dataset was confirmed.",
    "Beaux Arts Village": "Only a contractor-published public map was found; no verified official public city-hosted tree dataset was confirmed.",
    "Beaverton": "Official inventory web maps exist, but the raw city tree inventory service currently requires a token and is not publicly queryable for stable ETL access.",
    "Black Diamond": "City investigated; no official public single-tree species dataset was confirmed.",
    "Bonney Lake": "Official public portal was checked and no tree inventory layer was exposed.",
    "Bothell": "Official planning documents mention inventory work, but no public raw single-tree species endpoint was confirmed.",
    "Bremerton": "An official tree web map exists, but the underlying feature service is not publicly queryable for ETL access.",
    "Burnaby": "Official Burnaby GIS/open-data sources were reviewed, but no public single-tree species inventory was confirmed.",
    "Brier": "City investigated; public search hits were false positives, not an official city tree inventory.",
    "Burien": "Official tree data uses internal species codes without a public mapping table usable for current taxonomy.",
    "Carnation": "City investigated; no official public single-tree species dataset was confirmed.",
    "Clyde Hill": "City investigated; no official public single-tree species dataset was confirmed.",
    "Covington": "City investigated; no reliable official public single-tree species dataset was confirmed.",
    "Des Moines": "City investigated; no reliable official public single-tree species dataset was confirmed.",
    "Delta": "Official Delta GIS/open-data sources were reviewed, but no public single-tree species inventory was confirmed.",
    "Davenport": "City investigated; public ArcGIS hits in this round were Davenport, Iowa datasets, not a verified City of Davenport, WA tree inventory.",
    "Daly City": "Official city urban-forestry and GIS entry points were reviewed, but no verified public citywide single-tree species dataset was confirmed.",
    "Duvall": "City investigated; public search hits were false positives, not an official city tree inventory.",
    "Edmonds": "City investigated; no official public single-tree species dataset was confirmed.",
    "Enumclaw": "City investigated; no official public single-tree species dataset was confirmed.",
    "Ferndale": "City investigated; public ArcGIS search hits in this round pointed to Ferndale, Michigan data, not a verified Ferndale, WA citywide public tree inventory.",
    "Federal Way": "City investigated; the previously accessible hosted layer turned out to be street lights, not trees.",
    "Fife": "City investigated; no official public single-tree species dataset was confirmed.",
    "Gresham": "Official ArcGIS search and city-site checks in this round did not confirm a public citywide single-tree species dataset.",
    "Granite Falls": "City investigated; no official public single-tree species dataset was confirmed.",
    "Hayward": "Official city urban-forestry and GIS entry points were reviewed, but no verified public citywide single-tree species dataset was confirmed.",
    "Hillsboro": "Official ArcGIS search and city-site checks in this round did not confirm a public citywide single-tree species dataset.",
    "Hunts Point": "City investigated; no official public single-tree species dataset was confirmed.",
    "Issaquah": "Official Urban Forestry materials indicate the public tree inventory is still a future implementation item.",
    "Kent": "Official city sustainability and GIS sources were checked, but no public single-tree species layer was exposed.",
    "Lacey": "Official open-data sources were searched and no public single-tree species dataset was found.",
    "Lake Forest Park": "Official city pages and ArcGIS search did not confirm a city-owned public single-tree species layer.",
    "Lakewood": "Official materials reference inventory work, but current public city sources do not expose a raw single-tree species layer.",
    "Lake Stevens": "City investigated; no official public single-tree species dataset was confirmed.",
    "Lynden": "City investigated; no official public single-tree species dataset was confirmed.",
    "Lynnwood": "Official ArcGIS content reviewed was project-specific, not a citywide public single-tree inventory.",
    "Maple Valley": "City investigated; no reliable official public single-tree species dataset was confirmed.",
    "Marysville": "City investigated; search hits were false positives from other states, not a City of Marysville dataset.",
    "Medina": "Official GIS entry points were rechecked and no public tree inventory layer was confirmed.",
    "Mercer Island": "Only a partial 2018 Town Center inventory is documented publicly; a citywide public single-tree dataset is not confirmed.",
    "Montgomery County": "Official Montgomery County public GIS layers were reviewed; the public Tree Montgomery point layer is a planting-program dataset rather than a countywide single-tree inventory.",
    "Mill Creek": "City investigated; no official public single-tree species dataset was confirmed.",
    "Monroe": "City investigated; search hits were false positives, not a City of Monroe tree inventory.",
    "Monterey": "Official city tree standards and GIS entry points were reviewed, but no public citywide single-tree species dataset was confirmed.",
    "Mountain View": "Official city forestry materials describe inventory work, but no public citywide single-tree species dataset was confirmed in this round.",
    "Mountlake Terrace": "City investigated; no official public single-tree species dataset was confirmed.",
    "Mukilteo": "City investigated; no official public single-tree species dataset was confirmed.",
    "Newcastle": "City investigated; no official public single-tree species dataset was confirmed.",
    "Napa": "Official ArcGIS and city data portal searches in this round did not confirm a public citywide single-tree species dataset.",
    "Normandy Park": "City investigated; no official public single-tree species dataset was confirmed.",
    "North Bend": "City investigated; no official public single-tree species dataset was confirmed.",
    "Olympia": "No current official city single-tree species layer was confirmed; only older or non-city sources were found.",
    "Port Orchard": "City investigated; no official public single-tree species dataset was confirmed.",
    "Redwood City": "Official city GIS and public-works materials were reviewed, but no verified public citywide single-tree dataset was confirmed in this round.",
    "Richmond": "Official Richmond, CA ArcGIS and city data searches in this round did not confirm a public citywide single-tree species dataset.",
    "Richland": "City investigated; public search hits in this round were non-city or non-Washington datasets, not a verified City of Richland public tree inventory.",
    "Richmond BC": "Official City of Richmond GIS boundary services were confirmed, but no public citywide single-tree species inventory was confirmed in this round.",
    "Sacramento": "Official city pages and open-data entry points were checked, but no public citywide single-tree species dataset was confirmed in this round.",
    "Saanich": "Official Saanich GIS/open-data sources were reviewed, but no public single-tree species inventory was confirmed.",
    "Salem": "Official ArcGIS and city GIS searches in this round did not confirm a public citywide single-tree species dataset.",
    "Santa Clara": "Official city urban-forest materials were reviewed, but no public citywide single-tree species dataset was confirmed in this round.",
    "Santa Cruz": "Official ArcGIS and city GIS searches in this round did not confirm a public citywide single-tree species dataset.",
    "Santa Rosa": "Official city GIS results found fire-damaged tree-removal layers, not a citywide public single-tree inventory.",
    "Skykomish": "City investigated; no official public single-tree species dataset was confirmed.",
    "Snoqualmie": "City investigated; no official public single-tree species dataset was confirmed.",
    "Stockton": "Official ArcGIS and city GIS searches in this round did not confirm a public citywide single-tree species dataset.",
    "Sumner": "City investigated; search hits were false positives, not a city tree inventory.",
    "Surrey": "Official Surrey Open Data exposes `Important Trees` and `Park Specimen Trees`, but no citywide public single-tree species inventory was confirmed.",
    "Tacoma": "Official ArcGIS content found in this round was canopy-height mapping, not a public single-tree species inventory.",
    "Tigard": "Official ArcGIS results in this round exposed an ash-tree inventory, not a citywide public single-tree species inventory.",
    "Tukwila": "City investigated; no reliable official public single-tree species dataset was confirmed.",
    "Tumwater": "Official GIS sources were reviewed and no public single-tree species layer was confirmed.",
    "University Place": "City investigated; no official public single-tree species dataset was confirmed.",
    "Vancouver WA": "Official geohub content surfaced canopy and other inventories, but not a public single-tree species dataset.",
    "Wenatchee": "City investigated; only Wenatchee Valley College campus tree maps surfaced in this round, not a verified City of Wenatchee public tree inventory.",
    "Woodinville": "Official city pages did not confirm a public single-tree species point inventory.",
    "Woodway": "City investigated; no official public single-tree species dataset was confirmed.",
    "Yarrow Point": "City investigated; no official public single-tree species dataset was confirmed.",
    "Sunnyvale": "County and city GIS sources were reviewed, but no verified public citywide single-tree species dataset was confirmed in this round.",
}

UW_SUPPLEMENTAL_PATH = SUPPLEMENTAL_DIR / "uw_prunus_overpass.json"

GENERIC_SCIENTIFIC_NAMES = {
    "prunus species",
    "prunus sp",
    "prunus sp.",
    "prunus",
    "magnolia species",
    "magnolia sp",
    "magnolia sp.",
    "magnolia",
    "malus species",
    "malus sp",
    "malus sp.",
    "malus",
}

GENERIC_DETAIL_LOOKUP = {
    "cherry",
    "cherry species",
    "plum",
    "plum species",
    "peach",
    "peach tree",
    "magnolia",
    "magnolia species",
    "crabapple",
    "crabapple species",
    "apple",
    "apple species",
    "apple crabapple",
    "cherry plum laurel",
    "other see notes",
    "fruit tree non cherry",
}

DIRTY_SUBTYPE_COMMON_OVERRIDES: dict[str, dict[str, str]] = {
    "cherry": {
        "cherry trees": "Flowering Cherry",
        "cherry tree": "Flowering Cherry",
        "cherry flowering": "Flowering Cherry",
        "flowering cherry": "Flowering Cherry",
        "japanese cherry": "Japanese Flowering Cherry",
        "japanese flowering cherry": "Japanese Flowering Cherry",
        "chery japanese flowering": "Japanese Flowering Cherry",
    },
    "plum": {
        "plum cherry": "Cherry Plum",
        "cherry plum": "Cherry Plum",
        "plum common": "European Plum",
        "common plum": "European Plum",
    },
    "peach": {
        "pape": "Peach",
        "persian ironwood": "Peach",
        "peach tree": "Peach",
    },
    "magnolia": {
        "magnolia bigleaf": "Bigleaf Magnolia",
        "bigleaf magnolia": "Bigleaf Magnolia",
    },
    "crabapple": {
        "apple": "Apple",
        "apple species": "Apple",
        "crabapple common": "Common Crabapple",
        "common crabapple": "Common Crabapple",
        "crabapple pillar": "Pillar Crabapple",
        "pillar crabapple": "Pillar Crabapple",
    },
}

DIRTY_SUBTYPE_SCIENTIFIC_OVERRIDES: dict[tuple[str, str], str] = {
    ("plum", "prunus domestica"): "European Plum",
    ("plum", "prunus cerasifera"): "Cherry Plum",
    ("peach", "prunus persica"): "Peach",
    ("magnolia", "magnolia macrophylla"): "Bigleaf Magnolia",
    ("crabapple", "malus domestica"): "Apple",
    ("crabapple", "malus sylvestris"): "Common Crabapple",
}

DIRTY_SUBTYPE_LOOKUP = {
    *GENERIC_DETAIL_LOOKUP,
    "cherry trees",
    "cherry tree",
    "cherry flowering",
    "flowering cherry",
    "japanese cherry",
    "japanese flowering cherry",
    "chery japanese flowering",
    "plum cherry",
    "cherry plum",
    "plum common",
    "common plum",
    "pape",
    "persian ironwood",
    "prunus domestica",
    "prunus persica",
    "malus domestica",
    "malus sylvestris",
    "crabapple common",
    "common crabapple",
    "crabapple pillar",
    "pillar crabapple",
    "magnolia bigleaf",
    "bigleaf magnolia",
}


def iso_from_epoch(value: Any) -> str:
    if value in (None, ""):
        return ""
    number = int(value)
    if number > 10_000_000_000:
        number = number / 1000
    return dt.datetime.fromtimestamp(number, tz=dt.timezone.utc).isoformat()


def normalize_lookup_text(raw_value: str | None) -> str:
    if not raw_value:
        return ""

    value = raw_value.strip().lower()
    value = value.replace("\xa0", " ")
    value = value.replace("×", "x")
    value = value.replace("`", "")
    value = value.replace("’", "'")
    value = value.replace("'", "")
    value = value.replace("®", "")
    value = re.sub(r"[.,()/_-]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def fetch_json(
    url: str,
    params: dict[str, Any] | None = None,
    method: str = "GET",
    body: Any | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    query = urllib.parse.urlencode(params or {}, doseq=True)
    full_url = f"{url}?{query}" if query else url

    body_bytes: bytes | None = None
    if body is not None:
        if isinstance(body, (bytes, bytearray)):
            body_bytes = bytes(body)
        else:
            body_bytes = json.dumps(body).encode("utf-8")

    request_headers = dict(headers or {})
    if body_bytes is not None and "Content-Type" not in request_headers:
        request_headers["Content-Type"] = "application/json"

    last_error: Exception | None = None
    for attempt in range(1, 5):
        try:
            request = urllib.request.Request(full_url, data=body_bytes, headers=request_headers, method=method.upper())
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc

        for insecure in (False, True):
            cmd = ["curl", "-sL", "--max-time", "60"]
            if insecure:
                cmd.append("-k")
            if method.upper() != "GET":
                cmd.extend(["-X", method.upper()])
            for key, value in request_headers.items():
                cmd.extend(["-H", f"{key}: {value}"])
            if body_bytes is not None:
                cmd.extend(["--data", body_bytes.decode("utf-8")])
            cmd.append(full_url)
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                last_error = RuntimeError(f"curl failed ({result.returncode}): {result.stderr.strip()}")
                continue
            payload = result.stdout.strip()
            if not payload:
                last_error = RuntimeError("curl returned empty payload")
                continue
            try:
                return json.loads(payload)
            except Exception as exc:  # noqa: PERF203
                last_error = exc

        time.sleep(0.35 * attempt)

    raise RuntimeError(f"Failed to fetch valid JSON for {url}: {last_error}")


def fetch_binary(url: str) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, 5):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                return response.read()
        except Exception as exc:
            last_error = exc

        for insecure in (False, True):
            cmd = ["curl", "-sL", "--max-time", "60"]
            if insecure:
                cmd.append("-k")
            cmd.append(url)
            result = subprocess.run(cmd, capture_output=True, check=False)
            if result.returncode != 0:
                last_error = RuntimeError(f"curl failed ({result.returncode}): {result.stderr.decode('utf-8', 'ignore').strip()}")
                continue
            if result.stdout:
                return bytes(result.stdout)
            last_error = RuntimeError("curl returned empty payload")

        time.sleep(0.35 * attempt)

    raise RuntimeError(f"Failed to fetch binary payload for {url}: {last_error}")


def decode_cpg(payload: bytes | None) -> str:
    if not payload:
        return "utf-8"
    text = payload.decode("utf-8", "ignore").strip()
    if not text:
        return "utf-8"
    upper = text.upper()
    if upper in {"UTF-8", "UTF8"}:
        return "utf-8"
    if upper in {"ANSI 1252", "WINDOWS-1252", "1252"}:
        return "cp1252"
    return text


def transform_geojson_coordinates(value: Any, transformer: Transformer | None) -> Any:
    if transformer is None:
        if isinstance(value, tuple):
            return [transform_geojson_coordinates(item, transformer) for item in value]
        if isinstance(value, list):
            return [transform_geojson_coordinates(item, transformer) for item in value]
        return value

    if isinstance(value, (list, tuple)) and len(value) >= 2 and all(isinstance(item, (int, float)) for item in value[:2]):
        lon, lat = transformer.transform(float(value[0]), float(value[1]))
        tail = [float(item) for item in value[2:] if isinstance(item, (int, float))]
        return [lon, lat, *tail]
    if isinstance(value, tuple):
        return [transform_geojson_coordinates(item, transformer) for item in value]
    if isinstance(value, list):
        return [transform_geojson_coordinates(item, transformer) for item in value]
    return value


def transformer_from_prj(prj_text: str | None) -> Transformer | None:
    if not prj_text:
        return None
    source_crs = CRS.from_wkt(prj_text)
    if source_crs.to_epsg() == 4326:
        return None
    return Transformer.from_crs(source_crs, CRS.from_epsg(4326), always_xy=True)


def load_zipped_shapefile(zip_url: str) -> tuple[shapefile.Reader, str | None]:
    payload = fetch_binary(zip_url)
    archive = zipfile.ZipFile(io.BytesIO(payload))
    members = {Path(name).suffix.lower(): name for name in archive.namelist() if not name.endswith("/")}
    shp_name = members.get(".shp")
    shx_name = members.get(".shx")
    dbf_name = members.get(".dbf")
    if not shp_name or not shx_name or not dbf_name:
        raise RuntimeError(f"Missing one or more shapefile members in archive: {zip_url}")
    prj_name = members.get(".prj")
    cpg_name = members.get(".cpg")
    prj_text = archive.read(prj_name).decode("utf-8", "ignore") if prj_name else None
    encoding = decode_cpg(archive.read(cpg_name) if cpg_name else None)
    reader = shapefile.Reader(
        shp=io.BytesIO(archive.read(shp_name)),
        shx=io.BytesIO(archive.read(shx_name)),
        dbf=io.BytesIO(archive.read(dbf_name)),
        encoding=encoding,
    )
    return reader, prj_text


def load_zipped_point_shapefile_rows(zip_url: str) -> list[dict[str, Any]]:
    reader, prj_text = load_zipped_shapefile(zip_url)
    transformer = transformer_from_prj(prj_text)
    field_names = [field[0] for field in reader.fields[1:]]
    rows: list[dict[str, Any]] = []
    for shape_record in reader.iterShapeRecords():
        shape = shape_record.shape
        if not shape.points:
            continue
        lon, lat = shape.points[0][:2]
        if transformer:
            lon, lat = transformer.transform(float(lon), float(lat))
        rows.append(
            {
                "attributes": dict(zip(field_names, list(shape_record.record), strict=False)),
                "geometry": {"x": float(lon), "y": float(lat)},
            }
        )
    return rows


def load_zipped_boundary_geometry(zip_url: str) -> dict[str, Any] | None:
    reader, prj_text = load_zipped_shapefile(zip_url)
    transformer = transformer_from_prj(prj_text)
    for shape_record in reader.iterShapeRecords():
        shape = shape_record.shape
        if not shape.points:
            continue
        geometry = shape.__geo_interface__
        coordinates = transform_geojson_coordinates(geometry.get("coordinates"), transformer)
        return {"type": geometry.get("type"), "coordinates": coordinates}
    return None


def fetch_all_features(
    layer_url: str,
    where: str,
    out_fields: list[str],
    order_by_field: str,
    page_size: int = 2000,
) -> list[dict[str, Any]]:
    features: list[dict[str, Any]] = []
    offset = 0

    while True:
        payload = fetch_json(
            f"{layer_url}/query",
            {
                "where": where,
                "outFields": ",".join(out_fields),
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "pjson",
                "resultOffset": offset,
                "resultRecordCount": page_size,
                "orderByFields": f"{order_by_field} ASC",
            },
        )

        if "error" in payload:
            raise RuntimeError(f"ArcGIS error for {layer_url}: {payload['error']}")

        batch = payload.get("features", [])
        if not batch:
            break

        features.extend(batch)
        exceeded_transfer_limit = bool(payload.get("exceededTransferLimit"))
        if not exceeded_transfer_limit and len(batch) < page_size:
            break

        offset += len(batch)

    return features


def fetch_ods_records(
    dataset_url: str,
    *,
    where: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    offset = 0
    total_count: int | None = None

    while True:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if where:
            params["where"] = where

        payload = fetch_json(f"{dataset_url}/records", params)
        if "error_code" in payload:
            raise RuntimeError(f"ODS error for {dataset_url}: {payload}")
        batch = payload.get("results", [])
        if total_count is None:
            total_count = int(payload.get("total_count") or len(batch))
        if not batch:
            break

        records.extend(batch)
        if len(records) >= total_count or len(batch) < limit:
            break
        offset += len(batch)

    return records


def fetch_ods_export_rows(
    dataset_url: str,
    *,
    where: str | None = None,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {}
    if where:
        params["where"] = where

    payload = fetch_json(f"{dataset_url}/exports/json", params or None)
    if not isinstance(payload, list):
        raise RuntimeError(f"Expected ODS export list for {dataset_url}, got: {type(payload).__name__}")
    return payload


def fetch_soda_rows(
    dataset_url: str,
    *,
    where: str | None = None,
    limit: int = 50_000,
    order: str | None = None,
    select: str | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0

    while True:
        params: dict[str, Any] = {"$limit": limit, "$offset": offset}
        if where:
            params["$where"] = where
        if order:
            params["$order"] = order
        if select:
            params["$select"] = select

        payload = fetch_json(dataset_url, params)
        if not isinstance(payload, list):
            raise RuntimeError(f"Expected SODA list for {dataset_url}, got: {type(payload).__name__}")
        if not payload:
            break

        rows.extend(payload)
        if len(payload) < limit:
            break
        offset += len(payload)

    return rows


def fetch_soda_count(dataset_url: str, *, where: str | None = None) -> int:
    params: dict[str, Any] = {"$select": "count(*)"}
    if where:
        params["$where"] = where
    payload = fetch_json(dataset_url, params)
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(f"Expected SODA count list for {dataset_url}, got: {type(payload).__name__}")
    return int(payload[0].get("count") or 0)


def normalize_scientific_name(raw_value: str | None) -> str:
    if not raw_value:
        return ""

    value = raw_value.strip().lower()
    value = value.replace("\xa0", " ")
    value = value.replace("×", "x")
    value = value.replace("`", "")
    value = value.replace("’", "'")
    value = value.replace("'", "")
    value = value.replace("®", "")
    value = value.replace(".", " ")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"^prunus\s+p\s+", "prunus ", value)
    value = re.sub(r"^prunus\s+n\s*a$", "prunus", value)
    if value == "prunus species":
        return "prunus species"
    return value.strip()


def parse_bellevue_species(raw_value: str | None) -> tuple[str, str | None]:
    if not raw_value:
        return "", None

    text = raw_value.strip()
    scientific = text
    common_name: str | None = None

    if " - " in text:
        scientific, remainder = text.split(" - ", 1)
        scientific = scientific.strip()
        match = re.search(r"\(([^()]+)\)", remainder)
        if match:
            common_name = match.group(1).strip()
        else:
            cleaned = remainder.strip(" -")
            common_name = cleaned if cleaned else None

    return scientific, common_name


def parse_sammamish_species(raw_value: str | None) -> tuple[str, str | None]:
    if not raw_value:
        return "", None

    text = raw_value.strip()
    match = re.match(r"^(.*?)\s*\(([^()]+)\)\s*$", text)
    if match:
        common_name = match.group(1).strip() or None
        scientific_name = match.group(2).strip()
        return scientific_name, common_name

    if re.match(r"^[A-Z][a-z]+(?:\s+[xX])?\s+[a-z][\w.-]+", text):
        return text, None
    return "", text


def parse_portland_species(raw_value: str | None) -> tuple[str, str | None]:
    scientific_name, common_name = parse_bellevue_species(raw_value)
    normalized = normalize_scientific_name(scientific_name)

    if normalized == "prunus cherry species and cultivars":
        return "Prunus species", common_name or "cherry"
    if normalized == "prunus plum species and cultivars":
        return "Prunus species", common_name or "plum"
    if normalized == "prunus spp":
        return "Prunus species", common_name
    if normalized == "magnolia spp":
        return "Magnolia species", common_name
    if normalized == "malus spp":
        return "Malus species", common_name

    return scientific_name, common_name


def parse_san_francisco_species(raw_value: str | None) -> tuple[str, str | None]:
    if not raw_value:
        return "", None

    text = raw_value.strip()
    if "::" not in text:
        return text, None

    scientific_name, common_part = text.split("::", 1)
    primary_common = common_part.split(":", 1)[0].strip()
    common_name = title_case_if_upper(primary_common) or None
    return scientific_name.strip(), common_name


def canonical_ownership(raw_value: str | None) -> str:
    raw = (raw_value or "").strip().lower()
    if not raw:
        return "unknown"
    if "private" in raw:
        return "private"
    if "adjacent parcel" in raw:
        return "private"
    return "public"


def generic_scientific_name_for_common_hint(common_name: str | None) -> str:
    hinted_species = tree_hint_species_group(common_name)
    if hinted_species in {"cherry", "plum", "peach"}:
        return "Prunus species"
    if hinted_species == "magnolia":
        return "Magnolia species"
    if hinted_species == "crabapple":
        return "Malus species"
    return ""


YAKIMA_OWNER_LABELS = {
    1: "Parks and Recreation",
    2: "Public Works",
    3: "Streets",
    4: "Wastewater",
    5: "Yakima Fire Department",
    6: "Yakima Transit",
    7: "Other",
    8: "Yakima Police Department",
    10: "Convention Center/Visitor Center",
    11: "Yakima Air Terminal",
    12: "Yakima County",
}

YAKIMA_MANAGER_LABELS = {
    1: "Parks and Recreation",
    2: "Public Works",
    3: "Streets",
    4: "Wastewater",
    5: "Yakima Fire Department",
    6: "Yakima Transit",
    7: "Yakima County",
    8: "Private / Owner of Adjacent Parcel",
    9: "Yakima Police Department",
    10: "Convention Center/Visitor Center",
    11: "Yakima Air Terminal",
    12: "Downtown Association of Yakima",
}


def normalize_yakima_ownership(owned_by: Any, maintained_by: Any) -> str:
    owner_label = YAKIMA_OWNER_LABELS.get(owned_by)
    manager_label = YAKIMA_MANAGER_LABELS.get(maintained_by)
    if owner_label and manager_label and owner_label != manager_label:
        return f"{owner_label} / maintained by {manager_label}"
    if owner_label:
        return owner_label
    if manager_label:
        return manager_label
    return "City of Yakima"


def point_in_ring(lon: float, lat: float, ring: list[list[float]]) -> bool:
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        intersects = (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
        if intersects:
            inside = not inside
        j = i
    return inside


def point_in_geometry(lon: float, lat: float, geometry: dict[str, Any]) -> bool:
    geom_type = geometry.get("type")
    coordinates = geometry.get("coordinates")

    if geom_type == "Polygon":
        inside = False
        for ring in coordinates:
            if point_in_ring(lon, lat, ring):
                inside = not inside
        return inside

    if geom_type == "MultiPolygon":
        for polygon in coordinates:
            inside = False
            for ring in polygon:
                if point_in_ring(lon, lat, ring):
                    inside = not inside
            if inside:
                return True
        return False

    return False


def geometry_bbox(geometry: dict[str, Any]) -> tuple[float, float, float, float]:
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates")
    points: list[list[float]] = []

    if geom_type == "Polygon":
        for ring in coords:
            points.extend(ring)
    elif geom_type == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                points.extend(ring)
    else:
        raise RuntimeError(f"Unsupported geometry type for ZIP polygon: {geom_type}")

    lons = [point[0] for point in points]
    lats = [point[1] for point in points]
    return (min(lons), min(lats), max(lons), max(lats))


def boundary_line_to_polygon(geometry: dict[str, Any]) -> dict[str, Any]:
    def stitch_multiline_boundary_rings(
        multiline: list[list[list[float]]],
        *,
        tolerance: float = 0.002,
    ) -> list[list[list[float]]]:
        def distance(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
            return math.hypot(point_a[0] - point_b[0], point_a[1] - point_b[1])

        snapped_nodes: list[tuple[float, float]] = []

        def snap_node(point: tuple[float, float]) -> tuple[float, float]:
            for existing in snapped_nodes:
                if distance(point, existing) <= tolerance:
                    return existing
            snapped_nodes.append(point)
            return point

        segment_records: list[dict[str, Any]] = []
        closed_rings: list[list[list[float]]] = []

        for segment in multiline:
            coords = [list(map(float, point[:2])) for point in segment if len(point) >= 2]
            if len(coords) < 2:
                continue
            start_node = snap_node(tuple(coords[0]))
            end_node = snap_node(tuple(coords[-1]))
            if start_node == end_node:
                if coords[0] != coords[-1]:
                    coords.append(coords[0])
                if len(coords) >= 4:
                    closed_rings.append(coords)
                continue
            segment_records.append({"coords": coords, "start": start_node, "end": end_node})

        if not segment_records:
            return closed_rings

        node_to_segments: dict[tuple[float, float], list[int]] = {}
        for index, segment in enumerate(segment_records):
            node_to_segments.setdefault(segment["start"], []).append(index)
            node_to_segments.setdefault(segment["end"], []).append(index)

        stitched_rings: list[list[list[float]]] = []
        unused_segments = set(range(len(segment_records)))

        while unused_segments:
            current_index = max(unused_segments, key=lambda index: len(segment_records[index]["coords"]))
            current_segment = segment_records[current_index]
            start_node = current_segment["start"]
            current_node = current_segment["end"]
            ring = [point[:] for point in current_segment["coords"]]
            unused_segments.remove(current_index)

            while current_node != start_node:
                candidates = [index for index in node_to_segments.get(current_node, []) if index in unused_segments]
                if not candidates:
                    raise RuntimeError("Failed to stitch official MultiLineString boundary into a closed polygon ring.")

                next_index = max(candidates, key=lambda index: len(segment_records[index]["coords"]))
                next_segment = segment_records[next_index]
                if next_segment["start"] == current_node:
                    oriented = [point[:] for point in next_segment["coords"]]
                    current_node = next_segment["end"]
                else:
                    oriented = [point[:] for point in reversed(next_segment["coords"])]
                    current_node = next_segment["start"]

                if ring[-1] == oriented[0]:
                    ring.extend(oriented[1:])
                else:
                    ring.extend(oriented)
                unused_segments.remove(next_index)

            if ring[0] != ring[-1]:
                ring.append(ring[0])
            if len(ring) >= 4:
                stitched_rings.append(ring)

        stitched_rings.extend(closed_rings)
        if not stitched_rings:
            raise RuntimeError("Official boundary line geometry did not contain any coordinates.")
        return stitched_rings

    geom_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geom_type in {"Polygon", "MultiPolygon"}:
        return geometry

    ring: list[list[float]] = []
    if geom_type == "LineString":
        ring = [list(point) for point in coordinates]
    elif geom_type == "MultiLineString":
        stitched_rings = stitch_multiline_boundary_rings(coordinates)
        if len(stitched_rings) == 1:
            return {"type": "Polygon", "coordinates": [stitched_rings[0]]}
        return arcgis_rings_to_geojson_geometry(stitched_rings)
    else:
        raise RuntimeError(f"Unsupported boundary geometry type: {geom_type}")

    if not ring:
        raise RuntimeError("Official boundary line geometry did not contain any coordinates.")
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    return {"type": "Polygon", "coordinates": [ring]}


def first_non_empty_value(properties: dict[str, Any], fields: tuple[str, ...]) -> str:
    for field in fields:
        value = properties.get(field)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def build_zip_index(
    zip_features: list[dict[str, Any]],
    code_fields: tuple[str, ...] = ("ZIPCODE",),
) -> list[dict[str, Any]]:
    index: list[dict[str, Any]] = []
    for feature in zip_features:
        properties = feature.get("properties", {})
        zip_code = first_non_empty_value(properties, code_fields)
        geometry = feature.get("geometry")
        if not zip_code or not geometry:
            continue
        min_lon, min_lat, max_lon, max_lat = geometry_bbox(geometry)
        index.append(
            {
                "zip_code": zip_code,
                "geometry": geometry,
                "min_lon": min_lon,
                "min_lat": min_lat,
                "max_lon": max_lon,
                "max_lat": max_lat,
            }
        )
    return index


def fetch_us_city_zip_index(city: str) -> list[dict[str, Any]]:
    geometry = load_city_boundary_geometry(city)
    if not geometry:
        return []

    min_lon, min_lat, max_lon, max_lat = geometry_bbox(geometry)
    payload = fetch_json(
        f"{US_CENSUS_ZCTA_LAYER}/query",
        {
            "where": "1=1",
            "geometry": f"{min_lon},{min_lat},{max_lon},{max_lat}",
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "GEOID,NAME",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        },
    )
    return build_zip_index(payload.get("features", []), code_fields=("GEOID", "NAME"))


def assign_zip_code(lon: Any, lat: Any, zip_index: list[dict[str, Any]]) -> str | None:
    if lon is None or lat is None:
        return None

    point_lon = float(lon)
    point_lat = float(lat)
    for item in zip_index:
        if not (
            item["min_lon"] <= point_lon <= item["max_lon"]
            and item["min_lat"] <= point_lat <= item["max_lat"]
        ):
            continue
        if point_in_geometry(point_lon, point_lat, item["geometry"]):
            return item["zip_code"]
    return None


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    unique_points = sorted(set(points))
    if len(unique_points) <= 1:
        return unique_points

    def cross(origin: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
        return (a[0] - origin[0]) * (b[1] - origin[1]) - (a[1] - origin[1]) * (b[0] - origin[0])

    lower: list[tuple[float, float]] = []
    for point in unique_points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper: list[tuple[float, float]] = []
    for point in reversed(unique_points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    return lower[:-1] + upper[:-1]


def polygon_from_points(points: list[tuple[float, float]]) -> dict[str, Any]:
    if not points:
        raise RuntimeError("Cannot build polygon from empty point set.")

    if len(points) == 1:
        lon, lat = points[0]
        delta = 0.002
        return {
            "type": "Polygon",
            "coordinates": [
                [
                    [lon - delta, lat - delta],
                    [lon + delta, lat - delta],
                    [lon + delta, lat + delta],
                    [lon - delta, lat + delta],
                    [lon - delta, lat - delta],
                ]
            ],
        }

    if len(points) == 2:
        (lon_a, lat_a), (lon_b, lat_b) = points
        delta = 0.001
        min_lon = min(lon_a, lon_b) - delta
        max_lon = max(lon_a, lon_b) + delta
        min_lat = min(lat_a, lat_b) - delta
        max_lat = max(lat_a, lat_b) + delta
        return {"type": "Polygon", "coordinates": bbox_to_polygon(min_lon, min_lat, max_lon, max_lat)}

    hull = convex_hull(points)
    ring = [[lon, lat] for lon, lat in hull]
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    return {"type": "Polygon", "coordinates": [ring]}


def load_mapping(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = [
            {
                "match_type": row["match_type"].strip(),
                "pattern": normalize_scientific_name(row["scientific_pattern"]),
                "species_group": row["species_group"].strip().lower(),
                "notes": row.get("notes", "").strip(),
            }
            for row in reader
            if row.get("scientific_pattern")
        ]

    exact_rows = [row for row in rows if row["match_type"] == "exact"]
    prefix_rows = [row for row in rows if row["match_type"] == "prefix"]
    return exact_rows + prefix_rows


def load_subtype_mapping(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [
            {
                "species_group": row["species_group"].strip().lower(),
                "pattern": normalize_lookup_text(row["match_pattern"]),
                "subtype_name": row["subtype_name"].strip(),
                "notes": row.get("notes", "").strip(),
            }
            for row in reader
            if row.get("match_pattern") and row.get("subtype_name")
        ]


def classify_scientific_name(scientific_name: str, mapping_rows: list[dict[str, str]]) -> str | None:
    normalized = normalize_scientific_name(scientific_name)
    if not normalized:
        return None

    for row in mapping_rows:
        pattern = row["pattern"]
        if row["match_type"] == "exact" and normalized == pattern:
            species = row["species_group"]
            return None if species == "exclude" else species
        if row["match_type"] == "prefix" and normalized.startswith(pattern):
            species = row["species_group"]
            return None if species == "exclude" else species

    return None


def classify_with_common_hint(
    scientific_name: str,
    common_name: str | None,
    mapping_rows: list[dict[str, str]],
) -> str | None:
    species_group = classify_scientific_name(scientific_name, mapping_rows)
    if species_group:
        return species_group

    normalized = normalize_scientific_name(scientific_name)
    if normalized not in GENERIC_SCIENTIFIC_NAMES:
        return None

    hint = normalize_lookup_text(common_name)
    if "cherry" in hint:
        return "cherry"
    if "plum" in hint:
        return "plum"
    if "peach" in hint:
        return "peach"
    if "magnolia" in hint:
        return "magnolia"
    if "crabapple" in hint or "crab apple" in hint:
        return "crabapple"
    return None


def tree_hint_species_group(common_name: str | None) -> str | None:
    hint = normalize_lookup_text(common_name)
    if "cherry" in hint:
        return "cherry"
    if "plum" in hint:
        return "plum"
    if "peach" in hint:
        return "peach"
    if "magnolia" in hint:
        return "magnolia"
    if "crabapple" in hint or "crab apple" in hint:
        return "crabapple"
    return None


def match_subtype_row(
    scientific_name: str,
    common_name: str | None,
    subtype_rows: list[dict[str, str]],
    species_group: str | None = None,
) -> dict[str, str] | None:
    scientific_lookup = normalize_lookup_text(scientific_name)
    common_lookup = normalize_lookup_text(common_name)
    best_row: dict[str, str] | None = None
    best_score: tuple[int, int, int, int] | None = None
    for row in subtype_rows:
        if species_group and row["species_group"] != species_group:
            continue
        pattern = row["pattern"]
        if not pattern:
            continue
        common_exact = common_lookup == pattern
        common_match = bool(common_lookup) and pattern in common_lookup
        scientific_exact = scientific_lookup == pattern
        scientific_match = bool(scientific_lookup) and pattern in scientific_lookup
        if not (common_exact or common_match or scientific_exact or scientific_match):
            continue
        score = (
            1 if common_exact else 0,
            1 if common_match else 0,
            1 if scientific_exact else 0,
            1 if scientific_match else 0,
        )
        if best_score is None or score > best_score:
            best_score = score
            best_row = row
    return best_row


def fallback_subtype_name(species_group: str, scientific_name: str, common_name: str | None) -> str | None:
    common_display = (common_name or "").strip()
    common_lookup = normalize_lookup_text(common_display)
    if common_display and common_lookup not in GENERIC_DETAIL_LOOKUP:
        return common_display

    scientific_display = scientific_name.strip()
    if scientific_display:
        normalized_scientific = normalize_scientific_name(scientific_display)
        if normalized_scientific not in GENERIC_SCIENTIFIC_NAMES:
            return scientific_display

    return None


def clean_subtype_name(
    species_group: str,
    scientific_name: str,
    common_name: str | None,
    subtype_name: str | None,
) -> str | None:
    scientific_lookup = normalize_scientific_name(scientific_name)
    common_lookup = normalize_lookup_text(common_name)
    subtype_display = (subtype_name or "").strip()
    subtype_lookup = normalize_lookup_text(subtype_display)

    should_override = (
        not subtype_display
        or subtype_lookup in DIRTY_SUBTYPE_LOOKUP
        or subtype_lookup == scientific_lookup
        or (common_lookup and subtype_lookup == common_lookup)
    )
    if not should_override:
        return subtype_display

    common_override = DIRTY_SUBTYPE_COMMON_OVERRIDES.get(species_group, {}).get(common_lookup)
    if common_override:
        return common_override

    scientific_override = DIRTY_SUBTYPE_SCIENTIFIC_OVERRIDES.get((species_group, scientific_lookup))
    if scientific_override:
        return scientific_override

    return subtype_display or None


def classify_tree_record(
    scientific_name: str,
    common_name: str | None,
    mapping_rows: list[dict[str, str]],
    subtype_rows: list[dict[str, str]],
) -> tuple[str | None, str | None]:
    species_group = classify_with_common_hint(scientific_name, common_name, mapping_rows)
    subtype_match = match_subtype_row(scientific_name, common_name, subtype_rows, species_group=species_group)
    if not species_group and subtype_match:
        species_group = subtype_match["species_group"]
    if not species_group:
        return None, None

    subtype_name = subtype_match["subtype_name"] if subtype_match else fallback_subtype_name(
        species_group, scientific_name, common_name
    )
    return species_group, clean_subtype_name(species_group, scientific_name, common_name, subtype_name)


def expand_abbreviated_botanical_name(scientific_name: str | None, common_name: str | None) -> str:
    text = (scientific_name or "").strip()
    match = re.match(r"^([A-Za-z])\.\s*(.+)$", text)
    if not match:
        return text

    genus_initial = match.group(1).lower()
    remainder = match.group(2).strip()
    epithet = remainder.lower().split()[0]
    hinted_species = tree_hint_species_group(common_name)

    prunus_epithets = {
        "serrulata",
        "subhirtella",
        "yedoensis",
        "cerasifera",
        "blireiana",
        "blireana",
        "persica",
        "mume",
        "incisa",
        "campanulata",
        "pseudocerasus",
    }
    magnolia_epithets = {
        "soulangeana",
        "stellata",
        "kobus",
        "loebneri",
        "denudata",
        "liliiflora",
        "sieboldii",
        "salicifolia",
        "tripetala",
        "macrophylla",
        "virginiana",
        "grandiflora",
    }
    malus_epithets = {
        "floribunda",
        "hupehensis",
        "ioensis",
        "baccata",
        "transitoria",
        "fusca",
        "tschonoskii",
    }

    if genus_initial == "p" and (hinted_species in {"cherry", "plum", "peach"} or epithet in prunus_epithets):
        return f"Prunus {remainder}"
    if genus_initial == "m":
        if hinted_species == "magnolia" or epithet in magnolia_epithets:
            return f"Magnolia {remainder}"
        if hinted_species == "crabapple" or epithet in malus_epithets:
            return f"Malus {remainder}"
    return text


def looks_like_target_blossom_species(scientific_name: str, common_name: str | None) -> bool:
    normalized = normalize_scientific_name(scientific_name)
    if normalized.startswith(("prunus", "magnolia", "malus")):
        return True
    return tree_hint_species_group(common_name) is not None


def decode_wkb_point_hex(hex_value: str | None) -> tuple[float, float] | None:
    if not hex_value:
        return None

    text = hex_value.strip()
    if not text or text == "<Null>":
        return None

    try:
        payload = bytes.fromhex(text)
    except ValueError:
        return None

    if len(payload) < 21:
        return None

    byte_order = "<" if payload[0] == 1 else ">"
    geom_type_raw = struct.unpack(f"{byte_order}I", payload[1:5])[0]
    has_srid = bool(geom_type_raw & 0x20000000)
    geom_type = geom_type_raw & 0x000000FF
    offset = 5

    if has_srid:
        if len(payload) < offset + 4:
            return None
        offset += 4

    if geom_type != 1:
        return None

    if len(payload) < offset + 16:
        return None

    x, y = struct.unpack(f"{byte_order}dd", payload[offset : offset + 16])
    return x, y


def web_mercator_to_lon_lat(x: float, y: float) -> tuple[float, float]:
    lon = math.degrees(x / 6378137.0)
    lat = math.degrees(2.0 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2.0)
    return lon, lat


def bbox_to_polygon(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> list[list[list[float]]]:
    return [
        [
            [min_lon, min_lat],
            [max_lon, min_lat],
            [max_lon, max_lat],
            [min_lon, max_lat],
            [min_lon, min_lat],
        ]
    ]


def load_first_feature(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    features = payload.get("features", [])
    if not features:
        raise RuntimeError(f"No features found in boundary file: {path}")
    return features[0]


def city_boundary_cache_path(city: str) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "_", city.lower()).strip("_")
    return REFERENCE_DIR / f"boundary_{slug}.geojson"


def city_boundary_query_parts(city: str) -> tuple[str, str]:
    hint = CITY_BOUNDARY_HINTS.get(city, {})
    basename = hint.get("basename", city)
    state = hint.get("state", "53")
    return basename, state


def region_for_city(city: str) -> str:
    if city in REGION_CITY_OVERRIDES:
        return REGION_CITY_OVERRIDES[city]
    if city.endswith(" BC") or city.endswith(", BC"):
        return "bc"
    if city.endswith(" VA") or city.endswith(", VA"):
        return "va"
    if city.endswith(" MD") or city.endswith(", MD"):
        return "md"
    if city.endswith(" NJ") or city.endswith(", NJ"):
        return "nj"
    if city.endswith(" NY") or city.endswith(", NY"):
        return "ny"
    if city.endswith(" PA") or city.endswith(", PA"):
        return "pa"
    if city.endswith(" MA") or city.endswith(", MA"):
        return "ma"
    if city.endswith(" CA") or city.endswith(", CA"):
        return "ca"
    if city.endswith(" OR") or city.endswith(", OR"):
        return "or"
    if city == "Washington DC" or city.endswith(" DC"):
        return "dc"
    return "wa"


def slugify_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def summarize_species_counts(features: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(
        str(feature.get("properties", {}).get("species_group", "")).strip().lower()
        for feature in features
        if str(feature.get("properties", {}).get("species_group", "")).strip().lower() in SPECIES_GROUPS
    )
    return {species: int(counts.get(species, 0)) for species in SPECIES_GROUPS}


def classify_warning_level(raw_bytes: int) -> str:
    if raw_bytes >= HARD_FAIL_BYTES:
        return "hard_fail"
    if raw_bytes >= HIGH_WARNING_BYTES:
        return "high_warning"
    if raw_bytes >= WARNING_BYTES:
        return "warning"
    return "none"


def geometry_points(geometry: dict[str, Any]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []

    def walk(node: Any) -> None:
        if not isinstance(node, list) or not node:
            return
        if len(node) >= 2 and isinstance(node[0], (int, float)) and isinstance(node[1], (int, float)):
            points.append((float(node[0]), float(node[1])))
            return
        for item in node:
            walk(item)

    walk(geometry.get("coordinates"))
    return points


def bounds_for_geometry(geometry: dict[str, Any]) -> tuple[float, float, float, float] | None:
    points = geometry_points(geometry)
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def build_region_bounds(coverage_features: list[dict[str, Any]]) -> dict[str, list[list[float]]]:
    region_bounds: dict[str, list[float] | None] = {region: None for region in REGION_LABELS}
    for feature in coverage_features:
        region = region_for_city(feature["properties"]["jurisdiction"])
        bounds = bounds_for_geometry(feature["geometry"])
        if not bounds:
            continue
        if region_bounds[region] is None:
            region_bounds[region] = list(bounds)
            continue
        current = region_bounds[region]
        assert current is not None
        current[0] = min(current[0], bounds[0])
        current[1] = min(current[1], bounds[1])
        current[2] = max(current[2], bounds[2])
        current[3] = max(current[3], bounds[3])

    output: dict[str, list[list[float]]] = {}
    for region, bounds in region_bounds.items():
        if bounds is None:
            continue
        output[region] = [[bounds[0], bounds[1]], [bounds[2], bounds[3]]]

    output["wa"] = WA_METRO_OVERVIEW_BOUNDS
    return output


def boundary_feature_matches_city(feature: dict[str, Any], city: str) -> bool:
    properties = feature.get("properties", {})
    geometry = feature.get("geometry")
    if properties.get("jurisdiction") == city and geometry:
        return True
    basename, state = city_boundary_query_parts(city)
    return (
        bool(geometry)
        and properties.get("STATE") == state
        and properties.get("BASENAME") == basename
        and properties.get("LSADC") in ALLOWED_CENSUS_PLACE_LSADC
    )


def make_city_boundary_feature(city: str, geometry: dict[str, Any], *, source: str) -> dict[str, Any]:
    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "jurisdiction": city,
            "boundary_rule": "official_jurisdiction_boundary_only",
            "boundary_source": source,
        },
    }


def fetch_city_boundary_feature(city: str) -> dict[str, Any] | None:
    basename, state = city_boundary_query_parts(city)
    escaped_city = basename.replace("'", "''")
    payload = fetch_json(
        f"{US_CENSUS_CITIES_LAYER}/query",
        {
            "where": f"STATE = '{state}' AND BASENAME = '{escaped_city}' AND LSADC IN ('25','43')",
            "outFields": "BASENAME,NAME,STATE,GEOID,LSADC",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        },
    )

    features = payload.get("features", [])
    if not features:
        return None
    return features[0]


def fetch_special_city_boundary_feature(city: str) -> dict[str, Any] | None:
    hint = CITY_BOUNDARY_HINTS.get(city, {})
    boundary_source = hint.get("boundary_source")

    def fetch_arcgis_boundary_feature(layer_url: str, *, source: str) -> dict[str, Any] | None:
        query_layer_url = layer_url.rstrip("/")
        if not re.search(r"/(?:FeatureServer|MapServer)/\d+$", query_layer_url):
            service_payload = fetch_json(query_layer_url, {"f": "pjson"})
            layers = service_payload.get("layers") or []
            if layers:
                query_layer_url = f"{query_layer_url}/{layers[0]['id']}"

        payload = fetch_json(
            f"{query_layer_url}/query",
            {
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "pjson",
            },
        )
        features = payload.get("features", [])
        if not features:
            return None
        geometry_payload = (features[0].get("geometry") or {})
        if geometry_payload.get("rings"):
            geometry = arcgis_rings_to_geojson_geometry(geometry_payload["rings"])
        elif geometry_payload.get("paths"):
            geometry = boundary_line_to_polygon(
                {"type": "MultiLineString", "coordinates": geometry_payload["paths"]}
            )
        else:
            return None
        return make_city_boundary_feature(city, geometry, source=source)

    if boundary_source == "portland_or_arcgis":
        payload = fetch_json(
            f"{PORTLAND_BOUNDARY_LAYER}/query",
            {
                "where": "OBJECTID > 0",
                "outFields": "CITYNAME",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "pjson",
            },
        )
        features = payload.get("features", [])
        if not features:
            return None
        for feature in features:
            city_name = title_case_if_upper((feature.get("attributes") or {}).get("CITYNAME"))
            if city_name != city:
                continue
            rings = (feature.get("geometry") or {}).get("rings") or []
            if not rings:
                return None
            return make_city_boundary_feature(
                city,
                arcgis_rings_to_geojson_geometry(rings),
                source="City of Portland Open Data",
            )
        return None

    if boundary_source == "vancouver_bc_ods":
        records = fetch_ods_records(VANCOUVER_BC_BOUNDARY_DATASET, limit=1)
        if not records:
            return None
        geometry = ((records[0].get("geom") or {}).get("geometry")) or {}
        if not geometry:
            return None
        polygon_geometry = boundary_line_to_polygon(geometry)
        return make_city_boundary_feature(city, polygon_geometry, source="City of Vancouver Open Data")

    if boundary_source == "palo_alto_zip":
        geometry = load_zipped_boundary_geometry(PALO_ALTO_BOUNDARY_ZIP)
        if not geometry:
            return None
        return make_city_boundary_feature(city, geometry, source="City of Palo Alto Open GIS")

    if boundary_source == "ottawa_arcgis":
        payload = fetch_json(
            f"{OTTAWA_BOUNDARY_LAYER}/query",
            {
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "geojson",
            },
        )
        features = payload.get("features", [])
        if not features:
            return None
        geometry = features[0].get("geometry") or {}
        if not geometry:
            return None
        return make_city_boundary_feature(city, geometry, source="City of Ottawa Open Data")

    if boundary_source == "toronto_zip":
        geometry = load_zipped_boundary_geometry(TORONTO_BOUNDARY_ZIP)
        if not geometry:
            return None
        return make_city_boundary_feature(city, geometry, source="City of Toronto Open Data")

    if boundary_source == "montreal_arrondissements_geojson":
        result = subprocess.run(
            ["curl", "-sL", "-A", "Mozilla/5.0", MONTREAL_BOUNDARY_GEOJSON],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            payload = json.loads(result.stdout.lstrip("\ufeff"))
        else:
            payload = json.loads(fetch_binary(MONTREAL_BOUNDARY_GEOJSON).decode("utf-8-sig"))
        polygons: list[Any] = []
        for feature in payload.get("features", []):
            properties = feature.get("properties") or {}
            if properties.get("TYPE") != "Arrondissement":
                continue
            geometry = feature.get("geometry") or {}
            geom_type = geometry.get("type")
            coordinates = geometry.get("coordinates") or []
            if geom_type == "Polygon":
                polygons.append(coordinates)
            elif geom_type == "MultiPolygon":
                polygons.extend(coordinates)
        if not polygons:
            return None
        return make_city_boundary_feature(
            city,
            {"type": "MultiPolygon", "coordinates": polygons},
            source="Ville de Montréal Données ouvertes",
        )

    if boundary_source == "us_census_place":
        feature = fetch_city_boundary_feature(city)
        if not feature:
            return None
        return feature

    if boundary_source == "berkeley_arcgis":
        return fetch_arcgis_boundary_feature(BERKELEY_BOUNDARY_LAYER, source="City of Berkeley Land Boundary")

    if boundary_source == "cupertino_arcgis":
        return fetch_arcgis_boundary_feature(CUPERTINO_BOUNDARY_LAYER, source="City of Cupertino GIS")

    if boundary_source == "milpitas_arcgis":
        return fetch_arcgis_boundary_feature(MILPITAS_BOUNDARY_LAYER, source="City of Milpitas GIS")

    if boundary_source == "fremont_arcgis":
        return fetch_arcgis_boundary_feature(FREMONT_BOUNDARY_LAYER, source="City of Fremont GIS")

    if boundary_source == "concord_arcgis":
        return fetch_arcgis_boundary_feature(CONCORD_BOUNDARY_LAYER, source="City of Concord GIS")

    if boundary_source == "san_rafael_arcgis":
        return fetch_arcgis_boundary_feature(SAN_RAFAEL_BOUNDARY_LAYER, source="City of San Rafael GIS")

    if boundary_source == "south_sf_arcgis":
        return fetch_arcgis_boundary_feature(SOUTH_SF_BOUNDARY_LAYER, source="City of South San Francisco GIS")

    if boundary_source == "beaverton_arcgis":
        return fetch_arcgis_boundary_feature(BEAVERTON_BOUNDARY_LAYER, source="City of Beaverton GIS")

    if boundary_source == "arlington_county_arcgis":
        payload = fetch_json(
            f"{ARLINGTON_BOUNDARY_LAYER}/query",
            {
                "where": "1=1",
                "outFields": "COUNTY,STATE",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "pjson",
            },
        )
        features = payload.get("features", [])
        if not features:
            return None
        rings = (features[0].get("geometry") or {}).get("rings") or []
        if not rings:
            return None
        return make_city_boundary_feature(
            city,
            arcgis_rings_to_geojson_geometry(rings),
            source="Arlington County Open Data",
        )

    if boundary_source == "montgomery_county_arcgis":
        return fetch_arcgis_boundary_feature(
            MONTGOMERY_BOUNDARY_LAYER,
            source="Montgomery County GIS",
        )

    if boundary_source == "victoria_bc_arcgis":
        payload = fetch_json(
            f"{VICTORIA_BOUNDARY_LAYER}/query",
            {
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "geojson",
            },
        )
        features = payload.get("features", [])
        if not features:
            return None
        feature = features[0]
        feature["properties"] = {**(feature.get("properties") or {}), "jurisdiction": city}
        return feature

    if boundary_source == "burnaby_arcgis":
        return fetch_arcgis_boundary_feature(BURNABY_BOUNDARY_LAYER, source="City of Burnaby Open Data")

    if boundary_source == "delta_arcgis":
        return fetch_arcgis_boundary_feature(DELTA_BOUNDARY_LAYER, source="City of Delta GIS")

    if boundary_source == "saanich_arcgis":
        return fetch_arcgis_boundary_feature(SAANICH_BOUNDARY_LAYER, source="District of Saanich Maps")

    if boundary_source == "surrey_arcgis":
        return fetch_arcgis_boundary_feature(SURREY_BOUNDARY_LAYER, source="City of Surrey Open Data")

    if boundary_source == "richmond_bc_arcgis":
        return fetch_arcgis_boundary_feature(RICHMOND_BC_BOUNDARY_LAYER, source="City of Richmond Maps")

    return None


def load_city_boundary_geometry(city: str) -> dict[str, Any] | None:
    boundary_path = city_boundary_cache_path(city)
    special_boundary_source = CITY_BOUNDARY_HINTS.get(city, {}).get("boundary_source")

    if boundary_path.exists() and not special_boundary_source:
        feature = load_first_feature(boundary_path)
        if boundary_feature_matches_city(feature, city):
            geometry = feature.get("geometry")
            if not geometry:
                raise RuntimeError(f"No geometry found in boundary file: {boundary_path}")
            return geometry

    feature = fetch_special_city_boundary_feature(city) or fetch_city_boundary_feature(city)
    if not feature and boundary_path.exists():
        cached_feature = load_first_feature(boundary_path)
        if boundary_feature_matches_city(cached_feature, city):
            geometry = cached_feature.get("geometry")
            if not geometry:
                raise RuntimeError(f"No geometry found in boundary file: {boundary_path}")
            return geometry
    if not feature:
        return None

    ensure_dir(boundary_path.parent)
    boundary_path.write_text(
        json.dumps({"type": "FeatureCollection", "features": [feature]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return feature.get("geometry")


def normalize_redmond_ownership(raw_value: str | None) -> str:
    raw = (raw_value or "").strip().upper()
    if raw == "RED":
        return "City of Redmond"
    if raw == "PRV":
        return "Private"
    if raw == "UNK":
        return "Unknown"
    return raw_value or "Unknown"


def join_scientific_name(genus: str | None, species: str | None) -> str:
    parts = [part.strip() for part in [genus or "", species or ""] if part and part.strip()]
    return " ".join(parts).strip()


def generic_scientific_name_from_genus(genus: str | None) -> str:
    text = (genus or "").strip()
    if not text:
        return ""
    return f"{text} sp."


def title_case_if_upper(raw_value: str | None) -> str:
    text = (raw_value or "").strip()
    if not text:
        return ""

    letters = [character for character in text if character.isalpha()]
    if letters and all(character.isupper() for character in letters):
        return text.title().replace(" And ", " and ")
    return text


def arcgis_rings_to_geojson_geometry(rings: list[list[list[float]]]) -> dict[str, Any]:
    def signed_ring_area(ring: list[list[float]]) -> float:
        area = 0.0
        for point, next_point in zip(ring, ring[1:]):
            area += (point[0] * next_point[1]) - (next_point[0] * point[1])
        return area / 2.0

    def point_in_ring(point: list[float], ring: list[list[float]]) -> bool:
        x, y = point
        inside = False
        for point_a, point_b in zip(ring, ring[1:]):
            x1, y1 = point_a
            x2, y2 = point_b
            if (y1 > y) == (y2 > y):
                continue
            if y2 == y1:
                continue
            intersect_x = ((x2 - x1) * (y - y1) / (y2 - y1)) + x1
            if x < intersect_x:
                inside = not inside
        return inside

    normalized_rings: list[list[list[float]]] = []
    for ring in rings:
        coords = [list(map(float, point[:2])) for point in ring if len(point) >= 2]
        if len(coords) < 3:
            continue
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        if len(coords) >= 4:
            normalized_rings.append(coords)

    if not normalized_rings:
        raise RuntimeError("Official ArcGIS boundary geometry did not contain any polygon rings.")

    outers = [ring for ring in normalized_rings if signed_ring_area(ring) <= 0]
    holes = [ring for ring in normalized_rings if signed_ring_area(ring) > 0]
    if not outers:
        primary = max(normalized_rings, key=lambda ring: abs(signed_ring_area(ring)))
        outers = [primary]
        holes = [ring for ring in normalized_rings if ring is not primary]

    outers.sort(key=lambda ring: abs(signed_ring_area(ring)), reverse=True)
    polygons: list[list[list[list[float]]]] = [[outer] for outer in outers]

    for hole in holes:
        assigned = False
        hole_anchor = hole[0]
        for polygon in polygons:
            if point_in_ring(hole_anchor, polygon[0]):
                polygon.append(hole)
                assigned = True
                break
        if not assigned:
            polygons[0].append(hole)

    if len(polygons) == 1:
        return {"type": "Polygon", "coordinates": polygons[0]}
    return {"type": "MultiPolygon", "coordinates": polygons}


def build_species_guide() -> dict[str, Any]:
    now = dt.datetime.now(tz=dt.timezone.utc).isoformat()
    payload = json.loads(SPECIES_GUIDE_CONTENT_PATH.read_text(encoding="utf-8"))
    return {"updated_at": now, "entries": payload["entries"]}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_cached_source_features(city: str, source_dataset: str) -> list[dict[str, Any]]:
    tree_paths = sorted(PUBLIC_DATA_DIR.glob("trees.*.v2.geojson"))
    tree_paths.extend(sorted(PUBLIC_DATA_DIR.glob("trees.*.city.*.v1.geojson")))
    legacy_path = PUBLIC_DATA_DIR / "trees.v1.geojson"
    if legacy_path.exists():
        tree_paths.append(legacy_path)
    if not tree_paths:
        return []

    matched = []
    for trees_path in tree_paths:
        payload = json.loads(trees_path.read_text(encoding="utf-8"))
        features = payload.get("features", [])
        for feature in features:
            props = feature.get("properties", {})
            if props.get("city") == city and props.get("source_dataset") == source_dataset:
                matched.append(feature)
    return matched


def fetch_sammamish_layer_rows(uid: str, fac_id: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summary_payload = fetch_json(
        SAMMAMISH_SEARCH_ENDPOINT,
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

    rows_payload = fetch_json(
        SAMMAMISH_GRIDS_ENDPOINT,
        {
            "method": "getTreeKeeperGridOptions",
            "session_id": uid,
            "layer_id": fac_id,
            "gridType": "sites",
            "stopCache": int(time.time() * 1000),
        },
    )

    rows_raw = rows_payload.get("data", [])
    if isinstance(rows_raw, str):
        try:
            rows = json.loads(rows_raw)
        except Exception as exc:  # noqa: PERF203
            raise RuntimeError(f"Failed to parse Sammamish layer {fac_id} rows: {exc}") from exc
    elif isinstance(rows_raw, list):
        rows = rows_raw
    else:
        rows = []

    return summary_payload if isinstance(summary_payload, dict) else {}, rows


def fetch_everett_layer_rows(uid: str, fac_id: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    summary_payload = fetch_json(
        EVERETT_SEARCH_ENDPOINT,
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
            EVERETT_GRIDS_ENDPOINT,
            {
                "method": "getTreeKeeperGridOptionsData",
                "session_id": uid,
                "layer_id": fac_id,
                "gridType": "sites",
                "calls_search": "true",
                "limit": limit,
                "offset": offset,
                "stopCache": int(time.time() * 1000),
            },
            method="POST",
            body={"filters": "[]", "sorts": "[]"},
        )

        rows_raw = rows_payload.get("data", [])
        if isinstance(rows_raw, str):
            try:
                batch = json.loads(rows_raw)
            except Exception as exc:  # noqa: PERF203
                raise RuntimeError(f"Failed to parse Everett layer {fac_id} rows: {exc}") from exc
        elif isinstance(rows_raw, list):
            batch = rows_raw
        else:
            batch = []

        if not batch:
            break

        rows.extend(batch)
        if total_rows and len(rows) >= total_rows:
            break
        if len(batch) < limit:
            break
        offset += limit

    return summary_payload if isinstance(summary_payload, dict) else {}, rows


def post_form_with_curl(
    url: str,
    form_pairs: list[tuple[str, Any]],
    *,
    headers: dict[str, str] | None = None,
    cookie_path: str | None = None,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, 5):
        cmd = ["curl", "-sL", "--max-time", "120"]
        if cookie_path:
            cmd.extend(["-b", cookie_path, "-c", cookie_path])
        for key, value in (headers or {}).items():
            cmd.extend(["-H", f"{key}: {value}"])
        for key, value in form_pairs:
            cmd.extend(["--data-urlencode", f"{key}={value}"])
        cmd.append(url)

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            last_error = RuntimeError(f"curl failed ({result.returncode}): {result.stderr.strip()}")
            time.sleep(0.35 * attempt)
            continue

        payload = result.stdout.strip()
        if not payload:
            last_error = RuntimeError("curl returned empty payload")
            time.sleep(0.35 * attempt)
            continue

        try:
            return json.loads(payload)
        except Exception as exc:  # noqa: PERF203
            last_error = exc
            time.sleep(0.35 * attempt)

    raise RuntimeError(f"Failed to fetch valid form JSON for {url}: {last_error}")


def fetch_kirkland_rows(limit: int = 5000) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fields = {
        "pid": {"data_type": "integer", "input_type": "number"},
        "geom": {"data_type": "geometry", "input_type": "hidden"},
        "species_bo": {"data_type": "character varying", "input_type": "text"},
        "species_la": {"data_type": "character varying", "input_type": "text"},
    }

    with tempfile.NamedTemporaryFile(prefix="kirkland_tp_", suffix=".cookies", delete=False) as handle:
        cookie_path = handle.name

    try:
        session_result = subprocess.run(
            ["curl", "-sL", "-c", cookie_path, KIRKLAND_TREEPLOTTER_URL],
            capture_output=True,
            text=True,
            check=False,
        )
        if session_result.returncode != 0:
            raise RuntimeError(f"Failed to open Kirkland TreePlotter landing page: {session_result.stderr.strip()}")

        session_payload = post_form_with_curl(
            KIRKLAND_DB_ENDPOINT,
            [("action", "sessionCheck"), ("params[folder]", "KirklandWA")],
            headers={"X-Client-Version": KIRKLAND_CLIENT_VERSION},
            cookie_path=cookie_path,
        )
        if session_payload.get("status") != "OK":
            raise RuntimeError(f"Kirkland sessionCheck failed: {session_payload}")

        rows: list[dict[str, Any]] = []
        offset = 0
        total_rows = 0

        while True:
            form_pairs: list[tuple[str, Any]] = [
                ("action", "retrieveDataAlias"),
                ("params[folder]", "KirklandWA"),
                ("params[table]", "ref_trees"),
                ("params[firstIndex]", offset),
                ("params[limit]", limit),
                ("params[sortBy]", "pid"),
                ("params[sortOrder]", "asc"),
                ("params[timezoneOffset]", 0),
            ]
            for field_name, field_details in fields.items():
                form_pairs.extend(
                    [
                        (f"params[fields][{field_name}][data_type]", field_details["data_type"]),
                        (f"params[fields][{field_name}][input_type]", field_details["input_type"]),
                        (f"params[fields][{field_name}][name]", field_name),
                        (f"params[fields][{field_name}][referencer]", "ref_trees"),
                    ]
                )

            payload = post_form_with_curl(
                KIRKLAND_DB_ENDPOINT,
                form_pairs,
                headers={"X-Client-Version": KIRKLAND_CLIENT_VERSION},
                cookie_path=cookie_path,
            )
            if payload.get("status") != "OK":
                raise RuntimeError(f"Kirkland retrieveDataAlias failed at offset {offset}: {payload}")

            if not total_rows:
                total_rows = len(payload.get("returnPids") or [])

            batch = payload.get("resultsArray") or []
            if not batch:
                break

            rows.extend(batch)
            if len(batch) < limit:
                break

            offset += len(batch)
            if total_rows and offset >= total_rows:
                break

        return {"siteCount": total_rows or len(rows)}, rows
    finally:
        Path(cookie_path).unlink(missing_ok=True)


def main() -> int:
    ensure_dir(PUBLIC_DATA_DIR)
    ensure_dir(NORMALIZED_DIR)

    mapping_rows = load_mapping(MAPPING_PATH)
    subtype_rows = load_subtype_mapping(SUBTYPE_MAPPING_PATH)

    seattle_info = fetch_json(SEATTLE_LAYER, {"f": "pjson"})
    bellevue_info = fetch_json(BELLEVUE_LAYER, {"f": "pjson"})
    redmond_info = fetch_json(REDMOND_LAYER, {"f": "pjson"})
    kenmore_info = fetch_json(KENMORE_LAYER, {"f": "pjson"})
    seatac_info = fetch_json(SEATAC_LAYER, {"f": "pjson"})
    puyallup_info = fetch_json(PUYALLUP_LAYER, {"f": "pjson"})
    gig_harbor_info = fetch_json(GIG_HARBOR_LAYER, {"f": "pjson"})
    shoreline_info = fetch_json(SHORELINE_LAYER, {"f": "pjson"})
    snohomish_info = fetch_json(SNOHOMISH_LAYER, {"f": "pjson"})
    bellingham_info = fetch_json(BELLINGHAM_LAYER, {"f": "pjson"})
    spokane_info = fetch_json(SPOKANE_LAYER, {"f": "pjson"})
    yakima_info = fetch_json(YAKIMA_LAYER, {"f": "pjson"})
    walla_walla_info = fetch_json(WALLA_WALLA_LAYER, {"f": "pjson"})
    dc_info = fetch_json(DC_LAYER, {"f": "pjson"})
    portland_info = fetch_json(PORTLAND_LAYER, {"f": "pjson"})
    san_jose_info = fetch_json(SAN_JOSE_LAYER, {"f": "pjson"})
    san_francisco_info = fetch_json(SAN_FRANCISCO_METADATA)
    burlingame_info = fetch_json(BURLINGAME_LAYER, {"f": "pjson"})
    palo_alto_info = fetch_json(PALO_ALTO_TREES_LAYER, {"f": "pjson"})
    cupertino_info = fetch_json(CUPERTINO_TREES_LAYER, {"f": "pjson"})
    oakland_info = fetch_json(OAKLAND_METADATA)
    berkeley_info = fetch_json(
        "https://www.arcgis.com/sharing/rest/content/items/88829f4ae7254b5280732e88e65e6df5",
        {"f": "json"},
    )
    vancouver_bc_info = fetch_json(VANCOUVER_BC_DATASET)
    victoria_info = fetch_json(VICTORIA_PARK_TREES_ITEM, {"f": "json"})

    seattle_last_edit = iso_from_epoch(seattle_info.get("editingInfo", {}).get("lastEditDate"))
    bellevue_last_edit = iso_from_epoch(bellevue_info.get("editingInfo", {}).get("lastEditDate"))
    redmond_last_edit = iso_from_epoch(redmond_info.get("editingInfo", {}).get("lastEditDate"))
    kenmore_last_edit = iso_from_epoch(kenmore_info.get("editingInfo", {}).get("lastEditDate"))
    seatac_last_edit = iso_from_epoch(seatac_info.get("editingInfo", {}).get("lastEditDate"))
    puyallup_last_edit = iso_from_epoch(puyallup_info.get("editingInfo", {}).get("lastEditDate"))
    gig_harbor_last_edit = iso_from_epoch(gig_harbor_info.get("editingInfo", {}).get("lastEditDate"))
    shoreline_last_edit = iso_from_epoch(shoreline_info.get("editingInfo", {}).get("lastEditDate"))
    snohomish_last_edit = iso_from_epoch(snohomish_info.get("editingInfo", {}).get("lastEditDate"))
    bellingham_last_edit = iso_from_epoch(bellingham_info.get("editingInfo", {}).get("lastEditDate"))
    spokane_last_edit = iso_from_epoch(spokane_info.get("editingInfo", {}).get("lastEditDate"))
    yakima_last_edit = iso_from_epoch(yakima_info.get("editingInfo", {}).get("lastEditDate"))
    walla_walla_last_edit = iso_from_epoch(walla_walla_info.get("editingInfo", {}).get("lastEditDate"))
    dc_last_edit = iso_from_epoch(dc_info.get("editingInfo", {}).get("lastEditDate"))
    portland_last_edit = iso_from_epoch(portland_info.get("editingInfo", {}).get("lastEditDate"))
    san_jose_last_edit = iso_from_epoch(san_jose_info.get("editingInfo", {}).get("lastEditDate"))
    san_francisco_last_edit = iso_from_epoch(san_francisco_info.get("rowsUpdatedAt"))
    burlingame_last_edit = iso_from_epoch(burlingame_info.get("editingInfo", {}).get("lastEditDate"))
    palo_alto_last_edit = iso_from_epoch(palo_alto_info.get("editingInfo", {}).get("lastEditDate"))
    berkeley_last_edit = iso_from_epoch(berkeley_info.get("modified"))
    cupertino_last_edit = iso_from_epoch(cupertino_info.get("editingInfo", {}).get("lastEditDate"))
    oakland_last_edit = iso_from_epoch(oakland_info.get("rowsUpdatedAt"))
    vancouver_bc_last_edit = vancouver_bc_info.get("metas", {}).get("default", {}).get("modified") or ""
    victoria_last_edit = iso_from_epoch(victoria_info.get("modified"))
    everett_last_edit = ""
    kirkland_last_edit = ""

    renton_last_edit = ""
    renton_source_error = ""
    try:
        renton_info = fetch_json(RENTON_LAYER, {"f": "pjson"})
        renton_last_edit = iso_from_epoch(renton_info.get("editingInfo", {}).get("lastEditDate"))
    except Exception as exc:
        renton_source_error = str(exc)

    seattle_features = fetch_all_features(
        layer_url=SEATTLE_LAYER,
        where="SCIENTIFIC_NAME LIKE 'Prunus%' OR SCIENTIFIC_NAME LIKE 'Magnolia%' OR SCIENTIFIC_NAME LIKE 'Malus%'",
        out_fields=["OBJECTID", "SCIENTIFIC_NAME", "COMMON_NAME", "OWNERSHIP", "SOURCE_DEPT"],
        order_by_field="OBJECTID",
    )

    bellevue_features = fetch_all_features(
        layer_url=BELLEVUE_LAYER,
        where="SpeciesDesc LIKE 'Prunus%' OR SpeciesDesc LIKE 'Magnolia%' OR SpeciesDesc LIKE 'Malus%'",
        out_fields=["CityTreeID", "SpeciesDesc", "Management", "TreeStatus"],
        order_by_field="CityTreeID",
    )

    redmond_features = fetch_all_features(
        layer_url=REDMOND_LAYER,
        where="GenusSpecies LIKE 'Prunus%' OR GenusSpecies LIKE 'Magnolia%' OR GenusSpecies LIKE 'Malus%'",
        out_fields=["OBJECTID", "AssetID", "GenusSpecies", "CommonName", "d_Ownership", "NAME"],
        order_by_field="OBJECTID",
    )

    renton_features: list[dict[str, Any]] = []
    if not renton_source_error:
        try:
            renton_features = fetch_all_features(
                layer_url=RENTON_LAYER,
                where="GENUS IN ('Prunus', 'Magnolia', 'Malus')",
                out_fields=["OBJECTID", "GENUS", "SPECIES", "COMMONNAME", "OWNEDBY", "MAINTAINEDBY"],
                order_by_field="OBJECTID",
            )
        except Exception as exc:
            renton_source_error = str(exc)

    kenmore_features = fetch_all_features(
        layer_url=KENMORE_LAYER,
        where="SciName LIKE 'Prunus%' OR SciName LIKE 'Magnolia%' OR SciName LIKE 'Malus%'",
        out_fields=["OBJECTID", "SciName", "CommonName", "MaintBy"],
        order_by_field="OBJECTID",
    )

    seatac_features = fetch_all_features(
        layer_url=SEATAC_LAYER,
        where="GenusType LIKE 'Prunus%' OR GenusType LIKE 'Magnolia%' OR GenusType LIKE 'Malus%'",
        out_fields=["OBJECTID", "AssetID", "CommonName", "GenusType", "SpeciesType", "OwnedBy", "ManagedBy"],
        order_by_field="OBJECTID",
    )

    puyallup_features = fetch_all_features(
        layer_url=PUYALLUP_LAYER,
        where=(
            "SCIENTIFIC LIKE 'Prunus%' OR SCIENTIFIC LIKE 'Magnolia%' OR SCIENTIFIC LIKE 'Malus%' "
            "OR COMMON_NAM LIKE '%cherry%' OR COMMON_NAM LIKE '%plum%' OR COMMON_NAM LIKE '%peach%' "
            "OR COMMON_NAM LIKE '%magnolia%' OR COMMON_NAM LIKE '%crabapple%'"
        ),
        out_fields=["FID", "TREE_ID", "COMMON_NAM", "SCIENTIFIC", "CONDITION", "STATUS"],
        order_by_field="FID",
    )

    gig_harbor_features = fetch_all_features(
        layer_url=GIG_HARBOR_LAYER,
        where="Latin_Name LIKE 'Prunus%' OR Latin_Name LIKE 'Magnolia%' OR Latin_Name LIKE 'Malus%'",
        out_fields=["OBJECTID", "Primary_ID", "Latin_Name"],
        order_by_field="OBJECTID",
    )

    shoreline_features = fetch_all_features(
        layer_url=SHORELINE_LAYER,
        where="Scientific_Nm LIKE 'Prunus%' OR Scientific_Nm LIKE 'Magnolia%' OR Scientific_Nm LIKE 'Malus%'",
        out_fields=[
            "OBJECTID",
            "AssetID",
            "Scientific_Nm",
            "Common_Nm",
            "Location",
            "Jurisdiction",
            "created_date",
            "last_edited_date",
        ],
        order_by_field="OBJECTID",
    )

    snohomish_features = fetch_all_features(
        layer_url=SNOHOMISH_LAYER,
        where="BotanicalN LIKE 'Prunus%' OR BotanicalN LIKE 'Magnolia%' OR BotanicalN LIKE 'Malus%'",
        out_fields=[
            "OBJECTID_1",
            "BotanicalN",
            "CommonName",
            "Location_L",
            "ROW",
            "Zone",
            "last_edi_1",
        ],
        order_by_field="OBJECTID_1",
    )

    bellingham_features = fetch_all_features(
        layer_url=BELLINGHAM_LAYER,
        where="ScientificName LIKE 'Prunus%' OR ScientificName LIKE 'Magnolia%' OR ScientificName LIKE 'Malus%'",
        out_fields=[
            "OBJECTID",
            "CommonName",
            "ScientificName",
            "Ownership",
            "MaintainedBy",
            "Source",
            "InstallDate",
        ],
        order_by_field="OBJECTID",
    )

    spokane_features = fetch_all_features(
        layer_url=SPOKANE_LAYER,
        where="Genus IN ('Prunus', 'Malus', 'Magnolia')",
        out_fields=[
            "OBJECTID",
            "park",
            "species",
            "CommonName",
            "Genus",
            "TreeType",
            "UpdatedDT",
        ],
        order_by_field="OBJECTID",
    )

    yakima_features = fetch_all_features(
        layer_url=YAKIMA_LAYER,
        where=(
            "GENUS IN ('Prunus', 'Magnolia', 'Malus') "
            "OR NAME LIKE '%Cherry%' OR NAME LIKE '%Plum%' OR NAME LIKE '%Peach%' "
            "OR NAME LIKE '%Magnolia%' OR NAME LIKE '%Crabapple%' OR NAME LIKE '%Crab Apple%'"
        ),
        out_fields=[
            "OBJECTID",
            "NAME",
            "GENUS",
            "SPECIES",
            "OWNEDBY",
            "MAINTBY",
            "CONDITION",
            "last_edited_date",
        ],
        order_by_field="OBJECTID",
    )

    walla_walla_features = fetch_all_features(
        layer_url=WALLA_WALLA_LAYER,
        where=(
            "Botanical LIKE 'Prunus%' OR Botanical LIKE 'Magnolia%' OR Botanical LIKE 'Malus%' "
            "OR Common LIKE '%Cherry%' OR Common LIKE '%Plum%' OR Common LIKE '%Peach%' "
            "OR Common LIKE '%Magnolia%' OR Common LIKE '%Crabapple%' OR Common LIKE '%Crab Apple%'"
        ),
        out_fields=[
            "OBJECTID",
            "Common",
            "Botanical",
            "Property",
            "Status",
            "Last_Edited_On",
        ],
        order_by_field="OBJECTID",
    )

    portland_features = fetch_all_features(
        layer_url=PORTLAND_LAYER,
        where="SPECIES LIKE 'Prunus%' OR SPECIES LIKE 'Magnolia%' OR SPECIES LIKE 'Malus%'",
        out_fields=["OBJECTID", "SPECIES", "Neighborhood", "Address", "Date_Inventoried", "Site_Type"],
        order_by_field="OBJECTID",
    )
    portland_total = int(
        fetch_json(
            f"{PORTLAND_LAYER}/query",
            {"where": "OBJECTID > 0", "returnCountOnly": "true", "f": "json"},
        ).get("count")
        or len(portland_features)
    )

    sammamish_street_summary, sammamish_street_rows = fetch_sammamish_layer_rows(uid="pinkhunter-sammamish-street", fac_id=1)
    sammamish_park_summary, sammamish_park_rows = fetch_sammamish_layer_rows(uid="pinkhunter-sammamish-park", fac_id=2)
    sammamish_street_total = int(sammamish_street_summary.get("siteCount") or len(sammamish_street_rows))
    sammamish_park_total = int(sammamish_park_summary.get("siteCount") or len(sammamish_park_rows))

    everett_park_summary, everett_park_rows = fetch_everett_layer_rows(uid="pinkhunter-everett-park", fac_id=1)
    everett_park_total = int(everett_park_summary.get("siteCount") or len(everett_park_rows))
    kirkland_summary, kirkland_rows = fetch_kirkland_rows()
    kirkland_total = int(kirkland_summary.get("siteCount") or len(kirkland_rows))

    dc_features = fetch_all_features(
        layer_url=DC_LAYER,
        where="SCI_NM LIKE 'Prunus%' OR SCI_NM LIKE 'Magnolia%' OR SCI_NM LIKE 'Malus%'",
        out_fields=["OBJECTID", "SCI_NM", "CMMN_NM", "OWNERSHIP", "FACILITYID", "WARD"],
        order_by_field="OBJECTID",
    )

    san_jose_features = fetch_all_features(
        layer_url=SAN_JOSE_LAYER,
        where="NAMESCIENTIFIC LIKE 'Prunus%' OR NAMESCIENTIFIC LIKE 'Magnolia%' OR NAMESCIENTIFIC LIKE 'Malus%'",
        out_fields=["OBJECTID", "NAMESCIENTIFIC", "ADDRESSNUM", "STREETNAME", "OWNEDBY", "MAINTBY", "LASTUPDATE"],
        order_by_field="OBJECTID",
    )
    san_jose_total = int(
        fetch_json(
            f"{SAN_JOSE_LAYER}/query",
            {"where": "OBJECTID > 0", "returnCountOnly": "true", "f": "json"},
        ).get("count")
        or len(san_jose_features)
    )

    san_francisco_where = (
        "planttype='Tree' AND (qspecies like 'Prunus%' OR qspecies like 'Magnolia%' OR qspecies like 'Malus%')"
    )
    san_francisco_features = fetch_soda_rows(
        SAN_FRANCISCO_DATASET,
        where=san_francisco_where,
        order="treeid",
    )
    san_francisco_total = fetch_soda_count(
        SAN_FRANCISCO_DATASET,
        where="planttype='Tree'",
    )

    burlingame_features = fetch_all_features(
        layer_url=BURLINGAME_LAYER,
        where="BotanicalName LIKE 'Prunus%' OR BotanicalName LIKE 'Magnolia%' OR BotanicalName LIKE 'Malus%'",
        out_fields=["OBJECTID_1", "Tree_ID", "Species_Name", "CommonName", "BotanicalName", "Address", "Street", "OnStreet"],
        order_by_field="OBJECTID_1",
    )
    burlingame_total = int(
        fetch_json(
            f"{BURLINGAME_LAYER}/query",
            {"where": "OBJECTID_1 > 0", "returnCountOnly": "true", "f": "json"},
        ).get("count")
        or len(burlingame_features)
    )

    palo_alto_features = fetch_all_features(
        layer_url=PALO_ALTO_TREES_LAYER,
        where="SPECIES LIKE 'Prunus%' OR SPECIES LIKE 'Magnolia%' OR SPECIES LIKE 'Malus%'",
        out_fields=[
            "OBJECTID",
            "TREEID",
            "SPECIES",
            "PRIVATE",
            "JURISDICTION",
            "ONSTREET",
            "ADDRESSNUMBER",
            "MODIFIEDDATE",
        ],
        order_by_field="OBJECTID",
    )
    palo_alto_total = int(
        fetch_json(
            f"{PALO_ALTO_TREES_LAYER}/query",
            {"where": "OBJECTID > 0", "returnCountOnly": "true", "f": "json"},
        ).get("count")
        or len(palo_alto_features)
    )

    berkeley_rows = load_zipped_point_shapefile_rows(BERKELEY_TREES_ZIP)
    berkeley_total = len(berkeley_rows)

    cupertino_features = fetch_all_features(
        layer_url=CUPERTINO_TREES_LAYER,
        where="Species LIKE 'Prunus%' OR Species LIKE 'Magnolia%' OR Species LIKE 'Malus%'",
        out_fields=[
            "OBJECTID",
            "AssetID",
            "Species",
            "SpeciesCommonName",
            "OwnedBy",
            "MaintainedBy",
            "Status",
            "Neighborhood",
            "last_edited_date",
        ],
        order_by_field="OBJECTID",
    )
    cupertino_total = int(
        fetch_json(
            f"{CUPERTINO_TREES_LAYER}/query",
            {"where": "OBJECTID > 0", "returnCountOnly": "true", "f": "json"},
        ).get("count")
        or len(cupertino_features)
    )

    oakland_features = fetch_soda_rows(
        OAKLAND_TREES_DATASET,
        where="species like 'Prunus%' or species like 'Magnolia%' or species like 'Malus%'",
        order="objectid",
    )
    oakland_total = fetch_soda_count(OAKLAND_TREES_DATASET)

    vancouver_bc_features = fetch_ods_export_rows(
        VANCOUVER_BC_DATASET,
        where='genus_name in ("PRUNUS","MALUS","MAGNOLIA")',
    )

    victoria_features = fetch_all_features(
        layer_url=VICTORIA_PARK_TREES_LAYER,
        where="BotanicalName LIKE 'Prunus%' OR BotanicalName LIKE 'Magnolia%' OR BotanicalName LIKE 'Malus%'",
        out_fields=["OBJECTID", "BotanicalName", "CommonName", "Species", "TreeCategory", "Parks"],
        order_by_field="OBJECTID",
    )

    zip_payload = fetch_json(
        f"{ZIP_LAYER}/query",
        {
            "where": "1=1",
            "outFields": "ZIPCODE,COUNTY_NAME,PREFERRED_CITY",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        },
    )
    zip_index = build_zip_index(zip_payload.get("features", []))

    dc_zip_index: list[dict[str, Any]] = []
    dc_boundary_geometry = load_city_boundary_geometry("Washington DC")
    if dc_boundary_geometry:
        dc_min_lon, dc_min_lat, dc_max_lon, dc_max_lat = geometry_bbox(dc_boundary_geometry)
        dc_zip_payload = fetch_json(
            f"{US_CENSUS_ZCTA_LAYER}/query",
            {
                "where": "1=1",
                "geometry": f"{dc_min_lon},{dc_min_lat},{dc_max_lon},{dc_max_lat}",
                "geometryType": "esriGeometryEnvelope",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "GEOID,NAME",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "geojson",
            },
        )
        dc_zip_index = build_zip_index(dc_zip_payload.get("features", []), code_fields=("GEOID", "NAME"))

    portland_zip_index = fetch_us_city_zip_index("Portland")
    san_jose_zip_index = fetch_us_city_zip_index("San Jose")
    san_francisco_zip_index = fetch_us_city_zip_index("San Francisco")
    burlingame_zip_index = fetch_us_city_zip_index("Burlingame")
    palo_alto_zip_index = fetch_us_city_zip_index("Palo Alto")
    berkeley_zip_index = fetch_us_city_zip_index("Berkeley")
    cupertino_zip_index = fetch_us_city_zip_index("Cupertino")
    oakland_zip_index = fetch_us_city_zip_index("Oakland")

    uw_supplemental_payload = json.loads(UW_SUPPLEMENTAL_PATH.read_text(encoding="utf-8"))
    uw_supplemental_elements = uw_supplemental_payload.get("elements", [])

    output_features: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    unknown_counter: Counter[str] = Counter()

    for feature in seattle_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("SCIENTIFIC_NAME") or "").strip()
        common_name = attrs.get("COMMON_NAME")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = (attrs.get("OWNERSHIP") or "Unknown").strip() or "Unknown"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), portland_zip_index or zip_index)

        normalized_rows.append(
            {
                "id": f"seattle-{attrs.get('OBJECTID')}",
                "city": "Seattle",
                "source_dataset": "Combined Tree Point",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"seattle-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Seattle",
                    "source_dataset": "Combined Tree Point",
                    "source_department": attrs.get("SOURCE_DEPT") or "City of Seattle",
                    "source_last_edit_at": seattle_last_edit,
                },
            }
        )

    for feature in bellevue_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        species_desc = attrs.get("SpeciesDesc") or ""
        scientific_raw, common_name = parse_bellevue_species(species_desc)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        management = (attrs.get("Management") or "City of Bellevue").strip() or "City of Bellevue"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), portland_zip_index or zip_index)

        normalized_rows.append(
            {
                "id": f"bellevue-{attrs.get('CityTreeID')}",
                "city": "Bellevue",
                "source_dataset": "City Trees",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": zip_code or "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(management),
                "ownership_raw": management,
                "lat": geom.get("y"),
                "lon": geom.get("x"),
                "included": "1" if species_group else "0",
            }
        )

        if not species_group:
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"bellevue-{attrs.get('CityTreeID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(management),
                    "ownership_raw": management,
                    "city": "Bellevue",
                    "source_dataset": "City Trees",
                    "source_department": "City of Bellevue",
                    "source_last_edit_at": bellevue_last_edit,
                },
            }
        )

    for feature in redmond_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("GenusSpecies") or "").strip()
        common_name = attrs.get("CommonName")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = normalize_redmond_ownership(attrs.get("d_Ownership"))
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"redmond-{attrs.get('OBJECTID')}",
                "city": "Redmond",
                "source_dataset": "TreeSite",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"redmond-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Redmond",
                    "source_dataset": "TreeSite",
                    "source_department": "City of Redmond",
                    "source_last_edit_at": redmond_last_edit,
                },
            }
        )

    if renton_features:
        for feature in renton_features:
            attrs = feature.get("attributes", {})
            geom = feature.get("geometry", {})
            scientific_raw = join_scientific_name(attrs.get("GENUS"), attrs.get("SPECIES"))
            common_name = attrs.get("COMMONNAME")
            scientific_normalized = normalize_scientific_name(scientific_raw)
            species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

            ownership_raw = (attrs.get("OWNEDBY") or attrs.get("MAINTAINEDBY") or "City of Renton").strip()
            zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

            normalized_rows.append(
                {
                    "id": f"renton-{attrs.get('OBJECTID')}",
                    "city": "Renton",
                    "source_dataset": "Tree Sites",
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
                if scientific_normalized:
                    unknown_counter[scientific_normalized] += 1
                continue

            output_features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                    "properties": {
                        "id": f"renton-{attrs.get('OBJECTID')}",
                        "species_group": species_group,
                        "scientific_name": scientific_raw,
                        "common_name": common_name,
                        "subtype_name": subtype_name,
                        "zip_code": zip_code,
                        "ownership": canonical_ownership(ownership_raw),
                        "ownership_raw": ownership_raw,
                        "city": "Renton",
                        "source_dataset": "Tree Sites",
                        "source_department": "City of Renton",
                        "source_last_edit_at": renton_last_edit,
                    },
                }
            )
    elif renton_source_error:
        cached_renton_features = load_cached_source_features(city="Renton", source_dataset="Tree Sites")
        for cached in cached_renton_features:
            props = cached.get("properties", {})
            geometry = cached.get("geometry", {})
            coordinates = geometry.get("coordinates", [None, None])
            scientific_raw = props.get("scientific_name") or ""
            common_name = props.get("common_name")
            species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
            if not species_group:
                species_group = props.get("species_group")
            if not subtype_name:
                subtype_name = props.get("subtype_name")

            output_features.append(
                {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        **props,
                        "species_group": species_group,
                        "subtype_name": subtype_name,
                    },
                }
            )
            normalized_rows.append(
                {
                    "id": props.get("id", ""),
                    "city": "Renton",
                    "source_dataset": "Tree Sites",
                    "scientific_raw": scientific_raw,
                    "scientific_normalized": normalize_scientific_name(scientific_raw),
                    "common_name": common_name or "",
                    "subtype_name": subtype_name or "",
                    "zip_code": props.get("zip_code") or "",
                    "species_group": species_group or "",
                    "ownership": props.get("ownership") or "unknown",
                    "ownership_raw": props.get("ownership_raw") or "",
                    "lat": coordinates[1],
                    "lon": coordinates[0],
                    "included": "1" if species_group else "0",
                }
            )

    for feature in kenmore_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("SciName") or "").strip()
        common_name = attrs.get("CommonName")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = (attrs.get("MaintBy") or "City of Kenmore").strip()
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"kenmore-{attrs.get('OBJECTID')}",
                "city": "Kenmore",
                "source_dataset": "Public Trees",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"kenmore-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Kenmore",
                    "source_dataset": "Public Trees",
                    "source_department": "City of Kenmore",
                    "source_last_edit_at": kenmore_last_edit,
                },
            }
        )

    for feature in seatac_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = join_scientific_name(attrs.get("GenusType"), attrs.get("SpeciesType"))
        common_name = attrs.get("CommonName")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = (attrs.get("OwnedBy") or attrs.get("ManagedBy") or "City of SeaTac").strip()
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"seatac-{attrs.get('OBJECTID')}",
                "city": "SeaTac",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"seatac-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "SeaTac",
                    "source_dataset": "Trees",
                    "source_department": "City of SeaTac",
                    "source_last_edit_at": seatac_last_edit,
                },
            }
        )

    for feature in puyallup_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("SCIENTIFIC") or "").strip()
        common_name = attrs.get("COMMON_NAM")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = "City of Puyallup"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"puyallup-{attrs.get('FID')}",
                "city": "Puyallup",
                "source_dataset": "City Maintained Street Trees",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"puyallup-{attrs.get('FID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Puyallup",
                    "source_dataset": "City Maintained Street Trees",
                    "source_department": "City of Puyallup",
                    "source_last_edit_at": puyallup_last_edit,
                },
            }
        )

    for feature in gig_harbor_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("Latin_Name") or "").strip()
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, None, mapping_rows, subtype_rows)

        ownership_raw = "City of Gig Harbor"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"gigharbor-{attrs.get('OBJECTID')}",
                "city": "Gig Harbor",
                "source_dataset": "PW Trees Public Viewer",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"gigharbor-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Gig Harbor",
                    "source_dataset": "PW Trees Public Viewer",
                    "source_department": "City of Gig Harbor",
                    "source_last_edit_at": gig_harbor_last_edit,
                },
            }
        )

    for fac_id, rows, source_dataset in [
        (1, sammamish_street_rows, "TreeKeeper Street Sites"),
        (2, sammamish_park_rows, "TreeKeeper Park Sites"),
    ]:
        for row in rows:
            scientific_raw, parsed_common_name = parse_sammamish_species(row.get("SITE_ATTR1"))
            common_name = parsed_common_name or row.get("SITE_ATTR1")
            scientific_normalized = normalize_scientific_name(scientific_raw)
            species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

            lon = row.get("LONGITUDE")
            lat = row.get("LATITUDE")
            if lon is None or lat is None:
                geometry_text = row.get("SITE_GEOMETRY")
                if geometry_text:
                    try:
                        parsed_geometry = json.loads(geometry_text)
                        coords = parsed_geometry.get("coordinates") or [None, None]
                        lon = coords[0]
                        lat = coords[1]
                    except Exception:
                        lon, lat = None, None
            if lon is None or lat is None:
                continue
            zip_code = assign_zip_code(lon, lat, zip_index)
            ownership_raw = "City of Sammamish"

            normalized_rows.append(
                {
                    "id": f"sammamish-{fac_id}-{row.get('SITE_ID')}",
                    "city": "Sammamish",
                    "source_dataset": source_dataset,
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
                if scientific_normalized:
                    unknown_counter[scientific_normalized] += 1
                continue

            output_features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": {
                        "id": f"sammamish-{fac_id}-{row.get('SITE_ID')}",
                        "species_group": species_group,
                        "scientific_name": scientific_raw,
                        "common_name": common_name,
                        "subtype_name": subtype_name,
                        "zip_code": zip_code,
                        "ownership": canonical_ownership(ownership_raw),
                        "ownership_raw": ownership_raw,
                        "city": "Sammamish",
                        "source_dataset": source_dataset,
                        "source_department": "City of Sammamish",
                        "source_last_edit_at": "",
                    },
                }
            )

    for feature in shoreline_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("Scientific_Nm") or "").strip()
        common_name = attrs.get("Common_Nm")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = (attrs.get("Jurisdiction") or "City of Shoreline").strip() or "City of Shoreline"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"shoreline-{attrs.get('OBJECTID')}",
                "city": "Shoreline",
                "source_dataset": "Public Tree Inventory",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"shoreline-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Shoreline",
                    "source_dataset": "Public Tree Inventory",
                    "source_department": "City of Shoreline",
                    "source_last_edit_at": shoreline_last_edit,
                },
            }
        )

    for feature in snohomish_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("BotanicalN") or "").strip()
        common_name = attrs.get("CommonName")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        row_flag = (attrs.get("ROW") or "").strip().lower()
        location_raw = (attrs.get("Location_L") or "").strip()
        ownership_raw = "City of Snohomish Right-of-Way" if row_flag == "yes" else (location_raw or "City of Snohomish")
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"snohomish-{attrs.get('OBJECTID_1')}",
                "city": "Snohomish",
                "source_dataset": "Snohomish Tree Inventory",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"snohomish-{attrs.get('OBJECTID_1')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Snohomish",
                    "source_dataset": "Snohomish Tree Inventory",
                    "source_department": "City of Snohomish",
                    "source_last_edit_at": snohomish_last_edit,
                },
            }
        )

    for feature in bellingham_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("ScientificName") or "").strip()
        common_name = attrs.get("CommonName")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = (attrs.get("Ownership") or attrs.get("MaintainedBy") or "City of Bellingham").strip()
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"bellingham-{attrs.get('OBJECTID')}",
                "city": "Bellingham",
                "source_dataset": "Bellingham Trees",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"bellingham-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Bellingham",
                    "source_dataset": "Bellingham Trees",
                    "source_department": "City of Bellingham",
                    "source_last_edit_at": bellingham_last_edit,
                },
            }
        )

    for feature in spokane_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        common_label = (attrs.get("CommonName") or "").strip()
        species_label = (attrs.get("species") or "").strip()
        common_name = common_label if common_label and common_label.lower() != "unknown" else (species_label or None)
        scientific_raw = generic_scientific_name_from_genus(attrs.get("Genus"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = "City of Spokane Parks Department"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"spokane-{attrs.get('OBJECTID')}",
                "city": "Spokane",
                "source_dataset": "Spokane Tree Inventory",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"spokane-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Spokane",
                    "source_dataset": "Spokane Tree Inventory",
                    "source_department": "City of Spokane Parks Department",
                    "source_last_edit_at": spokane_last_edit,
                },
            }
        )

    for feature in yakima_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        common_name = (attrs.get("NAME") or "").strip() or None
        scientific_raw = join_scientific_name(attrs.get("GENUS"), attrs.get("SPECIES"))
        if not scientific_raw:
            scientific_raw = generic_scientific_name_for_common_hint(common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = normalize_yakima_ownership(attrs.get("OWNEDBY"), attrs.get("MAINTBY"))
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"yakima-{attrs.get('OBJECTID')}",
                "city": "Yakima",
                "source_dataset": "Yakima Trees",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"yakima-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Yakima",
                    "source_dataset": "Yakima Trees",
                    "source_department": "City of Yakima GIS",
                    "source_last_edit_at": yakima_last_edit,
                },
            }
        )

    for feature in walla_walla_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        common_name = (attrs.get("Common") or "").strip() or None
        scientific_raw = (attrs.get("Botanical") or "").strip()
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = (attrs.get("Property") or "City of Walla Walla").strip() or "City of Walla Walla"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"wallawalla-{attrs.get('OBJECTID')}",
                "city": "Walla Walla",
                "source_dataset": "City of Walla Walla Trees",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"wallawalla-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Walla Walla",
                    "source_dataset": "City of Walla Walla Trees",
                    "source_department": "City of Walla Walla",
                    "source_last_edit_at": walla_walla_last_edit,
                },
            }
        )

    for feature in portland_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw, parsed_common_name = parse_bellevue_species(attrs.get("SPECIES"))
        common_name = parsed_common_name
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = "City of Portland"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), zip_index)

        normalized_rows.append(
            {
                "id": f"portland-{attrs.get('OBJECTID')}",
                "city": "Portland",
                "source_dataset": "Street Tree Inventory - Active Records",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"portland-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Portland",
                    "source_dataset": "Street Tree Inventory - Active Records",
                    "source_department": "City of Portland Urban Forestry",
                    "source_last_edit_at": portland_last_edit,
                },
            }
        )

    for feature in san_jose_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("NAMESCIENTIFIC") or "").strip()
        common_name = None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        owned_by = (attrs.get("OWNEDBY") or "").strip()
        maintained_by = (attrs.get("MAINTBY") or "").strip()
        if owned_by and maintained_by and owned_by != maintained_by:
            ownership_raw = f"{owned_by} / managed by {maintained_by}"
        else:
            ownership_raw = owned_by or maintained_by or "City of San Jose"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), san_jose_zip_index)

        normalized_rows.append(
            {
                "id": f"san-jose-{attrs.get('OBJECTID')}",
                "city": "San Jose",
                "source_dataset": "Street Tree",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"san-jose-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "San Jose",
                    "source_dataset": "Street Tree",
                    "source_department": "City of San Jose",
                    "source_last_edit_at": san_jose_last_edit,
                },
            }
        )

    for row in san_francisco_features:
        scientific_raw, common_name = parse_san_francisco_species(row.get("qspecies"))
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        lon_raw = row.get("longitude")
        lat_raw = row.get("latitude")
        if lon_raw in (None, "") or lat_raw in (None, ""):
            continue
        lon = float(lon_raw)
        lat = float(lat_raw)

        ownership_raw = (row.get("qcaretaker") or row.get("qlegalstatus") or "San Francisco Public Works").strip()
        zip_code = assign_zip_code(lon, lat, san_francisco_zip_index)

        normalized_rows.append(
            {
                "id": f"san-francisco-{row.get('treeid')}",
                "city": "San Francisco",
                "source_dataset": "Street Tree List",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": f"san-francisco-{row.get('treeid')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "San Francisco",
                    "source_dataset": "Street Tree List",
                    "source_department": "San Francisco Public Works",
                    "source_last_edit_at": san_francisco_last_edit,
                },
            }
        )

    for feature in burlingame_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("BotanicalName") or attrs.get("Species_Name") or "").strip()
        common_name = title_case_if_upper(attrs.get("CommonName")) or None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = "City of Burlingame"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), burlingame_zip_index)
        feature_suffix = attrs.get("Tree_ID") or attrs.get("OBJECTID_1")

        normalized_rows.append(
            {
                "id": f"burlingame-{feature_suffix}",
                "city": "Burlingame",
                "source_dataset": "City Street Tree Inventory",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"burlingame-{feature_suffix}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Burlingame",
                    "source_dataset": "City Street Tree Inventory",
                    "source_department": "City of Burlingame",
                    "source_last_edit_at": burlingame_last_edit,
                },
            }
        )

    for feature in palo_alto_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("SPECIES") or "").strip()
        common_name = None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        if int(attrs.get("PRIVATE") or 0) == 1:
            ownership_raw = "Private"
        else:
            ownership_raw = title_case_if_upper(attrs.get("JURISDICTION")) or "City of Palo Alto"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), palo_alto_zip_index)
        feature_suffix = attrs.get("TREEID") or attrs.get("OBJECTID")

        normalized_rows.append(
            {
                "id": f"palo-alto-{feature_suffix}",
                "city": "Palo Alto",
                "source_dataset": "Tree Data",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"palo-alto-{feature_suffix}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Palo Alto",
                    "source_dataset": "Tree Data",
                    "source_department": "City of Palo Alto",
                    "source_last_edit_at": palo_alto_last_edit,
                },
            }
        )

    for row in berkeley_rows:
        attrs = row.get("attributes", {})
        geom = row.get("geometry", {})
        common_name = title_case_if_upper(attrs.get("NAME")) or None
        scientific_raw = expand_abbreviated_botanical_name((attrs.get("SPECIES") or "").strip(), common_name)
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        owned_by = title_case_if_upper(attrs.get("OWNEDBY"))
        maintained_by = title_case_if_upper(attrs.get("MAINTBY"))
        if owned_by and maintained_by and owned_by != maintained_by:
            ownership_raw = f"{owned_by} / maintained by {maintained_by}"
        else:
            ownership_raw = owned_by or maintained_by or "City of Berkeley"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), berkeley_zip_index)
        feature_suffix = attrs.get("FACILITYID") or attrs.get("OBJECTID")

        normalized_rows.append(
            {
                "id": f"berkeley-{feature_suffix}",
                "city": "Berkeley",
                "source_dataset": "Tree_Berkeley20191107",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"berkeley-{feature_suffix}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Berkeley",
                    "source_dataset": "Tree_Berkeley20191107",
                    "source_department": "City of Berkeley",
                    "source_last_edit_at": berkeley_last_edit,
                },
            }
        )

    for feature in cupertino_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("Species") or "").strip()
        common_name = title_case_if_upper(attrs.get("SpeciesCommonName")) or None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        owned_by = title_case_if_upper(attrs.get("OwnedBy"))
        maintained_by = title_case_if_upper(attrs.get("MaintainedBy"))
        if owned_by and maintained_by and owned_by != maintained_by:
            ownership_raw = f"{owned_by} / maintained by {maintained_by}"
        else:
            ownership_raw = owned_by or maintained_by or "City of Cupertino"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), cupertino_zip_index)
        feature_suffix = attrs.get("AssetID") or attrs.get("OBJECTID")

        normalized_rows.append(
            {
                "id": f"cupertino-{feature_suffix}",
                "city": "Cupertino",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"cupertino-{feature_suffix}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Cupertino",
                    "source_dataset": "Trees",
                    "source_department": "City of Cupertino",
                    "source_last_edit_at": cupertino_last_edit,
                },
            }
        )

    for row in oakland_features:
        scientific_raw = (row.get("species") or "").strip()
        common_name = None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        location = row.get("location_1") or {}
        lon_raw = location.get("longitude")
        lat_raw = location.get("latitude")
        if lon_raw in (None, "") or lat_raw in (None, ""):
            continue
        lon = float(lon_raw)
        lat = float(lat_raw)

        ownership_raw = "City of Oakland Public Works Agency"
        zip_code = assign_zip_code(lon, lat, oakland_zip_index)
        feature_suffix = row.get("objectid")

        normalized_rows.append(
            {
                "id": f"oakland-{feature_suffix}",
                "city": "Oakland",
                "source_dataset": "Oakland Street Trees",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": f"oakland-{feature_suffix}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": None,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Oakland",
                    "source_dataset": "Oakland Street Trees",
                    "source_department": "City of Oakland Public Works Agency",
                    "source_last_edit_at": oakland_last_edit,
                },
            }
        )

    for row in everett_park_rows:
        scientific_raw, parsed_common_name = parse_sammamish_species(row.get("SITE_ATTR1"))
        common_name = parsed_common_name or row.get("SITE_ATTR1")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        lon = row.get("LONGITUDE")
        lat = row.get("LATITUDE")
        if lon is None or lat is None:
            geometry_text = row.get("SITE_GEOMETRY")
            if geometry_text:
                try:
                    parsed_geometry = json.loads(geometry_text)
                    coords = parsed_geometry.get("coordinates") or [None, None]
                    lon = coords[0]
                    lat = coords[1]
                except Exception:
                    lon, lat = None, None
        if lon is None or lat is None:
            continue

        zip_code = assign_zip_code(lon, lat, zip_index)
        ownership_raw = "City of Everett"

        normalized_rows.append(
            {
                "id": f"everett-1-{row.get('SITE_ID')}",
                "city": "Everett",
                "source_dataset": "Everett TreeKeeper Park Sites",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": f"everett-1-{row.get('SITE_ID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Everett",
                    "source_dataset": "Everett TreeKeeper Park Sites",
                    "source_department": "City of Everett",
                    "source_last_edit_at": everett_last_edit,
                },
            }
        )

    for row in kirkland_rows:
        pid_info = row.get("pid") or {}
        geom_info = row.get("geom") or {}
        scientific_source = (row.get("species_bo") or {}).get("val")
        common_name_source = (row.get("species_la") or {}).get("val")

        common_name = None if common_name_source in (None, "", "<Null>") else str(common_name_source).strip()
        scientific_raw = expand_abbreviated_botanical_name(
            None if scientific_source in (None, "", "<Null>") else str(scientific_source).strip(),
            common_name,
        )
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        if not species_group and not looks_like_target_blossom_species(scientific_raw, common_name):
            continue

        point = decode_wkb_point_hex(geom_info.get("val"))
        if not point:
            continue
        lon, lat = web_mercator_to_lon_lat(*point)

        ownership_raw = "City of Kirkland"
        zip_code = assign_zip_code(lon, lat, zip_index)
        feature_id = f"kirkland-{pid_info.get('val')}"

        normalized_rows.append(
            {
                "id": feature_id,
                "city": "Kirkland",
                "source_dataset": "2023-2024 Kirkland Tree Inventory",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": feature_id,
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Kirkland",
                    "source_dataset": "2023-2024 Kirkland Tree Inventory",
                    "source_department": "City of Kirkland",
                    "source_last_edit_at": kirkland_last_edit,
                },
            }
        )

    for feature in dc_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("SCI_NM") or "").strip()
        common_name = attrs.get("CMMN_NM")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = (attrs.get("OWNERSHIP") or "District of Columbia").strip() or "District of Columbia"
        zip_code = assign_zip_code(geom.get("x"), geom.get("y"), dc_zip_index)

        normalized_rows.append(
            {
                "id": f"washington-dc-{attrs.get('OBJECTID')}",
                "city": "Washington DC",
                "source_dataset": "Urban Tree Canopy",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"washington-dc-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Washington DC",
                    "source_dataset": "Urban Tree Canopy",
                    "source_department": "District Department of Transportation (DDOT)",
                    "source_last_edit_at": dc_last_edit,
                },
            }
        )

    for row in vancouver_bc_features:
        geometry = ((row.get("geom") or {}).get("geometry")) or {}
        coordinates = geometry.get("coordinates") or [None, None]
        lon = coordinates[0]
        lat = coordinates[1]
        if lon is None or lat is None:
            continue

        common_name = title_case_if_upper(row.get("common_name")) or None
        cultivar_name = title_case_if_upper(row.get("cultivar_name"))
        source_subtype = None if not cultivar_name or cultivar_name.lower() == "none" else cultivar_name
        scientific_raw = join_scientific_name(
            title_case_if_upper(row.get("genus_name")),
            (row.get("species_name") or "").strip().lower(),
        )
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)
        if source_subtype and not subtype_name:
            subtype_name = source_subtype

        ownership_raw = "City of Vancouver"

        normalized_rows.append(
            {
                "id": f"vancouver-bc-{row.get('asset_id')}",
                "city": "Vancouver BC",
                "source_dataset": "Public trees",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": f"vancouver-bc-{row.get('asset_id')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": None,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Vancouver BC",
                    "source_dataset": "Public trees",
                    "source_department": "City of Vancouver",
                    "source_last_edit_at": vancouver_bc_last_edit,
                },
            }
        )

    for feature in victoria_features:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})
        scientific_raw = (attrs.get("BotanicalName") or "").strip()
        common_name = title_case_if_upper(attrs.get("CommonName")) or None
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        ownership_raw = "City of Victoria Parks Department"

        normalized_rows.append(
            {
                "id": f"victoria-bc-{attrs.get('OBJECTID')}",
                "city": "Victoria BC",
                "source_dataset": "Tree Species (Parks trees database)",
                "scientific_raw": scientific_raw,
                "scientific_normalized": scientific_normalized,
                "common_name": common_name or "",
                "subtype_name": subtype_name or "",
                "zip_code": "",
                "species_group": species_group or "",
                "ownership": canonical_ownership(ownership_raw),
                "ownership_raw": ownership_raw,
                "lat": geom.get("y"),
                "lon": geom.get("x"),
                "included": "1" if species_group else "0",
            }
        )

        if not species_group:
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [geom.get("x"), geom.get("y")]},
                "properties": {
                    "id": f"victoria-bc-{attrs.get('OBJECTID')}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": None,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Victoria BC",
                    "source_dataset": "Tree Species (Parks trees database)",
                    "source_department": "City of Victoria Parks Department",
                    "source_last_edit_at": victoria_last_edit,
                },
            }
        )

    uw_seen_ids: set[int] = set()
    for element in uw_supplemental_elements:
        if element.get("type") != "node":
            continue
        node_id = element.get("id")
        if node_id in uw_seen_ids:
            continue
        uw_seen_ids.add(node_id)

        tags = element.get("tags", {})
        scientific_raw = (tags.get("species") or tags.get("genus") or "").strip()
        if not scientific_raw:
            continue
        common_name = tags.get("species:en") or tags.get("genus:en")
        scientific_normalized = normalize_scientific_name(scientific_raw)
        species_group, subtype_name = classify_tree_record(scientific_raw, common_name, mapping_rows, subtype_rows)

        # OSM UW data often uses explicit English species tags for Yoshino cherry.
        if not species_group:
            species_hint = (tags.get("species:en") or "").strip().lower()
            if "cherry" in species_hint:
                species_group = "cherry"
                if not subtype_name:
                    subtype_name = "Yoshino" if "yoshino" in species_hint else None

        ownership_raw = "University of Washington"
        lon = element.get("lon")
        lat = element.get("lat")
        zip_code = assign_zip_code(lon, lat, zip_index)

        normalized_rows.append(
            {
                "id": f"uw-osm-{node_id}",
                "city": "Seattle",
                "source_dataset": "UW OSM Supplemental",
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
            if scientific_normalized:
                unknown_counter[scientific_normalized] += 1
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "id": f"uw-osm-{node_id}",
                    "species_group": species_group,
                    "scientific_name": scientific_raw,
                    "common_name": common_name,
                    "subtype_name": subtype_name,
                    "zip_code": zip_code,
                    "ownership": canonical_ownership(ownership_raw),
                    "ownership_raw": ownership_raw,
                    "city": "Seattle",
                    "source_dataset": "UW OSM Supplemental",
                    "source_department": "University of Washington (OSM supplemental)",
                    "source_last_edit_at": "",
                },
            }
        )

    output_features.sort(key=lambda item: item["properties"]["id"])

    covered_cities = sorted({feature["properties"]["city"] for feature in output_features})
    covered_city_set = set(covered_cities)
    official_unavailable_cities = sorted(
        city for city in OFFICIAL_DATA_UNAVAILABLE_CITIES if city not in covered_city_set
    )
    coverage_features: list[dict[str, Any]] = []
    skipped_coverage_cities: list[str] = []
    for city in covered_cities:
        geometry = load_city_boundary_geometry(city)
        if not geometry:
            skipped_coverage_cities.append(city)
            if STRICT_OFFICIAL_JURISDICTION_BOUNDARY_ONLY:
                continue
            raise RuntimeError(f"Missing official jurisdiction boundary geometry for: {city}")
        note = f"Covered by public tree inventory for {city}; geometry from official jurisdiction boundary."

        coverage_features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "id": f"covered-{city.lower().replace(' ', '-')}",
                    "status": "covered",
                    "jurisdiction": city,
                    "note": note,
                },
            }
        )

    skipped_official_unavailable_cities: list[str] = []
    for city in official_unavailable_cities:
        geometry = load_city_boundary_geometry(city)
        if not geometry:
            skipped_official_unavailable_cities.append(city)
            if STRICT_OFFICIAL_JURISDICTION_BOUNDARY_ONLY:
                continue
            raise RuntimeError(f"Missing official jurisdiction boundary geometry for: {city}")

        coverage_features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "id": f"official-unavailable-{city.lower().replace(' ', '-')}",
                    "status": "official_unavailable",
                    "jurisdiction": city,
                    "note": OFFICIAL_DATA_UNAVAILABLE_CITIES[city],
                },
            }
        )

    now_iso = dt.datetime.now(tz=dt.timezone.utc).isoformat()
    coverage_geojson = {"type": "FeatureCollection", "features": coverage_features}
    species_guide = build_species_guide()
    region_bounds = build_region_bounds(coverage_features)

    region_feature_map: dict[str, list[dict[str, Any]]] = {region: [] for region in REGION_LABELS}
    for feature in output_features:
        region_feature_map[region_for_city(feature["properties"]["city"])].append(feature)

    unknown_items = [
        {"scientific_name_normalized": name, "count": count}
        for name, count in unknown_counter.most_common()
    ]

    meta_sources = [
        {
            "name": "Combined Tree Point",
            "city": "Seattle",
            "endpoint": SEATTLE_LAYER,
            "last_edit_at": seattle_last_edit,
            "records_fetched": len(seattle_features),
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Combined Tree Point"]
            ),
        },
        {
            "name": "City Trees",
            "city": "Bellevue",
            "endpoint": BELLEVUE_LAYER,
            "last_edit_at": bellevue_last_edit,
            "records_fetched": len(bellevue_features),
            "records_included": len([f for f in output_features if f["properties"]["source_dataset"] == "City Trees"]),
        },
        {
            "name": "TreeSite",
            "city": "Redmond",
            "endpoint": REDMOND_LAYER,
            "last_edit_at": redmond_last_edit,
            "records_fetched": len(redmond_features),
            "records_included": len([f for f in output_features if f["properties"]["source_dataset"] == "TreeSite"]),
        },
        {
            "name": "Tree Sites",
            "city": "Renton",
            "endpoint": RENTON_LAYER,
            "last_edit_at": renton_last_edit,
            "records_fetched": len(renton_features),
            "records_included": len([f for f in output_features if f["properties"]["source_dataset"] == "Tree Sites"]),
            "note": f"fallback cache used: {renton_source_error}" if renton_source_error else "",
        },
        {
            "name": "Public Trees",
            "city": "Kenmore",
            "endpoint": KENMORE_LAYER,
            "last_edit_at": kenmore_last_edit,
            "records_fetched": len(kenmore_features),
            "records_included": len([f for f in output_features if f["properties"]["source_dataset"] == "Public Trees"]),
        },
        {
            "name": "Trees",
            "city": "SeaTac",
            "endpoint": SEATAC_LAYER,
            "last_edit_at": seatac_last_edit,
            "records_fetched": len(seatac_features),
            "records_included": len([f for f in output_features if f["properties"]["source_dataset"] == "Trees"]),
        },
        {
            "name": "City Maintained Street Trees",
            "city": "Puyallup",
            "endpoint": PUYALLUP_LAYER,
            "last_edit_at": puyallup_last_edit,
            "records_fetched": len(puyallup_features),
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "City Maintained Street Trees"]
            ),
        },
        {
            "name": "PW Trees Public Viewer",
            "city": "Gig Harbor",
            "endpoint": GIG_HARBOR_LAYER,
            "last_edit_at": gig_harbor_last_edit,
            "records_fetched": len(gig_harbor_features),
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "PW Trees Public Viewer"]
            ),
        },
        {
            "name": "Public Tree Inventory",
            "city": "Shoreline",
            "endpoint": SHORELINE_LAYER,
            "last_edit_at": shoreline_last_edit,
            "records_fetched": len(shoreline_features),
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Public Tree Inventory"]
            ),
        },
        {
            "name": "Snohomish Tree Inventory",
            "city": "Snohomish",
            "endpoint": SNOHOMISH_LAYER,
            "last_edit_at": snohomish_last_edit,
            "records_fetched": len(snohomish_features),
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Snohomish Tree Inventory"]
            ),
        },
        {
            "name": "Bellingham Trees",
            "city": "Bellingham",
            "endpoint": BELLINGHAM_LAYER,
            "last_edit_at": bellingham_last_edit,
            "records_fetched": len(bellingham_features),
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Bellingham Trees"]
            ),
        },
        {
            "name": "Spokane Tree Inventory",
            "city": "Spokane",
            "endpoint": SPOKANE_LAYER,
            "last_edit_at": spokane_last_edit,
            "records_fetched": len(spokane_features),
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Spokane Tree Inventory"]
            ),
        },
        {
            "name": "Yakima Trees",
            "city": "Yakima",
            "endpoint": YAKIMA_LAYER,
            "last_edit_at": yakima_last_edit,
            "records_fetched": len(yakima_features),
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Yakima Trees"]
            ),
        },
        {
            "name": "City of Walla Walla Trees",
            "city": "Walla Walla",
            "endpoint": WALLA_WALLA_LAYER,
            "last_edit_at": walla_walla_last_edit,
            "records_fetched": len(walla_walla_features),
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "City of Walla Walla Trees"]
            ),
        },
        {
            "name": "Street Tree Inventory - Active Records",
            "city": "Portland",
            "endpoint": PORTLAND_LAYER,
            "last_edit_at": portland_last_edit,
            "records_fetched": portland_total,
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Street Tree Inventory - Active Records"]
            ),
        },
        {
            "name": "Street Tree",
            "city": "San Jose",
            "endpoint": SAN_JOSE_DATASET_PAGE,
            "last_edit_at": san_jose_last_edit,
            "records_fetched": san_jose_total,
            "records_included": len([f for f in output_features if f["properties"]["source_dataset"] == "Street Tree"]),
        },
        {
            "name": "Street Tree List",
            "city": "San Francisco",
            "endpoint": SAN_FRANCISCO_DATASET_PAGE,
            "last_edit_at": san_francisco_last_edit,
            "records_fetched": san_francisco_total,
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Street Tree List"]
            ),
        },
        {
            "name": "City Street Tree Inventory",
            "city": "Burlingame",
            "endpoint": BURLINGAME_DATASET_PAGE,
            "last_edit_at": burlingame_last_edit,
            "records_fetched": burlingame_total,
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "City Street Tree Inventory"]
            ),
        },
        {
            "name": "Tree Data",
            "city": "Palo Alto",
            "endpoint": PALO_ALTO_DATASET_PAGE,
            "last_edit_at": palo_alto_last_edit,
            "records_fetched": palo_alto_total,
            "records_included": len([f for f in output_features if f["properties"]["source_dataset"] == "Tree Data"]),
        },
        {
            "name": "Tree_Berkeley20191107",
            "city": "Berkeley",
            "endpoint": BERKELEY_TREES_ITEM,
            "last_edit_at": berkeley_last_edit,
            "records_fetched": berkeley_total,
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Tree_Berkeley20191107"]
            ),
        },
        {
            "name": "Trees",
            "city": "Cupertino",
            "endpoint": CUPERTINO_DATASET_PAGE,
            "last_edit_at": cupertino_last_edit,
            "records_fetched": cupertino_total,
            "records_included": len([f for f in output_features if f["properties"]["source_dataset"] == "Trees"]),
        },
        {
            "name": "Oakland Street Trees",
            "city": "Oakland",
            "endpoint": OAKLAND_DATASET_PAGE,
            "last_edit_at": oakland_last_edit,
            "records_fetched": oakland_total,
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Oakland Street Trees"]
            ),
        },
        {
            "name": "Public trees",
            "city": "Vancouver BC",
            "endpoint": VANCOUVER_BC_DATASET,
            "last_edit_at": vancouver_bc_last_edit,
            "records_fetched": len(vancouver_bc_features),
            "records_included": len([f for f in output_features if f["properties"]["source_dataset"] == "Public trees"]),
        },
        {
            "name": "Tree Species (Parks trees database)",
            "city": "Victoria BC",
            "endpoint": VICTORIA_PARK_TREES_LAYER,
            "last_edit_at": victoria_last_edit,
            "records_fetched": len(victoria_features),
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Tree Species (Parks trees database)"]
            ),
        },
        {
            "name": "TreeKeeper Street Sites",
            "city": "Sammamish",
            "endpoint": SAMMAMISH_GRIDS_ENDPOINT,
            "last_edit_at": "",
            "records_fetched": sammamish_street_total,
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "TreeKeeper Street Sites"]
            ),
        },
        {
            "name": "TreeKeeper Park Sites",
            "city": "Sammamish",
            "endpoint": SAMMAMISH_GRIDS_ENDPOINT,
            "last_edit_at": "",
            "records_fetched": sammamish_park_total,
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "TreeKeeper Park Sites"]
            ),
        },
        {
            "name": "Everett TreeKeeper Park Sites",
            "city": "Everett",
            "endpoint": EVERETT_GRIDS_ENDPOINT,
            "last_edit_at": everett_last_edit,
            "records_fetched": everett_park_total,
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "Everett TreeKeeper Park Sites"]
            ),
        },
        {
            "name": "2023-2024 Kirkland Tree Inventory",
            "city": "Kirkland",
            "endpoint": KIRKLAND_DB_ENDPOINT,
            "last_edit_at": kirkland_last_edit,
            "records_fetched": kirkland_total,
            "records_included": len(
                [f for f in output_features if f["properties"]["source_dataset"] == "2023-2024 Kirkland Tree Inventory"]
            ),
        },
        {
            "name": "Urban Tree Canopy",
            "city": "Washington DC",
            "endpoint": DC_LAYER,
            "last_edit_at": dc_last_edit,
            "records_fetched": len(dc_features),
            "records_included": len([f for f in output_features if f["properties"]["source_dataset"] == "Urban Tree Canopy"]),
        },
        {
            "name": "UW OSM Supplemental",
            "city": "Seattle",
            "endpoint": "OpenStreetMap Overpass supplemental file",
            "last_edit_at": "",
            "records_fetched": len(uw_supplemental_elements),
            "records_included": len([f for f in output_features if f["properties"]["id"].startswith("uw-osm-")]),
        },
    ]

    total_records = (
        len(seattle_features)
        + len(bellevue_features)
        + len(redmond_features)
        + len(renton_features)
        + len(kenmore_features)
        + len(seatac_features)
        + len(puyallup_features)
        + len(gig_harbor_features)
        + len(shoreline_features)
        + len(snohomish_features)
        + len(bellingham_features)
        + len(spokane_features)
        + len(yakima_features)
        + len(walla_walla_features)
        + portland_total
        + san_jose_total
        + san_francisco_total
        + burlingame_total
        + palo_alto_total
        + berkeley_total
        + cupertino_total
        + oakland_total
        + len(vancouver_bc_features)
        + len(victoria_features)
        + sammamish_street_total
        + sammamish_park_total
        + everett_park_total
        + kirkland_total
        + len(dc_features)
        + len(uw_supplemental_elements)
    )

    next_dir = PUBLIC_DATA_DIR / ".next"
    if next_dir.exists():
        shutil.rmtree(next_dir)
    next_dir.mkdir(parents=True, exist_ok=True)

    region_meta: list[dict[str, Any]] = []
    area_meta: list[dict[str, Any]] = []
    region_size_summary: list[dict[str, Any]] = []
    extra_output_names: list[str] = []
    for region_id, label in REGION_LABELS.items():
        features = region_feature_map[region_id]
        trees_geojson = {"type": "FeatureCollection", "features": features}
        payload_bytes = json.dumps(trees_geojson, ensure_ascii=False).encode("utf-8")
        raw_bytes = len(payload_bytes)
        gzip_bytes = len(gzip.compress(payload_bytes))
        warning_level = classify_warning_level(raw_bytes)
        region_cities = sorted({feature["properties"]["city"] for feature in features})
        region_species_counts = summarize_species_counts(features)
        region_entry: dict[str, Any] = {
            "id": region_id,
            "label": label,
            "available": bool(features),
            "bounds": region_bounds.get(region_id, WA_METRO_OVERVIEW_BOUNDS),
            "data_path": None,
            "tree_count": len(features),
            "city_count": len(region_cities),
            "cities": region_cities,
            "species_counts": region_species_counts,
            "raw_bytes": raw_bytes,
            "gzip_bytes": gzip_bytes,
            "warning_level": warning_level,
        }

        if features:
            city_entries: list[dict[str, Any]] = []
            for city in region_cities:
                city_features = [feature for feature in features if feature["properties"]["city"] == city]
                city_file_name = f"trees.{region_id}.city.{slugify_token(city)}.v1.geojson"
                city_payload_bytes = json.dumps(
                    {"type": "FeatureCollection", "features": city_features}, ensure_ascii=False
                ).encode("utf-8")
                (next_dir / city_file_name).write_bytes(city_payload_bytes)
                city_entries.append(
                    {
                        "city": city,
                        "data_path": f"/data/{city_file_name}",
                        "tree_count": len(city_features),
                        "raw_bytes": len(city_payload_bytes),
                        "gzip_bytes": len(gzip.compress(city_payload_bytes)),
                    }
                )
                area_meta.append(
                    {
                        "jurisdiction": city,
                        "region": region_id,
                        "tree_count": len(city_features),
                        "species_counts": summarize_species_counts(city_features),
                    }
                )
                extra_output_names.append(city_file_name)

            city_index_name = f"trees.{region_id}.city-index.v1.json"
            (next_dir / city_index_name).write_text(
                json.dumps(
                    {
                        "generated_at": now_iso,
                        "region": region_id,
                        "strategy": "city",
                        "items": city_entries,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            extra_output_names.append(city_index_name)
            region_entry["city_split"] = {
                "strategy": "city",
                "index_path": f"/data/{city_index_name}",
                "file_count": len(city_entries),
                "ready": True,
            }

        region_meta.append(region_entry)
        region_size_summary.append(
            {
                "region": label,
                "tree_count": len(features),
                "raw_bytes": raw_bytes,
                "gzip_bytes": gzip_bytes,
                "warning_level": warning_level,
            }
        )

    meta = {
        "version": "v2",
        "generated_at": now_iso,
        "default_region": DEFAULT_REGION,
        "coverage_rule": "official_jurisdiction_boundary_only",
        "coverage_skipped_cities": skipped_coverage_cities,
        "coverage_official_unavailable_cities": official_unavailable_cities,
        "coverage_official_unavailable_skipped_cities": skipped_official_unavailable_cities,
        "source_count": len(meta_sources),
        "total_records": total_records,
        "included_records": len(output_features),
        "unknown_records": int(sum(unknown_counter.values())),
        "species_counts": summarize_species_counts(output_features),
        "regions": region_meta,
        "areas": sorted(area_meta, key=lambda item: (item["region"], item["jurisdiction"])),
        "sources": meta_sources,
    }

    (next_dir / "coverage.v1.geojson").write_text(json.dumps(coverage_geojson, ensure_ascii=False), encoding="utf-8")
    (next_dir / "species-guide.v1.json").write_text(json.dumps(species_guide, ensure_ascii=False, indent=2), encoding="utf-8")
    (next_dir / "meta.v2.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (next_dir / "unknown_scientific_names.v1.json").write_text(
        json.dumps({"generated_at": now_iso, "items": unknown_items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    output_names = [
        "coverage.v1.geojson",
        "species-guide.v1.json",
        "meta.v2.json",
        "unknown_scientific_names.v1.json",
        *extra_output_names,
    ]

    for stale_path in PUBLIC_DATA_DIR.glob("trees.*.v2.geojson"):
        stale_path.unlink()
    for stale_path in PUBLIC_DATA_DIR.glob("trees.*.city*.v1.geojson"):
        stale_path.unlink()
    for city_index_path in PUBLIC_DATA_DIR.glob("trees.*.city-index.v1.json"):
        city_index_path.unlink()
    legacy_trees = PUBLIC_DATA_DIR / "trees.v1.geojson"
    if legacy_trees.exists():
        legacy_trees.unlink()
    legacy_meta = PUBLIC_DATA_DIR / "meta.v1.json"
    if legacy_meta.exists():
        legacy_meta.unlink()

    for output_name in output_names:
        shutil.move(str(next_dir / output_name), str(PUBLIC_DATA_DIR / output_name))

    if next_dir.exists():
        shutil.rmtree(next_dir)

    csv_path = NORMALIZED_DIR / "trees_normalized.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
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
            ],
        )
        writer.writeheader()
        writer.writerows(normalized_rows)

    print(
        json.dumps(
            {
                "included_records": len(output_features),
                "total_records": total_records,
                "unknown_scientific_names": len(unknown_items),
                "generated_at": now_iso,
                "regions": region_size_summary,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
