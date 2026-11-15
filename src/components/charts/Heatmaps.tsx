import { useMemo, useRef, useState } from "react";
import type { Derived } from "../../lib/aggregate";
import { fmtInt, fmtPct, monthName, signedPct } from "../../lib/format";
import { ChartCard } from "../ui";

function mixColor(value: number, max: number): { bg: string; fg: string } {
  if (value <= 0) return { bg: "#f1ece3", fg: "#8a857c" };
  const t = Math.min(1, Math.sqrt(value / Math.max(1, max)));
  const from = [249, 236, 233];
  const to = [217, 4, 41];
  const c = from.map((v, i) => Math.round(v + (to[i] - v) * t));
  return { bg: `rgb(${c[0]}, ${c[1]}, ${c[2]})`, fg: t > 0.58 ? "#ffffff" : "#171717" };
}

function Heatmap({
  rows,
  cols,
  values,
  tooltip,
  ariaLabel,
  minWidth = 620,
}: {
  rows: string[];
  cols: string[];
  values: number[][];
  tooltip: (row: string, col: string, value: number) => string;
  ariaLabel: string;
  minWidth?: number;
}) {
  const [tip, setTip] = useState<{ x: number; y: number; text: string } | null>(null);
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const max = useMemo(() => Math.max(1, ...values.flat()), [values]);

  const show = (event: React.MouseEvent, text: string) => {
    const rect = wrapRef.current?.getBoundingClientRect();
    if (!rect) return;
    setTip({
      x: Math.max(8, Math.min(rect.width - 230, event.clientX - rect.left + 12)),
      y: Math.max(8, event.clientY - rect.top + 12),
      text,
    });
  };

  return (
    <div className="heat-wrap" ref={wrapRef}>
      <div
        className="heatmap"
        role="grid"
        aria-label={ariaLabel}
        style={{ gridTemplateColumns: `minmax(118px, 170px) repeat(${cols.length}, minmax(34px, 1fr))`, minWidth }}
      >
        <span className="heat-corner" aria-hidden="true" />
        {cols.map((col) => (
          <span key={col} className="heat-col" role="columnheader">
            {col}
          </span>
        ))}
        {rows.map((row, ri) => (
          <div className="heat-row-group" role="row" key={row}>
            <span className="heat-row" role="rowheader">
              {row}
            </span>
            {cols.map((col, ci) => {
              const value = values[ri][ci];
              const text = tooltip(row, col, value);
              const tone = mixColor(value, max);
              return (
                <span
                  key={`${row}-${col}`}
                  className="heat-cell"
                  role="gridcell"
                  tabIndex={-1}
                  aria-label={text}
                  style={{ background: tone.bg, color: tone.fg }}
                  onMouseEnter={(e) => show(e, text)}
                  onMouseMove={(e) => show(e, text)}
                  onMouseLeave={() => setTip(null)}
                  onClick={(e) => show(e, text)}
                >
                  {value > 0 ? fmtInt(value) : ""}
                </span>
              );
            })}
          </div>
        ))}
      </div>
      {tip ? (
        <div className="heat-tooltip" style={{ left: tip.x, top: tip.y }} role="status">
          {tip.text}
        </div>
      ) : null}
    </div>
  );
}

export function DecadeGenreHeatmap({ derived }: { derived: Derived }) {
  const decades = derived.byDecade.filter((d) => d.total > 0).map((d) => d.decade);
  const genres = derived.topGenres.slice(0, 10).map((g) => g.label).concat("Otros géneros");
  const lookup = new Map(derived.decadeGenre.map((d) => [`${d.decade}|${d.label}`, d.count]));
  const values = genres.map((g) => decades.map((decade) => lookup.get(`${decade}|${g}`) ?? 0));

  return (
    <ChartCard
      title="Década × género"
      subtitle="Qué géneros dominan en cada década de estreno. Una celda más roja concentra más títulos."
      help={[
        "Cada fila es un género y cada columna una década de estreno. El color y el número indican cuántos títulos de ese género se estrenaron en esa década.",
        "Como un título puede tener varios géneros, la suma de una fila o de una columna supera el número de títulos. No leas los totales como si fueran exclusivos.",
        "La escala de color es relativa al máximo de la matriz y usa raíz cuadrada para que las celdas pequeñas no desaparezcan.",
        "Cuidado: la década de 2020 solo incluye 2020 y 2021 (hasta el 25 de septiembre); no es una década completa.",
      ]}
      axis="Columnas: década de estreno · Filas: género (top 10 + resto agrupado). Color y cifra = títulos."
      note="La columna “Otros géneros” agrupa los 32 géneros fuera del top 10. No se pierde ningún título."
    >
      <div className="heat-scroll" tabIndex={0} role="region" aria-label="Matriz de géneros por década">
        <Heatmap
          rows={genres}
          cols={decades.map((d) => String(d))}
          values={values}
          ariaLabel="Matriz de cantidad de títulos por género y década"
          tooltip={(genre, decade, value) =>
            `${genre} · década de ${decade}: ${fmtInt(value)} título${value === 1 ? "" : "s"}`
          }
        />
      </div>
      <p className="scroll-hint">Desliza horizontalmente si la matriz no cabe en pantalla →</p>
    </ChartCard>
  );
}

