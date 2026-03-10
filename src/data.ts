import type {
  AreaIndex,
  CoverageCollection,
  RegionMeta,
  JumpIndex,
  SpeciesGuide,
  AppMeta,
  StaticAppData,
  TreeCollection,
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

export async function loadStaticAppData(): Promise<StaticAppData> {
  const [guide, meta, jumpIndex] = await Promise.all([
    loadJson<SpeciesGuide>("/data/species-guide.v1.json"),
    loadJson<AppMeta>("/data/meta.v2.json"),
    loadJson<JumpIndex>("/data/jump-index.v1.json")
  ]);

  const coverage =
    runtimeConfig.coverageLoadMode === "eager_all"
      ? await loadJson<CoverageCollection>("/data/coverage.v1.geojson")
      : null;

  return { coverage, guide, meta, jumpIndex };
}

export async function loadTreeCollection(path: string): Promise<TreeCollection> {
  return loadJson<TreeCollection>(path);
}

export async function loadAreaIndex(path: string): Promise<AreaIndex> {
  return loadJson<AreaIndex>(path);
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

function readBrowserHostname(): string {
  return typeof window !== "undefined" ? window.location.hostname.toLowerCase() : "";
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

async function loadCounterApiVisitorCount(): Promise<number> {
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

async function loadAwsVisitorCount(): Promise<number> {
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

export async function loadVisitorCount(): Promise<number> {
  return runtimeConfig.visitorCounterMode === "aws_api"
    ? loadAwsVisitorCount()
    : loadCounterApiVisitorCount();
}
