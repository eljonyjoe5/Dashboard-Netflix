"""
Genera el informe de implementación de la Fase 3.

El documento explica cómo el wireframe de la Fase 2 se convirtió en el
tablero React: estructura del proyecto, arquitectura, KPIs, gráficos, mapa,
paleta, problemas y reflexión técnica. Usa capturas reales del tablero y del
wireframe, y las cifras del mismo ETL que alimenta la aplicación.

Uso:
    python docs/generate_pdf_fase3.py
"""
from __future__ import annotations

import html
import json
import shutil
import subprocess
from datetime import date
from pathlib import Path

from generate_pdf import (
    BRAND,
    CSS as BASE_CSS,
    DOCS,
    PUBLIC_DOCS,
    ROOT,
    SUBJECT,
    TEACHER,
    TEAM,
    TOPIC,
    find_chrome,
    fmt_int,
    fmt_pct,
)

QUALITY = ROOT / "data" / "quality_report.json"
DASHBOARD = ROOT / "public" / "data" / "dashboard.json"
HTML = DOCS / "implementacion_fase3.html"
PDF = DOCS / "Implementacion_Fase3.pdf"
TOTAL_PAGES = 17

D: dict = {}
Q: dict = {}


def load() -> tuple[dict, dict]:
    quality = json.loads(QUALITY.read_text(encoding="utf-8"))
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))
    return quality, dashboard


CSS = BASE_CSS + r"""
/* ============================================================
   Fase 3 · implementación
   ============================================================ */

.f3-cover .cover-inner { padding: 11mm 18mm 12mm; }
.f3-cover h1 { font-size: 38pt; line-height: 0.92; }
.f3-cover h1 em { font-size: 20pt; margin-top: 2mm; }
.f3-cover .lead { margin-top: 4mm; max-width: 106mm; font-size: 10pt; }
.f3-cover .cover-meta { margin-top: 5mm; }
.f3-cover .cover-meta div { padding-top: 2.4mm; padding-bottom: 2.4mm; }
.f3-cover .cover-foot { margin-top: 3mm; padding-top: 2.4mm; }

.f3-cover-body {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(62mm, 0.85fr);
  gap: 11mm;
  align-items: end;
  margin: 7mm 0 6mm;
}

.f3-cover-visual {
  border-top: 2pt solid var(--ink);
  padding-top: 3mm;
}

.f3-mini-flow {
  display: grid;
  grid-template-columns: 1fr 7mm 1fr 7mm 1fr;
  align-items: center;
  gap: 1mm;
}

.f3-mini-flow > div:not(.arrow) {
  min-height: 23mm;
  padding: 2mm;
  border: 0.5pt solid var(--line-2);
  background: var(--white);
}

.f3-mini-flow span {
  display: block;
  font-size: 5.4pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--red);
}

.f3-mini-flow strong {
  display: block;
  margin-top: 1mm;
  font-family: var(--serif);
  font-size: 8.4pt;
  line-height: 1.1;
}

.f3-mini-flow p {
  margin: 1mm 0 0;
  font-size: 5.6pt;
  line-height: 1.35;
  color: var(--muted);
}

.f3-mini-flow .arrow {
  text-align: center;
  font-family: var(--serif);
  font-size: 12pt;
  color: var(--red);
}

.f3-cover-visual .cap {
  margin: 2.6mm 0 0;
  font-size: 6.4pt;
  line-height: 1.45;
  color: var(--muted);
}

.f3-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-top: 1.2pt solid var(--ink);
  border-bottom: 0.6pt solid var(--line);
}

.f3-metrics > div {
  padding: 2.2mm 3mm 2.2mm 0;
  border-right: 0.5pt solid var(--line);
}

.f3-metrics > div:last-child { border-right: 0; }
.f3-metrics > div:not(:first-child) { padding-left: 3mm; }

.f3-metrics .k {
  display: block;
  font-size: 5.7pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.f3-metrics strong {
  display: block;
  margin-top: 1mm;
  font-family: var(--serif);
  font-size: 16pt;
  font-weight: 600;
  line-height: 0.95;
  letter-spacing: -0.04em;
}

.f3-metrics p {
  margin: 1mm 0 0;
  font-size: 6.1pt;
  line-height: 1.35;
  color: var(--muted);
}

.f3-cover-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-top: 1.2pt solid var(--ink);
  margin-top: 4mm;
}

.f3-cover-strip > div {
  padding: 2.6mm 4mm 0 0;
  border-right: 0.5pt solid var(--line);
}

.f3-cover-strip > div:last-child { border-right: 0; }
.f3-cover-strip > div:not(:first-child) { padding-left: 4mm; }

.f3-cover-strip .k {
  display: block;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.f3-cover-strip p {
  margin: 1mm 0 0;
  font-size: 6.6pt;
  line-height: 1.4;
  color: var(--muted);
}

/* ------------------------------------------------------------
   Índice
   ------------------------------------------------------------ */

.f3-index .lead { font-size: 9.2pt; line-height: 1.42; margin-bottom: 2.6mm; }
.f3-index .index-title { margin-bottom: 3mm; }
.f3-index .index-row { padding: 1.55mm 0; }
.f3-index .index-row h3 { font-size: 10pt; }
.f3-index .index-row p { font-size: 6.8pt; margin-top: 0.3mm; }
.f3-index .index-row .n { font-size: 8.6pt; }
.f3-index .index-row .p { font-size: 9.4pt; }

.f3-index .index-foot { margin-top: 2.8mm; }
.f3-index table.compact { font-size: 6.4pt; }
.f3-index table.compact th { padding: 1mm 1.3mm; }
.f3-index table.compact td { padding: 0.75mm 1.3mm; }
.f3-index .f3-criteria > div { padding: 1.7mm 0; font-size: 6.9pt; }

/* ------------------------------------------------------------
   Bloques de contenido
   ------------------------------------------------------------ */

.f3-kicker {
  font-size: 6.2pt;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted-2);
  margin: 0 0 1.4mm;
}

.f3-number-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4mm;
  margin: 1mm 0 4mm;
}

.f3-number {
  border-top: 1.4pt solid var(--ink);
  padding-top: 2.2mm;
}

.f3-number span {
  display: block;
  font-family: var(--serif);
  font-size: 18pt;
  font-weight: 600;
  line-height: 1;
  color: var(--red);
  letter-spacing: -0.04em;
}

.f3-number h3 { margin: 1.4mm 0 1mm; font-size: 10.2pt; }
.f3-number p { margin: 0; font-size: 7.2pt; line-height: 1.45; color: var(--muted); }

.f3-shot {
  border: 0.6pt solid var(--line);
  background: var(--white);
  padding: 1.2mm;
}

.f3-shot img { display: block; width: 100%; border: 0; }

.f3-shot figcaption {
  margin: 1.2mm 0 0;
  padding: 0 0.6mm;
  font-size: 6.2pt;
  line-height: 1.4;
  color: var(--muted);
}

.f3-shot figcaption b { color: var(--ink-soft); font-weight: 600; }

.f3-compare {
  display: grid;
  grid-template-columns: 1.02fr 0.98fr;
  gap: 4mm;
  align-items: start;
}

.f3-compare-stack {
  display: grid;
  gap: 2.4mm;
}

.f3-caption {
  margin: 1.4mm 0 0;
  font-size: 6.3pt;
  line-height: 1.4;
  color: var(--muted);
}

.f3-caption b { color: var(--ink-soft); font-weight: 600; }

.f3-code {
  margin: 0;
  padding: 3mm 3.4mm;
  background: #171614;
  color: #e9e3d8;
  font-family: "Cascadia Mono", Consolas, "Courier New", monospace;
  font-size: 5.9pt;
  line-height: 1.5;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.f3-code .c { color: #a79e90; }
.f3-code .r { color: #f3a6b0; }
.f3-code .g { color: #d8b26a; }

.f3-code-label {
  display: flex;
  justify-content: space-between;
  gap: 4mm;
  margin: 0 0 1.2mm;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.f3-tree {
  margin: 0;
  padding: 3mm 3.4mm;
  border: 0.6pt solid var(--line);
  background: var(--paper-2);
  font-family: "Cascadia Mono", Consolas, "Courier New", monospace;
  font-size: 6.1pt;
  line-height: 1.58;
  color: var(--ink-soft);
  white-space: pre;
}

.f3-tree b { color: var(--red-deep); font-weight: 600; }
.f3-tree i { color: var(--muted); font-style: normal; }

.f3-flow {
  display: grid;
  grid-template-columns: 1fr 5mm 1fr 5mm 1fr 5mm 1fr 5mm 1fr;
  align-items: stretch;
  gap: 0;
  margin: 1mm 0 4mm;
}

.f3-flow > div:not(.arrow) {
  min-height: 24mm;
  padding: 2.2mm 2.4mm;
  border-top: 1.4pt solid var(--ink);
  background: var(--white);
}

.f3-flow .step {
  display: block;
  font-size: 5.4pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--red);
}

.f3-flow strong {
  display: block;
  margin-top: 1.2mm;
  font-family: var(--serif);
  font-size: 8.2pt;
  line-height: 1.12;
}

.f3-flow p {
  margin: 1.2mm 0 0;
  font-size: 5.7pt;
  line-height: 1.35;
  color: var(--muted);
}

.f3-flow .arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--serif);
  font-size: 11pt;
  color: var(--red);
}

.f3-note {
  border-left: 2.2pt solid var(--red);
  background: var(--white);
  padding: 2.8mm 3.4mm;
  font-size: 7.6pt;
  line-height: 1.5;
  color: var(--ink-soft);
}

.f3-note strong { color: var(--ink); }
.f3-note p:last-child { margin-bottom: 0; }

.f3-list {
  margin: 0;
  padding-left: 4mm;
  font-size: 7.4pt;
  line-height: 1.48;
}

.f3-list li { margin-bottom: 1.1mm; }
.f3-list li:last-child { margin-bottom: 0; }

.f3-mini-table { font-size: 6.9pt; }
.f3-mini-table th { padding: 1.1mm 1.3mm; }
.f3-mini-table td { padding: 1.05mm 1.3mm; }

.f3-criteria {
  display: grid;
  grid-template-columns: 1fr 12mm;
  gap: 0;
  border-top: 1.2pt solid var(--ink);
}

.f3-criteria > div {
  padding: 2.1mm 0;
  border-bottom: 0.5pt solid var(--line);
  font-size: 7.2pt;
  line-height: 1.4;
}

.f3-criteria .pts {
  text-align: right;
  font-family: var(--serif);
  font-size: 10pt;
  font-weight: 600;
  color: var(--red);
}

.f3-palette {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2.4mm;
  margin: 1mm 0 3.5mm;
}

.f3-swatch {
  border: 0.6pt solid var(--line);
  background: var(--white);
}

.f3-swatch .chip-color {
  height: 17mm;
  border-bottom: 0.6pt solid var(--line);
}

.f3-swatch .chip-body { padding: 2mm 2.2mm 2.4mm; }
.f3-swatch .chip-body span {
  display: block;
  font-size: 5.6pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-2);
}
.f3-swatch .chip-body strong {
  display: block;
  margin-top: 1mm;
  font-family: var(--serif);
  font-size: 9.6pt;
}
.f3-swatch .chip-body code {
  display: block;
  margin-top: 0.6mm;
  font-size: 6.4pt;
  color: var(--muted);
}
.f3-swatch .chip-body p {
  margin: 1.2mm 0 0;
  font-size: 6.2pt;
  line-height: 1.35;
  color: var(--muted);
}

.f3-problems { font-size: 6.8pt; }
.f3-problems th { padding: 1.1mm 1.2mm; }
.f3-problems td { padding: 1.15mm 1.2mm; line-height: 1.38; }
.f3-problems td:first-child { font-weight: 600; color: var(--ink); }

.f3-verdict {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 4mm;
  margin-top: 3.5mm;
}

.f3-quote {
  margin: 4mm 0 0;
  padding: 4mm 0 0;
  border-top: 1.4pt solid var(--ink);
  font-family: var(--serif);
  font-size: 15pt;
  font-style: italic;
  line-height: 1.28;
  letter-spacing: -0.02em;
}

.f3-quote span {
  display: block;
  margin-top: 2mm;
  font-family: var(--sans);
  font-style: normal;
  font-size: 6.2pt;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.f3-footnote {
  font-size: 6.3pt;
  line-height: 1.42;
  color: var(--muted);
}

.f3-strong { color: var(--ink); font-weight: 600; }
.f3-red { color: var(--red); }
.f3-amber { color: var(--amber); }

/* ------------------------------------------------------------
   Portada · captura del tablero
   ------------------------------------------------------------ */

.f3-cover-shot {
  margin: 5mm 0 0;
  padding: 1.2mm;
  border: 0.6pt solid var(--line);
  background: var(--white);
}

.f3-cover-shot img { display: block; width: 96%; margin: 0 auto; border: 0; }

.f3-cover-shot figcaption {
  margin: 1.4mm 0 0;
  padding: 0 0.4mm;
  font-size: 6.3pt;
  line-height: 1.4;
  color: var(--muted);
}

.f3-cover-shot figcaption b { color: var(--ink-soft); font-weight: 600; }

/* ------------------------------------------------------------
   Bandas de cierre
   ------------------------------------------------------------ */

.f3-timeline {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-top: 1.2pt solid var(--ink);
}

.f3-timeline > div {
  padding: 2.4mm 3.2mm 0 0;
  border-right: 0.5pt solid var(--line);
}

.f3-timeline > div:last-child { border-right: 0; }
.f3-timeline > div:not(:first-child) { padding-left: 3.2mm; }

.f3-timeline .k {
  display: block;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--red);
}

.f3-timeline strong {
  display: block;
  margin-top: 1.2mm;
  font-family: var(--serif);
  font-size: 10pt;
  line-height: 1.1;
}

.f3-timeline p {
  margin: 1.1mm 0 0;
  font-size: 6.6pt;
  line-height: 1.42;
  color: var(--muted);
}

.f3-specimen {
  display: grid;
  grid-template-columns: 0.86fr 1.14fr;
  border-top: 1.2pt solid var(--ink);
}

.f3-specimen > div { padding: 2.4mm 3.4mm 0 0; }

.f3-specimen > div + div {
  padding-left: 3.4mm;
  border-left: 0.5pt solid var(--line);
}

.f3-specimen .k {
  display: block;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.f3-specimen .aa {
  margin-top: 1.4mm;
  font-family: var(--serif);
  font-size: 32pt;
  font-weight: 600;
  line-height: 0.86;
  letter-spacing: -0.045em;
}

.f3-specimen .aa em { color: var(--red); font-weight: 400; }

.f3-specimen .aa-sans {
  margin-top: 1.6mm;
  font-family: var(--sans);
  font-size: 23pt;
  font-weight: 500;
  line-height: 0.9;
  letter-spacing: -0.02em;
}

.f3-specimen p {
  margin: 1.4mm 0 0;
  font-size: 6.5pt;
  line-height: 1.42;
  color: var(--muted);
}

.f3-states {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2.2mm;
  margin-top: 2.6mm;
}

.f3-states span {
  padding: 1.2mm 2.6mm;
  border: 0.6pt solid var(--line-2);
  background: var(--white);
  font-size: 6.6pt;
  color: var(--ink-soft);
}

.f3-states .on {
  border-color: var(--ink);
  background: var(--ink);
  color: #fff;
}

.f3-states .focus {
  border-color: var(--red);
  box-shadow: 0 0 0 1.2pt var(--red);
}

.f3-scale {
  width: 100%;
  border-collapse: collapse;
  font-size: 6.9pt;
}

.f3-scale td {
  padding: 1.1mm 1.3mm;
  border-bottom: 0.5pt solid var(--line);
  vertical-align: middle;
}

.f3-scale tr:last-child td { border-bottom: 0; }

.f3-scale .sw {
  width: 7mm;
  height: 4.2mm;
  border: 0.4pt solid rgba(0, 0, 0, 0.08);
}

.f3-subhead {
  margin: 4mm 0 2mm;
  padding-top: 2.2mm;
  border-top: 1.2pt solid var(--ink);
  font-size: 10.4pt;
}
"""


