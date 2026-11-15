import { useEffect, useMemo, useState } from "react";
import type { DashboardData } from "./types";
import {
  DEFAULT_FILTERS,
  derive,
  filtersLabel,
  hasActiveFilters,
  type Filters,
} from "./lib/aggregate";
import { fmtInt, fmtPct } from "./lib/format";
import { useActiveSection, useScrollProgress } from "./hooks/useUi";
import { Header } from "./components/Header";
import { Hero, HowToRead } from "./components/Hero";
import { Filters as FilterBar } from "./components/Filters";
import { KpiGrid } from "./components/KpiGrid";
import { Section } from "./components/ui";
import { MapChart } from "./components/charts/MapChart";
import { TimeSeriesChart } from "./components/charts/TimeSeriesChart";
import { WordCloudChart } from "./components/charts/WordCloudChart";
import { TopCountriesChart, TopGenresChart } from "./components/charts/Rankings";
import { TypeDonut } from "./components/charts/TypeDonut";
import { RatingsChart } from "./components/charts/RatingsChart";
import { DurationCharts } from "./components/charts/DurationCharts";
import { DirectorsTable } from "./components/charts/DirectorsTable";
import { DecadeGenreHeatmap, DecadeVariationChart, YearMonthHeatmap } from "./components/charts/Heatmaps";
import { Findings } from "./components/Findings";
import { Methodology } from "./components/Methodology";
import { Footer } from "./components/Footer";

const PDF_HREF = "./docs/Justificacion_Fase1.pdf";
const PDF_FASE2_HREF = "./docs/Diseno_Fase2.pdf";
const PDF_FASE3_HREF = "./docs/Implementacion_Fase3.pdf";
const SECTION_IDS = [
  "inicio",
  "panorama",
  "mapa",
  "tiempo",
  "generos",
  "tipos",
  "rankings",
  "patrones",
  "duracion",
  "hallazgos",
  "metodologia",
];

function Dashboard({ data }: { data: DashboardData }) {
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const progress = useScrollProgress();
  const active = useActiveSection(SECTION_IDS);
  const derived = useMemo(() => derive(data, filters), [data, filters]);

  // El mapa conserva todo el contexto de países: solo responde a tipo y periodo.
  const mapDerived = useMemo(
    () => derive(data, { ...filters, place: { kind: "all" } }),
    [data, filters],
  );

  const snapshotYear = Number(data.meta.snapshot.slice(0, 4));
  const currentLabel = filtersLabel(filters, data);

  const clearAll = () => setFilters(DEFAULT_FILTERS);
  const clearPlace = () => setFilters((current) => ({ ...current, place: { kind: "all" } }));

  const selectCountry = (index: number) =>
    setFilters((current) =>
      current.place.kind === "country" && current.place.index === index
        ? { ...current, place: { kind: "all" } }
        : { ...current, place: { kind: "country", index } },
    );

  return (
    <>
      <a className="skip-link" href="#contenido">
        Saltar al contenido
      </a>
      <Header active={active} progress={progress} pdfHref={PDF_HREF} />
      <main id="contenido">
        <Hero data={data} pdfHref={PDF_HREF} />
        <HowToRead />

        <FilterBar
          data={data}
          filters={filters}
          onChange={setFilters}
          resultCount={derived.count}
          onClear={clearAll}
        />

        <div className="page">
          <Section
            id="panorama"
            num="00"
            title="El catálogo en cifras"
            intro={`Vista actual: ${currentLabel}. Los seis indicadores, las gráficas y las tablas se recalculan con la misma selección.`}
          >
            {derived.count === 0 ? (
              <div className="filter-empty" role="status">
                <p>No hay títulos con esta combinación de filtros. Prueba con otro periodo, país o tipo de contenido.</p>
                <button type="button" className="btn btn-primary" onClick={clearAll}>
                  Limpiar filtros
                </button>
              </div>
            ) : null}
            <KpiGrid data={data} derived={derived} />
            <p className="data-note">
              {hasActiveFilters(filters)
                ? `El filtro contiene ${fmtInt(derived.count)} de ${fmtInt(data.meta.total_titulos)} títulos. Los porcentajes de las gráficas usan ese total filtrado como denominador.`
                : `Vista completa del catálogo: ${fmtInt(data.meta.total_titulos)} títulos. Todos los porcentajes usan este total como denominador.`}
            </p>
          </Section>

          <Section
            id="mapa"
            num="01"
            title="Dónde se produce el catálogo"
            intro="El mapa colorea cada país según cuántos títulos lo declaran como lugar de producción. Se mantiene como selector: al elegir un país, el resto de las vistas se enfoca en él."
          >
            <MapChart
              stats={mapDerived.byCountry}
              contextTotal={mapDerived.count}
              noCountry={mapDerived.noCountry}
              filters={filters.place}
              onSelectCountry={selectCountry}
              onClear={clearPlace}
            />
          </Section>

          <Section
            id="tiempo"
            num="02"
            title="Cómo cambió el catálogo en el tiempo"
            intro="Estrenar y llegar al catálogo son dos relojes distintos. Aquí se comparan sin mezclarlos y se mide cuánto pesa cada década."
          >
            <TimeSeriesChart derived={derived} snapshotYear={snapshotYear} />

            <div className="insight-strip">
              <article>
                <span className="mini-label">Estreno más alto</span>
                <strong>{derived.peakRelease ? derived.peakRelease.year : "—"}</strong>
                <p>
                  {derived.peakRelease
                    ? `${fmtInt(derived.peakRelease.count)} títulos estrenados en el filtro actual.`
                    : "Sin estrenos para la selección."}
                </p>
              </article>
              <article>
                <span className="mini-label">Incorporación más alta</span>
                <strong>{derived.peakAdded ? derived.peakAdded.year : "—"}</strong>
                <p>
                  {derived.peakAdded
                    ? `${fmtInt(derived.peakAdded.count)} títulos llegaron al catálogo ese año.`
                    : "Sin fechas de incorporación válidas."}
                </p>
              </article>
              <article>
                <span className="mini-label">Últimos 5 años ({derived.last5.from}–{derived.last5.to})</span>
                <strong>{fmtPct(derived.last5.share)}</strong>
                <p>
                  {fmtInt(derived.last5.count)} títulos del filtro se incorporaron en ese periodo. 2021 está incompleto.
                </p>
              </article>
            </div>

            <DecadeVariationChart derived={derived} />
          </Section>

          <Section
            id="generos"
            num="03"
            title="Qué géneros dominan"
            intro="La nube da una impresión rápida; el ranking y la lista ordenada permiten comparar con cifras exactas. Un título puede pertenecer a varios géneros."
          >
            <div className="grid grid-2">
              <WordCloudChart derived={derived} />
              <TopGenresChart derived={derived} />
            </div>
          </Section>

          <Section
            id="tipos"
            num="04"
            title="Películas, series y clasificaciones"
            intro="La composición del catálogo y las etiquetas de edad que declara el dataset. Son dos lecturas distintas del mismo conjunto filtrado."
          >
            <div className="grid grid-2">
              <TypeDonut derived={derived} />
              <RatingsChart derived={derived} />
            </div>
          </Section>

          <Section
            id="rankings"
            num="05"
            title="Países y directores con más títulos"
            intro="Dos rankings de volumen, no de éxito. Producir un título no equivale a tener audiencia, y acreditar más títulos no mide calidad."
          >
            <div className="grid grid-2">
              <TopCountriesChart derived={derived} onSelectCountry={selectCountry} />
              <DirectorsTable derived={derived} />
            </div>
          </Section>

          <Section
            id="patrones"
            num="06"
            title="Patrones por década y por mes"
            intro="Las matrices cruzan dos dimensiones a la vez: género por década de estreno y año por mes de incorporación. El color ayuda a detectar concentraciones."
          >
            <DecadeGenreHeatmap derived={derived} />
            <YearMonthHeatmap derived={derived} />
          </Section>

          <Section
            id="duracion"
            num="07"
            title="Cuánto dura el contenido"
            intro="Minutos para películas y temporadas para series. El tablero nunca promedia estas dos unidades juntas."
          >
            <DurationCharts derived={derived} />
          </Section>

          <Findings findings={data.findings} />
          <Methodology data={data} />
        </div>
      </main>

      <Footer
        data={data}
        pdfHref={PDF_HREF}
        pdfFase2Href={PDF_FASE2_HREF}
        pdfFase3Href={PDF_FASE3_HREF}
      />
    </>
  );
}

