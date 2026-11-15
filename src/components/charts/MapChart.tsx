import { useMemo, useRef, useState } from "react";
import { ComposableMap, Geographies, Geography, Graticule, Sphere, ZoomableGroup } from "react-simple-maps";
import world from "world-atlas/countries-110m.json";
import type { CountryStat, PlaceFilter } from "../../lib/aggregate";
import { fmtInt, fmtMin, fmtPct } from "../../lib/format";
import { INK, PAPER } from "../../lib/palette";
import { ChartCard, Legend } from "../ui";

const MAP_COLORS = ["#f2c6cb", "#e28a96", "#cf5265", "#b72742", "#8f001b"];

function buildScale(stats: CountryStat[]) {
  const counts = stats
    .map((s) => s.count)
    .filter((c) => c > 0)
    .sort((a, b) => a - b);
  const q = (p: number) => counts[Math.min(counts.length - 1, Math.max(0, Math.floor((counts.length - 1) * p)))] ?? 0;
  const breaks = [q(0.2), q(0.4), q(0.6), q(0.8)];
  const fill = (count: number) => {
    if (count <= 0) return "#e8e2d7";
    const idx = breaks.filter((b) => count > b).length;
    return MAP_COLORS[Math.min(idx, MAP_COLORS.length - 1)];
  };
  const labels = [
    `1–${fmtInt(breaks[0])}`,
    `${fmtInt(breaks[0] + 1)}–${fmtInt(breaks[1])}`,
    `${fmtInt(breaks[1] + 1)}–${fmtInt(breaks[2])}`,
    `${fmtInt(breaks[2] + 1)}–${fmtInt(breaks[3])}`,
    `${fmtInt(breaks[3] + 1)}+`,
  ];
  return { fill, labels };
}