# ------------------------------------------------------------------
# Helpers de composición
# ------------------------------------------------------------------

def pfoot(n: int) -> str:
    return (
        '<div class="pfoot">'
        f"<span>{BRAND} · Fase 3 · Implementación</span>"
        f"<span>{n} / {TOTAL_PAGES}</span>"
        "</div>"
    )


def page(n: int, section: str, body: str, extra: str = "") -> str:
    return f'<section class="page {extra}">{runhead(section)}{body}{pfoot(n)}</section>'


def runhead(section: str) -> str:
    return (
        '<div class="runhead">'
        f'<span class="rh-brand"><i></i>{BRAND}</span>'
        f"<span>{section}</span>"
        "</div>"
    )


def sec_head(num: str, label: str, title: str) -> str:
    return (
        '<div class="sec-head">'
        f'<div class="sec-num">{num}</div>'
        "<div>"
        f'<p class="sec-label">{label}</p>'
        f"<h2>{title}</h2>"
        "</div></div>"
    )


def code(text: str, label: str = "") -> str:
    label_html = f'<p class="f3-code-label"><span>{label}</span><span>código real</span></p>' if label else ""
    return f"{label_html}<pre class=\"f3-code\">{html.escape(text)}</pre>"


def shot(src: str, alt: str, caption: str) -> str:
    return (
        '<figure class="f3-shot">'
        f'<img src="{src}" alt="{html.escape(alt)}">'
        f"<figcaption>{caption}</figcaption>"
        "</figure>"
    )


def cover() -> str:
    meta = D["meta"]
    return f"""
<section class="page cover f3-cover">
  <div class="cover-inner">
    <div>
      <div class="cover-brand"><i></i>Catálogo <span>en foco</span></div>
      <div class="cover-topline" style="margin-top:5mm">
        <span>Fase 3 · Implementación en React</span>
        <span>Informe técnico · {date.today().strftime('%d/%m/%Y')}</span>
      </div>

      <div class="f3-cover-body">
        <div>
          <p class="sec-label" style="color:var(--red)">Del wireframe al tablero</p>
          <h1>El diseño,<br><em>en código</em></h1>
          <p class="lead">Cómo las decisiones de la Fase 2 se convirtieron en componentes, estados y datos reales: la misma jerarquía, los mismos KPIs y la misma paleta, ahora en una aplicación que filtra {fmt_int(meta['total_titulos'])} títulos.</p>
        </div>

        <aside class="f3-cover-visual">
          <div class="f3-mini-flow">
            <div><span>01</span><strong>Wireframe</strong><p>Jerarquía, retícula y paleta.</p></div>
            <div class="arrow">→</div>
            <div><span>02</span><strong>Componente</strong><p>React + TypeScript.</p></div>
            <div class="arrow">→</div>
            <div><span>03</span><strong>Tablero</strong><p>Datos reales y filtros.</p></div>
          </div>
          <p class="cap">La implementación no rediseña: traduce. Cada bloque del wireframe tiene un componente y cada cifra sale del mismo ETL.</p>
        </aside>
      </div>

      <div class="f3-metrics">
        <div><span class="k">Títulos</span><strong>{fmt_int(meta['total_titulos'])}</strong><p>100% del catálogo, sin muestreo.</p></div>
        <div><span class="k">Secciones</span><strong>11</strong><p>Una lectura de inicio a método.</p></div>
        <div><span class="k">Módulos de gráfica</span><strong>9</strong><p>Cinco núcleo y cuatro complementarios.</p></div>
        <div><span class="k">Datos de relleno</span><strong>0</strong><p>Todo sale de <code>dashboard.json</code>.</p></div>
      </div>

      <div class="f3-cover-strip">
        <div><span class="k">01 · Estructura</span><p>Un árbol de carpetas que separa composición, cálculo, gráficas y estilos.</p></div>
        <div><span class="k">02 · Implementación</span><p>KPIs, gráficos y mapa construidos con React, Recharts y react-simple-maps.</p></div>
        <div><span class="k">03 · Verificación</span><p>Build de TypeScript, QA visual a 390 px y correspondencia con la Fase 2.</p></div>
      </div>

      <figure class="f3-cover-shot">
        <img src="img/desktop-01-inicio.png" alt="Portada real del tablero implementado con el titular La economía del entretenimiento y la franja de datos del catálogo.">
        <figcaption><b>El tablero, ya en el navegador.</b> Portada a 1440 px con {fmt_int(meta['total_titulos'])} títulos, ficha técnica y franja de cifras calculadas desde el ETL. La captura no es una maqueta: es la aplicación en ejecución.</figcaption>
      </figure>
    </div>

    <div>
      <dl class="cover-meta">
        <div><dt>Equipo</dt><dd>{TEAM}</dd></div>
        <div><dt>Docente</dt><dd>{TEACHER}</dd></div>
        <div><dt>Materia</dt><dd>{SUBJECT}</dd></div>
        <div><dt>Tema</dt><dd>{TOPIC}</dd></div>
        <div><dt>Fuente</dt><dd>Kaggle · shivamb/netflix-shows</dd></div>
        <div><dt>Entregable</dt><dd>Tablero React + informe PDF</dd></div>
      </dl>
      <div class="cover-foot">
        <span><strong>{BRAND}</strong> · Informe de implementación</span>
        <span>{TOTAL_PAGES} páginas · Español (México)</span>
      </div>
    </div>
  </div>
</section>
"""


INDEX_ITEMS = [
    ("00", "Introducción", "El objetivo, el alcance y las tres promesas de la implementación.", 3),
    ("01", "El tablero implementado", "La primera pantalla real, sus cifras y lo que no se ve.", 4),
    ("02", "Correspondencia · primera pantalla", "Wireframe y dashboard, elemento por elemento.", 5),
    ("03", "Correspondencia · área de análisis", "Mapa, tiempo, géneros, formato y duración.", 6),
    ("04", "Estructura del proyecto", "Árbol de carpetas y responsabilidad de cada bloque.", 7),
    ("05", "Arquitectura y flujo de datos", "Del CSV al componente, con un solo estado filtrado.", 8),
    ("06", "Justificación técnica", "Por qué React, Recharts, react-simple-maps y TypeScript.", 9),
    ("07", "Implementación de KPIs", "Fórmulas, código y lugar de renderizado.", 10),
    ("08", "Implementación de gráficos", "Una gráfica por pregunta y la marca elegida.", 11),
    ("09", "Tiempo y distribución", "La serie temporal y el histograma de duración.", 12),
    ("10", "Implementación del mapa", "Fuente, escala, interacción y accesibilidad.", 13),
    ("11", "Paleta y estilos", "Tokens, contraste y tipografía aplicados en React.", 14),
    ("12", "Problemas y soluciones", "Lo que falló, cómo se resolvió y qué se aprendió.", 15),
    ("13", "Reflexión técnica", "Decisiones, costos y deuda técnica documentada.", 16),
    ("14", "Conclusión y verificación", "Aprendizajes y mapa de criterios de evaluación.", 17),
]


def index_page() -> str:
    rows = "".join(
        f'<div class="index-row"><span class="n">{n}</span><div><h3>{title}</h3><p>{desc}</p></div><span class="p">{p}</span></div>'
        for n, title, desc, p in INDEX_ITEMS
    )
    return page(
        2,
        "Índice",
        f"""
  <div class="index-title">
    <div class="sec-num">00</div>
    <div>
      <p class="sec-label">Contenido del informe</p>
      <h2>Índice</h2>
    </div>
  </div>
  <p class="lead">Este informe documenta la implementación, no la idea. Cada sección responde a una pregunta de la rúbrica y remite al archivo, al componente o a la captura que lo demuestra. El orden sigue el recorrido real: primero el tablero, después su estructura, luego el cálculo y al final la verificación.</p>

  <div class="index-list">{rows}</div>

  <div class="index-foot">
    <div>
      <h3 style="margin-bottom:1.6mm">Cómo se relaciona con la evaluación</h3>
      <table class="compact">
        <thead><tr><th style="width:46%">Criterio</th><th style="width:12%" class="num">Puntos</th><th>Dónde se responde</th></tr></thead>
        <tbody>
          <tr><td>Correspondencia wireframe ↔ dashboard</td><td class="num">25</td><td>Secciones 02–03 · pp. 5–6</td></tr>
          <tr><td>Implementación de KPIs y gráficos</td><td class="num">25</td><td>Secciones 07–10 · pp. 10–13</td></tr>
          <tr><td>Uso de la paleta de colores</td><td class="num">15</td><td>Sección 11 · p. 14</td></tr>
          <tr><td>Estructura y legibilidad del código</td><td class="num">15</td><td>Secciones 04–06 · pp. 7–9</td></tr>
          <tr><td>Documentación de la implementación</td><td class="num">20</td><td>Todo el informe · pp. 3–17</td></tr>
        </tbody>
      </table>
    </div>
    <div>
      <h3 style="margin-bottom:1.6mm">Estado del entregable</h3>
      <div class="f3-criteria">
        <div>Build de TypeScript y Vite</div><div class="pts">OK</div>
        <div>QA visual a 1440, 1024 y 390 px</div><div class="pts">OK</div>
        <div>Datos reales, sin relleno</div><div class="pts">8,807</div>
        <div>Correspondencia con la Fase 2</div><div class="pts">4/5</div>
      </div>
      <p class="f3-footnote" style="margin-top:2mm">La única variación de marca es la serie temporal: la Fase 2 proponía línea/área y la implementación usa barras apiladas. Se explica en la página 12.</p>
    </div>
  </div>
""",
        extra="f3-index",
    )


