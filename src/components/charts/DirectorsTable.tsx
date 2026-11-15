import type { Derived } from "../../lib/aggregate";
import { fmtInt, fmtPct } from "../../lib/format";
import { ChartCard, EmptyState } from "../ui";

export function DirectorsTable({ derived }: { derived: Derived }) {
  const rows = derived.topDirectors.slice(0, 10);

  return (
    <ChartCard
      title="Directores con más títulos"
      subtitle="Ranking de nombres acreditados. No mide calidad ni éxito de audiencia: cuenta títulos en el catálogo."
      help={[
        "Cada fila suma los títulos en los que esa persona aparece como director. Si un título tiene dos directores, ambos suman.",
        "Los 2.634 títulos sin director (29.91% del catálogo) no se imputan: se excluyen del ranking y se reportan en la metodología.",
        "El porcentaje usa como denominador los títulos con director del filtro actual; por la codirección, la columna puede sumar más de 100%.",
        "Cuidado: tener más títulos no significa tener más éxito. El dataset no incluye espectadores, horas vistas ni ingresos.",
      ]}
      axis="Tabla ordenada de mayor a menor por número de títulos. La columna “Género principal” es el género más frecuente entre los títulos de ese director en el filtro."
      note={`${fmtInt(derived.directorTitles)} títulos con director · ${fmtInt(derived.noDirector)} sin director (${fmtPct(derived.noDirectorShare)}) en el filtro actual.`}
    >
      {rows.length === 0 ? (
        <EmptyState message="No hay directores para el filtro actual." />
      ) : (
        <>
          <div className="table-scroll" tabIndex={0} role="region" aria-label="Tabla de directores con más títulos">
            <table className="data-table">
              <thead>
                <tr>
                  <th scope="col">#</th>
                  <th scope="col">Director</th>
                  <th scope="col" className="num">
                    Títulos
                  </th>
                  <th scope="col" className="num">
                    % con director
                  </th>
                  <th scope="col">Género principal</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((director, index) => (
                  <tr key={director.name}>
                    <td className="rank">{String(index + 1).padStart(2, "0")}</td>
                    <td className="strong">{director.name}</td>
                    <td className="num">{fmtInt(director.count)}</td>
                    <td className="num muted">{fmtPct(director.share)}</td>
                    <td>{director.topGenre}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="scroll-hint">Desliza horizontalmente para ver todas las columnas →</p>
        </>
      )}
    </ChartCard>
  );
}
