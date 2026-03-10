import type {
  BloomForecast,
  FeaturedAreaSourceKind,
  Language,
  TreeCoordSource,
  WeatherDaySummary,
  WeatherSnapshot
} from "./types";

type FeaturedAreaCopy = {
  sectionTitle: string;
  sectionBody: string;
  cardButton: string;
  chartTitle: string;
  startLabel: string;
  peakLabel: string;
  endLabel: string;
  weatherTitle: string;
  weatherLoading: string;
  weatherUnavailable: string;
  weatherStable: string;
  weatherShiftEarlier: string;
  weatherShiftLater: string;
  forecastModeMl: string;
  forecastModeFallback: string;
  sourcesTitle: string;
  confidenceTitle: string;
  treesTitle: string;
  treesLoading: string;
  treesEmpty: string;
  selectTree: string;
  openForecast: string;
  detailSourceLabel: string;
  coordSourceLabel: string;
  cultivarLabel: string;
  locationLabel: string;
  dbhLabel: string;
  weatherAdjusted: string;
  updatedAt: string;
};

const FEATURED_AREA_COPY: Record<Language, FeaturedAreaCopy> = {
  "en-US": {
    sectionTitle: "Featured Areas",
    sectionBody: "Pink Hunter can spotlight a few high-interest bloom areas with richer detail. UW is the first pilot.",
    cardButton: "Open bloom forecast",
    chartTitle: "Bloom intensity forecast",
    startLabel: "Start",
    peakLabel: "Peak",
    endLabel: "End",
    weatherTitle: "Live weather",
    weatherLoading: "Loading live weather...",
    weatherUnavailable: "Live weather is unavailable right now. The static bloom curve is still shown.",
    weatherStable: "Live weather keeps the curve unchanged today.",
    weatherShiftEarlier: "Live weather shifts the curve earlier.",
    weatherShiftLater: "Live weather shifts the curve later.",
    forecastModeMl: "ML forecast",
    forecastModeFallback: "Historical fallback",
    sourcesTitle: "Sources",
    confidenceTitle: "Confidence notes",
    treesTitle: "Trees in this area",
    treesLoading: "Loading area trees...",
    treesEmpty: "Area trees are not loaded yet.",
    selectTree: "Open tree details",
    openForecast: "Open area bloom forecast",
    detailSourceLabel: "Detail source",
    coordSourceLabel: "Coordinate source",
    cultivarLabel: "Cultivar",
    locationLabel: "Location note",
    dbhLabel: "DBH",
    weatherAdjusted: "Weather shift",
    updatedAt: "Updated"
  },
  "zh-CN": {
    sectionTitle: "热门区域",
    sectionBody: "Pink Hunter 会优先展示少数公众最关心、信息更完整的赏花区域。UW 是第一期试点。",
    cardButton: "打开开花预测",
    chartTitle: "开花强度预测",
    startLabel: "开始",
    peakLabel: "顶峰",
    endLabel: "结束",
    weatherTitle: "实时天气",
    weatherLoading: "正在加载实时天气...",
    weatherUnavailable: "实时天气暂时不可用，静态开花曲线仍然可看。",
    weatherStable: "实时天气今天没有改变这条曲线。",
    weatherShiftEarlier: "实时天气让曲线整体提前。",
    weatherShiftLater: "实时天气让曲线整体推后。",
    forecastModeMl: "机器学习预测",
    forecastModeFallback: "历史回退",
    sourcesTitle: "数据来源",
    confidenceTitle: "可信度说明",
    treesTitle: "区域内树木",
    treesLoading: "正在加载区域树木...",
    treesEmpty: "区域树木还没有加载完成。",
    selectTree: "打开树木详情",
    openForecast: "打开区域开花预测",
    detailSourceLabel: "详情来源",
    coordSourceLabel: "坐标来源",
    cultivarLabel: "品种",
    locationLabel: "位置说明",
    dbhLabel: "胸径",
    weatherAdjusted: "天气修正",
    updatedAt: "更新于"
  },
  "zh-TW": {
    sectionTitle: "熱門區域",
    sectionBody: "Pink Hunter 會優先展示少數最受關注、資訊更完整的賞花區域。UW 是第一期試點。",
    cardButton: "打開開花預測",
    chartTitle: "開花強度預測",
    startLabel: "開始",
    peakLabel: "高峰",
    endLabel: "結束",
    weatherTitle: "即時天氣",
    weatherLoading: "正在載入即時天氣...",
    weatherUnavailable: "即時天氣暫時不可用，靜態開花曲線仍可查看。",
    weatherStable: "即時天氣今天沒有改變這條曲線。",
    weatherShiftEarlier: "即時天氣讓曲線整體提前。",
    weatherShiftLater: "即時天氣讓曲線整體延後。",
    forecastModeMl: "機器學習預測",
    forecastModeFallback: "歷史回退",
    sourcesTitle: "資料來源",
    confidenceTitle: "可信度說明",
    treesTitle: "區域內樹木",
    treesLoading: "正在載入區域樹木...",
    treesEmpty: "區域樹木尚未載入完成。",
    selectTree: "打開樹木詳情",
    openForecast: "打開區域開花預測",
    detailSourceLabel: "詳情來源",
    coordSourceLabel: "座標來源",
    cultivarLabel: "品種",
    locationLabel: "位置說明",
    dbhLabel: "胸徑",
    weatherAdjusted: "天氣修正",
    updatedAt: "更新於"
  },
  "es-ES": {
    sectionTitle: "Zonas destacadas",
    sectionBody: "Pink Hunter puede destacar unas pocas zonas de floración de alto interés con más detalle. UW es el primer piloto.",
    cardButton: "Abrir pronóstico",
    chartTitle: "Pronóstico de intensidad de floración",
    startLabel: "Inicio",
    peakLabel: "Pico",
    endLabel: "Fin",
    weatherTitle: "Tiempo en vivo",
    weatherLoading: "Cargando tiempo en vivo...",
    weatherUnavailable: "El tiempo en vivo no está disponible ahora. La curva estática sigue visible.",
    weatherStable: "El tiempo en vivo no cambia la curva hoy.",
    weatherShiftEarlier: "El tiempo en vivo adelanta la curva.",
    weatherShiftLater: "El tiempo en vivo retrasa la curva.",
    forecastModeMl: "Pronóstico ML",
    forecastModeFallback: "Histórico de respaldo",
    sourcesTitle: "Fuentes",
    confidenceTitle: "Notas de confianza",
    treesTitle: "Árboles de esta zona",
    treesLoading: "Cargando árboles de la zona...",
    treesEmpty: "Los árboles de la zona todavía no se cargan.",
    selectTree: "Abrir detalles del árbol",
    openForecast: "Abrir pronóstico del área",
    detailSourceLabel: "Fuente de detalle",
    coordSourceLabel: "Fuente de coordenadas",
    cultivarLabel: "Cultivar",
    locationLabel: "Nota de ubicación",
    dbhLabel: "DAP",
    weatherAdjusted: "Ajuste por clima",
    updatedAt: "Actualizado"
  },
  "ko-KR": {
    sectionTitle: "주목 지역",
    sectionBody: "Pink Hunter는 관심이 높은 몇몇 꽃 구역을 더 자세히 보여줄 수 있습니다. UW가 첫 시범 지역입니다.",
    cardButton: "개화 예측 열기",
    chartTitle: "개화 강도 예측",
    startLabel: "시작",
    peakLabel: "절정",
    endLabel: "종료",
    weatherTitle: "실시간 날씨",
    weatherLoading: "실시간 날씨 불러오는 중...",
    weatherUnavailable: "실시간 날씨를 지금 불러올 수 없습니다. 정적 개화 곡선은 계속 표시됩니다.",
    weatherStable: "실시간 날씨가 오늘 곡선을 바꾸지 않았습니다.",
    weatherShiftEarlier: "실시간 날씨로 곡선이 더 앞당겨졌습니다.",
    weatherShiftLater: "실시간 날씨로 곡선이 더 늦춰졌습니다.",
    forecastModeMl: "ML 예측",
    forecastModeFallback: "과거값 대체",
    sourcesTitle: "출처",
    confidenceTitle: "신뢰도 메모",
    treesTitle: "이 지역의 나무",
    treesLoading: "지역 나무를 불러오는 중...",
    treesEmpty: "지역 나무가 아직 로드되지 않았습니다.",
    selectTree: "나무 상세 열기",
    openForecast: "지역 개화 예측 열기",
    detailSourceLabel: "상세 출처",
    coordSourceLabel: "좌표 출처",
    cultivarLabel: "품종",
    locationLabel: "위치 메모",
    dbhLabel: "흉고직경",
    weatherAdjusted: "날씨 보정",
    updatedAt: "업데이트"
  },
  "ja-JP": {
    sectionTitle: "注目エリア",
    sectionBody: "Pink Hunter は関心の高い花見エリアを、より詳しい情報つきで表示できます。UW が最初の試験導入です。",
    cardButton: "開花予測を開く",
    chartTitle: "開花強度の予測",
    startLabel: "咲き始め",
    peakLabel: "ピーク",
    endLabel: "見頃終了",
    weatherTitle: "最新の天気",
    weatherLoading: "最新の天気を読み込み中...",
    weatherUnavailable: "最新の天気は今利用できません。静的な開花曲線は表示されます。",
    weatherStable: "最新の天気による曲線の移動は今日はありません。",
    weatherShiftEarlier: "最新の天気で曲線が前倒しになっています。",
    weatherShiftLater: "最新の天気で曲線が後ろ倒しになっています。",
    forecastModeMl: "機械学習予測",
    forecastModeFallback: "履歴フォールバック",
    sourcesTitle: "データソース",
    confidenceTitle: "信頼性メモ",
    treesTitle: "このエリアの木",
    treesLoading: "エリア内の木を読み込み中...",
    treesEmpty: "エリア内の木はまだ読み込まれていません。",
    selectTree: "木の詳細を開く",
    openForecast: "エリアの開花予測を開く",
    detailSourceLabel: "詳細ソース",
    coordSourceLabel: "座標ソース",
    cultivarLabel: "品種",
    locationLabel: "位置メモ",
    dbhLabel: "胸高直径",
    weatherAdjusted: "天気補正",
    updatedAt: "更新"
  },
  "fr-FR": {
    sectionTitle: "Zones en vedette",
    sectionBody: "Pink Hunter peut mettre en avant quelques zones de floraison très demandées avec plus de détail. UW est le premier pilote.",
    cardButton: "Ouvrir la prévision",
    chartTitle: "Prévision d'intensité de floraison",
    startLabel: "Début",
    peakLabel: "Pic",
    endLabel: "Fin",
    weatherTitle: "Météo en direct",
    weatherLoading: "Chargement de la météo en direct...",
    weatherUnavailable: "La météo en direct est indisponible pour le moment. La courbe statique reste visible.",
    weatherStable: "La météo en direct ne décale pas la courbe aujourd'hui.",
    weatherShiftEarlier: "La météo en direct avance la courbe.",
    weatherShiftLater: "La météo en direct retarde la courbe.",
    forecastModeMl: "Prévision ML",
    forecastModeFallback: "Repli historique",
    sourcesTitle: "Sources",
    confidenceTitle: "Notes de confiance",
    treesTitle: "Arbres de cette zone",
    treesLoading: "Chargement des arbres de la zone...",
    treesEmpty: "Les arbres de la zone ne sont pas encore chargés.",
    selectTree: "Ouvrir les détails de l'arbre",
    openForecast: "Ouvrir la prévision de la zone",
    detailSourceLabel: "Source du détail",
    coordSourceLabel: "Source des coordonnées",
    cultivarLabel: "Cultivar",
    locationLabel: "Note de lieu",
    dbhLabel: "DHP",
    weatherAdjusted: "Ajustement météo",
    updatedAt: "Mis à jour"
  },
  "vi-VN": {
    sectionTitle: "Khu vực nổi bật",
    sectionBody: "Pink Hunter có thể làm nổi bật một vài khu vực ngắm hoa được quan tâm nhiều với thông tin chi tiết hơn. UW là điểm thử nghiệm đầu tiên.",
    cardButton: "Mở dự báo nở hoa",
    chartTitle: "Dự báo cường độ nở hoa",
    startLabel: "Bắt đầu",
    peakLabel: "Đỉnh",
    endLabel: "Kết thúc",
    weatherTitle: "Thời tiết trực tiếp",
    weatherLoading: "Đang tải thời tiết trực tiếp...",
    weatherUnavailable: "Thời tiết trực tiếp hiện không khả dụng. Đường cong tĩnh vẫn được hiển thị.",
    weatherStable: "Thời tiết trực tiếp hôm nay không làm thay đổi đường cong.",
    weatherShiftEarlier: "Thời tiết trực tiếp đẩy đường cong sớm hơn.",
    weatherShiftLater: "Thời tiết trực tiếp đẩy đường cong muộn hơn.",
    forecastModeMl: "Dự báo ML",
    forecastModeFallback: "Dự phòng lịch sử",
    sourcesTitle: "Nguồn",
    confidenceTitle: "Ghi chú độ tin cậy",
    treesTitle: "Cây trong khu vực này",
    treesLoading: "Đang tải cây trong khu vực...",
    treesEmpty: "Cây trong khu vực chưa được tải xong.",
    selectTree: "Mở chi tiết cây",
    openForecast: "Mở dự báo khu vực",
    detailSourceLabel: "Nguồn chi tiết",
    coordSourceLabel: "Nguồn tọa độ",
    cultivarLabel: "Giống",
    locationLabel: "Ghi chú vị trí",
    dbhLabel: "Đường kính thân",
    weatherAdjusted: "Điều chỉnh thời tiết",
    updatedAt: "Cập nhật"
  }
};