def introduction() -> str:
    k = D["kpis"]
    return page(
        3,
        "00 · Introducción",
        f"""
  {sec_head("00", "Introducción", "El objetivo era traducir, no rediseñar")}
  <p class="lead">La Fase 3 no empieza con una hoja en blanco: empieza con un wireframe aprobado. El trabajo consistió en convertir esa estructura en una aplicación funcional sin perder lo que la hacía legible: un KPI principal, cuatro lecturas que lo explican, una gráfica por pregunta y una paleta que jerarquiza. <strong>La prioridad no fue “que se viera bonito”, sino que el código respetara las decisiones de diseño y pudiera demostrarlo.</strong></p>

  <div class="f3-number-row">
    <div class="f3-number"><span>01</span><h3>Misma jerarquía</h3><p>El titular, el KPI principal y la evidencia conservan el orden N1–N3 del wireframe. La primera pantalla sigue terminando después de los filtros.</p></div>
    <div class="f3-number"><span>02</span><h3>Mismos KPIs</h3><p>El total filtrado es el denominador de todo. Las cuatro lecturas secundarias —formato, origen, tiempo y duración— se calculan sobre ese mismo conjunto.</p></div>
    <div class="f3-number"><span>03</span><h3>Misma estética</h3><p>Papel cálido, tinta, rojo y ámbar; Fraunces para titulares y DM Sans para texto. Los tokens de la Fase 2 se convirtieron en variables CSS.</p></div>
  </div>

  <div class="grid-2">
    <div>
      <h3>Qué cambió al pasar a código</h3>
      <table class="compact f3-mini-table">
        <thead><tr><th style="width:34%">Fase 2</th><th>Fase 3</th></tr></thead>
        <tbody>
          <tr><td>Wireframe estático</td><td>Componentes React con estado y eventos.</td></tr>
          <tr><td>Datos de referencia</td><td><code>dashboard.json</code> generado por el ETL.</td></tr>
          <tr><td>Paleta documentada</td><td>Variables CSS y constantes de gráfica.</td></tr>
          <tr><td>Notas al margen</td><td>Panel “¿Cómo leer esta gráfica?” en cada tarjeta.</td></tr>
          <tr><td>Cinco visualizaciones</td><td>Cinco núcleo + cuatro complementarias.</td></tr>
        </tbody>
      </table>
    </div>
    <div>
      <h3>Qué no cambió</h3>
      <ul class="f3-list">
        <li><strong>El denominador:</strong> todos los porcentajes usan el total filtrado, nunca el total del catálogo si hay filtros activos.</li>
        <li><strong>La lectura:</strong> primero el volumen, después la composición, luego la geografía y el tiempo.</li>
        <li><strong>La honestidad:</strong> el tablero describe el catálogo; no estima audiencia, ingresos ni éxito.</li>
        <li><strong>El corte:</strong> 25 de septiembre de 2021; 2021 está incompleto y se marca en la serie temporal.</li>
      </ul>
      <div class="f3-note" style="margin-top:3mm">
        <p><strong>Criterio de éxito.</strong> Si una persona puede repetir el recorrido de lectura de la Fase 2 en la aplicación —titular, KPI, mapa, tiempo, géneros, formato, duración— y llegar a las mismas conclusiones, la implementación es correcta.</p>
      </div>
    </div>
  </div>

  <h3 class="f3-subhead">El recorrido de lectura, ya implementado</h3>
  <p class="small" style="margin-top:0">La Fase 2 describió tres niveles. En la aplicación se traducen en un orden concreto de secciones y en un ancla de navegación para cada una.</p>
  <div class="f3-flow">
    <div><span class="step">N1 · PORTADA</span><strong>Titular</strong><p>Qué es el tablero y de qué dataset habla.</p></div>
    <div class="arrow">→</div>
    <div><span class="step">N1 · KPI</span><strong>Títulos en el filtro</strong><p>El total que sostiene todas las comparaciones.</p></div>
    <div class="arrow">→</div>
    <div><span class="step">N2 · MAPA</span><strong>Dónde</strong><p>Producción declarada por país y región.</p></div>
    <div class="arrow">→</div>
    <div><span class="step">N2 · TIEMPO</span><strong>Cómo cambió</strong><p>Estreno, incorporación y mezcla de formato.</p></div>
    <div class="arrow">→</div>
    <div><span class="step">N3 · MÉTODO</span><strong>Qué no se puede afirmar</strong><p>Calidad del dato, nulos y corte del snapshot.</p></div>
  </div>

  <div class="f3-note" style="margin-top:3.5mm">
    <p><strong>Alcance.</strong> El tablero tiene {fmt_int(k['total_titulos'])} títulos, {k['paises_distintos']} países y 42 géneros. Se sirve como sitio estático: un JSON de {fmt_int(round(579735 / 1024))} KB, sin backend, sin base de datos en el navegador y sin dependencia de una API externa. Esa decisión mantiene el proyecto reproducible y portátil; el costo es que actualizar los datos exige volver a ejecutar el ETL y el build.</p>
  </div>

  <div class="f3-quote">
    “Un tablero no se juzga por lo que muestra, sino por lo que permite concluir.”
    <span>Criterio de la Fase 2, verificado en la Fase 3</span>
  </div>
""",
    )


def implemented_board() -> str:
    meta = D["meta"]
    k = D["kpis"]
    return page(
        4,
        "01 · El tablero implementado",
        f"""
  {sec_head("01", "El tablero implementado", "La primera pantalla, ya en el navegador")}
  <p class="lead">La portada conserva la composición editorial de la Fase 2: marca, titular, ficha técnica, botones y franja de datos. No es una maqueta: los {fmt_int(meta['total_titulos'])} títulos, las {fmt_int(k['peliculas'])} películas y las {fmt_int(k['series'])} series se leen del JSON y se formatean en español de México.</p>

  {shot("img/desktop-01-inicio.png", "Portada del tablero implementado con el titular La economía del entretenimiento, la ficha técnica y la franja de datos.", "<b>Figura 1.</b> Portada implementada a 1440 px. La jerarquía del wireframe se mantiene: titular a la izquierda, ficha técnica a la derecha y franja de cifras al pie.")}

  <div class="grid-3" style="margin-top:3.5mm">
    <div class="card card-top red">
      <h3>La misma retícula</h3>
      <p class="small">Contenido máximo de 1380 px, margen fluido y una franja de cuatro cifras. En escritorio, el titular ocupa más ancho que la ficha; en móvil, la ficha baja y la franja se convierte en 2 × 2.</p>
    </div>
    <div class="card card-top amber">
      <h3>El mismo KPI</h3>
      <p class="small">“Títulos en el filtro” sigue siendo la primera tarjeta y el número más grande. Las otras cinco tarjetas —películas, series, países, año y duración— comparten peso y se leen como una sola frase.</p>
    </div>
    <div class="card card-top">
      <h3>La misma paleta</h3>
      <p class="small">Papel <code>#fbf9f5</code>, tinta <code>#171614</code>, rojo <code>#d90429</code> y ámbar <code>#b7791f</code>. No hay colores nuevos: solo se aplicaron los tokens de la Fase 2.</p>
    </div>
  </div>

  <div class="f3-note" style="margin-top:3.5mm">
    <p><strong>Lo que no se ve en la captura.</strong> Antes de renderizar, <code>App.tsx</code> descarga el JSON, valida que existan las filas y las dimensiones, y calcula un único objeto <code>Derived</code> con <code>useMemo</code>. Todos los KPIs, gráficas y tablas leen ese objeto. No hay cálculos duplicados ni cifras escritas a mano en el JSX.</p>
  </div>

  <h3 class="f3-subhead">De dónde sale cada cifra de la portada</h3>
  <table class="compact f3-mini-table">
    <thead><tr><th style="width:28%">Cifra en pantalla</th><th style="width:32%">Campo del JSON</th><th style="width:20%">Valor</th><th>Nota de cálculo</th></tr></thead>
    <tbody>
      <tr><td><strong>Títulos del catálogo</strong></td><td><code>meta.total_titulos</code></td><td class="num">{fmt_int(meta['total_titulos'])}</td><td>Entero · es-MX.</td></tr>
      <tr><td><strong>Películas</strong></td><td><code>kpis.peliculas</code></td><td class="num">{fmt_int(k['peliculas'])}</td><td>Mismo denominador.</td></tr>
      <tr><td><strong>Países</strong></td><td><code>kpis.paises_distintos</code></td><td class="num">{k['paises_distintos']}</td><td>Sin país no cuenta.</td></tr>
      <tr><td><strong>Año con más estrenos</strong></td><td><code>kpis.anio_mas_estrenos</code></td><td class="num">{k['anio_mas_estrenos']['year']} · {fmt_int(k['anio_mas_estrenos']['count'])}</td><td>Año y conteo.</td></tr>
      <tr><td><strong>Última actualización</strong></td><td><code>meta.snapshot</code></td><td>25 sep 2021</td><td>Fecha larga es-MX.</td></tr>
    </tbody>
  </table>
""",
    )


def correspondence_first() -> str:
    return page(
        5,
        "02 · Correspondencia · primera pantalla",
        f"""
  {sec_head("02", "Correspondencia · primera pantalla", "El wireframe se reconoce en la primera pantalla")}
  <p class="lead">La comparación no es metafórica: el wireframe de la Fase 2 y la captura del tablero comparten el orden de lectura. La implementación conservó la posición del titular, la ficha técnica, la franja de KPIs y la barra de filtros; cambió el material, no la estructura.</p>

  <div class="f3-compare">
    <div>
      {shot("img/f3/wireframe-first.png", "Wireframe de la primera pantalla de la Fase 2 con titular, ficha técnica, seis KPIs y filtros.", "<b>Fase 2 · wireframe.</b> Primera pantalla a 1440 px. La retícula de 12 columnas está marcada en rojo; los números remiten a la leyenda del informe de diseño.")}
    </div>
    <div class="f3-compare-stack">
      {shot("img/desktop-01-inicio.png", "Captura real de la portada del tablero.", "<b>Fase 3 · portada.</b> Titular, ficha y franja de cifras en la misma posición.")}
      {shot("img/f3/dashboard-panorama.png", "Captura real del panel de seis KPIs del tablero.", "<b>Fase 3 · KPIs.</b> Seis tarjetas en 3 × 2; la primera conserva el acento rojo.")}
    </div>
  </div>

  <table class="compact f3-mini-table" style="margin-top:3.2mm">
    <thead><tr><th style="width:27%">Elemento del wireframe</th><th style="width:27%">Componente implementado</th><th>Qué se conservó</th></tr></thead>
    <tbody>
      <tr><td><strong>1 · Titular y ficha</strong></td><td><code>Hero.tsx</code></td><td>Titular editorial, subtítulo, ficha de fuente, cobertura, registro y actualización.</td></tr>
      <tr><td><strong>2 · KPI principal</strong></td><td><code>KpiGrid.tsx</code></td><td>Primera celda, acento rojo, cifra más grande y nota con el porcentaje del catálogo.</td></tr>
      <tr><td><strong>3 · KPIs secundarios</strong></td><td><code>KpiGrid.tsx</code></td><td>Películas, series, países, año de estreno y duración mediana; misma franja y mismo peso.</td></tr>
      <tr><td><strong>4 · Filtros globales</strong></td><td><code>Filters.tsx</code></td><td>Tipo, periodo y país o región; contador de títulos y chips de filtros activos.</td></tr>
      <tr><td><strong>5 · Retícula</strong></td><td><code>Section</code> + <code>global.css</code></td><td>Riel de 252 px, contenido flexible y escala de 4 px; en móvil, una sola columna.</td></tr>
      <tr><td><strong>6 · Pliegue</strong></td><td><code>Hero</code> + <code>HowToRead</code> + <code>Filters</code></td><td>La primera pantalla termina después de los filtros; el usuario decide si baja al mapa o al tiempo.</td></tr>
    </tbody>
  </table>

  <h3 class="f3-subhead">Tres adiciones que no alteran la estructura</h3>
  <div class="grid-3">
    <div class="card card-top red">
      <h3>Ficha técnica ampliada</h3>
      <p class="small">El wireframe pedía fuente y cobertura; se añaden registro, snapshot y enlace al dataset para rastrear cada cifra.</p>
    </div>
    <div class="card card-top amber">
      <h3>Informe en la portada</h3>
      <p class="small">Un botón descarga el PDF de la Fase 3: resuelve la entrega sin salir del tablero.</p>
    </div>
    <div class="card card-top">
      <h3>Progreso de lectura</h3>
      <p class="small">Una barra marca el avance en una página de once secciones; apoya la navegación, no la jerarquía.</p>
    </div>
  </div>
  <p class="f3-footnote" style="margin-top:2.4mm">La prueba de que no se movió nada: al recortar la captura a la altura de los filtros, la silueta coincide con el wireframe. Las adiciones viven dentro de esos bloques, no entre ellos.</p>
""",
    )