function BootScreen({ error }: { error: string | null }) {
  return (
    <div className="boot-screen" role={error ? "alert" : "status"}>
      <div className="boot-card">
        <span className="brand-mark boot-mark" aria-hidden="true">
          <span />
        </span>
        <p className="boot-eyebrow">Catálogo en foco · Proyecto 3</p>
        <h1>{error ? "No se pudo cargar el tablero" : "Preparando el catálogo…"}</h1>
        {error ? (
          <>
            <p className="boot-text">
              El navegador no pudo leer <code>data/dashboard.json</code>. Detalle técnico: <code>{error}</code>.
            </p>
            <ol className="boot-steps">
              <li>
                Ejecuta <code>python etl/build_dataset.py</code> para regenerar los datos.
              </li>
              <li>
                Sirve el proyecto con <code>npm run dev</code> o <code>npm run preview</code>; abrir el archivo
                directamente con <code>file://</code> bloquea la lectura del JSON.
              </li>
              <li>Recarga esta página.</li>
            </ol>
            <button type="button" className="btn btn-primary" onClick={() => window.location.reload()}>
              Reintentar
            </button>
          </>
        ) : (
          <>
            <p className="boot-text">Leyendo 8.807 títulos y calculando los agregados del catálogo.</p>
            <div className="boot-bar" aria-hidden="true">
              <span />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch("./data/dashboard.json", { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json() as Promise<DashboardData>;
      })
      .then((payload) => {
        if (!payload?.titles?.rows?.length) throw new Error("El archivo no contiene filas de títulos.");
        if (!payload?.dimensions?.countries?.length) throw new Error("Faltan las dimensiones de países.");
        setData(payload);
      })
      .catch((cause: unknown) => {
        if (cause instanceof DOMException && cause.name === "AbortError") return;
        setError(cause instanceof Error ? cause.message : String(cause));
      });
    return () => controller.abort();
  }, []);

  if (error) return <BootScreen error={error} />;
  if (!data) return <BootScreen error={null} />;
  return <Dashboard data={data} />;
}
