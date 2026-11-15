import type { DashboardData } from "../types";
import { fmtDateEs, fmtInt, fmtPct } from "../lib/format";
import { Section } from "./ui";

const FIELD_LABELS: Record<string, string> = {
  show_id: "ID del título",
  type: "Tipo",
  title: "Título",
  director: "Director",
  cast: "Reparto",
  country: "País",
  date_added: "Fecha de incorporación",
  release_year: "Año de estreno",
  rating: "Clasificación",
  duration: "Duración",
  listed_in: "Géneros",
  description: "Descripción",
};

export function Methodology({ data }: { data: DashboardData }) {
  const q = data.quality;
  const anomalies = q.anomalias;

  return (
    <Section
      id="metodologia"
      num="09"
      title="Metodología y límites"
      intro="Cómo se construyó el tablero, qué se limpió y qué no se puede afirmar con este dataset. Todo lo que sigue sale del informe de calidad generado por el ETL."
    >
      <div className="method-grid">
        <article className="method-card">
          <span className="mini-label">01 · Fuente y corte</span>
          <h3>Un snapshot, no una serie viva</h3>
          <p>
            El archivo es <code>{q.archivo.nombre}</code> ({(q.archivo.bytes / 1024 / 1024).toFixed(1)} MB, SHA-256{" "}
            <code>{q.archivo.sha256.slice(0, 12)}…</code>). Contiene {fmtInt(q.totales.filas)} filas y{" "}
            {q.totales.columnas} columnas. El último día con datos es el <strong>{fmtDateEs(q.snapshot.corte)}</strong>.
          </p>
          <p>
            2021 está incompleto. Cualquier comparación con años cerrados debe tenerlo en cuenta: la caída de 2021 en
            incorporaciones no es una tendencia, es el efecto del corte.
          </p>
        </article>

        <article className="method-card">
          <span className="mini-label">02 · Calidad</span>
          <h3>Qué falta y qué se corrigió</h3>
          <ul className="method-list">
            <li>
              <strong>{fmtPct(q.cobertura.porcentaje_sin_director)}</strong> de los títulos no registra director (
              {fmtInt(q.cobertura.titulos_sin_director)}). No se imputa: queda fuera del ranking.
            </li>
            <li>
              <strong>{fmtInt(q.cobertura.titulos_sin_pais)}</strong> títulos no declaran país (
              {fmtPct((100 * q.cobertura.titulos_sin_pais) / q.totales.filas)}). Se excluyen del mapa y de los
              rankings, pero permanecen en los totales.
            </li>
            <li>
              <strong>{fmtInt(q.anomalias.rating_con_duracion.length)}</strong> filas tenían la duración en el campo
              rating; se movieron a <code>duration_min</code> y su clasificación quedó como desconocida.
            </li>
            <li>
              <strong>{fmtInt(q.anomalias.date_added_nulos.length)}</strong> títulos no tienen fecha de incorporación y{" "}
              <strong>{fmtInt(q.anomalias.date_added_antes_de_release_year.length)}</strong> tienen incorporación
              anterior al estreno (casi todos series cuya fecha corresponde a la última temporada). Se conservan y se
              marcan.
            </li>
            <li>
              <strong>{fmtInt(q.cobertura.anios_sin_titulos.length)}</strong> años entre {q.cobertura.release_year_min} y{" "}
              {q.cobertura.release_year_max} no tienen títulos. Se muestran en cero; no se interpolan.
            </li>
          </ul>
        </article>

        <article className="method-card">
          <span className="mini-label">03 · Reglas de conteo</span>
          <h3>Multivaluados y denominadores</h3>
          <ul className="method-list">
            <li>
              <strong>Géneros:</strong> un título puede tener hasta 3. Cada género suma; la suma de géneros supera el
              total de títulos.
            </li>
            <li>
              <strong>Países:</strong> un título puede declarar hasta 12. El mapa y el ranking suman en cada país;{" "}
              <code>primary_country</code> es el primero de la lista.
            </li>
            <li>
              <strong>Porcentajes:</strong> el denominador es el total de títulos del filtro (8.807 en el catálogo
              completo). Por eso los porcentajes por género o país pueden sumar más de 100%.
            </li>
            <li>
              <strong>Duración:</strong> minutos solo para películas; temporadas solo para series. Nunca se promedian
              juntos.
            </li>
            <li>
              <strong>Estreno vs. incorporación:</strong> <code>release_year</code> es cuándo se produjo el título;{" "}
              <code>date_added</code> es cuándo entró al catálogo. Son dos preguntas distintas.
            </li>
          </ul>
        </article>

        <article className="method-card">
          <span className="mini-label">04 · Límites</span>
          <h3>Lo que este tablero no puede decir</h3>
          <ul className="method-list">
            <li>No mide audiencia, horas vistas, ingresos ni popularidad: el dataset no trae esas variables.</li>
            <li>No representa toda la producción mundial, solo lo disponible en el catálogo de Netflix en el snapshot.</li>
            <li>No explica causalidad: una correlación entre año y género no prueba una estrategia.</li>
            <li>No corrige sesgos de declaración: país, director y reparto dependen de cómo se documentó cada título.</li>
            <li>No actualiza datos: es un análisis académico sobre un archivo histórico, no un panel en vivo.</li>
          </ul>
        </article>
      </div>

      <div className="quality-block">
        <div className="quality-head">
          <div>
            <h3>Tabla de calidad por campo</h3>
            <p>
              Nulos y valores distintos calculados por el ETL sobre {fmtInt(q.totales.filas)} títulos. La columna
              “Nota” explica los casos especiales.
            </p>
          </div>
          <div className="quality-badges">
            <span>{fmtInt(q.duplicados.show_id)} duplicados de ID</span>
            <span>{fmtInt(q.duplicados.filas_completas)} filas duplicadas</span>
            <span>{q.totales.muestreo}</span>
          </div>
        </div>

        <div className="table-scroll" tabIndex={0} role="region" aria-label="Tabla de calidad por campo">
          <table className="data-table quality-table">
            <thead>
              <tr>
                <th scope="col">Campo</th>
                <th scope="col" className="num">
                  Nulos
                </th>
                <th scope="col" className="num">
                  % nulos
                </th>
                <th scope="col" className="num">
                  Distintos
                </th>
                <th scope="col">Nota</th>
              </tr>
            </thead>
            <tbody>
              {q.campos.map((field) => (
                <tr key={field.campo}>
                  <td className="strong">{FIELD_LABELS[field.campo] ?? field.campo}</td>
                  <td className="num">{fmtInt(field.nulos)}</td>
                  <td className="num">{fmtPct(field.porcentaje_nulos)}</td>
                  <td className="num muted">{fmtInt(field.valores_distintos)}</td>
                  <td className="note-cell">{field.nota ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="scroll-hint">Desliza horizontalmente para ver todas las columnas →</p>
      </div>

      <div className="method-foot">
        <div>
          <h3>Normalizaciones aplicadas</h3>
          <ul className="normalization-list">
            {q.normalizaciones.map((n) => (
              <li key={n.regla}>
                <code>{n.regla}</code>
                <span>{n.detalle}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="method-callout">
          <span className="mini-label">Anomalías documentadas</span>
          <p>{anomalies.nota}</p>
          <ul>
            <li>
              {fmtInt(anomalies.rating_con_duracion.length)} ratings con duración (corregidos)
            </li>
            <li>
              {fmtInt(anomalies.rating_nulos.length)} títulos sin clasificación tras la corrección
            </li>
            <li>
              {fmtInt(anomalies.date_added_nulos.length)} títulos sin fecha de incorporación
            </li>
            <li>
              {fmtInt(anomalies.elementos_multivaluados_con_espacios)} elementos con espacios sobrantes (limpiados)
            </li>
          </ul>
          <p className="muted">
            El informe completo está en{" "}
            <a href="./data/quality_report.json" target="_blank" rel="noreferrer">
              quality_report.json
            </a>
            . La base reproducible y los Parquet se generan con <code>python etl/build_dataset.py</code>.
          </p>
        </div>
      </div>
    </Section>
  );
}