const FEATURED_AREA_METADATA: Record<
  string,
  Record<Language, { label: string; eyebrow: string; description: string }>
> = {
  "uw-seattle-quad": {
    "en-US": {
      label: "UW Seattle Quad",
      eyebrow: "University of Washington",
      description: "Campus-scale cherry forecast for the Liberal Arts Quadrangle with richer tree details and live weather."
    },
    "zh-CN": {
      label: "UW 樱花热门区域",
      eyebrow: "华盛顿大学",
      description: "聚焦 Liberal Arts Quadrangle 的校园级樱花预测，并配套更详细的树木信息与实时天气。"
    },
    "zh-TW": {
      label: "UW 櫻花熱門區域",
      eyebrow: "華盛頓大學",
      description: "聚焦 Liberal Arts Quadrangle 的校園級櫻花預測，並提供更詳細的樹木資訊與即時天氣。"
    },
    "es-ES": {
      label: "Cuadrángulo UW Seattle",
      eyebrow: "Universidad de Washington",
      description: "Pronóstico de cerezos a escala de campus para el Liberal Arts Quadrangle con más detalle arbóreo y tiempo en vivo."
    },
    "ko-KR": {
      label: "UW 시애틀 쿼드",
      eyebrow: "워싱턴대학교",
      description: "Liberal Arts Quadrangle의 캠퍼스 단위 벚꽃 예측과 더 자세한 나무 정보, 실시간 날씨를 제공합니다."
    },
    "ja-JP": {
      label: "UW シアトル・クアッド",
      eyebrow: "ワシントン大学",
      description: "Liberal Arts Quadrangle を対象にしたキャンパス規模の桜予測と、詳しい樹木情報、最新の天気をまとめて表示します。"
    },
    "fr-FR": {
      label: "Quad de l'UW Seattle",
      eyebrow: "Université de Washington",
      description: "Prévision des cerisiers à l'échelle du campus pour le Liberal Arts Quadrangle avec plus de détail et la météo en direct."
    },
    "vi-VN": {
      label: "Quad UW Seattle",
      eyebrow: "Đại học Washington",
      description: "Dự báo hoa anh đào cấp khuôn viên cho Liberal Arts Quadrangle cùng thông tin cây chi tiết hơn và thời tiết trực tiếp."
    }
  }
};

