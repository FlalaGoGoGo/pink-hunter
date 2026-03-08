import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
  type ReactNode
} from "react";
import { loadAreaIndex, loadStaticAppData, loadTreeCollection, loadVisitorCount } from "./data";
import {
  DEFAULT_LANGUAGE,
  LANGUAGE_OPTIONS,
  isSupportedLanguage,
  ownershipLabel,
  regionLabel,
  speciesLabel,
  t
} from "./i18n";
import {
  loadMapRuntimeDeps,
  type ClipMultiPolygon,
  type GeoJSONSource,
  type MapLayerMouseEvent,
  type MapLibreMap,
  type MapLibrePopup,
  type MapRuntimeDeps
} from "./mapRuntime";
import type {
  AreaIndex,
  AreaIndexItem,
  AreaShard,
  AppMeta,
  CoverageCollection,
  CoverageFeatureProps,
  CoverageRegion,
  JumpCountry,
  JumpState,
  JurisdictionType,
  Language,
  LayoutMode,
  MapStylePreset,
  OwnershipGroup,
  RegionMeta,
  SpeciesGroup,
  SpeciesCounts,
  StaticAppData,
  TreeCollection,
  TreeFeatureProps
} from "./types";

const SNAP_POINTS = [0.4, 0.72, 1] as const;
const SELECTED_MARKER_IMAGE_ID = "selected-bloom-marker";
const ALL_SPECIES = ["cherry", "plum", "peach", "magnolia", "crabapple"] as const;
const POINT_LAYER_IDS = [
  "tree-cherry",
  "tree-plum",
  "tree-peach",
  "tree-magnolia",
  "tree-crabapple"
] as const;
const ALL_OWNERSHIP = ["public", "private", "unknown"] as const;
const DEFAULT_CENTER: [number, number] = [-122.315, 47.55];
const DEFAULT_ZOOM = 8.45;
const POSITRON_STYLE_URL = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";
const FALLBACK_STYLE_URL = "https://demotiles.maplibre.org/style.json";
const ABOUT_SOURCES_PAGE_SIZE = 6;
const ABOUT_REGION_SUMMARY_PAGE_SIZE = 3;
const ABOUT_AREA_SUMMARY_PAGE_SIZE = 3;
const BRAND_LOGO_PATH = "/assets/brand/pink-hunter-logo.png";
const SORT_COLLATOR = new Intl.Collator("en", { sensitivity: "base" });
const EMPTY_SPECIES_COUNTS: SpeciesCounts = {
  cherry: 0,
  plum: 0,
  peach: 0,
  magnolia: 0,
  crabapple: 0
};
const POINT_COLORS: Record<SpeciesGroup, string> = {
  cherry: "#ef79ad",
  plum: "#d976b4",
  peach: "#f39a88",
  magnolia: "#b886ea",
  crabapple: "#ff6f9f"
};
const COVERAGE_COLORS = {
  coveredFill: "#f7b7cc",
  coveredLine: "#8a5567",
  unavailableFill: "#d7dbe1",
  unavailableLine: "#8f96a1"
} as const;
type BoundsTuple = [[number, number], [number, number]];

const REGION_CITY_OVERRIDES: Partial<Record<string, CoverageRegion>> = {
  Austin: "tx",
  Dallas: "tx",
  "Las Vegas": "nv",
  Arlington: "va",
  Alexandria: "va",
  "Montgomery County": "md",
  Baltimore: "md",
  "Jersey City": "nj",
  Boston: "ma",
  "New York City": "ny",
  Pittsburgh: "pa",
  Philadelphia: "pa",
  Cambridge: "ma",
  Ottawa: "on",
  Toronto: "on",
  Montreal: "qc",
  "Washington DC": "dc",
  "Salt Lake City": "ut",
  Burnaby: "bc",
  Coquitlam: "bc",
  Delta: "bc",
  "Langley City": "bc",
  "New Westminster": "bc",
  "North Vancouver City": "bc",
  "North Vancouver District": "bc",
  "Richmond BC": "bc",
  Saanich: "bc",
  Surrey: "bc",
  "Vancouver BC": "bc",
  "Victoria BC": "bc",
  "West Vancouver": "bc",
  "White Rock": "bc",
  Portland: "or",
  Beaverton: "or",
  Gresham: "or",
  Hillsboro: "or",
  Salem: "or",
  Tigard: "or",
  Monterey: "ca",
  "Mountain View": "ca",
  Napa: "ca",
  Irvine: "ca",
  "Long Beach": "ca",
  "Los Angeles": "ca",
  Ontario: "ca",
  Richmond: "ca",
  Sacramento: "ca",
  Salinas: "ca",
  "San Mateo": "ca",
  "San Rafael": "ca",
  "Santa Clara": "ca",
  "Santa Ana": "ca",
  "Santa Cruz": "ca",
  "Santa Rosa": "ca",
  Stockton: "ca",
  Sunnyvale: "ca",
  Burlingame: "ca",
  Concord: "ca",
  Fremont: "ca",
  Milpitas: "ca",
  Newark: "nj",
  "Palo Alto": "ca",
  Berkeley: "ca",
  Cupertino: "ca",
  Oakland: "ca",
  "San Diego": "ca",
  "South San Francisco": "ca",
  "San Francisco": "ca",
  "San Jose": "ca"
};

const JURISDICTION_OVERRIDES: Partial<Record<string, { displayName: string; type: JurisdictionType }>> = {
  Arlington: {
    displayName: "Arlington County",
    type: "county"
  },
  "Montgomery County": {
    displayName: "Montgomery County",
    type: "county"
  },
  "Richmond BC": {
    displayName: "Richmond",
    type: "city"
  },
  "Vancouver WA": {
    displayName: "Vancouver",
    type: "city"
  }
};

const GUIDE_FLOWER_ART: Record<SpeciesGroup, string> = {
  cherry: "/assets/guide/species/cherry-blossom.png",
  plum: "/assets/guide/species/plum-blossom.png",
  peach: "/assets/guide/species/peach-blossom.png",
  magnolia: "/assets/guide/species/magnolia-blossom.png",
  crabapple: "/assets/guide/species/crabapple-blossom.png"
};
const SPECIES_ICON_ART: Record<SpeciesGroup, string> = {
  cherry: "/assets/guide/species-icons/cherry-icon.png",
  plum: "/assets/guide/species-icons/plum-icon.png",
  peach: "/assets/guide/species-icons/peach-icon.png",
  magnolia: "/assets/guide/species-icons/magnolia-icon.png",
  crabapple: "/assets/guide/species-icons/crabapple-icon.png"
};

const GUIDE_COMPARISON_ART = [
  {
    id: "petals",
    image: "/assets/guide/comparisons/petal-comparison.png",
    title: {
      "en-US": "Petal Shape",
      "zh-CN": "花瓣形态",
      "zh-TW": "花瓣形態",
      "es-ES": "Forma de los pétalos",
      "ko-KR": "꽃잎 모양",
      "ja-JP": "花びらの形",
      "fr-FR": "Forme des pétales",
      "vi-VN": "Hình dáng cánh hoa"
    },
    body: {
      "en-US":
        "Left to right: Cherry, Plum, Peach, Magnolia, Crabapple. Cherry petals often show a notch, plum petals look rounder, peach petals run longer, magnolia blooms are much larger, and crabapple flowers feel tighter and denser.",
      "zh-CN":
        "从左到右：樱花、李花、桃花、木兰、海棠。樱花花瓣常有缺口，李花更圆，桃花更狭长，木兰花朵明显更大，海棠通常更紧凑。",
      "zh-TW":
        "從左到右：櫻花、李花、桃花、木蘭、海棠。櫻花花瓣常有缺口，李花更圓，桃花更狹長，木蘭花朵明顯更大，海棠通常更緊湊。",
      "es-ES":
        "De izquierda a derecha: cerezo, ciruelo, melocotonero, magnolia y manzano ornamental. El cerezo suele mostrar una pequeña hendidura, el ciruelo se ve más redondo, el melocotonero tiene pétalos más largos, la magnolia es mucho más grande y el manzano ornamental se ve más compacto.",
      "ko-KR":
        "왼쪽부터 벚꽃, 자두꽃, 복숭아꽃, 목련, 꽃사과입니다. 벚꽃은 꽃잎 끝이 살짝 갈라지는 경우가 많고, 자두꽃은 더 둥글며, 복숭아꽃은 길쭉하고, 목련은 꽃 자체가 훨씬 크고, 꽃사과는 더 조밀하게 보입니다.",
      "ja-JP":
        "左から順に、桜、李、桃、木蓮、海棠です。桜は花びらの先に切れ込みが出やすく、李はより丸く、桃は細長く、木蓮は花そのものが大きく、海棠は全体に詰まって見えます。",
      "fr-FR":
        "De gauche à droite : cerisier, prunier, pêcher, magnolia, pommier d'ornement. Le cerisier montre souvent une encoche, le prunier paraît plus rond, le pêcher est plus allongé, le magnolia est bien plus grand et le pommier d'ornement paraît plus serré.",
      "vi-VN":
        "Từ trái sang phải: anh đào, mận, đào, mộc lan, hải đường. Hoa anh đào thường có khe nhỏ ở đầu cánh, hoa mận tròn hơn, hoa đào dài hơn, hoa mộc lan lớn hơn hẳn và hoa hải đường trông dày, gọn hơn."
    }
  },
  {
    id: "clusters",
    image: "/assets/guide/comparisons/cluster-stem-comparison.png",
    title: {
      "en-US": "Cluster & Stem Pattern",
      "zh-CN": "成串方式与花梗",
      "zh-TW": "成串方式與花梗",
      "es-ES": "Racimos y tallos florales",
      "ko-KR": "송이 형태와 꽃자루",
      "ja-JP": "房のつき方と花柄",
      "fr-FR": "Port en grappe et pédicelles",
      "vi-VN": "Kiểu mọc thành chùm và cuống hoa"
    },
    body: {
      "en-US":
        "Left to right: Cherry, Plum, Peach, Magnolia, Crabapple. Cherry and crabapple often flower in clusters, plum and peach often sit closer to the twig in smaller groups, and magnolia usually carries one large bloom per bud.",
      "zh-CN":
        "从左到右：樱花、李花、桃花、木兰、海棠。樱花和海棠更常成串开放，李花和桃花更常贴着枝条、数量更少，木兰通常是一颗芽开出一朵大花。",
      "zh-TW":
        "從左到右：櫻花、李花、桃花、木蘭、海棠。櫻花和海棠更常成串開放，李花和桃花更常貼著枝條、數量更少，木蘭通常是一顆芽開出一朵大花。",
      "es-ES":
        "De izquierda a derecha: cerezo, ciruelo, melocotonero, magnolia y manzano ornamental. El cerezo y el manzano ornamental suelen florecer en racimos, el ciruelo y el melocotonero suelen quedar más pegados a la rama en grupos pequeños, y la magnolia normalmente muestra una flor grande por yema.",
      "ko-KR":
        "왼쪽부터 벚꽃, 자두꽃, 복숭아꽃, 목련, 꽃사과입니다. 벚꽃과 꽃사과는 송이로 피는 경우가 많고, 자두꽃과 복숭아꽃은 가지 가까이에 적은 수로 붙으며, 목련은 보통 한 개의 큰 꽃이 한 눈에서 나옵니다.",
      "ja-JP":
        "左から順に、桜、李、桃、木蓮、海棠です。桜と海棠は房状になりやすく、李と桃は枝に近い小さなまとまりで咲くことが多く、木蓮は一つの芽から大きな花が一輪出ることが一般的です。",
      "fr-FR":
        "De gauche à droite : cerisier, prunier, pêcher, magnolia, pommier d'ornement. Le cerisier et le pommier d'ornement fleurissent souvent en grappes, le prunier et le pêcher restent plus près du rameau en petits groupes, et le magnolia porte en général une grande fleur par bourgeon.",
      "vi-VN":
        "Từ trái sang phải: anh đào, mận, đào, mộc lan, hải đường. Anh đào và hải đường thường nở thành chùm, mận và đào thường bám sát cành với số lượng ít hơn, còn mộc lan thường có một bông lớn từ mỗi nụ."
    }
  },
  {
    id: "bark",
    image: "/assets/guide/comparisons/bark-trunk-comparison.png",
    title: {
      "en-US": "Bark & Trunk",
      "zh-CN": "树皮与树干",
      "zh-TW": "樹皮與樹幹",
      "es-ES": "Corteza y tronco",
      "ko-KR": "수피와 줄기",
      "ja-JP": "樹皮と幹",
      "fr-FR": "Écorce et tronc",
      "vi-VN": "Vỏ cây và thân cây"
    },
    body: {
      "en-US":
        "Left to right: Cherry, Plum, Peach, Magnolia, Crabapple. Cherry and plum often show horizontal lenticels, peach bark tends to look darker and rougher, magnolia bark is smoother and grayer, and crabapple bark usually looks finer and tighter.",
      "zh-CN":
        "从左到右：樱花、李花、桃花、木兰、海棠。樱花和李花常见横向皮孔，桃树树皮往往更深更粗，木兰更平滑偏灰，海棠的纹理通常更细密。",
      "zh-TW":
        "從左到右：櫻花、李花、桃花、木蘭、海棠。櫻花和李花常見橫向皮孔，桃樹樹皮往往更深更粗，木蘭更平滑偏灰，海棠的紋理通常更細密。",
      "es-ES":
        "De izquierda a derecha: cerezo, ciruelo, melocotonero, magnolia y manzano ornamental. El cerezo y el ciruelo suelen mostrar lenticelas horizontales, el melocotonero tiende a verse más oscuro y áspero, la magnolia es más lisa y gris, y el manzano ornamental suele tener una textura más fina.",
      "ko-KR":
        "왼쪽부터 벚꽃, 자두꽃, 복숭아꽃, 목련, 꽃사과입니다. 벚꽃과 자두는 가로 피목이 잘 보이고, 복숭아는 더 어둡고 거칠어 보이며, 목련은 더 매끈하고 회색빛이 돌고, 꽃사과는 질감이 더 촘촘하게 보입니다.",
      "ja-JP":
        "左から順に、桜、李、桃、木蓮、海棠です。桜と李には横向きの皮目が出やすく、桃はより濃く粗く見え、木蓮はなめらかで灰色寄り、海棠はより細かい質感に見えることが多いです。",
      "fr-FR":
        "De gauche à droite : cerisier, prunier, pêcher, magnolia, pommier d'ornement. Le cerisier et le prunier montrent souvent des lenticelles horizontales, le pêcher paraît plus sombre et plus rugueux, le magnolia plus lisse et plus gris, et le pommier d'ornement présente en général une texture plus fine.",
      "vi-VN":
        "Từ trái sang phải: anh đào, mận, đào, mộc lan, hải đường. Anh đào và mận thường có lỗ bì ngang rõ, đào có vỏ sẫm và thô hơn, mộc lan mịn và xám hơn, còn hải đường thường có bề mặt mảnh và chặt hơn."
    }
  },
  {
    id: "buds",
    image: "/assets/guide/comparisons/bud-leaf-comparison.png",
    title: {
      "en-US": "Bud & Leaf Emergence",
      "zh-CN": "花芽与叶片时机",
      "zh-TW": "花芽與葉片時機",
      "es-ES": "Brotes y momento de las hojas",
      "ko-KR": "눈과 잎의 시기",
      "ja-JP": "芽と葉のタイミング",
      "fr-FR": "Bourgeons et moment des feuilles",
      "vi-VN": "Chồi và thời điểm ra lá"
    },
    body: {
      "en-US":
        "Left to right: Cherry, Plum, Peach, Magnolia, Crabapple. Cherry often blooms before full leaf-out, plum may flower on bare wood, peach sends out long narrow leaves, magnolia buds are large and fuzzy, and crabapple often shows leaves and flowers together.",
      "zh-CN":
        "从左到右：樱花、李花、桃花、木兰、海棠。樱花常在叶片大量长出前开花，李花常直接在光枝上开，桃花会带出细长新叶，木兰花芽通常又大又有绒毛，海棠则更常出现叶花同出的情况。",
      "zh-TW":
        "從左到右：櫻花、李花、桃花、木蘭、海棠。櫻花常在葉片大量長出前開花，李花常直接在光枝上開，桃花會帶出細長新葉，木蘭花芽通常又大又有絨毛，海棠則更常出現葉花同出的情況。",
      "es-ES":
        "De izquierda a derecha: cerezo, ciruelo, melocotonero, magnolia y manzano ornamental. El cerezo suele florecer antes de llenarse de hojas, el ciruelo puede florecer sobre ramas desnudas, el melocotonero saca hojas largas y estrechas, la magnolia tiene yemas grandes y vellosas, y el manzano ornamental a menudo muestra hojas y flores a la vez.",
      "ko-KR":
        "왼쪽부터 벚꽃, 자두꽃, 복숭아꽃, 목련, 꽃사과입니다. 벚꽃은 잎이 본격적으로 나오기 전에 피는 경우가 많고, 자두꽃은 맨가지에서 피기도 하며, 복숭아는 길고 좁은 잎이 함께 나오고, 목련은 크고 보송한 꽃눈이 특징이고, 꽃사과는 꽃과 잎이 함께 보이는 경우가 많습니다.",
      "ja-JP":
        "左から順に、桜、李、桃、木蓮、海棠です。桜は葉が十分に出る前に咲くことが多く、李は裸枝で咲くことがあり、桃は細長い新葉が出やすく、木蓮は大きく毛のある芽が目立ち、海棠は葉と花が同時に見えることがよくあります。",
      "fr-FR":
        "De gauche à droite : cerisier, prunier, pêcher, magnolia, pommier d'ornement. Le cerisier fleurit souvent avant le plein déploiement des feuilles, le prunier peut fleurir sur le bois nu, le pêcher sort de longues feuilles étroites, le magnolia a de gros bourgeons duveteux, et le pommier d'ornement montre souvent feuilles et fleurs en même temps.",
      "vi-VN":
        "Từ trái sang phải: anh đào, mận, đào, mộc lan, hải đường. Anh đào thường nở trước khi lá ra nhiều, mận có thể nở trên cành trụi lá, đào cho lá mới dài và hẹp, mộc lan có nụ to có lông mịn, còn hải đường thường ra lá và hoa cùng lúc."
    }
  }
] as const;