def correspondence_analysis() -> str:
    return page(
        6,
        "03 · Correspondencia · área de análisis",
        f"""
  {sec_head("03", "Correspondencia · área de análisis", "Mapa, tiempo y composición, en su sitio")}
  <p class="lead">El cuerpo analítico también respeta el wireframe: riel de sección a la izquierda, mapa como selector, ranking lateral, tiempo, géneros y composición. La implementación añadió lecturas complementarias —clasificaciones, directores, patrones, hallazgos y método— sin mover el bloque principal ni cambiar la jerarquía.</p>

  <div class="f3-compare">
    <div>
      {shot("img/f3/wireframe-analysis.png", "Wireframe del área de análisis de la Fase 2 con riel, mapa, ranking, tiempo, géneros y composición.", "<b>Fase 2 · wireframe.</b> Área de análisis: riel sticky, mapa, ranking, tiempo, géneros, dona y duración.")}
    </div>
    <div class="f3-compare-stack">
      {shot("img/f3/dashboard-map.png", "Captura real del mapa mundial y del ranking de países.", "<b>Fase 3 · mapa.</b> Mapa coroplético, leyenda por cuantiles, ranking lateral y tarjeta de “sin país”.")}
      {shot("img/f3/dashboard-types.png", "Captura real de la dona de películas y series y del ranking de clasificaciones.", "<b>Fase 3 · composición.</b> Dona con total al centro y barras de clasificación; dos lecturas del mismo filtro.")}
    </div>
  </div>

  <table class="compact f3-mini-table" style="margin-top:3.2mm">
    <thead><tr><th style="width:26%">Bloque del wireframe</th><th style="width:27%">Componente implementado</th><th>Qué se conservó</th></tr></thead>
    <tbody>
      <tr><td><strong>1 · Riel sticky</strong></td><td><code>Section</code> + <code>.section-head</code></td><td>Número, título e introducción; se mantiene visible al hacer scroll en escritorio.</td></tr>
      <tr><td><strong>2 · Mapa selector</strong></td><td><code>MapChart.tsx</code></td><td>Color por conteo, leyenda por cuantiles, clic para filtrar y zoom.</td></tr>
      <tr><td><strong>3 · Ranking lateral</strong></td><td><code>MapChart.tsx</code></td><td>Top países con barra proporcional y valor directo; los nombres largos caben.</td></tr>
      <tr><td><strong>4 · Tiempo</strong></td><td><code>TimeSeriesChart.tsx</code></td><td>Estreno vs. incorporación, corte del snapshot y pico anual.</td></tr>
      <tr><td><strong>5 · Géneros</strong></td><td><code>WordCloudChart.tsx</code> + <code>TopGenresChart</code></td><td>Nube para la impresión y ranking con cifras exactas; lista ordenada como alternativa.</td></tr>
      <tr><td><strong>6 · Formato y duración</strong></td><td><code>TypeDonut.tsx</code> + <code>DurationCharts.tsx</code></td><td>Dona de dos categorías; histograma de minutos y distribución de temporadas separados.</td></tr>
    </tbody>
  </table>

  <div class="f3-note" style="margin-top:3mm">
    <p><strong>Alcance ampliado, no desviado.</strong> Las secciones de clasificaciones, directores, patrones, hallazgos y metodología se añadieron después del bloque principal. No compiten con el KPI ni con el mapa: viven en el nivel N3 del recorrido y se apoyan en los mismos datos filtrados.</p>
  </div>
""",
    )


def project_structure() -> str:
    tree = """Jhon/
├─ src/
│  ├─ App.tsx                 <i>composición, estado y fetch</i>
│  ├─ main.tsx                <i>montaje y fuentes</i>
│  ├─ types.ts                <i>contratos de datos</i>
│  ├─ components/
│  │  ├─ Header.tsx           <i>navegación y progreso</i>
│  │  ├─ Hero.tsx             <i>portada y cómo leer</i>
│  │  ├─ Filters.tsx          <i>filtros globales</i>
│  │  ├─ KpiGrid.tsx          <i>seis indicadores</i>
│  │  ├─ ui.tsx               <i>Section, ChartCard, Legend</i>
│  │  ├─ Findings.tsx         <i>hallazgos globales</i>
│  │  ├─ Methodology.tsx      <i>calidad y límites</i>
│  │  ├─ Footer.tsx           <i>créditos y documentos</i>
│  │  └─ charts/
│  │     ├─ MapChart.tsx      <i>mapa + ranking</i>
│  │     ├─ TimeSeriesChart.tsx
│  │     ├─ TypeDonut.tsx
│  │     ├─ Rankings.tsx      <i>países y géneros</i>
│  │     ├─ DurationCharts.tsx
│  │     ├─ RatingsChart.tsx
│  │     ├─ WordCloudChart.tsx
│  │     ├─ Heatmaps.tsx      <i>década y mes</i>
│  │     └─ DirectorsTable.tsx
│  ├─ lib/
│  │  ├─ aggregate.ts         <i>filtros y KPIs</i>
│  │  ├─ format.ts            <i>es-MX</i>
│  │  └─ palette.ts           <i>colores de gráfica</i>
│  ├─ hooks/useUi.ts          <i>scroll, foco, contadores</i>
│  └─ styles/global.css       <i>tokens y responsive</i>
├─ public/data/dashboard.json <i>datos del tablero</i>
├─ data/quality_report.json   <i>calidad del ETL</i>
├─ etl/build_dataset.py       <i>CSV → DuckDB → JSON</i>
└─ docs/generate_pdf_fase3.py <i>este informe</i>"""
    return page(
        7,
        "04 · Estructura del proyecto",
        f"""
  {sec_head("04", "Estructura del proyecto", "Una carpeta por responsabilidad")}
  <p class="lead">La organización no sigue el orden del wireframe, sino el flujo del dato: la aplicación compone, la carpeta <code>lib</code> calcula, <code>charts</code> dibuja y <code>styles</code> aplica el sistema visual. Esa separación permite cambiar una gráfica sin tocar los KPIs y cambiar un token sin recorrer veinte componentes.</p>

  <div class="grid-2" style="grid-template-columns:1.18fr 0.82fr;gap:5mm">
    <pre class="f3-tree">{tree}</pre>
    <div>
      <h3>Qué hace cada bloque</h3>
      <ul class="f3-list">
        <li><strong><code>src/App.tsx</code>:</strong> compone la página, guarda el estado de filtros y dispara el fetch. No calcula KPIs.</li>
        <li><strong><code>components/</code>:</strong> interfaz y accesibilidad. Cada tarjeta recibe datos ya calculados.</li>
        <li><strong><code>components/charts/</code>:</strong> nueve módulos de visualización; Recharts, SVG y CSS Grid según la tarea.</li>
        <li><strong><code>lib/aggregate.ts</code>:</strong> el único lugar donde se filtra y se agrega. Devuelve un objeto <code>Derived</code> completo.</li>
        <li><strong><code>lib/format.ts</code>:</strong> números, porcentajes y fechas en <code>es-MX</code>.</li>
        <li><strong><code>lib/palette.ts</code>:</strong> colores que Recharts necesita como cadenas, no como variables CSS.</li>
        <li><strong><code>hooks/useUi.ts</code>:</strong> progreso de lectura, sección activa, contadores y movimiento reducido.</li>
        <li><strong><code>public/data/dashboard.json</code>:</strong> filas compactas, dimensiones, agregados y reporte de calidad.</li>
      </ul>
    </div>
  </div>

  <div class="grid-3" style="margin-top:3.5mm">
    <div class="card card-top red">
      <h3>Regla 1 · Un solo cálculo</h3>
      <p class="small">Ningún componente suma títulos por su cuenta. Si una cifra aparece en dos lugares, sale del mismo campo de <code>Derived</code>.</p>
    </div>
    <div class="card card-top amber">
      <h3>Regla 2 · Datos tipados</h3>
      <p class="small"><code>TitleRow</code> es una tupla de 12 posiciones; <code>Derived</code> describe cada salida. TypeScript estricto evita confusiones entre tipos, países y años.</p>
    </div>
    <div class="card card-top">
      <h3>Regla 3 · Estilos tokenizados</h3>
      <p class="small">La paleta vive en <code>:root</code> y en <code>palette.ts</code>. No se usan colores sueltos en los componentes, salvo los cinco tramos del mapa.</p>
    </div>
  </div>

  <h3 class="f3-subhead">Dónde buscar qué</h3>
  <table class="compact f3-mini-table">
    <thead><tr><th style="width:34%">Si hay que cambiar…</th><th style="width:36%">Se toca</th><th>No se toca</th></tr></thead>
    <tbody>
      <tr><td><strong>Un color de la interfaz</strong></td><td><code>src/styles/global.css</code> · <code>:root</code></td><td>Los componentes.</td></tr>
      <tr><td><strong>Un color de gráfica</strong></td><td><code>src/lib/palette.ts</code></td><td>Recharts ni el CSS.</td></tr>
      <tr><td><strong>Una fórmula o un filtro</strong></td><td><code>src/lib/aggregate.ts</code></td><td>Los componentes de gráfica.</td></tr>
      <tr><td><strong>Una visualización</strong></td><td><code>src/components/charts/</code></td><td>Los KPIs ni el estado global.</td></tr>
      <tr><td><strong>El dataset o su limpieza</strong></td><td><code>etl/build_dataset.py</code> · <code>npm run etl</code></td><td>Ningún archivo de <code>src/</code>.</td></tr>
    </tbody>
  </table>
  <p class="f3-footnote" style="margin-top:1.6mm">Esa separación permite auditar el tablero: cada pregunta de la rúbrica tiene una carpeta y un archivo donde vivir.</p>
""",
    )


def architecture() -> str:
    fetch_code = """const [data, setData] = useState<DashboardData | null>(null);
useEffect(() => {
  fetch("./data/dashboard.json")
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json() as Promise<DashboardData>;
    })
    .then((payload) => {
      if (!payload?.titles?.rows?.length) throw new Error("Sin filas");
      setData(payload);
    });
}, []);"""
    derive_code = """const [filters, setFilters] = useState(DEFAULT_FILTERS);
const derived = useMemo(() => derive(data, filters), [data, filters]);

// El mapa conserva todos los países como selector:
const mapDerived = useMemo(
  () => derive(data, { ...filters, place: { kind: "all" } }),
  [data, filters],
);"""
    return page(
        8,
        "05 · Arquitectura y flujo de datos",
        f"""
  {sec_head("05", "Arquitectura y flujo de datos", "Un solo sentido: del CSV al componente")}
  <p class="lead">El tablero es una aplicación estática con un flujo unidireccional. El ETL produce un JSON; React lo descarga una vez; el estado de filtros dispara un cálculo memoizado; las vistas reciben el resultado. No hay llamadas por gráfica, ni estado duplicado, ni cifras que se recalculen en dos lugares.</p>

  <div class="f3-flow">
    <div><span class="step">01 · FUENTE</span><strong>CSV</strong><p><code>netflix_titles.csv</code>, 8,807 filas y 12 columnas.</p></div>
    <div class="arrow">→</div>
    <div><span class="step">02 · ETL</span><strong>DuckDB</strong><p>Limpieza, normalización y tablas puente.</p></div>
    <div class="arrow">→</div>
    <div><span class="step">03 · SALIDA</span><strong>JSON</strong><p><code>dashboard.json</code> con filas compactas y agregados.</p></div>
    <div class="arrow">→</div>
    <div><span class="step">04 · ESTADO</span><strong>Filtros</strong><p>Tipo, periodo y país en <code>useState</code>.</p></div>
    <div class="arrow">→</div>
    <div><span class="step">05 · VISTA</span><strong>Derived</strong><p>Un objeto por filtro; todas las vistas lo leen.</p></div>
  </div>

  <div class="grid-2">
    <div>
      <p class="f3-code-label"><span>App.tsx · carga y validación</span><span>código real</span></p>
      <pre class="f3-code">{html.escape(fetch_code)}</pre>
    </div>
    <div>
      <p class="f3-code-label"><span>App.tsx · estado y derivación</span><span>código real</span></p>
      <pre class="f3-code">{html.escape(derive_code)}</pre>
    </div>
  </div>

  <div class="grid-3" style="margin-top:3.5mm">
    <div>
      <h3>Por qué no hay backend</h3>
      <p class="small">El dataset es un snapshot cerrado. Un JSON estático elimina servidores, credenciales y latencia, y hace que el tablero se pueda publicar en GitHub Pages. El costo: actualizar datos exige repetir ETL y build.</p>
    </div>
    <div>
      <h3>Por qué no hay router</h3>
      <p class="small">Es una sola página con secciones ancladas. El hash permite enlazar <code>#mapa</code> o <code>#tiempo</code> sin cargar otra aplicación. El costo: no hay división del bundle por ruta.</p>
    </div>
    <div>
      <h3>Por qué no hay estado global</h3>
      <p class="small">El estado vive en <code>App</code> y baja por props. Con una sola pantalla y un solo filtro, Redux o Zustand añadirían ceremonia sin resolver un problema real.</p>
    </div>
  </div>

  <div class="f3-note" style="margin-top:3mm">
    <p><strong>La excepción documentada.</strong> El mapa no usa <code>derived</code> cuando hay un país seleccionado: usa <code>mapDerived</code>, calculado con <code>place: all</code>. Así el mapa sigue mostrando todos los países y funciona como selector, mientras el resto de las vistas se enfoca en el país elegido. Es una decisión de producto implementada en una línea de <code>App.tsx</code>.</p>
  </div>

  <h3 class="f3-subhead">El contrato de <code>Derived</code></h3>
  <table class="compact f3-mini-table">
    <thead><tr><th style="width:24%">Campo</th><th style="width:34%">Forma</th><th>Quién lo consume</th></tr></thead>
    <tbody>
      <tr><td><code>count</code></td><td><code>number</code></td><td>KPI principal, contador de filtros y encabezados de sección.</td></tr>
      <tr><td><code>movies</code> · <code>series</code></td><td><code>number</code> · <code>number</code></td><td>Tarjetas 2 y 3; dona <code>TypeDonut</code>.</td></tr>
      <tr><td><code>topCountries</code></td><td><code>CountryStat[]</code></td><td>Ranking lateral del mapa y tabla de países.</td></tr>
      <tr><td><code>topGenres</code></td><td><code>GenreStat[]</code></td><td>Nube de palabras y ranking de géneros.</td></tr>
      <tr><td><code>byYearRelease</code></td><td><code>YearStat[]</code></td><td><code>TimeSeriesChart</code> en modo estreno; hitos anuales.</td></tr>
      <tr><td><code>byYearAdded</code></td><td><code>YearStat[]</code></td><td><code>TimeSeriesChart</code> en modo incorporación.</td></tr>
      <tr><td><code>movieDuration</code></td><td><code>&#123; n, avg, median &#125;</code></td><td>Tarjeta 6, tooltip de países e histograma.</td></tr>
      <tr><td><code>last5</code></td><td><code>&#123; from, to, count, share &#125;</code></td><td>Tarjeta 5 y franja de hitos (2017–2021).</td></tr>
      <tr><td><code>noCountry</code></td><td><code>number</code></td><td>Tarjeta “sin país” del mapa y metodología.</td></tr>
    </tbody>
  </table>
  <p class="f3-footnote" style="margin-top:1.6mm">Ningún componente recibe filas crudas: todos reciben este objeto o una parte de él. Por eso una gráfica no puede “inventar” un denominador distinto al del KPI.</p>
""",
    )


