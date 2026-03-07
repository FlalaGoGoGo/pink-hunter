import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent
} from "react";
import type { FeatureCollection, Point } from "geojson";
import { loadRegionTrees, loadStaticAppData } from "./data";
import { DEFAULT_LANGUAGE, ownershipLabel, speciesLabel, t } from "./i18n";
import {
  loadMapRuntimeDeps,
  type ClipMultiPolygon,
  type GeoJSONSource,
  type MapLayerMouseEvent,
  type MapLibreMap,
  type MapLibrePopup,
  type MapRuntimeDeps
} from "./mapRuntime";
import type {
  AppMeta,
  CoverageCollection,
  CoverageFeatureProps,
  CoverageRegion,
  Language,
  LayoutMode,
  MapStylePreset,
  OwnershipGroup,
  RegionMeta,
  SpeciesGroup,
  StaticAppData,
  TreeCollection,
  TreeFeatureProps
} from "./types";

const SNAP_POINTS = [0.4, 0.72, 1] as const;
const USER_LOCATION_SOURCE_ID = "user-location";
const SELECTED_MARKER_IMAGE_ID = "selected-bloom-marker";
const ALL_SPECIES = ["cherry", "plum", "peach", "magnolia", "crabapple"] as const;
const POINT_LAYER_IDS = [
  "tree-cherry",
  "tree-plum",
  "tree-peach",
  "tree-magnolia",
  "tree-crabapple"
] as const;
const ALL_OWNERSHIP = ["public", "private", "unknown"] as const;
const DEFAULT_CENTER: [number, number] = [-122.315, 47.55];
const DEFAULT_ZOOM = 8.45;
const POSITRON_STYLE_URL = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";
const FALLBACK_STYLE_URL = "https://demotiles.maplibre.org/style.json";
const ABOUT_SOURCES_PAGE_SIZE = 8;
const POINT_COLORS: Record<SpeciesGroup, string> = {
  cherry: "#ef79ad",
  plum: "#d976b4",
  peach: "#f39a88",
  magnolia: "#b886ea",
  crabapple: "#ff6f9f"
};
const COVERAGE_COLORS = {
  coveredFill: "#f7b7cc",
  coveredLine: "#8a5567",
  unavailableFill: "#d7dbe1",
  unavailableLine: "#8f96a1"
} as const;
const EMPTY_TREE_COLLECTION: TreeCollection = { type: "FeatureCollection", features: [] };

const REGION_CITY_OVERRIDES: Partial<Record<string, CoverageRegion>> = {
  "Washington DC": "dc",
  "Vancouver BC": "bc",
  "Victoria BC": "bc",
  Portland: "or",
  Burlingame: "ca",
  "San Francisco": "ca",
  "San Jose": "ca"
};

const GLOBAL_REGION_OPTIONS: Array<{ region: CoverageRegion; label: string }> = [
  { region: "wa", label: "🇺🇸 WA" },
  { region: "ca", label: "🇺🇸 CA" },
  { region: "dc", label: "🇺🇸 DC" },
  { region: "or", label: "🇺🇸 OR" },
  { region: "bc", label: "🇨🇦 BC" }
];

interface SelectedTree {
  coordinates: [number, number];
  properties: TreeFeatureProps;
}

interface SelectedCoverage {
  coordinates: [number, number];
  properties: CoverageFeatureProps;
}

interface UrlState {
  region: CoverageRegion;
  language: Language;
  species: SpeciesGroup[];
  ownership: OwnershipGroup[];
  cities: string[];
  zipCodes: string[];
  hasSpeciesParam: boolean;
  hasOwnershipParam: boolean;
  hasCityParam: boolean;
  hasZipParam: boolean;
  hasViewportParam: boolean;
  zoom: number;
  lat: number;
  lon: number;
}

function parseLanguage(raw: string | null): Language {
  if (raw === "zh-CN" || raw === "en-US") {
    return raw;
  }
  return DEFAULT_LANGUAGE;
}

function parseDelimited<T extends string>(
  raw: string | null,
  allowed: readonly T[],
  fallback: readonly T[]
): T[] {
  if (raw === "none") {
    return [];
  }
  if (!raw) {
    return [...fallback];
  }
  const values = raw
    .split(",")
    .map((item) => item.trim())
    .filter((item): item is T => allowed.includes(item as T));
  return values.length > 0 ? values : [...fallback];
}

function parseStringList(raw: string | null): string[] {
  if (!raw || raw === "none") {
    return [];
  }
  return raw
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function parseUrlState(): UrlState {
  const params = new URLSearchParams(window.location.search);
  const cities = parseStringList(params.get("city"));
  const region = parseRegion(params.get("region"), cities);
  const language = parseLanguage(params.get("lang"));
  const hasSpeciesParam = params.has("species");
  const hasOwnershipParam = params.has("ownership");
  const hasCityParam = params.has("city");
  const hasZipParam = params.has("zip");
  const species = parseDelimited(params.get("species"), ALL_SPECIES, ALL_SPECIES);
  const ownership = parseDelimited(params.get("ownership"), ALL_OWNERSHIP, ALL_OWNERSHIP);
  const zipCodes = parseStringList(params.get("zip"));

  const zoom = Number(params.get("z"));
  const lat = Number(params.get("lat"));
  const lon = Number(params.get("lon"));
  const hasViewportParam = params.has("z") && params.has("lat") && params.has("lon");

  return {
    region,
    language,
    species,
    ownership,
    cities,
    zipCodes,
    hasSpeciesParam,
    hasOwnershipParam,
    hasCityParam,
    hasZipParam,
    hasViewportParam,
    zoom: Number.isFinite(zoom) ? zoom : DEFAULT_ZOOM,
    lat: Number.isFinite(lat) ? lat : DEFAULT_CENTER[1],
    lon: Number.isFinite(lon) ? lon : DEFAULT_CENTER[0]
  };
}

function boundsForRegion(regionMeta: RegionMeta | null): [[number, number], [number, number]] | null {
  return regionMeta?.bounds ?? null;
}

function setDocumentMeta(selector: string, content: string): void {
  const element = document.head.querySelector<HTMLMetaElement>(selector);
  if (element) {
    element.setAttribute("content", content);
  }
}

function nearestSnap(value: number): number {
  return SNAP_POINTS.reduce((closest, snap) =>
    Math.abs(snap - value) < Math.abs(closest - value) ? snap : closest
  );
}

function toTreeCollection(features: TreeCollection["features"]): TreeCollection {
  return {
    type: "FeatureCollection",
    features
  };
}

function getTreeCoordinates(feature: TreeCollection["features"][number]): [number, number] {
  const [lon, lat] = feature.geometry.coordinates;
  return [lon, lat];
}

function buildCoverageCollection(
  coverageFeatures: CoverageCollection["features"],
  polygonClippingModule: MapRuntimeDeps["polygonClipping"]
): CoverageCollection {
  const occupied: ClipMultiPolygon[] = [];
  const sortedFeatures = [...coverageFeatures].sort(
    (left, right) => geometryAreaApprox(left.geometry) - geometryAreaApprox(right.geometry)
  );

  const features = sortedFeatures
    .map((feature) => {
      const subject = geometryToClipMultiPolygon(feature.geometry);
      const clipped =
        occupied.length > 0
          ? (polygonClippingModule.difference(subject, ...occupied) as ClipMultiPolygon | null)
          : subject;
      const geometry = clipMultiPolygonToGeometry(clipped);
      if (!geometry) {
        return null;
      }
      occupied.push(geometryToClipMultiPolygon(geometry));
      return {
        ...feature,
        geometry
      };
    })
    .filter((feature): feature is CoverageCollection["features"][number] => feature !== null);

  return {
    type: "FeatureCollection",
    features
  };
}

function ringAreaApprox(ring: number[][]): number {
  let area = 0;
  for (let index = 0; index < ring.length - 1; index += 1) {
    const [x1, y1] = ring[index];
    const [x2, y2] = ring[index + 1];
    area += x1 * y2 - x2 * y1;
  }
  return Math.abs(area) / 2;
}

function geometryAreaApprox(geometry: CoverageCollection["features"][number]["geometry"]): number {
  if (geometry.type === "Polygon") {
    return geometry.coordinates.reduce((sum, ring, index) => sum + (index === 0 ? ringAreaApprox(ring) : 0), 0);
  }
  return geometry.coordinates.reduce(
    (sum, polygon) => sum + polygon.reduce((polySum, ring, index) => polySum + (index === 0 ? ringAreaApprox(ring) : 0), 0),
    0
  );
}

function geometryToClipMultiPolygon(
  geometry: CoverageCollection["features"][number]["geometry"]
): ClipMultiPolygon {
  return (geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates) as unknown as ClipMultiPolygon;
}

function clipMultiPolygonToGeometry(
  geometry: ClipMultiPolygon | null
): CoverageCollection["features"][number]["geometry"] | null {
  if (!geometry || geometry.length === 0) {
    return null;
  }
  if (geometry.length === 1) {
    return {
      type: "Polygon",
      coordinates: geometry[0]
    };
  }
  return {
    type: "MultiPolygon",
    coordinates: geometry
  };
}

function parseRegion(raw: string | null, cities: string[]): CoverageRegion {
  if (raw === "wa" || raw === "ca" || raw === "or" || raw === "dc" || raw === "bc") {
    return raw;
  }
  if (cities.length > 0) {
    return regionForCity(cities[0]);
  }
  return "wa";
}

function regionForCity(city: string): CoverageRegion {
  if (REGION_CITY_OVERRIDES[city]) {
    return REGION_CITY_OVERRIDES[city] as CoverageRegion;
  }
  if (city === "Washington DC" || city.endsWith(" DC")) {
    return "dc";
  }
  if (city.endsWith(" OR") || city.endsWith(", OR")) {
    return "or";
  }
  if (city.endsWith(" CA") || city.endsWith(", CA")) {
    return "ca";
  }
  if (city.endsWith(" BC") || city.endsWith(", BC")) {
    return "bc";
  }
  return "wa";
}

function stateCodeForCity(city: string): string {
  const region = regionForCity(city);
  if (region === "dc") {
    return "DC";
  }
  if (region === "bc") {
    return "BC";
  }
  if (region === "or") {
    return "OR";
  }
  if (region === "ca") {
    return "CA";
  }
  return "WA";
}

function formatCityLabel(city: string): string {
  const stateCode = stateCodeForCity(city);
  const uppercaseCity = city.toUpperCase();
  if (uppercaseCity.endsWith(` ${stateCode}`) || uppercaseCity.endsWith(`, ${stateCode}`)) {
    return city;
  }
  return `${city} (${stateCode})`;
}

function buildUserLocationData(coordinates: [number, number] | null): FeatureCollection<Point> {
  if (!coordinates) {
    return {
      type: "FeatureCollection",
      features: []
    };
  }

  return {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates
        },
        properties: {}
      }
    ]
  };
}

