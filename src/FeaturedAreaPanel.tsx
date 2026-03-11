import { useMemo } from "react";
import type { FeaturedAreaDetail, Language, SpeciesGroup, TreeFeatureProps, WeatherSnapshot } from "./types";
import {
  applyWeatherAdjustmentToForecast,
  describeWeatherAdjustment,
  featuredAreaConfidenceNote,
  featuredAreaCoordSourceLabel,
  featuredAreaCopy,
  featuredAreaInventoryCoverageNote,
  featuredAreaMeta,
  featuredAreaSourceKindLabel,
  featuredAreaWeatherBucket,
  featuredAreaWeatherLabel,
  formatFeaturedDate,
  formatFeaturedWeekday,
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
}

interface FeaturedAreaSummaryCardProps {
  area: FeaturedAreaDetail;
  language: Language;
  weather: WeatherSnapshot | null;
  onOpenArea: () => void;
}

type InventoryGroupSummary = {
  group: SpeciesGroup;
  count: number;
  variants: Array<{ label: string; count: number }>;
};

const SVG_WIDTH = 1200;
const SVG_HEIGHT = 340;
const CHART_LEFT = 72;
const CHART_RIGHT = 40;
const CHART_TOP = 44;
const CHART_BOTTOM = 118;
const ICON_ROW_BOTTOM = 42;

