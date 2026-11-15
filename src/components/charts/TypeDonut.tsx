import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { Derived } from "../../lib/aggregate";
import { fmtInt, fmtPct } from "../../lib/format";
import { AMBER, RED } from "../../lib/palette";
import { ChartCard, EmptyState } from "../ui";

const COLORS = [RED, AMBER];

function DonutTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const item = payload[0];
  return (
    <div className="tooltip">
      <p className="tooltip-title">{item.name}</p>
      <ul>
        <li>
          <span className="tooltip-dot" style={{ background: item.payload.fill ?? COLORS[0] }} />
          <span>Títulos</span>
          <strong>{fmtInt(Number(item.value))}</strong>
        </li>
      </ul>
    </div>
  );
}

export function TypeDonut({ derived }: { derived: Derived }) {
  const total = derived.count;

  return (
    <ChartCard
      title="Películas vs. series"
      subtitle="Composición del catálogo filtrado: cuánto es película y cuánto es serie."
      help={[
        "La dona divide el total de títulos en dos categorías: películas y series. El centro muestra el total del filtro actual.",
        "Los porcentajes se calculan sobre el total filtrado, no sobre el catálogo completo. Si aplicas un filtro, la composición cambia.",
        "El color rojo representa películas y el dorado, series, igual que en el resto del tablero.",
        "Cuidado: una serie cuenta como un título, aunque tenga varias temporadas. No se pondera por episodios ni por horas vistas.",
      ]}
      legend={
        <ul className="donut-legend">
          {derived.typeCounts.map((item, i) => (
            <li key={item.type}>
              <span className="legend-swatch square" style={{ background: COLORS[i] }} aria-hidden="true" />
              <span>{item.type}</span>
              <strong>{fmtInt(item.count)}</strong>
              <span className="muted">{fmtPct(item.share)}</span>
            </li>
          ))}
        </ul>
      }
      axis="Sin ejes: cada porción representa la participación de un tipo de contenido sobre el total filtrado."
      note="Un título = una fila del catálogo. Las series no se expanden por temporadas."
    >
      {total === 0 ? (
        <EmptyState message="No hay títulos para el filtro actual." />
      ) : (
        <div className="donut-wrap">
          <ResponsiveContainer width="100%" height={290}>
            <PieChart>
              <Pie
                data={derived.typeCounts}
                dataKey="count"
                nameKey="type"
                cx="50%"
                cy="50%"
                innerRadius={82}
                outerRadius={120}
                paddingAngle={2}
                startAngle={90}
                endAngle={-270}
                stroke="none"
              >
                {derived.typeCounts.map((entry, i) => (
                  <Cell key={entry.type} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip content={<DonutTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="donut-center" aria-hidden="true">
            <strong>{fmtInt(total)}</strong>
            <span>títulos</span>
          </div>
        </div>
      )}
    </ChartCard>
  );
}
