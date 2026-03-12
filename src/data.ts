import type {
  AreaIndex,
  CoverageCollection,
  FeaturedAreaDetail,
  FeaturedAreaIndex,
  RegionMeta,
  JumpIndex,
  SpeciesGuide,
  AppMeta,
  StaticAppData,
  TreeRenderTilesManifest,
  TreeCollection,
  WeatherSnapshot,
  VisitorCountHitResponse,
  VisitorCountReadResponse
} from "./types";
import { resolveDataUrl, resolveVisitorApiUrl, runtimeConfig, shouldCountVisitor } from "./runtimeConfig";

async function loadJson<T>(path: string): Promise<T> {
  const response = await fetch(resolveDataUrl(path));
  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status}`);
  }
  return (await response.json()) as T;
}

const OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast";
const WEATHER_SESSION_PREFIX = "pink-hunter-featured-weather:";
const WEATHER_CACHE_TTL_MS = 30 * 60 * 1000;

export async function loadStaticAppData(): Promise<StaticAppData> {
  const [featuredAreas, guide, meta, jumpIndex, treeTiles] = await Promise.all([
    loadJson<FeaturedAreaIndex>("/data/featured-areas.v1.json"),
    loadJson<SpeciesGuide>("/data/species-guide.v1.json"),
    loadJson<AppMeta>("/data/meta.v2.json"),
    loadJson<JumpIndex>("/data/jump-index.v1.json"),
    runtimeConfig.treeRenderMode === "pmtiles"
      ? loadJson<TreeRenderTilesManifest>("/data/trees.render.v1.json").catch(() => null)
      : Promise.resolve(null)
  ]);

  const coverage =
    runtimeConfig.coverageLoadMode === "eager_all"
      ? await loadJson<CoverageCollection>("/data/coverage.v1.geojson")
      : null;

  return { coverage, featuredAreas, guide, meta, jumpIndex, treeTiles };
}

export async function loadTreeCollection(path: string): Promise<TreeCollection> {
  return loadJson<TreeCollection>(path);
}

export async function loadAreaIndex(path: string): Promise<AreaIndex> {
  return loadJson<AreaIndex>(path);
}

export async function loadFeaturedAreaDetail(path: string): Promise<FeaturedAreaDetail> {
  return loadJson<FeaturedAreaDetail>(path);
}

export async function loadCoverageRegion(regionMeta: RegionMeta): Promise<CoverageCollection> {
  const coveragePath = regionMeta.coverage_path;
  if (!coveragePath) {
    return {
      type: "FeatureCollection",
      features: []
    };
  }
  return loadJson<CoverageCollection>(coveragePath);
}

const VISITOR_COUNTER_SESSION_KEY = "pink-hunter-visitor-counted";
const VISITOR_ID_STORAGE_KEY = "pink-hunter-visitor-id";

function buildWeatherCacheKey(areaId: string): string {
  return `${WEATHER_SESSION_PREFIX}${areaId}`;
}

function readCachedWeather(areaId: string): WeatherSnapshot | null {
  if (typeof window === "undefined") {
    return null;
  }

  const raw = window.sessionStorage.getItem(buildWeatherCacheKey(areaId));
  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw) as WeatherSnapshot;
    const fetchedAtMs = Date.parse(parsed.fetched_at);
    if (!Number.isFinite(fetchedAtMs) || Date.now() - fetchedAtMs > WEATHER_CACHE_TTL_MS) {
      window.sessionStorage.removeItem(buildWeatherCacheKey(areaId));
      return null;
    }
    return parsed;
  } catch {
    window.sessionStorage.removeItem(buildWeatherCacheKey(areaId));
    return null;
  }
}

function writeCachedWeather(snapshot: WeatherSnapshot): void {
  if (typeof window === "undefined") {
    return;
  }
  window.sessionStorage.setItem(buildWeatherCacheKey(snapshot.area_id), JSON.stringify(snapshot));
}

function readBrowserHostname(): string {
  return typeof window !== "undefined" ? window.location.hostname.toLowerCase() : "";
}

function shouldRespectBrowserPrivacySignals(): boolean {
  if (typeof navigator === "undefined" || typeof window === "undefined") {
    return false;
  }

  const browserNavigator = navigator as Navigator & {
    globalPrivacyControl?: boolean;
    msDoNotTrack?: string | null;
  };
  const browserWindow = window as Window & {
    doNotTrack?: string | null;
  };

  return (
    browserNavigator.globalPrivacyControl === true ||
    browserNavigator.doNotTrack === "1" ||
    browserNavigator.doNotTrack === "yes" ||
    browserNavigator.msDoNotTrack === "1" ||
    browserWindow.doNotTrack === "1"
  );
}

function getOrCreateVisitorId(): string {
  if (typeof window === "undefined") {
    return "server-render";
  }

  const existing = window.localStorage.getItem(VISITOR_ID_STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const visitorId = window.crypto?.randomUUID?.() ?? `visitor-${Date.now()}-${Math.round(Math.random() * 1e9)}`;
  window.localStorage.setItem(VISITOR_ID_STORAGE_KEY, visitorId);
  return visitorId;
}

async function loadCounterApiVisitorCount(): Promise<number | null> {
  if (shouldRespectBrowserPrivacySignals()) {
    return null;
  }

  const hostname = readBrowserHostname();
  const shouldIncrement = shouldCountVisitor(hostname);
  const alreadyCounted =
    typeof window !== "undefined" && window.sessionStorage.getItem(VISITOR_COUNTER_SESSION_KEY) === "1";
  const path =
    shouldIncrement && !alreadyCounted
      ? `${runtimeConfig.counterApiBaseUrl}/up`
      : `${runtimeConfig.counterApiBaseUrl}/`;
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Failed to fetch visitor count: ${response.status}`);
  }
  const payload = (await response.json()) as VisitorCountReadResponse;
  if (shouldIncrement && !alreadyCounted && typeof window !== "undefined") {
    window.sessionStorage.setItem(VISITOR_COUNTER_SESSION_KEY, "1");
  }
  return payload.count;
}