const GUIDE_COMPARE_COPY: Record<Language, { title: string; intro: string }> = {
  "en-US": {
    title: "Compare the details",
    intro:
      "Every panel keeps the same left-to-right order: Cherry, Plum, Peach, Magnolia, Crabapple. Color alone is weak; petal shape, cluster pattern, bark, and bud timing are more reliable."
  },
  "zh-CN": {
    title: "细节对比图",
    intro: "每张图都按从左到右一致排列：樱花、李花、桃花、木兰、海棠。除了颜色，真正稳定的区分线索通常来自花瓣、花梗、树皮和芽叶时机。"
  },
  "zh-TW": {
    title: "細節對比圖",
    intro: "每張圖都按從左到右一致排列：櫻花、李花、桃花、木蘭、海棠。除了顏色，真正穩定的區分線索通常來自花瓣、花梗、樹皮和芽葉時機。"
  },
  "es-ES": {
    title: "Compara los detalles",
    intro:
      "En cada panel el orden de izquierda a derecha es el mismo: cerezo, ciruelo, melocotonero, magnolia y manzano ornamental. El color por sí solo no basta; la forma de los pétalos, el patrón de racimos, la corteza y el momento de las yemas son más fiables."
  },
  "ko-KR": {
    title: "세부 비교",
    intro:
      "모든 패널은 왼쪽부터 같은 순서입니다: 벚꽃, 자두꽃, 복숭아꽃, 목련, 꽃사과. 색만으로는 부족하고, 꽃잎 모양, 송이 형태, 수피, 눈과 잎의 시기가 더 믿을 만한 단서입니다."
  },
  "ja-JP": {
    title: "細部を比べる",
    intro:
      "どの図も左から順に、桜、李、桃、木蓮、海棠で並んでいます。色だけでは判断しにくく、花びらの形、房のつき方、樹皮、芽と葉のタイミングのほうが確実です。"
  },
  "fr-FR": {
    title: "Comparer les détails",
    intro:
      "Dans chaque panneau, l'ordre de gauche à droite reste le même : cerisier, prunier, pêcher, magnolia, pommier d'ornement. La couleur seule ne suffit pas ; la forme des pétales, le port en grappe, l'écorce et le rythme des bourgeons sont plus fiables."
  },
  "vi-VN": {
    title: "So sánh chi tiết",
    intro:
      "Trong mọi khung, thứ tự từ trái sang phải luôn giống nhau: anh đào, mận, đào, mộc lan, hải đường. Chỉ nhìn màu là chưa đủ; hình dáng cánh hoa, kiểu mọc thành chùm, vỏ cây và thời điểm ra chồi đáng tin hơn."
  }
};

const ABOUT_COPY: Record<
  Language,
  {
    title: string;
    intro: string[];
    summaryTitle: string;
    summaryNote: string;
    summaryCoverageLead: string;
    summaryAllTitle: string;
    summaryByRegionTitle: string;
    summaryByAreaTitle: string;
    summaryTotalLabel: string;
    summarySearchPlaceholder: string;
    summaryEmpty: string;
    summaryAreaSearchPlaceholder: string;
    summaryAreaEmpty: string;
    sourcesTitle: string;
    sourcesSearchPlaceholder: string;
    sourcesEmpty: string;
    disclaimerTitle: string;
    contactTitle: string;
    contactLead: string;
    disclaimer: string[];
    officialBadge: string;
    supplementalBadge: string;
    openLink: string;
    previousPage: string;
    nextPage: string;
    pageLabel: string;
  }
> = {
  "en-US": {
    title: "About Pink Hunter",
    intro: [
      "Pink Hunter is a spring map for finding pink-blossoming cherry, plum, peach, magnolia, and crabapple trees. The project is meant to help people learn the differences between these lookalike blooms instead of calling every pink tree a cherry by default."
    ],
    summaryTitle: "Data Summary",
    summaryNote: "The counts below summarize the trees currently included on the site, first by species, then by region and area.",
    summaryCoverageLead: "Currently covering",
    summaryAllTitle: "All Covered Trees",
    summaryByRegionTitle: "By State / Province",
    summaryByAreaTitle: "By City / County",
    summaryTotalLabel: "Total trees",
    summarySearchPlaceholder: "Search states or provinces",
    summaryEmpty: "No state or province matched this search.",
    summaryAreaSearchPlaceholder: "Search cities or counties",
    summaryAreaEmpty: "No city or county matched this search.",
    sourcesTitle: "Data Sources",
    sourcesSearchPlaceholder: "Search data sources",
    sourcesEmpty: "No data sources matched this search.",
    disclaimerTitle: "Data Notes",
    contactTitle: "Contact",
    contactLead:
      "If you notice any issue on this site, or know of a public dataset this map has not covered yet, you are warmly welcome to contact Flala Zhang.",
    disclaimer: [
      "Jurisdiction-level coverage is built from official public single-tree datasets whenever those datasets are available; that is a hard rule for adding a covered area. What you see on the map can still differ from reality because of source refresh lag, pruning or removals, naming inconsistencies, or point-location error."
    ],
    officialBadge: "Official public source",
    supplementalBadge: "Supplemental source",
    openLink: "Open source link",
    previousPage: "Previous",
    nextPage: "Next",
    pageLabel: "Page"
  },
  "zh-CN": {
    title: "关于 Pink Hunter",
    intro: [
      "Pink Hunter 是一个春季粉色花树地图项目，帮助大家在花季里更快找到樱花、李花、桃花、木兰和海棠。这个项目不只是找花，也希望教大家分辨这些常被误认的花树，让“粉色花都叫樱花”这件事少一点。"
    ],
    summaryTitle: "数据总结",
    summaryNote: "下面的统计展示了当前网站已收录的树木数量，先按花种汇总，再按州/省和地区汇总。",
    summaryCoverageLead: "目前覆盖",
    summaryAllTitle: "全站收录",
    summaryByRegionTitle: "按州/省统计",
    summaryByAreaTitle: "按城市 / 县统计",
    summaryTotalLabel: "总树数",
    summarySearchPlaceholder: "搜索州或省",
    summaryEmpty: "没有匹配的州或省。",
    summaryAreaSearchPlaceholder: "搜索城市或县",
    summaryAreaEmpty: "没有匹配的城市或县。",
    sourcesTitle: "数据源",
    sourcesSearchPlaceholder: "搜索数据源",
    sourcesEmpty: "没有匹配的数据源。",
    disclaimerTitle: "数据说明",
    contactTitle: "联系方式",
    contactLead:
      "如果你发现网站有任何问题，或者知道这个网站还没有覆盖到的公开数据集，真诚欢迎你联系 Flala Zhang。",
    disclaimer: [
      "地区级覆盖优先采用官方公开的单株树木数据集；这是产品纳入覆盖地区的硬标准。但数据更新频率、树木修剪/移除、物种录入习惯、坐标偏差等问题，都会让网页显示与现实情况存在差异。"
    ],
    officialBadge: "官方公开源",
    supplementalBadge: "补充源",
    openLink: "打开源链接",
    previousPage: "上一页",
    nextPage: "下一页",
    pageLabel: "页"
  },
  "zh-TW": {
    title: "關於 Pink Hunter",
    intro: [
      "Pink Hunter 是一個春季粉色花樹地圖專案，幫助大家在花季裡更快找到櫻花、李花、桃花、木蘭和海棠。這個專案不只是找花，也希望教大家分辨這些常被誤認的花樹，讓「粉色花都叫櫻花」這件事少一點。"
    ],
    summaryTitle: "資料總結",
    summaryNote: "以下統計展示目前網站已收錄的樹木數量，先按花種彙總，再按州／省和地區彙總。",
    summaryCoverageLead: "目前覆蓋",
    summaryAllTitle: "全站收錄",
    summaryByRegionTitle: "按州／省統計",
    summaryByAreaTitle: "按城市／縣統計",
    summaryTotalLabel: "總樹數",
    summarySearchPlaceholder: "搜尋州或省",
    summaryEmpty: "沒有符合的州或省。",
    summaryAreaSearchPlaceholder: "搜尋城市或縣",
    summaryAreaEmpty: "沒有符合的城市或縣。",
    sourcesTitle: "資料來源",
    sourcesSearchPlaceholder: "搜尋資料來源",
    sourcesEmpty: "沒有符合的資料來源。",
    disclaimerTitle: "資料說明",
    contactTitle: "聯絡方式",
    contactLead:
      "如果你發現網站有任何問題，或知道這個網站還沒有覆蓋到的公開資料集，誠摯歡迎你聯絡 Flala Zhang。",
    disclaimer: [
      "地區級覆蓋優先採用官方公開的單株樹木資料集；這是產品納入覆蓋地區的硬標準。但資料更新頻率、樹木修剪或移除、物種登錄習慣、座標偏差等問題，都會讓網頁顯示與現實情況存在差異。"
    ],
    officialBadge: "官方公開源",
    supplementalBadge: "補充源",
    openLink: "打開來源連結",
    previousPage: "上一頁",
    nextPage: "下一頁",
    pageLabel: "頁"
  },
  "es-ES": {
    title: "Acerca de Pink Hunter",
    intro: [
      "Pink Hunter es un mapa de primavera para encontrar cerezos, ciruelos, melocotoneros, magnolias y manzanos ornamentales con floración rosa. El proyecto también busca enseñar a distinguir estas flores parecidas, en lugar de llamar cerezo a cualquier árbol rosado."
    ],
    summaryTitle: "Resumen de datos",
    summaryNote:
      "Los conteos siguientes resumen los árboles que el sitio incluye actualmente, primero por especie y luego por estado, provincia y área.",
    summaryCoverageLead: "Cobertura actual",
    summaryAllTitle: "Todos los árboles cubiertos",
    summaryByRegionTitle: "Por estado / provincia",
    summaryByAreaTitle: "Por ciudad / condado",
    summaryTotalLabel: "Total de árboles",
    summarySearchPlaceholder: "Buscar estado o provincia",
    summaryEmpty: "Ningún estado o provincia coincide con esta búsqueda.",
    summaryAreaSearchPlaceholder: "Buscar ciudades o condados",
    summaryAreaEmpty: "Ninguna ciudad o condado coincide con esta búsqueda.",
    sourcesTitle: "Fuentes de datos",
    sourcesSearchPlaceholder: "Buscar fuentes de datos",
    sourcesEmpty: "No se encontró ninguna fuente de datos.",
    disclaimerTitle: "Notas sobre los datos",
    contactTitle: "Contacto",
    contactLead:
      "Si encuentras algún problema en el sitio o conoces algún conjunto de datos público que aún no esté cubierto, te invitamos cordialmente a contactar a Flala Zhang.",
    disclaimer: [
      "La cobertura por jurisdicción se construye a partir de conjuntos públicos oficiales árbol por árbol siempre que estén disponibles; esa es una regla estricta para añadir un área cubierta. Lo que ves en el mapa puede diferir de la realidad por retrasos de actualización, podas o retiros, diferencias de nomenclatura o errores de ubicación."
    ],
    officialBadge: "Fuente pública oficial",
    supplementalBadge: "Fuente complementaria",
    openLink: "Abrir enlace",
    previousPage: "Anterior",
    nextPage: "Siguiente",
    pageLabel: "Página"
  },
  "ko-KR": {
    title: "Pink Hunter 소개",
    intro: [
      "Pink Hunter는 벚꽃, 자두꽃, 복숭아꽃, 목련, 꽃사과처럼 분홍빛으로 피는 나무를 찾기 위한 봄 지도입니다. 모든 분홍 꽃나무를 벚꽃이라고 부르지 않고, 서로 어떻게 다른지 배울 수 있게 돕는 것도 이 프로젝트의 목표입니다."
    ],
    summaryTitle: "데이터 요약",
    summaryNote: "아래 수치는 현재 사이트에 포함된 나무를 먼저 종별로, 그다음 주/주(省)와 지역별로 요약한 것입니다.",
    summaryCoverageLead: "현재 범위",
    summaryAllTitle: "전체 수록 현황",
    summaryByRegionTitle: "주 / 주(省)별 통계",
    summaryByAreaTitle: "시 / 카운티별 통계",
    summaryTotalLabel: "총 나무 수",
    summarySearchPlaceholder: "주 또는 주(省) 검색",
    summaryEmpty: "검색과 일치하는 주 또는 주(省)가 없습니다.",
    summaryAreaSearchPlaceholder: "시 또는 카운티 검색",
    summaryAreaEmpty: "검색과 일치하는 시 또는 카운티가 없습니다.",
    sourcesTitle: "데이터 출처",
    sourcesSearchPlaceholder: "데이터 출처 검색",
    sourcesEmpty: "검색 결과와 일치하는 데이터 출처가 없습니다.",
    disclaimerTitle: "데이터 안내",
    contactTitle: "연락처",
    contactLead:
      "이 사이트에서 문제를 발견했거나 아직 포함되지 않은 공개 데이터셋을 알고 있다면, Flala Zhang에게 알려 주시면 감사하겠습니다.",
    disclaimer: [
      "행정 구역 단위 커버리지는 가능한 경우 공식 공개 단일 수목 데이터셋을 기준으로 구축합니다. 이것은 커버된 지역을 추가할 때의 하드 룰입니다. 지도에 보이는 내용은 데이터 갱신 지연, 가지치기나 제거, 명칭 차이, 좌표 오차 때문에 실제와 다를 수 있습니다."
    ],
    officialBadge: "공식 공개 출처",
    supplementalBadge: "보완 출처",
    openLink: "원본 링크 열기",
    previousPage: "이전",
    nextPage: "다음",
    pageLabel: "페이지"
  },
  "ja-JP": {
    title: "Pink Hunter について",
    intro: [
      "Pink Hunter は、桜、李、桃、木蓮、海棠など、春にピンク色で咲く花木を見つけるための地図です。似た花木の違いを学び、ピンクの木を何でも桜と呼んでしまう状況を少し減らすことも、このプロジェクトの目的です。"
    ],
    summaryTitle: "データ概要",
    summaryNote: "以下の数は、現在このサイトに収録されている樹木を、まず花種別に、その次に州・省と地区別にまとめたものです。",
    summaryCoverageLead: "現在の対象範囲",
    summaryAllTitle: "全体集計",
    summaryByRegionTitle: "州・省ごとの集計",
    summaryByAreaTitle: "市・郡ごとの集計",
    summaryTotalLabel: "総本数",
    summarySearchPlaceholder: "州・省を検索",
    summaryEmpty: "一致する州・省はありません。",
    summaryAreaSearchPlaceholder: "市または郡を検索",
    summaryAreaEmpty: "一致する市または郡はありません。",
    sourcesTitle: "データソース",
    sourcesSearchPlaceholder: "データソースを検索",
    sourcesEmpty: "検索に一致するデータソースはありません。",
    disclaimerTitle: "データについて",
    contactTitle: "連絡先",
    contactLead:
      "このサイトの不具合を見つけた場合や、まだ掲載されていない公開データセットをご存じの場合は、ぜひ Flala Zhang までご連絡ください。",
    disclaimer: [
      "行政区画ごとのカバレッジは、利用可能な場合は公式に公開された単木データセットを優先して構築しています。これはカバー対象エリアを追加する際のハードルールです。更新遅延、剪定や撤去、名称のゆれ、座標誤差などにより、地図表示が実際の状況と異なることがあります。"
    ],
    officialBadge: "公式公開ソース",
    supplementalBadge: "補完ソース",
    openLink: "元リンクを開く",
    previousPage: "前へ",
    nextPage: "次へ",
    pageLabel: "ページ"
  },
  "fr-FR": {
    title: "À propos de Pink Hunter",
    intro: [
      "Pink Hunter est une carte de printemps pour trouver des cerisiers, pruniers, pêchers, magnolias et pommiers d'ornement à floraison rose. Le projet sert aussi à apprendre à distinguer ces floraisons ressemblantes au lieu d'appeler cerisier tout arbre rose."
    ],
    summaryTitle: "Résumé des données",
    summaryNote:
      "Les chiffres ci-dessous résument les arbres actuellement inclus sur le site, d'abord par espèce, puis par État, province et zone.",
    summaryCoverageLead: "Couverture actuelle",
    summaryAllTitle: "Tous les arbres couverts",
    summaryByRegionTitle: "Par État / province",
    summaryByAreaTitle: "Par ville / comté",
    summaryTotalLabel: "Total d'arbres",
    summarySearchPlaceholder: "Rechercher un État ou une province",
    summaryEmpty: "Aucun État ou province ne correspond à cette recherche.",
    summaryAreaSearchPlaceholder: "Rechercher une ville ou un comté",
    summaryAreaEmpty: "Aucune ville ou aucun comté ne correspond à cette recherche.",
    sourcesTitle: "Sources de données",
    sourcesSearchPlaceholder: "Rechercher une source",
    sourcesEmpty: "Aucune source de données ne correspond à cette recherche.",
    disclaimerTitle: "Notes sur les données",
    contactTitle: "Contact",
    contactLead:
      "Si vous repérez un problème sur ce site ou connaissez un jeu de données public encore absent, vous êtes chaleureusement invité à contacter Flala Zhang.",
    disclaimer: [
      "La couverture par juridiction repose, lorsque c'est possible, sur des jeux de données publics officiels arbre par arbre ; c'est une règle stricte pour ajouter une zone couverte. Ce que vous voyez sur la carte peut différer de la réalité à cause du retard de mise à jour, de la taille ou du retrait d'arbres, d'incohérences de nommage ou d'erreurs de géolocalisation."
    ],
    officialBadge: "Source publique officielle",
    supplementalBadge: "Source complémentaire",
    openLink: "Ouvrir le lien",
    previousPage: "Précédent",
    nextPage: "Suivant",
    pageLabel: "Page"
  },
  "vi-VN": {
    title: "Về Pink Hunter",
    intro: [
      "Pink Hunter là bản đồ mùa xuân để tìm các cây nở hoa màu hồng như anh đào, mận, đào, mộc lan và hải đường. Dự án cũng nhằm giúp mọi người phân biệt những loài hoa dễ bị nhầm lẫn này thay vì mặc định gọi mọi cây hoa hồng là anh đào."
    ],
    summaryTitle: "Tóm tắt dữ liệu",
    summaryNote:
      "Các số liệu dưới đây tóm tắt số cây hiện đã được đưa vào trang web, trước theo loài hoa, sau theo bang, tỉnh bang và khu vực.",
    summaryCoverageLead: "Hiện đang bao phủ",
    summaryAllTitle: "Toàn bộ cây đã phủ",
    summaryByRegionTitle: "Theo bang / tỉnh bang",
    summaryByAreaTitle: "Theo thành phố / quận hạt",
    summaryTotalLabel: "Tổng số cây",
    summarySearchPlaceholder: "Tìm bang hoặc tỉnh bang",
    summaryEmpty: "Không có bang hoặc tỉnh bang nào khớp.",
    summaryAreaSearchPlaceholder: "Tìm thành phố hoặc quận hạt",
    summaryAreaEmpty: "Không có thành phố hoặc quận hạt nào khớp.",
    sourcesTitle: "Nguồn dữ liệu",
    sourcesSearchPlaceholder: "Tìm nguồn dữ liệu",
    sourcesEmpty: "Không có nguồn dữ liệu nào khớp với tìm kiếm này.",
    disclaimerTitle: "Lưu ý dữ liệu",
    contactTitle: "Liên hệ",
    contactLead:
      "Nếu bạn phát hiện bất kỳ vấn đề nào trên trang web hoặc biết một bộ dữ liệu công khai mà bản đồ này chưa bao phủ, rất mong bạn liên hệ với Flala Zhang.",
    disclaimer: [
      "Phạm vi theo từng đơn vị hành chính được xây dựng từ các bộ dữ liệu công khai chính thức cho từng cây khi những bộ dữ liệu đó tồn tại; đây là quy tắc cứng để thêm một khu vực được phủ. Những gì bạn thấy trên bản đồ vẫn có thể khác thực tế do độ trễ cập nhật, việc cắt tỉa hoặc loại bỏ cây, cách ghi tên khác nhau hoặc sai số tọa độ."
    ],
    officialBadge: "Nguồn công khai chính thức",
    supplementalBadge: "Nguồn bổ sung",
    openLink: "Mở liên kết nguồn",
    previousPage: "Trang trước",
    nextPage: "Trang sau",
    pageLabel: "Trang"
  }
};