export function YearMonthHeatmap({ derived }: { derived: Derived }) {
  const years = Array.from(new Set(derived.yearMonth.map((d) => d.year)));
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  const lookup = new Map(derived.yearMonth.map((d) => [`${d.year}|${d.month}`, d.count]));
  const values = years.map((y) => months.map((m) => lookup.get(`${y}|${m}`) ?? 0));

  return (
    <ChartCard
      title="Año × mes de incorporación"
      subtitle="Cuándo llegaron los títulos al catálogo, mes a mes. Sirve para ver estacionalidad y picos de carga."
      help={[
        "Cada fila es un año de incorporación y cada columna un mes. El color y la cifra muestran cuántos títulos entraron ese mes.",
        "Un patrón recurrente (por ejemplo, más altas a mitad de año) puede reflejar la estrategia de lanzamientos de Netflix, pero el dataset no explica la causa.",
        "2021 solo llega al 25 de septiembre: septiembre está incompleto y los meses de octubre a diciembre aparecen vacíos porque no existen en el snapshot.",
        "Cuidado: esto mide incorporaciones al catálogo, no estrenos. Un título producido en 2010 puede haberse incorporado en 2020.",
      ]}
      axis="Columnas: mes · Filas: año de incorporación. Color y cifra = títulos añadidos."
      note="Solo se incluyen los 8.797 títulos con fecha de incorporación válida; 10 no la declaran."
    >
      <div className="heat-scroll" tabIndex={0} role="region" aria-label="Matriz de incorporaciones por año y mes">
        <Heatmap
          rows={years.map(String)}
          cols={months.map((m) => monthName(m).slice(0, 3))}
          values={values}
          minWidth={680}
          ariaLabel="Matriz de incorporaciones por año y mes"
          tooltip={(year, month, value) =>
            `${month} de ${year}: ${fmtInt(value)} título${value === 1 ? "" : "s"} incorporado${value === 1 ? "" : "s"}`
          }
        />
      </div>
      <p className="scroll-hint">Desliza horizontalmente si la matriz no cabe en pantalla →</p>
    </ChartCard>
  );
}

export function DecadeVariationChart({ derived }: { derived: Derived }) {
  const rows = derived.byDecade.filter((d) => d.total > 0);
  const max = Math.max(1, ...rows.map((d) => d.total));

  return (
    <ChartCard
      title="Títulos por década y variación"
      subtitle="Cuántos títulos del filtro se estrenaron en cada década y cómo cambió respecto a la anterior."
      help={[
        "La barra representa el total de títulos estrenados en esa década. El porcentaje compara con la década inmediatamente anterior.",
        "La variación solo se calcula si la década anterior tiene títulos. Si no hay base, aparece “—”: no se inventa un porcentaje.",
        "La década de 2020 está incompleta (2020–2021) y su caída no significa un cambio real de tendencia.",
        "Cuidado: el catálogo no es una muestra de toda la producción mundial; es lo que Netflix tiene disponible en el snapshot.",
      ]}
      axis="Barras: títulos por década de estreno. Etiqueta derecha: variación porcentual vs. la década previa."
      note="La suma de las barras coincide con el total del filtro. La variación se calcula con los totales reales, sin suavizado."
    >
      <ul className="decade-list">
        {rows.map((row) => (
          <li key={row.decade}>
            <span className="decade-label">{row.decade}</span>
            <span className="decade-bar" aria-hidden="true">
              <i style={{ width: `${(100 * row.total) / max}%` }} />
            </span>
            <strong>{fmtInt(row.total)}</strong>
            <span className={row.variation === null ? "muted" : row.variation >= 0 ? "delta up" : "delta down"}>
              {signedPct(row.variation)}
            </span>
            {row.partial ? <span className="partial-tag">parcial</span> : null}
          </li>
        ))}
      </ul>
      <p className="chart-footnote">
        Participación de la década más reciente completa (2010):{" "}
        {fmtPct(
          (100 * (derived.byDecade.find((d) => d.decade === 2010)?.total ?? 0)) / Math.max(1, derived.count),
        )}{" "}
        del filtro.
      </p>
    </ChartCard>
  );
}