const FEATURED_AREA_CONFIDENCE_NOTES: Record<string, Record<Language, string>> = {
  official_peak_dates: {
    "en-US": "Peak bloom dates come from official UW bloom history records.",
    "zh-CN": "盛开峰值日期来自 UW 官方 bloom 历史记录。",
    "zh-TW": "盛開高峰日期來自 UW 官方 bloom 歷史紀錄。",
    "es-ES": "Las fechas de pico provienen de los registros oficiales de UW.",
    "ko-KR": "절정 개화일은 UW 공식 기록을 사용합니다.",
    "ja-JP": "ピーク日は UW の公式 bloom 記録を使用しています。",
    "fr-FR": "Les dates de pic viennent des relevés officiels de l'UW.",
    "vi-VN": "Ngày nở rộ lấy từ hồ sơ bloom chính thức của UW."
  },
  osm_verified_locations: {
    "en-US": "Most tree points in this pilot area are OSM points checked against the UW cherry map.",
    "zh-CN": "本试点区域的大部分树点来自 OSM，并已对照 UW 樱花地图校对。",
    "zh-TW": "本試點區域的大部分樹點來自 OSM，並已對照 UW 櫻花地圖校對。",
    "es-ES": "La mayoría de los puntos de árboles provienen de OSM y fueron revisados con el mapa de UW.",
    "ko-KR": "이 시범 구역의 대부분의 나무 점은 OSM을 UW 벚꽃 지도와 대조해 확인했습니다.",
    "ja-JP": "この試験エリアの多くの樹木ポイントは、UW の桜マップで照合した OSM 点です。",
    "fr-FR": "La plupart des points d'arbres viennent d'OSM et ont été vérifiés avec la carte UW.",
    "vi-VN": "Phần lớn điểm cây trong khu vực thử nghiệm này đến từ OSM và đã được đối chiếu với bản đồ hoa anh đào UW."
  },
  weather_adjustment_clamped: {
    "en-US": "Live weather can shift the curve by at most four days to avoid unstable jumps.",
    "zh-CN": "实时天气的修正最多只会移动 4 天，避免预测每天大幅跳动。",
    "zh-TW": "即時天氣修正最多只會移動 4 天，避免預測每天大幅跳動。",
    "es-ES": "La corrección por tiempo en vivo se limita a cuatro días para evitar saltos bruscos.",
    "ko-KR": "실시간 날씨 보정은 예측이 크게 흔들리지 않도록 최대 4일까지만 이동합니다.",
    "ja-JP": "最新天気による補正は、大きく跳ねないよう最大 4 日までに制限しています。",
    "fr-FR": "L'ajustement météo en direct est limité à quatre jours pour éviter des sauts instables.",
    "vi-VN": "Điều chỉnh theo thời tiết trực tiếp chỉ dịch tối đa bốn ngày để tránh đường cong nhảy quá mạnh."
  }
};