const FIND_PANEL_COPY: Record<
  Language,
  {
    showTitle: string;
    showBody: string;
    showButton: string;
    jumpTitle: string;
    jumpBody: string;
    jumpCountry: string;
    jumpState: string;
    jumpProvince: string;
    jumpAnyState: string;
    jumpAnyProvince: string;
    jumpButton: string;
    searchState: string;
    searchProvince: string;
    filtersTitle: string;
    jumpUntrackedTitle: string;
    jumpUntrackedBody: string;
  }
> = {
  "en-US": {
    showTitle: "Show Trees",
    showBody:
      "Reload all covered tree data for the current visible map area. If the map does not refresh automatically after moving or jumping, try pressing the refresh button once.",
    showButton: "Refresh visible trees",
    jumpTitle: "Jump to a specific area",
    jumpBody: "Choose a country and a state or province, then jump to that area.",
    jumpCountry: "Country",
    jumpState: "State",
    jumpProvince: "Province",
    jumpAnyState: "Any state",
    jumpAnyProvince: "Any province",
    jumpButton: "Jump",
    searchState: "Search state",
    searchProvince: "Search province",
    filtersTitle: "Filters",
    jumpUntrackedTitle: "Not added to Pink Hunter yet",
    jumpUntrackedBody: "Pink Hunter has not added tree data for this area yet."
  },
  "zh-CN": {
    showTitle: "显示树木",
    showBody: "会刷新重新加载当前屏幕地图区域的所有已覆盖树木的数据。如果地图在变换过程中没有自动刷新，请尝试点击旁边的刷新按钮。",
    showButton: "刷新当前画面树木",
    jumpTitle: "跳转至指定区域",
    jumpBody: "选择国家和州/省后，点击 Jump 按钮即可跳转到对应区域。",
    jumpCountry: "国家",
    jumpState: "州",
    jumpProvince: "省",
    jumpAnyState: "任意州",
    jumpAnyProvince: "任意省",
    jumpButton: "跳转",
    searchState: "搜索州",
    searchProvince: "搜索省",
    filtersTitle: "筛选",
    jumpUntrackedTitle: "Pink Hunter 暂未收录",
    jumpUntrackedBody: "Pink Hunter 目前还没有添加这个地区的树木数据。"
  },
  "zh-TW": {
    showTitle: "顯示樹木",
    showBody: "會重新整理並載入目前畫面地圖區域中的所有已覆蓋樹木資料。如果地圖在變換過程中沒有自動更新，請嘗試點擊旁邊的重新整理按鈕。",
    showButton: "重新整理目前畫面樹木",
    jumpTitle: "跳轉至指定區域",
    jumpBody: "選擇國家和州／省後，點擊 Jump 按鈕即可跳轉到對應區域。",
    jumpCountry: "國家",
    jumpState: "州",
    jumpProvince: "省",
    jumpAnyState: "任意州",
    jumpAnyProvince: "任意省",
    jumpButton: "跳轉",
    searchState: "搜尋州",
    searchProvince: "搜尋省",
    filtersTitle: "篩選",
    jumpUntrackedTitle: "Pink Hunter 尚未收錄",
    jumpUntrackedBody: "Pink Hunter 目前還沒有加入這個地區的樹木資料。"
  },
  "es-ES": {
    showTitle: "Mostrar árboles",
    showBody:
      "Vuelve a cargar todos los datos de árboles cubiertos dentro del área visible del mapa. Si el mapa no se actualiza automáticamente después de moverlo o saltar a otra zona, prueba con el botón de recarga.",
    showButton: "Recargar árboles visibles",
    jumpTitle: "Saltar a una zona específica",
    jumpBody: "Elige un país y un estado o provincia, y luego pulsa Jump para ir a esa zona.",
    jumpCountry: "País",
    jumpState: "Estado",
    jumpProvince: "Provincia",
    jumpAnyState: "Cualquier estado",
    jumpAnyProvince: "Cualquier provincia",
    jumpButton: "Saltar",
    searchState: "Buscar estado",
    searchProvince: "Buscar provincia",
    filtersTitle: "Filtros",
    jumpUntrackedTitle: "Aún no se ha añadido a Pink Hunter",
    jumpUntrackedBody: "Pink Hunter todavía no ha añadido datos de árboles para esta zona."
  },
  "ko-KR": {
    showTitle: "나무 표시",
    showBody:
      "현재 화면에 보이는 지도 영역 안의 모든 커버된 나무 데이터를 다시 불러옵니다. 지도를 이동하거나 점프한 뒤 자동으로 새로고침되지 않으면 옆의 새로고침 버튼을 눌러 보세요.",
    showButton: "현재 화면 나무 새로고침",
    jumpTitle: "지정한 지역으로 이동",
    jumpBody: "국가와 주 또는 도를 선택한 뒤 Jump 버튼을 누르면 해당 지역으로 이동합니다.",
    jumpCountry: "국가",
    jumpState: "주",
    jumpProvince: "도",
    jumpAnyState: "모든 주",
    jumpAnyProvince: "모든 도",
    jumpButton: "이동",
    searchState: "주 검색",
    searchProvince: "도 검색",
    filtersTitle: "필터",
    jumpUntrackedTitle: "Pink Hunter에 아직 추가되지 않음",
    jumpUntrackedBody: "Pink Hunter는 아직 이 지역의 나무 데이터를 추가하지 않았습니다."
  },
  "ja-JP": {
    showTitle: "木を表示",
    showBody:
      "現在画面に表示されている地図範囲の、すべての対象樹木データを再読み込みします。地図を移動したりジャンプしたあと自動更新されない場合は、横の更新ボタンを押してください。",
    showButton: "表示中の木を更新",
    jumpTitle: "指定した地域へ移動",
    jumpBody: "国と州または県を選んでから Jump ボタンを押すと、その地域へ移動します。",
    jumpCountry: "国",
    jumpState: "州",
    jumpProvince: "県",
    jumpAnyState: "すべての州",
    jumpAnyProvince: "すべての県",
    jumpButton: "移動",
    searchState: "州を検索",
    searchProvince: "県を検索",
    filtersTitle: "フィルター",
    jumpUntrackedTitle: "Pink Hunter に未追加",
    jumpUntrackedBody: "Pink Hunter はこの地域の樹木データをまだ追加していません。"
  },
  "fr-FR": {
    showTitle: "Afficher les arbres",
    showBody:
      "Recharge toutes les données d’arbres couvertes dans la zone actuellement visible sur la carte. Si la carte ne se met pas à jour automatiquement après un déplacement ou un saut, utilisez le bouton d’actualisation.",
    showButton: "Actualiser les arbres visibles",
    jumpTitle: "Aller vers une zone précise",
    jumpBody: "Choisissez un pays puis un état ou une province, puis appuyez sur Jump pour aller vers cette zone.",
    jumpCountry: "Pays",
    jumpState: "État",
    jumpProvince: "Province",
    jumpAnyState: "Tout état",
    jumpAnyProvince: "Toute province",
    jumpButton: "Aller",
    searchState: "Rechercher un état",
    searchProvince: "Rechercher une province",
    filtersTitle: "Filtres",
    jumpUntrackedTitle: "Pas encore ajouté à Pink Hunter",
    jumpUntrackedBody: "Pink Hunter n’a pas encore ajouté de données d’arbres pour cette zone."
  },
  "vi-VN": {
    showTitle: "Hiển thị cây",
    showBody:
      "Tải lại toàn bộ dữ liệu cây đã được bao phủ trong vùng bản đồ hiện đang nhìn thấy. Nếu bản đồ không tự làm mới sau khi di chuyển hoặc nhảy tới vùng khác, hãy thử bấm nút làm mới bên cạnh.",
    showButton: "Làm mới cây đang nhìn thấy",
    jumpTitle: "Nhảy tới khu vực cụ thể",
    jumpBody: "Chọn quốc gia rồi chọn tiểu bang hoặc tỉnh, sau đó bấm Jump để chuyển tới khu vực đó.",
    jumpCountry: "Quốc gia",
    jumpState: "Tiểu bang",
    jumpProvince: "Tỉnh",
    jumpAnyState: "Mọi tiểu bang",
    jumpAnyProvince: "Mọi tỉnh",
    jumpButton: "Nhảy",
    searchState: "Tìm tiểu bang",
    searchProvince: "Tìm tỉnh",
    filtersTitle: "Bộ lọc",
    jumpUntrackedTitle: "Pink Hunter chưa thêm khu vực này",
    jumpUntrackedBody: "Pink Hunter hiện chưa thêm dữ liệu cây cho khu vực này."
  }
};

const REGION_SWITCH_BOUNDS: Partial<Record<CoverageRegion, [[number, number], [number, number]]>> = {
  wa: [
    [-122.62, 47.23],
    [-121.86, 47.83]
  ]
};

const REGION_COUNTRY_EMOJIS: Record<CoverageRegion, string> = {
  wa: "🇺🇸",
  ca: "🇺🇸",
  nv: "🇺🇸",
  dc: "🇺🇸",
  or: "🇺🇸",
  tx: "🇺🇸",
  ut: "🇺🇸",
  bc: "🇨🇦",
  on: "🇨🇦",
  qc: "🇨🇦",
  va: "🇺🇸",
  md: "🇺🇸",
  nj: "🇺🇸",
  ny: "🇺🇸",
  pa: "🇺🇸",
  ma: "🇺🇸"
};
const REGION_SORT_LABELS: Record<CoverageRegion, string> = {
  wa: "Washington",
  ca: "California",
  nv: "Nevada",
  dc: "Washington, DC",
  or: "Oregon",
  tx: "Texas",
  ut: "Utah",
  bc: "British Columbia",
  on: "Ontario",
  qc: "Quebec",
  va: "Virginia",
  md: "Maryland",
  nj: "New Jersey",
  ny: "New York",
  pa: "Pennsylvania",
  ma: "Massachusetts"
};
type CountryKey = "us" | "ca";
const REGION_COUNTRY_KEYS: Record<CoverageRegion, CountryKey> = {
  wa: "us",
  ca: "us",
  nv: "us",
  dc: "us",
  or: "us",
  tx: "us",
  ut: "us",
  bc: "ca",
  on: "ca",
  qc: "ca",
  va: "us",
  md: "us",
  nj: "us",
  ny: "us",
  pa: "us",
  ma: "us"
};
const COUNTRY_LABELS: Record<Language, Record<CountryKey, string>> = {
  "en-US": { us: "United States", ca: "Canada" },
  "zh-CN": { us: "美国", ca: "加拿大" },
  "zh-TW": { us: "美國", ca: "加拿大" },
  "es-ES": { us: "Estados Unidos", ca: "Canadá" },
  "ko-KR": { us: "미국", ca: "캐나다" },
  "ja-JP": { us: "アメリカ", ca: "カナダ" },
  "fr-FR": { us: "États-Unis", ca: "Canada" },
  "vi-VN": { us: "Hoa Kỳ", ca: "Canada" }
};
const CROSS_REGION_POPUP_COPY: Record<
  Language,
  { title: string; body: string; button: string }
> = {
  "en-US": {
    title: "Covered in another state or province",
    body: "This area is covered, but its tree data belongs to {region}.",
    button: "Show {region} data"
  },
  "zh-CN": {
    title: "这个区域属于其他州/省",
    body: "这个区域已经覆盖，但它的树木数据属于 {region}。",
    button: "显示 {region} 的数据"
  },
  "zh-TW": {
    title: "這個區域屬於其他州／省",
    body: "這個區域已經覆蓋，但它的樹木資料屬於 {region}。",
    button: "顯示 {region} 的資料"
  },
  "es-ES": {
    title: "Cubierto en otro estado o provincia",
    body: "Esta zona está cubierta, pero sus datos de árboles pertenecen a {region}.",
    button: "Mostrar datos de {region}"
  },
  "ko-KR": {
    title: "다른 주 / 주(省)에 속한 지역입니다",
    body: "이 지역은 이미 커버되어 있지만, 나무 데이터는 {region}에 속합니다.",
    button: "{region} 데이터 보기"
  },
  "ja-JP": {
    title: "別の州・省に属するエリアです",
    body: "このエリアはカバー済みですが、樹木データは {region} に属しています。",
    button: "{region} のデータを見る"
  },
  "fr-FR": {
    title: "Zone couverte dans un autre État / province",
    body: "Cette zone est couverte, mais ses données d'arbres appartiennent à {region}.",
    button: "Afficher les données de {region}"
  },
  "vi-VN": {
    title: "Khu vực này thuộc bang / tỉnh bang khác",
    body: "Khu vực này đã được phủ, nhưng dữ liệu cây của nó thuộc về {region}.",
    button: "Hiện dữ liệu của {region}"
  }
};
const LANGUAGE_LIST_CONJUNCTION: Record<Language, string> = {
  "en-US": "and",
  "zh-CN": "和",
  "zh-TW": "和",
  "es-ES": "y",
  "ko-KR": "및",
  "ja-JP": "と",
  "fr-FR": "et",
  "vi-VN": "và"
};

interface SelectedTree {
  coordinates: [number, number];
  properties: TreeFeatureProps;
}

interface SelectedCoverage {
  coordinates: [number, number];
  properties: CoverageFeatureProps;
}

interface JumpNotice {
  kind: "official_unavailable" | "untracked";
  title: string;
  body: string;
}

type AboutSummaryMode = "region" | "area";

function ContactIconLink({
  href,
  label,
  children
}: {
  href: string;
  label: string;
  children: ReactNode;
}): JSX.Element {
  const external = href.startsWith("http");
  return (
    <a
      aria-label={label}
      className="about-contact-link"
      href={href}
      rel={external ? "noreferrer" : undefined}
      target={external ? "_blank" : undefined}
      title={label}
    >
      {children}
    </a>
  );
}

