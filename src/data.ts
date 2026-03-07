import type {
  CoverageCollection,
  SpeciesGuide,
  AppMeta,
  RegionCityDataIndex,
  StaticAppData,
  TreeCollection
} from "./types";

async function loadJson<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function loadStaticAppData(): Promise<StaticAppData> {
  const [coverage, guide, meta] = await Promise.all([
    loadJson<CoverageCollection>("/data/coverage.v1.geojson"),
    loadJson<SpeciesGuide>("/data/species-guide.v1.json"),
    loadJson<AppMeta>("/data/meta.v2.json")
  ]);

  return { coverage, guide, meta };
}

export async function loadTreeCollection(path: string): Promise<TreeCollection> {
  return loadJson<TreeCollection>(path);
}

export async function loadRegionCityIndex(path: string): Promise<RegionCityDataIndex> {
  return loadJson<RegionCityDataIndex>(path);
}

interface VisitorCounterResponse {
  count: number;
}

const VISITOR_COUNTER_BASE_URL = "https://api.counterapi.dev/v1/pink-hunter/pinkhunter-flalaz-com";
const VISITOR_COUNTER_SESSION_KEY = "pink-hunter-visitor-counted";
const PRODUCTION_HOSTS = new Set(["pinkhunter.flalaz.com"]);

export async function loadVisitorCount(): Promise<number> {
  const hostname =
    typeof window !== "undefined" ? window.location.hostname.toLowerCase() : "";
  const shouldIncrement = PRODUCTION_HOSTS.has(hostname);
  const alreadyCounted =
    typeof window !== "undefined" && window.sessionStorage.getItem(VISITOR_COUNTER_SESSION_KEY) === "1";
  const path = shouldIncrement && !alreadyCounted ? `${VISITOR_COUNTER_BASE_URL}/up` : `${VISITOR_COUNTER_BASE_URL}/`;
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Failed to fetch visitor count: ${response.status}`);
  }
  const payload = (await response.json()) as VisitorCounterResponse;
  if (shouldIncrement && !alreadyCounted && typeof window !== "undefined") {
    window.sessionStorage.setItem(VISITOR_COUNTER_SESSION_KEY, "1");
  }
  return payload.count;
}