const SOURCE_KIND_LABELS: Record<FeaturedAreaSourceKind, Record<Language, string>> = {
  official: {
    "en-US": "Official",
    "zh-CN": "官方",
    "zh-TW": "官方",
    "es-ES": "Oficial",
    "ko-KR": "공식",
    "ja-JP": "公式",
    "fr-FR": "Officiel",
    "vi-VN": "Chính thức"
  },
  supplemental: {
    "en-US": "Supplemental",
    "zh-CN": "补充",
    "zh-TW": "補充",
    "es-ES": "Complementario",
    "ko-KR": "보완",
    "ja-JP": "補足",
    "fr-FR": "Complémentaire",
    "vi-VN": "Bổ sung"
  },
  live: {
    "en-US": "Live",
    "zh-CN": "实时",
    "zh-TW": "即時",
    "es-ES": "En vivo",
    "ko-KR": "실시간",
    "ja-JP": "ライブ",
    "fr-FR": "En direct",
    "vi-VN": "Trực tiếp"
  }
};

const COORD_SOURCE_LABELS: Record<TreeCoordSource, Record<Language, string>> = {
  official: {
    "en-US": "Official coordinates",
    "zh-CN": "官方坐标",
    "zh-TW": "官方座標",
    "es-ES": "Coordenadas oficiales",
    "ko-KR": "공식 좌표",
    "ja-JP": "公式座標",
    "fr-FR": "Coordonnées officielles",
    "vi-VN": "Tọa độ chính thức"
  },
  osm_verified: {
    "en-US": "OSM verified with UW map",
    "zh-CN": "OSM + UW 地图校对",
    "zh-TW": "OSM + UW 地圖校對",
    "es-ES": "OSM verificado con mapa UW",
    "ko-KR": "OSM + UW 지도 대조",
    "ja-JP": "OSM を UW 地図で確認",
    "fr-FR": "OSM vérifié avec la carte UW",
    "vi-VN": "OSM đối chiếu với bản đồ UW"
  },
  manual_pdf: {
    "en-US": "Manual PDF estimate",
    "zh-CN": "PDF 手工补点",
    "zh-TW": "PDF 手工補點",
    "es-ES": "Estimación manual por PDF",
    "ko-KR": "PDF 수동 보정",
    "ja-JP": "PDF 手動補点",
    "fr-FR": "Estimation manuelle PDF",
    "vi-VN": "Ước lượng thủ công từ PDF"
  }
};

