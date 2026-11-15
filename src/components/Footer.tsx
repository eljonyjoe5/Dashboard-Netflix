import type { DashboardData } from "../types";
import { fmtDateEs, fmtInt } from "../lib/format";

export function Footer({
  data,
  pdfHref,
  pdfFase2Href,
  pdfFase3Href,
}: {
  data: DashboardData;
  pdfHref: string;
  pdfFase2Href: string;
  pdfFase3Href: string;
}) {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <a href="#inicio" className="brand" aria-label="Volver al inicio">
            <span className="brand-mark" aria-hidden="true">
              <span />
            </span>
            <span className="brand-text">
              Catálogo <i>en foco</i>
            </span>
          </a>
          <p>
            La economía del entretenimiento: Netflix y tendencias globales. Tablero editorial construido con{" "}
            {fmtInt(data.meta.total_titulos)} títulos del catálogo y un corte al {fmtDateEs(data.meta.snapshot)}.
          </p>
          <p className="footer-disclaimer">
            Análisis independiente con fines educativos. No está afiliado, patrocinado ni respaldado por Netflix.
          </p>
        </div>

        <div className="footer-col">
          <h3>Equipo</h3>
          <ul>
            <li>Jonathan Alexander Gonzalez Romero</li>
            <li className="muted">Docente: Jessica Carmin Mendiola Fuentes</li>
            <li className="muted">Visualización de datos · Proyecto 3</li>
            <li className="muted">Negocios y cultura digital</li>
          </ul>
        </div>

        <div className="footer-col">
          <h3>Explorar</h3>
          <ul>
            <li>
              <a href="#mapa">Mapa mundial</a>
            </li>
            <li>
              <a href="#tiempo">Evolución en el tiempo</a>
            </li>
            <li>
              <a href="#generos">Géneros</a>
            </li>
            <li>
              <a href="#hallazgos">Hallazgos</a>
            </li>
            <li>
              <a href="#metodologia">Metodología</a>
            </li>
          </ul>
        </div>

        <div className="footer-col">
          <h3>Documentos y datos</h3>
          <ul>
            <li>
              <a href={pdfHref} target="_blank" rel="noreferrer">
                Informe de justificación (PDF)
              </a>
            </li>
            <li>
              <a href={pdfFase2Href} target="_blank" rel="noreferrer">
                Informe de diseño · Fase 2 (PDF)
              </a>
            </li>
            <li>
              <a href={pdfFase3Href} target="_blank" rel="noreferrer">
                Informe de implementación · Fase 3 (PDF)
              </a>
            </li>
            <li>
              <a href="./data/quality_report.json" target="_blank" rel="noreferrer">
                Reporte de calidad (JSON)
              </a>
            </li>
            <li>
              <a href={data.meta.url_fuente} target="_blank" rel="noreferrer">
                Dataset original en Kaggle
              </a>
            </li>
            <li className="muted">
              <code>python etl/build_dataset.py</code>
            </li>
            <li className="muted">
              <code>npm install &amp;&amp; npm run dev</code>
            </li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <p>
          Generado el {fmtDateEs(data.meta.generado_en.slice(0, 10))} · Datos: {data.meta.fuente} · Snapshot{" "}
          {data.meta.snapshot}
        </p>
        <a href="#inicio" className="back-top">
          Volver arriba <span aria-hidden="true">↑</span>
        </a>
      </div>
    </footer>
  );
}