function createSelectedBloomImageData(): ImageData {
  const size = 120;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d");
  if (!context) {
    throw new Error("Canvas 2D context is unavailable.");
  }
  const ctx = context;

  const center = size / 2;

  function drawTriangle(radius: number, rotation: number): void {
    ctx.beginPath();
    for (let index = 0; index < 3; index += 1) {
      const angle = rotation + (index * (Math.PI * 2)) / 3;
      const x = center + Math.cos(angle) * radius;
      const y = center + Math.sin(angle) * radius;
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.closePath();
  }

  ctx.clearRect(0, 0, size, size);
  ctx.strokeStyle = "rgba(255,255,255,0.92)";
  ctx.lineWidth = 11;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  drawTriangle(34, -Math.PI / 2);
  ctx.stroke();
  drawTriangle(34, Math.PI / 2);
  ctx.stroke();

  ctx.shadowColor = "rgba(124, 51, 82, 0.24)";
  ctx.shadowBlur = 12;
  ctx.strokeStyle = "#6f3550";
  ctx.lineWidth = 5;
  drawTriangle(34, -Math.PI / 2);
  ctx.stroke();
  drawTriangle(34, Math.PI / 2);
  ctx.stroke();
  ctx.shadowBlur = 0;

  ctx.beginPath();
  ctx.arc(center, center, 11, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(255, 248, 252, 0.98)";
  ctx.fill();
  ctx.lineWidth = 4;
  ctx.strokeStyle = "#de5f95";
  ctx.stroke();

  return ctx.getImageData(0, 0, size, size);
}

function sortZipCodesByMasterOrder(values: Iterable<string>, order: string[]): string[] {
  const lookup = new Map(order.map((zipCode, index) => [zipCode, index]));
  return Array.from(new Set(values)).sort((left, right) => {
    const leftIndex = lookup.get(left) ?? Number.MAX_SAFE_INTEGER;
    const rightIndex = lookup.get(right) ?? Number.MAX_SAFE_INTEGER;
    return leftIndex - rightIndex || left.localeCompare(right);
  });
}

function getCitiesForTrees(trees: TreeCollection): string[] {
  return Array.from(new Set(trees.features.map((feature) => feature.properties.city))).sort();
}

function getZipCodesForTrees(trees: TreeCollection): string[] {
  return Array.from(new Set(trees.features.map((feature) => feature.properties.zip_code ?? "unknown"))).sort(
    (left, right) => {
      if (left === "unknown") {
        return 1;
      }
      if (right === "unknown") {
        return -1;
      }
      return left.localeCompare(right);
    }
  );
}

function isHttpUrl(value: string): boolean {
  return /^https?:\/\//i.test(value);
}

function escapeHtml(raw: string): string {
  return raw
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

async function resolveMapStyle(): Promise<{ styleUrl: string; preset: MapStylePreset }> {
  try {
    const response = await fetch(POSITRON_STYLE_URL, { method: "GET" });
    if (response.ok) {
      return { styleUrl: POSITRON_STYLE_URL, preset: "positron" };
    }
  } catch {
    // Fall through to default style.
  }

  return { styleUrl: FALLBACK_STYLE_URL, preset: "demotiles" };
}

export default function App(): JSX.Element {
  const initialUrlState = useMemo(parseUrlState, []);
  const initialLayoutMode: LayoutMode =
    typeof window !== "undefined" && window.innerWidth >= 1024 ? "desktop_split" : "mobile_sheet";

  const [data, setData] = useState<StaticAppData | null>(null);
  const [mapRuntime, setMapRuntime] = useState<MapRuntimeDeps | null>(null);
  const [regionTreeCache, setRegionTreeCache] = useState<Partial<Record<CoverageRegion, TreeCollection>>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [regionLoading, setRegionLoading] = useState<CoverageRegion | null>(null);

  const [activeRegion, setActiveRegion] = useState<CoverageRegion>(initialUrlState.region);
  const [language, setLanguage] = useState<Language>(initialUrlState.language);
  const [selectedSpecies, setSelectedSpecies] = useState<SpeciesGroup[]>(initialUrlState.species);
  const [selectedOwnership, setSelectedOwnership] = useState<OwnershipGroup[]>(initialUrlState.ownership);
  const [selectedCities, setSelectedCities] = useState<string[]>(initialUrlState.cities);
  const [selectedZipCodes, setSelectedZipCodes] = useState<string[]>(initialUrlState.zipCodes);
  const [cityDropdownOpen, setCityDropdownOpen] = useState(false);
  const [citySearchQuery, setCitySearchQuery] = useState("");
  const [zipDropdownOpen, setZipDropdownOpen] = useState(false);
  const [zipSearchQuery, setZipSearchQuery] = useState("");
  const [sheetHeight, setSheetHeight] = useState<number>(0.4);
  const [activePanel, setActivePanel] = useState<"filters" | "guide" | "about">("filters");
  const [aboutSourcesPage, setAboutSourcesPage] = useState(0);
  const [selectedTree, setSelectedTree] = useState<SelectedTree | null>(null);
  const [selectedCoverage, setSelectedCoverage] = useState<SelectedCoverage | null>(null);
  const [layoutMode, setLayoutMode] = useState<LayoutMode>(initialLayoutMode);
  const [mapStylePreset, setMapStylePreset] = useState<MapStylePreset>("positron");
  const [globalMenuOpen, setGlobalMenuOpen] = useState(false);
  const [mapView, setMapView] = useState({
    zoom: initialUrlState.zoom,
    lat: initialUrlState.lat,
    lon: initialUrlState.lon
  });
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);

  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const popupRef = useRef<MapLibrePopup | null>(null);
  const filteredFeaturesRef = useRef<TreeCollection["features"]>([]);
  const isDesktopRef = useRef(layoutMode === "desktop_split");
  const initialRegionFiltersAppliedRef = useRef(false);
  const pendingRegionResetRef = useRef<CoverageRegion | null>(null);
  const dragStateRef = useRef<{ startY: number; startHeight: number; dragging: boolean }>({
    startY: 0,
    startHeight: 0.4,
    dragging: false
  });

  const isDesktop = layoutMode === "desktop_split";

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const [loadedData, runtimeDeps] = await Promise.all([loadStaticAppData(), loadMapRuntimeDeps()]);
        if (cancelled) {
          return;
        }
        setData(loadedData);
        setMapRuntime(runtimeDeps);
      } catch (loadError) {
        const message = loadError instanceof Error ? loadError.message : "Unknown loading error";
        if (!cancelled) {
          setError(message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(min-width: 1024px)");
    const handleChange = (event: MediaQueryListEvent): void => {
      setLayoutMode(event.matches ? "desktop_split" : "mobile_sheet");
    };

    setLayoutMode(mediaQuery.matches ? "desktop_split" : "mobile_sheet");
    mediaQuery.addEventListener("change", handleChange);
    return () => {
      mediaQuery.removeEventListener("change", handleChange);
    };
  }, []);

  useEffect(() => {
    isDesktopRef.current = isDesktop;
    mapRef.current?.resize();
  }, [isDesktop]);

  const regionMetaById = useMemo(() => {
    const entries = (data?.meta.regions ?? []).map((regionMeta) => [regionMeta.id, regionMeta]);
    return new Map(entries as Array<[CoverageRegion, RegionMeta]>);
  }, [data]);

  const activeRegionMeta = regionMetaById.get(activeRegion) ?? null;
  const activeRegionTrees = regionTreeCache[activeRegion] ?? null;
  const activeRegionPending = Boolean(
    data && activeRegionMeta?.available && !activeRegionTrees && regionLoading === activeRegion
  );

  useEffect(() => {
    if (!data) {
      return;
    }
    const fallbackRegion = data.meta.default_region;
    if (!regionMetaById.get(activeRegion)?.available) {
      setActiveRegion(fallbackRegion);
    }
  }, [activeRegion, data, regionMetaById]);

  useEffect(() => {
    if (!activeRegionMeta || !activeRegionMeta.available || activeRegionTrees) {
      return;
    }

    let cancelled = false;
    setRegionLoading(activeRegion);
    setError(null);

    void (async () => {
      try {
        const regionTrees = await loadRegionTrees(activeRegionMeta.data_path);
        if (cancelled) {
          return;
        }
        setRegionTreeCache((current) => ({ ...current, [activeRegion]: regionTrees }));
      } catch (loadError) {
        if (cancelled) {
          return;
        }
        const message = loadError instanceof Error ? loadError.message : "Unknown region loading error";
        setError(message);
      } finally {
        if (!cancelled) {
          setRegionLoading((current) => (current === activeRegion ? null : current));
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [activeRegion, activeRegionMeta, activeRegionTrees]);

  const currentTrees = activeRegionTrees ?? EMPTY_TREE_COLLECTION;

  const cities = useMemo(() => {
    if (!activeRegionTrees) {
      return [] as string[];
    }
    return getCitiesForTrees(currentTrees);
  }, [activeRegionTrees, currentTrees]);

  const zipCodes = useMemo(() => {
    if (!activeRegionTrees) {
      return [] as string[];
    }
    return getZipCodesForTrees(currentTrees);
  }, [activeRegionTrees, currentTrees]);

  const zipCodesByCity = useMemo(() => {
    const cityMap = new Map<string, Set<string>>();
    if (!activeRegionTrees) {
      return new Map<string, string[]>();
    }

    currentTrees.features.forEach((feature) => {
      const city = feature.properties.city;
      const zipCode = feature.properties.zip_code ?? "unknown";
      const bucket = cityMap.get(city) ?? new Set<string>();
      bucket.add(zipCode);
      cityMap.set(city, bucket);
    });

    return new Map(
      Array.from(cityMap.entries()).map(([city, zipSet]) => [city, sortZipCodesByMasterOrder(zipSet, zipCodes)])
    );
  }, [activeRegionTrees, currentTrees, zipCodes]);

  const cityOptions = useMemo(
    () => cities.map((city) => ({ city, label: formatCityLabel(city), stateCode: stateCodeForCity(city) })),
    [cities]
  );

  const allOwnershipOptions = useMemo(() => {
    if (!activeRegionTrees) {
      return ["public", "private"] as OwnershipGroup[];
    }
    const options = new Set<OwnershipGroup>(currentTrees.features.map((feature) => feature.properties.ownership));
    return (["public", "private", "unknown"] as const).filter((item) => options.has(item));
  }, [activeRegionTrees, currentTrees]);

  const displayCoverage = useMemo(() => {
    if (!data) {
      return { type: "FeatureCollection", features: [] } as CoverageCollection;
    }
    if (!mapRuntime) {
      return data.coverage;
    }
    return buildCoverageCollection(data.coverage.features, mapRuntime.polygonClipping);
  }, [data, mapRuntime]);

  useEffect(() => {
    if (!activeRegionTrees) {
      return;
    }

    if (!initialRegionFiltersAppliedRef.current && activeRegion === initialUrlState.region) {
      const nextCities = initialUrlState.hasCityParam
        ? cities.filter((city) => initialUrlState.cities.includes(city))
        : cities;
      const nextZipCodes = initialUrlState.hasZipParam
        ? zipCodes.filter((zipCode) => initialUrlState.zipCodes.includes(zipCode))
        : zipCodes;

      setSelectedCities(nextCities);
      setSelectedZipCodes(nextZipCodes);
      initialRegionFiltersAppliedRef.current = true;
      pendingRegionResetRef.current = null;
      return;
    }

    if (pendingRegionResetRef.current === activeRegion) {
      setSelectedCities(cities);
      setSelectedZipCodes(zipCodes);
      pendingRegionResetRef.current = null;
    }
  }, [activeRegion, activeRegionTrees, cities, initialUrlState.cities, initialUrlState.hasCityParam, initialUrlState.hasZipParam, initialUrlState.region, initialUrlState.zipCodes, zipCodes]);

  const filteredFeatures = useMemo(() => {
    if (
      !activeRegionTrees ||
      selectedSpecies.length === 0 ||
      selectedOwnership.length === 0 ||
      selectedCities.length === 0 ||
      selectedZipCodes.length === 0
    ) {
      return [] as TreeCollection["features"];
    }

    const speciesSet = new Set(selectedSpecies);
    const ownershipSet = new Set(selectedOwnership);
    const citySet = new Set(selectedCities);
    const zipSet = new Set(selectedZipCodes);

    return currentTrees.features.filter((feature) => {
      const props = feature.properties;
      return (
        speciesSet.has(props.species_group) &&
        ownershipSet.has(props.ownership) &&
        citySet.has(props.city) &&
        zipSet.has(props.zip_code ?? "unknown")
      );
    });
  }, [activeRegionTrees, currentTrees, selectedCities, selectedOwnership, selectedSpecies, selectedZipCodes]);

  const ownershipOptions = useMemo(() => {
    if (!activeRegionTrees || selectedSpecies.length === 0 || selectedCities.length === 0 || selectedZipCodes.length === 0) {
      return [] as OwnershipGroup[];
    }

    const speciesSet = new Set(selectedSpecies);
    const citySet = new Set(selectedCities);
    const zipSet = new Set(selectedZipCodes);
    const options = new Set<OwnershipGroup>();

    currentTrees.features.forEach((feature) => {
      const props = feature.properties;
      if (
        speciesSet.has(props.species_group) &&
        citySet.has(props.city) &&
        zipSet.has(props.zip_code ?? "unknown")
      ) {
        options.add(props.ownership);
      }
    });

    return (["public", "private", "unknown"] as const).filter((item) => options.has(item));
  }, [activeRegionTrees, currentTrees, selectedCities, selectedSpecies, selectedZipCodes]);

  const filteredCollection = useMemo(() => toTreeCollection(filteredFeatures), [filteredFeatures]);

  useEffect(() => {
    filteredFeaturesRef.current = filteredFeatures;
  }, [filteredFeatures]);

  useEffect(() => {
    setSelectedOwnership((current) => {
      if (ownershipOptions.length === 0) {
        return current;
      }
      if (current.length === 0) {
        return current;
      }
      return current.filter((item) => ownershipOptions.includes(item));
    });
  }, [ownershipOptions]);

  useEffect(() => {
    if (activePanel !== "filters" && cityDropdownOpen) {
      setCityDropdownOpen(false);
    }
    if (activePanel !== "filters" && zipDropdownOpen) {
      setZipDropdownOpen(false);
    }
  }, [activePanel, cityDropdownOpen, zipDropdownOpen]);

  useEffect(() => {
    if (!cityDropdownOpen) {
      setCitySearchQuery("");
    }
  }, [cityDropdownOpen]);

  useEffect(() => {
    if (!zipDropdownOpen) {
      setZipSearchQuery("");
    }
  }, [zipDropdownOpen]);

  const visibleCities = useMemo(() => {
    const query = citySearchQuery.trim().toLowerCase();
    if (!query) {
      return cityOptions;
    }

    return cityOptions.filter(({ city, label, stateCode }) => {
      return (
        city.toLowerCase().includes(query) ||
        label.toLowerCase().includes(query) ||
        stateCode.toLowerCase().includes(query)
      );
    });
  }, [cityOptions, citySearchQuery]);

  const visibleZipCodes = useMemo(() => {
    const query = zipSearchQuery.trim().toLowerCase();
    if (!query) {
      return zipCodes;
    }
    return zipCodes.filter((zipCode) => {
      const label = zipCode === "unknown" ? t(language, "unknown").toLowerCase() : zipCode.toLowerCase();
      return label.includes(query);
    });
  }, [language, zipCodes, zipSearchQuery]);

  const aboutCopy = language === "zh-CN"
    ? {
        title: "关于 Pink Hunter",
        intro: [
          "Pink Hunter 是一个春季粉色花树地图项目，帮助大家在花季里更快找到樱花、李花、桃花、木兰和海棠。",
          "这个项目不只是找花，也希望教大家分辨这些常被误认的花树，让“粉色花都叫樱花”这件事少一点。"
        ],
        sourcesTitle: "数据源",
        disclaimerTitle: "数据说明",
        contactTitle: "联系方式",
        contactLead: "如果你知道新的官方公开树木数据源，欢迎发邮件给 Flala Zhang。",
        disclaimer: [
          "城市级覆盖优先采用官方公开的单株树木数据集；这是产品纳入覆盖城市的硬标准。",
          "但数据更新频率、树木修剪/移除、物种录入习惯、坐标偏差等问题，都会让网页显示与现实情况存在差异。",
          "UW 樱花点位目前使用补充数据来弥补官方城市树木清单的空缺，因此这一部分不是官方 city inventory。"
        ],
        officialBadge: "官方公开源",
        supplementalBadge: "补充源",
        openLink: "打开源链接",
        previousPage: "上一页",
        nextPage: "下一页",
        pageLabel: "页"
      }
    : {
        title: "About Pink Hunter",
        intro: [
          "Pink Hunter is a spring map for finding pink-blossoming cherry, plum, peach, magnolia, and crabapple trees.",
          "The project is meant to help people learn the differences between these lookalike blooms instead of calling every pink tree a cherry by default."
        ],
        sourcesTitle: "Data Sources",
        disclaimerTitle: "Data Notes",
        contactTitle: "Contact",
        contactLead: "If you know an official public tree dataset that should be included, send it to Flala Zhang.",
        disclaimer: [
          "City-level coverage is built from official public single-tree datasets whenever those datasets are available; that is a hard rule for city integration.",
          "What you see on the map can still differ from reality because of source refresh lag, pruning or removals, naming inconsistencies, or point-location error.",
          "UW cherry points are currently included through a supplemental dataset because the official city inventory does not fully cover that campus hotspot."
        ],
        officialBadge: "Official public source",
        supplementalBadge: "Supplemental source",
        openLink: "Open source link",
        previousPage: "Previous",
        nextPage: "Next",
        pageLabel: "Page"
      };

  useEffect(() => {
    document.title = t(language, "browserTitle");
    setDocumentMeta('meta[name="description"]', t(language, "browserDescription"));
    setDocumentMeta('meta[property="og:title"]', t(language, "browserTitle"));
    setDocumentMeta('meta[property="og:description"]', t(language, "browserDescription"));
    setDocumentMeta('meta[name="twitter:title"]', t(language, "browserTitle"));
    setDocumentMeta('meta[name="twitter:description"]', t(language, "browserDescription"));
  }, [language]);

  const aboutSources = useMemo(() => {
    if (!data) {
      return [] as AppMeta["sources"];
    }
    return [...data.meta.sources].sort(
      (left, right) => left.city.localeCompare(right.city) || left.name.localeCompare(right.name)
    );
  }, [data]);

  const aboutSourcePageCount = Math.max(1, Math.ceil(aboutSources.length / ABOUT_SOURCES_PAGE_SIZE));

  const pagedAboutSources = useMemo(
    () =>
      aboutSources.slice(
        aboutSourcesPage * ABOUT_SOURCES_PAGE_SIZE,
        (aboutSourcesPage + 1) * ABOUT_SOURCES_PAGE_SIZE
      ),
    [aboutSources, aboutSourcesPage]
  );

  useEffect(() => {
    setAboutSourcesPage((current) => Math.min(current, aboutSourcePageCount - 1));
  }, [aboutSourcePageCount]);

  useEffect(() => {
    if (!data || !mapRuntime || mapRef.current || !mapContainerRef.current) {
      return;
    }

    let isCancelled = false;
    let mapInstance: MapLibreMap | null = null;

    void (async () => {
      try {
        const { styleUrl, preset } = await resolveMapStyle();
        if (isCancelled || !mapContainerRef.current) {
          return;
        }

        setMapStylePreset(preset);

        const map = new mapRuntime.maplibre.Map({
          container: mapContainerRef.current,
          style: styleUrl,
          center: [initialUrlState.lon, initialUrlState.lat],
          zoom: initialUrlState.zoom,
          minZoom: 7,
          maxZoom: 18,
          attributionControl: false
        });

        mapInstance = map;
        mapRef.current = map;

        map.on("error", (event) => {
          console.error("map-runtime-error", event?.error ?? event);
        });

        map.on("load", () => {
          map.addControl(new mapRuntime.maplibre.ScaleControl({ maxWidth: 110, unit: "metric" }), "bottom-right");

        map.addSource("coverage", {
          type: "geojson",
          data: displayCoverage
        });

        map.addLayer({
          id: "coverage-official-unavailable",
          type: "fill",
          source: "coverage",
          filter: ["==", ["get", "status"], "official_unavailable"],
          paint: {
            "fill-color": COVERAGE_COLORS.unavailableFill,
            "fill-opacity": 0.34
          }
        });

        map.addLayer({
          id: "coverage-covered",
          type: "fill",
          source: "coverage",
          filter: ["==", ["get", "status"], "covered"],
          paint: {
            "fill-color": COVERAGE_COLORS.coveredFill,
            "fill-opacity": 0.18
          }
        });

        map.addLayer({
          id: "coverage-unavailable-outline",
          type: "line",
          source: "coverage",
          filter: ["==", ["get", "status"], "official_unavailable"],
          paint: {
            "line-color": COVERAGE_COLORS.unavailableLine,
            "line-width": 1.45,
            "line-dasharray": [2.4, 2.2]
          }
        });

        map.addLayer({
          id: "coverage-outline",
          type: "line",
          source: "coverage",
          filter: ["==", ["get", "status"], "covered"],
          paint: {
            "line-color": COVERAGE_COLORS.coveredLine,
            "line-width": 1.5,
            "line-dasharray": [2, 2]
          }
        });

        map.addSource("trees", {
          type: "geojson",
          data: filteredCollection,
          cluster: true,
          clusterMaxZoom: 11,
          clusterRadius: 48
        });

        map.addLayer({
          id: "tree-clusters",
          type: "circle",
          source: "trees",
          filter: ["has", "point_count"],
          paint: {
            "circle-color": "#f4a8c5",
            "circle-radius": ["step", ["get", "point_count"], 13, 35, 17, 120, 21],
            "circle-stroke-width": 1.5,
            "circle-stroke-color": "#ffffff",
            "circle-opacity": 0.95
          }
        });

        map.addLayer({
          id: "tree-cluster-count",
          type: "symbol",
          source: "trees",
          filter: ["has", "point_count"],
          layout: {
            "text-field": ["get", "point_count_abbreviated"],
            "text-size": 12,
            "text-font": ["Open Sans Bold"]
          },
          paint: {
            "text-color": "#4f2d3d"
          }
        });

        ALL_SPECIES.forEach((species) => {
          map.addLayer({
            id: `tree-${species}`,
            type: "circle",
            source: "trees",
            filter: ["all", ["!", ["has", "point_count"]], ["==", ["get", "species_group"], species]],
            paint: {
              "circle-color": POINT_COLORS[species],
              "circle-radius": ["interpolate", ["linear"], ["zoom"], 8, 1.8, 12, 3.4, 15, 5.6],
              "circle-opacity": 0.92,
              "circle-stroke-color": "#ffffff",
              "circle-stroke-width": 0.75
            }
          });
        });

        if (!map.hasImage(SELECTED_MARKER_IMAGE_ID)) {
          map.addImage(SELECTED_MARKER_IMAGE_ID, createSelectedBloomImageData());
        }

        map.addLayer({
          id: "tree-selected-halo",
          type: "circle",
          source: "trees",
          filter: ["==", ["get", "id"], "__none__"],
          paint: {
            "circle-color": "rgba(255, 250, 253, 0.86)",
            "circle-radius": ["interpolate", ["linear"], ["zoom"], 8, 6.5, 15, 10.5],
            "circle-opacity": 0.98,
            "circle-blur": 0.12
          }
        });

        map.addLayer({
          id: "tree-selected-star",
          type: "symbol",
          source: "trees",
          filter: ["==", ["get", "id"], "__none__"],
          layout: {
            "icon-image": SELECTED_MARKER_IMAGE_ID,
            "icon-size": ["interpolate", ["linear"], ["zoom"], 8, 0.26, 12, 0.34, 15, 0.42],
            "icon-allow-overlap": true,
            "icon-ignore-placement": true
          }
        });

        map.addSource(USER_LOCATION_SOURCE_ID, {
          type: "geojson",
          data: buildUserLocationData(null)
        });

        map.addLayer({
          id: "user-location-halo",
          type: "circle",
          source: USER_LOCATION_SOURCE_ID,
          paint: {
            "circle-color": "#48a7ff",
            "circle-radius": 14,
            "circle-opacity": 0.2
          }
        });

        map.addLayer({
          id: "user-location-dot",
          type: "circle",
          source: USER_LOCATION_SOURCE_ID,
          paint: {
            "circle-color": "#1976d2",
            "circle-radius": 6,
            "circle-stroke-color": "#ffffff",
            "circle-stroke-width": 2
          }
        });

        map.on("click", "tree-clusters", (event: MapLayerMouseEvent) => {
          const features = map.queryRenderedFeatures(event.point, { layers: ["tree-clusters"] });
          if (features.length === 0) {
            return;
          }

          const clusterId = features[0].properties?.cluster_id;
          const source = map.getSource("trees") as GeoJSONSource;
          if (clusterId == null || !source) {
            return;
          }

          void source
            .getClusterExpansionZoom(Number(clusterId))
            .then((zoom) => {
              const geometry = features[0].geometry;
              if (!geometry || geometry.type !== "Point") {
                return;
              }

              map.easeTo({
                center: geometry.coordinates as [number, number],
                zoom
              });
            })
            .catch(() => {
              // Ignore cluster expansion failures.
            });
        });

        map.on("click", (event: MapLayerMouseEvent) => {
          const clusterFeatures = map.queryRenderedFeatures(event.point, { layers: ["tree-clusters"] });
          if (clusterFeatures.length > 0) {
            return;
          }

          const features = map.queryRenderedFeatures(event.point, { layers: [...POINT_LAYER_IDS] });
          if (features.length === 0) {
            const coverageFeatures = map.queryRenderedFeatures(event.point, {
              layers: ["coverage-official-unavailable", "coverage-unavailable-outline"]
            });
            if (coverageFeatures.length === 0) {
              return;
            }

            const coverageProperties = coverageFeatures[0].properties;
            const jurisdiction = coverageProperties?.jurisdiction;
            if (!jurisdiction) {
              return;
            }

            setSelectedTree(null);
            setSelectedCoverage({
              coordinates: [event.lngLat.lng, event.lngLat.lat],
              properties: {
                id: String(coverageProperties.id ?? `coverage-${jurisdiction}`),
                status: "official_unavailable",
                jurisdiction: String(jurisdiction),
                note: String(coverageProperties.note ?? "")
              }
            });
            return;
          }

          const id = features[0].properties?.id;
          if (!id) {
            return;
          }

          const matched = filteredFeaturesRef.current.find((feature) => feature.properties.id === id);
          if (!matched) {
            return;
          }

          setSelectedTree({
            coordinates: getTreeCoordinates(matched),
            properties: matched.properties
          });
          setSelectedCoverage(null);
          if (!isDesktopRef.current) {
            setSheetHeight(0.72);
            setActivePanel("filters");
          }
        });

        map.on("mouseenter", "tree-clusters", () => {
          map.getCanvas().style.cursor = "pointer";
        });
        map.on("mouseleave", "tree-clusters", () => {
          map.getCanvas().style.cursor = "";
        });

        POINT_LAYER_IDS.forEach((layerId) => {
          map.on("mouseenter", layerId, () => {
            map.getCanvas().style.cursor = "pointer";
          });

          map.on("mouseleave", layerId, () => {
            map.getCanvas().style.cursor = "";
          });
        });

        ["coverage-official-unavailable", "coverage-unavailable-outline"].forEach((layerId) => {
          map.on("mouseenter", layerId, () => {
            map.getCanvas().style.cursor = "pointer";
          });

          map.on("mouseleave", layerId, () => {
            map.getCanvas().style.cursor = "";
          });
        });

        map.on("moveend", () => {
          const center = map.getCenter();
          setMapView({
            zoom: Number(map.getZoom().toFixed(2)),
            lat: Number(center.lat.toFixed(5)),
            lon: Number(center.lng.toFixed(5))
          });
        });

        if (!initialUrlState.hasViewportParam) {
          const defaultBounds = boundsForRegion(activeRegionMeta);
          if (defaultBounds) {
            map.fitBounds(defaultBounds, {
              padding: isDesktopRef.current ? 80 : 48,
              duration: 0
            });
            const center = map.getCenter();
            setMapView({
              zoom: Number(map.getZoom().toFixed(2)),
              lat: Number(center.lat.toFixed(5)),
              lon: Number(center.lng.toFixed(5))
            });
          }
        }
        });
      } catch (mapError) {
        console.error("map-init-failed", mapError);
        if (!isCancelled) {
          setError(mapError instanceof Error ? mapError.message : "Failed to initialize map.");
        }
      }
    })();

    return () => {
      isCancelled = true;
      popupRef.current?.remove();
      popupRef.current = null;
      if (mapInstance) {
        mapInstance.remove();
      }
      if (mapRef.current === mapInstance) {
        mapRef.current = null;
      }
    };
  }, [
    loading,
    activeRegionPending,
    data,
    displayCoverage,
    activeRegionMeta,
    initialUrlState.hasViewportParam,
    initialUrlState.lat,
    initialUrlState.lon,
    initialUrlState.zoom,
    mapRuntime
  ]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapRuntime) {
      return;
    }
    const source = map.getSource("trees") as GeoJSONSource | undefined;
    if (source) {
      source.setData(filteredCollection);
    }

    if (selectedTree && !filteredFeatures.find((feature) => feature.properties.id === selectedTree.properties.id)) {
      setSelectedTree(null);
    }
  }, [filteredCollection, filteredFeatures, selectedTree]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) {
      return;
    }

    const source = map.getSource("coverage") as GeoJSONSource | undefined;
    if (source) {
      source.setData(displayCoverage);
    }
  }, [displayCoverage]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) {
      return;
    }

    const selectedId = selectedTree?.properties.id ?? "__none__";
    if (map.getLayer("tree-selected-halo")) {
      map.setFilter("tree-selected-halo", ["==", ["get", "id"], selectedId]);
    }
    if (map.getLayer("tree-selected-star")) {
      map.setFilter("tree-selected-star", ["==", ["get", "id"], selectedId]);
    }
  }, [selectedTree]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) {
      return;
    }

    const source = map.getSource(USER_LOCATION_SOURCE_ID) as GeoJSONSource | undefined;
    if (source) {
      source.setData(buildUserLocationData(userLocation));
    }
  }, [userLocation]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapRuntime) {
      return;
    }
    const runtime = mapRuntime;

    popupRef.current?.remove();
    popupRef.current = null;

    if (selectedTree) {
      const [lon, lat] = selectedTree.coordinates;
      const subtypeLine = selectedTree.properties.subtype_name
        ? `<p><strong>${escapeHtml(t(language, "subtype"))}:</strong> ${escapeHtml(selectedTree.properties.subtype_name)}</p>`
        : "";
      const popupHtml = `
        <div class="tree-popup-card">
          <h4>${escapeHtml(speciesLabel(language, selectedTree.properties.species_group))}</h4>
          ${subtypeLine}
          <p>${escapeHtml(selectedTree.properties.scientific_name)}</p>
          <p><strong>${escapeHtml(t(language, "city"))}:</strong> ${escapeHtml(selectedTree.properties.city)}</p>
          <p><strong>${escapeHtml(t(language, "zipCode"))}:</strong> ${escapeHtml(selectedTree.properties.zip_code ?? t(language, "unknown"))}</p>
          <p><strong>${escapeHtml(t(language, "coordinates"))}:</strong> ${lon.toFixed(5)}, ${lat.toFixed(5)}</p>
        </div>
      `;

      const popup = new runtime.maplibre.Popup({
        closeButton: true,
        closeOnClick: false,
        offset: 14,
        maxWidth: "300px",
        className: "tree-popup"
      })
        .setLngLat(selectedTree.coordinates)
        .setHTML(popupHtml)
        .addTo(map);

      popup.on("close", () => {
        setSelectedTree((current) =>
          current && current.properties.id === selectedTree.properties.id ? null : current
        );
      });

      popupRef.current = popup;
      return;
    }

    if (!selectedCoverage) {
      return;
    }

    const popupHtml = `
      <div class="coverage-popup-card">
        <h4>${escapeHtml(selectedCoverage.properties.jurisdiction)}</h4>
        <p class="coverage-popup-eyebrow">${escapeHtml(t(language, "officialUnavailablePopupTitle"))}</p>
        <p>${escapeHtml(t(language, "officialUnavailablePopupBody"))}</p>
        <p>${escapeHtml(t(language, "officialUnavailablePopupFoot"))}</p>
      </div>
    `;

    const popup = new runtime.maplibre.Popup({
      closeButton: true,
      closeOnClick: false,
      offset: 12,
      maxWidth: "320px",
      className: "coverage-popup"
    })
      .setLngLat(selectedCoverage.coordinates)
      .setHTML(popupHtml)
      .addTo(map);

    popup.on("close", () => {
      setSelectedCoverage((current) =>
        current && current.properties.id === selectedCoverage.properties.id ? null : current
      );
    });

    popupRef.current = popup;
  }, [language, mapRuntime, selectedCoverage, selectedTree]);

  useEffect(() => {
    if (!data) {
      return;
    }

    const params = new URLSearchParams();
    params.set("region", activeRegion);
    params.set("lang", language);

    if (selectedSpecies.length === 0) {
      params.set("species", "none");
    } else if (selectedSpecies.length !== ALL_SPECIES.length) {
      params.set("species", selectedSpecies.join(","));
    }

    if (selectedOwnership.length === 0) {
      params.set("ownership", "none");
    } else if (selectedOwnership.length !== allOwnershipOptions.length) {
      params.set("ownership", selectedOwnership.join(","));
    }

    if (selectedCities.length === 0) {
      params.set("city", "none");
    } else if (selectedCities.length !== cities.length) {
      params.set("city", selectedCities.join(","));
    }

    if (selectedZipCodes.length === 0) {
      params.set("zip", "none");
    } else if (selectedZipCodes.length !== zipCodes.length) {
      params.set("zip", selectedZipCodes.join(","));
    }

    params.set("z", mapView.zoom.toString());
    params.set("lat", mapView.lat.toString());
    params.set("lon", mapView.lon.toString());

    const nextUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState(null, "", nextUrl);
  }, [
    activeRegion,
    allOwnershipOptions.length,
    cities.length,
    data,
    language,
    mapView,
    selectedCities,
    selectedOwnership,
    selectedSpecies,
    selectedZipCodes,
    zipCodes.length
  ]);

  function toggleSpecies(species: SpeciesGroup): void {
    setSelectedSpecies((current) => {
      if (current.includes(species)) {
        return current.filter((item) => item !== species);
      }
      return [...current, species];
    });
  }

  function toggleOwnership(ownership: OwnershipGroup): void {
    setSelectedOwnership((current) => {
      if (current.includes(ownership)) {
        return current.filter((item) => item !== ownership);
      }
      return [...current, ownership];
    });
  }

  function toggleCity(city: string): void {
    const isSelected = selectedCities.includes(city);
    const nextCities = isSelected ? selectedCities.filter((item) => item !== city) : [...selectedCities, city];
    const nextOwnership =
      allOwnershipOptions.length > 0 ? [...allOwnershipOptions] : (["public", "private"] as OwnershipGroup[]);

    setSelectedCities(nextCities);
    setSelectedZipCodes((current) => {
      if (!isSelected) {
        const nextZipCodes = new Set(current);
        (zipCodesByCity.get(city) ?? []).forEach((zipCode) => nextZipCodes.add(zipCode));
        return sortZipCodesByMasterOrder(nextZipCodes, zipCodes);
      }

      if (nextCities.length === 0) {
        return [];
      }

      const allowedZipCodes = new Set(nextCities.flatMap((item) => zipCodesByCity.get(item) ?? []));
      return sortZipCodesByMasterOrder(
        current.filter((zipCode) => allowedZipCodes.has(zipCode)),
        zipCodes
      );
    });

    if (!isSelected) {
      if (selectedSpecies.length === 0) {
        setSelectedSpecies([...ALL_SPECIES]);
      }
      if (selectedOwnership.length === 0) {
        setSelectedOwnership(nextOwnership);
      }
    }
  }

  function toggleZipCode(zipCode: string): void {
    setSelectedZipCodes((current) => {
      if (current.includes(zipCode)) {
        return current.filter((item) => item !== zipCode);
      }
      return [...current, zipCode];
    });
  }

  function toggleLanguage(): void {
    setLanguage((current) => (current === "zh-CN" ? "en-US" : "zh-CN"));
  }

  function zoomInMap(): void {
    setGlobalMenuOpen(false);
    mapRef.current?.zoomIn({ duration: 220 });
  }

  function zoomOutMap(): void {
    setGlobalMenuOpen(false);
    mapRef.current?.zoomOut({ duration: 220 });
  }

  function locateNearbyTrees(): void {
    setGlobalMenuOpen(false);
    if (!navigator.geolocation || !mapRef.current) {
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const nextCenter: [number, number] = [position.coords.longitude, position.coords.latitude];
        setUserLocation(nextCenter);
        mapRef.current?.easeTo({
          center: nextCenter,
          zoom: Math.max(mapRef.current.getZoom(), 14)
        });
      },
      () => {
        // Ignore location errors in UI to avoid intrusive permission edge cases.
      },
      {
        enableHighAccuracy: true,
        timeout: 10_000
      }
    );
  }

  function switchRegion(region: CoverageRegion): void {
    const regionMeta = regionMetaById.get(region) ?? null;
    if (!regionMeta?.available) {
      return;
    }

    setGlobalMenuOpen(false);
    setSelectedTree(null);
    setSelectedCoverage(null);
    setCityDropdownOpen(false);
    setZipDropdownOpen(false);
    const cachedTrees = regionTreeCache[region];
    if (cachedTrees) {
      setSelectedCities(getCitiesForTrees(cachedTrees));
      setSelectedZipCodes(getZipCodesForTrees(cachedTrees));
      pendingRegionResetRef.current = null;
    } else {
      setSelectedCities([]);
      setSelectedZipCodes([]);
      pendingRegionResetRef.current = region;
    }
    setActiveRegion(region);

    const bounds = boundsForRegion(regionMeta);
    if (mapRef.current && bounds) {
      mapRef.current.fitBounds(bounds, {
        padding: isDesktop ? 80 : 48,
        duration: 700
      });
    }
  }

  function showAllFilters(): void {
    const nextOwnership =
      allOwnershipOptions.length > 0 ? [...allOwnershipOptions] : (["public", "private"] as OwnershipGroup[]);
    setSelectedSpecies([...ALL_SPECIES]);
    setSelectedCities([...cities]);
    setSelectedZipCodes([...zipCodes]);
    setSelectedOwnership(nextOwnership);
    setSelectedTree(null);
    setSelectedCoverage(null);
    setCityDropdownOpen(false);
    setZipDropdownOpen(false);
  }

  function clearAllFilters(): void {
    setSelectedSpecies([]);
    setSelectedCities([]);
    setSelectedZipCodes([]);
    setSelectedOwnership([]);
    setSelectedTree(null);
    setSelectedCoverage(null);
    setCityDropdownOpen(false);
    setZipDropdownOpen(false);
  }

  function toggleGlobalMenu(): void {
    setGlobalMenuOpen((current) => !current);
  }

  function handleSheetPointerDown(event: ReactPointerEvent<HTMLButtonElement>): void {
    dragStateRef.current = {
      startY: event.clientY,
      startHeight: sheetHeight,
      dragging: true
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function handleSheetPointerMove(event: ReactPointerEvent<HTMLButtonElement>): void {
    if (!dragStateRef.current.dragging) {
      return;
    }

    const delta = (dragStateRef.current.startY - event.clientY) / window.innerHeight;
    const nextHeight = Math.min(1, Math.max(0.4, dragStateRef.current.startHeight + delta));
    setSheetHeight(nextHeight);
  }

  function handleSheetPointerUp(event: ReactPointerEvent<HTMLButtonElement>): void {
    if (!dragStateRef.current.dragging) {
      return;
    }
    dragStateRef.current.dragging = false;
    event.currentTarget.releasePointerCapture(event.pointerId);
    setSheetHeight((current) => nearestSnap(current));
  }

  if (loading || activeRegionPending) {
    return (
      <div className="loading-screen">
        <div className="loading-shell" />
        <p>{t(language, "loading")}</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="loading-screen">
        <p>{error ?? "Failed to load data."}</p>
      </div>
    );
  }

  return (
    <div className={isDesktop ? "app-root desktop-mode" : "app-root mobile-mode"}>
      <div className="map-root" ref={mapContainerRef} />
      <section className="map-corner-legend">
        <div className="legend-row">
          <span className="legend-dot covered" />
          <span>{t(language, "coveredLegend")}</span>
        </div>
        <div className="legend-row">
          <span className="legend-dot official-unavailable" />
          <span>{t(language, "officialUnavailableLegend")}</span>
        </div>
        {mapStylePreset === "demotiles" && <p>{t(language, "fallbackBasemap")}</p>}
      </section>

      <section
        className="map-left-controls"
        style={isDesktop ? undefined : { bottom: `calc(${sheetHeight * 100}vh + 0.75rem)` }}
      >
        {globalMenuOpen && (
          <div className="map-global-menu" role="menu">
            {GLOBAL_REGION_OPTIONS.map((option) => (
              <button
                key={option.region}
                className="map-global-option"
                disabled={!regionMetaById.get(option.region)?.available}
                onClick={() => switchRegion(option.region)}
                type="button"
              >
                {option.label}
              </button>
            ))}
          </div>
        )}
        <div className="map-left-controls-stack">
          <button
            aria-label={t(language, "expand")}
            className="map-action-btn"
            onClick={zoomInMap}
            title={t(language, "expand")}
            type="button"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24">
              <path
                d="M12 6.4v11.2M6.4 12h11.2"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeWidth="2.35"
              />
            </svg>
          </button>
          <button
            aria-label={t(language, "collapse")}
            className="map-action-btn"
            onClick={zoomOutMap}
            title={t(language, "collapse")}
            type="button"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24">
              <path d="M6.4 12h11.2" fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth="2.35" />
            </svg>
          </button>
          <button
            aria-label={t(language, "fitCoverage")}
            className={globalMenuOpen ? "map-action-btn active" : "map-action-btn"}
            onClick={toggleGlobalMenu}
            title={t(language, "fitCoverage")}
            type="button"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24">
              <path
                d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2.35"
              />
            </svg>
          </button>
          <button
            aria-label={t(language, "locateNearby")}
            className="map-action-btn"
            onClick={locateNearbyTrees}
            title={t(language, "locateNearby")}
            type="button"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24">
              <circle cx="12" cy="12" fill="none" r="3.2" stroke="currentColor" strokeWidth="2.35" />
              <path
                d="M12 3.5v3.1M12 17.4v3.1M3.5 12h3.1M17.4 12h3.1"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeWidth="2.35"
              />
            </svg>
          </button>
        </div>
      </section>

      <section className="sheet" style={isDesktop ? undefined : { height: `${sheetHeight * 100}vh` }}>
        <button
          className="sheet-handle"
          onPointerDown={handleSheetPointerDown}
          onPointerMove={handleSheetPointerMove}
          onPointerUp={handleSheetPointerUp}
          type="button"
          aria-label="Resize panel"
        >
          <span />
        </button>

        <div className="sheet-content">
          <section className="panel-header-card">
            <div className="panel-header-top">
            <div className="panel-title-group">
                <h1>{t(language, "appTitle")}</h1>
                <p>{t(language, "appSubtitle")}</p>
              </div>
              <button className="icon-btn language-btn" onClick={toggleLanguage} type="button">
                {t(language, "language")}
              </button>
            </div>
          </section>

          <div className="sheet-toolbar">
            <button
              className={activePanel === "filters" ? "tab-btn active" : "tab-btn"}
              onClick={() => setActivePanel("filters")}
              type="button"
            >
              {t(language, "showList")}
            </button>
            <button
              className={activePanel === "guide" ? "tab-btn active" : "tab-btn"}
              onClick={() => setActivePanel("guide")}
              type="button"
            >
              {t(language, "showGuide")}
            </button>
            <button
              className={activePanel === "about" ? "tab-btn active" : "tab-btn"}
              onClick={() => setActivePanel("about")}
              type="button"
            >
              {t(language, "showAbout")}
            </button>
            <div className="record-count">
              {filteredFeatures.length.toLocaleString()} {t(language, "records")}
            </div>
          </div>

          {activePanel === "filters" ? (
            <>
              <section className="filters">
                <div className="filters-heading">
                  <h3>{t(language, "filtersTitle")}</h3>
                  <div className="filter-actions">
                    <button className="clear-btn show-all-btn" onClick={showAllFilters} type="button">
                      {t(language, "showAll")}
                    </button>
                    <button className="clear-btn" onClick={clearAllFilters} type="button">
                      {t(language, "clearAll")}
                    </button>
                  </div>
                </div>

                <div className="filter-group">
                  <strong>{t(language, "speciesFilter")}</strong>
                  <div className="chip-wrap">
                    {ALL_SPECIES.map((species) => (
                      <button
                        key={species}
                        className={selectedSpecies.includes(species) ? "chip active" : "chip"}
                        onClick={() => toggleSpecies(species)}
                        type="button"
                      >
                        {speciesLabel(language, species)}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="filter-group">
                  <strong>{t(language, "cityFilter")}</strong>
                  <button
                    aria-expanded={cityDropdownOpen}
                    className="filter-dropdown-trigger"
                    onClick={() => setCityDropdownOpen((current) => !current)}
                    type="button"
                  >
                    <span>
                      {t(language, "cityFilter")} ({selectedCities.length}/{cities.length})
                    </span>
                    <span className={cityDropdownOpen ? "caret open" : "caret"} />
                  </button>
                  {cityDropdownOpen && (
                    <div className="filter-dropdown-menu">
                      <input
                        className="filter-search-input"
                        onChange={(event) => setCitySearchQuery(event.target.value)}
                        placeholder={t(language, "searchCityPlaceholder")}
                        type="search"
                        value={citySearchQuery}
                      />
                      {visibleCities.map(({ city, label }) => (
                        <label className="filter-option" key={city}>
                          <input
                            checked={selectedCities.includes(city)}
                            onChange={() => toggleCity(city)}
                            type="checkbox"
                          />
                          <span>{label}</span>
                        </label>
                      ))}
                      {visibleCities.length === 0 && (
                        <p className="filter-empty">{t(language, "noResultsBody")}</p>
                      )}
                    </div>
                  )}
                </div>

                <div className="filter-group">
                  <strong>{t(language, "zipFilter")}</strong>
                  <button
                    aria-expanded={zipDropdownOpen}
                    className="filter-dropdown-trigger"
                    onClick={() => setZipDropdownOpen((current) => !current)}
                    type="button"
                  >
                    <span>
                      {t(language, "zipFilter")} ({selectedZipCodes.length}/{zipCodes.length})
                    </span>
                    <span className={zipDropdownOpen ? "caret open" : "caret"} />
                  </button>
                  {zipDropdownOpen && (
                    <div className="filter-dropdown-menu">
                      <input
                        className="filter-search-input"
                        onChange={(event) => setZipSearchQuery(event.target.value)}
                        placeholder={t(language, "searchZipPlaceholder")}
                        type="search"
                        value={zipSearchQuery}
                      />
                      {visibleZipCodes.map((zipCode) => (
                        <label className="filter-option" key={zipCode}>
                          <input
                            checked={selectedZipCodes.includes(zipCode)}
                            onChange={() => toggleZipCode(zipCode)}
                            type="checkbox"
                          />
                          <span>{zipCode === "unknown" ? t(language, "unknown") : zipCode}</span>
                        </label>
                      ))}
                      {visibleZipCodes.length === 0 && (
                        <p className="filter-empty">{t(language, "noResultsBody")}</p>
                      )}
                    </div>
                  )}
                </div>

                <div className="filter-group">
                  <strong>{t(language, "ownershipFilter")}</strong>
                  <div className="chip-wrap">
                    {ownershipOptions.map((item) => (
                      <button
                        key={item}
                        className={selectedOwnership.includes(item) ? "chip active" : "chip"}
                        onClick={() => toggleOwnership(item)}
                        type="button"
                      >
                        {ownershipLabel(language, item)}
                      </button>
                    ))}
                  </div>
                </div>
              </section>
              {filteredFeatures.length === 0 ? (
                <div className="empty-state">
                  <img
                    src="/assets/ui/placeholders/empty_state_spring_tree.svg"
                    alt="No results"
                    loading="lazy"
                  />
                  <h4>{t(language, "noResultsTitle")}</h4>
                  <p>{t(language, "noResultsBody")}</p>
                </div>
              ) : (
                <p className="selection-hint">{t(language, "tapTreeHint")}</p>
              )}

              {selectedTree && (
                <article className="tree-card selected">
                  <header>
                    <span className="badge">{t(language, "selectedTree")}</span>
                    <h4>{speciesLabel(language, selectedTree.properties.species_group)}</h4>
                  </header>
                  {selectedTree.properties.subtype_name && (
                    <p>
                      <strong>{t(language, "subtype")}: </strong>
                      {selectedTree.properties.subtype_name}
                    </p>
                  )}
                  <p>
                    <strong>{t(language, "scientific")}: </strong>
                    {selectedTree.properties.scientific_name}
                  </p>
                  <p>
                    <strong>{t(language, "common")}: </strong>
                    {selectedTree.properties.common_name ?? t(language, "unknown")}
                  </p>
                  <p>
                    <strong>{t(language, "zipCode")}: </strong>
                    {selectedTree.properties.zip_code ?? t(language, "unknown")}
                  </p>
                  <p>
                    <strong>{t(language, "ownership")}: </strong>
                    {ownershipLabel(language, selectedTree.properties.ownership)} (
                    {selectedTree.properties.ownership_raw})
                  </p>
                  <p>
                    <strong>{t(language, "coordinates")}: </strong>
                    {selectedTree.coordinates[0].toFixed(5)}, {selectedTree.coordinates[1].toFixed(5)}
                  </p>
                  <p>
                    <strong>{t(language, "source")}: </strong>
                    {selectedTree.properties.source_department}
                  </p>
                </article>
              )}
            </>
          ) : activePanel === "guide" ? (
            <section className="guide-panel">
              <h3>{t(language, "guideTitle")}</h3>
              {data.guide.entries.map((entry) => (
                <article className="guide-card" key={entry.id}>
                  <header>
                    <h4>{entry.title[language]}</h4>
                    <p>{entry.subtitle[language]}</p>
                  </header>
                  <ul>
                    {entry.bullets[language].map((bullet) => (
                      <li key={bullet}>{bullet}</li>
                    ))}
                  </ul>
                  <p className="tips-title">{t(language, "tipsTitle")}</p>
                  <ul>
                    {entry.confusionTips[language].map((tip) => (
                      <li key={tip}>{tip}</li>
                    ))}
                  </ul>
                </article>
              ))}
            </section>
          ) : (
            <section className="about-panel">
              <div className="about-section">
                <h3 className="about-section-title">{aboutCopy.title}</h3>
                <article className="about-card">
                  {aboutCopy.intro.map((paragraph) => (
                    <p key={paragraph}>{paragraph}</p>
                  ))}
                </article>
              </div>

              <div className="about-section">
                <h3 className="about-section-title">{aboutCopy.sourcesTitle}</h3>
                <article className="about-card about-sources-shell">
                  <div className="about-source-list">
                    {pagedAboutSources.map((source) => {
                      const supplemental = source.name === "UW OSM Supplemental" || !isHttpUrl(source.endpoint);
                      return (
                        <div className="about-source-item" key={`${source.city}-${source.name}`}>
                          <div className="about-source-head">
                            <div className="about-source-title-block">
                              <div className="about-source-title-row">
                                <strong>
                                  {source.city}: {source.name}
                                </strong>
                                {isHttpUrl(source.endpoint) ? (
                                  <a
                                    aria-label={aboutCopy.openLink}
                                    className="source-link-icon"
                                    href={source.endpoint}
                                    rel="noreferrer"
                                    target="_blank"
                                  >
                                    <svg aria-hidden="true" viewBox="0 0 24 24">
                                      <path
                                        d="M8 16 16 8M10 8h6v6"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth="2"
                                      />
                                      <path
                                        d="M16 13v5H5V7h5"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth="2"
                                      />
                                    </svg>
                                  </a>
                                ) : null}
                              </div>
                              <span className={supplemental ? "source-badge supplemental" : "source-badge official"}>
                                {supplemental ? aboutCopy.supplementalBadge : aboutCopy.officialBadge}
                              </span>
                            </div>
                          </div>
                          {!isHttpUrl(source.endpoint) && <p>{source.endpoint}</p>}
                        </div>
                      );
                    })}
                  </div>
                  {aboutSources.length > 0 && (
                    <div className="about-source-pagination">
                      <button
                        className="clear-btn"
                        disabled={aboutSourcesPage === 0}
                        onClick={() => setAboutSourcesPage((current) => Math.max(0, current - 1))}
                        type="button"
                      >
                        {aboutCopy.previousPage}
                      </button>
                      <span>
                        {aboutCopy.pageLabel} {aboutSourcesPage + 1} / {aboutSourcePageCount}
                      </span>
                      <button
                        className="clear-btn"
                        disabled={aboutSourcesPage >= aboutSourcePageCount - 1}
                        onClick={() =>
                          setAboutSourcesPage((current) => Math.min(aboutSourcePageCount - 1, current + 1))
                        }
                        type="button"
                      >
                        {aboutCopy.nextPage}
                      </button>
                    </div>
                  )}
                </article>
              </div>

              <div className="about-section">
                <h3 className="about-section-title">{aboutCopy.disclaimerTitle}</h3>
                <article className="about-card">
                  {aboutCopy.disclaimer.map((paragraph) => (
                    <p key={paragraph}>{paragraph}</p>
                  ))}
                </article>
              </div>

              <div className="about-section">
                <h3 className="about-section-title">{aboutCopy.contactTitle}</h3>
                <article className="about-card">
                  <p>{aboutCopy.contactLead}</p>
                  <p>
                    <a className="about-contact-email" href="mailto:flalaz@uw.edu">
                      flalaz@uw.edu
                    </a>
                  </p>
                </article>
              </div>
            </section>
          )}

          <footer className="meta-row">
            {t(language, "dataUpdated")}: {new Date(data.meta.generated_at).toLocaleString(language)}
          </footer>
        </div>
      </section>
    </div>
  );
}
