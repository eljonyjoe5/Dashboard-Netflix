import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Derived } from "../../lib/aggregate";
import { fmtInt } from "../../lib/format";
import { AMBER, AXIS, GRID, RED } from "../../lib/palette";
import { ChartCard, Legend, Segmented } from "../ui";

type Mode = "release" | "added";

function TimeTooltip({ active, payload, label, mode }: any) {
  if (!active || !payload?.length) return null;
  const total = payload.reduce((sum: number, p: any) => sum + (Number(p.value) || 0), 0);
  return (
    <div className="tooltip">
      <p className="tooltip-title">
        {mode === "release" ? "Estreno" : "Incorporación"}: {label}
      </p>
      <ul>
        {payload.map((p: any) => (
          <li key={p.dataKey}>
            <span className="tooltip-dot" style={{ background: p.color }} />
            <span>{p.name}</span>
            <strong>{fmtInt(Number(p.value) || 0)}</strong>
          </li>
        ))}
        <li className="tooltip-total">
          <span>Total</span>
          <strong>{fmtInt(total)}</strong>
        </li>
      </ul>
    </div>
  );
}

export function TimeSeriesChart({ derived, snapshotYear }: { derived: Derived; snapshotYear: number }) {
  const [mode, setMode] = useState<Mode>("release");
  const [fullHistory, setFullHistory] = useState(false);

  const releaseData = fullHistory
    ? derived.byYearRelease
    : derived.byYearRelease.filter((d) => d.year >= 1990);
  const data = mode === "release" ? releaseData : derived.byYearAdded;
  const peak = mode === "release" ? derived.peakRelease : derived.peakAdded;

  return (
    <ChartCard
      title="Estrenos e incorporaciones por año"
      subtitle="La misma línea de tiempo contada de dos maneras: cuándo se produjo cada título y cuándo llegó al catálogo."
      help={[
        "Las barras apiladas suman películas (rojo) y series (dorado) por año. La altura total es el número de títulos de ese año.",
        "El selector cambia el eje temporal: “Año de estreno” usa release_year (cuándo se produjo el título); “Año de incorporación” usa date_added (cuándo entró al catálogo de Netflix). No son lo mismo y no deben mezclarse.",
        "La línea punteada marca el corte del snapshot (25 de septiembre de 2021). 2021 está incompleto: la caída del último año no significa que el catálogo haya dejado de crecer.",
        "Cuidado: el filtro de periodo selecciona títulos por año de estreno. Si cambias a “incorporación”, ves cuándo llegaron al catálogo esos mismos títulos, no todos los añadidos del periodo.",
      ]}
      legend={
        <Legend
          items={[
            { color: RED, label: "Películas" },
            { color: AMBER, label: "Series" },
          ]}
        />
      }
      axis={
        mode === "release"
          ? "Eje X: año de estreno · Eje Y: número de títulos. Los años sin títulos aparecen en cero; no se interpolan."
          : "Eje X: año de incorporación al catálogo · Eje Y: número de títulos incorporados."
      }
      note="Un título se cuenta una sola vez por año. La serie por incorporación solo incluye títulos con fecha válida (8.797 de 8.807)."
      actions={
        <div className="chart-actions">
          <Segmented
            ariaLabel="Elegir eje temporal"
            value={mode}
            onChange={setMode}
            options={[
              { value: "release", label: "Año de estreno" },
              { value: "added", label: "Año de incorporación" },
            ]}
          />
          {mode === "release" ? (
            <button type="button" className="text-btn" onClick={() => setFullHistory((v) => !v)}>
              {fullHistory ? "Ver desde 1990" : "Ver todo el histórico"}
            </button>
          ) : null}
        </div>
      }
    >
      <div className="chart-summary">
        {peak ? (
          <p>
            <span className="mini-label">Año pico</span>
            <strong>{peak.year}</strong>
            <span>{fmtInt(peak.count)} títulos</span>
          </p>
        ) : (
          <p className="muted">No hay datos para el filtro actual.</p>
        )}
        <p>
          <span className="mini-label">Corte del snapshot</span>
          <strong>25 sep 2021</strong>
          <span>último día con datos</span>
        </p>
      </div>

      <div className="chart-frame">
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }} barCategoryGap="12%">
            <CartesianGrid stroke={GRID} vertical={false} />
            <XAxis
              dataKey="year"
              tick={{ fill: AXIS, fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: GRID }}
              minTickGap={18}
              interval={mode === "release" && fullHistory ? 9 : "preserveStartEnd"}
            />
            <YAxis
              tick={{ fill: AXIS, fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              width={44}
              allowDecimals={false}
            />
            <Tooltip content={<TimeTooltip mode={mode} />} cursor={{ fill: "#f3eee6" }} />
            <ReferenceLine
              x={snapshotYear}
              stroke={AMBER}
              strokeDasharray="4 4"
              label={{ value: "corte", fill: AMBER, fontSize: 10, position: "insideTopRight" }}
            />
            <Bar dataKey="movies" name="Películas" stackId="a" fill={RED} />
            <Bar dataKey="series" name="Series" stackId="a" fill={AMBER} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="chart-footnote">
        {mode === "release"
          ? `Mostrando ${releaseData.length} años${fullHistory ? " (1925–2021)" : " (1990–2021)"}.`
          : "Serie completa de incorporaciones: 2008–2021."}{" "}
        {mode === "added"
          ? "2021 incluye solo hasta el 25 de septiembre."
          : "El corte también afecta a 2021: los estrenos posteriores al 25 de septiembre no están en el snapshot."}
      </p>
    </ChartCard>
  );
}
