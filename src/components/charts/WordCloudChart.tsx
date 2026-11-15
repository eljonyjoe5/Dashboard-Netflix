import { useEffect, useMemo, useState } from "react";
import cloud from "d3-cloud";
import type { Derived } from "../../lib/aggregate";
import { useElementWidth } from "../../hooks/useUi";
import { fmtInt, fmtPct } from "../../lib/format";
import { AMBER, AMBER_SOFT, INK, MUTED, RED, RED_DARK, RED_SOFT, UNKNOWN } from "../../lib/palette";
import { ChartCard, EmptyState } from "../ui";

interface CloudWord {
  text: string;
  full?: string;
  size: number;
  x: number;
  y: number;
  rotate: number;
  value?: number;
}

const PALETTE = [RED, INK, AMBER, RED_DARK, MUTED, RED_SOFT, AMBER_SOFT, UNKNOWN];

// Nombres compactos solo para la nube: permiten que las etiquetas largas
// conserven un tamaño proporcional en pantallas estrechas. La lista accesible
// y los tooltips muestran el nombre completo.
const CLOUD_LABELS: Record<string, string> = {
  "Películas internacionales": "Películas intl.",
  "Series internacionales": "Series intl.",
  "Películas infantiles y familiares": "Infantiles y familiares",
  "Películas independientes": "Cine independiente",
  "Series dramáticas": "Series drama",
  "Series de comedia": "Comedias de TV",
  "Películas románticas": "Románticas",
  "Series románticas": "Series románticas",
  "Series de acción y aventura": "Series acción",
  "Series de ciencia ficción y fantasía": "Series sci-fi",
  "Películas de ciencia ficción y fantasía": "Sci-fi y fantasía",
  "Series en español": "Series en español",
};

export function WordCloudChart({ derived }: { derived: Derived }) {
  const { ref, width } = useElementWidth<HTMLDivElement>();
  const [placed, setPlaced] = useState<CloudWord[]>([]);

  const words = useMemo(() => derived.topGenres.slice(0, 24), [derived.topGenres]);

  useEffect(() => {
    if (!width || words.length === 0) {
      setPlaced([]);
      return;
    }
    const max = words[0]?.count ?? 1;
    const min = words[words.length - 1]?.count ?? 1;
    const span = Math.max(1, max - min);
    const baseSize = width < 520 ? 9 : 11;
    const sizeRange = width < 520 ? 24 : 32;
    const layout = cloud()
      .size([Math.max(320, width), 420])
      .words(
        words.map((w) => {
          const label = CLOUD_LABELS[w.label] ?? w.label;
          const raw = baseSize + sizeRange * Math.sqrt((w.count - min) / span);
          // Evita que una etiqueta larga sea más ancha que la nube y se descarte.
          const fit = (Math.max(320, width) * 0.9) / Math.max(6, label.length * 0.6);
          return { text: label, full: w.label, size: Math.min(raw, fit), value: w.count };
        }),
      )
      .padding(2)
      .rotate(0)
      .font("Fraunces")
      .fontWeight(600)
      // d3-cloud usa Math.sqrt(d.value) por defecto e ignora el tamaño calculado.
      .fontSize((d: { size?: number }) => d.size ?? 12)
      .spiral("archimedean")
      .on("end", (output: CloudWord[]) => setPlaced(output));
    layout.start();
    return () => {
      layout.stop();
    };
  }, [width, words]);

  const maxCount = words[0]?.count ?? 1;

  return (
    <ChartCard
      title="Nube de palabras de géneros"
      subtitle="El tamaño de cada palabra es proporcional al número de títulos que pertenecen a ese género."
      help={[
        "Cuanto más grande la palabra, más títulos tienen ese género en el filtro actual. El color es decorativo: no codifica otra variable.",
        "Un título puede tener hasta tres géneros, así que la suma de todos los géneros supera el número de títulos. Los porcentajes usan el total de títulos como denominador.",
        "La nube es una vista exploratoria. Para leer cifras exactas y comparar, usa la lista ordenada que aparece debajo.",
        "Cuidado: “Películas internacionales” o “Series internacionales” son categorías amplias de Netflix, no un género narrativo único.",
      ]}
      legend={
        <p className="legend-note">
          Tamaño = número de títulos · Color = solo estético · {words.length} géneros mostrados de 42
        </p>
      }
      axis="Sin ejes: el tamaño codifica la frecuencia. La lista ordenada ofrece la misma información de forma accesible."
      note="El tamaño se calcula con raíz cuadrada para que las palabras pequeñas sigan siendo legibles; en la nube algunos nombres largos aparecen abreviados y la lista de abajo usa los nombres completos."
    >
      {words.length === 0 ? (
        <EmptyState message="No hay géneros para el filtro actual." />
      ) : (
        <>
          <div className="cloud-wrap" ref={ref}>
            {width > 0 ? (
              <svg
                viewBox={`0 0 ${Math.max(320, width)} 420`}
                role="img"
                aria-label={`Nube de palabras con ${words.length} géneros; el más frecuente es ${words[0].label} con ${fmtInt(words[0].count)} títulos.`}
              >
                <g transform={`translate(${Math.max(320, width) / 2}, 210)`}>
                  {placed.map((word, index) => (
                    <text
                      key={`${word.text}-${index}`}
                      x={word.x}
                      y={word.y}
                      transform={`rotate(${word.rotate})`}
                      textAnchor="middle"
                      fontSize={word.size}
                      fontWeight={600}
                      fontFamily="'Fraunces', Georgia, serif"
                      fill={PALETTE[index % PALETTE.length]}
                      opacity={0.92}
                    >
                      <title>{`${word.full ?? word.text}: ${fmtInt(word.value ?? 0)} títulos`}</title>
                      {word.text}
                    </text>
                  ))}
                </g>
              </svg>
            ) : null}
          </div>

          <details className="cloud-list">
            <summary>Ver lista ordenada (alternativa accesible)</summary>
            <ol>
              {words.map((word) => (
                <li key={word.name}>
                  <span className="cloud-list-label">{word.label}</span>
                  <span className="cloud-list-bar" aria-hidden="true">
                    <i style={{ width: `${(100 * word.count) / maxCount}%` }} />
                  </span>
                  <strong>{fmtInt(word.count)}</strong>
                  <span className="cloud-list-share">{fmtPct(word.share)}</span>
                </li>
              ))}
            </ol>
          </details>
        </>
      )}
    </ChartCard>
  );
}
