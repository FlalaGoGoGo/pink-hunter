import type { Feature, FeatureCollection, Geometry, MultiPolygon, Point, Polygon } from "geojson";

export type SpeciesGroup = "cherry" | "plum" | "peach" | "magnolia" | "crabapple";

export type OwnershipGroup = "public" | "private" | "unknown";
export type JurisdictionType = "city" | "county" | "district";

export type Language =
  | "zh-CN"
  | "zh-TW"
  | "en-US"
  | "es-ES"
  | "ko-KR"
  | "ja-JP"
  | "fr-FR"
  | "vi-VN";
export type CoverageRegion = "wa" | "ca" | "co" | "nv" | "or" | "tx" | "ut" | "dc" | "bc" | "on" | "qc" | "va" | "md" | "nj" | "ny" | "pa" | "ma";
export type RegionWarningLevel = "none" | "warning" | "high_warning" | "hard_fail";
export type RegionAggregateAdvisoryLevel = "none" | "watch" | "large" | "very_large";
export type SpeciesCounts = Record<SpeciesGroup, number>;

export type LayoutMode = "mobile_sheet" | "desktop_split";
export type MapStylePreset = "positron" | "demotiles" | "mapbox" | "blank_fallback";
export type MapStack = "maplibre" | "mapbox";
export type VisitorCounterMode = "counterapi" | "aws_api";
export type RuntimeEnv = "stable" | "staging" | "production";
export type CoverageLoadMode = "eager_all" | "lazy_by_region";

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
  coverage_path?: string | null;
  tree_count: number;
  city_count: number;
  cities: string[];
  species_counts: SpeciesCounts;
  ownership_groups?: OwnershipGroup[];
  raw_bytes: number;
  gzip_bytes: number;
  warning_level: RegionWarningLevel;
  aggregate_raw_bytes?: number;
  aggregate_gzip_bytes?: number;
  aggregate_warning_level?: RegionAggregateAdvisoryLevel;
  largest_shard_raw_bytes?: number;
  largest_shard_gzip_bytes?: number;
  largest_shard_area?: string | null;
  largest_shard_warning_level?: RegionWarningLevel;
  area_split?: {
    strategy: "area_shard";
    index_path: string;
    area_count: number;
    shard_count: number;
    ready: boolean;
  } | null;
}

export interface AreaShard {
  id: string;
  bounds: [[number, number], [number, number]];
  data_path: string;
  tree_count: number;
  raw_bytes: number;
  gzip_bytes: number;
}

export interface AreaIndexItem {
  jurisdiction: string;
  slug: string;
  display_name: string;
  jurisdiction_type: JurisdictionType;
  state_province: string;
  country: string;
  bounds: [[number, number], [number, number]];
  tree_count: number;
  zip_codes: string[];
  species_counts: SpeciesCounts;
  ownership_groups?: OwnershipGroup[];
  shards: AreaShard[];
}

export interface AreaIndex {
  generated_at: string;
  region: CoverageRegion;
  strategy: "area_shard";
  items: AreaIndexItem[];
}

export interface AreaSummary {
  jurisdiction: string;
  region: CoverageRegion;
  tree_count: number;
  species_counts: SpeciesCounts;
  jurisdiction_type?: JurisdictionType;
  state_province?: string;
}

export interface JumpCountry {
  id: "us" | "ca";
  label: string;
  emoji: string;
  bounds: [[number, number], [number, number]];
}

export interface JumpState {
  id: string;
  country_id: JumpCountry["id"];
  code: string;
  label: string;
  bounds: [[number, number], [number, number]];
  region_hint?: CoverageRegion | null;
}

export interface JumpArea {
  id: string;
  country_id: JumpCountry["id"];
  state_id: string;
  jurisdiction: string;
  display_name: string;
  area_type: JurisdictionType;
  bounds: [[number, number], [number, number]];
  region_hint?: CoverageRegion | null;
  coverage_status: "covered" | "official_unavailable" | "untracked";
}

export interface JumpIndex {
  generated_at: string;
  countries: JumpCountry[];
  states: JumpState[];
  areas: JumpArea[];
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

export interface VisitorCountHitResponse {
  count: number;
  incremented: boolean;
  updatedAt: string;
}

export interface VisitorCountReadResponse {
  count: number;
  updatedAt: string;
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
  coverage: CoverageCollection | null;
  guide: SpeciesGuide;
  meta: AppMeta;
  jumpIndex: JumpIndex;
}
