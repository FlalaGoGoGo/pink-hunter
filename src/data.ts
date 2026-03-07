import type {
  CoverageCollection,
  SpeciesGuide,
  AppMeta,
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

export async function loadRegionTrees(path: string): Promise<TreeCollection> {
  return loadJson<TreeCollection>(path);
}