async function loadAwsVisitorCount(): Promise<number | null> {
  if (shouldRespectBrowserPrivacySignals()) {
    return null;
  }

  if (!runtimeConfig.visitorApiBaseUrl) {
    throw new Error("Missing VITE_VISITOR_API_BASE_URL for AWS visitor counter.");
  }

  const hostname = readBrowserHostname();
  const shouldIncrement = shouldCountVisitor(hostname);
  if (!shouldIncrement) {
    const response = await fetch(resolveVisitorApiUrl("/api/v1/visitor-count"));
    if (!response.ok) {
      throw new Error(`Failed to read visitor count: ${response.status}`);
    }
    const payload = (await response.json()) as VisitorCountReadResponse;
    return payload.count;
  }

  const response = await fetch(resolveVisitorApiUrl("/api/v1/visitor-count/hit"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      visitorId: getOrCreateVisitorId(),
      pathname: typeof window !== "undefined" ? window.location.pathname : "/"
    })
  });

  if (!response.ok) {
    throw new Error(`Failed to update visitor count: ${response.status}`);
  }

  const payload = (await response.json()) as VisitorCountHitResponse;
  if (typeof window !== "undefined") {
    window.sessionStorage.setItem(VISITOR_COUNTER_SESSION_KEY, "1");
  }
  return payload.count;
}

export async function loadVisitorCount(): Promise<number | null> {
  return runtimeConfig.visitorCounterMode === "aws_api"
    ? loadAwsVisitorCount()
    : loadCounterApiVisitorCount();
}

export async function loadFeaturedAreaWeather(
  areaId: string,
  latitude: number,
  longitude: number
): Promise<WeatherSnapshot> {
  const cached = readCachedWeather(areaId);
  if (cached) {
    return cached;
  }

  const url = new URL(OPEN_METEO_FORECAST_URL);
  url.searchParams.set("latitude", latitude.toFixed(5));
  url.searchParams.set("longitude", longitude.toFixed(5));
  url.searchParams.set(
    "daily",
    ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"].join(",")
  );
  url.searchParams.set("forecast_days", "10");
  url.searchParams.set("past_days", "3");
  url.searchParams.set("timezone", "auto");

  const payload = await fetchJson<{
    timezone?: string;
    daily?: {
      time?: string[];
      weather_code?: number[];
      temperature_2m_max?: number[];
      temperature_2m_min?: number[];
      precipitation_probability_max?: Array<number | null>;
    };
  }>(url.toString());

  const times = payload.daily?.time ?? [];
  const weatherCodes = payload.daily?.weather_code ?? [];
  const maxTemps = payload.daily?.temperature_2m_max ?? [];
  const minTemps = payload.daily?.temperature_2m_min ?? [];
  const precipitation = payload.daily?.precipitation_probability_max ?? [];

  const snapshot: WeatherSnapshot = {
    area_id: areaId,
    fetched_at: new Date().toISOString(),
    latitude,
    longitude,
    timezone: payload.timezone ?? "auto",
    days: times.map((date, index) => ({
      date,
      weather_code: Number(weatherCodes[index] ?? 0),
      temperature_max_c: Number(maxTemps[index] ?? 0),
      temperature_min_c: Number(minTemps[index] ?? 0),
      precipitation_probability_max:
        precipitation[index] === null || precipitation[index] === undefined
          ? null
          : Number(precipitation[index])
    }))
  };

  writeCachedWeather(snapshot);
  return snapshot;
}
