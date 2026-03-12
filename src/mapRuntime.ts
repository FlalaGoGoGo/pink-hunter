import type { MultiPolygon as ClipMultiPolygon } from "polygon-clipping";
import type { AppRuntimeConfig } from "./runtimeConfig";
import type { MapStack } from "./types";

export type { ClipMultiPolygon };

export interface GeoJSONSource {
  setData(data: unknown): void;
  getClusterExpansionZoom?(clusterId: number): Promise<number>;
}

export interface MapLayerMouseEvent {
  point: unknown;
  lngLat: {
    lng: number;
    lat: number;
  };
  error?: unknown;
}

export interface MapEngineMap {
  on(...args: unknown[]): unknown;
  addControl(control: unknown, position?: string): void;
  addSource(id: string, source: unknown): void;
  addLayer(layer: unknown): void;
  hasImage(id: string): boolean;
  addImage(id: string, image: unknown): void;
  queryRenderedFeatures(...args: unknown[]): Array<{ properties?: Record<string, unknown>; geometry?: unknown }>;
  getSource(id: string): GeoJSONSource | undefined;
  getLayer(id: string): unknown;
  getBounds(): {
    getWest(): number;
    getSouth(): number;
    getEast(): number;
    getNorth(): number;
  };
  getCenter(): {
    lng: number;
    lat: number;
  };
  getZoom(): number;
  easeTo(options: unknown): void;
  fitBounds(bounds: unknown, options?: unknown): void;
  setFilter(layerId: string, filter: unknown): void;
  remove(): void;
  getCanvas(): HTMLCanvasElement;
  resize(): void;
}

export interface MapEnginePopup {
  setLngLat(coordinates: [number, number]): MapEnginePopup;
  setHTML(html: string): MapEnginePopup;
  addTo(map: MapEngineMap): MapEnginePopup;
  on(event: string, listener: () => void): MapEnginePopup;
  remove(): void;
}

type PolygonClippingModule = typeof import("polygon-clipping");
type RuntimeImport<T> = T & { default?: T };
type MapModule = {
  Map: new (options: unknown) => MapEngineMap;
  Popup: new (options: unknown) => MapEnginePopup;
  ScaleControl: new (options: unknown) => unknown;
  accessToken?: string;
  addProtocol?(scheme: string, loadFn: unknown): void;
};

export interface MapRuntimeDeps {
  kind: MapStack;
  map: MapModule;
  polygonClipping: PolygonClippingModule;
}

const runtimePromises = new Map<string, Promise<MapRuntimeDeps>>();

function normalizeRuntimeModule<T extends object>(module: RuntimeImport<T>): T {
  return ((module as { default?: T }).default ?? module) as T;
}

export async function loadMapRuntimeDeps(config: AppRuntimeConfig): Promise<MapRuntimeDeps> {
  const cacheKey = `${config.mapStack}:${config.treeRenderMode}`;

  if (!runtimePromises.has(cacheKey)) {
    runtimePromises.set(
      cacheKey,
      config.mapStack === "mapbox"
        ? Promise.all([import("mapbox-gl"), import("polygon-clipping")]).then(([mapbox, polygonClipping]) => {
            const normalized = normalizeRuntimeModule(mapbox as RuntimeImport<MapModule>);
            if (config.mapboxPublicToken) {
              normalized.accessToken = config.mapboxPublicToken;
            }
            return {
              kind: "mapbox",
              map: normalized,
              polygonClipping: normalizeRuntimeModule(polygonClipping)
            };
          })
        : Promise.all([
            import("maplibre-gl"),
            import("polygon-clipping"),
            config.treeRenderMode === "pmtiles" ? import("pmtiles") : Promise.resolve(null)
          ]).then(([maplibre, polygonClipping, pmtilesModule]) => {
            const normalized = normalizeRuntimeModule(maplibre as RuntimeImport<MapModule>);
            if (config.treeRenderMode === "pmtiles" && pmtilesModule) {
              const protocol = new pmtilesModule.Protocol();
              normalized.addProtocol?.("pmtiles", protocol.tile);
            }
            return {
              kind: "maplibre",
              map: normalized,
              polygonClipping: normalizeRuntimeModule(polygonClipping)
            };
          })
    );
  }

  return runtimePromises.get(cacheKey) as Promise<MapRuntimeDeps>;
}