function ContactIcons(): JSX.Element {
  return (
    <div className="about-contact-links">
      <ContactIconLink href="mailto:flalaz@uw.edu" label="Email Flala Zhang">
        <svg aria-hidden="true" viewBox="0 0 24 24">
          <path d="M3 6.75A2.75 2.75 0 0 1 5.75 4h12.5A2.75 2.75 0 0 1 21 6.75v10.5A2.75 2.75 0 0 1 18.25 20H5.75A2.75 2.75 0 0 1 3 17.25V6.75Zm2 .29v.21l7 4.83 7-4.83v-.21c0-.41-.34-.75-.75-.75H5.75c-.41 0-.75.34-.75.75Zm14 2.64-6.43 4.43a1 1 0 0 1-1.14 0L5 9.68v7.57c0 .41.34.75.75.75h12.5c.41 0 .75-.34.75-.75V9.68Z" />
        </svg>
      </ContactIconLink>
      <ContactIconLink href="https://github.com/FlalaGoGoGo" label="GitHub FlalaGoGoGo">
        <svg aria-hidden="true" viewBox="0 0 24 24">
          <path d="M12 2.5a9.5 9.5 0 0 0-3 18.51c.48.09.66-.2.66-.46v-1.7c-2.68.58-3.24-1.14-3.24-1.14-.44-1.08-1.06-1.37-1.06-1.37-.87-.58.07-.57.07-.57.97.07 1.48.96 1.48.96.85 1.43 2.24 1.02 2.79.77.09-.61.34-1.02.62-1.25-2.14-.24-4.39-1.04-4.39-4.63 0-1.02.37-1.84.97-2.49-.1-.24-.42-1.21.09-2.53 0 0 .8-.25 2.62.95A9.8 9.8 0 0 1 12 7.14c.87 0 1.75.12 2.57.35 1.82-1.2 2.62-.95 2.62-.95.51 1.32.19 2.29.09 2.53.61.65.97 1.47.97 2.49 0 3.6-2.25 4.39-4.4 4.63.35.29.66.85.66 1.72v2.55c0 .26.18.55.67.46A9.5 9.5 0 0 0 12 2.5Z" />
        </svg>
      </ContactIconLink>
      <ContactIconLink href="https://www.instagram.com/FlalaGoGoGo/" label="Instagram FlalaGoGoGo">
        <svg aria-hidden="true" viewBox="0 0 24 24">
          <path d="M7.25 3h9.5A4.25 4.25 0 0 1 21 7.25v9.5A4.25 4.25 0 0 1 16.75 21h-9.5A4.25 4.25 0 0 1 3 16.75v-9.5A4.25 4.25 0 0 1 7.25 3Zm0 2A2.25 2.25 0 0 0 5 7.25v9.5A2.25 2.25 0 0 0 7.25 19h9.5A2.25 2.25 0 0 0 19 16.75v-9.5A2.25 2.25 0 0 0 16.75 5h-9.5Zm9.9 1.4a1.1 1.1 0 1 1 0 2.2 1.1 1.1 0 0 1 0-2.2ZM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z" />
        </svg>
      </ContactIconLink>
    </div>
  );
}

function renderBoldName(text: string, name: string): ReactNode {
  const parts = text.split(name);
  if (parts.length === 1) {
    return text;
  }

  return parts.flatMap((part, index) => {
    if (index === parts.length - 1) {
      return [part];
    }
    return [part, <strong key={`${name}-${index}`}>{name}</strong>];
  });
}

interface UrlState {
  region: CoverageRegion;
  language: Language;
  species: SpeciesGroup[];
  ownership: OwnershipGroup[];
  cities: string[];
  zipCodes: string[];
  hasSpeciesParam: boolean;
  hasOwnershipParam: boolean;
  hasCityParam: boolean;
  hasZipParam: boolean;
  hasViewportParam: boolean;
  zoom: number;
  lat: number;
  lon: number;
}

function parseLanguage(raw: string | null): Language {
  if (isSupportedLanguage(raw)) {
    return raw;
  }
  return DEFAULT_LANGUAGE;
}

function parseDelimited<T extends string>(
  raw: string | null,
  allowed: readonly T[],
  fallback: readonly T[]
): T[] {
  if (raw === "none") {
    return [];
  }
  if (!raw) {
    return [...fallback];
  }
  const values = raw
    .split(",")
    .map((item) => item.trim())
    .filter((item): item is T => allowed.includes(item as T));
  return values.length > 0 ? values : [...fallback];
}

