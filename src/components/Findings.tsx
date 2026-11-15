import type { Finding } from "../types";
import { Section } from "./ui";

export function Findings({ findings }: { findings: Finding[] }) {
  return (
    <Section
      id="hallazgos"
      num="08"
      title="Hallazgos del catálogo"
      intro="Seis lecturas redactadas con las cifras del ETL. Se calculan sobre el catálogo completo y no cambian con los filtros: son el punto de partida, no el resultado de tu selección."
    >
      <div className="findings-grid">
        {findings.map((finding) => (
          <article key={finding.id} className="finding-card">
            <span className="finding-number">{finding.cifra}</span>
            <h3>{finding.titulo}</h3>
            <p>{finding.texto}</p>
            <span className="finding-detail">{finding.detalle}</span>
          </article>
        ))}
      </div>
      <p className="data-note">
        Estas tarjetas usan los totales del catálogo completo (8.807 títulos). Los KPI y las gráficas de arriba sí
        responden a los filtros activos.
      </p>
    </Section>
  );
}
