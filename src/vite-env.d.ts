/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_RUNTIME_ENV?: string;
  readonly VITE_APP_BASE_URL?: string;
  readonly VITE_DATA_BASE_URL?: string;
  readonly VITE_TREE_RENDER_MODE?: string;
  readonly VITE_COUNTER_API_BASE_URL?: string;
  readonly VITE_VISITOR_API_BASE_URL?: string;
  readonly VITE_MAPBOX_PUBLIC_TOKEN?: string;
  readonly VITE_MAPBOX_STYLE_ID?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