function parseStringList(raw: string | null): string[] {
  if (!raw || raw === "none") {
    return [];
  }
  return raw
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function parseUrlState(): UrlState {
  const params = new URLSearchParams(window.location.search);
  const cities = parseStringList(params.get("city"));
  const region = parseRegion(params.get("region"), cities);
  const language = parseLanguage(params.get("lang"));
  const hasSpeciesParam = params.has("species");
  const hasOwnershipParam = params.has("ownership");
  const hasCityParam = params.has("city");
  const hasZipParam = params.has("zip");
  const species = parseDelimited(params.get("species"), ALL_SPECIES, ALL_SPECIES);
  const ownership = parseDelimited(params.get("ownership"), ALL_OWNERSHIP, ALL_OWNERSHIP);
  const zipCodes = parseStringList(params.get("zip"));

  const zoom = Number(params.get("z"));
  const lat = Number(params.get("lat"));
  const lon = Number(params.get("lon"));
  const hasViewportParam = params.has("z") && params.has("lat") && params.has("lon");

  return {
    region,
    language,
    species,
    ownership,
    cities,
    zipCodes,
    hasSpeciesParam,
    hasOwnershipParam,
    hasCityParam,
    hasZipParam,
    hasViewportParam,
    zoom: Number.isFinite(zoom) ? zoom : DEFAULT_ZOOM,
    lat: Number.isFinite(lat) ? lat : DEFAULT_CENTER[1],
    lon: Number.isFinite(lon) ? lon : DEFAULT_CENTER[0]
  };
}

function boundsForRegion(regionMeta: RegionMeta | null): [[number, number], [number, number]] | null {
  return regionMeta?.bounds ?? null;
}

function preferredBoundsForRegion(
  region: CoverageRegion,
  regionMeta: RegionMeta | null
): [[number, number], [number, number]] | null {
  return REGION_SWITCH_BOUNDS[region] ?? boundsForRegion(regionMeta);
}

function webMercatorToLonLat(x: number, y: number): [number, number] {
  const lon = (x / 20037508.34) * 180;
  const lat = (Math.atan(Math.exp((y / 20037508.34) * Math.PI)) * 360) / Math.PI - 90;
  return [lon, lat];
}

function normalizeMapBounds(bounds: BoundsTuple | null): BoundsTuple | null {
  if (!bounds) {
    return null;
  }

  const hasProjectedCoordinates = Math.abs(bounds[0][0]) > 180 || Math.abs(bounds[0][1]) > 90;
  if (!hasProjectedCoordinates) {
    return normalizeBounds(bounds);
  }

  const [minLon, minLat] = webMercatorToLonLat(bounds[0][0], bounds[0][1]);
  const [maxLon, maxLat] = webMercatorToLonLat(bounds[1][0], bounds[1][1]);
  return normalizeBounds([
    [minLon, minLat],
    [maxLon, maxLat]
  ]);
}

function normalizeBounds(bounds: BoundsTuple): BoundsTuple {
  const [[x1, y1], [x2, y2]] = bounds;
  return [
    [Math.min(x1, x2), Math.min(y1, y2)],
    [Math.max(x1, x2), Math.max(y1, y2)]
  ];
}

function boundsIntersect(left: BoundsTuple, right: BoundsTuple): boolean {
  const [[leftMinX, leftMinY], [leftMaxX, leftMaxY]] = normalizeBounds(left);
  const [[rightMinX, rightMinY], [rightMaxX, rightMaxY]] = normalizeBounds(right);
  return !(leftMaxX < rightMinX || rightMaxX < leftMinX || leftMaxY < rightMinY || rightMaxY < leftMinY);
}

function boundsContainPoint(bounds: BoundsTuple, lon: number, lat: number): boolean {
  const [[minX, minY], [maxX, maxY]] = normalizeBounds(bounds);
  return lon >= minX && lon <= maxX && lat >= minY && lat <= maxY;
}

function mergeTreeCollections(collections: TreeCollection[]): TreeCollection {
  return toTreeCollection(collections.flatMap((collection) => collection.features));
}

function setDocumentMeta(selector: string, content: string): void {
  const element = document.head.querySelector<HTMLMetaElement>(selector);
  if (element) {
    element.setAttribute("content", content);
  }
}

function nearestSnap(value: number): number {
  return SNAP_POINTS.reduce((closest, snap) =>
    Math.abs(snap - value) < Math.abs(closest - value) ? snap : closest
  );
}

function toTreeCollection(features: TreeCollection["features"]): TreeCollection {
  return {
    type: "FeatureCollection",
    features
  };
}

function getTreeCoordinates(feature: TreeCollection["features"][number]): [number, number] {
  const [lon, lat] = feature.geometry.coordinates;
  return [lon, lat];
}

function buildCoverageCollection(
  coverageFeatures: CoverageCollection["features"],
  polygonClippingModule: MapRuntimeDeps["polygonClipping"]
): CoverageCollection {
  const occupied: ClipMultiPolygon[] = [];
  const sortedFeatures = [...coverageFeatures].sort(
    (left, right) => geometryAreaApprox(left.geometry) - geometryAreaApprox(right.geometry)
  );

  const features = sortedFeatures
    .map((feature) => {
      const subject = geometryToClipMultiPolygon(feature.geometry);
      const clipped =
        occupied.length > 0
          ? (polygonClippingModule.difference(subject, ...occupied) as ClipMultiPolygon | null)
          : subject;
      const geometry = clipMultiPolygonToGeometry(clipped);
      if (!geometry) {
        return null;
      }
      occupied.push(geometryToClipMultiPolygon(geometry));
      return {
        ...feature,
        geometry
      };
    })
    .filter((feature): feature is CoverageCollection["features"][number] => feature !== null);

  return {
    type: "FeatureCollection",
    features
  };
}

function ringAreaApprox(ring: number[][]): number {
  let area = 0;
  for (let index = 0; index < ring.length - 1; index += 1) {
    const [x1, y1] = ring[index];
    const [x2, y2] = ring[index + 1];
    area += x1 * y2 - x2 * y1;
  }
  return Math.abs(area) / 2;
}

function geometryAreaApprox(geometry: CoverageCollection["features"][number]["geometry"]): number {
  if (geometry.type === "Polygon") {
    return geometry.coordinates.reduce((sum, ring, index) => sum + (index === 0 ? ringAreaApprox(ring) : 0), 0);
  }
  return geometry.coordinates.reduce(
    (sum, polygon) => sum + polygon.reduce((polySum, ring, index) => polySum + (index === 0 ? ringAreaApprox(ring) : 0), 0),
    0
  );
}

function geometryToClipMultiPolygon(
  geometry: CoverageCollection["features"][number]["geometry"]
): ClipMultiPolygon {
  return (geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates) as unknown as ClipMultiPolygon;
}

function clipMultiPolygonToGeometry(
  geometry: ClipMultiPolygon | null
): CoverageCollection["features"][number]["geometry"] | null {
  if (!geometry || geometry.length === 0) {
    return null;
  }
  if (geometry.length === 1) {
    return {
      type: "Polygon",
      coordinates: geometry[0]
    };
  }
  return {
    type: "MultiPolygon",
    coordinates: geometry
  };
}

function parseRegion(raw: string | null, cities: string[]): CoverageRegion {
  if (raw === "wa" || raw === "ca" || raw === "or" || raw === "dc" || raw === "bc" || raw === "on" || raw === "qc" || raw === "va" || raw === "md" || raw === "nj" || raw === "ny" || raw === "pa" || raw === "ma") {
    return raw;
  }
  if (cities.length > 0) {
    return regionForCity(cities[0]);
  }
  return "wa";
}

function regionForCity(city: string): CoverageRegion {
  if (REGION_CITY_OVERRIDES[city]) {
    return REGION_CITY_OVERRIDES[city] as CoverageRegion;
  }
  if (city === "Washington DC" || city.endsWith(" DC")) {
    return "dc";
  }
  if (city.endsWith(" VA") || city.endsWith(", VA")) {
    return "va";
  }
  if (city.endsWith(" MD") || city.endsWith(", MD")) {
    return "md";
  }
  if (city.endsWith(" NJ") || city.endsWith(", NJ")) {
    return "nj";
  }
  if (city.endsWith(" NY") || city.endsWith(", NY")) {
    return "ny";
  }
  if (city.endsWith(" PA") || city.endsWith(", PA")) {
    return "pa";
  }
  if (city.endsWith(" MA") || city.endsWith(", MA")) {
    return "ma";
  }
  if (city.endsWith(" ON") || city.endsWith(", ON")) {
    return "on";
  }
  if (city.endsWith(" QC") || city.endsWith(", QC")) {
    return "qc";
  }
  if (city.endsWith(" OR") || city.endsWith(", OR")) {
    return "or";
  }
  if (city.endsWith(" CA") || city.endsWith(", CA")) {
    return "ca";
  }
  if (city.endsWith(" BC") || city.endsWith(", BC")) {
    return "bc";
  }
  return "wa";
}

function stateCodeForCity(city: string): string {
  const region = regionForCity(city);
  if (region === "dc") {
    return "DC";
  }
  if (region === "bc") {
    return "BC";
  }
  if (region === "va") {
    return "VA";
  }
  if (region === "md") {
    return "MD";
  }
  if (region === "nj") {
    return "NJ";
  }
  if (region === "ny") {
    return "NY";
  }
  if (region === "pa") {
    return "PA";
  }
  if (region === "ma") {
    return "MA";
  }
  if (region === "on") {
    return "ON";
  }
  if (region === "qc") {
    return "QC";
  }
  if (region === "or") {
    return "OR";
  }
  if (region === "ca") {
    return "CA";
  }
  return "WA";
}

function jurisdictionDisplayName(city: string): string {
  return JURISDICTION_OVERRIDES[city]?.displayName ?? city;
}

function jurisdictionTypeForCity(city: string): JurisdictionType {
  return JURISDICTION_OVERRIDES[city]?.type ?? "city";
}

function areaTypeLabel(language: Language, city: string): string {
  return t(language, jurisdictionTypeForCity(city) === "county" ? "countyBadge" : "cityBadge");
}

function areaTypeClassName(city: string): string {
  return jurisdictionTypeForCity(city) === "county" ? "county" : "city";
}

function formatAreaLabel(city: string): string {
  const displayName = jurisdictionDisplayName(city).trim();
  const stateCode = stateCodeForCity(city);
  if (new RegExp(`(?:,\\s*|\\s+)${stateCode}$`, "i").test(displayName)) {
    return displayName;
  }
  return `${displayName}, ${stateCode}`;
}

function hasKnownZipCode(zipCode: string | null): zipCode is string {
  return Boolean(zipCode && zipCode.trim() && zipCode.trim().toLowerCase() !== "unknown");
}

function regionOptionLabel(language: Language, region: CoverageRegion): string {
  return `${REGION_COUNTRY_EMOJIS[region]} ${regionLabel(language, region)}`;
}

function formatLanguageList(language: Language, items: string[]): string {
  const values = items.filter(Boolean);
  if (values.length <= 1) {
    return values[0] ?? "";
  }

  const conjunction = LANGUAGE_LIST_CONJUNCTION[language];
  if (values.length === 2) {
    return `${values[0]} ${conjunction} ${values[1]}`;
  }

  return `${values.slice(0, -1).join(", ")}, ${conjunction} ${values[values.length - 1]}`;
}

function formatCoverageScope(language: Language, regions: CoverageRegion[]): string {
  const grouped = new Map<CountryKey, string[]>();

  regions.forEach((region) => {
    const country = REGION_COUNTRY_KEYS[region];
    const current = grouped.get(country) ?? [];
    current.push(region.toUpperCase());
    grouped.set(country, current);
  });

  const countryOrder: CountryKey[] = ["us", "ca"];

  return countryOrder
    .filter((country) => grouped.has(country))
    .map((country) => {
      const labels = [...(grouped.get(country) ?? [])].sort((left, right) => left.localeCompare(right));
      return `${COUNTRY_LABELS[language][country]} (${formatLanguageList(language, labels)})`;
    })
    .join("; ");
}

function formatCrossRegionPopup(language: Language, region: CoverageRegion): { title: string; body: string; button: string } {
  const regionName = regionLabel(language, region);
  const copy = CROSS_REGION_POPUP_COPY[language];
  return {
    title: copy.title,
    body: copy.body.split("{region}").join(regionName),
    button: copy.button.split("{region}").join(regionName)
  };
}

function createSelectedBloomImageData(): ImageData {
  const size = 120;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d");
  if (!context) {
    throw new Error("Canvas 2D context is unavailable.");
  }
  const ctx = context;

  const center = size / 2;

  function drawTriangle(radius: number, rotation: number): void {
    ctx.beginPath();
    for (let index = 0; index < 3; index += 1) {
      const angle = rotation + (index * (Math.PI * 2)) / 3;
      const x = center + Math.cos(angle) * radius;
      const y = center + Math.sin(angle) * radius;
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.closePath();
  }

  ctx.clearRect(0, 0, size, size);
  ctx.strokeStyle = "rgba(255,255,255,0.92)";
  ctx.lineWidth = 11;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  drawTriangle(34, -Math.PI / 2);
  ctx.stroke();
  drawTriangle(34, Math.PI / 2);
  ctx.stroke();

  ctx.shadowColor = "rgba(124, 51, 82, 0.24)";
  ctx.shadowBlur = 12;
  ctx.strokeStyle = "#6f3550";
  ctx.lineWidth = 5;
  drawTriangle(34, -Math.PI / 2);
  ctx.stroke();
  drawTriangle(34, Math.PI / 2);
  ctx.stroke();
  ctx.shadowBlur = 0;

  ctx.beginPath();
  ctx.arc(center, center, 11, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(255, 248, 252, 0.98)";
  ctx.fill();
  ctx.lineWidth = 4;
  ctx.strokeStyle = "#de5f95";
  ctx.stroke();

  return ctx.getImageData(0, 0, size, size);
}

function isHttpUrl(value: string): boolean {
  return /^https?:\/\//i.test(value);
}

function sourceEndpointSearchText(endpoint: string): string {
  if (!isHttpUrl(endpoint)) {
    return endpoint.toLowerCase();
  }

  try {
    const url = new URL(endpoint);
    return `${url.hostname} ${url.pathname} ${endpoint}`.toLowerCase();
  } catch {
    return endpoint.toLowerCase();
  }
}

function escapeHtml(raw: string): string {
  return raw
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

async function resolveMapStyle(): Promise<{ styleUrl: string; preset: MapStylePreset }> {
  try {
    const response = await fetch(POSITRON_STYLE_URL, { method: "GET" });
    if (response.ok) {
      return { styleUrl: POSITRON_STYLE_URL, preset: "positron" };
    }
  } catch {
    // Fall through to default style.
  }

  return { styleUrl: FALLBACK_STYLE_URL, preset: "demotiles" };
}

export default function App(): JSX.Element {
  const initialUrlState = useMemo(parseUrlState, []);
  const initialLayoutMode: LayoutMode =
    typeof window !== "undefined" && window.innerWidth >= 1024 ? "desktop_split" : "mobile_sheet";

  const [data, setData] = useState<StaticAppData | null>(null);
  const [mapRuntime, setMapRuntime] = useState<MapRuntimeDeps | null>(null);
  const [regionAreaIndexCache, setRegionAreaIndexCache] = useState<Partial<Record<CoverageRegion, AreaIndex>>>({});
  const [regionShardCache, setRegionShardCache] = useState<
    Partial<Record<CoverageRegion, Record<string, TreeCollection>>>
  >({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingAreaIndexes, setLoadingAreaIndexes] = useState(false);
  const [loadingShards, setLoadingShards] = useState(false);
  const [mapReady, setMapReady] = useState(false);
  const [visitorCount, setVisitorCount] = useState<number | null>(null);

  const [activeRegion, setActiveRegion] = useState<CoverageRegion>(initialUrlState.region);
  const [language, setLanguage] = useState<Language>(initialUrlState.language);
  const [selectedSpecies, setSelectedSpecies] = useState<SpeciesGroup[]>(initialUrlState.species);
  const [selectedOwnership, setSelectedOwnership] = useState<OwnershipGroup[]>(initialUrlState.ownership);
  const [jumpCountry, setJumpCountry] = useState<JumpCountry["id"]>("us");
  const [jumpState, setJumpState] = useState<string>("");
  const [jumpStateSearch, setJumpStateSearch] = useState("");
  const [jumpNotice, setJumpNotice] = useState<JumpNotice | null>(null);
  const [languageMenuOpen, setLanguageMenuOpen] = useState(false);
  const [sheetHeight, setSheetHeight] = useState<number>(0.4);
  const [activePanel, setActivePanel] = useState<"filters" | "guide" | "about">("filters");
  const [aboutSourcesPage, setAboutSourcesPage] = useState(0);
  const [aboutSourcesSearchQuery, setAboutSourcesSearchQuery] = useState("");
  const [aboutRegionSummaryPage, setAboutRegionSummaryPage] = useState(0);
  const [aboutRegionSummarySearchQuery, setAboutRegionSummarySearchQuery] = useState("");
  const [aboutAreaSummaryPage, setAboutAreaSummaryPage] = useState(0);
  const [aboutAreaSummarySearchQuery, setAboutAreaSummarySearchQuery] = useState("");
  const [aboutSummaryMode, setAboutSummaryMode] = useState<AboutSummaryMode>("region");
  const [selectedTree, setSelectedTree] = useState<SelectedTree | null>(null);
  const [selectedCoverage, setSelectedCoverage] = useState<SelectedCoverage | null>(null);
  const [layoutMode, setLayoutMode] = useState<LayoutMode>(initialLayoutMode);
  const [mapStylePreset, setMapStylePreset] = useState<MapStylePreset>("positron");
  const [mapView, setMapView] = useState({
    zoom: initialUrlState.zoom,
    lat: initialUrlState.lat,
    lon: initialUrlState.lon
  });
  const [viewportBounds, setViewportBounds] = useState<BoundsTuple | null>(null);

  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const languageMenuRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const popupRef = useRef<MapLibrePopup | null>(null);
  const filteredFeaturesRef = useRef<TreeCollection["features"]>([]);
  const isDesktopRef = useRef(layoutMode === "desktop_split");
  const activeRegionRef = useRef(activeRegion);
  const pendingRegionFitRef = useRef<CoverageRegion | null>(null);
  const dragStateRef = useRef<{ startY: number; startHeight: number; dragging: boolean }>({
    startY: 0,
    startHeight: 0.4,
    dragging: false
  });

  const isDesktop = layoutMode === "desktop_split";

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const [loadedData, runtimeDeps] = await Promise.all([loadStaticAppData(), loadMapRuntimeDeps()]);
        if (cancelled) {
          return;
        }
        setData(loadedData);
        setMapRuntime(runtimeDeps);
      } catch (loadError) {
        const message = loadError instanceof Error ? loadError.message : "Unknown loading error";
        if (!cancelled) {
          setError(message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const count = await loadVisitorCount();
        if (!cancelled) {
          setVisitorCount(count);
        }
      } catch (loadError) {
        console.warn("visitor-count-unavailable", loadError);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(min-width: 1024px)");
    const handleChange = (event: MediaQueryListEvent): void => {
      setLayoutMode(event.matches ? "desktop_split" : "mobile_sheet");
    };

    setLayoutMode(mediaQuery.matches ? "desktop_split" : "mobile_sheet");
    mediaQuery.addEventListener("change", handleChange);
    return () => {
      mediaQuery.removeEventListener("change", handleChange);
    };
  }, []);

  useEffect(() => {
    isDesktopRef.current = isDesktop;
    mapRef.current?.resize();
  }, [isDesktop]);

  useEffect(() => {
    activeRegionRef.current = activeRegion;
  }, [activeRegion]);

  const regionMetaById = useMemo(() => {
    const entries = (data?.meta.regions ?? []).map((regionMeta) => [regionMeta.id, regionMeta]);
    return new Map(entries as Array<[CoverageRegion, RegionMeta]>);
  }, [data]);

  const activeRegionMeta = regionMetaById.get(activeRegion) ?? null;
  const activeLanguageOption = LANGUAGE_OPTIONS.find((option) => option.id === language) ?? LANGUAGE_OPTIONS[0];

  useEffect(() => {
    const map = mapRef.current;
    if (!mapReady || !map || pendingRegionFitRef.current !== activeRegion) {
      return;
    }

    const bounds = preferredBoundsForRegion(activeRegion, activeRegionMeta);
    if (!bounds) {
      return;
    }

    map.fitBounds(bounds, {
      padding: isDesktop ? 80 : 48,
      duration: 700
    });
    pendingRegionFitRef.current = null;
  }, [activeRegion, activeRegionMeta, isDesktop, mapReady]);

  useEffect(() => {
    if (!data) {
      return;
    }
    const fallbackRegion = data.meta.default_region;
    if (!regionMetaById.get(activeRegion)?.available) {
      setActiveRegion(fallbackRegion);
    }
  }, [activeRegion, data, regionMetaById]);

  const effectiveViewportBounds = viewportBounds ?? preferredBoundsForRegion(activeRegion, activeRegionMeta);

  const visibleRegions = useMemo(() => {
    if (!data) {
      return [] as RegionMeta[];
    }
    const viewport = effectiveViewportBounds;
    const availableRegions = data.meta.regions.filter((region) => region.available);
    if (!viewport) {
      return activeRegionMeta ? [activeRegionMeta] : availableRegions;
    }
    const matched = availableRegions.filter((region) => boundsIntersect(region.bounds, viewport));
    return matched;
  }, [activeRegionMeta, data, effectiveViewportBounds]);

  const visibleRegionIds = useMemo(() => visibleRegions.map((region) => region.id), [visibleRegions]);

  const pendingAreaIndexRegions = useMemo(
    () =>
      visibleRegions.filter((region) => region.area_split?.ready && !regionAreaIndexCache[region.id]).map((region) => region.id),
    [regionAreaIndexCache, visibleRegions]
  );

  useEffect(() => {
    if (pendingAreaIndexRegions.length === 0) {
      return;
    }

    let cancelled = false;
    setLoadingAreaIndexes(true);
    setError(null);

    void (async () => {
      try {
        const loaded = await Promise.all(
          pendingAreaIndexRegions.map(async (regionId) => {
            const regionMeta = regionMetaById.get(regionId);
            const indexPath = regionMeta?.area_split?.index_path;
            if (!indexPath) {
              throw new Error(`Missing area index path for region ${regionId}`);
            }
            return [regionId, await loadAreaIndex(indexPath)] as const;
          })
        );
        if (cancelled) {
          return;
        }
        setRegionAreaIndexCache((current) => ({
          ...current,
          ...Object.fromEntries(loaded)
        }));
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Unknown area index loading error");
        }
      } finally {
        if (!cancelled) {
          setLoadingAreaIndexes(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [pendingAreaIndexRegions, regionMetaById]);

  const visibleAreaEntries = useMemo(
    () =>
      visibleRegionIds.flatMap((regionId) =>
        (regionAreaIndexCache[regionId]?.items ?? []).map((item) => ({ region: regionId, item }))
      ),
    [regionAreaIndexCache, visibleRegionIds]
  );

  const allOwnershipOptions = useMemo(() => {
    const groups = visibleAreaEntries.flatMap(({ item }) => item.ownership_groups ?? []);
    const ordered = (["public", "private", "unknown"] as const).filter((item) => groups.includes(item));
    return ordered.length > 0 ? [...ordered] : (["public", "private"] as OwnershipGroup[]);
  }, [visibleAreaEntries]);

  const viewportAreaEntries = useMemo(() => {
    if (!effectiveViewportBounds) {
      return visibleAreaEntries;
    }
    return visibleAreaEntries.filter(({ item }) => boundsIntersect(item.bounds, effectiveViewportBounds));
  }, [effectiveViewportBounds, visibleAreaEntries]);

  const viewportShardEntries = useMemo(() => {
    const next: Array<{ region: CoverageRegion; shard: AreaShard }> = [];
    const seen = new Set<string>();

    viewportAreaEntries.forEach(({ region, item }) => {
      const candidateShards = effectiveViewportBounds
        ? item.shards.filter((shard) => boundsIntersect(shard.bounds, effectiveViewportBounds))
        : item.shards;
      candidateShards.forEach((shard) => {
        const key = `${region}:${shard.data_path}`;
        if (!seen.has(key)) {
          seen.add(key);
          next.push({ region, shard });
        }
      });
    });

    return next;
  }, [effectiveViewportBounds, viewportAreaEntries]);

  const requiredAreaEntries = useMemo(() => {
    if (selectedSpecies.length === 0 || selectedOwnership.length === 0) {
      return [] as Array<{ region: CoverageRegion; item: AreaIndexItem }>;
    }
    if (!effectiveViewportBounds) {
      return visibleAreaEntries;
    }
    return viewportAreaEntries;
  }, [effectiveViewportBounds, selectedOwnership.length, selectedSpecies.length, viewportAreaEntries, visibleAreaEntries]);

  const requiredShardEntries = useMemo(() => {
    const next: Array<{ region: CoverageRegion; shard: AreaShard }> = [];
    const seen = new Set<string>();

    requiredAreaEntries.forEach(({ region, item }) => {
      const candidateShards = effectiveViewportBounds
        ? item.shards.filter((shard) => boundsIntersect(shard.bounds, effectiveViewportBounds))
        : item.shards;
      candidateShards.forEach((shard) => {
        const key = `${region}:${shard.data_path}`;
        if (!seen.has(key)) {
          seen.add(key);
          next.push({ region, shard });
        }
      });
    });

    return next;
  }, [effectiveViewportBounds, requiredAreaEntries]);

  const missingRequiredShardEntries = useMemo(
    () =>
      requiredShardEntries.filter(({ region, shard }) => !regionShardCache[region]?.[shard.data_path]),
    [regionShardCache, requiredShardEntries]
  );

  const activeRegionPending = Boolean(
    data && (loadingAreaIndexes || loadingShards || pendingAreaIndexRegions.length > 0 || missingRequiredShardEntries.length > 0)
  );

  useEffect(() => {
    if (missingRequiredShardEntries.length === 0) {
      return;
    }

    let cancelled = false;
    setLoadingShards(true);
    setError(null);

    void (async () => {
      try {
        const loaded = await Promise.all(
          missingRequiredShardEntries.map(async ({ region, shard }) => {
            return [region, shard.data_path, await loadTreeCollection(shard.data_path)] as const;
          })
        );
        if (cancelled) {
          return;
        }
        setRegionShardCache((current) => {
          const next = { ...current };
          loaded.forEach(([region, dataPath, collection]) => {
            next[region] = {
              ...(next[region] ?? {}),
              [dataPath]: collection
            };
          });
          return next;
        });
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Unknown tree loading error");
        }
      } finally {
        if (!cancelled) {
          setLoadingShards(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [missingRequiredShardEntries]);

  const currentTrees = useMemo(
    () =>
      mergeTreeCollections(
        requiredShardEntries
          .map(({ region, shard }) => regionShardCache[region]?.[shard.data_path])
          .filter((collection): collection is TreeCollection => Boolean(collection))
      ),
    [regionShardCache, requiredShardEntries]
  );

  const jumpCountries = useMemo(() => {
    if (!data) {
      return [] as JumpCountry[];
    }
    return [...data.jumpIndex.countries].sort((left, right) => SORT_COLLATOR.compare(left.label, right.label));
  }, [data]);

  const allJumpStates = useMemo(() => {
    if (!data) {
      return [] as JumpState[];
    }
    return [...data.jumpIndex.states]
      .filter((item) => item.country_id === jumpCountry)
      .sort((left, right) => SORT_COLLATOR.compare(left.label, right.label));
  }, [data, jumpCountry]);

  const jumpStates = useMemo(() => {
    const query = jumpStateSearch.trim().toLowerCase();
    if (!query) {
      return allJumpStates;
    }
    return allJumpStates.filter((item) => {
      return item.label.toLowerCase().includes(query) || item.code.toLowerCase().includes(query);
    });
  }, [allJumpStates, jumpStateSearch]);

  useEffect(() => {
    if (!data) {
      return;
    }
    const fallbackCountry = REGION_COUNTRY_KEYS[activeRegion];
    setJumpCountry((current) =>
      current && data.jumpIndex.countries.some((item) => item.id === current) ? current : fallbackCountry
    );
    setJumpState((current) =>
      current && data.jumpIndex.states.some((item) => item.id === current) ? current : activeRegion
    );
  }, [activeRegion, data]);

  useEffect(() => {
    if (!jumpState) {
      return;
    }
    if (!allJumpStates.some((item) => item.id === jumpState)) {
      setJumpState("");
    }
  }, [allJumpStates, jumpState]);

  const displayCoverage = useMemo(() => {
    if (!data) {
      return { type: "FeatureCollection", features: [] } as CoverageCollection;
    }
    if (!mapRuntime) {
      return data.coverage;
    }
    return buildCoverageCollection(data.coverage.features, mapRuntime.polygonClipping);
  }, [data, mapRuntime]);

  const filteredFeatures = useMemo(() => {
    if (selectedSpecies.length === 0 || selectedOwnership.length === 0) {
      return [] as TreeCollection["features"];
    }

    const speciesSet = new Set(selectedSpecies);
    const ownershipSet = new Set(selectedOwnership);

    return currentTrees.features.filter((feature) => {
      const props = feature.properties;
      return speciesSet.has(props.species_group) && ownershipSet.has(props.ownership);
    });
  }, [currentTrees, selectedOwnership, selectedSpecies]);

  const ownershipOptions = useMemo(() => {
    if (currentTrees.features.length === 0) {
      return allOwnershipOptions;
    }

    const options = new Set<OwnershipGroup>();

    currentTrees.features.forEach((feature) => {
      options.add(feature.properties.ownership);
    });

    const narrowed = (["public", "private", "unknown"] as const).filter((item) => options.has(item));
    return narrowed.length > 0 ? [...narrowed] : allOwnershipOptions;
  }, [allOwnershipOptions, currentTrees]);

  const filteredCollection = useMemo(() => toTreeCollection(filteredFeatures), [filteredFeatures]);
  const showMapLoadingOverlay = activeRegionPending && filteredFeatures.length === 0;

  useEffect(() => {
    filteredFeaturesRef.current = filteredFeatures;
  }, [filteredFeatures]);

  useEffect(() => {
    setSelectedOwnership((current) => {
      if (ownershipOptions.length === 0) {
        return current;
      }
      if (current.length === 0) {
        return current;
      }
      return current.filter((item) => ownershipOptions.includes(item));
    });
  }, [ownershipOptions]);

  useEffect(() => {
    const handlePointerDown = (event: PointerEvent): void => {
      if (!languageMenuRef.current?.contains(event.target as Node)) {
        setLanguageMenuOpen(false);
      }
    };

    document.addEventListener("pointerdown", handlePointerDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
    };
  }, []);

  const guideCompareCopy = GUIDE_COMPARE_COPY[language];
  const aboutCopy = ABOUT_COPY[language];
  const findPanelCopy = FIND_PANEL_COPY[language];
  const jumpSubnationalLabel = jumpCountry === "us" ? findPanelCopy.jumpState : findPanelCopy.jumpProvince;
  const jumpAnySubnationalLabel = jumpCountry === "us" ? findPanelCopy.jumpAnyState : findPanelCopy.jumpAnyProvince;
  const jumpSubnationalSearchPlaceholder = jumpCountry === "us" ? findPanelCopy.searchState : findPanelCopy.searchProvince;

  useEffect(() => {
    document.title = t(language, "browserTitle");
    setDocumentMeta('meta[name="description"]', t(language, "browserDescription"));
    setDocumentMeta('meta[property="og:title"]', t(language, "browserTitle"));
    setDocumentMeta('meta[property="og:description"]', t(language, "browserDescription"));
    setDocumentMeta('meta[name="twitter:title"]', t(language, "browserTitle"));
    setDocumentMeta('meta[name="twitter:description"]', t(language, "browserDescription"));
  }, [language]);

  const aboutSources = useMemo(() => {
    if (!data) {
      return [] as AppMeta["sources"];
    }
    return [...data.meta.sources].sort(
      (left, right) =>
        SORT_COLLATOR.compare(formatAreaLabel(left.city), formatAreaLabel(right.city)) ||
        SORT_COLLATOR.compare(left.name, right.name)
    );
  }, [data]);

  const normalizedAboutSourceSearchQuery = aboutSourcesSearchQuery.trim().toLowerCase();

  const filteredAboutSources = useMemo(() => {
    if (!normalizedAboutSourceSearchQuery) {
      return aboutSources;
    }

    return aboutSources.filter((source) => {
      const searchHaystack = [
        source.city,
        formatAreaLabel(source.city),
        source.name,
        source.endpoint,
        sourceEndpointSearchText(source.endpoint)
      ]
        .join(" ")
        .toLowerCase();

      return searchHaystack.includes(normalizedAboutSourceSearchQuery);
    });
  }, [aboutSources, normalizedAboutSourceSearchQuery]);

  const aboutSourcePageCount = Math.max(1, Math.ceil(filteredAboutSources.length / ABOUT_SOURCES_PAGE_SIZE));

  const pagedAboutSources = useMemo(
    () =>
      filteredAboutSources.slice(
        aboutSourcesPage * ABOUT_SOURCES_PAGE_SIZE,
        (aboutSourcesPage + 1) * ABOUT_SOURCES_PAGE_SIZE
      ),
    [filteredAboutSources, aboutSourcesPage]
  );

  useEffect(() => {
    setAboutSourcesPage((current) => Math.min(current, aboutSourcePageCount - 1));
  }, [aboutSourcePageCount]);

  useEffect(() => {
    setAboutSourcesPage(0);
  }, [normalizedAboutSourceSearchQuery]);

  const aboutRegionSummaries = useMemo(() => {
    if (!data) {
      return [] as Array<{
        id: CoverageRegion;
        label: string;
        sortLabel: string;
        searchLabel: string;
        totalTrees: number;
        speciesCounts: SpeciesCounts;
      }>;
    }

    return data.meta.regions
      .filter((region) => region.available && region.tree_count > 0)
      .map((region) => ({
        id: region.id,
        label: regionOptionLabel(language, region.id),
        sortLabel: regionLabel(language, region.id),
        searchLabel: `${regionLabel(language, region.id)} ${REGION_SORT_LABELS[region.id]} ${region.id.toUpperCase()}`,
        totalTrees: region.tree_count,
        speciesCounts: region.species_counts ?? EMPTY_SPECIES_COUNTS
      }))
      .sort((left, right) => SORT_COLLATOR.compare(left.sortLabel, right.sortLabel));
  }, [data, language]);

  const normalizedAboutRegionSummarySearchQuery = aboutRegionSummarySearchQuery.trim().toLowerCase();

  const aboutCoverageScope = useMemo(() => {
    if (!data) {
      return "";
    }

    const coveredRegions = data.meta.regions
      .filter((region) => region.available && region.tree_count > 0)
      .map((region) => region.id);

    return formatCoverageScope(language, coveredRegions);
  }, [data, language]);

  const filteredAboutRegionSummaries = useMemo(() => {
    if (!normalizedAboutRegionSummarySearchQuery) {
      return aboutRegionSummaries;
    }

    return aboutRegionSummaries.filter(({ label, searchLabel, id }) => {
      const query = normalizedAboutRegionSummarySearchQuery;
      return (
        label.toLowerCase().includes(query) ||
        searchLabel.toLowerCase().includes(query) ||
        id.toUpperCase().includes(query.toUpperCase())
      );
    });
  }, [aboutRegionSummaries, normalizedAboutRegionSummarySearchQuery]);

  const aboutRegionSummaryPageCount = Math.max(
    1,
    Math.ceil(filteredAboutRegionSummaries.length / ABOUT_REGION_SUMMARY_PAGE_SIZE)
  );

  const pagedAboutRegionSummaries = useMemo(
    () =>
      filteredAboutRegionSummaries.slice(
        aboutRegionSummaryPage * ABOUT_REGION_SUMMARY_PAGE_SIZE,
        (aboutRegionSummaryPage + 1) * ABOUT_REGION_SUMMARY_PAGE_SIZE
      ),
    [filteredAboutRegionSummaries, aboutRegionSummaryPage]
  );

  useEffect(() => {
    setAboutRegionSummaryPage((current) => Math.min(current, aboutRegionSummaryPageCount - 1));
  }, [aboutRegionSummaryPageCount]);

  useEffect(() => {
    setAboutRegionSummaryPage(0);
  }, [normalizedAboutRegionSummarySearchQuery]);

  const aboutAreaSummaries = useMemo(() => {
    if (!data) {
      return [] as Array<{
        jurisdiction: string;
        label: string;
        sortLabel: string;
        searchLabel: string;
        totalTrees: number;
        speciesCounts: SpeciesCounts;
        areaType: JurisdictionType;
      }>;
    }

    return (data.meta.areas ?? [])
      .filter((area) => area.tree_count > 0)
      .map((area) => {
        const label = formatAreaLabel(area.jurisdiction);
        return {
          jurisdiction: area.jurisdiction,
          label,
          sortLabel: label,
          searchLabel: `${label} ${jurisdictionDisplayName(area.jurisdiction)} ${regionLabel(language, area.region)} ${REGION_SORT_LABELS[area.region]} ${area.region.toUpperCase()}`,
          totalTrees: area.tree_count,
          speciesCounts: area.species_counts ?? EMPTY_SPECIES_COUNTS,
          areaType: jurisdictionTypeForCity(area.jurisdiction)
        };
      })
      .sort((left, right) => SORT_COLLATOR.compare(left.sortLabel, right.sortLabel));
  }, [data, language]);

  const normalizedAboutAreaSummarySearchQuery = aboutAreaSummarySearchQuery.trim().toLowerCase();

  const filteredAboutAreaSummaries = useMemo(() => {
    if (!normalizedAboutAreaSummarySearchQuery) {
      return aboutAreaSummaries;
    }

    return aboutAreaSummaries.filter(({ label, searchLabel, jurisdiction }) => {
      const query = normalizedAboutAreaSummarySearchQuery;
      return (
        label.toLowerCase().includes(query) ||
        searchLabel.toLowerCase().includes(query) ||
        jurisdiction.toLowerCase().includes(query)
      );
    });
  }, [aboutAreaSummaries, normalizedAboutAreaSummarySearchQuery]);

  const aboutAreaSummaryPageCount = Math.max(
    1,
    Math.ceil(filteredAboutAreaSummaries.length / ABOUT_AREA_SUMMARY_PAGE_SIZE)
  );

  const pagedAboutAreaSummaries = useMemo(
    () =>
      filteredAboutAreaSummaries.slice(
        aboutAreaSummaryPage * ABOUT_AREA_SUMMARY_PAGE_SIZE,
        (aboutAreaSummaryPage + 1) * ABOUT_AREA_SUMMARY_PAGE_SIZE
      ),
    [filteredAboutAreaSummaries, aboutAreaSummaryPage]
  );

  useEffect(() => {
    setAboutAreaSummaryPage((current) => Math.min(current, aboutAreaSummaryPageCount - 1));
  }, [aboutAreaSummaryPageCount]);

  useEffect(() => {
    setAboutAreaSummaryPage(0);
  }, [normalizedAboutAreaSummarySearchQuery]);

  const activeAboutSummaryTitle =
    aboutSummaryMode === "region" ? aboutCopy.summaryByRegionTitle : aboutCopy.summaryByAreaTitle;
  const activeAboutSummarySearchPlaceholder =
    aboutSummaryMode === "region" ? aboutCopy.summarySearchPlaceholder : aboutCopy.summaryAreaSearchPlaceholder;
  const activeAboutSummaryEmpty =
    aboutSummaryMode === "region" ? aboutCopy.summaryEmpty : aboutCopy.summaryAreaEmpty;
  const activeAboutSummaryPage = aboutSummaryMode === "region" ? aboutRegionSummaryPage : aboutAreaSummaryPage;
  const activeAboutSummaryPageCount =
    aboutSummaryMode === "region" ? aboutRegionSummaryPageCount : aboutAreaSummaryPageCount;

  useEffect(() => {
    if (!data || !mapRuntime || mapRef.current || !mapContainerRef.current) {
      return;
    }

    let isCancelled = false;
    let mapInstance: MapLibreMap | null = null;
    setMapReady(false);

    void (async () => {
      try {
        const { styleUrl, preset } = await resolveMapStyle();
        if (isCancelled || !mapContainerRef.current) {
          return;
        }

        setMapStylePreset(preset);

        const map = new mapRuntime.maplibre.Map({
          container: mapContainerRef.current,
          style: styleUrl,
          center: [initialUrlState.lon, initialUrlState.lat],
          zoom: initialUrlState.zoom,
          minZoom: 5,
          maxZoom: 18,
          attributionControl: false
        });

        mapInstance = map;
        mapRef.current = map;

        map.on("error", (event) => {
          console.error("map-runtime-error", event?.error ?? event);
        });

        map.on("load", () => {
          setMapReady(true);
          map.addControl(new mapRuntime.maplibre.ScaleControl({ maxWidth: 110, unit: "metric" }), "bottom-right");

        map.addSource("coverage", {
          type: "geojson",
          data: displayCoverage
        });

        map.addLayer({
          id: "coverage-official-unavailable",
          type: "fill",
          source: "coverage",
          filter: ["==", ["get", "status"], "official_unavailable"],
          paint: {
            "fill-color": COVERAGE_COLORS.unavailableFill,
            "fill-opacity": 0.34
          }
        });

        map.addLayer({
          id: "coverage-covered",
          type: "fill",
          source: "coverage",
          filter: ["==", ["get", "status"], "covered"],
          paint: {
            "fill-color": COVERAGE_COLORS.coveredFill,
            "fill-opacity": 0.18
          }
        });

        map.addLayer({
          id: "coverage-unavailable-outline",
          type: "line",
          source: "coverage",
          filter: ["==", ["get", "status"], "official_unavailable"],
          paint: {
            "line-color": COVERAGE_COLORS.unavailableLine,
            "line-width": 1.45,
            "line-dasharray": [2.4, 2.2]
          }
        });

        map.addLayer({
          id: "coverage-outline",
          type: "line",
          source: "coverage",
          filter: ["==", ["get", "status"], "covered"],
          paint: {
            "line-color": COVERAGE_COLORS.coveredLine,
            "line-width": 1.5,
            "line-dasharray": [2, 2]
          }
        });

        map.addSource("trees", {
          type: "geojson",
          data: filteredCollection,
          cluster: true,
          clusterMaxZoom: 11,
          clusterRadius: 48
        });

        map.addLayer({
          id: "tree-clusters",
          type: "circle",
          source: "trees",
          filter: ["has", "point_count"],
          paint: {
            "circle-color": "#f4a8c5",
            "circle-radius": ["step", ["get", "point_count"], 13, 35, 17, 120, 21],
            "circle-stroke-width": 1.5,
            "circle-stroke-color": "#ffffff",
            "circle-opacity": 0.95
          }
        });

        map.addLayer({
          id: "tree-cluster-count",
          type: "symbol",
          source: "trees",
          filter: ["has", "point_count"],
          layout: {
            "text-field": ["get", "point_count_abbreviated"],
            "text-size": 12,
            "text-font": ["Open Sans Bold"]
          },
          paint: {
            "text-color": "#4f2d3d"
          }
        });

        ALL_SPECIES.forEach((species) => {
          map.addLayer({
            id: `tree-${species}`,
            type: "circle",
            source: "trees",
            filter: ["all", ["!", ["has", "point_count"]], ["==", ["get", "species_group"], species]],
            paint: {
              "circle-color": POINT_COLORS[species],
              "circle-radius": ["interpolate", ["linear"], ["zoom"], 8, 1.8, 12, 3.4, 15, 5.6],
              "circle-opacity": 0.92,
              "circle-stroke-color": "#ffffff",
              "circle-stroke-width": 0.75
            }
          });
        });

        if (!map.hasImage(SELECTED_MARKER_IMAGE_ID)) {
          map.addImage(SELECTED_MARKER_IMAGE_ID, createSelectedBloomImageData());
        }

        map.addLayer({
          id: "tree-selected-halo",
          type: "circle",
          source: "trees",
          filter: ["==", ["get", "id"], "__none__"],
          paint: {
            "circle-color": "rgba(255, 250, 253, 0.86)",
            "circle-radius": ["interpolate", ["linear"], ["zoom"], 8, 6.5, 15, 10.5],
            "circle-opacity": 0.98,
            "circle-blur": 0.12
          }
        });

        map.addLayer({
          id: "tree-selected-star",
          type: "symbol",
          source: "trees",
          filter: ["==", ["get", "id"], "__none__"],
          layout: {
            "icon-image": SELECTED_MARKER_IMAGE_ID,
            "icon-size": ["interpolate", ["linear"], ["zoom"], 8, 0.26, 12, 0.34, 15, 0.42],
            "icon-allow-overlap": true,
            "icon-ignore-placement": true
          }
        });

        map.on("click", "tree-clusters", (event: MapLayerMouseEvent) => {
          const features = map.queryRenderedFeatures(event.point, { layers: ["tree-clusters"] });
          if (features.length === 0) {
            return;
          }

          const clusterId = features[0].properties?.cluster_id;
          const source = map.getSource("trees") as GeoJSONSource;
          if (clusterId == null || !source) {
            return;
          }

          void source
            .getClusterExpansionZoom(Number(clusterId))
            .then((zoom) => {
              const geometry = features[0].geometry;
              if (!geometry || geometry.type !== "Point") {
                return;
              }

              map.easeTo({
                center: geometry.coordinates as [number, number],
                zoom
              });
            })
            .catch(() => {
              // Ignore cluster expansion failures.
            });
        });

        map.on("click", (event: MapLayerMouseEvent) => {
          const clusterFeatures = map.queryRenderedFeatures(event.point, { layers: ["tree-clusters"] });
          if (clusterFeatures.length > 0) {
            return;
          }

          const features = map.queryRenderedFeatures(event.point, { layers: [...POINT_LAYER_IDS] });
          if (features.length === 0) {
            const coverageFeatures = map.queryRenderedFeatures(event.point, {
              layers: [
                "coverage-covered",
                "coverage-outline",
                "coverage-official-unavailable",
                "coverage-unavailable-outline"
              ]
            });
            if (coverageFeatures.length === 0) {
              return;
            }

            const coverageFeature =
              coverageFeatures.find((feature) => feature.properties?.status === "official_unavailable") ??
              coverageFeatures[0];
            const coverageProperties = coverageFeature.properties;
            const jurisdiction = coverageProperties?.jurisdiction;
            if (!jurisdiction) {
              return;
            }

            const coverageStatus = String(coverageProperties.status ?? "official_unavailable");
            if (coverageStatus === "covered") {
              const targetRegion = regionForCity(String(jurisdiction));
              if (targetRegion === activeRegionRef.current) {
                return;
              }

              setSelectedTree(null);
              setSelectedCoverage({
                coordinates: [event.lngLat.lng, event.lngLat.lat],
                properties: {
                  id: String(coverageProperties.id ?? `coverage-${jurisdiction}`),
                  status: "covered",
                  jurisdiction: String(jurisdiction),
                  note: targetRegion
                }
              });
              return;
            }

            setSelectedTree(null);
            setSelectedCoverage({
              coordinates: [event.lngLat.lng, event.lngLat.lat],
              properties: {
                id: String(coverageProperties.id ?? `coverage-${jurisdiction}`),
                status: "official_unavailable",
                jurisdiction: String(jurisdiction),
                note: String(coverageProperties.note ?? "")
              }
            });
            return;
          }

          const id = features[0].properties?.id;
          if (!id) {
            return;
          }

          const matched = filteredFeaturesRef.current.find((feature) => feature.properties.id === id);
          if (!matched) {
            return;
          }

          setSelectedTree({
            coordinates: getTreeCoordinates(matched),
            properties: matched.properties
          });
          setSelectedCoverage(null);
          if (!isDesktopRef.current) {
            setSheetHeight(0.72);
            setActivePanel("filters");
          }
        });

        map.on("mouseenter", "tree-clusters", () => {
          map.getCanvas().style.cursor = "pointer";
        });
        map.on("mouseleave", "tree-clusters", () => {
          map.getCanvas().style.cursor = "";
        });

        POINT_LAYER_IDS.forEach((layerId) => {
          map.on("mouseenter", layerId, () => {
            map.getCanvas().style.cursor = "pointer";
          });

          map.on("mouseleave", layerId, () => {
            map.getCanvas().style.cursor = "";
          });
        });

        ["coverage-covered", "coverage-outline", "coverage-official-unavailable", "coverage-unavailable-outline"].forEach((layerId) => {
          map.on("mouseenter", layerId, () => {
            map.getCanvas().style.cursor = "pointer";
          });

          map.on("mouseleave", layerId, () => {
            map.getCanvas().style.cursor = "";
          });
        });

        map.on("moveend", () => {
          const center = map.getCenter();
          const bounds = map.getBounds();
          const availableRegions = (data?.meta.regions ?? []).filter((region) => region.available);
          const centerRegion = availableRegions.find((region) =>
            boundsContainPoint(region.bounds, center.lng, center.lat)
          );

          setViewportBounds([
            [bounds.getWest(), bounds.getSouth()],
            [bounds.getEast(), bounds.getNorth()]
          ]);
          setMapView({
            zoom: Number(map.getZoom().toFixed(2)),
            lat: Number(center.lat.toFixed(5)),
            lon: Number(center.lng.toFixed(5))
          });

          if (centerRegion && activeRegionRef.current !== centerRegion.id) {
            setActiveRegion(centerRegion.id);
          }
        });

        if (!initialUrlState.hasViewportParam) {
          const defaultBounds = preferredBoundsForRegion(
            initialUrlState.region,
            regionMetaById.get(initialUrlState.region) ?? null
          );
          if (defaultBounds) {
            map.fitBounds(defaultBounds, {
              padding: isDesktopRef.current ? 80 : 48,
              duration: 0
            });
            setViewportBounds(defaultBounds);
            const center = map.getCenter();
            setMapView({
              zoom: Number(map.getZoom().toFixed(2)),
              lat: Number(center.lat.toFixed(5)),
              lon: Number(center.lng.toFixed(5))
            });
          }
        } else {
          const bounds = map.getBounds();
          setViewportBounds([
            [bounds.getWest(), bounds.getSouth()],
            [bounds.getEast(), bounds.getNorth()]
          ]);
        }
        });
      } catch (mapError) {
        console.error("map-init-failed", mapError);
        if (!isCancelled) {
          setError(mapError instanceof Error ? mapError.message : "Failed to initialize map.");
        }
      }
    })();

    return () => {
      isCancelled = true;
      setMapReady(false);
      popupRef.current?.remove();
      popupRef.current = null;
      if (mapInstance) {
        mapInstance.remove();
      }
      if (mapRef.current === mapInstance) {
        mapRef.current = null;
      }
    };
  }, [
    data,
    initialUrlState.hasViewportParam,
    initialUrlState.lat,
    initialUrlState.lon,
    initialUrlState.region,
    initialUrlState.zoom,
    mapRuntime,
    regionMetaById
  ]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapRuntime) {
      return;
    }
    const source = map.getSource("trees") as GeoJSONSource | undefined;
    if (source) {
      source.setData(filteredCollection);
    }

    if (selectedTree && !filteredFeatures.find((feature) => feature.properties.id === selectedTree.properties.id)) {
      setSelectedTree(null);
    }
  }, [filteredCollection, filteredFeatures, selectedTree]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) {
      return;
    }

    const source = map.getSource("coverage") as GeoJSONSource | undefined;
    if (source) {
      source.setData(displayCoverage);
    }
  }, [displayCoverage]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) {
      return;
    }

    const selectedId = selectedTree?.properties.id ?? "__none__";
    if (map.getLayer("tree-selected-halo")) {
      map.setFilter("tree-selected-halo", ["==", ["get", "id"], selectedId]);
    }
    if (map.getLayer("tree-selected-star")) {
      map.setFilter("tree-selected-star", ["==", ["get", "id"], selectedId]);
    }
  }, [selectedTree]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapRuntime) {
      return;
    }
    const runtime = mapRuntime;

    popupRef.current?.remove();
    popupRef.current = null;

    if (selectedTree) {
      const [lon, lat] = selectedTree.coordinates;
      const areaDisplayName = formatAreaLabel(selectedTree.properties.city);
      const areaBadge = `<span class="tree-area-type-badge ${areaTypeClassName(selectedTree.properties.city)}">${escapeHtml(
        areaTypeLabel(language, selectedTree.properties.city)
      )}</span>`;
      const zipCodeLine = hasKnownZipCode(selectedTree.properties.zip_code)
        ? `<p><strong>${escapeHtml(t(language, "zipCode"))}:</strong> ${escapeHtml(selectedTree.properties.zip_code)}</p>`
        : "";
      const subtypeLine = selectedTree.properties.subtype_name
        ? `<p><strong>${escapeHtml(t(language, "subtype"))}:</strong> ${escapeHtml(selectedTree.properties.subtype_name)}</p>`
        : "";
      const popupHtml = `
        <div class="tree-popup-card">
          <h4>${escapeHtml(speciesLabel(language, selectedTree.properties.species_group))}</h4>
          ${subtypeLine}
          <p>${escapeHtml(selectedTree.properties.scientific_name)}</p>
          <p><strong>${escapeHtml(t(language, "city"))}:</strong> <span class="area-value-inline">${escapeHtml(areaDisplayName)}${areaBadge}</span></p>
          ${zipCodeLine}
          <p><strong>${escapeHtml(t(language, "coordinates"))}:</strong> ${lon.toFixed(5)}, ${lat.toFixed(5)}</p>
        </div>
      `;

      const popup = new runtime.maplibre.Popup({
        closeButton: true,
        closeOnClick: false,
        offset: 14,
        maxWidth: "300px",
        className: "tree-popup"
      })
        .setLngLat(selectedTree.coordinates)
        .setHTML(popupHtml)
        .addTo(map);

      popup.on("close", () => {
        setSelectedTree((current) =>
          current && current.properties.id === selectedTree.properties.id ? null : current
        );
      });

      popupRef.current = popup;
      return;
    }

    if (!selectedCoverage) {
      return;
    }

    const coverageAreaDisplayName = formatAreaLabel(selectedCoverage.properties.jurisdiction);
    const coverageAreaBadge = `<span class="coverage-area-type-badge ${areaTypeClassName(
      selectedCoverage.properties.jurisdiction
    )}">${escapeHtml(areaTypeLabel(language, selectedCoverage.properties.jurisdiction))}</span>`;
    const crossRegionTarget =
      selectedCoverage.properties.status === "covered"
        ? regionForCity(selectedCoverage.properties.jurisdiction)
        : null;
    const popupHtml =
      selectedCoverage.properties.status === "covered" && crossRegionTarget
        ? (() => {
            const crossRegionCopy = formatCrossRegionPopup(language, crossRegionTarget);
            return `
              <div class="coverage-popup-card coverage-popup-card-covered">
                <h4>${escapeHtml(coverageAreaDisplayName)}</h4>
                <div class="coverage-popup-meta">${coverageAreaBadge}</div>
                <p class="coverage-popup-eyebrow">${escapeHtml(crossRegionCopy.title)}</p>
                <p>${escapeHtml(crossRegionCopy.body)}</p>
                <button class="coverage-popup-action" data-region-switch="${escapeHtml(crossRegionTarget)}" type="button">
                  ${escapeHtml(crossRegionCopy.button)}
                </button>
              </div>
            `;
          })()
        : `
            <div class="coverage-popup-card">
              <h4>${escapeHtml(coverageAreaDisplayName)}</h4>
              <div class="coverage-popup-meta">${coverageAreaBadge}</div>
              <p class="coverage-popup-eyebrow">${escapeHtml(t(language, "officialUnavailablePopupTitle"))}</p>
              <p>${escapeHtml(t(language, "officialUnavailablePopupBody"))}</p>
              <p>${escapeHtml(t(language, "officialUnavailablePopupFoot"))}</p>
              <p>${escapeHtml(t(language, "officialUnavailablePopupContact"))}</p>
            </div>
          `;

    const popup = new runtime.maplibre.Popup({
      closeButton: true,
      closeOnClick: false,
      offset: 12,
      maxWidth: "320px",
      className: "coverage-popup"
    })
      .setLngLat(selectedCoverage.coordinates)
      .setHTML(popupHtml)
      .addTo(map);

    popup.on("close", () => {
      setSelectedCoverage((current) =>
        current && current.properties.id === selectedCoverage.properties.id ? null : current
      );
    });

    if (selectedCoverage.properties.status === "covered" && crossRegionTarget) {
      const switchButton = popup.getElement().querySelector<HTMLButtonElement>("[data-region-switch]");
      switchButton?.addEventListener("click", () => {
        setSelectedCoverage(null);
        if (!isDesktopRef.current) {
          setSheetHeight(0.72);
          setActivePanel("filters");
        }
        switchRegion(crossRegionTarget);
      });
    }

    popupRef.current = popup;
  }, [activeRegion, language, mapRuntime, selectedCoverage, selectedTree]);

  useEffect(() => {
    if (!data) {
      return;
    }

    const params = new URLSearchParams();
    params.set("region", activeRegion);
    params.set("lang", language);

    if (selectedSpecies.length === 0) {
      params.set("species", "none");
    } else if (selectedSpecies.length !== ALL_SPECIES.length) {
      params.set("species", selectedSpecies.join(","));
    }

    if (selectedOwnership.length === 0) {
      params.set("ownership", "none");
    } else if (selectedOwnership.length !== allOwnershipOptions.length) {
      params.set("ownership", selectedOwnership.join(","));
    }

    params.set("z", mapView.zoom.toString());
    params.set("lat", mapView.lat.toString());
    params.set("lon", mapView.lon.toString());

    const nextUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState(null, "", nextUrl);
  }, [
    activeRegion,
    allOwnershipOptions.length,
    data,
    language,
    mapView,
    selectedOwnership,
    selectedSpecies,
  ]);

  function toggleSpecies(species: SpeciesGroup): void {
    setSelectedSpecies((current) => {
      if (current.includes(species)) {
        return current.filter((item) => item !== species);
      }
      return [...current, species];
    });
  }

  function toggleOwnership(ownership: OwnershipGroup): void {
    setSelectedOwnership((current) => {
      if (current.includes(ownership)) {
        return current.filter((item) => item !== ownership);
      }
      return [...current, ownership];
    });
  }

  function changeLanguage(nextLanguage: Language): void {
    setLanguage(nextLanguage);
    setLanguageMenuOpen(false);
  }

  function fitMapToBounds(bounds: BoundsTuple | null): void {
    const normalizedBounds = normalizeMapBounds(bounds);
    if (!normalizedBounds) {
      return;
    }
    setViewportBounds(normalizedBounds);
    const map = mapRef.current;
    if (!map || !mapReady) {
      return;
    }
    map.fitBounds(normalizedBounds, {
      padding: isDesktop ? 80 : 48,
      duration: 700
    });
  }

  function switchRegion(region: CoverageRegion): void {
    const regionMeta = regionMetaById.get(region) ?? null;
    if (!regionMeta?.available) {
      return;
    }

    const bounds = preferredBoundsForRegion(region, regionMeta);

    setSelectedTree(null);
    setSelectedCoverage(null);
    setJumpNotice(null);
    setSelectedSpecies([...ALL_SPECIES]);
    setSelectedOwnership(
      regionMeta.ownership_groups && regionMeta.ownership_groups.length > 0
        ? [...regionMeta.ownership_groups]
        : [...ALL_OWNERSHIP]
    );
    setActiveRegion(region);
    if (bounds) {
      setViewportBounds(bounds);
    }

    const map = mapRef.current;
    if (map && mapReady && bounds) {
      map.fitBounds(bounds, {
        padding: isDesktop ? 80 : 48,
        duration: 700
      });
      pendingRegionFitRef.current = null;
      return;
    }

    pendingRegionFitRef.current = region;
  }

  function handleJump(): void {
    if (!data) {
      return;
    }

    const selectedJumpState = jumpState ? jumpStates.find((item) => item.id === jumpState) ?? null : null;
    const selectedJumpCountry = jumpCountries.find((item) => item.id === jumpCountry) ?? null;
    const targetBounds = selectedJumpState?.bounds ?? selectedJumpCountry?.bounds ?? null;
    const targetRegion = selectedJumpState?.region_hint ?? null;

    setSelectedTree(null);
    setJumpNotice(null);
    setSelectedCoverage(null);

    if (targetRegion) {
      setActiveRegion(targetRegion);
    }
    fitMapToBounds(targetBounds);

    if (selectedJumpState && !selectedJumpState.region_hint) {
      setJumpNotice({
        kind: "untracked",
        title: findPanelCopy.jumpUntrackedTitle,
        body: findPanelCopy.jumpUntrackedBody
      });
    }

    if (!isDesktop) {
      setActivePanel("filters");
    }
  }

  function refreshViewportTrees(): void {
    setSelectedSpecies([...ALL_SPECIES]);
    setSelectedOwnership([...allOwnershipOptions]);
    setSelectedTree(null);
    setSelectedCoverage(null);
    setJumpNotice(null);
    setRegionShardCache((current) => {
      const next = { ...current };
      viewportShardEntries.forEach(({ region, shard }) => {
        if (!next[region]?.[shard.data_path]) {
          return;
        }
        const regionCache = { ...(next[region] ?? {}) };
        delete regionCache[shard.data_path];
        next[region] = regionCache;
      });
      return next;
    });
  }

  function clearAllFilters(): void {
    setSelectedSpecies([]);
    setSelectedOwnership([]);
    setSelectedTree(null);
    setSelectedCoverage(null);
    setJumpNotice(null);
  }

  function selectAllFilters(): void {
    setSelectedSpecies([...ALL_SPECIES]);
    setSelectedOwnership([...allOwnershipOptions]);
    setSelectedTree(null);
    setSelectedCoverage(null);
    setJumpNotice(null);
  }

  function handleSheetPointerDown(event: ReactPointerEvent<HTMLButtonElement>): void {
    dragStateRef.current = {
      startY: event.clientY,
      startHeight: sheetHeight,
      dragging: true
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function handleSheetPointerMove(event: ReactPointerEvent<HTMLButtonElement>): void {
    if (!dragStateRef.current.dragging) {
      return;
    }

    const delta = (dragStateRef.current.startY - event.clientY) / window.innerHeight;
    const nextHeight = Math.min(1, Math.max(0.4, dragStateRef.current.startHeight + delta));
    setSheetHeight(nextHeight);
  }

  function handleSheetPointerUp(event: ReactPointerEvent<HTMLButtonElement>): void {
    if (!dragStateRef.current.dragging) {
      return;
    }
    dragStateRef.current.dragging = false;
    event.currentTarget.releasePointerCapture(event.pointerId);
    setSheetHeight((current) => nearestSnap(current));
  }

  function formatCount(value: number): string {
    return value.toLocaleString(language);
  }

  function renderSpeciesCountRows(counts: SpeciesCounts, compact = false): JSX.Element {
    return (
      <div className={compact ? "species-summary-list compact" : "species-summary-list"}>
        {ALL_SPECIES.map((species) => (
          <div className={compact ? "species-summary-row compact" : "species-summary-row"} key={species}>
            <div className="species-summary-label">
              <img
                alt=""
                aria-hidden="true"
                className={compact ? "species-summary-icon compact" : "species-summary-icon"}
                src={SPECIES_ICON_ART[species]}
              />
              <span>{speciesLabel(language, species)}</span>
            </div>
            <strong>{formatCount(counts[species] ?? 0)}</strong>
          </div>
        ))}
      </div>
    );
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-shell" />
        <p>{t(language, "loading")}</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="loading-screen">
        <p>{error ?? "Failed to load data."}</p>
      </div>
    );
  }

  return (
    <div className={isDesktop ? "app-root desktop-mode" : "app-root mobile-mode"}>
      <div className="map-root" ref={mapContainerRef} />
      {showMapLoadingOverlay && (
        <div className="region-loading-overlay">
          <div className="region-loading-pill">
            <div className="region-loading-dot" />
            <span>{t(language, "loading")}</span>
          </div>
        </div>
      )}
      <section className="map-corner-legend">
        <div className="legend-row">
          <span className="legend-dot covered" />
          <span>{t(language, "coveredLegend")}</span>
        </div>
        <div className="legend-row">
          <span className="legend-dot official-unavailable" />
          <span>{t(language, "officialUnavailableLegend")}</span>
        </div>
        {mapStylePreset === "demotiles" && <p>{t(language, "fallbackBasemap")}</p>}
      </section>

      <section className="sheet" style={isDesktop ? undefined : { height: `${sheetHeight * 100}vh` }}>
        <button
          className="sheet-handle"
          onPointerDown={handleSheetPointerDown}
          onPointerMove={handleSheetPointerMove}
          onPointerUp={handleSheetPointerUp}
          type="button"
          aria-label="Resize panel"
        >
          <span />
        </button>

        <div className="sheet-content">
          <section className="panel-header-card">
            <div className="panel-header-top">
              <div className="panel-title-group">
                <span className="sr-only">{t(language, "appTitle")}</span>
                <img
                  alt="Pink Hunter"
                  className="brand-logo"
                  loading="eager"
                  src={BRAND_LOGO_PATH}
                />
                <p>{t(language, "appSubtitle")}</p>
                {visitorCount !== null && (
                  <p className="visitor-count-line">
                    {t(language, "visitorCountPrefix")}
                    <strong className="visitor-count-number">{visitorCount.toLocaleString(language)}</strong>
                    {t(language, "visitorCountSuffix")}
                  </p>
                )}
              </div>
              <div className="language-switcher" ref={languageMenuRef}>
                <button
                  aria-expanded={languageMenuOpen}
                  aria-label={t(language, "language")}
                  className="icon-btn language-btn"
                  onClick={() => setLanguageMenuOpen((current) => !current)}
                  title={t(language, "language")}
                  type="button"
                >
                  <span aria-hidden="true">{activeLanguageOption.emoji}</span>
                </button>
                {languageMenuOpen && (
                  <div className="language-menu">
                    {LANGUAGE_OPTIONS.map((option) => (
                      <button
                        className={option.id === language ? "language-option active" : "language-option"}
                        key={option.id}
                        onClick={() => changeLanguage(option.id)}
                        type="button"
                      >
                        <span className="language-option-emoji" aria-hidden="true">
                          {option.emoji}
                        </span>
                        <span className="language-option-label">{option.label}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </section>

          <div className="sheet-toolbar">
            <button
              className={activePanel === "filters" ? "tab-btn active" : "tab-btn"}
              onClick={() => setActivePanel("filters")}
              type="button"
            >
              {t(language, "showList")}
            </button>
            <button
              className={activePanel === "guide" ? "tab-btn active" : "tab-btn"}
              onClick={() => setActivePanel("guide")}
              type="button"
            >
              {t(language, "showGuide")}
            </button>
            <button
              className={activePanel === "about" ? "tab-btn active" : "tab-btn"}
              onClick={() => setActivePanel("about")}
              type="button"
            >
              {t(language, "showAbout")}
            </button>
            <div className="record-count">
              {filteredFeatures.length.toLocaleString()} {t(language, "records")}
            </div>
          </div>

          {activePanel === "filters" ? (
            <>
              <section className="filters show-panel">
                <section className="show-block">
                  <div className="show-block-header">
                    <h3>{findPanelCopy.showTitle}</h3>
                    <button
                      aria-label={findPanelCopy.showButton}
                      className="clear-btn show-all-btn"
                      onClick={refreshViewportTrees}
                      title={findPanelCopy.showButton}
                      type="button"
                    >
                      <svg aria-hidden="true" viewBox="0 0 24 24">
                        <path
                          d="M20 12a8 8 0 1 1-2.34-5.66"
                          fill="none"
                          stroke="currentColor"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                        />
                        <path
                          d="M20 4v6h-6"
                          fill="none"
                          stroke="currentColor"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                        />
                      </svg>
                    </button>
                  </div>
                  <p className="show-block-copy">{findPanelCopy.showBody}</p>
                </section>

                <section className="show-block">
                  <div className="show-block-header">
                    <h3>{findPanelCopy.jumpTitle}</h3>
                  </div>
                  <p className="show-block-copy">{findPanelCopy.jumpBody}</p>
                  <div className="jump-grid">
                    <label className="jump-field">
                      <span>{findPanelCopy.jumpCountry}</span>
                      <select
                        className="jump-select"
                        onChange={(event) => {
                          const nextCountry = event.target.value as JumpCountry["id"];
                          setJumpCountry(nextCountry);
                          setJumpState("");
                          setJumpStateSearch("");
                        }}
                        value={jumpCountry}
                      >
                        {jumpCountries.map((country) => (
                          <option key={country.id} value={country.id}>
                            {country.emoji} {COUNTRY_LABELS[language][country.id]}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label className="jump-field">
                      <span>{jumpSubnationalLabel}</span>
                      <input
                        className="filter-search-input jump-search-input"
                        onChange={(event) => setJumpStateSearch(event.target.value)}
                        placeholder={jumpSubnationalSearchPlaceholder}
                        type="search"
                        value={jumpStateSearch}
                      />
                      <select
                        className="jump-select"
                        onChange={(event) => {
                          const nextState = event.target.value;
                          setJumpState(nextState);
                        }}
                        value={jumpState}
                      >
                        <option value="">{jumpAnySubnationalLabel}</option>
                        {jumpStates.map((state) => (
                          <option key={state.id} value={state.id}>
                            {state.label}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                  <div className="jump-actions">
                    <button className="clear-btn jump-btn" onClick={handleJump} type="button">
                      {findPanelCopy.jumpButton}
                    </button>
                  </div>
                  {jumpNotice && (
                    <div className={`jump-notice ${jumpNotice.kind}`}>
                      <strong>{jumpNotice.title}</strong>
                      <p>{jumpNotice.body}</p>
                    </div>
                  )}
                </section>

                <section className="show-block">
                  <div className="filters-heading">
                    <h3>{findPanelCopy.filtersTitle}</h3>
                    <div className="filter-actions">
                      <button className="clear-btn" onClick={selectAllFilters} type="button">
                        {t(language, "selectAll")}
                      </button>
                      <button className="clear-btn" onClick={clearAllFilters} type="button">
                        {t(language, "clearAll")}
                      </button>
                    </div>
                  </div>

                  <div className="filter-group">
                    <strong>{t(language, "speciesFilter")}</strong>
                    <div className="chip-wrap">
                      {ALL_SPECIES.map((species) => (
                        <button
                          key={species}
                          className={
                            selectedSpecies.includes(species)
                              ? `chip species-chip species-chip-${species} active`
                              : `chip species-chip species-chip-${species}`
                          }
                          onClick={() => toggleSpecies(species)}
                          type="button"
                        >
                          {speciesLabel(language, species)}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="filter-group">
                    <strong>{t(language, "ownershipFilter")}</strong>
                    <div className="chip-wrap">
                      {ownershipOptions.map((item) => (
                        <button
                          key={item}
                          className={selectedOwnership.includes(item) ? "chip active" : "chip"}
                          onClick={() => toggleOwnership(item)}
                          type="button"
                        >
                          {ownershipLabel(language, item)}
                        </button>
                      ))}
                    </div>
                  </div>
                </section>
              </section>
              {activeRegionPending ? null : filteredFeatures.length === 0 ? (
                <div className="empty-state">
                  <img
                    src="/assets/ui/placeholders/empty_state_spring_tree.svg"
                    alt="No results"
                    loading="lazy"
                  />
                  <h4>{t(language, "noResultsTitle")}</h4>
                  <p>{t(language, "noResultsBody")}</p>
                </div>
              ) : (
                <p className="selection-hint">{t(language, "tapTreeHint")}</p>
              )}

              {selectedTree && (
                <article className="tree-card selected">
                  <header className="selected-tree-header">
                    <h4>{speciesLabel(language, selectedTree.properties.species_group)}</h4>
                    <img
                      alt={`${speciesLabel(language, selectedTree.properties.species_group)} icon`}
                      className="selected-tree-species-icon"
                      loading="lazy"
                      src={SPECIES_ICON_ART[selectedTree.properties.species_group]}
                    />
                  </header>
                  {selectedTree.properties.subtype_name && (
                    <p>
                      <strong>{t(language, "subtype")}: </strong>
                      {selectedTree.properties.subtype_name}
                    </p>
                  )}
                  <p>
                    <strong>{t(language, "scientific")}: </strong>
                    {selectedTree.properties.scientific_name}
                  </p>
                  <p>
                    <strong>{t(language, "common")}: </strong>
                    {selectedTree.properties.common_name ?? t(language, "unknown")}
                  </p>
                  <p>
                    <strong>{t(language, "city")}: </strong>
                    <span className="area-value-inline">
                      <span>{formatAreaLabel(selectedTree.properties.city)}</span>
                      <span className={`tree-area-type-badge ${areaTypeClassName(selectedTree.properties.city)}`}>
                        {areaTypeLabel(language, selectedTree.properties.city)}
                      </span>
                    </span>
                  </p>
                  {hasKnownZipCode(selectedTree.properties.zip_code) && (
                    <p>
                      <strong>{t(language, "zipCode")}: </strong>
                      {selectedTree.properties.zip_code}
                    </p>
                  )}
                  <p>
                    <strong>{t(language, "ownership")}: </strong>
                    {ownershipLabel(language, selectedTree.properties.ownership)} (
                    {selectedTree.properties.ownership_raw})
                  </p>
                  <p>
                    <strong>{t(language, "coordinates")}: </strong>
                    {selectedTree.coordinates[0].toFixed(5)}, {selectedTree.coordinates[1].toFixed(5)}
                  </p>
                  <p>
                    <strong>{t(language, "source")}: </strong>
                    {selectedTree.properties.source_department}
                  </p>
                </article>
              )}
            </>
          ) : activePanel === "guide" ? (
            <section className="guide-panel">
              <h3>{t(language, "guideTitle")}</h3>
              {data.guide.entries.map((entry) => (
                <article className="guide-card" key={entry.id}>
                  <div className="guide-card-hero">
                    <img
                      alt={`${entry.title[language]} illustration`}
                      className="guide-card-image"
                      loading="lazy"
                      src={GUIDE_FLOWER_ART[entry.id]}
                    />
                  </div>
                  <header>
                    <h4>{entry.title[language]}</h4>
                    <p>{entry.subtitle[language]}</p>
                  </header>
                  <ul>
                    {entry.bullets[language].map((bullet) => (
                      <li key={bullet}>{bullet}</li>
                    ))}
                  </ul>
                  <p className="tips-title">{t(language, "tipsTitle")}</p>
                  <ul>
                    {entry.confusionTips[language].map((tip) => (
                      <li key={tip}>{tip}</li>
                    ))}
                  </ul>
                </article>
              ))}
              <section className="guide-compare-section">
                <div className="guide-compare-header">
                  <h4>{guideCompareCopy.title}</h4>
                  <p>{guideCompareCopy.intro}</p>
                </div>
                <div className="guide-compare-grid">
                  {GUIDE_COMPARISON_ART.map((item) => (
                    <article className="guide-compare-card" key={item.id}>
                      <img
                        alt={item.title[language]}
                        className="guide-compare-image"
                        loading="lazy"
                        src={item.image}
                      />
                      <div className="guide-compare-copy">
                        <h5>{item.title[language]}</h5>
                        <p>{item.body[language]}</p>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            </section>
          ) : (
            <section className="about-panel">
              <div className="about-section">
                <h3 className="about-section-title">{aboutCopy.title}</h3>
                <div className="about-copy-block">
                  {aboutCopy.intro.map((paragraph) => (
                    <p key={paragraph}>{paragraph}</p>
                  ))}
                </div>
              </div>

              <div className="about-section">
                <h3 className="about-section-title">{aboutCopy.summaryTitle}</h3>
                <p className="about-summary-note">{aboutCopy.summaryNote}</p>
                <p className="about-summary-note about-summary-coverage-note">
                  {aboutCopy.summaryCoverageLead}: {aboutCoverageScope}
                </p>
                <div className="about-summary-stack">
                  <article className="about-card about-summary-card about-summary-total-card">
                    <div className="about-summary-head">
                      <div>
                        <h4>{aboutCopy.summaryAllTitle}</h4>
                      </div>
                      <strong className="about-summary-total-number">{formatCount(data.meta.included_records)}</strong>
                    </div>
                    <div className="about-summary-divider" />
                    {renderSpeciesCountRows(data.meta.species_counts ?? EMPTY_SPECIES_COUNTS)}
                  </article>

                  <article className="about-card about-summary-card about-summary-browse-card">
                    <div className="about-summary-section-head">
                      <h4>{activeAboutSummaryTitle}</h4>
                      <div className="about-summary-mode-switch" role="tablist" aria-label={aboutCopy.summaryTitle}>
                        <button
                          aria-selected={aboutSummaryMode === "region"}
                          className={aboutSummaryMode === "region" ? "tab-btn active" : "tab-btn"}
                          onClick={() => setAboutSummaryMode("region")}
                          role="tab"
                          type="button"
                        >
                          {aboutCopy.summaryByRegionTitle}
                        </button>
                        <button
                          aria-selected={aboutSummaryMode === "area"}
                          className={aboutSummaryMode === "area" ? "tab-btn active" : "tab-btn"}
                          onClick={() => setAboutSummaryMode("area")}
                          role="tab"
                          type="button"
                        >
                          {aboutCopy.summaryByAreaTitle}
                        </button>
                      </div>
                    </div>
                    <input
                      className="filter-search-input about-summary-search-input"
                      onChange={(event) =>
                        aboutSummaryMode === "region"
                          ? setAboutRegionSummarySearchQuery(event.target.value)
                          : setAboutAreaSummarySearchQuery(event.target.value)
                      }
                      placeholder={activeAboutSummarySearchPlaceholder}
                      type="search"
                      value={aboutSummaryMode === "region" ? aboutRegionSummarySearchQuery : aboutAreaSummarySearchQuery}
                    />
                    <div className="about-summary-browser-list">
                      {aboutSummaryMode === "region"
                        ? pagedAboutRegionSummaries.map((region) => (
                            <div className="about-region-summary-item" key={region.id}>
                              <div className="about-region-summary-head">
                                <strong>{region.label}</strong>
                                <span className="about-region-summary-total">{formatCount(region.totalTrees)}</span>
                              </div>
                              <div className="about-summary-divider compact" />
                              {renderSpeciesCountRows(region.speciesCounts, true)}
                            </div>
                          ))
                        : pagedAboutAreaSummaries.map((area) => (
                            <div className="about-area-summary-item" key={`${area.label}-${area.areaType}`}>
                              <div className="about-area-summary-head">
                                <div className="about-area-summary-title-stack">
                                  <div className="about-area-summary-title-row">
                                    <strong>{area.label}</strong>
                                    <span className={`coverage-area-type-badge ${areaTypeClassName(area.jurisdiction)}`}>
                                      {areaTypeLabel(language, area.jurisdiction)}
                                    </span>
                                  </div>
                                </div>
                                <span className="about-region-summary-total">{formatCount(area.totalTrees)}</span>
                              </div>
                              <div className="about-summary-divider compact" />
                              {renderSpeciesCountRows(area.speciesCounts, true)}
                            </div>
                          ))}
                      {(aboutSummaryMode === "region"
                        ? filteredAboutRegionSummaries.length === 0
                        : filteredAboutAreaSummaries.length === 0) && (
                        <p className="filter-empty">{activeAboutSummaryEmpty}</p>
                      )}
                    </div>
                    <div className="about-source-pagination">
                      <button
                        className="clear-btn"
                        disabled={
                          activeAboutSummaryPage === 0 ||
                          (aboutSummaryMode === "region"
                            ? filteredAboutRegionSummaries.length === 0
                            : filteredAboutAreaSummaries.length === 0)
                        }
                        onClick={() =>
                          aboutSummaryMode === "region"
                            ? setAboutRegionSummaryPage((current) => Math.max(0, current - 1))
                            : setAboutAreaSummaryPage((current) => Math.max(0, current - 1))
                        }
                        type="button"
                      >
                        {aboutCopy.previousPage}
                      </button>
                      <span>
                        {aboutCopy.pageLabel} {activeAboutSummaryPage + 1} / {activeAboutSummaryPageCount}
                      </span>
                      <button
                        className="clear-btn"
                        disabled={
                          activeAboutSummaryPage >= activeAboutSummaryPageCount - 1 ||
                          (aboutSummaryMode === "region"
                            ? filteredAboutRegionSummaries.length === 0
                            : filteredAboutAreaSummaries.length === 0)
                        }
                        onClick={() =>
                          aboutSummaryMode === "region"
                            ? setAboutRegionSummaryPage((current) =>
                                Math.min(aboutRegionSummaryPageCount - 1, current + 1)
                              )
                            : setAboutAreaSummaryPage((current) =>
                                Math.min(aboutAreaSummaryPageCount - 1, current + 1)
                              )
                        }
                        type="button"
                      >
                        {aboutCopy.nextPage}
                      </button>
                    </div>
                  </article>
                </div>
              </div>

              <div className="about-section">
                <h3 className="about-section-title">{aboutCopy.sourcesTitle}</h3>
                <div className="about-copy-block">
                  {aboutCopy.disclaimer.map((paragraph) => (
                    <p key={paragraph}>{paragraph}</p>
                  ))}
                </div>
                <article className="about-card about-sources-shell">
                  <input
                    className="filter-search-input about-source-search-input"
                    onChange={(event) => setAboutSourcesSearchQuery(event.target.value)}
                    placeholder={aboutCopy.sourcesSearchPlaceholder}
                    type="search"
                    value={aboutSourcesSearchQuery}
                  />
                  <div className="about-source-legend" role="presentation">
                    <span className="about-source-legend-item">
                      <span className="about-source-legend-dot official" />
                      <span>{aboutCopy.officialBadge}</span>
                    </span>
                    <span className="about-source-legend-item">
                      <span className="about-source-legend-dot supplemental" />
                      <span>{aboutCopy.supplementalBadge}</span>
                    </span>
                  </div>
                  <div className="about-source-list">
                    {pagedAboutSources.map((source) => {
                      const supplemental = source.name === "UW OSM Supplemental" || !isHttpUrl(source.endpoint);
                      return (
                        <div
                          className={`about-source-item ${supplemental ? "supplemental" : "official"}`}
                          key={`${source.city}-${source.name}`}
                        >
                          <div className="about-source-head">
                            <div className="about-source-title-row">
                              <strong>
                                {formatAreaLabel(source.city)}: {source.name}
                              </strong>
                              {isHttpUrl(source.endpoint) ? (
                                <a
                                  aria-label={aboutCopy.openLink}
                                  className="source-link-icon"
                                  href={source.endpoint}
                                  rel="noreferrer"
                                  target="_blank"
                                >
                                  <svg aria-hidden="true" viewBox="0 0 24 24">
                                    <path
                                      d="M9.35 14.65 14.65 9.35"
                                      fill="none"
                                      stroke="currentColor"
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth="2"
                                    />
                                    <path
                                      d="M7.25 14.4 5.6 16.05a3.15 3.15 0 1 0 4.45 4.45l1.65-1.65"
                                      fill="none"
                                      stroke="currentColor"
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth="2"
                                    />
                                    <path
                                      d="M16.75 9.6l1.65-1.65a3.15 3.15 0 1 0-4.45-4.45L12.3 5.15"
                                      fill="none"
                                      stroke="currentColor"
                                      strokeLinecap="round"
                                      strokeLinejoin="round"
                                      strokeWidth="2"
                                    />
                                  </svg>
                                </a>
                              ) : null}
                            </div>
                          </div>
                          {!isHttpUrl(source.endpoint) && <p>{source.endpoint}</p>}
                        </div>
                      );
                    })}
                    {filteredAboutSources.length === 0 && <p className="filter-empty">{aboutCopy.sourcesEmpty}</p>}
                  </div>
                  {aboutSources.length > 0 && (
                    <div className="about-source-pagination">
                      <button
                        className="clear-btn"
                        disabled={aboutSourcesPage === 0 || filteredAboutSources.length === 0}
                        onClick={() => setAboutSourcesPage((current) => Math.max(0, current - 1))}
                        type="button"
                      >
                        {aboutCopy.previousPage}
                      </button>
                      <span>
                        {aboutCopy.pageLabel} {aboutSourcesPage + 1} / {aboutSourcePageCount}
                      </span>
                      <button
                        className="clear-btn"
                        disabled={aboutSourcesPage >= aboutSourcePageCount - 1 || filteredAboutSources.length === 0}
                        onClick={() =>
                          setAboutSourcesPage((current) => Math.min(aboutSourcePageCount - 1, current + 1))
                        }
                        type="button"
                      >
                        {aboutCopy.nextPage}
                      </button>
                    </div>
                  )}
                </article>
              </div>

              <div className="about-section">
                <h3 className="about-section-title">{aboutCopy.contactTitle}</h3>
                <div className="about-copy-block about-contact-block">
                  <p>{renderBoldName(aboutCopy.contactLead, "Flala Zhang")}</p>
                  <ContactIcons />
                </div>
              </div>
            </section>
          )}

          <footer className="meta-row">
            {t(language, "dataUpdated")}: {new Date(data.meta.generated_at).toLocaleString(language)}
          </footer>
        </div>
      </section>
    </div>
  );
}
