import type { Feature, FeatureCollection, Geometry, MultiPolygon, Point, Polygon } from "geojson";

export type SpeciesGroup = "cherry" | "plum" | "peach" | "magnolia" | "crabapple";

export type OwnershipGroup = "public" | "private" | "unknown";

export type Language =
  | "zh-CN"
  | "zh-TW"
  | "en-US"
  | "es-ES"
  | "ko-KR"
  | "ja-JP"
  | "fr-FR"
  | "vi-VN";
export type CoverageRegion = "wa" | "ca" | "or" | "dc" | "bc" | "va" | "md" | "nj" | "ny" | "pa" | "ma";
export type RegionWarningLevel = "none" | "warning" | "high_warning" | "hard_fail";
export type SpeciesCounts = Record<SpeciesGroup, number>;

export type LayoutMode = "mobile_sheet" | "desktop_split";
export type MapStylePreset = "positron" | "demotiles";

export interface TreeFeatureProps {
  id: string;
  species_group: SpeciesGroup;
  scientific_name: string;
  common_name: string | null;
  subtype_name: string | null;
  zip_code: string | null;
  ownership: OwnershipGroup;
  ownership_raw: string;
  city: string;
  source_dataset: string;
  source_department: string;
  source_last_edit_at: string;
}

export interface CoverageFeatureProps {
  id: string;
  status: "covered" | "official_unavailable";
  jurisdiction: string;
  note: string;
}

export interface RegionMeta {
  id: CoverageRegion;
  label: string;
  available: boolean;
  bounds: [[number, number], [number, number]];
  data_path?: string | null;
  tree_count: number;
  city_count: number;
  cities: string[];
  species_counts: SpeciesCounts;
  raw_bytes: number;
  gzip_bytes: number;
  warning_level: RegionWarningLevel;
  city_split?: {
    strategy: "city";
    index_path: string;
    file_count: number;
    ready: boolean;
  } | null;
}

export interface RegionCityDataEntry {
  city: string;
  data_path: string;
  tree_count: number;
  raw_bytes: number;
  gzip_bytes: number;
}

export interface RegionCityDataIndex {
  generated_at: string;
  region: CoverageRegion;
  strategy: "city";
  items: RegionCityDataEntry[];
}

export interface AreaSummary {
  jurisdiction: string;
  region: CoverageRegion;
  tree_count: number;
  species_counts: SpeciesCounts;
}

export interface AppMeta {
  version: string;
  generated_at: string;
  default_region: CoverageRegion;
  source_count: number;
  total_records: number;
  included_records: number;
  unknown_records: number;
  species_counts: SpeciesCounts;
  regions: RegionMeta[];
  areas: AreaSummary[];
  sources: Array<{
    name: string;
    city: string;
    endpoint: string;
    last_edit_at: string;
    records_fetched: number;
    records_included: number;
    note?: string;
  }>;
}

export interface SpeciesGuideEntry {
  id: SpeciesGroup;
  title: Record<Language, string>;
  subtitle: Record<Language, string>;
  bullets: Record<Language, string[]>;
  confusionTips: Record<Language, string[]>;
}

export interface SpeciesGuide {
  updated_at: string;
  entries: SpeciesGuideEntry[];
}

export type GeoJsonFeature<P, G extends Geometry = Geometry> = Feature<G, P>;
export type GeoJsonCollection<P, G extends Geometry = Geometry> = FeatureCollection<G, P>;

export type TreeFeature = GeoJsonFeature<TreeFeatureProps, Point>;
export type TreeCollection = GeoJsonCollection<TreeFeatureProps, Point>;
export type CoverageFeature = GeoJsonFeature<CoverageFeatureProps, Polygon | MultiPolygon>;
export type CoverageCollection = GeoJsonCollection<CoverageFeatureProps, Polygon | MultiPolygon>;

export interface StaticAppData {
  coverage: CoverageCollection;
  guide: SpeciesGuide;
  meta: AppMeta;
}
