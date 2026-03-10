import { useEffect, useMemo, useState } from "react";
import type { FeaturedAreaDetail, Language, TreeFeatureProps, WeatherSnapshot } from "./types";
import {
  applyWeatherAdjustmentToForecast,
  describeWeatherAdjustment,
  featuredAreaConfidenceNote,
  featuredAreaCoordSourceLabel,
  featuredAreaCopy,
  featuredAreaMeta,
  featuredAreaSourceKindLabel,
  featuredAreaWeatherLabel,
  featuredAreaWeatherShortCode,
  formatFeaturedDate,
  futureWeatherDays
} from "./featuredAreaContent";
import { speciesLabel } from "./i18n";

type AreaTree = {
  coordinates: [number, number];
  properties: TreeFeatureProps;
};

interface FeaturedAreaPanelProps {
  area: FeaturedAreaDetail;
  language: Language;
  weather: WeatherSnapshot | null;
  weatherLoading: boolean;
  weatherError: string | null;
  trees: AreaTree[];
  selectedTreeId: string | null;
  onSelectTree: (treeId: string) => void;
}

interface FeaturedAreaSummaryCardProps {
  area: FeaturedAreaDetail;
  language: Language;
  weather: WeatherSnapshot | null;
  onOpenArea: () => void;
}

const SVG_WIDTH = 1000;
const SVG_HEIGHT = 308;
const CHART_LEFT = 54;
const CHART_RIGHT = 18;
const CHART_TOP = 24;
const CHART_HEIGHT = 148;
const WEATHER_TOP = 198;
const WEATHER_HEIGHT = 82;

