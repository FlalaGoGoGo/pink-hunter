import type { Feature, FeatureCollection, Geometry, MultiPolygon, Point, Polygon } from "geojson";

export type SpeciesGroup = "cherry" | "plum" | "peach" | "magnolia" | "crabapple";

export type OwnershipGroup = "public" | "private" | "unknown";

export type Language = "zh-CN" | "en-US";

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

export interface AppMeta {
  version: string;
  generated_at: string;
  source_count: number;
  total_records: number;
  included_records: number;
  unknown_records: number;
  sources: Array<{
    name: string;
    city: string;
    endpoint: string;
    last_edit_at: string;
    records_fetched: number;
    records_included: number;
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

export interface AppData {
  trees: TreeCollection;
  coverage: CoverageCollection;
  guide: SpeciesGuide;
  meta: AppMeta;
}
