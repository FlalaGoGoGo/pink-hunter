import type {
  AppData,
  TreeCollection,
  CoverageCollection,
  SpeciesGuide,
  AppMeta
} from "./types";

async function loadJson<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function loadAppData(): Promise<AppData> {
  const [trees, coverage, guide, meta] = await Promise.all([
    loadJson<TreeCollection>("/data/trees.v1.geojson"),
    loadJson<CoverageCollection>("/data/coverage.v1.geojson"),
    loadJson<SpeciesGuide>("/data/species-guide.v1.json"),
    loadJson<AppMeta>("/data/meta.v1.json")
  ]);

  return { trees, coverage, guide, meta };
}
