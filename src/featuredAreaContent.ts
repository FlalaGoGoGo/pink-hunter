import type {
  BloomForecast,
  FeaturedAreaSourceKind,
  Language,
  TreeCoordSource,
  WeatherDaySummary,
  WeatherSnapshot
} from "./types";

export type FeaturedWeatherBucket =
  | "clear"
  | "partly_cloudy"
  | "cloudy"
  | "fog"
  | "rain"
  | "snow"
  | "storm";

type FeaturedAreaCopy = {
  sectionTitle: string;
  sectionBody: string;
  openArea: string;
  previousPage: string;
  nextPage: string;
  pageLabel: string;
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
  openForecast: string;
  detailSourceLabel: string;
  coordSourceLabel: string;
  cultivarLabel: string;
  locationLabel: string;
  dbhLabel: string;
  updatedAt: string;
  mappedTreesLabel: string;
  officialMapTreesLabel: string;
  rainChanceShort: string;
  tempRangeLabel: string;
  notesCoverageTemplate: string;
  distanceUnit: string;
};

const FEATURED_AREA_COPY: Record<Language, FeaturedAreaCopy> = {
  "en-US": {
    sectionTitle: "Recommended Viewing Areas",
    sectionBody: "High-interest bloom areas with a faster way in.",
    openArea: "Open area details",
    previousPage: "Previous",
    nextPage: "Next",
    pageLabel: "Page {current} / {total}",
    chartTitle: "Bloom forecast",
    startLabel: "Start",
    peakLabel: "Peak",
    endLabel: "End",
    weatherTitle: "10-day weather",
    weatherLoading: "Loading live weather...",
    weatherUnavailable: "Live weather is temporarily unavailable. The static forecast is still shown.",
    weatherStable: "Live weather keeps the forecast unchanged today.",
    weatherShiftEarlier: "Live weather shifts the forecast earlier.",
    weatherShiftLater: "Live weather shifts the forecast later.",
    forecastModeMl: "ML forecast",
    forecastModeFallback: "Historical fallback",
    sourcesTitle: "Sources",
    confidenceTitle: "Notes",
    treesTitle: "Tree inventory",
    treesLoading: "Loading tree inventory...",
    treesEmpty: "Tree inventory is not loaded yet.",
    openForecast: "Open area bloom forecast",
    detailSourceLabel: "Detail source",
    coordSourceLabel: "Coordinate source",
    cultivarLabel: "Cultivar",
    locationLabel: "Location note",
    dbhLabel: "DBH",
    updatedAt: "Updated",
    mappedTreesLabel: "Mapped precise points",
    officialMapTreesLabel: "Official UW map codes",
    rainChanceShort: "Rain",
    tempRangeLabel: "Range",
    notesCoverageTemplate:
      "The official UW map shows {official} coded cherry locations; the current Pink Hunter pilot has precise points for {mapped} of them.",
    distanceUnit: "km"
  },
  "zh-CN": {
    sectionTitle: "推荐观赏区域",
    sectionBody: "把更值得去的赏花点放到前面。",
    openArea: "打开区域详情",
    previousPage: "上一页",
    nextPage: "下一页",
    pageLabel: "第 {current} / {total} 页",
    chartTitle: "开花预测",
    startLabel: "开始",
    peakLabel: "顶峰",
    endLabel: "结束",
    weatherTitle: "未来十天天气",
    weatherLoading: "正在加载实时天气...",
    weatherUnavailable: "实时天气暂时不可用，静态预测仍然可看。",
    weatherStable: "实时天气今天没有改变这条预测。",
    weatherShiftEarlier: "实时天气让预测整体提前。",
    weatherShiftLater: "实时天气让预测整体推后。",
    forecastModeMl: "机器学习预测",
    forecastModeFallback: "历史回退",
    sourcesTitle: "来源",
    confidenceTitle: "说明",
    treesTitle: "区域树木统计",
    treesLoading: "正在加载树木统计...",
    treesEmpty: "树木统计暂时不可用。",
    openForecast: "打开区域开花预测",
    detailSourceLabel: "详情来源",
    coordSourceLabel: "坐标来源",
    cultivarLabel: "品种",
    locationLabel: "位置说明",
    dbhLabel: "胸径",
    updatedAt: "更新于",
    mappedTreesLabel: "已映射精确点位",
    officialMapTreesLabel: "UW 官方地图编码点位",
    rainChanceShort: "降水",
    tempRangeLabel: "温度带",
    notesCoverageTemplate:
      "UW 官方地图目前可读出的樱花编码点位至少有 {official} 处；Pink Hunter 这期试点目前已经补到其中的精确点位 {mapped} 处。",
    distanceUnit: "公里"
  },
  "zh-TW": {
    sectionTitle: "推薦觀賞區域",
    sectionBody: "把更值得去的賞花點放到前面。",
    openArea: "打開區域詳情",
    previousPage: "上一頁",
    nextPage: "下一頁",
    pageLabel: "第 {current} / {total} 頁",
    chartTitle: "開花預測",
    startLabel: "開始",
    peakLabel: "高峰",
    endLabel: "結束",
    weatherTitle: "未來十天天氣",
    weatherLoading: "正在載入即時天氣...",
    weatherUnavailable: "即時天氣暫時不可用，靜態預測仍可查看。",
    weatherStable: "即時天氣今天沒有改變這條預測。",
    weatherShiftEarlier: "即時天氣讓預測整體提前。",
    weatherShiftLater: "即時天氣讓預測整體延後。",
    forecastModeMl: "機器學習預測",
    forecastModeFallback: "歷史回退",
    sourcesTitle: "來源",
    confidenceTitle: "說明",
    treesTitle: "區域樹木統計",
    treesLoading: "正在載入樹木統計...",
    treesEmpty: "樹木統計暫時不可用。",
    openForecast: "打開區域開花預測",
    detailSourceLabel: "詳情來源",
    coordSourceLabel: "座標來源",
    cultivarLabel: "品種",
    locationLabel: "位置說明",
    dbhLabel: "胸徑",
    updatedAt: "更新於",
    mappedTreesLabel: "已映射精確點位",
    officialMapTreesLabel: "UW 官方地圖編碼點位",
    rainChanceShort: "降水",
    tempRangeLabel: "溫度帶",
    notesCoverageTemplate:
      "UW 官方地圖目前可讀出的櫻花編碼點位至少有 {official} 處；Pink Hunter 這期試點目前已補到其中的精確點位 {mapped} 處。",
    distanceUnit: "公里"
  },
  "es-ES": {
    sectionTitle: "Zonas recomendadas",
    sectionBody: "Accesos rápidos a los mejores puntos de floración.",
    openArea: "Abrir detalles del área",
    previousPage: "Anterior",
    nextPage: "Siguiente",
    pageLabel: "Página {current} / {total}",
    chartTitle: "Pronóstico de floración",
    startLabel: "Inicio",
    peakLabel: "Pico",
    endLabel: "Fin",
    weatherTitle: "Tiempo a 10 días",
    weatherLoading: "Cargando tiempo en vivo...",
    weatherUnavailable: "El tiempo en vivo no está disponible por ahora. El pronóstico estático sigue visible.",
    weatherStable: "El tiempo en vivo no mueve el pronóstico hoy.",
    weatherShiftEarlier: "El tiempo en vivo adelanta el pronóstico.",
    weatherShiftLater: "El tiempo en vivo retrasa el pronóstico.",
    forecastModeMl: "Pronóstico ML",
    forecastModeFallback: "Respaldo histórico",
    sourcesTitle: "Fuentes",
    confidenceTitle: "Notas",
    treesTitle: "Inventario de árboles",
    treesLoading: "Cargando inventario...",
    treesEmpty: "El inventario aún no está disponible.",
    openForecast: "Abrir pronóstico del área",
    detailSourceLabel: "Fuente de detalle",
    coordSourceLabel: "Fuente de coordenadas",
    cultivarLabel: "Cultivar",
    locationLabel: "Nota de ubicación",
    dbhLabel: "DAP",
    updatedAt: "Actualizado",
    mappedTreesLabel: "Puntos precisos mapeados",
    officialMapTreesLabel: "Códigos del mapa oficial UW",
    rainChanceShort: "Lluvia",
    tempRangeLabel: "Rango",
    notesCoverageTemplate:
      "El mapa oficial de UW muestra {official} ubicaciones codificadas; el piloto actual de Pink Hunter tiene puntos precisos para {mapped} de ellas.",
    distanceUnit: "km"
  },
  "ko-KR": {
    sectionTitle: "추천 관람 구역",
    sectionBody: "먼저 봐야 할 꽃 구역을 빠르게 여는 목록입니다.",
    openArea: "구역 상세 열기",
    previousPage: "이전",
    nextPage: "다음",
    pageLabel: "{current} / {total} 페이지",
    chartTitle: "개화 예측",
    startLabel: "시작",
    peakLabel: "절정",
    endLabel: "종료",
    weatherTitle: "10일 날씨",
    weatherLoading: "실시간 날씨 불러오는 중...",
    weatherUnavailable: "실시간 날씨를 지금 불러올 수 없습니다. 정적 예측은 계속 표시됩니다.",
    weatherStable: "실시간 날씨가 오늘 예측을 바꾸지 않았습니다.",
    weatherShiftEarlier: "실시간 날씨로 예측이 더 앞당겨졌습니다.",
    weatherShiftLater: "실시간 날씨로 예측이 더 늦춰졌습니다.",
    forecastModeMl: "ML 예측",
    forecastModeFallback: "과거값 대체",
    sourcesTitle: "출처",
    confidenceTitle: "메모",
    treesTitle: "나무 통계",
    treesLoading: "나무 통계 불러오는 중...",
    treesEmpty: "나무 통계를 아직 불러오지 못했습니다.",
    openForecast: "지역 개화 예측 열기",
    detailSourceLabel: "상세 출처",
    coordSourceLabel: "좌표 출처",
    cultivarLabel: "품종",
    locationLabel: "위치 메모",
    dbhLabel: "흉고직경",
    updatedAt: "업데이트",
    mappedTreesLabel: "정밀 점 위치",
    officialMapTreesLabel: "UW 공식 지도 코드",
    rainChanceShort: "강수",
    tempRangeLabel: "범위",
    notesCoverageTemplate:
      "UW 공식 지도에는 코드 위치가 {official}개 보이며, 현재 Pink Hunter 시범판은 그중 정밀 점 {mapped}개를 담고 있습니다.",
    distanceUnit: "km"
  },
  "ja-JP": {
    sectionTitle: "おすすめ観賞エリア",
    sectionBody: "見に行く価値が高いエリアを先に出します。",
    openArea: "エリア詳細を開く",
    previousPage: "前へ",
    nextPage: "次へ",
    pageLabel: "{current} / {total} ページ",
    chartTitle: "開花予測",
    startLabel: "咲き始め",
    peakLabel: "ピーク",
    endLabel: "見頃終了",
    weatherTitle: "10日間の天気",
    weatherLoading: "最新の天気を読み込み中...",
    weatherUnavailable: "最新の天気は今利用できません。静的な予測は表示されます。",
    weatherStable: "最新の天気による予測の移動は今日はありません。",
    weatherShiftEarlier: "最新の天気で予測が前倒しになっています。",
    weatherShiftLater: "最新の天気で予測が後ろ倒しになっています。",
    forecastModeMl: "機械学習予測",
    forecastModeFallback: "履歴フォールバック",
    sourcesTitle: "出典",
    confidenceTitle: "メモ",
    treesTitle: "樹木サマリー",
    treesLoading: "樹木サマリーを読み込み中...",
    treesEmpty: "樹木サマリーはまだ利用できません。",
    openForecast: "エリアの開花予測を開く",
    detailSourceLabel: "詳細ソース",
    coordSourceLabel: "座標ソース",
    cultivarLabel: "品種",
    locationLabel: "位置メモ",
    dbhLabel: "胸高直径",
    updatedAt: "更新",
    mappedTreesLabel: "精密ポイント",
    officialMapTreesLabel: "UW 公式マップのコード数",
    rainChanceShort: "降水",
    tempRangeLabel: "幅",
    notesCoverageTemplate:
      "UW の公式マップでは少なくとも {official} 件のコード付き位置が確認でき、Pink Hunter の現行試験版ではそのうち精密ポイント {mapped} 件を掲載しています。",
    distanceUnit: "km"
  },
  "fr-FR": {
    sectionTitle: "Zones recommandées",
    sectionBody: "Des accès rapides vers les meilleurs lieux de floraison.",
    openArea: "Ouvrir les détails de la zone",
    previousPage: "Précédent",
    nextPage: "Suivant",
    pageLabel: "Page {current} / {total}",
    chartTitle: "Prévision de floraison",
    startLabel: "Début",
    peakLabel: "Pic",
    endLabel: "Fin",
    weatherTitle: "Météo sur 10 jours",
    weatherLoading: "Chargement de la météo en direct...",
    weatherUnavailable: "La météo en direct est indisponible pour le moment. La prévision statique reste visible.",
    weatherStable: "La météo en direct ne décale pas la prévision aujourd'hui.",
    weatherShiftEarlier: "La météo en direct avance la prévision.",
    weatherShiftLater: "La météo en direct retarde la prévision.",
    forecastModeMl: "Prévision ML",
    forecastModeFallback: "Repli historique",
    sourcesTitle: "Sources",
    confidenceTitle: "Notes",
    treesTitle: "Inventaire des arbres",
    treesLoading: "Chargement de l'inventaire...",
    treesEmpty: "L'inventaire n'est pas encore disponible.",
    openForecast: "Ouvrir la prévision de la zone",
    detailSourceLabel: "Source du détail",
    coordSourceLabel: "Source des coordonnées",
    cultivarLabel: "Cultivar",
    locationLabel: "Note de lieu",
    dbhLabel: "DHP",
    updatedAt: "Mis à jour",
    mappedTreesLabel: "Points précis cartographiés",
    officialMapTreesLabel: "Codes sur la carte officielle UW",
    rainChanceShort: "Pluie",
    tempRangeLabel: "Plage",
    notesCoverageTemplate:
      "La carte officielle de l'UW montre {official} emplacements codés ; le pilote Pink Hunter dispose de points précis pour {mapped} d'entre eux.",
    distanceUnit: "km"
  },
  "vi-VN": {
    sectionTitle: "Khu vực gợi ý",
    sectionBody: "Mở nhanh các điểm ngắm hoa đáng đi nhất.",
    openArea: "Mở chi tiết khu vực",
    previousPage: "Trước",
    nextPage: "Sau",
    pageLabel: "Trang {current} / {total}",
    chartTitle: "Dự báo nở hoa",
    startLabel: "Bắt đầu",
    peakLabel: "Đỉnh",
    endLabel: "Kết thúc",
    weatherTitle: "Thời tiết 10 ngày",
    weatherLoading: "Đang tải thời tiết trực tiếp...",
    weatherUnavailable: "Thời tiết trực tiếp hiện không khả dụng. Dự báo tĩnh vẫn được hiển thị.",
    weatherStable: "Thời tiết trực tiếp hôm nay không làm thay đổi dự báo.",
    weatherShiftEarlier: "Thời tiết trực tiếp đẩy dự báo sớm hơn.",
    weatherShiftLater: "Thời tiết trực tiếp đẩy dự báo muộn hơn.",
    forecastModeMl: "Dự báo ML",
    forecastModeFallback: "Dự phòng lịch sử",
    sourcesTitle: "Nguồn",
    confidenceTitle: "Ghi chú",
    treesTitle: "Thống kê cây",
    treesLoading: "Đang tải thống kê cây...",
    treesEmpty: "Chưa có thống kê cây.",
    openForecast: "Mở dự báo khu vực",
    detailSourceLabel: "Nguồn chi tiết",
    coordSourceLabel: "Nguồn tọa độ",
    cultivarLabel: "Giống",
    locationLabel: "Ghi chú vị trí",
    dbhLabel: "Đường kính thân",
    updatedAt: "Cập nhật",
    mappedTreesLabel: "Điểm chính xác đã gắn",
    officialMapTreesLabel: "Mã trên bản đồ UW",
    rainChanceShort: "Mưa",
    tempRangeLabel: "Khoảng",
    notesCoverageTemplate:
      "Bản đồ chính thức của UW cho thấy {official} điểm được mã hóa; Pink Hunter hiện có điểm chính xác cho {mapped} trong số đó.",
    distanceUnit: "km"
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
      description: "A campus pilot centered on the Quad with bloom timing, weather, and a tighter cherry inventory view."
    },
    "zh-CN": {
      label: "UW Seattle Quad",
      eyebrow: "University of Washington",
      description: "围绕 Quad 做的校园试点，把开花时间、天气和更紧凑的樱花树数据放在一起。"
    },
    "zh-TW": {
      label: "UW Seattle Quad",
      eyebrow: "University of Washington",
      description: "圍繞 Quad 做的校園試點，把開花時間、天氣與更精簡的櫻花樹資料放在一起。"
    },
    "es-ES": {
      label: "UW Seattle Quad",
      eyebrow: "University of Washington",
      description: "Piloto de campus centrado en el Quad con fechas de floración, tiempo y un inventario más claro."
    },
    "ko-KR": {
      label: "UW Seattle Quad",
      eyebrow: "University of Washington",
      description: "Quad를 중심으로 개화 시기, 날씨, 더 정리된 벚나무 데이터를 묶은 캠퍼스 시범판입니다."
    },
    "ja-JP": {
      label: "UW Seattle Quad",
      eyebrow: "University of Washington",
      description: "Quad を中心に、開花時期と天気、整理した桜データをまとめたキャンパス試験版です。"
    },
    "fr-FR": {
      label: "UW Seattle Quad",
      eyebrow: "University of Washington",
      description: "Pilote sur le campus autour du Quad avec les dates de floraison, la météo et un inventaire plus lisible."
    },
    "vi-VN": {
      label: "UW Seattle Quad",
      eyebrow: "University of Washington",
      description: "Bản thử nghiệm trong khuôn viên tập trung vào Quad, gộp thời gian nở hoa, thời tiết và dữ liệu cây gọn hơn."
    }
  }
};

