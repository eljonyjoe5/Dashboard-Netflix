import type { DashboardData } from "../types";
import { fmtDateEs, fmtInt } from "../lib/format";

export function Hero({ data, pdfHref }: { data: DashboardData; pdfHref: string }) {
  const { meta } = data;
  return (
    <section id="inicio" className="hero">
      <div className="hero-meta">
        <p className="eyebrow">
          <span className="eyebrow-dot" aria-hidden="true" /> Proyecto 3 · Visualización de datos
        </p>
        <p className="hero-issue">Snapshot del catálogo · {fmtDateEs(meta.snapshot)}</p>
      </div>

      <div className="hero-inner">
        <div className="hero-copy">
          <h1>
            La economía del <em>entretenimiento</em>
            <span>Netflix y tendencias globales</span>
          </h1>
          <p className="hero-lead">
            Qué produce Netflix, para quién y desde dónde. Un recorrido por {fmtInt(meta.total_titulos)} títulos
            del catálogo para entender cómo cambian los gustos por región y por año.
          </p>

          <div className="hero-actions">
            <a className="btn btn-primary" href="#panorama">
              Explorar el tablero <span aria-hidden="true">→</span>
            </a>
            <a className="btn btn-ghost" href={pdfHref} target="_blank" rel="noreferrer">
              Leer el informe (PDF)
            </a>
          </div>
        </div>

        <aside className="hero-figure" aria-label="Ficha técnica del dataset">
          <span className="hero-figure-label">Títulos analizados</span>
          <p className="hero-figure-value">{fmtInt(meta.total_titulos)}</p>
          <p className="hero-figure-note">{meta.snapshot_nota}</p>
          <dl className="hero-card-grid">
            <div>
              <dt>Fuente</dt>
              <dd>Kaggle · shivamb/netflix-shows</dd>
            </div>
            <div>
              <dt>Cobertura</dt>
              <dd>
                {data.kpis.paises_distintos} países · 42 géneros
              </dd>
            </div>
            <div>
              <dt>Registro</dt>
              <dd>100% del catálogo, sin muestreo</dd>
            </div>
            <div>
              <dt>Actualización</dt>
              <dd>{fmtDateEs(meta.generado_en.slice(0, 10))}</dd>
            </div>
          </dl>
          <p className="hero-disclaimer">Análisis académico no oficial. No está afiliado a Netflix.</p>
        </aside>
      </div>

      <ul className="hero-chips" aria-label="Datos clave del análisis">
        <li>
          <span>Títulos</span>
          <strong>{fmtInt(meta.total_titulos)}</strong>
        </li>
        <li>
          <span>Películas</span>
          <strong>{fmtInt(meta.peliculas)}</strong>
        </li>
        <li>
          <span>Series</span>
          <strong>{fmtInt(meta.series)}</strong>
        </li>
        <li>
          <span>Países</span>
          <strong>{data.kpis.paises_distintos}</strong>
        </li>
      </ul>
    </section>
  );
}

const GESTURES = [
  {
    num: "01",
    title: "Filtra",
    text: "Elige tipo de contenido, periodo y país o región. Todas las gráficas se recalculan con la misma selección.",
  },
  {
    num: "02",
    title: "Pasa el cursor",
    text: "Cada barra, celda y país muestra una ficha con cifras exactas: títulos, porcentaje y duración cuando aplica.",
  },
  {
    num: "03",
    title: "Haz clic",
    text: "Un clic en un país del mapa o en una barra aplica el filtro. El botón “Limpiar” devuelve el panorama completo.",
  },
  {
    num: "04",
    title: "Abre la ayuda",
    text: "Cada tarjeta tiene “¿Cómo leer esta gráfica?” con lo esencial: qué muestra, qué representan ejes y colores, y qué cuidar.",
  },
];

export function HowToRead() {
  return (
    <section id="como-leer" className="howto">
      <div className="howto-head">
        <div>
          <p className="eyebrow">Antes de empezar</p>
          <h2>Cómo leer este tablero</h2>
        </div>
        <p>
          No necesitas saber estadística. Cuatro gestos bastan para moverte y entender qué está pasando con el
          catálogo.
        </p>
      </div>

      <div className="howto-grid">
        {GESTURES.map((g) => (
          <article key={g.num} className="howto-card">
            <span className="howto-num">{g.num}</span>
            <h3>{g.title}</h3>
            <p>{g.text}</p>
          </article>
        ))}
      </div>

      <div className="color-code" aria-label="Código de color del tablero">
        <span className="color-code-label">Código de color</span>
        <span>
          <i className="swatch red" aria-hidden="true" /> Películas y acento editorial
        </span>
        <span>
          <i className="swatch gold" aria-hidden="true" /> Series
        </span>
        <span>
          <i className="swatch grey" aria-hidden="true" /> Sin dato declarado
        </span>
        <span>
          <i className="swatch dash" aria-hidden="true" /> Corte del snapshot
        </span>
      </div>
    </section>
  );
}