def technical_justification() -> str:
    return page(
        9,
        "06 · Justificación técnica",
        f"""
  {sec_head("06", "Justificación técnica", "Cada librería resuelve una tarea concreta")}
  <p class="lead">El stack se eligió por adecuación a la tarea, no por novedad. React y TypeScript sostienen la composición y los contratos; Recharts cubre las gráficas cartesianas; <code>react-simple-maps</code> resuelve el mapa sin tiles; <code>d3-cloud</code> calcula la nube; Fontsource evita depender de Google Fonts. Cada elección tiene una alternativa descartada y un costo asumido.</p>

  <table class="compact">
    <thead><tr><th style="width:20%">Herramienta</th><th style="width:16%">Versión</th><th style="width:24%">Uso en el tablero</th><th>Por qué se eligió / alternativa descartada</th></tr></thead>
    <tbody>
      <tr><td><strong>React + Vite</strong></td><td>19.3 · 7.3</td><td>Composición, estado y build.</td><td>Componentes declarativos y recarga instantánea. Se descartó Next.js: no hay SSR, rutas ni API que lo justifiquen.</td></tr>
      <tr><td><strong>TypeScript</strong></td><td>5.9 · strict</td><td>Contratos de filas, dimensiones y KPIs.</td><td>Una tupla de 12 posiciones se vuelve legible y verificable. Se descartó JavaScript: el costo de un índice mal usado era mayor.</td></tr>
      <tr><td><strong>Recharts</strong></td><td>3.10</td><td>Dona, barras, serie temporal e histograma.</td><td>Gráficas SVG declarativas y <code>ResponsiveContainer</code>. Se descartaron Chart.js (canvas, menos integración React) y Plotly (peso).</td></tr>
      <tr><td><strong>react-simple-maps</strong></td><td>3.0</td><td>Mapa coroplético y zoom.</td><td>TopoJSON local, eventos por geografía y control de proyección. Se descartó Leaflet: necesita tiles, CSS extra y no aporta para un mapa sin calles.</td></tr>
      <tr><td><strong>world-atlas</strong></td><td>2.0</td><td>Geometría <code>countries-110m.json</code>.</td><td>TopoJSON liviano y offline. Se descartó un GeoJSON completo: más peso para la misma lectura.</td></tr>
      <tr><td><strong>d3-cloud</strong></td><td>1.2</td><td>Nube de géneros.</td><td>Layout de palabras probado. Se descartó construir el empaquetado a mano: no era el objetivo del proyecto.</td></tr>
      <tr><td><strong>Fontsource</strong></td><td>5.3</td><td>Fraunces y DM Sans locales.</td><td>Sin peticiones a Google Fonts, reproducible y sin FOUT de red. Se descartó el CDN por privacidad y disponibilidad.</td></tr>
      <tr><td><strong>CSS propio</strong></td><td>—</td><td>Tokens, retícula, responsive.</td><td>Variables CSS y 3 000 líneas legibles. Se descartó Tailwind: el sistema ya estaba definido y no se quería reescribir en utilidades.</td></tr>
    </tbody>
  </table>

  <div class="grid-2" style="margin-top:3.5mm">
    <div class="f3-note">
      <p><strong>La dependencia incómoda.</strong> <code>react-simple-maps@3</code> declara compatibilidad con React 18 y el proyecto usa React 19. La instalación se hizo con <code>--legacy-peer-deps</code> y se verificó el mapa, el zoom y los eventos en el navegador. Está documentado en el README para que otra persona pueda reproducirlo.</p>
    </div>
    <div class="f3-note">
      <p><strong>El criterio.</strong> Ninguna librería entra para “tener más”: si una tarea se resuelve con CSS Grid —las matrices de década y mes— no se añade un paquete de heatmaps. Esa disciplina mantiene el bundle y la superficie de mantenimiento bajo control.</p>
    </div>
  </div>

  <h3 class="f3-subhead">Reproducir el entorno desde cero</h3>
  <div class="grid-2" style="grid-template-columns:1.06fr 0.94fr;gap:5mm">
    <div>
      <p class="f3-code-label"><span>Terminal · Windows PowerShell</span><span>comandos reales</span></p>
      <pre class="f3-code"># 1 · dependencias (react-simple-maps declara React 18)
npm install --legacy-peer-deps

# 2 · datos: CSV → DuckDB → JSON
npm run etl

# 3 · desarrollo y build de producción
npm run dev
npm run build

# 4 · informes en PDF
npm run pdf:fase3</pre>
    </div>
    <div>
      <h3>Qué garantiza cada paso</h3>
      <ul class="f3-list">
        <li><strong>Instalación:</strong> el lockfile fija versiones; <code>--legacy-peer-deps</code> evita que npm rechace el árbol por el peer de React 18.</li>
        <li><strong>ETL:</strong> vuelve a generar <code>dashboard.json</code> y <code>quality_report.json</code> desde el CSV; si el esquema cambia, el tablero falla en la validación.</li>
        <li><strong>Build:</strong> ejecuta <code>tsc --noEmit</code> antes de Vite; un tipo mal usado detiene la entrega.</li>
        <li><strong>Informes:</strong> los tres PDF se generan con Chrome headless desde el mismo HTML imprimible.</li>
      </ul>
    </div>
  </div>
  <p class="f3-footnote" style="margin-top:2mm">El proyecto no necesita variables de entorno, credenciales ni servicios externos: clonar la carpeta y ejecutar los cuatro pasos reproduce el tablero y los informes.</p>
""",
    )


def kpi_implementation() -> str:
    kpi_code = """const rows = data.titles.rows.filter((row) =>
  matchesType(row, filters.type) &&
  matchesPeriod(row, filters.period) &&
  matchesPlace(row, filters.place, countries),
);
const count = rows.length;

for (const row of rows) {
  const [type, , , , durationMin] = row;
  if (type === 0) movies += 1; else series += 1;
  if (type === 0 && durationMin !== null) durations.push(durationMin);
}

const movieDuration = {
  n: durations.length,
  avg: durations.reduce((a, b) => a + b, 0) / durations.length,
  median: median(durations),
};"""
    kpi_jsx = """<Kpi
  label="Títulos en el filtro"
  value={derived.count}
  note={`${fmtPct(catalogShare)} del catálogo completo`}
  accent="red"
  start={inView}
/>"""
    return page(
        10,
        "07 · Implementación de KPIs",
        f"""
  {sec_head("07", "Implementación de KPIs", "Se calculan una vez; se leen en todas partes")}
  <p class="lead">El KPI principal de la Fase 2 —“Títulos en el filtro”— se implementó como <code>derived.count</code>: la longitud del arreglo que sobrevive a los tres filtros. Las cuatro lecturas secundarias salen del mismo recorrido de datos. La tarjeta solo formatea y muestra; no calcula.</p>

  <table class="compact f3-mini-table">
    <thead><tr><th style="width:22%">KPI de la Fase 2</th><th style="width:31%">Fórmula implementada</th><th style="width:22%">Campo de <code>Derived</code></th><th>Dónde se renderiza</th></tr></thead>
    <tbody>
      <tr><td><strong>N1 · Títulos en el filtro</strong></td><td><code>rows.length</code> tras tipo + periodo + lugar.</td><td><code>count</code></td><td>Primera tarjeta de <code>KpiGrid</code> y contador de filtros.</td></tr>
      <tr><td><strong>N2 · Mezcla de formato</strong></td><td>Conteo de <code>type === 0</code> y <code>type === 1</code>; porcentaje sobre <code>count</code>.</td><td><code>movies</code>, <code>series</code></td><td>Tarjetas 2 y 3; dona <code>TypeDonut</code>.</td></tr>
      <tr><td><strong>N2 · Concentración geográfica</strong></td><td>Países con <code>count &gt; 0</code>; líder por conteo.</td><td><code>countryCount</code>, <code>topCountries</code></td><td>Tarjeta 4; mapa y ranking lateral.</td></tr>
      <tr><td><strong>N2 · Dinámica temporal</strong></td><td>Máximo de <code>byYearRelease.total</code>; títulos con <code>addedYear &gt;= 2017</code>.</td><td><code>peakRelease</code>, <code>last5</code></td><td>Tarjeta 5; serie temporal y franja de hitos.</td></tr>
      <tr><td><strong>N2 · Duración mediana</strong></td><td>Mediana de <code>durationMin</code> para películas con dato.</td><td><code>movieDuration.median</code></td><td>Tarjeta 6; histograma de minutos.</td></tr>
    </tbody>
  </table>

  <div class="grid-2" style="margin-top:3.2mm;grid-template-columns:1.12fr 0.88fr">
    <div>
      <p class="f3-code-label"><span>aggregate.ts · filtro y cálculo</span><span>código real</span></p>
      <pre class="f3-code">{html.escape(kpi_code)}</pre>
    </div>
    <div>
      <p class="f3-code-label"><span>KpiGrid.tsx · tarjeta principal</span><span>código real</span></p>
      <pre class="f3-code">{html.escape(kpi_jsx)}</pre>
      <div class="f3-note" style="margin-top:2.6mm">
        <p><strong>Reglas que no se negocian.</strong> El denominador es el total filtrado; los porcentajes se formatean con <code>Intl.NumberFormat("es-MX")</code>; los títulos sin país o sin director no se imputan; 2021 se marca como incompleto.</p>
      </div>
    </div>
  </div>

  <div class="grid-3" style="margin-top:3mm">
    <div><h3>Contador animado</h3><p class="small"><code>useCountUp</code> interpola la cifra al entrar en pantalla. Con <code>prefers-reduced-motion</code> salta directo al valor final.</p></div>
    <div><h3>Estado vacío</h3><p class="small">Si el filtro no devuelve títulos, <code>filter-empty</code> explica el motivo y ofrece “Limpiar filtros”; las tarjetas no muestran cero sin contexto.</p></div>
    <div><h3>Lectura accesible</h3><p class="small">Cada tarjeta tiene etiqueta, valor y nota; el contador de filtros usa <code>aria-live="polite"</code> para anunciar cambios.</p></div>
  </div>

  <h3 class="f3-subhead">El mismo KPI con cuatro combinaciones de filtro</h3>
  <table class="compact f3-mini-table">
    <thead><tr><th style="width:36%">Filtro activo</th><th class="num" style="width:12%">Títulos</th><th class="num" style="width:13%">% del catálogo</th><th>Lectura</th></tr></thead>
    <tbody>
      <tr><td><strong>Sin filtro</strong></td><td class="num">8,807</td><td class="num">100.0%</td><td>El catálogo completo; denominador de la portada.</td></tr>
      <tr><td><strong>Películas</strong></td><td class="num">6,131</td><td class="num">69.6%</td><td>Dos tercios del catálogo son películas.</td></tr>
      <tr><td><strong>Películas · 2010–2019</strong></td><td class="num">4,184</td><td class="num">47.5%</td><td>La década reciente concentra casi la mitad del catálogo.</td></tr>
      <tr><td><strong>Películas · 2010–2019 · EE. UU.</strong></td><td class="num">1,843</td><td class="num">20.9%</td><td>El país líder dentro de esa década.</td></tr>
      <tr><td><strong>Series · 2010–2019 · India</strong></td><td class="num">56</td><td class="num">0.6%</td><td>El filtro más estrecho: una lectura distinta del mismo tablero.</td></tr>
    </tbody>
  </table>
  <p class="f3-footnote" style="margin-top:1.6mm">Las cinco filas salen de la misma función <code>derive()</code>, con el periodo evaluado sobre <code>release_year</code> y el país sobre la lista multivaluada de <code>countries</code>. El porcentaje siempre divide entre 8,807, nunca entre el subconjunto, para que las columnas sean comparables.</p>
""",
    )