const WEATHER_LABELS: Record<
  "clear" | "partly_cloudy" | "cloudy" | "fog" | "rain" | "snow" | "storm",
  Record<Language, string>
> = {
  clear: {
    "en-US": "Clear",
    "zh-CN": "晴",
    "zh-TW": "晴",
    "es-ES": "Despejado",
    "ko-KR": "맑음",
    "ja-JP": "晴れ",
    "fr-FR": "Clair",
    "vi-VN": "Trời quang"
  },
  partly_cloudy: {
    "en-US": "Partly cloudy",
    "zh-CN": "多云间晴",
    "zh-TW": "多雲時晴",
    "es-ES": "Parcial",
    "ko-KR": "구름 조금",
    "ja-JP": "一部くもり",
    "fr-FR": "Partiel",
    "vi-VN": "Có mây"
  },
  cloudy: {
    "en-US": "Cloudy",
    "zh-CN": "多云",
    "zh-TW": "多雲",
    "es-ES": "Nublado",
    "ko-KR": "흐림",
    "ja-JP": "くもり",
    "fr-FR": "Nuageux",
    "vi-VN": "Nhiều mây"
  },
  fog: {
    "en-US": "Fog",
    "zh-CN": "雾",
    "zh-TW": "霧",
    "es-ES": "Niebla",
    "ko-KR": "안개",
    "ja-JP": "霧",
    "fr-FR": "Brouillard",
    "vi-VN": "Sương mù"
  },
  rain: {
    "en-US": "Rain",
    "zh-CN": "雨",
    "zh-TW": "雨",
    "es-ES": "Lluvia",
    "ko-KR": "비",
    "ja-JP": "雨",
    "fr-FR": "Pluie",
    "vi-VN": "Mưa"
  },
  snow: {
    "en-US": "Snow",
    "zh-CN": "雪",
    "zh-TW": "雪",
    "es-ES": "Nieve",
    "ko-KR": "눈",
    "ja-JP": "雪",
    "fr-FR": "Neige",
    "vi-VN": "Tuyết"
  },
  storm: {
    "en-US": "Storm",
    "zh-CN": "雷雨",
    "zh-TW": "雷雨",
    "es-ES": "Tormenta",
    "ko-KR": "폭풍",
    "ja-JP": "雷雨",
    "fr-FR": "Orage",
    "vi-VN": "Dông"
  }
};

