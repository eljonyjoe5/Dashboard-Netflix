import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Derived } from "../../lib/aggregate";
import { fmt1, fmtInt } from "../../lib/format";
import { AMBER, AXIS, GRID, RED } from "../../lib/palette";
import { ChartCard, EmptyState } from "../ui";

function MiniTooltip({ active, payload, label, unit }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="tooltip">
      <p className="tooltip-title">
        {label} {unit}
      </p>
      <ul>
        <li>
          <span className="tooltip-dot" style={{ background: payload[0].color }} />
          <span>Títulos</span>
          <strong>{fmtInt(Number(payload[0].value))}</strong>
        </li>
      </ul>
    </div>
  );
}

export function DurationCharts({ derived }: { derived: Derived }) {
  const seasonMax = derived.seasonsDist.filter((s) => s.count > 0).at(-1)?.seasons ?? 0;

  return (
    <ChartCard
      title="¿Cuánto dura el contenido?"
      subtitle="Dos unidades que nunca se mezclan: minutos para películas y temporadas para series."
      help={[
        "La izquierda muestra cuántas películas caen en cada rango de minutos. La derecha muestra cuántas series tienen 1, 2, 3… temporadas.",
        "La mediana es el valor que deja la mitad de los títulos por debajo y la mitad por arriba; es más resistente a casos extremos que el promedio.",
        "No se promedian minutos con temporadas. Son unidades distintas y el tablero las mantiene separadas en todos los cálculos.",
        "Cuidado: una serie de varias temporadas cuenta como un solo título. El dataset no trae número de episodios ni duración por episodio.",
      ]}
      axis="Izquierda: eje X = rango de duración en minutos · eje Y = películas. Derecha: eje X = número de temporadas · eje Y = series."
      note="Las 3 películas con la duración desalineada en el campo rating se recuperaron en el ETL; no queda ninguna película sin minutos."
    >
      {derived.movieDuration.n === 0 && derived.seasons.n === 0 ? (
        <EmptyState message="No hay duraciones para el filtro actual." />
      ) : (
        <div className="split-charts">
          <div className="split-chart">
            <div className="split-head">
              <h4>Películas · minutos</h4>
              <p>
                Mediana <strong>{fmt1(derived.movieDuration.median)} min</strong> · promedio{" "}
                <strong>{fmt1(derived.movieDuration.avg)} min</strong> · n = {fmtInt(derived.movieDuration.n)}
              </p>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={derived.durationHist} margin={{ top: 10, right: 6, left: 0, bottom: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis
                  dataKey="bin"
                  tick={{ fill: AXIS, fontSize: 10 }}
                  tickFormatter={(value: string) => value.replace(" min", "").replace("> 180", ">180")}
                  tickLine={false}
                  axisLine={{ stroke: GRID }}
                  interval={0}
                  angle={-20}
                  textAnchor="end"
                  height={48}
                />
                <YAxis tick={{ fill: AXIS, fontSize: 10 }} tickLine={false} axisLine={false} width={36} allowDecimals={false} />
                <Tooltip content={<MiniTooltip unit="min" />} cursor={{ fill: "#f3eee6" }} />
                <Bar dataKey="count" fill={RED} radius={[3, 3, 0, 0]} barSize={26} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="split-chart">
            <div className="split-head">
              <h4>Series · temporadas</h4>
              <p>
                Mediana <strong>{fmt1(derived.seasons.median)} temporada(s)</strong> · n = {fmtInt(derived.seasons.n)} · máx.{" "}
                {seasonMax}
              </p>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={derived.seasonsDist} margin={{ top: 10, right: 6, left: 0, bottom: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis
                  dataKey="seasons"
                  tick={{ fill: AXIS, fontSize: 10 }}
                  tickLine={false}
                  axisLine={{ stroke: GRID }}
                  interval={1}
                  height={30}
                />
                <YAxis tick={{ fill: AXIS, fontSize: 10 }} tickLine={false} axisLine={false} width={36} allowDecimals={false} />
                <Tooltip content={<MiniTooltip unit="temporada(s)" />} cursor={{ fill: "#f3eee6" }} />
                <Bar dataKey="count" fill={AMBER} radius={[3, 3, 0, 0]} barSize={16} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </ChartCard>
  );
}
