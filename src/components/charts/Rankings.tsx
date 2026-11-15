import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Derived } from "../../lib/aggregate";
import { fmtInt, fmtPct } from "../../lib/format";
import { AXIS, GRID, INK, RED } from "../../lib/palette";
import { ChartCard, EmptyState } from "../ui";

function RankTooltip({ active, payload, suffix }: any) {
  if (!active || !payload?.length) return null;
  const item = payload[0]?.payload;
  if (!item) return null;
  return (
    <div className="tooltip">
      <p className="tooltip-title">{item.label}</p>
      <ul>
        <li>
          <span className="tooltip-dot" style={{ background: payload[0].color }} />
          <span>{suffix}</span>
          <strong>{fmtInt(item.count)}</strong>
        </li>
        <li>
          <span>% del filtro</span>
          <strong>{fmtPct(item.share)}</strong>
        </li>
      </ul>
      {item.avgDuration ? <p className="tooltip-hint">Duración media de películas: {Math.round(item.avgDuration)} min</p> : null}
    </div>
  );
}

function truncate(label: string, max = 17): string {
  return label.length > max ? `${label.slice(0, max - 1)}…` : label;
}

export function TopCountriesChart({
  derived,
  onSelectCountry,
}: {
  derived: Derived;
  onSelectCountry: (index: number) => void;
}) {
  const data = derived.topCountries.slice(0, 10);

  return (
    <ChartCard
      title="Top 10 países por títulos"
      subtitle="Ranking de producción declarada. Un título puede sumar en más de un país."
      help={[
        "La barra muestra cuántos títulos declaran ese país. El ranking usa la tabla puente título–país: si un título tiene tres países, suma en los tres.",
        "Los títulos sin país (9.44% del catálogo completo) se excluyen del ranking, pero sí cuentan en los totales y en la dona.",
        "Haz clic en una barra para filtrar el tablero por ese país. El botón “Limpiar” vuelve al panorama general.",
        "Cuidado: producir no es lo mismo que estar disponible. El dataset no dice en qué países se ve cada título, solo qué país se declara como productor.",
      ]}
      axis="Eje X: número de títulos · Eje Y: país. El porcentaje se calcula sobre el total del filtro actual."
      note="La suma del ranking no coincide con el total de títulos: los países son multivaluados."
    >
      {data.length === 0 ? (
        <EmptyState message="No hay países para el filtro actual." />
      ) : (
        <>
          <div className="chart-frame">
            <ResponsiveContainer width="100%" height={Math.max(260, data.length * 32 + 30)}>
              <BarChart data={data} layout="vertical" margin={{ top: 4, right: 52, left: 0, bottom: 4 }} barCategoryGap={6}>
                <CartesianGrid horizontal={false} stroke={GRID} />
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="label"
                  width={128}
                  tickFormatter={(value: string) => truncate(value)}
                  tick={{ fill: AXIS, fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip content={<RankTooltip suffix="Títulos" />} cursor={{ fill: "#f3eee6" }} />
                <Bar
                  dataKey="count"
                  fill={RED}
                  radius={[0, 3, 3, 0]}
                  barSize={15}
                  onClick={(_: unknown, index: number) => {
                    const item = data[index];
                    if (item) onSelectCountry(item.index);
                  }}
                  className="clickable-bar"
                >
                  <LabelList
                    dataKey="count"
                    position="right"
                    formatter={(value: unknown) => fmtInt(Number(value))}
                    fill={INK}
                    fontSize={11}
                  />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <details className="table-alt">
            <summary>Ver ranking accesible (botones)</summary>
            <ol>
              {data.map((item) => (
                <li key={item.name}>
                  <button type="button" onClick={() => onSelectCountry(item.index)}>
                    <span>{item.label}</span>
                    <strong>{fmtInt(item.count)}</strong>
                    <span className="muted">{fmtPct(item.share)}</span>
                  </button>
                </li>
              ))}
            </ol>
          </details>
        </>
      )}
    </ChartCard>
  );
}

export function TopGenresChart({ derived }: { derived: Derived }) {
  const data = derived.topGenres.slice(0, 10);

  return (
    <ChartCard
      title="Top 10 géneros"
      subtitle="Los géneros más frecuentes del filtro actual. Un título puede tener hasta tres."
      help={[
        "La barra muestra en cuántos títulos aparece cada género. Un título con “Dramas, Comedias” suma en ambos.",
        "Por eso los porcentajes usan el total de títulos como denominador y la suma de todos los géneros supera 100%. No es un error: es la naturaleza multivaluada del campo listed_in.",
        "Los nombres se muestran en español; el valor original en inglés se conserva en la base de datos para trazabilidad.",
        "Cuidado: “Películas internacionales” es una etiqueta comercial amplia, no un género narrativo. Úsala como categoría del catálogo, no como gusto de la audiencia.",
      ]}
      axis="Eje X: número de títulos que incluyen el género · Eje Y: género (etiqueta en español)."
      note="42 géneros distintos en el dataset. La nube de palabras muestra el panorama completo; este ranking, los diez primeros."
    >
      {data.length === 0 ? (
        <EmptyState message="No hay géneros para el filtro actual." />
      ) : (
        <div className="chart-frame">
          <ResponsiveContainer width="100%" height={Math.max(260, data.length * 32 + 30)}>
            <BarChart data={data} layout="vertical" margin={{ top: 4, right: 52, left: 0, bottom: 4 }} barCategoryGap={6}>
              <CartesianGrid horizontal={false} stroke={GRID} />
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="label"
                width={172}
                tickFormatter={(value: string) => truncate(value, 24)}
                tick={{ fill: AXIS, fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<RankTooltip suffix="Títulos" />} cursor={{ fill: "#f3eee6" }} />
              <Bar dataKey="count" fill={RED} radius={[0, 3, 3, 0]} barSize={15}>
                <LabelList
                  dataKey="count"
                  position="right"
                  formatter={(value: unknown) => fmtInt(Number(value))}
                  fill={INK}
                  fontSize={11}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </ChartCard>
  );
}