function addDays(dateString: string, days: number): string {
  const date = new Date(`${dateString}T12:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

function classifyWeatherCode(code: number): keyof typeof WEATHER_LABELS {
  if (code === 0) {
    return "clear";
  }
  if (code === 1 || code === 2) {
    return "partly_cloudy";
  }
  if (code === 3) {
    return "cloudy";
  }
  if (code >= 45 && code <= 48) {
    return "fog";
  }
  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) {
    return "rain";
  }
  if ((code >= 71 && code <= 77) || code === 85 || code === 86) {
    return "snow";
  }
  return "storm";
}

export function featuredAreaCopy(language: Language): FeaturedAreaCopy {
  return FEATURED_AREA_COPY[language];
}

export function featuredAreaMeta(language: Language, areaId: string): {
  label: string;
  eyebrow: string;
  description: string;
} {
  return FEATURED_AREA_METADATA[areaId]?.[language] ?? FEATURED_AREA_METADATA["uw-seattle-quad"]["en-US"];
}

export function featuredAreaConfidenceNote(language: Language, noteId: string): string | null {
  return FEATURED_AREA_CONFIDENCE_NOTES[noteId]?.[language] ?? null;
}

export function featuredAreaSourceKindLabel(language: Language, kind: FeaturedAreaSourceKind): string {
  return SOURCE_KIND_LABELS[kind][language];
}

export function featuredAreaCoordSourceLabel(language: Language, source: TreeCoordSource | null | undefined): string | null {
  if (!source) {
    return null;
  }
  return COORD_SOURCE_LABELS[source][language];
}

export function featuredAreaWeatherLabel(language: Language, code: number): string {
  const bucket = classifyWeatherCode(code);
  return WEATHER_LABELS[bucket][language];
}

export function featuredAreaWeatherShortCode(code: number): string {
  const bucket = classifyWeatherCode(code);
  switch (bucket) {
    case "clear":
      return "CLR";
    case "partly_cloudy":
      return "PTC";
    case "cloudy":
      return "CLD";
    case "fog":
      return "FOG";
    case "rain":
      return "RAN";
    case "snow":
      return "SNW";
    default:
      return "STM";
  }
}

export function formatFeaturedDate(language: Language, dateString: string): string {
  return new Date(`${dateString}T12:00:00Z`).toLocaleDateString(language, {
    month: "short",
    day: "numeric"
  });
}

export function describeWeatherAdjustment(language: Language, adjustmentDays: number): string {
  const copy = featuredAreaCopy(language);
  if (adjustmentDays === 0) {
    return copy.weatherStable;
  }
  if (adjustmentDays < 0) {
    return `${copy.weatherShiftEarlier} ${Math.abs(adjustmentDays)}d`;
  }
  return `${copy.weatherShiftLater} ${Math.abs(adjustmentDays)}d`;
}

function averageWeatherMean(days: WeatherDaySummary[]): number | null {
  if (days.length === 0) {
    return null;
  }
  const sum = days.reduce((total, day) => total + (day.temperature_max_c + day.temperature_min_c) / 2, 0);
  return sum / days.length;
}

export function computeFeaturedAreaWeatherAdjustmentDays(areaId: string, weather: WeatherSnapshot | null): number {
  if (!weather) {
    return 0;
  }

  const baselineByAreaId: Record<string, number> = {
    "uw-seattle-quad": 8.5
  };
  const baseline = baselineByAreaId[areaId] ?? 8.5;
  const recentAndNextDays = weather.days.slice(0, 13);
  const averageMean = averageWeatherMean(recentAndNextDays);
  if (averageMean === null) {
    return 0;
  }

  const adjustment = Math.round((baseline - averageMean) / 1.6);
  return Math.max(-4, Math.min(4, adjustment));
}

export function applyWeatherAdjustmentToForecast(
  areaId: string,
  forecast: BloomForecast,
  weather: WeatherSnapshot | null
): BloomForecast {
  const adjustmentDays = computeFeaturedAreaWeatherAdjustmentDays(areaId, weather);
  if (adjustmentDays === 0) {
    return forecast;
  }
  return {
    ...forecast,
    curve_dates: forecast.curve_dates.map((date) => addDays(date, adjustmentDays)),
    start_date: addDays(forecast.start_date, adjustmentDays),
    peak_date: addDays(forecast.peak_date, adjustmentDays),
    end_date: addDays(forecast.end_date, adjustmentDays),
    weather_adjustment_days: adjustmentDays
  };
}

export function futureWeatherDays(weather: WeatherSnapshot | null): WeatherDaySummary[] {
  if (!weather) {
    return [];
  }
  const today = new Date().toISOString().slice(0, 10);
  return weather.days.filter((day) => day.date >= today).slice(0, 10);
}
