import type { DashboardData } from "../types";
import type { Derived } from "../lib/aggregate";
import { fmtInt, fmtPct } from "../lib/format";
import { useCountUp, useInView } from "../hooks/useUi";

function Kpi({
  label,
  value,
  unit,
  note,
  accent,
  animate = true,
  isYear = false,
  start,
  delay = 0,
}: {
  label: string;
  value: number;
  unit?: string;
  note: string;
  accent: "red" | "gold" | "grey";
  animate?: boolean;
  isYear?: boolean;
  start: boolean;
  delay?: number;
}) {
  const counted = useCountUp(value, 820, start);
  const shown = animate ? counted : value;
  const display = isYear ? String(Math.round(shown)) : fmtInt(Math.round(shown));

  return (
    <article className={`kpi-card kpi-${accent}`} style={{ animationDelay: `${delay}ms` }}>
      <span className="kpi-label">{label}</span>
      <p className="kpi-value">
        <strong>{display}</strong>
        {unit ? <span className="kpi-unit">{unit}</span> : null}
      </p>
      <p className="kpi-note">{note}</p>
      <span className="kpi-bar" aria-hidden="true" />
    </article>
  );
}

export function KpiGrid({ data, derived }: { data: DashboardData; derived: Derived }) {
  const { ref, inView } = useInView<HTMLDivElement>(0.05);
  const total = data.meta.total_titulos;
  const catalogShare = total ? (100 * derived.count) / total : 0;
  const movieShare = derived.count ? (100 * derived.movies) / derived.count : 0;
  const seriesShare = derived.count ? (100 * derived.series) / derived.count : 0;
  const leader = derived.topCountries[0];
  const peak = derived.peakRelease;

  return (
    <div className="kpi-grid" ref={ref}>
      <Kpi
        label="Títulos en el filtro"
        value={derived.count}
        note={`${fmtPct(catalogShare)} del catálogo completo (${fmtInt(total)})`}
        accent="red"
        start={inView}
        delay={0}
      />
      <Kpi
        label="Películas"
        value={derived.movies}
        note={`${fmtPct(movieShare)} del filtro actual`}
        accent="red"
        start={inView}
        delay={60}
      />
      <Kpi
        label="Series"
        value={derived.series}
        note={`${fmtPct(seriesShare)} del filtro actual`}
        accent="gold"
        start={inView}
        delay={120}
      />
      <Kpi
        label="Países productores"
        value={derived.countryCount}
        note={leader ? `Lidera ${leader.label} con ${fmtInt(leader.count)} títulos` : "Sin países declarados en el filtro"}
        accent="grey"
        start={inView}
        delay={180}
      />
      <Kpi
        label="Año con más estrenos"
        value={peak?.year ?? 0}
        note={peak ? `${fmtInt(peak.count)} títulos estrenados ese año` : "Sin datos para el filtro"}
        accent="red"
        animate={false}
        isYear
        start={inView}
        delay={240}
      />
      <Kpi
        label="Duración mediana"
        value={derived.movieDuration.median}
        unit="min"
        note={`${fmtInt(derived.movieDuration.n)} películas con duración válida`}
        accent="gold"
        start={inView}
        delay={300}
      />
    </div>
  );
}