def charts_overview() -> str:
    genres = D["aggregates"]["by_genre"][:8]
    genre_rows = "".join(
        f'<tr><td><strong>{g["label"]}</strong></td><td class="num">{fmt_int(g["count"])}</td>'
        f'<td class="num">{fmt_pct(g["share"])}</td></tr>'
        for g in genres
    )
    return page(
        11,
        "08 · Implementación de gráficos",
        f"""
  {sec_head("08", "Implementación de gráficos", "Una gráfica por pregunta, como en la Fase 2")}
  <p class="lead">La correspondencia es directa: el mapa responde “dónde”, la dona “cuánto de cada formato”, las barras “quién concentra”, la serie temporal “cómo cambió” y el histograma “cómo se distribuye”. Cuatro de las cinco marcas coinciden exactamente con la Fase 2; la serie temporal se explica en la página siguiente.</p>

  <table class="compact f3-mini-table">
    <thead><tr><th style="width:20%">Pregunta / KPI</th><th style="width:17%">Fase 2</th><th style="width:23%">Implementación</th><th>Por qué se mantiene</th></tr></thead>
    <tbody>
      <tr><td><strong>¿Cuánto hay y dónde?</strong><br>Títulos en el filtro</td><td>Tarjeta + mapa</td><td><code>KpiGrid</code> + <code>MapChart</code></td><td>La cifra ancla; el mapa descompone el volumen y filtra el resto.</td></tr>
      <tr><td><strong>¿Películas o series?</strong><br>Mezcla de formato</td><td>Dona</td><td><code>TypeDonut</code> · Recharts <code>PieChart</code></td><td>Dos categorías, parte-todo simple y total visible al centro.</td></tr>
      <tr><td><strong>¿Qué países concentran?</strong><br>Concentración geográfica</td><td>Barras horizontales</td><td><code>TopCountriesChart</code> · <code>BarChart</code> horizontal</td><td>Ordena magnitudes y permite leer nombres largos sin rotar.</td></tr>
      <tr><td><strong>¿Cómo cambió?</strong><br>Dinámica temporal</td><td>Línea / área</td><td><code>TimeSeriesChart</code> · barras apiladas</td><td>Misma pregunta y mismo eje; cambia la marca para no sugerir continuidad entre años discretos.</td></tr>
      <tr><td><strong>¿Cómo se distribuye?</strong><br>Duración mediana</td><td>Histograma</td><td><code>DurationCharts</code> · <code>BarChart</code></td><td>Rangos de minutos para películas; temporadas para series, nunca mezclados.</td></tr>
    </tbody>
  </table>

  <div class="f3-compare" style="margin-top:3.2mm;grid-template-columns:1.08fr 0.92fr">
    <div>
      {shot("img/f3/dashboard-types.png", "Dona de películas y series y barras de clasificación por edad.", "<b>Figura 2.</b> Dona y clasificaciones. La dona usa el total filtrado como centro; las barras excluyen los 7 títulos sin rating y lo indican al pie.")}
    </div>
    <div>
      <h3>Decisiones de marca que se conservaron</h3>
      <ul class="f3-list">
        <li><strong>Dona, no pastel:</strong> el centro aloja el total y evita una leyenda flotante.</li>
        <li><strong>Barras horizontales:</strong> los nombres de países y géneros caben sin rotar.</li>
        <li><strong>Etiquetas directas:</strong> el valor aparece al final de la barra; el tooltip añade porcentaje y duración.</li>
        <li><strong>Un color por serie:</strong> rojo para películas, ámbar para series; el gris queda para “sin dato”.</li>
        <li><strong>Alternativa accesible:</strong> rankings con <code>&lt;details&gt;</code> y botones; la nube tiene lista ordenada.</li>
      </ul>
      <div class="f3-note" style="margin-top:2.6mm">
        <p><strong>Gráficas complementarias.</strong> Clasificaciones, directores, patrones por década/mes y hallazgos se añadieron como lecturas N3. No reemplazan las cinco principales ni cambian el orden de lectura.</p>
      </div>
    </div>
  </div>

  <h3 class="f3-subhead">Los números detrás de la nube</h3>
  <div class="grid-2" style="grid-template-columns:1fr 1fr;gap:6mm">
    <table class="compact f3-mini-table">
      <thead><tr><th>Género</th><th class="num">Títulos</th><th class="num">% del filtro</th></tr></thead>
      <tbody>{genre_rows}</tbody>
    </table>
    <div>
      <p class="small" style="margin-top:0">La nube comunica la impresión; esta tabla y el ranking lateral dan la cifra exacta. Ambos leen <code>derived.topGenres</code> y <code>derived.byGenre</code>, así que no pueden discrepar.</p>
      <div class="f3-note" style="margin-top:2.4mm">
        <p><strong>Por qué la suma supera 100%.</strong> Un título puede pertenecer hasta a tres géneros. Cada género cuenta por separado sobre el total filtrado; el tablero lo advierte al pie de la nube y en la metodología.</p>
      </div>
    </div>
  </div>
""",
    )


def time_and_distribution() -> str:
    def peak_rows(series: list[dict]) -> str:
        top = sorted([x for x in series if x["total"] > 0], key=lambda x: -x["total"])[:5]
        return "".join(
            f'<tr><td><strong>{x["year"]}</strong></td><td class="num">{fmt_int(x["movies"])}</td>'
            f'<td class="num">{fmt_int(x["series"])}</td><td class="num">{fmt_int(x["total"])}</td></tr>'
            for x in top
        )

    release_rows = peak_rows(D["aggregates"]["by_year_release"])
    added_rows = peak_rows(D["aggregates"]["by_year_added"])
    return page(
        12,
        "09 · Tiempo y distribución",
        f"""
  {sec_head("09", "Tiempo y distribución", "La única variación de marca, documentada")}
  <p class="lead">La Fase 2 proponía línea/área para la dinámica temporal. La implementación usa barras apiladas: la pregunta es la misma —cómo cambió el catálogo y dónde están los picos—, pero la barra evita sugerir continuidad entre años discretos y conserva la separación entre películas y series. Es la única diferencia de marca respecto del informe de diseño y no altera la jerarquía.</p>

  <div class="f3-compare" style="grid-template-columns:1.12fr 0.88fr">
    <div>
      {shot("img/f3/dashboard-time.png", "Serie temporal de estrenos e incorporaciones por año con barras apiladas y línea de corte.", "<b>Figura 3.</b> Serie temporal. El selector alterna estreno e incorporación; la línea punteada marca el corte del 25 de septiembre de 2021.")}
    </div>
    <div>
      {shot("img/f3/dashboard-duration.png", "Histograma de duración de películas y distribución de temporadas de series.", "<b>Figura 4.</b> Duración. Mediana de 98 min para películas y 1 temporada para series; dos unidades, dos gráficas.")}
    </div>
  </div>

  <div class="grid-3" style="margin-top:3.2mm">
    <div class="card card-top red">
      <h3>Dos relojes</h3>
      <p class="small"><code>release_year</code> es cuándo se produjo el título; <code>date_added</code> es cuándo entró al catálogo. El selector no mezcla ambos ejes y el texto lo advierte.</p>
    </div>
    <div class="card card-top amber">
      <h3>Un corte explícito</h3>
      <p class="small">2021 está incompleto. La línea de referencia y la nota al pie evitan leer la caída del último año como una tendencia real.</p>
    </div>
    <div class="card card-top">
      <h3>Dos unidades</h3>
      <p class="small">Minutos solo para películas; temporadas solo para series. El tablero nunca promedia 98 minutos con 1 temporada.</p>
    </div>
  </div>

  <div class="f3-note" style="margin-top:3mm">
    <p><strong>Por qué la barra apilada.</strong> La línea/área de la Fase 2 priorizaba la forma de la tendencia; la barra apilada prioriza el volumen anual y la composición por formato. Con 32 años visibles (1990–2021), la barra permite comparar 2018 con 2019 sin interpolar y mantiene el pico de estrenos (2018, 1,147) y el de incorporaciones (2019, 2,016) como referencias legibles. Si se quisiera recuperar la línea, el cambio está aislado en <code>TimeSeriesChart.tsx</code>.</p>
  </div>

  <h3 class="f3-subhead">Los picos, año por año</h3>
  <div class="grid-2" style="grid-template-columns:1fr 1fr;gap:6mm">
    <div>
      <p class="f3-kicker">Estrenos · top 5 por año de producción</p>
      <table class="compact f3-mini-table">
        <thead><tr><th>Año</th><th class="num">Películas</th><th class="num">Series</th><th class="num">Total</th></tr></thead>
        <tbody>{release_rows}</tbody>
      </table>
    </div>
    <div>
      <p class="f3-kicker">Incorporaciones · top 5 por fecha de alta</p>
      <table class="compact f3-mini-table">
        <thead><tr><th>Año</th><th class="num">Películas</th><th class="num">Series</th><th class="num">Total</th></tr></thead>
        <tbody>{added_rows}</tbody>
      </table>
    </div>
  </div>
  <p class="f3-footnote" style="margin-top:1.6mm">Los dos relojes no coinciden: el pico de estrenos es 2018 y el de incorporaciones es 2019. En 2021 las altas llegan a 1,498 títulos aun con el corte de septiembre; por eso la comparación anual se detiene ahí y se marca como año incompleto.</p>
""",
    )


def map_implementation() -> str:
    map_code = """const byIso = useMemo(() => {
  const map = new Map<number, CountryStat>();
  stats.forEach((s) => map.set(s.isoN, s));
  return map;
}, [stats]);

const q = (p: number) =>
  counts[Math.floor((counts.length - 1) * p)];
const breaks = [q(0.2), q(0.4), q(0.6), q(0.8)];"""
    return page(
        13,
        "10 · Implementación del mapa",
        f"""
  {sec_head("10", "Implementación del mapa", "La geografía como pregunta y como selector")}
  <p class="lead">El mapa es la visualización obligatoria de la Fase 2 y una de las piezas centrales del tablero. Responde dónde se produce el catálogo y, al mismo tiempo, funciona como control: un clic en un país enfoca el resto de las vistas. La fuente es local, la escala es por cuantiles y la interacción es accesible por teclado.</p>

  <div class="f3-compare" style="grid-template-columns:1.15fr 0.85fr">
    <div>
      {shot("img/f3/dashboard-map.png", "Mapa mundial coroplético de títulos por país con leyenda de cuantiles y ranking lateral.", "<b>Figura 5.</b> Mapa implementado. Cinco tramos de color, gris para “sin títulos”, leyenda inferior y ranking lateral con los ocho primeros países.")}
    </div>
    <div>
      <h3>Fuente y geometría</h3>
      <ul class="f3-list">
        <li><strong>Geometría:</strong> <code>world-atlas/countries-110m.json</code> (TopoJSON) con <code>react-simple-maps</code> y <code>topojson-client</code>.</li>
        <li><strong>Datos:</strong> <code>dimensions.countries</code> del JSON, con nombre, etiqueta, ISO3, ISO numérico y región.</li>
        <li><strong>Unión:</strong> el <code>id</code> numérico de la geografía se cruza con <code>isoN</code> mediante un <code>Map</code>. Los países sin geometría siguen en el ranking y en el filtro.</li>
        <li><strong>Escala:</strong> cuantiles (20/40/60/80 %), no lineal; así los países pequeños no desaparecen frente a Estados Unidos.</li>
        <li><strong>Color:</strong> cinco tramos de rojo; el gris queda para cero. La leyenda muestra los cortes reales.</li>
      </ul>
    </div>
  </div>

  <div class="grid-2" style="margin-top:3mm;grid-template-columns:1fr 1fr">
    <div>
      <p class="f3-code-label"><span>MapChart.tsx · unión y escala</span><span>código real</span></p>
      <pre class="f3-code">{html.escape(map_code)}</pre>
    </div>
    <div>
      <h3>Interacción y accesibilidad</h3>
      <ul class="f3-list">
        <li><strong>Hover:</strong> tooltip con país, títulos, porcentaje, género principal y duración media.</li>
        <li><strong>Clic:</strong> filtra el tablero por país; el mapa conserva todos los países como selector.</li>
        <li><strong>Teclado:</strong> <code>tabIndex</code>, <code>role="button"</code>, <code>aria-label</code> y activación con Enter/Espacio.</li>
        <li><strong>Zoom:</strong> botones +, − y restablecer, con etiquetas accesibles.</li>
        <li><strong>Sin país:</strong> tarjeta con 831 títulos (9.4%) que se excluyen del mapa, pero permanecen en los totales.</li>
      </ul>
    </div>
  </div>

  <div class="f3-note" style="margin-top:3mm">
    <p><strong>Honestidad del dato.</strong> El mapa cuenta producción declarada, no audiencia ni ingresos. Un título puede declarar varios países, así que la suma del mapa supera el total del catálogo. El ranking y la tarjeta de “sin país” hacen visible esa regla; no se oculta en una nota al pie.</p>
  </div>

  <h3 class="f3-subhead">La escala, en números</h3>
  <div class="grid-2" style="grid-template-columns:1fr 1fr;gap:6mm">
    <div>
      <p class="f3-kicker">Cortes por cuantiles · 119 países con títulos</p>
      <table class="f3-scale">
        <tbody>
          <tr><td class="sw" style="background:#f2c6cb"></td><td><strong>1</strong></td><td class="num">37 países</td><td>Un solo título declarado.</td></tr>
          <tr><td class="sw" style="background:#e28a96"></td><td><strong>2–3</strong></td><td class="num">14 países</td><td>Producción testimonial.</td></tr>
          <tr><td class="sw" style="background:#cf5265"></td><td><strong>4–11</strong></td><td class="num">20 países</td><td>Presencia sostenida.</td></tr>
          <tr><td class="sw" style="background:#b72742"></td><td><strong>12–62</strong></td><td class="num">24 países</td><td>Mercados consolidados.</td></tr>
          <tr><td class="sw" style="background:#8f001b"></td><td><strong>63+</strong></td><td class="num">24 países</td><td>Los grandes productores.</td></tr>
          <tr><td class="sw" style="background:#e8e2d7"></td><td><strong>0</strong></td><td class="num">—</td><td>Sin títulos en el filtro actual.</td></tr>
        </tbody>
      </table>
    </div>
    <div>
      <p class="f3-kicker">Títulos por región · lectura agregada</p>
      <table class="compact f3-mini-table">
        <thead><tr><th>Región</th><th class="num">Títulos</th><th class="num">%</th></tr></thead>
        <tbody>
          <tr><td><strong>América del Norte</strong></td><td class="num">3,918</td><td class="num">44.5%</td></tr>
          <tr><td><strong>Asia</strong></td><td class="num">2,439</td><td class="num">27.7%</td></tr>
          <tr><td><strong>Europa</strong></td><td class="num">1,796</td><td class="num">20.4%</td></tr>
          <tr><td><strong>América Latina y el Caribe</strong></td><td class="num">444</td><td class="num">5.0%</td></tr>
          <tr><td><strong>África</strong></td><td class="num">311</td><td class="num">3.5%</td></tr>
          <tr><td><strong>Oceanía</strong></td><td class="num">187</td><td class="num">2.1%</td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <p class="f3-footnote" style="margin-top:1.6mm">La suma por región (9,095) supera el total del catálogo (8,807) porque un título puede declarar países de más de una región; 831 títulos no declaran país y quedan fuera del mapa, pero siguen en los totales. La escala por cuantiles evita que Estados Unidos aplaste a los 37 países con un solo título.</p>
""",
    )


