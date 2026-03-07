import type {
  GeoJSONSource,
  Map as MapLibreMap,
  MapLayerMouseEvent,
  Popup as MapLibrePopup
} from "maplibre-gl";
import type { MultiPolygon as ClipMultiPolygon } from "polygon-clipping";

export type { ClipMultiPolygon, GeoJSONSource, MapLayerMouseEvent, MapLibreMap, MapLibrePopup };

type MapLibreModule = typeof import("maplibre-gl");
type PolygonClippingModule = typeof import("polygon-clipping");
type RuntimeImport<T> = T & { default?: T };

export interface MapRuntimeDeps {
  maplibre: MapLibreModule;
  polygonClipping: PolygonClippingModule;
}

let runtimePromise: Promise<MapRuntimeDeps> | null = null;

function normalizeRuntimeModule<T>(module: RuntimeImport<T>): T {
  return module.default ?? module;
}

export async function loadMapRuntimeDeps(): Promise<MapRuntimeDeps> {
  if (!runtimePromise) {
    runtimePromise = Promise.all([import("maplibre-gl"), import("polygon-clipping")]).then(
      ([maplibre, polygonClipping]) => ({
        maplibre: normalizeRuntimeModule(maplibre),
        polygonClipping: normalizeRuntimeModule(polygonClipping)
      })
    );
  }
  return runtimePromise;
}