const FEATURED_AREA_CONFIDENCE_NOTES: Record<string, Record<Language, string>> = {
  official_peak_dates: {
    "en-US": "Peak bloom dates come from official UW bloom history records.",
    "zh-CN": "盛开峰值日期来自 UW 官方 bloom 历史记录。",
    "zh-TW": "盛開高峰日期來自 UW 官方 bloom 歷史紀錄。",
    "es-ES": "Las fechas pico vienen del historial oficial de floración de UW.",
    "ko-KR": "절정 개화일은 UW 공식 bloom 기록을 사용합니다.",
    "ja-JP": "ピーク日は UW の公式 bloom 記録を使用しています。",
    "fr-FR": "Les dates de pic proviennent des relevés officiels de l'UW.",
    "vi-VN": "Ngày nở rộ lấy từ hồ sơ bloom chính thức của UW."
  },
  osm_verified_locations: {
    "en-US": "Most precise pilot points come from OSM and were checked against the UW cherry map.",
    "zh-CN": "目前这批精确点位大多来自 OSM，并已对照 UW 樱花地图校对。",
    "zh-TW": "目前這批精確點位大多來自 OSM，並已對照 UW 櫻花地圖校對。",
    "es-ES": "La mayoría de los puntos precisos vienen de OSM y se revisaron con el mapa de UW.",
    "ko-KR": "현재 정밀 점 위치 대부분은 OSM을 UW 벚꽃 지도와 대조해 확인했습니다.",
    "ja-JP": "現在の精密ポイントの多くは OSM を UW の桜マップで照合しています。",
    "fr-FR": "La plupart des points précis viennent d'OSM et ont été vérifiés avec la carte UW.",
    "vi-VN": "Phần lớn điểm chính xác hiện tại đến từ OSM và đã đối chiếu với bản đồ UW."
  },
  weather_adjustment_clamped: {
    "en-US": "Live weather can shift the forecast by at most four days to avoid unstable jumps.",
    "zh-CN": "实时天气修正最多只会移动 4 天，避免预测大幅跳动。",
    "zh-TW": "即時天氣修正最多只會移動 4 天，避免預測大幅跳動。",
    "es-ES": "El ajuste por tiempo en vivo se limita a cuatro días para evitar saltos bruscos.",
    "ko-KR": "실시간 날씨 보정은 예측이 크게 흔들리지 않도록 최대 4일까지만 이동합니다.",
    "ja-JP": "最新天気による補正は大きく跳ねないよう最大 4 日までに制限しています。",
    "fr-FR": "L'ajustement météo en direct est limité à quatre jours pour éviter les sauts instables.",
    "vi-VN": "Điều chỉnh theo thời tiết trực tiếp chỉ dịch tối đa bốn ngày để tránh nhảy quá mạnh."
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

const WEATHER_LABELS: Record<FeaturedWeatherBucket, Record<Language, string>> = {
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
    "zh-CN": "晴间多云",
    "zh-TW": "多雲時晴",
    "es-ES": "Parcialmente nublado",
    "ko-KR": "구름 조금",
    "ja-JP": "一部くもり",
    "fr-FR": "Partiellement nuageux",
    "vi-VN": "Ít mây"
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

function classifyWeatherCode(code: number): FeaturedWeatherBucket {
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

export function formatFeaturedPageLabel(language: Language, current: number, total: number): string {
  const copy = featuredAreaCopy(language);
  return copy.pageLabel
    .replace("{current}", current.toLocaleString(language))
    .replace("{total}", total.toLocaleString(language));
}

export function featuredAreaMeta(
  language: Language,
  areaId: string
): { label: string; eyebrow: string; description: string } {
  return FEATURED_AREA_METADATA[areaId]?.[language] ?? FEATURED_AREA_METADATA["uw-seattle-quad"]["en-US"];
}

export function featuredAreaConfidenceNote(language: Language, noteId: string): string | null {
  return FEATURED_AREA_CONFIDENCE_NOTES[noteId]?.[language] ?? null;
}

export function featuredAreaInventoryCoverageNote(
  language: Language,
  officialCount: number | null,
  mappedCount: number
): string | null {
  if (!officialCount || mappedCount <= 0) {
    return null;
  }
  const copy = featuredAreaCopy(language);
  return copy.notesCoverageTemplate
    .replace("{official}", officialCount.toLocaleString(language))
    .replace("{mapped}", mappedCount.toLocaleString(language));
}

export function featuredAreaSourceKindLabel(language: Language, kind: FeaturedAreaSourceKind): string {
  return SOURCE_KIND_LABELS[kind][language];
}

export function featuredAreaCoordSourceLabel(
  language: Language,
  source: TreeCoordSource | null | undefined
): string | null {
  if (!source) {
    return null;
  }
  return COORD_SOURCE_LABELS[source][language];
}

export function featuredAreaWeatherBucket(code: number): FeaturedWeatherBucket {
  return classifyWeatherCode(code);
}

export function featuredAreaWeatherLabel(language: Language, code: number): string {
  return WEATHER_LABELS[classifyWeatherCode(code)][language];
}

export function formatFeaturedDate(language: Language, dateString: string): string {
  return new Date(`${dateString}T12:00:00Z`).toLocaleDateString(language, {
    month: "short",
    day: "numeric"
  });
}

export function formatFeaturedWeekday(language: Language, dateString: string): string {
  return new Date(`${dateString}T12:00:00Z`).toLocaleDateString(language, {
    weekday: "short"
  });
}

export function formatDistanceKm(language: Language, distanceKm: number): string {
  const copy = featuredAreaCopy(language);
  return `${new Intl.NumberFormat(language, { maximumFractionDigits: distanceKm < 10 ? 1 : 0 }).format(distanceKm)} ${copy.distanceUnit}`;
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