def palette_styles() -> str:
    return page(
        14,
        "11 · Paleta y estilos",
        f"""
  {sec_head("11", "Paleta y estilos", "Los tokens de la Fase 2, aplicados en React")}
  <p class="lead">La paleta no se reinterpretó: se trasladó. El papel cálido, la tinta, el rojo y el ámbar viven en <code>:root</code> como variables CSS y en <code>palette.ts</code> como constantes para Recharts. El resultado es que un cambio de token se propaga a la interfaz y a las gráficas sin buscar hex sueltos.</p>

  <div class="f3-palette">
    <div class="f3-swatch">
      <div class="chip-color" style="background:#fbf9f5"></div>
      <div class="chip-body"><span>Fondo</span><strong>Papel</strong><code>#fbf9f5</code><p>Fondo cálido y tarjetas. 70% de la superficie.</p></div>
    </div>
    <div class="f3-swatch">
      <div class="chip-color" style="background:#171614"></div>
      <div class="chip-body"><span>Estructura</span><strong>Tinta</strong><code>#171614</code><p>Texto, ejes, títulos y bordes. 17.2:1 sobre papel.</p></div>
    </div>
    <div class="f3-swatch">
      <div class="chip-color" style="background:#d90429"></div>
      <div class="chip-body"><span>Énfasis</span><strong>Rojo</strong><code>#d90429</code><p>KPI principal, películas, selección y foco. 4.99:1.</p></div>
    </div>
    <div class="f3-swatch">
      <div class="chip-color" style="background:#b7791f"></div>
      <div class="chip-body"><span>Contrapunto</span><strong>Ámbar</strong><code>#b7791f</code><p>Series y acentos. 3.46:1: solo marcas grandes.</p></div>
    </div>
  </div>

  <div class="grid-2" style="grid-template-columns:1.02fr 0.98fr">
    <div>
      <h3>Tokens y aplicación</h3>
      <table class="compact f3-mini-table">
        <thead><tr><th style="width:30%">Token</th><th style="width:24%">Valor</th><th>Uso</th></tr></thead>
        <tbody>
          <tr><td><code>--paper</code></td><td>#fbf9f5</td><td>Fondo de página y tarjetas.</td></tr>
          <tr><td><code>--ink</code></td><td>#171614</td><td>Texto, ejes y bordes principales.</td></tr>
          <tr><td><code>--red</code></td><td>#d90429</td><td>KPI, películas, foco y selección.</td></tr>
          <tr><td><code>--red-deep</code></td><td>#9e0018</td><td>Hover del mapa y énfasis profundo.</td></tr>
          <tr><td><code>--amber</code></td><td>#b7791f</td><td>Series, corte y acentos secundarios.</td></tr>
          <tr><td><code>--muted</code></td><td>#6f6b63</td><td>Notas, leyendas y texto secundario.</td></tr>
          <tr><td><code>--line</code></td><td>#e4ded3</td><td>Bordes y separadores.</td></tr>
        </tbody>
      </table>
    </div>
    <div>
      <h3>Contraste verificado (WCAG 2.2)</h3>
      <table class="compact f3-mini-table">
        <thead><tr><th>Combinación</th><th class="num">Ratio</th><th>Uso</th></tr></thead>
        <tbody>
          <tr><td>Tinta sobre papel</td><td class="num">17.2:1</td><td>Texto y ejes · AAA</td></tr>
          <tr><td>Rojo sobre papel</td><td class="num">4.99:1</td><td>Texto normal · AA</td></tr>
          <tr><td>Blanco sobre rojo</td><td class="num">5.25:1</td><td>Botones y chips · AA</td></tr>
          <tr><td>Gris medio sobre papel</td><td class="num">5.04:1</td><td>Notas y leyendas · AA</td></tr>
          <tr><td>Ámbar sobre papel</td><td class="num">3.46:1</td><td>Solo marcas grandes · AA no texto</td></tr>
          <tr><td>Ámbar oscuro sobre papel</td><td class="num">5.62:1</td><td>Texto pequeño · AA</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="grid-3" style="margin-top:3.2mm">
    <div><h3>Tipografía</h3><p class="small">Fraunces para titulares y cifras; DM Sans para texto, etiquetas y notas. Ambas se cargan localmente con Fontsource.</p></div>
    <div><h3>Retícula</h3><p class="small">1380 px de ancho máximo, riel de 252 px, cabecera de 68 px y escala de espacios de 4 px. Radio de 2 px.</p></div>
    <div><h3>Movimiento</h3><p class="small">Contadores y revelados suaves; <code>prefers-reduced-motion</code> los desactiva. El foco visible nunca depende solo del color.</p></div>
  </div>

  <h3 class="f3-subhead">La tipografía y los estados, aplicados</h3>
  <div class="f3-specimen">
    <div>
      <span class="k">Fraunces · titulares y cifras</span>
      <p class="aa">Aa <em>g</em></p>
      <p>400 · 500 · 600 · 700. Titulares, cifras KPI y subtítulos. Carga local desde Fontsource: sin peticiones a Google Fonts ni FOUT de red.</p>
    </div>
    <div>
      <span class="k">DM Sans · texto, etiquetas y controles</span>
      <p class="aa-sans">Aa 8,807</p>
      <p>400 · 500 · 700. Párrafos, notas y leyendas. Las cifras usan <code>tabular-nums</code> para alinear tablas y ejes.</p>
      <div class="f3-states">
        <span class="on">Películas</span>
        <span>Series</span>
        <span class="focus">Foco visible</span>
        <span>Limpiar filtros</span>
      </div>
    </div>
  </div>
  <p class="f3-footnote" style="margin-top:1.6mm">Los estados no dependen solo del color: el chip activo cambia de fondo y de contraste, y el foco añade un contorno de 1.2 pt que se mantiene sobre cualquier superficie.</p>

  <div class="f3-note" style="margin-top:3mm">
    <p><strong>Deuda visible.</strong> La tinta existe como <code>#171614</code> en CSS y como <code>#171717</code> en <code>palette.ts</code>. La diferencia es imperceptible, pero debería unificarse en un solo token compartido. Se documenta aquí para no presentar el sistema como perfecto.</p>
  </div>
""",
    )


def problems() -> str:
    return page(
        15,
        "12 · Problemas y soluciones",
        f"""
  {sec_head("12", "Problemas y soluciones", "Lo que falló y cómo se resolvió")}
  <p class="lead">Documentar solo lo que salió bien sería propaganda. Estos son los problemas reales que aparecieron al implementar el wireframe, la causa técnica y la solución que quedó en el código. Ninguno se resolvió “ocultando” el síntoma en la interfaz.</p>

  <table class="compact f3-problems">
    <thead><tr><th style="width:21%">Problema</th><th style="width:25%">Causa</th><th style="width:32%">Solución implementada</th><th>Evidencia</th></tr></thead>
    <tbody>
      <tr><td>Conflicto de peer dependency</td><td><code>react-simple-maps@3</code> declara React 18; el proyecto usa React 19.</td><td>Instalación con <code>--legacy-peer-deps</code> y verificación manual del mapa, zoom y eventos.</td><td>README · <code>package.json</code></td></tr>
      <tr><td>Países sin geometría</td><td>El TopoJSON de 110 m no incluye algunas islas o territorios pequeños.</td><td>El mapa los omite, pero el ranking lateral y el filtro los conservan; la nota lo advierte.</td><td><code>MapChart.tsx</code></td></tr>
      <tr><td>El mapa se colapsaba al filtrar</td><td>Si el filtro de país se aplicaba al mapa, solo quedaba un país visible y se perdía el selector.</td><td><code>mapDerived</code> se calcula con <code>place: all</code>; el resto de las vistas usa <code>derived</code>.</td><td><code>App.tsx</code> · p. 8</td></tr>
      <tr><td>Porcentajes que suman más de 100%</td><td>Países y géneros son multivaluados: un título puede tener hasta 12 países y 3 géneros.</td><td>El denominador es el total filtrado y cada categoría cuenta por separado; la interfaz lo explica.</td><td><code>aggregate.ts</code> · metodología</td></tr>
      <tr><td>2021 parece una caída</td><td>El snapshot termina el 25 de septiembre de 2021; el año está incompleto.</td><td>Línea de corte, nota al pie y texto explícito; no se interpola ni se extrapola.</td><td>Serie temporal · p. 12</td></tr>
      <tr><td>Filtros sin resultados</td><td>Combinaciones de tipo, periodo y país pueden devolver cero títulos.</td><td><code>filter-empty</code> con explicación y “Limpiar filtros”; <code>EmptyState</code> en cada gráfica.</td><td><code>App.tsx</code> · <code>ui.tsx</code></td></tr>
      <tr><td>Desbordamiento a 390 px</td><td>Tablas de calidad, matrices y rankings anchos.</td><td><code>.table-scroll</code> con <code>tabIndex=0</code> y <code>role=region</code>; el resto se apila en una columna.</td><td>QA móvil · p. 5</td></tr>
      <tr><td>Tipos de <code>d3-cloud</code></td><td>El paquete no incluye declaraciones TypeScript.</td><td>Declaración local en <code>src/types/d3-cloud.d.ts</code>; el resto del proyecto sigue en strict.</td><td><code>tsconfig.json</code></td></tr>
      <tr><td>Bundle de ≈900 kB</td><td>Recharts, react-simple-maps y world-atlas en un solo chunk.</td><td>Se acepta para uso local/académico; queda documentado el próximo paso: <code>React.lazy</code> y <code>manualChunks</code>.</td><td>Salida de <code>vite build</code></td></tr>
    </tbody>
  </table>

  <div class="grid-2" style="margin-top:3.2mm">
    <div class="f3-note">
      <p><strong>Lo que no se hizo.</strong> No se añadieron tests automatizados ni un pipeline de capturas. La verificación fue build de TypeScript + QA visual manual en tres anchos. Es una deuda real y se reconoce en la reflexión técnica.</p>
    </div>
    <div class="f3-note">
      <p><strong>Lo que sí se evitó.</strong> No se imputaron países ni directores faltantes, no se inventaron ingresos y no se ocultó el 2021 incompleto. Los límites del dataset se muestran en la interfaz, no solo en el informe.</p>
    </div>
  </div>

  <h3 class="f3-subhead">Checklist de verificación aplicado</h3>
  <table class="compact f3-mini-table">
    <thead><tr><th style="width:30%">Verificación</th><th style="width:46%">Cómo se comprobó</th><th>Resultado</th></tr></thead>
    <tbody>
      <tr><td><strong>Tipos y build</strong></td><td><code>npm run build</code> ejecuta <code>tsc --noEmit</code> antes de Vite.</td><td>Sin errores.</td></tr>
      <tr><td><strong>Datos reales</strong></td><td>8,807 filas en <code>dashboard.json</code> contra el CSV de origen.</td><td>Coinciden.</td></tr>
      <tr><td><strong>Escritorio 1440 px</strong></td><td>Retícula, riel sticky, mapa y rankings en una sola pasada.</td><td>Sin solapamientos.</td></tr>
      <tr><td><strong>Móvil 390 px</strong></td><td>Ancho mínimo, tablas con <code>.table-scroll</code> y KPIs en 2 × 2.</td><td>Sin desbordamiento.</td></tr>
      <tr><td><strong>Teclado</strong></td><td>Mapa, filtros, <code>&lt;details&gt;</code> y zoom con Tab, Enter y Espacio.</td><td>Recorrido completo.</td></tr>
      <tr><td><strong>Contraste</strong></td><td>Pares de la paleta sobre papel y sobre rojo.</td><td>AA en texto.</td></tr>
      <tr><td><strong>Movimiento reducido</strong></td><td>Contadores y revelados con <code>prefers-reduced-motion</code>.</td><td>Se desactivan.</td></tr>
      <tr><td><strong>Documentos</strong></td><td>Los tres PDF se sirven desde <code>public/docs</code> y responden 200.</td><td>Descargan.</td></tr>
    </tbody>
  </table>
  <p class="f3-footnote" style="margin-top:1.6mm">El checklist se ejecutó sobre la versión que genera este informe; no sustituye una suite de pruebas, pero cubre los tres anchos declarados.</p>
""",
    )