export function MapChart({
  stats,
  contextTotal,
  noCountry,
  filters,
  onSelectCountry,
  onClear,
}: {
  stats: CountryStat[];
  contextTotal: number;
  noCountry: number;
  filters: PlaceFilter;
  onSelectCountry: (index: number) => void;
  onClear: () => void;
}) {
  const [tip, setTip] = useState<{
    x: number;
    y: number;
    name: string;
    stat?: CountryStat;
  } | null>(null);
  const [zoom, setZoom] = useState(1);
  const [center, setCenter] = useState<[number, number]>([0, 0]);
  const wrapRef = useRef<HTMLDivElement | null>(null);

  const byIso = useMemo(() => {
    const map = new Map<number, CountryStat>();
    stats.forEach((s) => map.set(s.isoN, s));
    return map;
  }, [stats]);

  const { fill, labels } = useMemo(() => buildScale(stats), [stats]);
  const selectedIndex = filters.kind === "country" ? filters.index : null;

  const top = [...stats].filter((s) => s.count > 0).sort((a, b) => b.count - a.count);
  const maxTop = top[0]?.count ?? 1;

  const handleMove = (event: React.MouseEvent, name: string, stat?: CountryStat) => {
    const rect = wrapRef.current?.getBoundingClientRect();
    if (!rect) return;
    setTip({
      x: Math.max(10, Math.min(rect.width - 250, event.clientX - rect.left + 14)),
      y: Math.max(10, event.clientY - rect.top + 14),
      name,
      stat,
    });
  };

  const handleFocus = (name: string, stat?: CountryStat) => {
    setTip({ x: 24, y: 24, name, stat });
  };

  return (
    <ChartCard
      className="map-card"
      title="Mapa mundial de títulos por país"
      subtitle="Cada país se colorea según cuántos títulos del catálogo lo declaran como país de producción."
      help={[
        "El color indica cantidad de títulos por país. La escala usa cuantiles (grupos con el mismo número de países), no una escala lineal: así los países con pocos títulos siguen siendo visibles frente a Estados Unidos.",
        "Un título puede declarar varios países, por lo que la suma del mapa supera el total del catálogo. Los títulos sin país no se pintan: se muestran aparte.",
        "Pasa el cursor para ver títulos, porcentaje, género principal y duración media de películas. Haz clic en un país para filtrar todo el tablero; el mapa se mantiene como selector para que puedas cambiar de país.",
        "Cuidado: el mapa representa producción declarada, no audiencia ni ingresos. Netflix no publica esas cifras en este dataset.",
      ]}
      axis="Lectura: color = número de títulos. El tamaño del país no representa volumen; el mapa es una referencia geográfica."
      note="Los países pequeños o sin geometría en el mapa (por ejemplo, islas) igual aparecen en el ranking lateral y en el filtro de país."
    >
      <div className="map-main">
        <div className="map-shell" ref={wrapRef}>
        <ComposableMap
          projection="geoEqualEarth"
          width={820}
          height={430}
          projectionConfig={{ scale: 165 }}
          aria-label="Mapa mundial coroplético de títulos de Netflix por país"
        >
          <Sphere id="map-sphere" fill="#f4f0e8" stroke="#d8d2c6" strokeWidth={0.6} />
          <Graticule stroke="#d8d2c6" strokeWidth={0.4} />
          <ZoomableGroup
            zoom={zoom}
            center={center}
            minZoom={1}
            maxZoom={6}
            onMoveEnd={({ coordinates, zoom: z }) => {
              setCenter(coordinates);
              setZoom(z);
            }}
          >
            <Geographies geography={world}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  const iso = Number(geo.id);
                  const stat = byIso.get(iso);
                  const count = stat?.count ?? 0;
                  const selected = selectedIndex !== null && stat?.index === selectedIndex;
                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill={fill(count)}
                      stroke={selected ? INK : PAPER}
                      strokeWidth={selected ? 1.6 : 0.5}
                      tabIndex={count > 0 ? 0 : -1}
                      role="button"
                      aria-label={`${stat?.label ?? geo.properties.name}: ${fmtInt(count)} títulos`}
                      onMouseEnter={(e) => handleMove(e, stat?.label ?? geo.properties.name, stat)}
                      onMouseMove={(e) => handleMove(e, stat?.label ?? geo.properties.name, stat)}
                      onMouseLeave={() => setTip(null)}
                      onFocus={() => handleFocus(stat?.label ?? geo.properties.name, stat)}
                      onBlur={() => setTip(null)}
                      onClick={() => {
                        if (stat && count > 0) onSelectCountry(stat.index);
                      }}
                      onKeyDown={(e) => {
                        if ((e.key === "Enter" || e.key === " ") && stat && count > 0) {
                          e.preventDefault();
                          onSelectCountry(stat.index);
                        }
                      }}
                      style={{
                        default: { outline: "none", cursor: count > 0 ? "pointer" : "default" },
                        hover: { fill: count > 0 ? "#d90429" : "#ddd6c9", outline: "none" },
                        pressed: { fill: "#9e0018", outline: "none" },
                      }}
                    />
                  );
                })
              }
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>

        <div className="map-controls" aria-label="Controles del mapa">
          <button
            type="button"
            onClick={() => setZoom((z) => Math.min(6, Number((z + 0.5).toFixed(1))))}
            aria-label="Acercar el mapa"
          >
            +
          </button>
          <button
            type="button"
            onClick={() => setZoom((z) => Math.max(1, Number((z - 0.5).toFixed(1))))}
            aria-label="Alejar el mapa"
          >
            −
          </button>
          <button
            type="button"
            onClick={() => {
              setZoom(1);
              setCenter([0, 0]);
            }}
            aria-label="Restablecer el zoom"
          >
            ⟲
          </button>
        </div>

        {tip ? (
          <div className="map-tooltip" style={{ left: tip.x, top: tip.y }} role="status">
            <p className="tooltip-title">{tip.name}</p>
            {tip.stat && tip.stat.count > 0 ? (
              <>
                <dl>
                  <div>
                    <dt>Títulos</dt>
                    <dd>{fmtInt(tip.stat.count)}</dd>
                  </div>
                  <div>
                    <dt>% del filtro</dt>
                    <dd>{fmtPct((100 * tip.stat.count) / Math.max(1, contextTotal))}</dd>
                  </div>
                  <div>
                    <dt>Género principal</dt>
                    <dd>{tip.stat.topGenreLabel}</dd>
                  </div>
                  <div>
                    <dt>Duración media</dt>
                    <dd>{tip.stat.avgDuration ? fmtMin(tip.stat.avgDuration) : "Sin películas"}</dd>
                  </div>
                </dl>
                <p className="tooltip-hint">Clic para filtrar este país</p>
              </>
            ) : (
              <p className="tooltip-hint">Sin títulos en el filtro actual</p>
            )}
          </div>
        ) : null}
        </div>

        <div className="map-legend">
          <Legend
            items={[
              { color: "#e8e2d7", label: "Sin títulos" },
              ...labels.map((label, i) => ({ color: MAP_COLORS[i], label })),
            ]}
          />
          <span className="legend-extra">
            Escala por cuantiles · {stats.filter((s) => s.count > 0).length} países con datos
          </span>
        </div>
      </div>

      <div className="map-side">
        <div className="map-sin-dato">
          <span className="mini-label">Sin país declarado</span>
          <strong>{fmtInt(noCountry)}</strong>
          <span className="mini-sub">
            {fmtPct((100 * noCountry) / Math.max(1, contextTotal))} del filtro. Se excluyen del mapa y de los
            rankings, pero permanecen en los totales.
          </span>
          <button
            type="button"
            className="text-btn"
            onClick={() => onClear()}
            hidden={filters.kind === "all"}
          >
            Limpiar selección
          </button>
        </div>

        <div className="map-ranking">
          <div className="map-ranking-head">
            <h4>Top países</h4>
            <span>títulos</span>
          </div>
          <ol>
            {top.slice(0, 8).map((s) => (
              <li key={s.name}>
                <button
                  type="button"
                  className={selectedIndex === s.index ? "is-selected" : ""}
                  onClick={() => onSelectCountry(s.index)}
                  aria-pressed={selectedIndex === s.index}
                >
                  <span className="rank-label">{s.label}</span>
                  <span className="rank-bar" aria-hidden="true">
                    <i style={{ width: `${(100 * s.count) / maxTop}%` }} />
                  </span>
                  <span className="rank-value">{fmtInt(s.count)}</span>
                </button>
              </li>
            ))}
          </ol>
          <p className="map-ranking-note">Selecciona un país para enfocar el resto de las vistas.</p>
        </div>
      </div>
    </ChartCard>
  );
}
