import { Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Derived } from "../../lib/aggregate";
import { fmtInt, fmtPct } from "../../lib/format";
import { AXIS, GRID, INK, RED, UNKNOWN } from "../../lib/palette";
import { ChartCard, EmptyState } from "../ui";

function RatingTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const item = payload[0]?.payload;
  if (!item) return null;
  return (
    <div className="tooltip">
      <p className="tooltip-title">{item.name}</p>
      <ul>
        <li>
          <span className="tooltip-dot" style={{ background: item.name === "Sin dato" ? UNKNOWN : RED }} />
          <span>Títulos</span>
          <strong>{fmtInt(item.count)}</strong>
        </li>
        <li>
          <span>% del filtro</span>
          <strong>{fmtPct(item.share)}</strong>
        </li>
      </ul>
    </div>
  );
}

export function RatingsChart({ derived }: { derived: Derived }) {
  const data = derived.byRating.filter((r) => r.count > 0);

  return (
    <ChartCard
      title="Distribución de clasificaciones (rating)"
      subtitle="Cómo se reparten los títulos según la clasificación por edad que registra el dataset."
      help={[
        "Cada barra cuenta los títulos con esa clasificación. TV-MA agrupa contenido para adultos; TV-Y y TV-Y7, contenido infantil; PG, PG-13, R y NC-17 son clasificaciones de cine.",
        "La clasificación es la que declara el dataset, no una evaluación de calidad ni de popularidad. Un rating frecuente no significa que sea “mejor”.",
        "“Sin dato” incluye 7 títulos sin clasificación después de corregir tres filas donde la duración estaba en el campo rating. NR y UR se mantienen separados porque no son equivalentes.",
        "Cuidado: las etiquetas de TV y de cine no son intercambiables; el gráfico las muestra juntas solo para describir el catálogo.",
      ]}
      axis="Eje X: número de títulos · Eje Y: clasificación. “Sin dato” se muestra en gris."
      note={
        derived.topRating
          ? `La clasificación más frecuente del filtro es ${derived.topRating.name}, con ${fmtInt(derived.topRating.count)} títulos (${fmtPct(derived.topRating.share)}).`
          : "No hay clasificaciones para el filtro actual."
      }
    >
      {data.length === 0 ? (
        <EmptyState message="No hay clasificaciones para el filtro actual." />
      ) : (
        <div className="chart-frame">
          <ResponsiveContainer width="100%" height={Math.max(260, data.length * 30 + 30)}>
            <BarChart data={data} layout="vertical" margin={{ top: 4, right: 50, left: 0, bottom: 4 }} barCategoryGap={5}>
              <CartesianGrid horizontal={false} stroke={GRID} />
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="name"
                width={72}
                tick={{ fill: AXIS, fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<RatingTooltip />} cursor={{ fill: "#f3eee6" }} />
              <Bar dataKey="count" radius={[0, 3, 3, 0]} barSize={13}>
                {data.map((item) => (
                  <Cell key={item.name} fill={item.name === "Sin dato" ? UNKNOWN : RED} />
                ))}
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