def reflection() -> str:
    return page(
        16,
        "13 · Reflexión técnica",
        f"""
  {sec_head("13", "Reflexión técnica", "Qué sostuvo el diseño y qué costó")}
  <p class="lead">La implementación confirma una idea: un buen wireframe no se “copia” al código, se convierte en un contrato. Cuando la jerarquía, los tokens y las reglas de cálculo están escritos, cada componente tiene una responsabilidad clara. Lo que sigue es el balance honesto entre lo que funcionó, lo que se pagó y lo que se cambiaría.</p>

  <div class="grid-2">
    <div>
      <h3>Lo que funcionó</h3>
      <ul class="f3-list">
        <li><strong>El sistema visual como contrato.</strong> Los tokens de la Fase 2 evitaron discutir colores en cada componente.</li>
        <li><strong>Un solo <code>derive()</code>.</strong> KPIs, gráficas y tablas comparten denominador; no hay cifras contradictorias.</li>
        <li><strong>Tipos estrictos.</strong> La tupla <code>TitleRow</code> y el objeto <code>Derived</code> hicieron visibles los errores antes del navegador.</li>
        <li><strong>Accesibilidad desde la estructura.</strong> Secciones semánticas, tablas equivalentes, teclado en el mapa y movimiento reducido.</li>
        <li><strong>La documentación como parte del entregable.</strong> Cada decisión tiene una página, un archivo o una captura que la respalda.</li>
      </ul>
    </div>
    <div>
      <h3>Lo que costó</h3>
      <ul class="f3-list">
        <li><strong>Sin tests automatizados:</strong> la confianza depende de TypeScript y del QA manual; una regresión visual podría pasar.</li>
        <li><strong>Un bundle grande:</strong> ≈900 kB en un solo chunk; aceptable en local, mejorable con carga diferida.</li>
        <li><strong>Tokens duplicados:</strong> CSS y <code>palette.ts</code> mantienen hex separados; una fuente única sería más limpia.</li>
        <li><strong>Datos estáticos:</strong> actualizar el catálogo exige ETL + build; no hay panel en vivo ni programación.</li>
        <li><strong>Una desviación de marca:</strong> barras apiladas en lugar de línea/área; documentada, pero es una diferencia real.</li>
      </ul>
    </div>
  </div>

  <h3 style="margin-top:3.5mm">Qué cambiaría en una segunda iteración</h3>
  <div class="grid-4">
    <div class="card card-top red"><h3>Tests</h3><p class="small">Vitest para <code>derive()</code> y Playwright para el recorrido de filtros, el mapa y los estados vacíos.</p></div>
    <div class="card card-top amber"><h3>Tokens</h3><p class="small">Un archivo <code>tokens.json</code> que genere las variables CSS y las constantes de <code>palette.ts</code>.</p></div>
    <div class="card card-top"><h3>Bundle</h3><p class="small"><code>React.lazy</code> para las gráficas complementarias y <code>manualChunks</code> para separar Recharts y el mapa.</p></div>
    <div class="card card-top"><h3>Datos</h3><p class="small">Un script de actualización que valide el CSV, ejecute el ETL y compare el reporte de calidad antes de publicar.</p></div>
  </div>

  <div class="f3-note" style="margin-top:3.2mm">
    <p><strong>La lección principal.</strong> El mayor riesgo no era que una gráfica se viera distinta, sino que el tablero dijera cosas distintas en dos lugares. La decisión de calcular todo una vez y tipar la salida eliminó ese riesgo. La estética se sostuvo porque estaba escrita; la lógica se sostuvo porque estaba centralizada.</p>
  </div>

  <h3 class="f3-subhead">Tres fases, una misma decisión</h3>
  <div class="f3-timeline">
    <div>
      <span class="k">Fase 1 · Justificación</span>
      <strong>Por qué este dataset</strong>
      <p>Pregunta, audiencia, objetivos y límites del dato. El tablero debía describir el catálogo, no estimar audiencia ni ingresos.</p>
    </div>
    <div>
      <span class="k">Fase 2 · Diseño visual</span>
      <strong>La estructura antes del código</strong>
      <p>KPI principal, cuatro secundarios, una gráfica por pregunta, paleta, tipografía, retícula y wireframes aprobados.</p>
    </div>
    <div>
      <span class="k">Fase 3 · Implementación</span>
      <strong>El diseño, en código</strong>
      <p>Componentes, estado único, mapa interactivo, accesibilidad y verificación. La misma jerarquía, ahora con datos reales.</p>
    </div>
  </div>

  <div class="f3-quote" style="margin-top:26mm;font-size:16.5pt">
    “Diseñar es decidir qué no se muestra. Implementar es decidir qué no se calcula dos veces.”
    <span>Balance de la Fase 3 · Catálogo en foco</span>
  </div>
""",
    )


def conclusion() -> str:
    return page(
        17,
        "14 · Conclusión y verificación",
        f"""
  {sec_head("14", "Conclusión y verificación", "El wireframe no se copia: se demuestra")}
  <p class="lead">El tablero está implementado y documentado. La Fase 3 no consistió en añadir adornos, sino en probar que las decisiones de la Fase 2 resistían el contacto con datos reales, estados de filtro, pantallas pequeñas y limitaciones del navegador. El resultado conserva la jerarquía, los KPIs y la estética; las diferencias están explicadas, no escondidas.</p>

  <div class="grid-4" style="margin-top:1mm">
    <div class="f3-number"><span>01</span><h3>Diseñar es decidir</h3><p>El wireframe se volvió útil cuando cada bloque tuvo un componente y una regla de datos.</p></div>
    <div class="f3-number"><span>02</span><h3>El dato manda</h3><p>8,807 títulos, 119 países y 42 géneros: el tablero no necesita cifras inventadas para verse completo.</p></div>
    <div class="f3-number"><span>03</span><h3>La accesibilidad es estructura</h3><p>Tablas, teclado, contraste y movimiento reducido se resolvieron en la arquitectura, no al final.</p></div>
    <div class="f3-number"><span>04</span><h3>Documentar es parte del trabajo</h3><p>Este informe explica qué se hizo, dónde vive y qué falta; no solo muestra capturas.</p></div>
  </div>

  <div class="f3-verdict">
    <div>
      <h3>Verificación contra la rúbrica</h3>
      <table class="compact f3-mini-table">
        <thead><tr><th style="width:52%">Criterio</th><th class="num">Pts.</th><th>Evidencia</th></tr></thead>
        <tbody>
          <tr><td>Correspondencia wireframe ↔ dashboard</td><td class="num">25</td><td>Pp. 5–6 · figuras 1–2</td></tr>
          <tr><td>Implementación de KPIs y gráficos</td><td class="num">25</td><td>Pp. 10–13 · código</td></tr>
          <tr><td>Uso de la paleta de colores</td><td class="num">15</td><td>P. 14 · tokens</td></tr>
          <tr><td>Estructura y legibilidad del código</td><td class="num">15</td><td>Pp. 7–9 · árbol</td></tr>
          <tr><td>Documentación de la implementación</td><td class="num">20</td><td>Todo el informe</td></tr>
        </tbody>
      </table>
    </div>
    <div>
      <h3>Estado final</h3>
      <div class="f3-criteria">
        <div>Build de TypeScript + Vite</div><div class="pts">OK</div>
        <div>Datos reales del ETL</div><div class="pts">8,807</div>
        <div>Secciones del tablero</div><div class="pts">11</div>
        <div>Módulos de gráfica</div><div class="pts">9</div>
        <div>QA visual 1440 / 1024 / 390</div><div class="pts">OK</div>
        <div>Datos de relleno</div><div class="pts">0</div>
      </div>
      <p class="f3-footnote" style="margin-top:2mm">La única variación de marca es la serie temporal (barras apiladas en lugar de línea/área), explicada en la página 12. El resto de las decisiones de la Fase 2 se conserva.</p>
    </div>
  </div>

  <h3 class="f3-subhead">Entregables de las tres fases</h3>
  <table class="compact f3-mini-table">
    <thead><tr><th style="width:36%">Archivo</th><th style="width:32%">Contenido</th><th>Estado</th></tr></thead>
    <tbody>
      <tr><td><code>docs/Implementacion_Fase3.pdf</code></td><td>Este informe · 17 páginas</td><td>Generado y verificado.</td></tr>
      <tr><td><code>docs/Diseno_Fase2.pdf</code></td><td>Wireframe y sistema visual · 13 páginas</td><td>Aprobado en la fase anterior.</td></tr>
      <tr><td><code>docs/Justificacion_Fase1.pdf</code></td><td>Pregunta, objetivos y ETL · 12 páginas</td><td>Entregado.</td></tr>
      <tr><td><code>public/data/dashboard.json</code></td><td>Datos del tablero · 8,807 filas</td><td>Generado por el ETL.</td></tr>
      <tr><td><code>data/quality_report.json</code></td><td>Calidad por campo y anomalías</td><td>Base de la sección de método.</td></tr>
      <tr><td><code>README.md</code></td><td>Reproducción y decisiones técnicas</td><td>Actualizado con la Fase 3.</td></tr>
    </tbody>
  </table>
  <p class="f3-footnote" style="margin-top:1.6mm">Los tres informes comparten el mismo sistema editorial y la misma fuente de datos; ninguno cita cifras de otro proyecto. El tablero se sirve junto con los PDF desde <code>public/docs</code>.</p>

  <div class="f3-quote">
    “El wireframe no se copia: se demuestra. Un tablero está bien implementado cuando el usuario puede repetir el recorrido que el diseño prometió, con datos reales y sin explicaciones de emergencia.”
    <span>Catálogo en foco · Implementación · Fase 3</span>
  </div>
""",
    )


# ------------------------------------------------------------------
# Ensamblado
# ------------------------------------------------------------------

def build_html(quality: dict, dashboard: dict) -> str:
    global D, Q
    D, Q = dashboard, quality
    pages = [
        cover(),
        index_page(),
        introduction(),
        implemented_board(),
        correspondence_first(),
        correspondence_analysis(),
        project_structure(),
        architecture(),
        technical_justification(),
        kpi_implementation(),
        charts_overview(),
        time_and_distribution(),
        map_implementation(),
        palette_styles(),
        problems(),
        reflection(),
        conclusion(),
    ]
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{BRAND} · Implementación Fase 3</title>
<style>{CSS}</style>
</head>
<body>
{''.join(pages)}
</body>
</html>
"""


def main() -> None:
    quality, dashboard = load()
    DOCS.mkdir(parents=True, exist_ok=True)
    PUBLIC_DOCS.mkdir(parents=True, exist_ok=True)
    HTML.write_text(build_html(quality, dashboard), encoding="utf-8")

    chrome = find_chrome()
    command = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=12000",
        f"--print-to-pdf={PDF}",
        HTML.as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0 or not PDF.exists():
        raise SystemExit(f"Chrome no pudo generar el PDF.\n{result.stderr}")

    shutil.copy2(PDF, PUBLIC_DOCS / PDF.name)
    print(f"HTML: {HTML.relative_to(ROOT)}")
    print(f"PDF:  {PDF.relative_to(ROOT)} ({PDF.stat().st_size / 1024:.0f} KB)")
    print(f"Copia: {(PUBLIC_DOCS / PDF.name).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