function addDays(dateString: string, days: number): string {
  const date = new Date(`${dateString}T12:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

function dateDiffDays(left: string, right: string): number {
  const leftDate = new Date(`${left}T12:00:00Z`);
  const rightDate = new Date(`${right}T12:00:00Z`);
  return Math.round((rightDate.getTime() - leftDate.getTime()) / 86_400_000);
}

function buildDateRange(startDate: string, endDate: string): string[] {
  const totalDays = Math.max(0, dateDiffDays(startDate, endDate));
  return Array.from({ length: totalDays + 1 }, (_, index) => addDays(startDate, index));
}

function maxDate(left: string, right: string): string {
  return left >= right ? left : right;
}

function minDate(left: string, right: string): string {
  return left <= right ? left : right;
}

function forecastWindowEnd(todayIso: string, endDate: string): string {
  const rawEnd = maxDate(addDays(todayIso, 10), addDays(endDate, 3));
  return minDate(rawEnd, addDays(addDays(todayIso, -3), 44));
}

function metricChip(label: string, value: string): JSX.Element {
  return (
    <div className="featured-area-metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function formatDbh(language: Language, value: number | null | undefined): string | null {
  if (value == null || !Number.isFinite(value)) {
    return null;
  }
  return `${new Intl.NumberFormat(language, { maximumFractionDigits: 1 }).format(value)} in`;
}

export function FeaturedAreaSummaryCard({
  area,
  language,
  weather,
  onOpenArea
}: FeaturedAreaSummaryCardProps): JSX.Element {
  const copy = featuredAreaCopy(language);
  const meta = featuredAreaMeta(language, area.id);
  const adjustedForecast = useMemo(
    () => applyWeatherAdjustmentToForecast(area.id, area.bloom_forecast, weather),
    [area, weather]
  );

  return (
    <article className="tree-card selected featured-area-summary-card">
      <p className="featured-area-eyebrow">{meta.eyebrow}</p>
      <h4>{meta.label}</h4>
      <p>{meta.description}</p>
      <div className="featured-area-metrics compact">
        {metricChip(copy.startLabel, formatFeaturedDate(language, adjustedForecast.start_date))}
        {metricChip(copy.peakLabel, formatFeaturedDate(language, adjustedForecast.peak_date))}
        {metricChip(copy.endLabel, formatFeaturedDate(language, adjustedForecast.end_date))}
      </div>
      <p className="featured-area-summary-note">{describeWeatherAdjustment(language, adjustedForecast.weather_adjustment_days)}</p>
      <button className="detail-route-btn featured-area-open-btn" onClick={onOpenArea} type="button">
        {copy.openForecast}
      </button>
    </article>
  );
}

export function FeaturedAreaPanel({
  area,
  language,
  weather,
  weatherLoading,
  weatherError,
  trees,
  selectedTreeId,
  onSelectTree
}: FeaturedAreaPanelProps): JSX.Element {
  const copy = featuredAreaCopy(language);
  const meta = featuredAreaMeta(language, area.id);
  const adjustedForecast = useMemo(
    () => applyWeatherAdjustmentToForecast(area.id, area.bloom_forecast, weather),
    [area, weather]
  );
  const weatherDays = useMemo(() => futureWeatherDays(weather), [weather]);
  const todayIso = new Date().toISOString().slice(0, 10);
  const windowStart = addDays(todayIso, -3);
  const windowEnd = forecastWindowEnd(todayIso, adjustedForecast.end_date);
  const windowDates = useMemo(() => buildDateRange(windowStart, windowEnd), [windowEnd, windowStart]);
  const curveValuesByDate = useMemo(
    () => new Map(adjustedForecast.curve_dates.map((date, index) => [date, adjustedForecast.curve_values[index] ?? 0])),
    [adjustedForecast.curve_dates, adjustedForecast.curve_values]
  );
  const weatherByDate = useMemo(() => new Map(weatherDays.map((day) => [day.date, day])), [weatherDays]);
  const [selectedDate, setSelectedDate] = useState<string>(adjustedForecast.peak_date);

  useEffect(() => {
    setSelectedDate(adjustedForecast.peak_date);
  }, [adjustedForecast.peak_date, area.id]);

  const plotWidth = SVG_WIDTH - CHART_LEFT - CHART_RIGHT;
  const step = windowDates.length > 1 ? plotWidth / (windowDates.length - 1) : plotWidth;
  const xForDate = (date: string): number => CHART_LEFT + step * Math.max(0, dateDiffDays(windowStart, date));
  const yForValue = (value: number): number => CHART_TOP + CHART_HEIGHT - (value / 100) * CHART_HEIGHT;

  const linePath = windowDates
    .map((date, index) => `${index === 0 ? "M" : "L"} ${xForDate(date).toFixed(2)} ${yForValue(curveValuesByDate.get(date) ?? 0).toFixed(2)}`)
    .join(" ");
  const areaPath = `${linePath} L ${xForDate(windowDates[windowDates.length - 1] ?? windowStart).toFixed(2)} ${(CHART_TOP + CHART_HEIGHT).toFixed(2)} L ${xForDate(windowDates[0] ?? windowStart).toFixed(2)} ${(CHART_TOP + CHART_HEIGHT).toFixed(2)} Z`;

  const axisLabelDates = new Set<string>([
    todayIso,
    adjustedForecast.start_date,
    adjustedForecast.peak_date,
    adjustedForecast.end_date
  ]);
  windowDates.forEach((date, index) => {
    if (index % 4 === 0) {
      axisLabelDates.add(date);
    }
  });

  const selectedCurveValue = curveValuesByDate.get(selectedDate) ?? 0;
  const selectedWeather = weatherByDate.get(selectedDate) ?? null;

  return (
    <article className="featured-area-card">
      <header className="featured-area-hero">
        <div>
          <p className="featured-area-eyebrow">{meta.eyebrow}</p>
          <h3>{meta.label}</h3>
          <p>{meta.description}</p>
        </div>
        <div className="featured-area-mode-badge">{adjustedForecast.mode === "ml" ? copy.forecastModeMl : copy.forecastModeFallback}</div>
      </header>

      <div className="featured-area-metrics">
        {metricChip(copy.startLabel, formatFeaturedDate(language, adjustedForecast.start_date))}
        {metricChip(copy.peakLabel, formatFeaturedDate(language, adjustedForecast.peak_date))}
        {metricChip(copy.endLabel, formatFeaturedDate(language, adjustedForecast.end_date))}
      </div>

      <div className="featured-area-forecast-shell">
        <div className="featured-area-forecast-header">
          <div>
            <h4>{copy.chartTitle}</h4>
            <p>{describeWeatherAdjustment(language, adjustedForecast.weather_adjustment_days)}</p>
          </div>
          <div className="featured-area-updated">
            {copy.updatedAt}: {new Date(adjustedForecast.updated_at).toLocaleDateString(language)}
          </div>
        </div>

        <svg
          aria-label={copy.chartTitle}
          className="featured-area-chart"
          role="img"
          viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
        >
          <rect className="featured-area-chart-bg" height={CHART_HEIGHT + WEATHER_HEIGHT + 20} rx="18" ry="18" width={SVG_WIDTH} x="0" y="0" />
          {selectedDate ? (
            <rect
              className="featured-area-selected-band"
              height={SVG_HEIGHT - 28}
              width={Math.max(step, 16)}
              x={xForDate(selectedDate) - Math.max(step, 16) / 2}
              y="16"
            />
          ) : null}
          <path className="featured-area-area-fill" d={areaPath} />
          <path className="featured-area-line" d={linePath} />
          <line className="featured-area-baseline" x1={CHART_LEFT} x2={SVG_WIDTH - CHART_RIGHT} y1={CHART_TOP + CHART_HEIGHT} y2={CHART_TOP + CHART_HEIGHT} />
          <line className="featured-area-today-line" x1={xForDate(todayIso)} x2={xForDate(todayIso)} y1={CHART_TOP - 4} y2={CHART_TOP + CHART_HEIGHT + WEATHER_HEIGHT + 8} />

          {[adjustedForecast.start_date, adjustedForecast.peak_date, adjustedForecast.end_date].map((date) => {
            const value = curveValuesByDate.get(date) ?? 0;
            return (
              <g key={date}>
                <circle className="featured-area-point" cx={xForDate(date)} cy={yForValue(value)} r="5.5" />
              </g>
            );
          })}

          {selectedDate ? (
            <circle className="featured-area-selected-point" cx={xForDate(selectedDate)} cy={yForValue(selectedCurveValue)} r="6.5" />
          ) : null}

          {windowDates
            .filter((date) => axisLabelDates.has(date))
            .map((date) => (
              <text className="featured-area-axis-label" key={date} x={xForDate(date)} y={CHART_TOP + CHART_HEIGHT + 18}>
                {formatFeaturedDate(language, date)}
              </text>
            ))}

          {weatherDays.map((day) => {
            const isSelected = selectedDate === day.date;
            const cardWidth = Math.max(42, Math.min(72, step * 1.6));
            return (
              <g
                className={isSelected ? "featured-area-weather-card selected" : "featured-area-weather-card"}
                key={day.date}
                onClick={() => setSelectedDate(day.date)}
              >
                <rect
                  className="featured-area-weather-rect"
                  height={WEATHER_HEIGHT - 10}
                  rx="10"
                  ry="10"
                  width={cardWidth}
                  x={xForDate(day.date) - cardWidth / 2}
                  y={WEATHER_TOP}
                />
                <text className="featured-area-weather-date" x={xForDate(day.date)} y={WEATHER_TOP + 16}>
                  {formatFeaturedDate(language, day.date)}
                </text>
                <text className="featured-area-weather-code" x={xForDate(day.date)} y={WEATHER_TOP + 33}>
                  {featuredAreaWeatherShortCode(day.weather_code)}
                </text>
                <text className="featured-area-weather-temp" x={xForDate(day.date)} y={WEATHER_TOP + 50}>
                  {Math.round(day.temperature_max_c)} / {Math.round(day.temperature_min_c)}
                </text>
                <text className="featured-area-weather-pop" x={xForDate(day.date)} y={WEATHER_TOP + 66}>
                  {day.precipitation_probability_max == null ? "--" : `${Math.round(day.precipitation_probability_max)}%`}
                </text>
              </g>
            );
          })}
        </svg>

        <div className="featured-area-chart-detail">
          {selectedWeather ? (
            <p>
              <strong>{formatFeaturedDate(language, selectedWeather.date)}:</strong>{" "}
              {featuredAreaWeatherLabel(language, selectedWeather.weather_code)}. {Math.round(selectedWeather.temperature_max_c)} /{" "}
              {Math.round(selectedWeather.temperature_min_c)} C.
            </p>
          ) : null}
          {weatherLoading ? <p>{copy.weatherLoading}</p> : null}
          {!weatherLoading && (weatherError || (!weather && area.bloom_forecast.weather_adjustment_days === 0)) ? (
            <p>{copy.weatherUnavailable}</p>
          ) : null}
        </div>
      </div>

      <section className="featured-area-sources">
        <h4>{copy.sourcesTitle}</h4>
        <div className="featured-area-source-list">
          {area.sources.map((source) => (
            <a
              className="featured-area-source-pill"
              href={source.href ?? undefined}
              key={source.id}
              rel="noreferrer"
              target={source.href ? "_blank" : undefined}
            >
              <span>{source.label}</span>
              <strong>{featuredAreaSourceKindLabel(language, source.kind)}</strong>
            </a>
          ))}
        </div>
      </section>

      <section className="featured-area-confidence">
        <h4>{copy.confidenceTitle}</h4>
        <ul>
          {area.confidence_note_ids
            .map((noteId) => featuredAreaConfidenceNote(language, noteId))
            .filter((note): note is string => Boolean(note))
            .map((note) => (
              <li key={note}>{note}</li>
            ))}
        </ul>
      </section>

      <section className="featured-area-tree-list">
        <div className="featured-area-tree-list-head">
          <h4>{copy.treesTitle}</h4>
          <span>
            {trees.length} / {area.tree_ids.length}
          </span>
        </div>
        {trees.length === 0 ? (
          <p>{copy.treesLoading}</p>
        ) : (
          <div className="featured-area-tree-grid">
            {trees.map((tree) => {
              const coordSourceLabel = featuredAreaCoordSourceLabel(language, tree.properties.coord_source);
              const dbhText = formatDbh(language, tree.properties.dbh);
              return (
                <button
                  className={
                    tree.properties.id === selectedTreeId
                      ? "featured-area-tree-item active"
                      : "featured-area-tree-item"
                  }
                  key={tree.properties.id}
                  onClick={() => onSelectTree(tree.properties.id)}
                  type="button"
                >
                  <strong>{tree.properties.cultivar ?? tree.properties.subtype_name ?? speciesLabel(language, tree.properties.species_group)}</strong>
                  <span>{tree.properties.location_note ?? tree.properties.scientific_name}</span>
                  <span>{coordSourceLabel ?? tree.properties.detail_source_label ?? tree.properties.source_dataset}</span>
                  {dbhText ? (
                    <span>
                      {copy.dbhLabel}: {dbhText}
                    </span>
                  ) : null}
                </button>
              );
            })}
          </div>
        )}
      </section>
    </article>
  );
}

export function FeaturedTreeMetaRows({
  language,
  tree
}: {
  language: Language;
  tree: AreaTree;
}): JSX.Element {
  const copy = featuredAreaCopy(language);
  const coordSourceLabel = featuredAreaCoordSourceLabel(language, tree.properties.coord_source);
  const dbhText = formatDbh(language, tree.properties.dbh);

  return (
    <>
      {tree.properties.cultivar ? (
        <p>
          <strong>{copy.cultivarLabel}: </strong>
          {tree.properties.cultivar}
        </p>
      ) : null}
      {tree.properties.location_note ? (
        <p>
          <strong>{copy.locationLabel}: </strong>
          {tree.properties.location_note}
        </p>
      ) : null}
      {coordSourceLabel ? (
        <p>
          <strong>{copy.coordSourceLabel}: </strong>
          {coordSourceLabel}
        </p>
      ) : null}
      {tree.properties.detail_source_label ? (
        <p>
          <strong>{copy.detailSourceLabel}: </strong>
          {tree.properties.detail_source_label}
        </p>
      ) : null}
      {dbhText ? (
        <p>
          <strong>{copy.dbhLabel}: </strong>
          {dbhText}
        </p>
      ) : null}
    </>
  );
}
