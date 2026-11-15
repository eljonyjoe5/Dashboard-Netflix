import { useEffect, useState } from "react";

const NAV = [
  { id: "panorama", label: "Panorama" },
  { id: "mapa", label: "Mapa" },
  { id: "tiempo", label: "Tiempo" },
  { id: "generos", label: "Géneros" },
  { id: "tipos", label: "Tipos" },
  { id: "rankings", label: "Rankings" },
  { id: "patrones", label: "Patrones" },
  { id: "duracion", label: "Duración" },
  { id: "hallazgos", label: "Hallazgos" },
  { id: "metodologia", label: "Método" },
];

export function Header({ active, progress, pdfHref }: { active: string; progress: number; pdfHref: string }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <>
      <div className="reading-progress" aria-hidden="true">
        <span style={{ width: `${progress}%` }} />
      </div>

      <header className="site-header">
        <div className="header-inner">
          <a href="#inicio" className="brand" aria-label="Ir al inicio">
            <span className="brand-mark" aria-hidden="true">
              <span />
            </span>
            <span className="brand-text">
              Catálogo <i>en foco</i>
            </span>
          </a>

          <nav className="desktop-nav" aria-label="Secciones del tablero">
            {NAV.map((item) => (
              <a key={item.id} href={`#${item.id}`} className={active === item.id ? "is-active" : ""}>
                {item.label}
              </a>
            ))}
          </nav>

          <div className="header-actions">
            <button
              type="button"
              className="menu-btn"
              aria-expanded={open}
              aria-controls="mobile-menu"
              onClick={() => setOpen((v) => !v)}
            >
              <span className="sr-only">{open ? "Cerrar menú" : "Abrir menú"}</span>
              <span className={`burger ${open ? "is-open" : ""}`} aria-hidden="true">
                <i />
                <i />
              </span>
            </button>
          </div>
        </div>
      </header>

      {open ? (
        <div className="mobile-menu" id="mobile-menu">
          <nav aria-label="Secciones del tablero (móvil)">
            {NAV.map((item, index) => (
              <a key={item.id} href={`#${item.id}`} onClick={() => setOpen(false)}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                {item.label}
              </a>
            ))}
            <a href={pdfHref} target="_blank" rel="noreferrer" onClick={() => setOpen(false)}>
              <span>↧</span> Descargar PDF
            </a>
          </nav>
        </div>
      ) : null}
    </>
  );
}