function dateNumber(dateString: string): number {
  return new Date(`${dateString}T12:00:00Z`).getTime();
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

function inventoryVariantLabel(tree: AreaTree): string {
  return (
    tree.properties.cultivar ??
    tree.properties.subtype_name ??
    tree.properties.common_name ??
    tree.properties.scientific_name
  );
}

function WeatherIcon({
  code,
  size = 18,
  className
}: {
  code: number;
  size?: number;
  className?: string;
}): JSX.Element {
  const bucket = featuredAreaWeatherBucket(code);

  if (bucket === "clear") {
    return (
      <svg aria-hidden="true" className={className} height={size} viewBox="0 0 24 24" width={size}>
        <circle cx="12" cy="12" fill="none" r="4.4" stroke="currentColor" strokeWidth="1.9" />
        <path
          d="M12 2.8v3.1M12 18.1v3.1M21.2 12h-3.1M5.9 12H2.8M18.5 5.5l-2.2 2.2M7.7 16.3l-2.2 2.2M18.5 18.5l-2.2-2.2M7.7 7.7 5.5 5.5"
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeWidth="1.7"
        />
      </svg>
    );
  }

  if (bucket === "partly_cloudy") {
    return (
      <svg aria-hidden="true" className={className} height={size} viewBox="0 0 24 24" width={size}>
        <path
          d="M8.2 9.1a3.6 3.6 0 1 1 5.3-3.2"
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeWidth="1.7"
        />
        <path
          d="M7.8 18.6h8.2a3.1 3.1 0 0 0 .3-6.2 4.5 4.5 0 0 0-8.5-1.3 3.6 3.6 0 1 0 0 7.5Z"
          fill="none"
          stroke="currentColor"
          strokeLinejoin="round"
          strokeWidth="1.8"
        />
      </svg>
    );
  }

  if (bucket === "cloudy") {
    return (
      <svg aria-hidden="true" className={className} height={size} viewBox="0 0 24 24" width={size}>
        <path
          d="M7.4 18.3h9.1a3.3 3.3 0 0 0 .2-6.6 4.8 4.8 0 0 0-9.2-1.4 3.9 3.9 0 1 0-.1 8Z"
          fill="none"
          stroke="currentColor"
          strokeLinejoin="round"
          strokeWidth="1.9"
        />
      </svg>
    );
  }

  if (bucket === "fog") {
    return (
      <svg aria-hidden="true" className={className} height={size} viewBox="0 0 24 24" width={size}>
        <path
          d="M6.8 10.2h9.6a2.9 2.9 0 0 0 .1-5.8 4.2 4.2 0 0 0-7.9-1.2 3.3 3.3 0 1 0-.1 7Z"
          fill="none"
          stroke="currentColor"
          strokeLinejoin="round"
          strokeWidth="1.7"
        />
        <path
          d="M4 14.8h16M6.2 18h11.6"
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeWidth="1.7"
        />
      </svg>
    );
  }

  if (bucket === "rain") {
    return (
      <svg aria-hidden="true" className={className} height={size} viewBox="0 0 24 24" width={size}>
        <path
          d="M7.2 13.2h9.3a3.2 3.2 0 0 0 .2-6.4 4.6 4.6 0 0 0-8.8-1.3 3.7 3.7 0 1 0-.7 7.7Z"
          fill="none"
          stroke="currentColor"
          strokeLinejoin="round"
          strokeWidth="1.7"
        />
        <path
          d="M9 16.5 7.8 20M13 16.5 11.8 20M17 16.5 15.8 20"
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeWidth="1.8"
        />
      </svg>
    );
  }

  if (bucket === "snow") {
    return (
      <svg aria-hidden="true" className={className} height={size} viewBox="0 0 24 24" width={size}>
        <path
          d="M7.2 12.9h9.3a3.2 3.2 0 0 0 .2-6.4 4.6 4.6 0 0 0-8.8-1.3 3.7 3.7 0 1 0-.7 7.7Z"
          fill="none"
          stroke="currentColor"
          strokeLinejoin="round"
          strokeWidth="1.7"
        />
        <path
          d="m9.4 16.6 1.3 1.3m0-2.6-1.3 1.3m4.9 0 1.3 1.3m0-2.6-1.3 1.3"
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeWidth="1.6"
        />
      </svg>
    );
  }

  return (
    <svg aria-hidden="true" className={className} height={size} viewBox="0 0 24 24" width={size}>
      <path
        d="M7.1 12.7h9.4a3.2 3.2 0 0 0 .2-6.4 4.6 4.6 0 0 0-8.8-1.3 3.7 3.7 0 1 0-.8 7.7Z"
        fill="none"
        stroke="currentColor"
        strokeLinejoin="round"
        strokeWidth="1.7"
      />
      <path
        d="m12.3 14.9-2.1 3.7h2l-1 3.4 3.5-4.9h-2.1l1.3-2.2"
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function ForecastCurve({
  areaId,
  forecast,
  language,
  weather
}: {
  areaId: string;
  forecast: FeaturedAreaDetail["bloom_forecast"];
  language: Language;
  weather: WeatherSnapshot | null;
}): JSX.Element {
  const adjustedForecast = useMemo(
    () => applyWeatherAdjustmentToForecast(areaId, forecast, weather),
    [areaId, forecast, weather]
  );
  const weatherDays = useMemo(() => futureWeatherDays(weather), [weather]);
  const allDates = adjustedForecast.curve_dates;
  const minDate = allDates[0] ?? adjustedForecast.start_date;
  const maxDate = allDates[allDates.length - 1] ?? adjustedForecast.end_date;
  const dateSpan = Math.max(1, dateNumber(maxDate) - dateNumber(minDate));
  const chartWidth = SVG_WIDTH - CHART_LEFT - CHART_RIGHT;
  const chartHeight = SVG_HEIGHT - CHART_TOP - CHART_BOTTOM;
  const xForDate = (date: string): number =>
    CHART_LEFT + ((dateNumber(date) - dateNumber(minDate)) / dateSpan) * chartWidth;
  const yForValue = (value: number): number => CHART_TOP + chartHeight - (value / 100) * chartHeight;

  const linePath = adjustedForecast.curve_dates
    .map((date, index) => {
      const value = adjustedForecast.curve_values[index] ?? 0;
      return `${index === 0 ? "M" : "L"} ${xForDate(date).toFixed(1)} ${yForValue(value).toFixed(1)}`;
    })
    .join(" ");
  const areaPath = `${linePath} L ${xForDate(maxDate).toFixed(1)} ${(CHART_TOP + chartHeight).toFixed(1)} L ${xForDate(minDate).toFixed(1)} ${(CHART_TOP + chartHeight).toFixed(1)} Z`;

  const keyDates = [
    { id: "start", label: featuredAreaCopy(language).startLabel, date: adjustedForecast.start_date },
    { id: "peak", label: featuredAreaCopy(language).peakLabel, date: adjustedForecast.peak_date },
    { id: "end", label: featuredAreaCopy(language).endLabel, date: adjustedForecast.end_date }
  ];
  const valuesByDate = new Map(
    adjustedForecast.curve_dates.map((date, index) => [date, adjustedForecast.curve_values[index] ?? 0])
  );

  return (
    <svg
      aria-label={featuredAreaCopy(language).chartTitle}
      className="featured-area-chart"
      role="img"
      viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
    >
      <defs>
        <linearGradient id="featured-area-curve-fill" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="rgba(132, 111, 240, 0.36)" />
          <stop offset="100%" stopColor="rgba(132, 111, 240, 0.06)" />
        </linearGradient>
      </defs>
      <rect className="featured-area-chart-bg" height={SVG_HEIGHT} rx="28" ry="28" width={SVG_WIDTH} x="0" y="0" />
      <line
        className="featured-area-baseline"
        x1={CHART_LEFT}
        x2={SVG_WIDTH - CHART_RIGHT}
        y1={CHART_TOP + chartHeight}
        y2={CHART_TOP + chartHeight}
      />
      <path className="featured-area-area-fill" d={areaPath} />
      <path className="featured-area-line" d={linePath} />

      {keyDates.map((item) => {
        const value = valuesByDate.get(item.date) ?? (item.id === "peak" ? 100 : 10);
        const x = xForDate(item.date);
        const y = yForValue(value);
        return (
          <g className={`featured-area-curve-marker ${item.id}`} key={item.id}>
            <circle className="featured-area-point" cx={x} cy={y} r="8.5" />
            <line className="featured-area-marker-stem" x1={x} x2={x} y1={y + 12} y2={CHART_TOP + chartHeight + 14} />
            <text className="featured-area-marker-label" x={x} y={y - (item.id === "peak" ? 18 : 14)}>
              {item.label}
            </text>
            <text className="featured-area-marker-date" x={x} y={CHART_TOP + chartHeight + 36}>
              {formatFeaturedDate(language, item.date)}
            </text>
          </g>
        );
      })}

      {weatherDays.map((day) => {
        const x = xForDate(day.date);
        return (
          <g className="featured-area-curve-weather" key={day.date} transform={`translate(${x - 9}, ${SVG_HEIGHT - ICON_ROW_BOTTOM - 16})`}>
            <WeatherIcon code={day.weather_code} className="featured-area-chart-icon" size={18} />
            <text className="featured-area-curve-weather-date" x="10" y="32">
              {formatFeaturedWeekday(language, day.date)}
            </text>
          </g>
        );
      })}
    </svg>
  );
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
  trees
}: FeaturedAreaPanelProps): JSX.Element {
  const copy = featuredAreaCopy(language);
  const meta = featuredAreaMeta(language, area.id);
  const adjustedForecast = useMemo(
    () => applyWeatherAdjustmentToForecast(area.id, area.bloom_forecast, weather),
    [area, weather]
  );
  const weatherDays = useMemo(() => futureWeatherDays(weather), [weather]);

  const inventoryGroups = useMemo(() => {
    const groups = new Map<
      SpeciesGroup,
      { count: number; variants: Map<string, number> }
    >();

    trees.forEach((tree) => {
      const group = tree.properties.species_group;
      const existing = groups.get(group) ?? { count: 0, variants: new Map<string, number>() };
      existing.count += 1;
      const variant = inventoryVariantLabel(tree);
      existing.variants.set(variant, (existing.variants.get(variant) ?? 0) + 1);
      groups.set(group, existing);
    });

    return Array.from(groups.entries())
      .map<InventoryGroupSummary>(([group, value]) => ({
        group,
        count: value.count,
        variants: Array.from(value.variants.entries())
          .map(([label, count]) => ({ label, count }))
          .sort((left, right) => right.count - left.count || left.label.localeCompare(right.label))
      }))
      .sort((left, right) => right.count - left.count);
  }, [trees]);

  const inventoryCoverageNote = featuredAreaInventoryCoverageNote(
    language,
    area.inventory_summary?.official_pdf_tree_count ?? null,
    area.inventory_summary?.mapped_tree_count ?? trees.length
  );
  const notes = [
    inventoryCoverageNote,
    describeWeatherAdjustment(language, adjustedForecast.weather_adjustment_days),
    ...area.confidence_note_ids
      .map((noteId) => featuredAreaConfidenceNote(language, noteId))
      .filter((note): note is string => Boolean(note))
  ];
  const weatherMin = weatherDays.reduce((min, day) => Math.min(min, day.temperature_min_c), Number.POSITIVE_INFINITY);
  const weatherMax = weatherDays.reduce((max, day) => Math.max(max, day.temperature_max_c), Number.NEGATIVE_INFINITY);
  const weatherRangeSpan = Math.max(1, weatherMax - weatherMin);

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

      <section className="featured-area-section featured-area-forecast-shell">
        <div className="featured-area-forecast-header">
          <div>
            <h4>{copy.chartTitle}</h4>
            <p>{describeWeatherAdjustment(language, adjustedForecast.weather_adjustment_days)}</p>
          </div>
          <div className="featured-area-updated">
            {copy.updatedAt}: {new Date(adjustedForecast.updated_at).toLocaleDateString(language)}
          </div>
        </div>
        <div className="featured-area-metrics">
          {metricChip(copy.startLabel, formatFeaturedDate(language, adjustedForecast.start_date))}
          {metricChip(copy.peakLabel, formatFeaturedDate(language, adjustedForecast.peak_date))}
          {metricChip(copy.endLabel, formatFeaturedDate(language, adjustedForecast.end_date))}
        </div>
        <ForecastCurve areaId={area.id} forecast={area.bloom_forecast} language={language} weather={weather} />
      </section>

      <section className="featured-area-section featured-area-weather-shell">
        <div className="featured-area-section-head">
          <h4>{copy.weatherTitle}</h4>
        </div>
        {weatherLoading ? <p className="featured-area-section-copy">{copy.weatherLoading}</p> : null}
        {!weatherLoading && weatherError ? <p className="featured-area-section-copy">{copy.weatherUnavailable}</p> : null}
        {!weatherLoading && !weatherError && weatherDays.length > 0 ? (
          <div className="featured-area-weather-list">
            {weatherDays.map((day) => {
              const left = ((day.temperature_min_c - weatherMin) / weatherRangeSpan) * 100;
              const width = ((day.temperature_max_c - day.temperature_min_c) / weatherRangeSpan) * 100;
              return (
                <div className="featured-area-weather-row" key={day.date}>
                  <div className="featured-area-weather-day">
                    <strong>{formatFeaturedWeekday(language, day.date)}</strong>
                    <span>{formatFeaturedDate(language, day.date)}</span>
                  </div>
                  <div className="featured-area-weather-icon-col">
                    <WeatherIcon code={day.weather_code} className="featured-area-weather-icon" size={20} />
                    <span>{featuredAreaWeatherLabel(language, day.weather_code)}</span>
                  </div>
                  <div className="featured-area-weather-rain">
                    {day.precipitation_probability_max == null ? "--" : `${Math.round(day.precipitation_probability_max)}%`}
                    <span>{copy.rainChanceShort}</span>
                  </div>
                  <div className="featured-area-weather-temp-min">{Math.round(day.temperature_min_c)}°</div>
                  <div className="featured-area-weather-track" aria-label={copy.tempRangeLabel}>
                    <div className="featured-area-weather-range" style={{ left: `${left}%`, width: `${Math.max(width, 10)}%` }} />
                  </div>
                  <div className="featured-area-weather-temp-max">{Math.round(day.temperature_max_c)}°</div>
                </div>
              );
            })}
          </div>
        ) : null}
      </section>

      <section className="featured-area-section featured-area-tree-summary">
        <div className="featured-area-section-head">
          <h4>{copy.treesTitle}</h4>
        </div>
        <div className="featured-area-tree-summary-meta">
          <div className="featured-area-summary-stat">
            <span>{copy.mappedTreesLabel}</span>
            <strong>{(area.inventory_summary?.mapped_tree_count ?? trees.length).toLocaleString(language)}</strong>
          </div>
          {area.inventory_summary?.official_pdf_tree_count ? (
            <div className="featured-area-summary-stat">
              <span>{copy.officialMapTreesLabel}</span>
              <strong>{area.inventory_summary.official_pdf_tree_count.toLocaleString(language)}</strong>
            </div>
          ) : null}
        </div>
        {trees.length === 0 ? (
          <p className="featured-area-section-copy">{copy.treesLoading}</p>
        ) : (
          <div className="featured-area-inventory-groups">
            {inventoryGroups.map((group) => (
              <div className="featured-area-inventory-card" key={group.group}>
                <div className="featured-area-inventory-head">
                  <strong>{speciesLabel(language, group.group)}</strong>
                  <span>{group.count.toLocaleString(language)}</span>
                </div>
                <div className="featured-area-inventory-variants">
                  {group.variants.map((variant) => (
                    <span className="featured-area-inventory-chip" key={`${group.group}-${variant.label}`}>
                      {variant.label} <strong>{variant.count}</strong>
                    </span>
                  ))}
                </div>
              </div>
            ))}
            {area.inventory_summary?.official_pdf_buckets?.length ? (
              <div className="featured-area-inventory-card official">
                <div className="featured-area-inventory-head">
                  <strong>{copy.officialMapTreesLabel}</strong>
                  <span>{area.inventory_summary.official_pdf_tree_count?.toLocaleString(language) ?? "--"}</span>
                </div>
                <div className="featured-area-inventory-variants">
                  {area.inventory_summary.official_pdf_buckets.map((bucket) => (
                    <span className="featured-area-inventory-chip subtle" key={bucket.id}>
                      {bucket.label} <strong>{bucket.tree_count}</strong>
                    </span>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        )}
      </section>

      <section className="featured-area-section featured-area-confidence">
        <div className="featured-area-section-head">
          <h4>{copy.confidenceTitle}</h4>
        </div>
        <ul>
          {notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </section>

      <section className="featured-area-section featured-area-sources">
        <div className="featured-area-section-head">
          <h4>{copy.sourcesTitle}</h4>
        </div>
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
