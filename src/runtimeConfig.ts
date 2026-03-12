import type { CoverageLoadMode, MapStack, RuntimeEnv, TreeRenderMode, VisitorCounterMode } from "./types";

const DEFAULT_COUNTER_API_BASE_URL = "https://api.counterapi.dev/v1/pink-hunter/pinkhunter-flalaz-com";
const DEFAULT_MAPBOX_STYLE_ID = "mapbox/light-v11";
const STABLE_COUNT_HOSTS = ["pinkhunter.flalaz.com"];
const AWS_COUNT_HOSTS = ["next.pinkhunter.flalaz.com", "pinkhunter.flalaz.com"];

export interface AppRuntimeConfig {
  env: RuntimeEnv;
  appBaseUrl: string;
  dataBaseUrl: string;
  mapStack: MapStack;
  coverageLoadMode: CoverageLoadMode;
  treeRenderMode: TreeRenderMode;
  visitorCounterMode: VisitorCounterMode;
  counterApiBaseUrl: string;
  visitorApiBaseUrl: string;
  visitorCountHosts: string[];
  mapboxPublicToken: string;
  mapboxStyleId: string;
}

function parseCoverageLoadMode(
  rawValue: string | undefined,
  fallback: CoverageLoadMode
): CoverageLoadMode {
  switch ((rawValue ?? "").trim().toLowerCase()) {
    case "eager_all":
      return "eager_all";
    case "lazy_by_region":
      return "lazy_by_region";
    default:
      return fallback;
  }
}

function parseTreeRenderMode(rawValue: string | undefined, fallback: TreeRenderMode): TreeRenderMode {
  switch ((rawValue ?? "").trim().toLowerCase()) {
    case "geojson":
      return "geojson";
    case "pmtiles":
      return "pmtiles";
    default:
      return fallback;
  }
}

function normalizeBaseUrl(rawValue: string | undefined): string {
  return (rawValue ?? "").trim().replace(/\/+$/, "");
}

function parseRuntimeEnv(rawValue: string | undefined): RuntimeEnv {
  switch ((rawValue ?? "").trim().toLowerCase()) {
    case "staging":
      return "staging";
    case "production":
      return "production";
    default:
      return "stable";
  }
}

function buildMapboxStyleId(rawValue: string | undefined): string {
  const value = (rawValue ?? "").trim();
  if (!value) {
    return DEFAULT_MAPBOX_STYLE_ID;
  }
  return value.startsWith("mapbox://styles/") ? value.slice("mapbox://styles/".length) : value;
}

function isAwsRuntime(env: RuntimeEnv): boolean {
  return env === "staging" || env === "production";
}

const env = parseRuntimeEnv(import.meta.env.VITE_RUNTIME_ENV);
const treeRenderMode = parseTreeRenderMode(import.meta.env.VITE_TREE_RENDER_MODE, "pmtiles");

export const runtimeConfig: AppRuntimeConfig = {
  env,
  appBaseUrl: normalizeBaseUrl(import.meta.env.VITE_APP_BASE_URL),
  dataBaseUrl: normalizeBaseUrl(import.meta.env.VITE_DATA_BASE_URL),
  mapStack: treeRenderMode === "pmtiles" ? "maplibre" : isAwsRuntime(env) ? "mapbox" : "maplibre",
  coverageLoadMode: parseCoverageLoadMode(
    import.meta.env.VITE_COVERAGE_LOAD_MODE,
    isAwsRuntime(env) ? "lazy_by_region" : "eager_all"
  ),
  treeRenderMode,
  visitorCounterMode: isAwsRuntime(env) ? "aws_api" : "counterapi",
  counterApiBaseUrl: normalizeBaseUrl(import.meta.env.VITE_COUNTER_API_BASE_URL) || DEFAULT_COUNTER_API_BASE_URL,
  visitorApiBaseUrl: normalizeBaseUrl(import.meta.env.VITE_VISITOR_API_BASE_URL),
  visitorCountHosts: isAwsRuntime(env) ? AWS_COUNT_HOSTS : STABLE_COUNT_HOSTS,
  mapboxPublicToken: (import.meta.env.VITE_MAPBOX_PUBLIC_TOKEN ?? "").trim(),
  mapboxStyleId: buildMapboxStyleId(import.meta.env.VITE_MAPBOX_STYLE_ID)
};

export function resolveAssetUrl(baseUrl: string, path: string): string {
  if (/^https?:\/\//i.test(path)) {
    return path;
  }

  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  if (!baseUrl) {
    return normalizedPath;
  }

  return `${baseUrl}${normalizedPath}`;
}

export function resolveAppUrl(path: string): string {
  return resolveAssetUrl(runtimeConfig.appBaseUrl, path);
}

export function resolveDataUrl(path: string): string {
  return resolveAssetUrl(runtimeConfig.dataBaseUrl, path);
}

export function resolveVisitorApiUrl(path: string): string {
  return resolveAssetUrl(runtimeConfig.visitorApiBaseUrl, path);
}

export function shouldCountVisitor(hostname: string): boolean {
  return runtimeConfig.visitorCountHosts.includes(hostname.toLowerCase());
}

export function buildMapboxStyleUrl(config: AppRuntimeConfig = runtimeConfig): string {
  return `mapbox://styles/${config.mapboxStyleId}`;
}

export function buildMapboxStyleProbeUrl(config: AppRuntimeConfig = runtimeConfig): string | null {
  if (!config.mapboxPublicToken) {
    return null;
  }

  return `https://api.mapbox.com/styles/v1/${config.mapboxStyleId}?access_token=${encodeURIComponent(
    config.mapboxPublicToken
  )}`;
}

export const BLANK_MAP_STYLE = {
  version: 8,
  name: "Pink Hunter Blank Fallback",
  sources: {},
  layers: [
    {
      id: "pink-hunter-background",
      type: "background",
      paint: {
        "background-color": "#fff7fa"
      }
    }
  ]
} as const;
