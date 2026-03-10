import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
  type ReactNode
} from "react";
import { loadAreaIndex, loadCoverageRegion, loadStaticAppData, loadTreeCollection, loadVisitorCount } from "./data";
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
  BLANK_MAP_STYLE,
  buildMapboxStyleProbeUrl,
  buildMapboxStyleUrl,
  runtimeConfig
} from "./runtimeConfig";
import {
  loadMapRuntimeDeps,
  type ClipMultiPolygon,
  type GeoJSONSource,
  type MapLayerMouseEvent,
  type MapEngineMap,
  type MapEnginePopup,
  type MapRuntimeDeps
} from "./mapRuntime";
import type {
  AreaIndex,
  AreaIndexItem,
  AreaShard,
  AppMeta,
  CoverageCollection,
  CoverageFeatureProps,
  JumpArea,
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
const BRAND_MARK_PATH = "/assets/brand/pink-hunter-mark-512.png";
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
  Denver: "co",
  Austin: "tx",
  Dallas: "tx",
  "Las Vegas": "nv",
  Arlington: "va",
  Alexandria: "va",
  "Montgomery County": "md",
  Baltimore: "md",
  "Jersey City": "nj",
  Newark: "nj",
  Millburn: "nj",
  Princeton: "nj",
  "Ho-Ho-Kus": "nj",
  Oradell: "nj",
  Rutherford: "nj",
  "River Edge": "nj",
  Dumont: "nj",
  Westwood: "nj",
  Tenafly: "nj",
  Teaneck: "nj",
  Ridgewood: "nj",
  Bergenfield: "nj",
  Montvale: "nj",
  "Glen Rock": "nj",
  Englewood: "nj",
  "Franklin Lakes": "nj",
  Demarest: "nj",
  Haworth: "nj",
  "New Milford": "nj",
  Ramsey: "nj",
  Wyckoff: "nj",
  "Fair Lawn": "nj",
  Allendale: "nj",
  Mahwah: "nj",
  "Fort Lee": "nj",
  Hoboken: "nj",
  Morristown: "nj",
  Linden: "nj",
  Montclair: "nj",
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
    jumpTitle: "Jump to an area",
    jumpBody: "Choose an area, then press the Jump button below and the map will move there.",
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
    jumpBody: "选择一个区域，并点击下方「跳转」按钮，地图会跳转过去。",
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
    jumpBody: "選擇一個區域，並點擊下方「跳轉」按鈕，地圖會跳轉過去。",
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
    jumpTitle: "Ir a una zona",
    jumpBody: "Elige una zona y luego pulsa el botón de salto de abajo para mover el mapa hasta allí.",
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
    jumpBody: "지역을 선택한 뒤 아래의 이동 버튼을 누르면 지도가 그곳으로 이동합니다.",
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
    jumpBody: "地域を選び、下の移動ボタンを押すと地図がその場所へ移動します。",
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
    jumpTitle: "Aller à une zone",
    jumpBody: "Choisissez une zone puis appuyez sur le bouton ci-dessous pour déplacer la carte vers cet endroit.",
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
    jumpBody: "Chọn một khu vực rồi bấm nút nhảy bên dưới để đưa bản đồ tới đó.",
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

const DISCOVERY_COPY: Record<
  Language,
  {
    areaSearchShow: string;
    areaSearchHide: string;
    areaSearchEmpty: string;
    areaStatusCovered: string;
    areaStatusCityLevelCoverage: string;
    areaStatusOfficialUnavailable: string;
    areaStatusUntracked: string;
    locationLoading: string;
    locationRetry: string;
    locationUnsupportedTitle: string;
    locationUnsupportedBody: string;
    locationDeniedTitle: string;
    locationDeniedBody: string;
    locationTimeoutTitle: string;
    locationTimeoutBody: string;
    locationUnavailableTitle: string;
    locationUnavailableBody: string;
    officialUnavailableTitle: string;
    officialUnavailableBody: string;
    officialUnavailableCta: string;
    cityLevelCoverageTitle: string;
    cityLevelCoverageBody: string;
    cityLevelCoverageCta: string;
    untrackedTitle: string;
    untrackedBody: string;
    untrackedCta: string;
    coveredEmptyTitle: string;
    coveredEmptyBody: string;
  }
> = {
  "en-US": {
    areaSearchShow: "Search city / county",
    areaSearchHide: "Hide city / county search",
    areaSearchEmpty: "No city or county matched that search.",
    areaStatusCovered: "Covered",
    areaStatusCityLevelCoverage: "Covered cities inside",
    areaStatusOfficialUnavailable: "Official data unavailable",
    areaStatusUntracked: "Not added yet",
    locationLoading: "Locating your position...",
    locationRetry: "Try locate again",
    locationUnsupportedTitle: "This browser cannot locate you",
    locationUnsupportedBody: "Your browser does not support geolocation in this session.",
    locationDeniedTitle: "Location permission was denied",
    locationDeniedBody: "Pink Hunter could not access your location. Please allow location access and try again.",
    locationTimeoutTitle: "Location lookup timed out",
    locationTimeoutBody: "Pink Hunter could not get your position in time. Try again in a stronger-signal spot.",
    locationUnavailableTitle: "Location is unavailable",
    locationUnavailableBody: "Pink Hunter could not determine your current position right now.",
    officialUnavailableTitle: "Official boundary found, but no official public tree dataset yet",
    officialUnavailableBody:
      "Pink Hunter knows this area and can draw its official boundary, but there is still no official public single-tree dataset to load here.",
    officialUnavailableCta: "Share a data lead",
    cityLevelCoverageTitle: "Covered cities are already inside this county",
    cityLevelCoverageBody:
      "Pink Hunter does not have a single county-wide dataset for this area, but it already includes covered cities within these county bounds.",
    cityLevelCoverageCta: "Show covered trees here",
    untrackedTitle: "Pink Hunter has not added this area yet",
    untrackedBody:
      "This area is not integrated into Pink Hunter yet. If you know a public official dataset, please send it over.",
    untrackedCta: "Request this area",
    coveredEmptyTitle: "No trees match the current filters here",
    coveredEmptyBody:
      "This area is covered, but the current filters left no matching trees. Clear the filters or reload visible trees."
  },
  "zh-CN": {
    areaSearchShow: "搜索城市 / 县",
    areaSearchHide: "收起城市 / 县搜索",
    areaSearchEmpty: "没有匹配的城市或县。",
    areaStatusCovered: "已覆盖",
    areaStatusCityLevelCoverage: "县内已有覆盖城市",
    areaStatusOfficialUnavailable: "官方暂无公开数据",
    areaStatusUntracked: "尚未加入",
    locationLoading: "正在定位你的位置...",
    locationRetry: "重新定位",
    locationUnsupportedTitle: "当前浏览器不支持定位",
    locationUnsupportedBody: "这个浏览器会话暂时无法使用地理定位。",
    locationDeniedTitle: "定位权限被拒绝",
    locationDeniedBody: "Pink Hunter 无法访问你的位置。请允许定位权限后再试一次。",
    locationTimeoutTitle: "定位超时",
    locationTimeoutBody: "Pink Hunter 在限定时间内没有拿到你的位置。请在信号更好的地方再试一次。",
    locationUnavailableTitle: "暂时无法获取位置",
    locationUnavailableBody: "Pink Hunter 现在无法确定你的当前位置。",
    officialUnavailableTitle: "已确认官方边界，但暂无官方公开树木数据",
    officialUnavailableBody:
      "Pink Hunter 已经知道这个地区，也能绘制它的官方边界，但目前还没有可公开接入的官方单株树木数据。",
    officialUnavailableCta: "提供数据线索",
    cityLevelCoverageTitle: "这个县范围内已经有已覆盖城市",
    cityLevelCoverageBody:
      "Pink Hunter 目前没有这个县统一的 county 级数据集，但这个县范围内已经包含多个已覆盖城市。",
    cityLevelCoverageCta: "显示这里的已覆盖树木",
    untrackedTitle: "Pink Hunter 还没有接入这个地区",
    untrackedBody: "这个地区目前还没有被 Pink Hunter 收录。如果你知道官方公开数据源，欢迎发给我们。",
    untrackedCta: "请求添加该地区",
    coveredEmptyTitle: "这个地区当前没有符合筛选条件的树",
    coveredEmptyBody: "该地区已经覆盖，但当前筛选条件下没有匹配树木。你可以清空筛选，或重新显示当前视口的树木。"
  },
  "zh-TW": {
    areaSearchShow: "搜尋城市 / 縣",
    areaSearchHide: "收起城市 / 縣搜尋",
    areaSearchEmpty: "沒有符合的城市或縣。",
    areaStatusCovered: "已覆蓋",
    areaStatusCityLevelCoverage: "縣內已有覆蓋城市",
    areaStatusOfficialUnavailable: "官方暫無公開資料",
    areaStatusUntracked: "尚未加入",
    locationLoading: "正在定位你的位置...",
    locationRetry: "重新定位",
    locationUnsupportedTitle: "目前瀏覽器不支援定位",
    locationUnsupportedBody: "這個瀏覽器工作階段目前無法使用地理定位。",
    locationDeniedTitle: "定位權限被拒絕",
    locationDeniedBody: "Pink Hunter 無法取得你的位置。請允許定位權限後再試一次。",
    locationTimeoutTitle: "定位逾時",
    locationTimeoutBody: "Pink Hunter 沒有在限定時間內取得你的位置。請到訊號更好的地方再試一次。",
    locationUnavailableTitle: "暫時無法取得位置",
    locationUnavailableBody: "Pink Hunter 目前無法確認你的即時位置。",
    officialUnavailableTitle: "已確認官方邊界，但暫無官方公開樹木資料",
    officialUnavailableBody:
      "Pink Hunter 已知道這個地區，也能繪製它的官方邊界，但目前還沒有可公開接入的官方單株樹木資料。",
    officialUnavailableCta: "提供資料線索",
    cityLevelCoverageTitle: "這個縣範圍內已經有已覆蓋城市",
    cityLevelCoverageBody:
      "Pink Hunter 目前沒有這個縣統一的 county 級資料集，但這個縣範圍內已經包含多個已覆蓋城市。",
    cityLevelCoverageCta: "顯示這裡的已覆蓋樹木",
    untrackedTitle: "Pink Hunter 尚未接入這個地區",
    untrackedBody: "這個地區目前尚未被 Pink Hunter 收錄。如果你知道官方公開資料來源，歡迎提供給我們。",
    untrackedCta: "請求加入這個地區",
    coveredEmptyTitle: "這個地區目前沒有符合篩選條件的樹",
    coveredEmptyBody: "這個地區已經覆蓋，但目前的篩選條件下沒有符合的樹木。你可以清空篩選，或重新顯示目前視窗內的樹木。"
  },
  "es-ES": {
    areaSearchShow: "Buscar ciudad / condado",
    areaSearchHide: "Ocultar búsqueda de ciudad / condado",
    areaSearchEmpty: "Ninguna ciudad o condado coincide con la búsqueda.",
    areaStatusCovered: "Cubierto",
    areaStatusCityLevelCoverage: "Ciudades cubiertas dentro",
    areaStatusOfficialUnavailable: "Sin datos oficiales",
    areaStatusUntracked: "Aún no añadido",
    locationLoading: "Buscando tu ubicación...",
    locationRetry: "Intentar de nuevo",
    locationUnsupportedTitle: "Este navegador no puede ubicarte",
    locationUnsupportedBody: "La geolocalización no está disponible en este navegador ahora mismo.",
    locationDeniedTitle: "Permiso de ubicación denegado",
    locationDeniedBody: "Pink Hunter no pudo acceder a tu ubicación. Activa el permiso y vuelve a intentarlo.",
    locationTimeoutTitle: "La búsqueda de ubicación tardó demasiado",
    locationTimeoutBody: "Pink Hunter no obtuvo tu posición a tiempo. Prueba otra vez en un lugar con mejor señal.",
    locationUnavailableTitle: "Ubicación no disponible",
    locationUnavailableBody: "Pink Hunter no pudo determinar tu posición actual en este momento.",
    officialUnavailableTitle: "Límite oficial confirmado, pero sin datos públicos oficiales de árboles",
    officialUnavailableBody:
      "Pink Hunter conoce esta zona y puede dibujar su límite oficial, pero todavía no existe un conjunto público oficial árbol por árbol para cargar aquí.",
    officialUnavailableCta: "Compartir una pista de datos",
    cityLevelCoverageTitle: "Ya hay ciudades cubiertas dentro de este condado",
    cityLevelCoverageBody:
      "Pink Hunter no tiene un único conjunto de datos a nivel de condado para esta zona, pero ya incluye ciudades cubiertas dentro de estos límites del condado.",
    cityLevelCoverageCta: "Mostrar árboles aquí",
    untrackedTitle: "Pink Hunter aún no ha añadido esta zona",
    untrackedBody: "Esta zona todavía no está integrada en Pink Hunter. Si conoces un conjunto oficial público, envíalo.",
    untrackedCta: "Solicitar esta zona",
    coveredEmptyTitle: "No hay árboles aquí que coincidan con los filtros actuales",
    coveredEmptyBody:
      "Esta zona sí está cubierta, pero los filtros actuales no dejaron resultados. Borra los filtros o vuelve a cargar los árboles visibles."
  },
  "ko-KR": {
    areaSearchShow: "시 / 카운티 검색",
    areaSearchHide: "시 / 카운티 검색 닫기",
    areaSearchEmpty: "검색과 일치하는 시 또는 카운티가 없습니다.",
    areaStatusCovered: "커버됨",
    areaStatusCityLevelCoverage: "안에 커버된 도시 있음",
    areaStatusOfficialUnavailable: "공식 공개 데이터 없음",
    areaStatusUntracked: "아직 미추가",
    locationLoading: "현재 위치를 찾는 중...",
    locationRetry: "다시 위치 찾기",
    locationUnsupportedTitle: "이 브라우저에서는 위치를 찾을 수 없습니다",
    locationUnsupportedBody: "현재 브라우저 세션에서는 위치 정보를 사용할 수 없습니다.",
    locationDeniedTitle: "위치 권한이 거부되었습니다",
    locationDeniedBody: "Pink Hunter가 위치에 접근하지 못했습니다. 위치 권한을 허용한 뒤 다시 시도해 주세요.",
    locationTimeoutTitle: "위치 확인 시간이 초과되었습니다",
    locationTimeoutBody: "Pink Hunter가 제시간에 위치를 받지 못했습니다. 신호가 더 좋은 곳에서 다시 시도해 주세요.",
    locationUnavailableTitle: "위치를 사용할 수 없습니다",
    locationUnavailableBody: "Pink Hunter가 현재 위치를 확인할 수 없습니다.",
    officialUnavailableTitle: "공식 경계는 확인됐지만 공개된 공식 수목 데이터가 없습니다",
    officialUnavailableBody:
      "Pink Hunter는 이 지역과 공식 경계를 알고 있지만, 현재는 불러올 수 있는 공식 공개 단일 수목 데이터셋이 없습니다.",
    officialUnavailableCta: "데이터 제보하기",
    cityLevelCoverageTitle: "이 카운티 안에는 이미 커버된 도시가 있습니다",
    cityLevelCoverageBody:
      "Pink Hunter에는 이 지역 전체를 하나로 다루는 county 단위 데이터셋은 없지만, 이 카운티 경계 안에는 이미 커버된 도시들이 포함되어 있습니다.",
    cityLevelCoverageCta: "여기 나무 보기",
    untrackedTitle: "Pink Hunter에 아직 이 지역이 추가되지 않았습니다",
    untrackedBody: "이 지역은 아직 Pink Hunter에 통합되지 않았습니다. 공식 공개 데이터셋을 알고 있다면 보내 주세요.",
    untrackedCta: "이 지역 요청하기",
    coveredEmptyTitle: "현재 필터로는 이 지역에 맞는 나무가 없습니다",
    coveredEmptyBody: "이 지역은 커버되어 있지만 현재 필터 조건에서는 결과가 없습니다. 필터를 지우거나 현재 화면의 나무를 다시 불러오세요."
  },
  "ja-JP": {
    areaSearchShow: "市 / 郡を検索",
    areaSearchHide: "市 / 郡の検索を閉じる",
    areaSearchEmpty: "一致する市または郡はありません。",
    areaStatusCovered: "カバー済み",
    areaStatusCityLevelCoverage: "中にカバー済みの市あり",
    areaStatusOfficialUnavailable: "公式データ未公開",
    areaStatusUntracked: "未追加",
    locationLoading: "現在地を取得しています...",
    locationRetry: "もう一度試す",
    locationUnsupportedTitle: "このブラウザでは現在地を取得できません",
    locationUnsupportedBody: "このブラウザでは今回のセッションで位置情報を利用できません。",
    locationDeniedTitle: "位置情報の許可が拒否されました",
    locationDeniedBody: "Pink Hunter は現在地にアクセスできませんでした。位置情報の許可を有効にして再度お試しください。",
    locationTimeoutTitle: "位置情報の取得がタイムアウトしました",
    locationTimeoutBody: "Pink Hunter は時間内に現在地を取得できませんでした。電波のよい場所で再度お試しください。",
    locationUnavailableTitle: "現在地を取得できません",
    locationUnavailableBody: "Pink Hunter は今この瞬間の位置を特定できませんでした。",
    officialUnavailableTitle: "公式境界は確認済みですが、公開された公式樹木データはまだありません",
    officialUnavailableBody:
      "Pink Hunter はこの地域と公式境界を把握していますが、ここで読み込める公式公開の単木データセットはまだありません。",
    officialUnavailableCta: "データの手がかりを送る",
    cityLevelCoverageTitle: "この郡の中にはすでにカバー済みの市があります",
    cityLevelCoverageBody:
      "Pink Hunter にはこの地域全体を 1 つの county データセットとして扱う情報はまだありませんが、この郡の範囲内にはすでにカバー済みの市が含まれています。",
    cityLevelCoverageCta: "この範囲の木を表示",
    untrackedTitle: "Pink Hunter にはまだこの地域が追加されていません",
    untrackedBody: "この地域はまだ Pink Hunter に統合されていません。公開された公式データをご存じなら共有してください。",
    untrackedCta: "この地域を依頼する",
    coveredEmptyTitle: "現在の条件に一致する木がこの地域にはありません",
    coveredEmptyBody: "この地域自体はカバー済みですが、現在のフィルター条件では一致する木がありません。フィルターを解除するか、表示中の木を再読み込みしてください。"
  },
  "fr-FR": {
    areaSearchShow: "Rechercher une ville / un comté",
    areaSearchHide: "Masquer la recherche ville / comté",
    areaSearchEmpty: "Aucune ville ou aucun comté ne correspond à cette recherche.",
    areaStatusCovered: "Couvert",
    areaStatusCityLevelCoverage: "Villes couvertes dedans",
    areaStatusOfficialUnavailable: "Pas de données officielles",
    areaStatusUntracked: "Pas encore ajouté",
    locationLoading: "Localisation en cours...",
    locationRetry: "Réessayer",
    locationUnsupportedTitle: "Ce navigateur ne peut pas vous localiser",
    locationUnsupportedBody: "La géolocalisation n'est pas disponible dans ce navigateur pour le moment.",
    locationDeniedTitle: "Autorisation de localisation refusée",
    locationDeniedBody: "Pink Hunter n'a pas pu accéder à votre position. Autorisez la localisation puis réessayez.",
    locationTimeoutTitle: "La localisation a expiré",
    locationTimeoutBody: "Pink Hunter n'a pas obtenu votre position à temps. Réessayez dans un endroit avec un meilleur signal.",
    locationUnavailableTitle: "Localisation indisponible",
    locationUnavailableBody: "Pink Hunter n'a pas pu déterminer votre position actuelle pour le moment.",
    officialUnavailableTitle: "Limite officielle confirmée, mais pas encore de données publiques officielles d'arbres",
    officialUnavailableBody:
      "Pink Hunter connaît cette zone et peut dessiner sa limite officielle, mais aucun jeu de données public officiel arbre par arbre n'est encore disponible ici.",
    officialUnavailableCta: "Partager une piste de données",
    cityLevelCoverageTitle: "Des villes couvertes existent déjà dans ce comté",
    cityLevelCoverageBody:
      "Pink Hunter ne dispose pas encore d'un jeu de données unique à l'échelle du comté pour cette zone, mais il inclut déjà des villes couvertes à l'intérieur des limites de ce comté.",
    cityLevelCoverageCta: "Afficher les arbres ici",
    untrackedTitle: "Pink Hunter n'a pas encore ajouté cette zone",
    untrackedBody: "Cette zone n'est pas encore intégrée à Pink Hunter. Si vous connaissez un jeu de données public officiel, envoyez-le.",
    untrackedCta: "Demander cette zone",
    coveredEmptyTitle: "Aucun arbre ici ne correspond aux filtres actuels",
    coveredEmptyBody:
      "Cette zone est couverte, mais les filtres actuels ne laissent aucun résultat. Effacez les filtres ou rechargez les arbres visibles."
  },
  "vi-VN": {
    areaSearchShow: "Tìm thành phố / quận hạt",
    areaSearchHide: "Ẩn tìm kiếm thành phố / quận hạt",
    areaSearchEmpty: "Không có thành phố hoặc quận hạt nào khớp.",
    areaStatusCovered: "Đã phủ",
    areaStatusCityLevelCoverage: "Bên trong có thành phố đã phủ",
    areaStatusOfficialUnavailable: "Chưa có dữ liệu chính thức",
    areaStatusUntracked: "Chưa thêm",
    locationLoading: "Đang xác định vị trí của bạn...",
    locationRetry: "Thử lại",
    locationUnsupportedTitle: "Trình duyệt này không thể định vị bạn",
    locationUnsupportedBody: "Phiên trình duyệt hiện tại không hỗ trợ định vị địa lý.",
    locationDeniedTitle: "Quyền truy cập vị trí bị từ chối",
    locationDeniedBody: "Pink Hunter không thể truy cập vị trí của bạn. Hãy cho phép truy cập vị trí rồi thử lại.",
    locationTimeoutTitle: "Định vị bị quá thời gian",
    locationTimeoutBody: "Pink Hunter không lấy được vị trí của bạn kịp lúc. Hãy thử lại ở nơi có tín hiệu tốt hơn.",
    locationUnavailableTitle: "Không thể lấy vị trí",
    locationUnavailableBody: "Pink Hunter hiện không thể xác định vị trí của bạn.",
    officialUnavailableTitle: "Đã xác nhận ranh giới chính thức nhưng chưa có dữ liệu cây công khai chính thức",
    officialUnavailableBody:
      "Pink Hunter biết khu vực này và có thể vẽ ranh giới chính thức của nó, nhưng hiện chưa có bộ dữ liệu công khai chính thức cho từng cây để tải ở đây.",
    officialUnavailableCta: "Gửi manh mối dữ liệu",
    cityLevelCoverageTitle: "Bên trong quận hạt này đã có các thành phố được phủ",
    cityLevelCoverageBody:
      "Pink Hunter hiện chưa có một bộ dữ liệu duy nhất ở cấp county cho khu vực này, nhưng bên trong ranh giới quận hạt này đã có các thành phố được phủ.",
    cityLevelCoverageCta: "Hiển thị cây ở đây",
    untrackedTitle: "Pink Hunter chưa thêm khu vực này",
    untrackedBody: "Khu vực này vẫn chưa được tích hợp vào Pink Hunter. Nếu bạn biết bộ dữ liệu công khai chính thức, hãy gửi cho chúng tôi.",
    untrackedCta: "Yêu cầu thêm khu vực này",
    coveredEmptyTitle: "Không có cây nào ở đây khớp với bộ lọc hiện tại",
    coveredEmptyBody: "Khu vực này đã được phủ, nhưng bộ lọc hiện tại không còn kết quả nào. Hãy xóa bộ lọc hoặc tải lại các cây đang hiển thị."
  }
};

const REGION_SWITCH_BOUNDS: Partial<Record<CoverageRegion, [[number, number], [number, number]]>> = {
  wa: [
    [-122.46, 47.49],
    [-122.2, 47.74]
  ]
};

const REGION_COUNTRY_EMOJIS: Record<CoverageRegion, string> = {
  wa: "🇺🇸",
  ca: "🇺🇸",
  co: "🇺🇸",
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
  co: "Colorado",
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
  co: "us",
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
const SUBNATIONAL_LABELS: Partial<Record<Language, Record<string, string>>> = {
  "zh-CN": {
    AL: "阿拉巴马州",
    AK: "阿拉斯加州",
    AZ: "亚利桑那州",
    AR: "阿肯色州",
    CA: "加利福尼亚州",
    CO: "科罗拉多州",
    CT: "康涅狄格州",
    DE: "特拉华州",
    FL: "佛罗里达州",
    GA: "佐治亚州",
    HI: "夏威夷州",
    ID: "爱达荷州",
    IL: "伊利诺伊州",
    IN: "印第安纳州",
    IA: "艾奥瓦州",
    KS: "堪萨斯州",
    KY: "肯塔基州",
    LA: "路易斯安那州",
    ME: "缅因州",
    MD: "马里兰州",
    MA: "马萨诸塞州",
    MI: "密歇根州",
    MN: "明尼苏达州",
    MS: "密西西比州",
    MO: "密苏里州",
    MT: "蒙大拿州",
    NE: "内布拉斯加州",
    NV: "内华达州",
    NH: "新罕布什尔州",
    NJ: "新泽西州",
    NM: "新墨西哥州",
    NY: "纽约州",
    NC: "北卡罗来纳州",
    ND: "北达科他州",
    OH: "俄亥俄州",
    OK: "俄克拉何马州",
    OR: "俄勒冈州",
    PA: "宾夕法尼亚州",
    RI: "罗得岛州",
    SC: "南卡罗来纳州",
    SD: "南达科他州",
    TN: "田纳西州",
    TX: "得克萨斯州",
    UT: "犹他州",
    VT: "佛蒙特州",
    VA: "弗吉尼亚州",
    WA: "华盛顿州",
    WV: "西弗吉尼亚州",
    WI: "威斯康星州",
    WY: "怀俄明州",
    DC: "哥伦比亚特区",
    AB: "艾伯塔省",
    BC: "不列颠哥伦比亚省",
    MB: "马尼托巴省",
    NB: "新不伦瑞克省",
    NL: "纽芬兰与拉布拉多省",
    NS: "新斯科舍省",
    NT: "西北地区",
    NU: "努纳武特地区",
    ON: "安大略省",
    PE: "爱德华王子岛省",
    QC: "魁北克省",
    SK: "萨斯喀彻温省",
    YT: "育空地区"
  },
  "zh-TW": {
    AL: "阿拉巴馬州",
    AK: "阿拉斯加州",
    AZ: "亞利桑那州",
    AR: "阿肯色州",
    CA: "加利福尼亞州",
    CO: "科羅拉多州",
    CT: "康乃狄克州",
    DE: "德拉瓦州",
    FL: "佛羅里達州",
    GA: "喬治亞州",
    HI: "夏威夷州",
    ID: "愛達荷州",
    IL: "伊利諾州",
    IN: "印第安納州",
    IA: "愛荷華州",
    KS: "堪薩斯州",
    KY: "肯塔基州",
    LA: "路易斯安那州",
    ME: "緬因州",
    MD: "馬里蘭州",
    MA: "麻薩諸塞州",
    MI: "密西根州",
    MN: "明尼蘇達州",
    MS: "密西西比州",
    MO: "密蘇里州",
    MT: "蒙大拿州",
    NE: "內布拉斯加州",
    NV: "內華達州",
    NH: "新罕布夏州",
    NJ: "新澤西州",
    NM: "新墨西哥州",
    NY: "紐約州",
    NC: "北卡羅來納州",
    ND: "北達科他州",
    OH: "俄亥俄州",
    OK: "奧克拉荷馬州",
    OR: "奧勒岡州",
    PA: "賓夕法尼亞州",
    RI: "羅德島州",
    SC: "南卡羅來納州",
    SD: "南達科他州",
    TN: "田納西州",
    TX: "德州",
    UT: "猶他州",
    VT: "佛蒙特州",
    VA: "維吉尼亞州",
    WA: "華盛頓州",
    WV: "西維吉尼亞州",
    WI: "威斯康辛州",
    WY: "懷俄明州",
    DC: "哥倫比亞特區",
    AB: "亞伯達省",
    BC: "卑詩省",
    MB: "曼尼托巴省",
    NB: "新不倫瑞克省",
    NL: "紐芬蘭與拉布拉多省",
    NS: "新斯科細亞省",
    NT: "西北地區",
    NU: "努納武特地區",
    ON: "安大略省",
    PE: "愛德華王子島省",
    QC: "魁北克省",
    SK: "薩斯喀徹溫省",
    YT: "育空地區"
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

type StatusNoticeKind =
  | "city_level_coverage"
  | "official_unavailable"
  | "untracked"
  | "location_unsupported"
  | "location_denied"
  | "location_timeout"
  | "location_unavailable";

interface StatusNotice {
  kind: StatusNoticeKind;
  areaName?: string;
}

type JumpAreaDisplayStatus = "covered" | "city_level_coverage" | "official_unavailable" | "untracked";

interface JumpAreaDisplayStatusInfo {
  kind: JumpAreaDisplayStatus;
  coveredCityCount: number;
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
  areaId: string | null;
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
  const areaId = params.get("area");
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
    areaId,
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

function boundsContainCoordinate(bounds: BoundsTuple, coordinate: [number, number]): boolean {
  const [[minX, minY], [maxX, maxY]] = normalizeBounds(bounds);
  return coordinate[0] >= minX && coordinate[0] <= maxX && coordinate[1] >= minY && coordinate[1] <= maxY;
}

function boundsCenter(bounds: BoundsTuple): [number, number] {
  const [[minX, minY], [maxX, maxY]] = normalizeBounds(bounds);
  return [(minX + maxX) / 2, (minY + maxY) / 2];
}

function normalizeSearchText(value: string): string {
  return value.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, " ").trim();
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
  if (
    raw === "wa" ||
    raw === "ca" ||
    raw === "co" ||
    raw === "nv" ||
    raw === "or" ||
    raw === "tx" ||
    raw === "ut" ||
    raw === "dc" ||
    raw === "bc" ||
    raw === "on" ||
    raw === "qc" ||
    raw === "va" ||
    raw === "md" ||
    raw === "nj" ||
    raw === "ny" ||
    raw === "pa" ||
    raw === "ma"
  ) {
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
  if (city.endsWith(" CO") || city.endsWith(", CO")) {
    return "co";
  }
  if (city.endsWith(" NV") || city.endsWith(", NV")) {
    return "nv";
  }
  if (city.endsWith(" TX") || city.endsWith(", TX")) {
    return "tx";
  }
  if (city.endsWith(" UT") || city.endsWith(", UT")) {
    return "ut";
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
  const directMatch = city.match(/(?:,\s*|\s+)(DC|BC|VA|MD|NJ|NY|PA|MA|ON|QC|OR|CO|CA|WA)$/i);
  if (directMatch) {
    return directMatch[1].toUpperCase();
  }
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
  if (region === "co") {
    return "CO";
  }
  if (region === "ca") {
    return "CA";
  }
  return "";
}

function jurisdictionDisplayName(city: string): string {
  return JURISDICTION_OVERRIDES[city]?.displayName ?? city;
}

function jurisdictionTypeForCity(city: string): JurisdictionType {
  return JURISDICTION_OVERRIDES[city]?.type ?? "city";
}

function jurisdictionTypeLabel(language: Language, areaType: JurisdictionType): string {
  return t(language, areaType === "county" ? "countyBadge" : "cityBadge");
}

function areaTypeLabel(language: Language, city: string, explicitType?: JurisdictionType): string {
  return jurisdictionTypeLabel(language, explicitType ?? jurisdictionTypeForCity(city));
}

function jurisdictionTypeClassName(areaType: JurisdictionType): string {
  return areaType === "county" ? "county" : "city";
}

function areaTypeClassName(city: string, explicitType?: JurisdictionType): string {
  return jurisdictionTypeClassName(explicitType ?? jurisdictionTypeForCity(city));
}

function jumpStateDisplayLabel(language: Language, state: JumpState): string {
  if (language === "zh-CN" || language === "zh-TW") {
    return SUBNATIONAL_LABELS[language]?.[state.code.toUpperCase()] ?? state.label;
  }
  return state.label;
}

function treeDirectionsHref(coordinates: [number, number]): string {
  const [lon, lat] = coordinates;
  const destination = `${lat.toFixed(6)},${lon.toFixed(6)}`;
  if (typeof navigator !== "undefined" && /iPad|iPhone|iPod|Macintosh/i.test(navigator.userAgent)) {
    return `https://maps.apple.com/?daddr=${destination}&dirflg=d`;
  }
  return `https://www.google.com/maps/dir/?api=1&destination=${destination}`;
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

function buildContactMailtoHref(kind: "official_unavailable" | "untracked", areaName: string): string {
  const subject =
    kind === "official_unavailable"
      ? `Pink Hunter data lead: ${areaName}`
      : `Pink Hunter area request: ${areaName}`;
  const lines = [
    `Area: ${areaName}`,
    `Status: ${kind}`,
    typeof window !== "undefined" ? `Page: ${window.location.href}` : "",
    "",
    kind === "official_unavailable"
      ? "I know a public source or lead for this area:"
      : "I would like Pink Hunter to add this area. Possible public source:"
  ].filter(Boolean);
  return `mailto:flalaz@uw.edu?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join("\n"))}`;
}

interface ResolvedMapStyle {
  style: string | typeof BLANK_MAP_STYLE;
  preset: MapStylePreset;
  supportsClusterText: boolean;
}

async function resolveMapStyle(): Promise<ResolvedMapStyle> {
  if (runtimeConfig.mapStack === "mapbox") {
    const probeUrl = buildMapboxStyleProbeUrl(runtimeConfig);
    if (probeUrl && runtimeConfig.mapboxPublicToken) {
      try {
        const response = await fetch(probeUrl, { method: "GET" });
        if (response.ok) {
          return {
            style: buildMapboxStyleUrl(runtimeConfig),
            preset: "mapbox",
            supportsClusterText: true
          };
        }
      } catch {
        // Fall through to blank fallback.
      }
    }

    return {
      style: BLANK_MAP_STYLE,
      preset: "blank_fallback",
      supportsClusterText: false
    };
  }

  try {
    const response = await fetch(POSITRON_STYLE_URL, { method: "GET" });
    if (response.ok) {
      return {
        style: POSITRON_STYLE_URL,
        preset: "positron",
        supportsClusterText: true
      };
    }
  } catch {
    // Fall through to default style.
  }

  return {
    style: FALLBACK_STYLE_URL,
    preset: "demotiles",
    supportsClusterText: true
  };
}

export default function App(): JSX.Element {
  const initialUrlState = useMemo(parseUrlState, []);
  const initialLayoutMode: LayoutMode =
    typeof window !== "undefined" && window.innerWidth >= 1024 ? "desktop_split" : "mobile_sheet";

  const [data, setData] = useState<StaticAppData | null>(null);
  const [mapRuntime, setMapRuntime] = useState<MapRuntimeDeps | null>(null);
  const [regionAreaIndexCache, setRegionAreaIndexCache] = useState<Partial<Record<CoverageRegion, AreaIndex>>>({});
  const [regionCoverageCache, setRegionCoverageCache] = useState<Partial<Record<CoverageRegion, CoverageCollection>>>({});
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
  const [selectedJumpAreaId, setSelectedJumpAreaId] = useState<string | null>(initialUrlState.areaId);
  const [jumpAreaQuery, setJumpAreaQuery] = useState("");
  const [jumpAreaExpanded, setJumpAreaExpanded] = useState(false);
  const [statusNotice, setStatusNotice] = useState<StatusNotice | null>(null);
  const [locatingUser, setLocatingUser] = useState(false);
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [languageMenuOpen, setLanguageMenuOpen] = useState(false);
  const [sheetHeight, setSheetHeight] = useState<number>(0.4);
  const [activePanel, setActivePanel] = useState<"details" | "filters" | "guide" | "about">("filters");
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
  const mapRef = useRef<MapEngineMap | null>(null);
  const popupRef = useRef<MapEnginePopup | null>(null);
  const filteredFeaturesRef = useRef<TreeCollection["features"]>([]);
  const isDesktopRef = useRef(layoutMode === "desktop_split");
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
        const [loadedData, runtimeDeps] = await Promise.all([loadStaticAppData(), loadMapRuntimeDeps(runtimeConfig)]);
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

  const regionMetaById = useMemo(() => {
    const entries = (data?.meta.regions ?? []).map((regionMeta) => [regionMeta.id, regionMeta]);
    return new Map(entries as Array<[CoverageRegion, RegionMeta]>);
  }, [data]);

  const activeRegionMeta = regionMetaById.get(activeRegion) ?? null;
  const activeLanguageOption = LANGUAGE_OPTIONS.find((option) => option.id === language) ?? LANGUAGE_OPTIONS[0];

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

  const pendingCoverageRegions = useMemo(() => {
    if (runtimeConfig.coverageLoadMode !== "lazy_by_region") {
      return [] as CoverageRegion[];
    }
    return visibleRegions
      .filter((region) => region.coverage_path && !regionCoverageCache[region.id])
      .map((region) => region.id);
  }, [regionCoverageCache, visibleRegions]);

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

  useEffect(() => {
    if (pendingCoverageRegions.length === 0) {
      return;
    }

    let cancelled = false;
    setError(null);

    void (async () => {
      try {
        const loaded = await Promise.all(
          pendingCoverageRegions.map(async (regionId) => {
            const regionMeta = regionMetaById.get(regionId);
            if (!regionMeta?.coverage_path) {
              throw new Error(`Missing coverage path for region ${regionId}`);
            }
            return [regionId, await loadCoverageRegion(regionMeta)] as const;
          })
        );

        if (cancelled) {
          return;
        }

        setRegionCoverageCache((current) => ({
          ...current,
          ...Object.fromEntries(loaded)
        }));
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Unknown coverage loading error");
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [pendingCoverageRegions, regionMetaById]);

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
    const collator = new Intl.Collator(language, { sensitivity: "base" });
    return [...data.jumpIndex.countries].sort((left, right) =>
      collator.compare(COUNTRY_LABELS[language][left.id], COUNTRY_LABELS[language][right.id])
    );
  }, [data, language]);

  const jumpStates = useMemo(() => {
    if (!data) {
      return [] as JumpState[];
    }
    const collator = new Intl.Collator(language, { sensitivity: "base" });
    return [...data.jumpIndex.states]
      .filter((item) => item.country_id === jumpCountry)
      .sort((left, right) =>
        collator.compare(jumpStateDisplayLabel(language, left), jumpStateDisplayLabel(language, right))
      );
  }, [data, jumpCountry, language]);

  const jumpStateById = useMemo(() => {
    if (!data) {
      return new Map<string, JumpState>();
    }
    return new Map(data.jumpIndex.states.map((state) => [state.id, state]));
  }, [data]);

  const areaStateCodeByName = useMemo(() => {
    const next = new Map<string, string>();

    data?.jumpIndex.areas.forEach((area) => {
      const state = jumpStateById.get(area.state_id);
      if (!state) {
        return;
      }
      next.set(area.jurisdiction, state.code.toUpperCase());
      next.set(area.display_name, state.code.toUpperCase());
    });

    (data?.meta.areas ?? []).forEach((area) => {
      if (!area.state_province) {
        return;
      }
      next.set(area.jurisdiction, area.state_province.toUpperCase());
      const displayName = jurisdictionDisplayName(area.jurisdiction);
      next.set(displayName, area.state_province.toUpperCase());
    });

    Object.values(regionAreaIndexCache).forEach((index) => {
      index?.items.forEach((item) => {
        next.set(item.jurisdiction, item.state_province.toUpperCase());
        next.set(item.display_name, item.state_province.toUpperCase());
      });
    });

    return next;
  }, [data, jumpStateById, regionAreaIndexCache]);

  const resolvedStateCodeForArea = useCallback(
    (city: string) => {
      const directMatch = city.match(/(?:,\s*|\s+)(DC|BC|VA|MD|NJ|NY|PA|MA|ON|QC|OR|CO|CA|WA|TX|NV|UT)$/i);
      if (directMatch) {
        return directMatch[1].toUpperCase();
      }
      const displayName = jurisdictionDisplayName(city).trim();
      return areaStateCodeByName.get(city) ?? areaStateCodeByName.get(displayName) ?? stateCodeForCity(city);
    },
    [areaStateCodeByName]
  );

  const formatAreaLabelResolved = useCallback(
    (city: string) => {
      const displayName = jurisdictionDisplayName(city).trim();
      const stateCode = resolvedStateCodeForArea(city);
      if (!stateCode) {
        return displayName;
      }
      if (new RegExp(`(?:,\\s*|\\s+)${stateCode}$`, "i").test(displayName)) {
        return displayName;
      }
      return `${displayName}, ${stateCode}`;
    },
    [resolvedStateCodeForArea]
  );

  const jumpAreaById = useMemo(() => {
    if (!data) {
      return new Map<string, JumpArea>();
    }
    return new Map(data.jumpIndex.areas.map((area) => [area.id, area]));
  }, [data]);

  const jumpAreaDisplayStatusById = useMemo(() => {
    const next = new Map<string, JumpAreaDisplayStatusInfo>();
    if (!data) {
      return next;
    }

    const cityCenters = new Map(
      data.jumpIndex.areas
        .filter((area) => area.area_type === "city")
        .map((area) => [area.id, boundsCenter(area.bounds)])
    );

    data.jumpIndex.areas.forEach((area) => {
      if (area.coverage_status === "covered") {
        next.set(area.id, { kind: "covered", coveredCityCount: 0 });
        return;
      }

      if (area.coverage_status === "official_unavailable") {
        next.set(area.id, { kind: "official_unavailable", coveredCityCount: 0 });
        return;
      }

      if (area.area_type === "county") {
        const coveredCityCount = data.jumpIndex.areas.reduce((count, candidate) => {
          if (
            candidate.id === area.id ||
            candidate.country_id !== area.country_id ||
            candidate.state_id !== area.state_id ||
            candidate.area_type !== "city" ||
            candidate.coverage_status !== "covered"
          ) {
            return count;
          }

          const candidateCenter = cityCenters.get(candidate.id) ?? boundsCenter(candidate.bounds);
          return boundsContainCoordinate(area.bounds, candidateCenter) ? count + 1 : count;
        }, 0);

        if (coveredCityCount > 0) {
          next.set(area.id, { kind: "city_level_coverage", coveredCityCount });
          return;
        }
      }

      next.set(area.id, { kind: "untracked", coveredCityCount: 0 });
    });

    return next;
  }, [data]);

  const selectedJumpArea = useMemo(
    () => (selectedJumpAreaId ? jumpAreaById.get(selectedJumpAreaId) ?? null : null),
    [jumpAreaById, selectedJumpAreaId]
  );

  const initialJumpArea = useMemo(
    () => (initialUrlState.areaId ? jumpAreaById.get(initialUrlState.areaId) ?? null : null),
    [initialUrlState.areaId, jumpAreaById]
  );

  const formatJumpAreaLabel = useCallback(
    (area: JumpArea) => {
      const displayName = jurisdictionDisplayName(area.jurisdiction).trim();
      const stateCode = jumpStateById.get(area.state_id)?.code.toUpperCase() ?? "";
      if (!stateCode) {
        return displayName;
      }
      if (new RegExp(`(?:,\\s*|\\s+)${stateCode}$`, "i").test(displayName)) {
        return displayName;
      }
      return `${displayName}, ${stateCode}`;
    },
    [jumpStateById]
  );

  const normalizedJumpAreaQuery = normalizeSearchText(jumpAreaQuery);

  const jumpAreaMatches = useMemo(() => {
    if (!data || !normalizedJumpAreaQuery) {
      return [] as JumpArea[];
    }

    const collator = new Intl.Collator(language, { sensitivity: "base" });
    const queryTokens = normalizedJumpAreaQuery.split(/\s+/).filter(Boolean);

    return data.jumpIndex.areas
      .map((area) => {
        const state = jumpStateById.get(area.state_id);
        const displayStatus = jumpAreaDisplayStatusById.get(area.id);
        const formattedLabel = formatJumpAreaLabel(area);
        const stateLabel = state ? jumpStateDisplayLabel(language, state) : "";
        const stateCode = state?.code.toUpperCase() ?? "";
        const countryLabel = COUNTRY_LABELS[language][area.country_id];
        const searchHaystack = normalizeSearchText(
          [area.display_name, area.jurisdiction, formattedLabel, stateLabel, stateCode, countryLabel].join(" ")
        );
        const normalizedDisplayName = normalizeSearchText(area.display_name);
        const normalizedJurisdiction = normalizeSearchText(area.jurisdiction);
        const normalizedLabel = normalizeSearchText(formattedLabel);

        if (!queryTokens.every((token) => searchHaystack.includes(token))) {
          return null;
        }

        const startsWithMatch =
          normalizedLabel.startsWith(normalizedJumpAreaQuery) ||
          normalizedDisplayName.startsWith(normalizedJumpAreaQuery) ||
          normalizedJurisdiction.startsWith(normalizedJumpAreaQuery);

        let score = startsWithMatch ? 20 : 0;
        if (queryTokens.includes(stateCode.toLowerCase())) {
          score += 6;
        }
        if (queryTokens.some((token) => normalizeSearchText(stateLabel).includes(token))) {
          score += 4;
        }
        if (
          normalizedDisplayName === normalizedJumpAreaQuery ||
          normalizedJurisdiction === normalizedJumpAreaQuery ||
          normalizedLabel === normalizedJumpAreaQuery
        ) {
          score += 10;
        }
        if (area.country_id === jumpCountry) {
          score += 12;
        }
        if (jumpState && area.state_id === jumpState) {
          score += 8;
        }
        if (displayStatus?.kind === "covered") {
          score += 4;
        } else if (displayStatus?.kind === "city_level_coverage") {
          score += 2;
        }

        return {
          area,
          label: formattedLabel,
          score
        };
      })
      .filter((item): item is { area: JumpArea; label: string; score: number } => item !== null)
      .sort((left, right) => right.score - left.score || collator.compare(left.label, right.label))
      .slice(0, 20)
      .map((item) => item.area);
  }, [
    data,
    formatJumpAreaLabel,
    jumpCountry,
    jumpAreaDisplayStatusById,
    jumpState,
    jumpStateById,
    language,
    normalizedJumpAreaQuery
  ]);

  useEffect(() => {
    if (!data) {
      return;
    }
    const fallbackCountry = REGION_COUNTRY_KEYS[initialUrlState.region];
    setJumpCountry((current) =>
      current && data.jumpIndex.countries.some((item) => item.id === current) ? current : fallbackCountry
    );
    setJumpState((current) => (current && data.jumpIndex.states.some((item) => item.id === current) ? current : ""));
  }, [data, initialUrlState.region]);

  useEffect(() => {
    if (!selectedJumpAreaId) {
      return;
    }
    const area = jumpAreaById.get(selectedJumpAreaId);
    if (!area) {
      setSelectedJumpAreaId(null);
      return;
    }
    setJumpCountry(area.country_id);
    setJumpState(area.state_id);
  }, [jumpAreaById, selectedJumpAreaId]);

  useEffect(() => {
    if (!jumpState) {
      return;
    }
    if (!jumpStates.some((item) => item.id === jumpState)) {
      setJumpState("");
    }
  }, [jumpState, jumpStates]);

  const rawCoverageFeatures = useMemo(() => {
    if (!data) {
      return [] as CoverageCollection["features"];
    }

    if (runtimeConfig.coverageLoadMode === "eager_all") {
      return data.coverage?.features ?? [];
    }

    return visibleRegionIds.flatMap((regionId) => regionCoverageCache[regionId]?.features ?? []);
  }, [data, regionCoverageCache, visibleRegionIds]);

  const displayCoverage = useMemo(() => {
    if (!mapRuntime) {
      return {
        type: "FeatureCollection",
        features: rawCoverageFeatures
      } as CoverageCollection;
    }
    return buildCoverageCollection(rawCoverageFeatures, mapRuntime.polygonClipping);
  }, [mapRuntime, rawCoverageFeatures]);

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
  const showMapLoadingOverlay = false;

  useEffect(() => {
    if (!selectedTree && activePanel === "details") {
      setActivePanel("filters");
    }
  }, [activePanel, selectedTree]);

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
  const discoveryCopy = DISCOVERY_COPY[language];
  const jumpSubnationalLabel = jumpCountry === "us" ? findPanelCopy.jumpState : findPanelCopy.jumpProvince;
  const jumpAnySubnationalLabel = jumpCountry === "us" ? findPanelCopy.jumpAnyState : findPanelCopy.jumpAnyProvince;

  const getJumpAreaDisplayStatus = useCallback(
    (area: JumpArea): JumpAreaDisplayStatusInfo =>
      jumpAreaDisplayStatusById.get(area.id) ?? {
        kind:
          area.coverage_status === "covered"
            ? "covered"
            : area.coverage_status === "official_unavailable"
              ? "official_unavailable"
              : "untracked",
        coveredCityCount: 0
      },
    [jumpAreaDisplayStatusById]
  );

  const jumpAreaStatusLabel = useCallback(
    (status: JumpAreaDisplayStatus): string => {
      if (status === "covered") {
        return discoveryCopy.areaStatusCovered;
      }
      if (status === "city_level_coverage") {
        return discoveryCopy.areaStatusCityLevelCoverage;
      }
      if (status === "official_unavailable") {
        return discoveryCopy.areaStatusOfficialUnavailable;
      }
      return discoveryCopy.areaStatusUntracked;
    },
    [discoveryCopy]
  );

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
        SORT_COLLATOR.compare(formatAreaLabelResolved(left.city), formatAreaLabelResolved(right.city)) ||
        SORT_COLLATOR.compare(left.name, right.name)
    );
  }, [data, formatAreaLabelResolved]);

  const normalizedAboutSourceSearchQuery = aboutSourcesSearchQuery.trim().toLowerCase();

  const filteredAboutSources = useMemo(() => {
    if (!normalizedAboutSourceSearchQuery) {
      return aboutSources;
    }

    return aboutSources.filter((source) => {
      const searchHaystack = [
        source.city,
        formatAreaLabelResolved(source.city),
        source.name,
        source.endpoint,
        sourceEndpointSearchText(source.endpoint)
      ]
        .join(" ")
        .toLowerCase();

      return searchHaystack.includes(normalizedAboutSourceSearchQuery);
    });
  }, [aboutSources, formatAreaLabelResolved, normalizedAboutSourceSearchQuery]);

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
        const label = formatAreaLabelResolved(area.jurisdiction);
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
  }, [data, formatAreaLabelResolved, language]);

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
    let mapInstance: MapEngineMap | null = null;
    setMapReady(false);

    void (async () => {
      try {
        const { style, preset, supportsClusterText } = await resolveMapStyle();
        if (isCancelled || !mapContainerRef.current) {
          return;
        }

        setMapStylePreset(preset);

        const map = new mapRuntime.map.Map({
          container: mapContainerRef.current,
          style: style as unknown,
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
          map.addControl(new mapRuntime.map.ScaleControl({ maxWidth: 110, unit: "metric" }), "bottom-right");

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

        if (supportsClusterText) {
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
        }

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

        map.addSource("user-location", {
          type: "geojson",
          data: {
            type: "FeatureCollection",
            features: []
          }
        });

        map.addLayer({
          id: "user-location-halo",
          type: "circle",
          source: "user-location",
          paint: {
            "circle-color": "rgba(63, 131, 248, 0.16)",
            "circle-radius": 14,
            "circle-stroke-color": "rgba(63, 131, 248, 0.32)",
            "circle-stroke-width": 1.5
          }
        });

        map.addLayer({
          id: "user-location-dot",
          type: "circle",
          source: "user-location",
          paint: {
            "circle-color": "#3f83f8",
            "circle-radius": 5,
            "circle-stroke-color": "#ffffff",
            "circle-stroke-width": 2
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
              setSelectedTree(null);
              setSelectedCoverage(null);
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
          setStatusNotice(null);
          if (!isDesktopRef.current) {
            setSheetHeight(0.72);
            setActivePanel("details");
          }
          if (isDesktopRef.current) {
            setActivePanel("details");
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

          setViewportBounds([
            [bounds.getWest(), bounds.getSouth()],
            [bounds.getEast(), bounds.getNorth()]
          ]);
          setMapView({
            zoom: Number(map.getZoom().toFixed(2)),
            lat: Number(center.lat.toFixed(5)),
            lon: Number(center.lng.toFixed(5))
          });
        });

        if (!initialUrlState.hasViewportParam) {
          const defaultBounds =
            initialJumpArea?.bounds ??
            preferredBoundsForRegion(initialUrlState.region, regionMetaById.get(initialUrlState.region) ?? null);
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
    initialJumpArea,
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

    const source = map.getSource("user-location") as GeoJSONSource | undefined;
    if (!source) {
      return;
    }

    source.setData(
      userLocation
        ? {
            type: "FeatureCollection",
            features: [
              {
                type: "Feature",
                geometry: {
                  type: "Point",
                  coordinates: userLocation
                },
                properties: {}
              }
            ]
          }
        : {
            type: "FeatureCollection",
            features: []
          }
    );
  }, [userLocation]);

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
      const areaDisplayName = formatAreaLabelResolved(selectedTree.properties.city);
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
          <p><strong>${escapeHtml(t(language, "city"))}:</strong> ${escapeHtml(areaDisplayName)}</p>
          ${zipCodeLine}
          <p><strong>${escapeHtml(t(language, "coordinates"))}:</strong> ${lon.toFixed(5)}, ${lat.toFixed(5)}</p>
        </div>
      `;

      const popup = new runtime.map.Popup({
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
        setSelectedTree((current) => {
          const next = current && current.properties.id === selectedTree.properties.id ? null : current;
          if (!next) {
            setActivePanel("filters");
          }
          return next;
        });
      });

      popupRef.current = popup;
      return;
    }

    if (!selectedCoverage) {
      return;
    }

    const coverageAreaDisplayName = formatAreaLabelResolved(selectedCoverage.properties.jurisdiction);
    const coverageAreaBadge = `<span class="coverage-area-type-badge ${areaTypeClassName(
      selectedCoverage.properties.jurisdiction
    )}">${escapeHtml(areaTypeLabel(language, selectedCoverage.properties.jurisdiction))}</span>`;
    const popupHtml = `
      <div class="coverage-popup-card">
        <h4>${escapeHtml(coverageAreaDisplayName)}</h4>
        <div class="coverage-popup-meta">${coverageAreaBadge}</div>
        <p class="coverage-popup-eyebrow">${escapeHtml(t(language, "officialUnavailablePopupTitle"))}</p>
        <p>${escapeHtml(t(language, "officialUnavailablePopupBody"))}</p>
        <p>${escapeHtml(t(language, "officialUnavailablePopupFoot"))}</p>
        <p>${escapeHtml(t(language, "officialUnavailablePopupContact"))}</p>
      </div>
    `;

    const popup = new runtime.map.Popup({
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

    popupRef.current = popup;
  }, [language, mapRuntime, selectedCoverage, selectedTree]);

  useEffect(() => {
    if (!data) {
      return;
    }

    const params = new URLSearchParams();
    params.set("region", activeRegion);
    params.set("lang", language);
    if (selectedJumpAreaId) {
      params.set("area", selectedJumpAreaId);
    }

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
    selectedJumpAreaId,
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

  function clearSelectedJumpArea(): void {
    setSelectedJumpAreaId(null);
    setJumpAreaQuery("");
    setStatusNotice(null);
  }

  function handleSelectJumpArea(area: JumpArea): void {
    setJumpCountry(area.country_id);
    setJumpState(area.state_id);
    setSelectedJumpAreaId(area.id);
    setJumpAreaExpanded(false);
    setJumpAreaQuery("");
    setStatusNotice(null);
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

  function handleJump(): void {
    if (!data) {
      return;
    }

    const selectedArea = selectedJumpArea;
    const selectedJumpState = jumpState ? jumpStates.find((item) => item.id === jumpState) ?? null : null;
    const selectedJumpCountry = jumpCountries.find((item) => item.id === jumpCountry) ?? null;
    const targetBounds = selectedArea?.bounds ?? selectedJumpState?.bounds ?? selectedJumpCountry?.bounds ?? null;

    setSelectedTree(null);
    setSelectedCoverage(null);
    setStatusNotice(null);
    setUserLocation(null);
    setJumpAreaExpanded(false);

    if (selectedArea?.region_hint) {
      setActiveRegion(selectedArea.region_hint);
    } else if (selectedJumpState?.region_hint) {
      setActiveRegion(selectedJumpState.region_hint);
    }

    fitMapToBounds(targetBounds);

    if (selectedArea) {
      const areaName = formatJumpAreaLabel(selectedArea);
      const displayStatus = getJumpAreaDisplayStatus(selectedArea);
      if (displayStatus.kind === "official_unavailable") {
        setStatusNotice({
          kind: "official_unavailable",
          areaName
        });
      } else if (displayStatus.kind === "city_level_coverage") {
        setStatusNotice({
          kind: "city_level_coverage",
          areaName
        });
      } else if (displayStatus.kind === "untracked") {
        setStatusNotice({
          kind: "untracked",
          areaName
        });
      }
    } else if (selectedJumpState && !selectedJumpState.region_hint) {
      setStatusNotice({
        kind: "untracked",
        areaName: jumpStateDisplayLabel(language, selectedJumpState)
      });
    }

    if (!isDesktop) {
      setActivePanel("filters");
    }
  }

  function handleLocateNearby(): void {
    if (typeof navigator === "undefined" || !navigator.geolocation) {
      setStatusNotice({ kind: "location_unsupported" });
      return;
    }

    if (!data) {
      return;
    }

    setLocatingUser(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coordinates: [number, number] = [position.coords.longitude, position.coords.latitude];
        const matchedArea =
          [...data.jumpIndex.areas]
            .filter((area) => boundsContainCoordinate(area.bounds, coordinates))
            .sort(
              (left, right) =>
                (left.bounds[1][0] - left.bounds[0][0]) * (left.bounds[1][1] - left.bounds[0][1]) -
                (right.bounds[1][0] - right.bounds[0][0]) * (right.bounds[1][1] - right.bounds[0][1])
            )[0] ?? null;
        const matchedRegion =
          data.meta.regions.find((region) => boundsContainCoordinate(region.bounds, coordinates)) ?? null;

        setLocatingUser(false);
        setSelectedTree(null);
        setSelectedCoverage(null);
        setSelectedJumpAreaId(null);
        setJumpAreaQuery("");
        setJumpAreaExpanded(false);
        setUserLocation(coordinates);
        setStatusNotice(null);
        if (matchedArea) {
          setJumpCountry(matchedArea.country_id);
          setJumpState(matchedArea.state_id);
        }
        if (matchedArea?.region_hint) {
          setActiveRegion(matchedArea.region_hint);
        } else if (matchedRegion?.id) {
          setActiveRegion(matchedRegion.id);
        }

        if (matchedArea && getJumpAreaDisplayStatus(matchedArea).kind === "official_unavailable") {
          setStatusNotice({
            kind: "official_unavailable",
            areaName: formatJumpAreaLabel(matchedArea)
          });
        } else if (matchedArea && getJumpAreaDisplayStatus(matchedArea).kind === "city_level_coverage") {
          setStatusNotice({
            kind: "city_level_coverage",
            areaName: formatJumpAreaLabel(matchedArea)
          });
        } else if (matchedArea && getJumpAreaDisplayStatus(matchedArea).kind === "untracked") {
          setStatusNotice({
            kind: "untracked",
            areaName: formatJumpAreaLabel(matchedArea)
          });
        }

        const map = mapRef.current;
        if (map && mapReady) {
          map.easeTo({
            center: coordinates,
            zoom: Math.max(13, map.getZoom()),
            duration: 700
          });
        }

        if (!isDesktopRef.current) {
          setActivePanel("filters");
        }
      },
      (positionError) => {
        setLocatingUser(false);
        if (positionError.code === 1) {
          setStatusNotice({ kind: "location_denied" });
          return;
        }
        if (positionError.code === 3) {
          setStatusNotice({ kind: "location_timeout" });
          return;
        }
        setStatusNotice({ kind: "location_unavailable" });
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      }
    );
  }

  function refreshViewportTrees(): void {
    setSelectedSpecies([...ALL_SPECIES]);
    setSelectedOwnership([...allOwnershipOptions]);
    setSelectedTree(null);
    setSelectedCoverage(null);
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
  }

  function selectAllFilters(): void {
    setSelectedSpecies([...ALL_SPECIES]);
    setSelectedOwnership([...allOwnershipOptions]);
    setSelectedTree(null);
    setSelectedCoverage(null);
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

  const selectedJumpAreaLabel = selectedJumpArea ? formatJumpAreaLabel(selectedJumpArea) : null;
  const locateButtonStyle = isDesktop
    ? { right: "446px", bottom: "4.9rem" }
    : { right: "0.88rem", bottom: `calc(${sheetHeight * 100}vh + 1rem)` };

  function renderStatusCard(): JSX.Element | null {
    if (locatingUser) {
      return (
        <article className="status-card location_loading">
          <div className="status-card-loading-row">
            <span className="status-card-loading-dot" />
            <strong>{discoveryCopy.locationLoading}</strong>
          </div>
        </article>
      );
    }

    if (statusNotice) {
      let title = "";
      let body = "";
      let action: ReactNode = null;

      if (statusNotice.kind === "official_unavailable") {
        title = discoveryCopy.officialUnavailableTitle;
        body = discoveryCopy.officialUnavailableBody;
        action = (
          <a
            className="detail-route-btn status-card-primary-link"
            href={buildContactMailtoHref("official_unavailable", statusNotice.areaName ?? "Unknown area")}
          >
            {discoveryCopy.officialUnavailableCta}
          </a>
        );
      } else if (statusNotice.kind === "city_level_coverage") {
        title = discoveryCopy.cityLevelCoverageTitle;
        body = discoveryCopy.cityLevelCoverageBody;
        action = (
          <button className="clear-btn" onClick={refreshViewportTrees} type="button">
            {discoveryCopy.cityLevelCoverageCta}
          </button>
        );
      } else if (statusNotice.kind === "untracked") {
        title = discoveryCopy.untrackedTitle;
        body = discoveryCopy.untrackedBody;
        action = (
          <a
            className="detail-route-btn status-card-primary-link"
            href={buildContactMailtoHref("untracked", statusNotice.areaName ?? "Unknown area")}
          >
            {discoveryCopy.untrackedCta}
          </a>
        );
      } else if (statusNotice.kind === "location_unsupported") {
        title = discoveryCopy.locationUnsupportedTitle;
        body = discoveryCopy.locationUnsupportedBody;
      } else if (statusNotice.kind === "location_denied") {
        title = discoveryCopy.locationDeniedTitle;
        body = discoveryCopy.locationDeniedBody;
        action = (
          <button className="clear-btn" onClick={handleLocateNearby} type="button">
            {discoveryCopy.locationRetry}
          </button>
        );
      } else if (statusNotice.kind === "location_timeout") {
        title = discoveryCopy.locationTimeoutTitle;
        body = discoveryCopy.locationTimeoutBody;
        action = (
          <button className="clear-btn" onClick={handleLocateNearby} type="button">
            {discoveryCopy.locationRetry}
          </button>
        );
      } else if (statusNotice.kind === "location_unavailable") {
        title = discoveryCopy.locationUnavailableTitle;
        body = discoveryCopy.locationUnavailableBody;
        action = (
          <button className="clear-btn" onClick={handleLocateNearby} type="button">
            {discoveryCopy.locationRetry}
          </button>
        );
      }

      return (
        <article className={`status-card ${statusNotice.kind}`}>
          {statusNotice.areaName && <p className="status-card-area">{statusNotice.areaName}</p>}
          <h4>{title}</h4>
          <p>{body}</p>
          {action && <div className="status-card-actions">{action}</div>}
        </article>
      );
    }

    if (!activeRegionPending && filteredFeatures.length === 0) {
      const filtersCleared = selectedSpecies.length === 0 || selectedOwnership.length === 0;
      return (
        <article className="status-card covered_empty">
          {selectedJumpAreaLabel && <p className="status-card-area">{selectedJumpAreaLabel}</p>}
          <h4>{discoveryCopy.coveredEmptyTitle}</h4>
          <p>{discoveryCopy.coveredEmptyBody}</p>
          <div className="status-card-actions">
            <button className="clear-btn" onClick={filtersCleared ? selectAllFilters : clearAllFilters} type="button">
              {filtersCleared ? t(language, "selectAll") : t(language, "clearFilters")}
            </button>
            <button className="clear-btn" onClick={refreshViewportTrees} type="button">
              {findPanelCopy.showButton}
            </button>
          </div>
        </article>
      );
    }

    return null;
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
        <img alt="Pink Hunter" className="loading-brand-logo" src={BRAND_LOGO_PATH} />
        <div className="loading-progress-track" aria-hidden="true">
          <div className="loading-progress-fill" />
          <img alt="" className="loading-progress-flower" src={BRAND_MARK_PATH} />
        </div>
        <p className="loading-copy">{t(language, "loading")}</p>
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
        {(mapStylePreset === "demotiles" || mapStylePreset === "blank_fallback") && (
          <p>{t(language, "fallbackBasemap")}</p>
        )}
      </section>
      <button
        aria-label={t(language, "locateNearby")}
        className={locatingUser ? "map-locate-btn locating" : "map-locate-btn"}
        disabled={locatingUser}
        onClick={handleLocateNearby}
        style={locateButtonStyle}
        title={t(language, "locateNearby")}
        type="button"
      >
        <svg aria-hidden="true" viewBox="0 0 24 24">
          <path
            d="M12 3.5v3.2M12 17.3v3.2M20.5 12h-3.2M6.7 12H3.5"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.8"
          />
          <circle
            cx="12"
            cy="12"
            fill="none"
            r="5.25"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.8"
          />
          <circle cx="12" cy="12" fill="currentColor" r="1.6" />
        </svg>
      </button>

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
            {selectedTree && (
              <button
                className={activePanel === "details" ? "tab-btn active" : "tab-btn"}
                onClick={() => setActivePanel("details")}
                type="button"
              >
                {t(language, "showDetails")}
              </button>
            )}
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

          {activePanel === "details" && selectedTree ? (
            <article className="tree-card selected details-card">
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
                {formatAreaLabelResolved(selectedTree.properties.city)}
              </p>
              {hasKnownZipCode(selectedTree.properties.zip_code) && (
                <p>
                  <strong>{t(language, "zipCode")}: </strong>
                  {selectedTree.properties.zip_code}
                </p>
              )}
              <p>
                <strong>{t(language, "ownership")}: </strong>
                {ownershipLabel(language, selectedTree.properties.ownership)} ({selectedTree.properties.ownership_raw})
              </p>
              <p>
                <strong>{t(language, "coordinates")}: </strong>
                {selectedTree.coordinates[0].toFixed(5)}, {selectedTree.coordinates[1].toFixed(5)}
              </p>
              <p>
                <strong>{t(language, "source")}: </strong>
                {selectedTree.properties.source_department}
              </p>
              <a
                className="detail-route-btn"
                href={treeDirectionsHref(selectedTree.coordinates)}
                rel="noreferrer"
                target="_blank"
              >
                {t(language, "navigateToTree")}
              </a>
            </article>
          ) : activePanel === "filters" ? (
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
                          clearSelectedJumpArea();
                          setJumpAreaExpanded(false);
                          setStatusNotice(null);
                          setUserLocation(null);
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
                      <select
                        className="jump-select"
                        onChange={(event) => {
                          const nextState = event.target.value;
                          setJumpState(nextState);
                          clearSelectedJumpArea();
                          setStatusNotice(null);
                          setUserLocation(null);
                        }}
                        value={jumpState}
                      >
                        <option value="">{jumpAnySubnationalLabel}</option>
                        {jumpStates.map((state) => (
                          <option key={state.id} value={state.id}>
                            {jumpStateDisplayLabel(language, state)}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                  <div className="jump-area-tools">
                    <button
                      className="jump-area-toggle"
                      onClick={() => setJumpAreaExpanded((current) => !current)}
                      type="button"
                    >
                      {jumpAreaExpanded ? discoveryCopy.areaSearchHide : discoveryCopy.areaSearchShow}
                    </button>
                    {selectedJumpAreaLabel && (
                      <div className="jump-selected-area">
                        <span>{selectedJumpAreaLabel}</span>
                        <button
                          aria-label={t(language, "clearAll")}
                          className="jump-selected-area-clear"
                          onClick={clearSelectedJumpArea}
                          type="button"
                        >
                          ×
                        </button>
                      </div>
                    )}
                  </div>
                  {jumpAreaExpanded && (
                    <div className="jump-area-search-shell">
                      <input
                        className="filter-search-input jump-area-search-input"
                        onChange={(event) => setJumpAreaQuery(event.target.value)}
                        placeholder={t(language, "searchCityPlaceholder")}
                        type="search"
                        value={jumpAreaQuery}
                      />
                      {normalizedJumpAreaQuery ? (
                        jumpAreaMatches.length > 0 ? (
                          <div className="jump-area-results">
                            {jumpAreaMatches.map((area) => {
                              const areaDisplayStatus = getJumpAreaDisplayStatus(area);
                              return (
                                <button
                                  className={
                                    area.id === selectedJumpAreaId
                                      ? "jump-area-result active"
                                      : "jump-area-result"
                                  }
                                  key={area.id}
                                  onClick={() => handleSelectJumpArea(area)}
                                  type="button"
                                >
                                  <div className="jump-area-result-head">
                                    <strong>{formatJumpAreaLabel(area)}</strong>
                                  </div>
                                  <div className="jump-area-result-meta">
                                    <span
                                      className={`coverage-area-type-badge ${jurisdictionTypeClassName(
                                        area.area_type
                                      )}`}
                                    >
                                      {jurisdictionTypeLabel(language, area.area_type)}
                                    </span>
                                    <span className={`jump-area-status-badge ${areaDisplayStatus.kind}`}>
                                      {jumpAreaStatusLabel(areaDisplayStatus.kind)}
                                    </span>
                                  </div>
                                </button>
                              );
                            })}
                          </div>
                        ) : (
                          <p className="filter-empty jump-area-empty">{discoveryCopy.areaSearchEmpty}</p>
                        )
                      ) : null}
                    </div>
                  )}
                  <div className="jump-actions">
                    <button className="clear-btn jump-btn" onClick={handleJump} type="button">
                      {findPanelCopy.jumpButton}
                    </button>
                  </div>
                </section>
                {renderStatusCard()}

                <section className="show-block">
                  <div className="filters-heading">
                    <h3>{t(language, "filtersSectionTitle")}</h3>
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
              {activeRegionPending ? null : filteredFeatures.length > 0 ? (
                <p className="selection-hint">{t(language, "tapTreeHint")}</p>
              ) : null}
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
                                    <span
                                      className={`coverage-area-type-badge ${jurisdictionTypeClassName(area.areaType)}`}
                                    >
                                      {jurisdictionTypeLabel(language, area.areaType)}
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
                                {formatAreaLabelResolved(source.city)}: {source.name}
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
