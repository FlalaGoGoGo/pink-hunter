import type { Language, OwnershipGroup, SpeciesGroup } from "./types";

export const DEFAULT_LANGUAGE: Language = "en-US";

const copy = {
  "zh-CN": {
    appTitle: "Pink Hunter",
    appSubtitle: "",
    locate: "定位",
    filter: "筛选",
    language: "EN",
    loading: "正在加载地图与树点数据...",
    records: "棵树",
    coveredLegend: "已覆盖区域",
    officialUnavailableLegend: "官方未公开",
    officialUnavailablePopupTitle: "已核验，暂无官方数据",
    officialUnavailablePopupBody: "该城市已完成核验，但官方目前没有公开可接入的单株树木数据。",
    officialUnavailablePopupFoot: "如果未来官方公开数据上线，这里会转为粉色覆盖区。",
    notCoveredLegend: "待覆盖区域",
    coverageEnvelopeLegend: "Coverage Envelope",
    coverageEnvelopeBanner: "Coverage Envelope 仅表示数据覆盖包络，不是法定行政边界。",
    noResultsTitle: "没有符合条件的树",
    noResultsBody: "尝试放宽筛选条件，或切换到其它城市。",
    selectedTree: "当前选中",
    guideTitle: "花树辨认指南",
    listTitle: "附近与筛选结果",
    dataUpdated: "数据更新",
    source: "来源",
    ownership: "产权",
    subtype: "细分类",
    scientific: "学名",
    common: "常用名",
    city: "城市",
    unknown: "未知",
    filtersTitle: "筛选条件",
    speciesFilter: "树种",
    cityFilter: "城市",
    zipFilter: "ZIP Code",
    ownershipFilter: "产权",
    clearFilters: "清除全部",
    showAll: "显示全部",
    clearAll: "清空全部",
    searchCityPlaceholder: "搜索城市",
    searchZipPlaceholder: "搜索 ZIP Code",
    tipsTitle: "辨认提示",
    coverageBanner: "",
    showGuide: "科普",
    showList: "筛选",
    showAbout: "关于",
    tapTreeHint: "点击地图上的树点查看详细信息。",
    coordinates: "坐标",
    zipCode: "邮编",
    fitCoverage: "全局",
    locateNearby: "定位",
    loadedCount: "已加载",
    fallbackBasemap: "当前使用备用底图。",
    collapse: "收起",
    expand: "展开"
  },
  "en-US": {
    appTitle: "Pink Hunter",
    appSubtitle: "",
    locate: "Locate",
    filter: "Filter",
    language: "中",
    loading: "Loading map and tree data...",
    records: "trees",
    coveredLegend: "Covered area",
    officialUnavailableLegend: "Official data unavailable",
    officialUnavailablePopupTitle: "Researched, no official public data",
    officialUnavailablePopupBody:
      "This city has been researched, but no official public single-tree dataset is currently available.",
    officialUnavailablePopupFoot:
      "If an official public dataset becomes available later, this area can move into covered status.",
    notCoveredLegend: "Not covered yet",
    coverageEnvelopeLegend: "Coverage Envelope",
    coverageEnvelopeBanner: "Coverage Envelope shows data coverage only, not official administrative boundaries.",
    noResultsTitle: "No trees match the filters",
    noResultsBody: "Try broader filters or switch to another city.",
    selectedTree: "Selected tree",
    guideTitle: "Flower guide",
    listTitle: "Nearby & filtered results",
    dataUpdated: "Data updated",
    source: "Source",
    ownership: "Ownership",
    subtype: "Subtype",
    scientific: "Scientific",
    common: "Common",
    city: "City",
    unknown: "Unknown",
    filtersTitle: "Filters",
    speciesFilter: "Species",
    cityFilter: "City",
    zipFilter: "ZIP Code",
    ownershipFilter: "Ownership",
    clearFilters: "Clear all",
    showAll: "Show All",
    clearAll: "Clear All",
    searchCityPlaceholder: "Search city",
    searchZipPlaceholder: "Search ZIP code",
    tipsTitle: "Tips",
    coverageBanner:
      "",
    showGuide: "Guide",
    showList: "Filters",
    showAbout: "About",
    tapTreeHint: "Tap a tree pin on the map to view details.",
    coordinates: "Coordinates",
    zipCode: "ZIP",
    fitCoverage: "Global",
    locateNearby: "Locate",
    loadedCount: "Loaded",
    fallbackBasemap: "Fallback basemap is active.",
    collapse: "Collapse",
    expand: "Expand"
  }
} as const;

const speciesLabelMap: Record<Language, Record<SpeciesGroup, string>> = {
  "zh-CN": {
    cherry: "樱花",
    plum: "李花",
    peach: "桃花",
    magnolia: "木兰",
    crabapple: "海棠"
  },
  "en-US": {
    cherry: "Cherry",
    plum: "Plum",
    peach: "Peach",
    magnolia: "Magnolia",
    crabapple: "Crabapple"
  }
};

const ownershipLabelMap: Record<Language, Record<OwnershipGroup, string>> = {
  "zh-CN": {
    public: "公共",
    private: "私有",
    unknown: "未知"
  },
  "en-US": {
    public: "Public",
    private: "Private",
    unknown: "Unknown"
  }
};

export function t(language: Language, key: keyof (typeof copy)["zh-CN"]): string {
  return copy[language][key];
}

export function speciesLabel(language: Language, species: SpeciesGroup): string {
  return speciesLabelMap[language][species];
}

export function ownershipLabel(language: Language, ownership: OwnershipGroup): string {
  return ownershipLabelMap[language][ownership];
}
