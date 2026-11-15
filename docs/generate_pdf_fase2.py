"""
Genera el informe de diseño visual de la Fase 2.

El documento planifica la estructura del tablero antes de implementarlo:
KPI principal y secundarios, tipo de gráfico por KPI, paleta, tipografía,
retícula, wireframes y jerarquía visual. Usa las cifras reales del ETL y el
sistema visual de "Catálogo en foco".

Uso:
    python docs/generate_pdf_fase2.py
"""
from __future__ import annotations

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
HTML = DOCS / "diseno_fase2.html"
PDF = DOCS / "Diseno_Fase2.pdf"
TOTAL_PAGES = 13


def load() -> tuple[dict, dict]:
    quality = json.loads(QUALITY.read_text(encoding="utf-8"))
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))
    return quality, dashboard


CSS = BASE_CSS + r"""
/* ============================================================
   Fase 2 · componentes propios
   ============================================================ */

.f2-cover .cover-inner { padding: 15mm 18mm 12mm; }
.f2-cover h1 { font-size: 36pt; line-height: 0.95; }
.f2-cover h1 em { font-size: 18pt; margin-top: 2mm; }
.f2-cover .lead { margin-top: 5mm; max-width: 104mm; font-size: 10.2pt; }

.f2-cover-body {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(58mm, 0.75fr);
  gap: 12mm;
  align-items: end;
  margin: 7mm 0 5mm;
}

.f2-cover-visual {
  border-top: 2pt solid var(--ink);
  padding-top: 3mm;
}

.f2-cover-visual .cap {
  margin: 2.4mm 0 0;
  font-size: 6.4pt;
  line-height: 1.45;
  color: var(--muted);
}

.f2-mini-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.4mm;
}

.f2-mini-grid div {
  position: relative;
  min-height: 10mm;
  padding: 1.4mm;
  border: 0.5pt solid var(--line-2);
  background: var(--white);
  font-size: 4.8pt;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.f2-mini-grid div::after {
  content: "";
  position: absolute;
  left: 1.4mm;
  right: 1.4mm;
  bottom: 1.4mm;
  height: 0.5pt;
  background: var(--line);
}

.f2-mini-grid .span2 { grid-column: span 2; }
.f2-mini-grid .span3 { grid-column: span 3; }
.f2-mini-grid .is-red {
  background: #fdf0f2;
  border-color: var(--red);
  color: var(--red-deep);
}
.f2-mini-grid .is-ink {
  background: var(--ink);
  border-color: var(--ink);
  color: var(--paper);
}
.f2-mini-grid .is-ink::after { background: #4a4640; }

.f2-cover-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-top: 1.2pt solid var(--ink);
  border-bottom: 0.6pt solid var(--line);
  margin-top: 5mm;
}

.f2-cover-strip div {
  padding: 2.4mm 3mm 2.6mm 0;
  border-right: 0.5pt solid var(--line);
}

.f2-cover-strip div:last-child { border-right: 0; }
.f2-cover-strip div:not(:first-child) { padding-left: 3mm; }

.f2-cover-strip .k {
  display: block;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.f2-cover-strip strong {
  display: block;
  margin-top: 1mm;
  font-family: var(--serif);
  font-size: 14pt;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.03em;
}

.f2-cover-strip p {
  margin: 1mm 0 0;
  font-size: 6.2pt;
  line-height: 1.35;
  color: var(--muted);
}

.f2-cover-levels {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  align-content: space-between;
  gap: 5mm;
  min-height: 43mm;
  margin: 2mm 0 4mm;
  padding-top: 3mm;
  border-top: 1.4pt solid var(--ink);
}

.f2-cover-levels-head {
  grid-column: span 3;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 6mm;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.f2-cover-level {
  padding-top: 2.2mm;
  border-top: 0.6pt solid var(--line);
}

.f2-cover-level h3 {
  margin: 1.4mm 0 1.1mm;
  font-size: 10.4pt;
}

.f2-cover-level p {
  margin: 0;
  font-size: 7pt;
  line-height: 1.45;
  color: var(--muted);
}

.f2-cover-level .tag { margin-bottom: 0; }

/* ------------------------------------------------------------
   Resumen y punto de partida
   ------------------------------------------------------------ */

.index-page .lead {
  font-size: 9.5pt;
  line-height: 1.44;
  margin-bottom: 3mm;
}

.index-page .index-row {
  padding: 2.15mm 0;
}

.index-page .index-row h3 {
  font-size: 10.2pt;
}

.index-page .index-row p {
  margin-top: 0.45mm;
  font-size: 6.9pt;
  line-height: 1.35;
}

.index-page .index-row .n {
  font-size: 8.8pt;
}

.index-page .index-row .p {
  font-size: 9.8pt;
}

.index-page h3 {
  font-size: 10.4pt;
  margin-bottom: 1.4mm;
}

.index-page .note-box {
  padding: 2.6mm 3.4mm;
  font-size: 7.2pt;
  line-height: 1.42;
}

.brief-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4mm;
}

.brief-card {
  border-top: 1.4pt solid var(--ink);
  padding-top: 2.6mm;
}

.brief-card:nth-child(2) { border-top-color: var(--red); }
.brief-card:nth-child(3) { border-top-color: var(--amber); }

.brief-card .k {
  display: block;
  font-size: 6pt;
  font-weight: 600;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.brief-card h3 {
  margin: 1.3mm 0 1.4mm;
  font-size: 10pt;
}

.brief-card p {
  margin: 0;
  font-size: 7.5pt;
  line-height: 1.5;
  color: var(--muted);
}

.brief-decisions {
  margin: 0;
  padding: 0;
  list-style: none;
  border-top: 0.8pt solid var(--ink);
}

.brief-decisions li {
  display: grid;
  grid-template-columns: 8mm minmax(0, 1fr);
  gap: 2.4mm;
  padding: 2.2mm 0;
  border-bottom: 0.5pt solid var(--line);
  font-size: 7.6pt;
  line-height: 1.45;
  color: var(--ink-soft);
}

.brief-decisions .n {
  font-family: var(--serif);
  font-size: 11pt;
  font-weight: 600;
  line-height: 1;
  color: var(--red);
}

.brief-decisions strong { color: var(--ink); }

.principles {
  display: flex;
  flex-wrap: wrap;
  gap: 1.6mm;
  margin-top: 3.5mm;
}

.principles span {
  padding: 0.8mm 2mm;
  border: 0.5pt solid var(--line-2);
  background: var(--white);
  font-size: 6.4pt;
  color: var(--muted);
}

.data-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-top: 1.4pt solid var(--ink);
  border-bottom: 0.6pt solid var(--line);
  margin: 3.5mm 0;
}

.data-strip div {
  padding: 2.4mm 3mm 2.6mm 0;
  border-right: 0.5pt solid var(--line);
}

.data-strip div:last-child { border-right: 0; }
.data-strip div:not(:first-child) { padding-left: 3mm; }

.data-strip .k {
  display: block;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.data-strip strong {
  display: block;
  margin-top: 1mm;
  font-family: var(--serif);
  font-size: 15pt;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.04em;
  font-variant-numeric: tabular-nums;
}

.data-strip p {
  margin: 1mm 0 0;
  font-size: 6.2pt;
  line-height: 1.35;
  color: var(--muted);
}

/* ------------------------------------------------------------
   KPI principal y secundarios
   ------------------------------------------------------------ */

.kpi-main-card {
  display: grid;
  grid-template-columns: minmax(0, 1.18fr) minmax(0, 0.82fr);
  gap: 7mm;
  border-top: 2.6pt solid var(--red);
  background: var(--white);
  padding: 4.4mm 5mm 4.6mm;
  margin-bottom: 3.5mm;
}

.kpi-main-label {
  margin: 2.4mm 0 0;
  font-size: 7pt;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
}

.kpi-main-value {
  margin: 1.2mm 0 0;
  font-family: var(--serif);
  font-size: 43pt;
  font-weight: 600;
  line-height: 0.88;
  letter-spacing: -0.055em;
  font-variant-numeric: tabular-nums;
}

.kpi-main-note {
  max-width: 62mm;
  margin: 2.4mm 0 0;
  font-size: 7.4pt;
  line-height: 1.45;
  color: var(--muted);
}

.kpi-main-side {
  border-left: 0.6pt solid var(--line);
  padding-left: 5mm;
}

.kpi-main-side h4 {
  margin: 0 0 1.6mm;
  font-family: var(--sans);
  font-size: 6.2pt;
  font-weight: 600;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.kpi-main-side ul {
  margin: 0;
  padding-left: 4mm;
}

.kpi-main-side li {
  margin-bottom: 1.4mm;
  font-size: 7.2pt;
  line-height: 1.45;
  color: var(--ink-soft);
}

.kpi-mini-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 3mm;
}

.kpi-mini {
  border-top: 1.2pt solid var(--line-2);
  padding-top: 2.4mm;
}

.kpi-mini:nth-child(1) { border-top-color: var(--amber); }
.kpi-mini:nth-child(2) { border-top-color: var(--ink); }
.kpi-mini:nth-child(3) { border-top-color: var(--red); }
.kpi-mini:nth-child(4) { border-top-color: var(--amber); }

.kpi-mini .k {
  display: block;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.kpi-mini strong {
  display: block;
  margin-top: 1.2mm;
  font-family: var(--serif);
  font-size: 18pt;
  font-weight: 600;
  line-height: 0.95;
  letter-spacing: -0.045em;
  font-variant-numeric: tabular-nums;
}

.kpi-mini p {
  margin: 1.4mm 0 0;
  font-size: 6.5pt;
  line-height: 1.4;
  color: var(--muted);
}

.kpi-mini .chart-ref {
  display: inline-block;
  margin-top: 1.6mm;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--red-deep);
}

/* ------------------------------------------------------------
   Razones y comparaciones
   ------------------------------------------------------------ */

.reason-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3.5mm 5mm;
}

.reason-block {
  display: grid;
  grid-template-columns: 8mm minmax(0, 1fr);
  gap: 2.4mm;
  padding-top: 2.2mm;
  border-top: 0.6pt solid var(--line);
}

.reason-block .n {
  font-family: var(--serif);
  font-size: 13pt;
  font-weight: 600;
  line-height: 0.9;
  color: var(--red);
}

.reason-block h3 {
  margin: 0 0 1.1mm;
  font-size: 9.2pt;
}

.reason-block p {
  margin: 0;
  font-size: 7.3pt;
  line-height: 1.48;
  color: var(--muted);
}

/* ------------------------------------------------------------
   Gráficos: iconos y gramática
   ------------------------------------------------------------ */

.chart-grammar {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 2.5mm;
  margin-bottom: 3.5mm;
}

.chart-grammar div {
  border-top: 1.2pt solid var(--ink);
  padding-top: 2mm;
}

.chart-grammar div:nth-child(1) { border-top-color: var(--red); }
.chart-grammar div:nth-child(3) { border-top-color: var(--amber); }

.chart-icon {
  width: 8mm;
  height: 8mm;
  margin-bottom: 1.4mm;
  color: var(--red);
}

.chart-icon svg { width: 100%; height: 100%; display: block; }

.chart-grammar .k {
  display: block;
  font-size: 6pt;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.chart-grammar p {
  margin: 0.8mm 0 0;
  font-size: 6.4pt;
  line-height: 1.4;
  color: var(--muted);
}

/* ------------------------------------------------------------
   Paleta
   ------------------------------------------------------------ */

.swatches {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 3mm;
}

.swatch {
  border: 0.6pt solid var(--line);
  background: var(--white);
}

.swatch-color {
  height: 28mm;
  border-bottom: 0.6pt solid var(--line);
}

.swatch:nth-child(2) .swatch-color { border-bottom-color: var(--line-2); }

.swatch-body { padding: 2.6mm 3mm 3mm; }

.swatch-body .k {
  display: block;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.swatch-body h3 {
  margin: 1mm 0 1.2mm;
  font-size: 9.4pt;
}

.swatch-hex {
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 7pt;
  color: var(--ink-soft);
}

.swatch-body p {
  margin: 1.2mm 0 0;
  font-size: 6.4pt;
  line-height: 1.42;
  color: var(--muted);
}

.color-ratio {
  display: flex;
  height: 8mm;
  margin: 3.5mm 0 2mm;
  border: 0.6pt solid var(--line);
  overflow: hidden;
}

.color-ratio span {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 5.6pt;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: #fff;
}

.color-ratio .paper { background: var(--paper-2); color: var(--muted); }
.color-ratio .ink { background: var(--ink); }
.color-ratio .red { background: var(--red); }
.color-ratio .amber { background: var(--amber); }

.ratio-legend {
  display: flex;
  justify-content: space-between;
  gap: 3mm;
  font-size: 6pt;
  color: var(--muted);
}

/* ------------------------------------------------------------
   Tipografía y retícula
   ------------------------------------------------------------ */

.grid12 {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1.2mm;
  margin: 2mm 0 1.2mm;
}

.grid12 span {
  height: 12mm;
  border: 0.4pt solid #e8b8bd;
  background: #fbebed;
}

.grid12 span:nth-child(odd) { background: #f7dfe2; }

.grid12-labels {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1.2mm;
  font-size: 5.2pt;
  text-align: center;
  color: var(--muted-2);
}

.level-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 3mm;
}

.level-card {
  border-top: 1.6pt solid var(--line-2);
  padding-top: 2.2mm;
}

.level-card.n1 { border-top-color: var(--red); }
.level-card.n2 { border-top-color: var(--amber); }

.level-card .tag { margin-bottom: 1.4mm; }

.level-card h3 {
  margin: 0 0 1mm;
  font-size: 9.4pt;
}

.level-card p {
  margin: 0;
  font-size: 6.9pt;
  line-height: 1.45;
  color: var(--muted);
}

/* ------------------------------------------------------------
   Wireframe
   ------------------------------------------------------------ */

.wf {
  position: relative;
  border: 0.8pt solid var(--ink);
  background: var(--white);
  overflow: hidden;
}

.wf-topbar {
  display: flex;
  align-items: center;
  gap: 1.2mm;
  padding: 1.3mm 2.4mm;
  border-bottom: 0.5pt solid var(--line);
  background: var(--paper-2);
}

.wf-dot {
  width: 1.3mm;
  height: 1.3mm;
  border-radius: 50%;
  background: var(--line-2);
}

.wf-url {
  margin-left: 2mm;
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 5pt;
  color: var(--muted-2);
}

.wf-canvas {
  position: relative;
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 1.5mm;
  padding: 3mm;
  min-height: 88mm;
}

.wf-grid {
  position: absolute;
  inset: 0;
  z-index: 8;
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 1.5mm;
  padding: 3mm;
  pointer-events: none;
  background-image: linear-gradient(
    to bottom,
    transparent 33.1%,
    rgba(217, 4, 41, 0.16) 33.1%,
    rgba(217, 4, 41, 0.16) 33.35%,
    transparent 33.35%,
    transparent 66.4%,
    rgba(217, 4, 41, 0.16) 66.4%,
    rgba(217, 4, 41, 0.16) 66.65%,
    transparent 66.65%
  );
}

.wf-grid span {
  border-left: 0.4pt dashed rgba(217, 4, 41, 0.3);
}

.wf-grid span:last-child {
  border-right: 0.4pt dashed rgba(217, 4, 41, 0.3);
}

.wf-block {
  position: relative;
  min-width: 0;
  border: 0.5pt solid var(--line-2);
  background: var(--paper);
  padding: 1.6mm;
}

.wf-block.white { background: var(--white); }
.wf-block.red {
  border-color: var(--red);
  background: #fdf3f4;
}

.wf-label {
  font-size: 4.6pt;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.wf-h1 {
  margin: 1.4mm 0 0;
  font-family: var(--serif);
  font-size: 13pt;
  font-weight: 600;
  line-height: 0.98;
  letter-spacing: -0.03em;
  color: var(--ink);
}

.wf-h1 em { color: var(--red); font-weight: 400; }

.wf-h3 {
  margin: 0;
  font-family: var(--serif);
  font-size: 7pt;
  font-weight: 600;
  line-height: 1.1;
  letter-spacing: -0.015em;
}

.wf-line {
  height: 1mm;
  margin-top: 1.1mm;
  background: var(--line);
}

.wf-line.dark { background: var(--line-2); }
.wf-line.short { width: 62%; }

.wf-value {
  margin-top: 1mm;
  font-family: var(--serif);
  font-size: 13pt;
  font-weight: 600;
  line-height: 0.95;
  letter-spacing: -0.04em;
  font-variant-numeric: tabular-nums;
}

.wf-value.sm { font-size: 9pt; }

.wf-pin {
  position: absolute;
  top: 1.1mm;
  right: 1.1mm;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3.6mm;
  height: 3.6mm;
  border-radius: 50%;
  background: var(--red);
  color: #fff;
  font-size: 5pt;
  font-weight: 700;
}

.wf-tag {
  display: inline-block;
  padding: 0.2mm 1mm;
  border: 0.4pt solid;
  font-size: 4.4pt;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.wf-tag.n1 { background: var(--red); border-color: var(--red); color: #fff; }
.wf-tag.n2 { background: #f8efdd; border-color: #d8c39a; color: #7a5210; }
.wf-tag.n3 { background: var(--paper-2); border-color: var(--line-2); color: var(--muted); }

.wf-header {
  grid-column: span 12;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4mm;
  padding-bottom: 1.4mm;
  border-bottom: 0.5pt solid var(--line);
}

.wf-brand {
  display: flex;
  align-items: center;
  gap: 1.4mm;
  font-family: var(--serif);
  font-size: 6.8pt;
  font-weight: 600;
}

.wf-brand i {
  display: inline-block;
  width: 3mm;
  height: 3mm;
  background: var(--red);
}

.wf-nav {
  display: flex;
  gap: 2mm;
  font-size: 4.6pt;
  color: var(--muted);
}

.wf-pill {
  padding: 0.3mm 1.2mm;
  border: 0.4pt solid var(--line-2);
  font-size: 4.4pt;
  color: var(--muted);
}

.wf-hero-copy { grid-column: span 7; padding-top: 1.6mm; }
.wf-hero-figure {
  grid-column: span 5;
  border-top: 1.2pt solid var(--ink);
  padding-top: 1.4mm;
}

.wf-kpi {
  grid-column: span 4;
  border-top: 1pt solid var(--ink);
  padding-top: 1.4mm;
  min-height: 17mm;
}

.wf-kpi.main {
  border-top: 2.2pt solid var(--red);
  background: #fdf3f4;
  padding-left: 1.4mm;
  padding-right: 1.4mm;
}

.wf-filters {
  grid-column: span 12;
  display: flex;
  align-items: center;
  gap: 1.4mm;
  padding: 1.4mm 0;
  border-top: 0.8pt solid var(--ink);
  border-bottom: 0.5pt solid var(--line);
}

.wf-chip {
  padding: 0.6mm 1.6mm;
  border: 0.4pt solid var(--line-2);
  font-size: 4.8pt;
  color: var(--muted);
}

.wf-chip.active {
  background: var(--red);
  border-color: var(--red);
  color: #fff;
}

.wf-select {
  flex: 1;
  padding: 0.8mm 1.4mm;
  border: 0.4pt solid var(--line-2);
  font-size: 4.8pt;
  color: var(--muted);
  background: var(--white);
}

.wf-result {
  margin-left: auto;
  font-size: 4.8pt;
  font-weight: 600;
  color: var(--ink-soft);
  white-space: nowrap;
}

.wf-rail {
  grid-column: span 3;
  display: flex;
  flex-direction: column;
  align-self: stretch;
  padding-right: 2mm;
}

.wf-rail-note {
  margin-top: auto;
  padding-top: 2mm;
  border-top: 0.5pt solid var(--line);
}

.wf-rail-note .wf-line { margin-top: 0.9mm; }

.wf-rail .num {
  font-family: var(--serif);
  font-size: 10pt;
  font-weight: 600;
  color: var(--red);
}

.wf-main {
  grid-column: span 9;
  display: grid;
  grid-template-columns: repeat(9, minmax(0, 1fr));
  gap: 1.5mm;
  border-left: 0.5pt solid var(--line);
  padding-left: 2.4mm;
}

.wf-map { grid-column: span 6; }
.wf-side { grid-column: span 3; }
.wf-time { grid-column: span 9; }
.wf-genres { grid-column: span 5; }
.wf-types { grid-column: span 4; }
.wf-duration { grid-column: span 9; }

.wf-map-img {
  height: 34mm;
  margin-top: 1.2mm;
  border: 0.4pt solid var(--line);
  background-image: url("img/pdf-mapa.png");
  background-size: 160% auto;
  background-position: left center;
  background-repeat: no-repeat;
  filter: grayscale(1) opacity(0.22);
}

.wf-legend-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.4mm;
  margin-top: 1.2mm;
}

.wf-legend-row span {
  display: inline-flex;
  align-items: center;
  gap: 0.8mm;
  font-size: 4.6pt;
  color: var(--muted);
}

.wf-legend-row i {
  width: 2.4mm;
  height: 1.4mm;
  background: var(--red-soft);
  border: 0.3pt solid var(--red);
}

.wf-bars {
  display: flex;
  align-items: flex-end;
  gap: 1mm;
  height: 18mm;
  margin-top: 1.2mm;
  padding-bottom: 0.6mm;
  border-bottom: 0.4pt solid var(--line-2);
}

.wf-bars span {
  flex: 1;
  background: var(--red);
  opacity: 0.72;
}

.wf-bars span:nth-child(2n) { opacity: 0.42; }

.wf-line-chart {
  position: relative;
  height: 18mm;
  margin-top: 1.2mm;
  border-bottom: 0.4pt solid var(--line-2);
  background-image: linear-gradient(to top, transparent 24.5%, var(--line) 24.5%, var(--line) 25%, transparent 25%, transparent 49.5%, var(--line) 49.5%, var(--line) 50%, transparent 50%, transparent 74.5%, var(--line) 74.5%, var(--line) 75%, transparent 75%);
}

.wf-line-chart::after {
  content: "";
  position: absolute;
  left: 2%;
  right: 2%;
  bottom: 18%;
  height: 46%;
  border-top: 1.4pt solid var(--red);
  border-radius: 50% 50% 0 0 / 40% 40% 0 0;
  transform: skewY(-6deg);
}

.wf-donut {
  width: 20mm;
  height: 20mm;
  margin: 1.4mm auto 0;
  border-radius: 50%;
  background: conic-gradient(var(--red) 0 69.6%, var(--amber) 69.6% 100%);
  position: relative;
}

.wf-donut::after {
  content: "";
  position: absolute;
  inset: 4.4mm;
  border-radius: 50%;
  background: var(--white);
}

.wf-hist {
  display: flex;
  align-items: flex-end;
  gap: 0.8mm;
  height: 18mm;
  margin-top: 1.2mm;
  border-bottom: 0.4pt solid var(--line-2);
}

.wf-hist span {
  flex: 1;
  background: var(--amber);
  opacity: 0.65;
}

.wf-heat {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 0.6mm;
  margin-top: 1.2mm;
}

.wf-heat span {
  height: 3mm;
  background: var(--red-soft);
}

.wf-heat span:nth-child(3n) { background: #efb9bf; }
.wf-heat span:nth-child(5n) { background: #d90429; opacity: 0.65; }

.wf-legend-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.4mm 5mm;
  margin-top: 3mm;
}

.wf-legend-grid > div {
  display: grid;
  grid-template-columns: 5mm minmax(0, 1fr);
  gap: 1.6mm;
  padding: 1.4mm 0;
  border-bottom: 0.5pt solid var(--line);
  font-size: 6.5pt;
  line-height: 1.4;
  color: var(--muted);
}

.wf-legend-grid > div > div {
  display: block;
  padding: 0;
  border: 0;
  font-size: inherit;
  line-height: inherit;
  color: inherit;
}

.wf-legend-grid b {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 4.4mm;
  height: 4.4mm;
  border-radius: 50%;
  background: var(--red);
  color: #fff;
  font-size: 5.6pt;
}

.wf-legend-grid strong { color: var(--ink-soft); }

.filter-proof {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 3.5mm;
  margin-top: 3.5mm;
}

.filter-proof > div {
  padding-top: 2.2mm;
  border-top: 1.4pt solid var(--line-2);
}

.filter-proof > div:nth-child(2) { border-top-color: var(--red); }
.filter-proof > div:nth-child(3) { border-top-color: var(--amber); }

.filter-proof .k {
  display: block;
  font-size: 5.8pt;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-2);
}

.filter-proof strong {
  display: block;
  margin-top: 1.2mm;
  font-family: var(--serif);
  font-size: 18pt;
  font-weight: 600;
  line-height: 0.95;
  letter-spacing: -0.045em;
  font-variant-numeric: tabular-nums;
}

.filter-proof p {
  margin: 1mm 0 0;
  font-size: 6.8pt;
  line-height: 1.4;
  color: var(--muted);
}

/* ------------------------------------------------------------
   Cuadrícula de prioridad
   ------------------------------------------------------------ */

.priority-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2mm;
  margin-bottom: 3.5mm;
}

.pg-cell {
  position: relative;
  min-height: 30mm;
  padding: 2.8mm 3mm;
  border: 0.6pt solid var(--line);
  background: var(--white);
}

.pg-cell.n1 { border-top: 2.6pt solid var(--red); background: #fdf3f4; }
.pg-cell.n2 { border-top: 2.6pt solid var(--amber); }
.pg-cell.n3 { border-top: 2.6pt solid var(--line-2); background: var(--paper-2); }

.pg-cell .tag { margin-bottom: 1.4mm; }

.pg-cell h3 {
  margin: 0 0 1mm;
  font-size: 9pt;
  line-height: 1.12;
}

.pg-cell p {
  margin: 0;
  font-size: 6.6pt;
  line-height: 1.42;
  color: var(--muted);
}

.pg-cell .mark {
  position: absolute;
  right: 2.4mm;
  bottom: 2mm;
  font-family: var(--serif);
  font-size: 17pt;
  font-weight: 600;
  line-height: 1;
  color: rgba(23, 22, 20, 0.12);
}

/* ------------------------------------------------------------
   Responsive
   ------------------------------------------------------------ */

.device-grid {
  display: grid;
  grid-template-columns: 1.25fr 1fr 0.72fr;
  gap: 3mm;
  align-items: end;
  margin-bottom: 3.5mm;
}

.device {
  border: 0.6pt solid var(--line);
  background: var(--white);
  padding: 2mm;
}

.device .screen {
  border: 0.5pt solid var(--line-2);
  background: var(--paper);
  padding: 1.6mm;
}

.device .bar {
  height: 2.4mm;
  background: var(--ink);
  margin-bottom: 1.4mm;
}

.device .hero-mini {
  height: 10mm;
  background: var(--paper-2);
  border: 0.4pt solid var(--line);
  margin-bottom: 1.4mm;
}

.device .kpis-mini {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.8mm;
  margin-bottom: 1.4mm;
}

.device .kpis-mini span {
  height: 5mm;
  border: 0.4pt solid var(--line);
  background: var(--white);
}

.device .kpis-mini span:first-child {
  background: var(--red-soft);
  border-color: var(--red);
}

.device .charts-mini {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8mm;
}

.device .charts-mini span {
  height: 10mm;
  border: 0.4pt solid var(--line);
  background: var(--white);
}

.device .caption {
  margin: 1.4mm 0 0;
  font-size: 5.8pt;
  color: var(--muted);
}

.device.tablet .kpis-mini { grid-template-columns: repeat(2, 1fr); }
.device.tablet .charts-mini { grid-template-columns: 1fr; }
.device.phone .kpis-mini { grid-template-columns: repeat(2, 1fr); }
.device.phone .charts-mini { grid-template-columns: 1fr; }
.device.phone .hero-mini { height: 16mm; }

.states {
  display: flex;
  flex-wrap: wrap;
  gap: 1.6mm;
  margin-top: 2mm;
}

.state-chip {
  padding: 1.2mm 2.4mm;
  border: 0.5pt solid var(--line-2);
  background: var(--white);
  font-size: 6.2pt;
  color: var(--muted);
}

.state-chip.active { background: var(--red); border-color: var(--red); color: #fff; }
.state-chip.focus { border-color: var(--red); box-shadow: 0 0 0 1.2pt var(--red-soft); }

"""


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def runhead(section: str) -> str:
    return (
        '<div class="runhead">'
        f'<span class="rh-brand"><i></i>{BRAND}</span>'
        f"<span>{section}</span>"
        "</div>"
    )


def pfoot(n: int) -> str:
    return (
        '<div class="pfoot">'
        f"<span>{BRAND} · Fase 2 · Diseño visual</span>"
        f"<span>{n} / {TOTAL_PAGES}</span>"
        "</div>"
    )


def page(n: int, section: str, body: str, extra: str = "") -> str:
    return f'<section class="page {extra}">{runhead(section)}{body}{pfoot(n)}</section>'


def sec_head(num: str, label: str, title: str) -> str:
    return (
        '<div class="sec-head">'
        f'<div class="sec-num">{num}</div>'
        "<div>"
        f'<p class="sec-label">{label}</p>'
        f"<h2>{title}</h2>"
        "</div></div>"
    )


def wf_grid() -> str:
    return '<div class="wf-grid" aria-hidden="true">' + "".join("<span></span>" for _ in range(12)) + "</div>"


# ------------------------------------------------------------------
# 01 · Portada
# ------------------------------------------------------------------

def cover() -> str:
    return f"""
<section class="page cover f2-cover">
  <div class="cover-inner">
    <div>
      <div class="cover-brand"><i></i>Catálogo <span>en foco</span></div>
      <div class="cover-topline" style="margin-top:4.5mm">
        <span>Fase 2 · Diseño visual</span>
        <span>Informe de estructura · {date.today().strftime('%d/%m/%Y')}</span>
      </div>

      <div class="f2-cover-body">
        <div>
          <p class="sec-label" style="color:var(--red)">Antes de implementar</p>
          <h1>La estructura <em>antes del código</em></h1>
          <p class="lead">Cómo se distribuye, jerarquiza y colorea el tablero: un KPI principal, cuatro indicadores que lo explican, una gráfica para cada pregunta y un wireframe que ordena la lectura antes de escribir la primera línea de interfaz.</p>
        </div>

        <div class="f2-cover-visual">
          <div class="f2-mini-grid" aria-hidden="true">
            <div class="span2">Título general</div>
            <div class="is-red">KPI principal</div>
            <div class="span3">Filtros globales</div>
            <div class="span2">Mapa / selector</div>
            <div>Ranking</div>
            <div class="span2">Tiempo</div>
            <div class="is-ink">Géneros</div>
          </div>
          <p class="cap">Wireframe de la primera pantalla. La retícula de 12 columnas se convierte en una jerarquía de tres niveles: titular, indicadores y análisis.</p>
        </div>
      </div>
    </div>

    <div class="f2-cover-levels">
      <div class="f2-cover-levels-head">
        <span>Jerarquía de lectura</span>
        <span>Tres niveles · un solo recorrido</span>
      </div>
      <div class="f2-cover-level">
        <span class="tag red">N1</span>
        <h3>Titular y KPI principal</h3>
        <p>Qué es el tablero y cuál es el total que sostiene todas las comparaciones.</p>
      </div>
      <div class="f2-cover-level">
        <span class="tag" style="border-color:#d8c39a;background:#f8efdd;color:#7a5210">N2</span>
        <h3>Evidencia visual</h3>
        <p>Mapa, tiempo, formato y duración: una gráfica para cada pregunta.</p>
      </div>
      <div class="f2-cover-level">
        <span class="tag">N3</span>
        <h3>Contexto y método</h3>
        <p>Filtros, leyendas y límites del dato, siempre en la periferia de la lectura.</p>
      </div>
    </div>

    <div>
      <div class="f2-cover-strip">
        <div><span class="k">KPI principal</span><strong>1</strong><p>Títulos en el filtro</p></div>
        <div><span class="k">Secundarios</span><strong>4</strong><p>Formato, origen, tiempo y duración</p></div>
        <div><span class="k">Visualizaciones</span><strong>5</strong><p>Mapa, dona, barras, línea e histograma</p></div>
        <div><span class="k">Colores base</span><strong>4</strong><p>Tinta, papel, rojo y ámbar</p></div>
      </div>

      <dl class="cover-meta">
        <div><dt>Equipo</dt><dd>{TEAM}</dd></div>
        <div><dt>Docente</dt><dd>{TEACHER}</dd></div>
        <div><dt>Materia</dt><dd>{SUBJECT}</dd></div>
        <div><dt>Tema</dt><dd>{TOPIC}</dd></div>
        <div><dt>Entregable</dt><dd>Informe de diseño · Fase 2</dd></div>
        <div><dt>Base</dt><dd>8,807 títulos · 119 países</dd></div>
      </dl>
      <div class="cover-foot">
        <span><strong>{BRAND}</strong> · Diseño visual y estructura del tablero</span>
        <span>{TOTAL_PAGES} páginas · Español (México)</span>
      </div>
    </div>
  </div>
</section>
"""


# ------------------------------------------------------------------
# 02 · Índice
# ------------------------------------------------------------------

INDEX_ITEMS = [
    ("00", "El diseño en una página", "Pregunta, audiencia, decisiones y principios de la propuesta.", 3),
    ("01", "Punto de partida", "Qué debe resolver el tablero y qué restricciones lo delimitan.", 4),
    ("02", "KPI principal y secundarios", "Un indicador ancla y cuatro lecturas que lo explican.", 5),
    ("03", "Por qué ese KPI principal", "Denominador, filtro y comparación: la base de todo lo demás.", 6),
    ("04", "Gráfico para cada KPI", "Selección, justificación y alternativas descartadas.", 7),
    ("05", "Paleta y accesibilidad", "Cuatro colores, contraste y uso del color como jerarquía.", 8),
    ("06", "Tipografía, retícula y jerarquía", "Escala, espacios y prioridad visual de los elementos.", 9),
    ("07", "Wireframe · primera pantalla", "Título, KPI, filtros y retícula marcada.", 10),
    ("08", "Wireframe · área de análisis", "Mapa, tiempo, géneros y leyendas en contexto.", 11),
    ("09", "Cuadrícula y prioridad visual", "Matriz 3 × 3 con los tres niveles de lectura.", 12),
    ("10", "Responsive y accesibilidad", "La misma jerarquía en 1440, 1024 y 390 px.", 13),
]


def index_page() -> str:
    rows = "".join(
        f"""<div class="index-row">
          <span class="n">{n}</span>
          <div><h3>{title}</h3><p>{desc}</p></div>
          <span class="p">{p}</span>
        </div>"""
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
  <p class="lead">El documento sigue el orden en que se toman las decisiones de diseño: primero el problema y la audiencia, después los indicadores y las gráficas, luego la paleta y la retícula, y al final el wireframe con su jerarquía. Cada sección termina en una decisión que la siguiente puede usar.</p>

  <div class="index-list">{rows}</div>

  <h3 style="margin-top:4mm">Cómo se relaciona con la evaluación</h3>
  <table class="compact">
    <thead><tr><th style="width:38%">Criterio</th><th style="width:10%" class="num">Puntos</th><th>Dónde se responde</th></tr></thead>
    <tbody>
      <tr><td>Justificación del KPI principal</td><td class="num">20</td><td>Secciones 02 y 03 · páginas 5–6</td></tr>
      <tr><td>Selección adecuada de tipos de gráficos</td><td class="num">20</td><td>Sección 04 · página 7</td></tr>
      <tr><td>Paleta de colores y coherencia visual</td><td class="num">20</td><td>Sección 05 · página 8</td></tr>
      <tr><td>Wireframe claro y bien estructurado</td><td class="num">30</td><td>Secciones 07–09 · páginas 10–12</td></tr>
      <tr><td>Presentación y claridad del documento</td><td class="num">10</td><td>Índice, mapa de criterios y sistema editorial completo</td></tr>
    </tbody>
  </table>
""",
        extra="index-page",
    )


# ------------------------------------------------------------------
# 03 · Resumen de diseño
# ------------------------------------------------------------------

def brief_page(dashboard: dict) -> str:
    k = dashboard["kpis"]
    return page(
        3,
        "00 · El diseño en una página",
        f"""
  {sec_head("00", "Resumen de diseño", "El tablero en una página")}
  <p class="lead">La propuesta no empieza por los gráficos, sino por una decisión: <strong>qué debe entender el usuario primero</strong>. El tablero se organiza como una lectura editorial en tres tiempos: el titular, la evidencia y el detalle. Todo lo demás —KPIs, colores, retícula y wireframe— existe para sostener ese orden.</p>

  <div class="brief-grid">
    <article class="brief-card">
      <span class="k">La pregunta</span>
      <h3>¿Cómo se compone el catálogo y qué cambia al mirarlo por país, año, género y formato?</h3>
      <p>La pregunta es comparativa, no predictiva. El tablero debe permitir contrastar mercados, periodos y mezclas con un mismo denominador.</p>
    </article>
    <article class="brief-card">
      <span class="k">La audiencia</span>
      <h3>Tres profundidades, una misma página</h3>
      <p>Analista de catálogo, docencia y público general. La lectura de treinta segundos debe convivir con la de tres minutos y con la de quince.</p>
    </article>
    <article class="brief-card">
      <span class="k">Los datos</span>
      <h3>Composición, no éxito</h3>
      <p>{fmt_int(k['total_titulos'])} títulos y {k['paises_distintos']} países. Sin ingresos, audiencia ni suscriptores: el tablero describe qué hay, no cuánto rinde.</p>
    </article>
    <article class="brief-card">
      <span class="k">La respuesta visual</span>
      <h3>Un tablero táctico, editorial y filtrable</h3>
      <p>Un KPI ancla, cuatro indicadores de contexto, un mapa que también es selector y una retícula que separa el hallazgo de la nota metodológica.</p>
    </article>
  </div>

  <h3 style="margin-top:4mm">Cinco decisiones que ordenan el diseño</h3>
  <ol class="brief-decisions">
    <li><span class="n">01</span><div><strong>El KPI principal es el volumen filtrado.</strong> Es el denominador de todos los porcentajes y la señal inmediata de que el filtro funciona.</div></li>
    <li><span class="n">02</span><div><strong>Cada KPI tiene una gráfica y una pregunta.</strong> No se elige una visualización por moda: se elige por la operación mental que el usuario debe hacer.</div></li>
    <li><span class="n">03</span><div><strong>El color es jerarquía, no decoración.</strong> Rojo para el KPI principal y la selección; ámbar para series; tinta y papel para la estructura.</div></li>
    <li><span class="n">04</span><div><strong>La retícula es asimétrica y estable.</strong> Riel de sección a la izquierda, contenido a la derecha; 3 columnas para KPIs y 2 para gráficas.</div></li>
    <li><span class="n">05</span><div><strong>El wireframe se prueba en 390 px.</strong> La misma jerarquía se apila sin scroll horizontal y sin perder el KPI principal.</div></li>
  </ol>

  <div class="principles">
    <span>Una pregunta por gráfica</span>
    <span>Un denominador por vista</span>
    <span>El color no es el único canal</span>
    <span>La leyenda vive cerca de la marca</span>
    <span>El detalle está a un clic</span>
  </div>
""",
    )


# ------------------------------------------------------------------
# 04 · Punto de partida
# ------------------------------------------------------------------

def starting_point(dashboard: dict) -> str:
    k = dashboard["kpis"]
    return page(
        4,
        "01 · Punto de partida",
        f"""
  {sec_head("01", "Punto de partida", "Qué debe resolver el diseño")}
  <p class="lead">El tablero no se diseña en el vacío: hereda una pregunta, una audiencia y unas restricciones. Esta página las fija para que las decisiones visuales de las secciones siguientes tengan un criterio verificable.</p>

  <div class="data-strip">
    <div><span class="k">Títulos</span><strong>{fmt_int(k['total_titulos'])}</strong><p>100% del catálogo, sin muestreo</p></div>
    <div><span class="k">Países</span><strong>{k['paises_distintos']}</strong><p>Un título puede declarar varios</p></div>
    <div><span class="k">Géneros</span><strong>42</strong><p>Hasta 3 etiquetas por título</p></div>
    <div><span class="k">Corte</span><strong>2021</strong><p>25 de septiembre; 2021 incompleto</p></div>
  </div>

  <div class="grid-2">
    <div class="callout" style="margin-top:0">
      <h4>La pregunta central</h4>
      <p>¿Cómo se compone el catálogo de Netflix y qué cambia cuando se mira por <strong>tipo, país, año y género</strong>? La respuesta debe ser comparable, trazable y honesta sobre lo que el dataset no contiene.</p>
      <p style="margin-top:2mm"><strong>No</strong> es una pregunta sobre éxito, audiencia o ingresos. Es una pregunta sobre composición y evolución.</p>
    </div>

    <div>
      <h3>La audiencia, en tres capas</h3>
      <ul>
        <li><strong>Analista de catálogo:</strong> decide qué mercado, género o formato mirar con más atención. Necesita cifras exactas y filtros combinables.</li>
        <li><strong>Docencia:</strong> decide qué evidencia llevar al aula y qué límites discutir. Necesita método y contexto.</li>
        <li><strong>Público general:</strong> decide si el tema le interesa y qué explorar. Necesita una entrada narrativa y lenguaje claro.</li>
      </ul>
    </div>
  </div>

  <h3 style="margin-top:4mm">Restricciones que se convierten en decisiones</h3>
  <table class="compact">
    <thead><tr><th style="width:27%">Restricción</th><th>Consecuencia de diseño</th></tr></thead>
    <tbody>
      <tr><td><strong>Snapshot cerrado</strong></td><td>No se simula tiempo real ni se promete monitoreo. El corte se muestra en portada, fichas y pie.</td></tr>
      <tr><td><strong>Sin ingresos ni audiencia</strong></td><td>Los KPIs son de conteo y composición. No hay “rentabilidad”, “éxito” ni “participación de mercado”.</td></tr>
      <tr><td><strong>País y género multivaluados</strong></td><td>Los porcentajes usan el total de títulos como denominador; las sumas por categoría pueden superar 100%.</td></tr>
      <tr><td><strong>Datos faltantes</strong></td><td>No se imputan. Se excluyen de la vista que los requiere y se reportan en la metodología.</td></tr>
      <tr><td><strong>Móvil de 390 px</strong></td><td>La jerarquía se apila; las tablas hacen scroll dentro de su contenedor, no la página.</td></tr>
      <tr><td><strong>Accesibilidad</strong></td><td>Contraste, foco visible, navegación por teclado y tablas equivalentes para cada gráfica.</td></tr>
    </tbody>
  </table>

  <div class="note-box" style="margin-top:3.5mm">
    <strong>Lo que el tablero no promete.</strong> No predice qué título funcionará, no mide horas vistas y no compara Netflix con otras plataformas. El diseño debe hacer visible esa frontera, no esconderla.
  </div>
""",
    )


# ------------------------------------------------------------------
# 05 · KPI principal y secundarios
# ------------------------------------------------------------------

def kpi_hierarchy(dashboard: dict) -> str:
    k = dashboard["kpis"]
    movie_share = 100 * k["peliculas"] / k["total_titulos"]
    return page(
        5,
        "02 · Indicadores",
        f"""
  {sec_head("02", "Indicadores", "Un KPI principal y cuatro que lo explican")}
  <p class="lead">El KPI principal no es el más llamativo: es el que hace interpretables a los demás. Aquí se define el ancla y se ordenan cuatro lecturas complementarias para que el usuario nunca vea un porcentaje sin saber de qué total sale.</p>

  <div class="kpi-main-card">
    <div>
      <span class="tag red">N1 · KPI principal</span>
      <p class="kpi-main-label">Títulos en el filtro</p>
      <p class="kpi-main-value">{fmt_int(k['total_titulos'])}</p>
      <p class="kpi-main-note">100% del catálogo completo. Es el denominador de todos los porcentajes y la primera señal de que el filtro está activo.</p>
    </div>
    <div class="kpi-main-side">
      <h4>Por qué es el principal</h4>
      <ul>
        <li><strong>Es el denominador:</strong> sin él, “69.6%” o “41.9%” no significan nada.</li>
        <li><strong>Es el termómetro del filtro:</strong> cambia con cada selección y confirma que la vista es válida.</li>
        <li><strong>Es la base de comparación:</strong> países, años, géneros y formatos se leen contra ese total.</li>
      </ul>
    </div>
  </div>

  <div class="kpi-mini-grid">
    <article class="kpi-mini">
      <span class="k">Mezcla de formato</span>
      <strong>{fmt_pct(movie_share, 1)}</strong>
      <p>Películas · {fmt_pct(k['porcentaje_series'], 1)} series. La primera división del catálogo.</p>
      <span class="chart-ref">Dona → p. 7</span>
    </article>
    <article class="kpi-mini">
      <span class="k">Concentración geográfica</span>
      <strong>{fmt_pct(k['top5_paises'][0]['share'], 1)}</strong>
      <p>Estados Unidos · {k['paises_distintos']} países. Mide el peso del mercado líder.</p>
      <span class="chart-ref">Mapa + barras → p. 7</span>
    </article>
    <article class="kpi-mini">
      <span class="k">Dinámica temporal</span>
      <strong>{fmt_pct(k['ultimos_5_anios']['porcentaje'])}</strong>
      <p>Incorporado entre {k['ultimos_5_anios']['desde']} y {k['ultimos_5_anios']['hasta']}. Pico en {k['anio_mas_incorporaciones']['year']}.</p>
      <span class="chart-ref">Línea / área → p. 7</span>
    </article>
    <article class="kpi-mini">
      <span class="k">Duración mediana</span>
      <strong>{k['duracion_peliculas']['mediana_min']:.0f} min</strong>
      <p>Películas · {fmt_int(k['duracion_peliculas']['n'])} con dato válido. Series: {k['temporadas_series']['mediana']:.0f} temporada.</p>
      <span class="chart-ref">Histograma → p. 7</span>
    </article>
  </div>

  <h3 style="margin-top:4mm">Cálculo y unidad de cada indicador</h3>
  <table class="compact">
    <thead><tr><th style="width:23%">Indicador</th><th style="width:39%">Cálculo</th><th>Unidad</th></tr></thead>
    <tbody>
      <tr><td><strong>Títulos en el filtro</strong></td><td><code>COUNT(show_id)</code> sobre el conjunto filtrado</td><td>títulos</td></tr>
      <tr><td><strong>Mezcla de formato</strong></td><td><code>COUNT(type = 'Movie') / COUNT(*)</code> y su complemento</td><td>% del filtro</td></tr>
      <tr><td><strong>Concentración geográfica</strong></td><td><code>COUNT(country = 'United States') / COUNT(*)</code></td><td>% · países</td></tr>
      <tr><td><strong>Dinámica temporal</strong></td><td><code>COUNT(added_year BETWEEN 2017 AND 2021) / COUNT(*)</code></td><td>% · año</td></tr>
      <tr><td><strong>Duración mediana</strong></td><td><code>MEDIAN(duration_min)</code> solo para películas</td><td>minutos</td></tr>
    </tbody>
  </table>

  <p class="tiny" style="margin-top:2.5mm">Los cuatro secundarios no compiten con el principal: lo descomponen por formato, origen, tiempo y duración. La suma de sus lecturas es la historia del catálogo, no una lista de cifras sueltas.</p>
""",
    )


# ------------------------------------------------------------------
# 06 · Justificación del KPI principal
# ------------------------------------------------------------------

def kpi_justification(dashboard: dict) -> str:
    k = dashboard["kpis"]
    return page(
        6,
        "03 · Justificación del KPI principal",
        f"""
  {sec_head("03", "Justificación", "Por qué el volumen filtrado es la base")}
  <p class="lead">Elegir “títulos en el filtro” como KPI principal es una decisión analítica, no una preferencia estética. El indicador no resume el hallazgo: <strong>crea las condiciones para que el hallazgo sea comparable</strong>. Estas son las cuatro razones.</p>

  <div class="reason-grid">
    <div class="reason-block"><span class="n">1</span><div><h3>Es el denominador común</h3><p>Todos los porcentajes del tablero —formato, país, género, tiempo— se calculan sobre el mismo total filtrado. Sin ese ancla, cada gráfica tendría un denominador distinto y las comparaciones serían inválidas.</p></div></div>
    <div class="reason-block"><span class="n">2</span><div><h3>Hace visible el efecto del filtro</h3><p>El usuario elige tipo, periodo y país; el número cambia de inmediato. Es la confirmación de que la selección existe y de que las vistas que siguen hablan del mismo subconjunto.</p></div></div>
    <div class="reason-block"><span class="n">3</span><div><h3>Permite comparar sin perder escala</h3><p>Un país con 3,690 títulos y otro con 393 no se leen igual. El volumen filtrado obliga a mirar el tamaño de la base antes de interpretar una participación.</p></div></div>
    <div class="reason-block"><span class="n">4</span><div><h3>Es honesto con el dataset</h3><p>No promete ingresos, audiencia ni éxito. Cuenta lo que el archivo realmente contiene: títulos. Esa modestia es lo que hace defendible el resto del análisis.</p></div></div>
  </div>

  <h3 style="margin-top:4mm">Si otro indicador fuera el principal</h3>
  <table class="compact">
    <thead><tr><th style="width:26%">Candidato</th><th style="width:33%">Qué respondería</th><th>Por qué no es el principal</th></tr></thead>
    <tbody>
      <tr><td><strong>93.45% incorporado 2017–2021</strong></td><td>Cuánto creció el catálogo en los últimos cinco años.</td><td>Es un hallazgo sobre la base, no la base. Sirve para explicar, no para denominar.</td></tr>
      <tr><td><strong>41.9% Estados Unidos</strong></td><td>Qué tan concentrado está el origen.</td><td>Es una conclusión geográfica; depende de que el total esté definido.</td></tr>
      <tr><td><strong>30.38% series</strong></td><td>Qué peso tiene la ficción seriada.</td><td>Es una lectura de composición; sin el total, el porcentaje flota.</td></tr>
      <tr><td><strong>98 min de mediana</strong></td><td>Cómo es la duración típica de una película.</td><td>Es una medida de distribución, no un indicador de cobertura.</td></tr>
    </tbody>
  </table>

  <h3 style="margin-top:4mm">Cómo responde el KPI principal a los filtros</h3>
  <table class="compact">
    <thead><tr><th>Selección</th><th class="num">Títulos</th><th class="num">% del catálogo</th><th>Lectura</th></tr></thead>
    <tbody>
      <tr><td>Catálogo completo</td><td class="num">{fmt_int(k['total_titulos'])}</td><td class="num">100.00%</td><td>Base de todas las comparaciones.</td></tr>
      <tr><td>Solo series</td><td class="num">{fmt_int(k['series'])}</td><td class="num">{fmt_pct(k['porcentaje_series'])}</td><td>El denominador cambia; los porcentajes se recalculan.</td></tr>
      <tr><td>País: Estados Unidos</td><td class="num">{fmt_int(k['top5_paises'][0]['count'])}</td><td class="num">{fmt_pct(k['top5_paises'][0]['share'])}</td><td>El mercado líder concentra cuatro de cada diez títulos.</td></tr>
      <tr><td>Sin país declarado</td><td class="num">{fmt_int(k['sin_pais']['titulos'])}</td><td class="num">{fmt_pct(k['sin_pais']['porcentaje'])}</td><td>El dato faltante también es una selección válida.</td></tr>
      <tr><td>Incorporado 2017–2021</td><td class="num">{fmt_int(k['ultimos_5_anios']['titulos'])}</td><td class="num">{fmt_pct(k['ultimos_5_anios']['porcentaje'])}</td><td>La expansión reciente es el fenómeno temporal dominante.</td></tr>
    </tbody>
  </table>

  <div class="callout" style="margin-top:3.5mm">
    <h4>La prueba de fuego</h4>
    <p>Si el KPI principal desapareciera, el usuario seguiría viendo gráficas, pero no sabría <strong>de qué total hablan</strong>. Esa es la diferencia entre un tablero y una colección de imágenes. El volumen filtrado es el contrato de lectura que une todas las vistas.</p>
  </div>
""",
    )


# ------------------------------------------------------------------
# 07 · Selección de gráficos
# ------------------------------------------------------------------

def chart_selection(dashboard: dict) -> str:
    k = dashboard["kpis"]
    return page(
        7,
        "04 · Visualizaciones",
        f"""
  {sec_head("04", "Visualizaciones", "Una gráfica para cada pregunta")}
  <p class="lead">La forma de la gráfica debe seguir a la operación mental que se pide al usuario. Comparar categorías no es lo mismo que mostrar una tendencia, una parte-todo o una distribución. Esta sección justifica cada elección y también lo que se descartó.</p>

  <div class="chart-grammar">
    <div>
      <div class="chart-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2.5" y="4" width="19" height="16"/><path d="M6 14l3-3 3 2 4-5 3 3"/></svg></div>
      <span class="k">Mapa</span>
      <p>Distribución geográfica y selección por país.</p>
    </div>
    <div>
      <div class="chart-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="7"/><path d="M12 5v7l5 3"/></svg></div>
      <span class="k">Dona</span>
      <p>Parte-todo con dos categorías y un total visible.</p>
    </div>
    <div>
      <div class="chart-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20V10M9 20V5M14 20V13M19 20V8"/></svg></div>
      <span class="k">Barras</span>
      <p>Comparación de magnitudes entre categorías.</p>
    </div>
    <div>
      <div class="chart-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 17l5-6 4 3 4-7 5 4"/></svg></div>
      <span class="k">Línea / área</span>
      <p>Tendencia y picos a lo largo del tiempo.</p>
    </div>
    <div>
      <div class="chart-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20V13M8 20V8M12 20V11M16 20V5M20 20V14"/></svg></div>
      <span class="k">Histograma</span>
      <p>Distribución de una variable continua.</p>
    </div>
  </div>

  <table class="compact">
    <thead>
      <tr>
        <th style="width:18%">KPI</th>
        <th style="width:18%">Pregunta</th>
        <th style="width:15%">Gráfico</th>
        <th style="width:27%">Por qué</th>
        <th>Alternativa descartada</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Títulos en el filtro</strong><br><span class="tiny">N1 · {fmt_int(k['total_titulos'])}</span></td>
        <td>¿Cuánto hay y dónde está?</td>
        <td><strong>Tarjeta + mapa</strong></td>
        <td>La cifra grande da el total; el mapa descompone el volumen por país y funciona como selector.</td>
        <td>Pastel: 119 países no caben. Barras: pierden la dimensión espacial.</td>
      </tr>
      <tr>
        <td><strong>Mezcla de formato</strong><br><span class="tiny">N2 · 69.62% / 30.38%</span></td>
        <td>¿Películas o series?</td>
        <td><strong>Dona</strong></td>
        <td>Dos categorías, parte-todo simple; el centro puede mostrar el total filtrado.</td>
        <td>Pastel 3D: distorsiona. Barras: correcto pero menos compacto para dos categorías.</td>
      </tr>
      <tr>
        <td><strong>Concentración geográfica</strong><br><span class="tiny">N2 · 41.9% EE. UU.</span></td>
        <td>¿Qué países concentran?</td>
        <td><strong>Barras horizontales</strong></td>
        <td>Ordena magnitudes y permite leer nombres largos sin rotar etiquetas.</td>
        <td>Mapa: ya se usó para el KPI principal. Pastel: 119 categorías.</td>
      </tr>
      <tr>
        <td><strong>Dinámica temporal</strong><br><span class="tiny">N2 · 93.45% · pico 2019</span></td>
        <td>¿Cuándo creció?</td>
        <td><strong>Línea / área</strong></td>
        <td>Muestra tendencia y picos; separa estreno de incorporación con dos relojes.</td>
        <td>Dispersión: no hay una hipótesis bivariada. Pastel: el tiempo no es parte-todo.</td>
      </tr>
      <tr>
        <td><strong>Duración mediana</strong><br><span class="tiny">N2 · 98 min</span></td>
        <td>¿Cómo se distribuye?</td>
        <td><strong>Histograma</strong></td>
        <td>Muestra la forma de la distribución y la mediana sin borrar los extremos.</td>
        <td>Un solo promedio: oculta la dispersión. Pastel: no aplica.</td>
      </tr>
    </tbody>
  </table>

  <div class="grid-2" style="margin-top:3.5mm">
    <div class="note-box">
      <strong>Reglas de selección.</strong>
      <ul style="margin:1.5mm 0 0;padding-left:4mm">
        <li>Tiempo → línea o área.</li>
        <li>Categorías → barras; si son muchas, horizontales.</li>
        <li>Parte-todo con 2 categorías → dona; con más de 5 → barras.</li>
        <li>Geografía → mapa + ranking; nunca solo color.</li>
        <li>Distribución → histograma; no pastel.</li>
      </ul>
    </div>
    <div class="note-box">
      <strong>Lo que se descartó y por qué.</strong>
      <p style="margin-top:1.5mm"><strong>Dispersión:</strong> no hay dos variables continuas con una pregunta clara; usarla sería decorar, no analizar.</p>
      <p><strong>Pastel para países:</strong> 119 categorías hacen ilegible cualquier ángulo.</p>
      <p><strong>Doble eje:</strong> mezclar minutos y temporadas en un mismo eje sería una comparación falsa.</p>
    </div>
  </div>
""",
    )


# ------------------------------------------------------------------
# 08 · Paleta
# ------------------------------------------------------------------

def palette_page() -> str:
    return page(
        8,
        "05 · Paleta y accesibilidad",
        """
  <div class="sec-head">
    <div class="sec-num">05</div>
    <div>
      <p class="sec-label">Paleta y accesibilidad</p>
      <h2>Cuatro colores, una jerarquía</h2>
    </div>
  </div>
  <p class="lead">La paleta no busca parecer “de datos”: busca que el ojo sepa dónde está el KPI principal, qué es una serie y qué es una nota. Cuatro colores base, dos neutros de apoyo y una regla: <strong>el color nunca es el único canal de información</strong>.</p>

  <div class="swatches">
    <article class="swatch">
      <div class="swatch-color" style="background:#171614"></div>
      <div class="swatch-body">
        <span class="k">01 · Estructura</span>
        <h3>Tinta</h3>
        <span class="swatch-hex">#171614</span>
        <p>Texto, ejes, títulos y bordes. Contraste 17.2:1 sobre papel.</p>
      </div>
    </article>
    <article class="swatch">
      <div class="swatch-color" style="background:#fbf9f5"></div>
      <div class="swatch-body">
        <span class="k">02 · Fondo</span>
        <h3>Papel</h3>
        <span class="swatch-hex">#fbf9f5</span>
        <p>Fondo cálido y tarjetas. Da respiración editorial sin competir con los datos.</p>
      </div>
    </article>
    <article class="swatch">
      <div class="swatch-color" style="background:#d90429"></div>
      <div class="swatch-body">
        <span class="k">03 · Énfasis</span>
        <h3>Rojo</h3>
        <span class="swatch-hex">#d90429</span>
        <p>KPI principal, películas, selección y foco. Contraste 4.99:1 sobre papel.</p>
      </div>
    </article>
    <article class="swatch">
      <div class="swatch-color" style="background:#b7791f"></div>
      <div class="swatch-body">
        <span class="k">04 · Contrapunto</span>
        <h3>Ámbar</h3>
        <span class="swatch-hex">#b7791f</span>
        <p>Series y acentos secundarios. 3.46:1: solo para marcas grandes, nunca texto pequeño.</p>
      </div>
    </article>
  </div>

  <div class="color-ratio" aria-label="Proporción de uso del color">
    <span class="paper" style="width:70%">70% papel y blanco</span>
    <span class="ink" style="width:20%">20% tinta</span>
    <span class="red" style="width:7%">7%</span>
    <span class="amber" style="width:3%">3%</span>
  </div>
  <div class="ratio-legend">
    <span>Base y tarjetas</span>
    <span>Texto y estructura</span>
    <span>Énfasis y selección</span>
    <span>Series y apoyo</span>
  </div>

  <div class="grid-2" style="margin-top:4mm">
    <div>
      <h3>Contraste verificado (WCAG 2.2)</h3>
      <table class="compact">
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

    <div>
      <h3>Por qué funciona para este tema</h3>
      <div class="brief-card" style="border-top-color:var(--red);margin-bottom:2.5mm">
        <span class="k">Coherencia temática</span>
        <p>El rojo remite al entretenimiento y a Netflix sin copiar su marca; el papel cálido evita el “dashboard corporativo” azul y gris.</p>
      </div>
      <div class="brief-card" style="border-top-color:var(--amber);margin-bottom:2.5mm">
        <span class="k">Jerarquía</span>
        <p>El rojo se reserva para el KPI principal y la selección; el ámbar distingue series; la tinta y el papel sostienen el resto.</p>
      </div>
      <div class="brief-card" style="border-top-color:var(--ink)">
        <span class="k">Accesibilidad</span>
        <p>No se usa rojo-verde como par único. Cada serie lleva etiqueta y valor directo; las gráficas tienen tabla equivalente.</p>
      </div>
    </div>
  </div>

  <div class="callout" style="margin-top:3.5mm">
    <h4>El color no es el único canal</h4>
    <p>Rojo y ámbar pueden confundirse en deuteranopia o protanopia. Por eso la dona separa físicamente las categorías, las barras llevan nombre y valor, el mapa tiene leyenda textual y cada vista ofrece una tabla o lista ordenada. El color acelera la lectura; no la sostiene solo.</p>
  </div>

  <p class="tiny" style="margin-top:2.5mm">Neutros de apoyo: <code>#6f6b63</code> para texto secundario, <code>#e0d9cc</code> para líneas y <code>#ffffff</code> para tarjetas. Los ratios se calcularon con la fórmula de luminancia relativa de WCAG 2.2.</p>
""",
    )


# ------------------------------------------------------------------
# 09 · Tipografía y retícula
# ------------------------------------------------------------------

def type_grid_page() -> str:
    return page(
        9,
        "06 · Tipografía, retícula y jerarquía",
        """
  <div class="sec-head">
    <div class="sec-num">06</div>
    <div>
      <p class="sec-label">Tipografía, retícula y jerarquía</p>
      <h2>La estructura que sostiene la lectura</h2>
    </div>
  </div>
  <p class="lead">Dos tipografías, una escala corta y una retícula de 12 columnas. La combinación busca una lectura editorial: titular con carácter, datos con precisión y notas que no compitan con la evidencia.</p>

  <div class="grid-2">
    <div>
      <h3>Escala tipográfica</h3>
      <table class="compact">
        <thead><tr><th>Rol</th><th>Fuente</th><th>Tamaño / peso</th></tr></thead>
        <tbody>
          <tr><td>Display</td><td>Fraunces</td><td>clamp(2.7rem, 6.4vw, 5.4rem) · 600</td></tr>
          <tr><td>Título de sección</td><td>Fraunces</td><td>clamp(1.6rem, 2.6vw, 2.3rem) · 600</td></tr>
          <tr><td>Título de tarjeta</td><td>Fraunces</td><td>1.3rem · 600</td></tr>
          <tr><td>KPI</td><td>Fraunces</td><td>clamp(2rem, 3.2vw, 2.7rem) · 600</td></tr>
          <tr><td>Texto</td><td>DM Sans</td><td>16px / 1.65 · 400</td></tr>
          <tr><td>Nota</td><td>DM Sans</td><td>11.5px / 1.55 · 400</td></tr>
          <tr><td>Etiqueta</td><td>DM Sans</td><td>9.5px · 500 · 0.16em</td></tr>
        </tbody>
      </table>
    </div>

    <div>
      <h3>Espacios y contenedores</h3>
      <table class="compact">
        <thead><tr><th>Token</th><th>Valor</th><th>Uso</th></tr></thead>
        <tbody>
          <tr><td>Página</td><td>1380 px</td><td>Ancho máximo del contenido</td></tr>
          <tr><td>Margen</td><td>clamp(20px, 4vw, 48px)</td><td>Respiro lateral</td></tr>
          <tr><td>Cabecera</td><td>68 px</td><td>Barra fija</td></tr>
          <tr><td>Riel</td><td>252 px</td><td>Columna de sección</td></tr>
          <tr><td>Separación</td><td>4 / 8 / 12 / 16 / 24 / 32 / 48 / 64</td><td>Escala de 4 px</td></tr>
          <tr><td>Radio</td><td>2 px</td><td>Bordes sobrios</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <h3 style="margin-top:3.5mm">Retícula de 12 columnas</h3>
  <div class="grid12" aria-hidden="true">""" + "".join("<span></span>" for _ in range(12)) + """</div>
  <div class="grid12-labels" aria-hidden="true">""" + "".join(f"<span>{i}</span>" for i in range(1, 13)) + """</div>
  <p class="tiny" style="margin-top:1.5mm">La implementación usa un riel de 3 columnas y 9 para el contenido. Dentro del contenido, los KPIs se organizan en 3 columnas y las gráficas se reparten en 2 o 3 bloques. La retícula no es una plantilla rígida: es una forma de mantener alineadas las jerarquías.</p>

  <h3 style="margin-top:3.5mm">Tres niveles de lectura</h3>
  <div class="level-cards">
    <article class="level-card n1">
      <span class="tag red">N1</span>
      <h3>Titular y KPI principal</h3>
      <p>El título y la cifra ancla. Es lo primero que se ve y lo que decide si el usuario sigue leyendo.</p>
    </article>
    <article class="level-card n2">
      <span class="tag" style="border-color:#d8c39a;background:#f8efdd;color:#7a5210">N2</span>
      <h3>Gráficas principales</h3>
      <p>Mapa, tiempo, géneros y tipos. Cada una responde una pregunta y comparte el mismo denominador.</p>
    </article>
    <article class="level-card n3">
      <span class="tag">N3</span>
      <h3>Filtros, leyendas y notas</h3>
      <p>El contexto que permite leer sin ruido: selección, escalas, ayuda y método.</p>
    </article>
  </div>

  <div class="note-box" style="margin-top:3.5mm">
    <strong>Reglas de énfasis.</strong> Un solo elemento rojo por vista; el KPI principal siempre con el mayor tamaño tipográfico; los títulos de gráfica por encima del texto; las notas en gris medio; sin sombras, degradados ni bordes decorativos. La jerarquía se construye con tamaño, posición y contraste, no con efectos.
  </div>
""",
    )


# ------------------------------------------------------------------
# 10 · Wireframe primera pantalla
# ------------------------------------------------------------------

def wireframe_first_screen(dashboard: dict) -> str:
    k = dashboard["kpis"]
    return page(
        10,
        "07 · Wireframe · primera pantalla",
        f"""
  {sec_head("07", "Wireframe · primera pantalla", "Qué ve el usuario antes de hacer scroll")}
  <p class="lead">El wireframe de alta fidelidad muestra la primera pantalla a 1440 px: cabecera, titular, ficha técnica, panel de KPIs y filtros. La retícula de 12 columnas está marcada en rojo; los números remiten a la leyenda inferior.</p>

  <div class="wf">
    <div class="wf-topbar"><span class="wf-dot"></span><span class="wf-dot"></span><span class="wf-dot"></span><span class="wf-url">catalogo-en-foco / inicio · 1440 px</span></div>
    <div class="wf-canvas">
      {wf_grid()}

      <div class="wf-header">
        <div class="wf-brand"><i></i>Catálogo en foco</div>
        <div class="wf-nav"><span>Inicio</span><span>Panorama</span><span>Mapa</span><span>Tiempo</span><span>Géneros</span><span class="wf-pill">PDF</span></div>
      </div>

      <div class="wf-hero-copy">
        <div class="wf-label">Proyecto 3 · Visualización de datos</div>
        <div class="wf-h1">La economía del<br><em>entretenimiento</em></div>
        <div class="wf-line dark" style="width:92%"></div>
        <div class="wf-line" style="width:84%"></div>
        <div class="wf-line" style="width:70%"></div>
        <div style="display:flex;gap:1.4mm;margin-top:2mm"><span class="wf-chip active">Explorar</span><span class="wf-chip">Leer informe</span></div>
      </div>

      <div class="wf-hero-figure">
        <div class="wf-label">Títulos analizados</div>
        <div class="wf-value">{fmt_int(k['total_titulos'])}</div>
        <div class="wf-line short"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1mm;margin-top:1.6mm">
          <div><div class="wf-label">Películas</div><div class="wf-value sm">{fmt_int(k['peliculas'])}</div></div>
          <div><div class="wf-label">Series</div><div class="wf-value sm">{fmt_int(k['series'])}</div></div>
          <div><div class="wf-label">Países</div><div class="wf-value sm">{k['paises_distintos']}</div></div>
          <div><div class="wf-label">Géneros</div><div class="wf-value sm">42</div></div>
        </div>
      </div>

      <div class="wf-kpi main">
        <span class="wf-tag n1">N1</span>
        <div class="wf-label">Títulos en el filtro</div>
        <div class="wf-value">{fmt_int(k['total_titulos'])}</div>
        <div class="wf-line short"></div>
        <span class="wf-pin">1</span>
      </div>
      <div class="wf-kpi">
        <span class="wf-tag n2">N2</span>
        <div class="wf-label">Películas</div>
        <div class="wf-value">{fmt_int(k['peliculas'])}</div>
        <div class="wf-line short"></div>
        <span class="wf-pin">2</span>
      </div>
      <div class="wf-kpi">
        <span class="wf-tag n2">N2</span>
        <div class="wf-label">Series</div>
        <div class="wf-value">{fmt_int(k['series'])}</div>
        <div class="wf-line short"></div>
        <span class="wf-pin">3</span>
      </div>
      <div class="wf-kpi">
        <span class="wf-tag n2">N2</span>
        <div class="wf-label">Países productores</div>
        <div class="wf-value">{k['paises_distintos']}</div>
        <div class="wf-line short"></div>
      </div>
      <div class="wf-kpi">
        <span class="wf-tag n2">N2</span>
        <div class="wf-label">Año con más estrenos</div>
        <div class="wf-value">{k['anio_mas_estrenos']['year']}</div>
        <div class="wf-line short"></div>
      </div>
      <div class="wf-kpi">
        <span class="wf-tag n2">N2</span>
        <div class="wf-label">Duración mediana</div>
        <div class="wf-value">{k['duracion_peliculas']['mediana_min']:.0f}<span style="font-size:5pt"> min</span></div>
        <div class="wf-line short"></div>
      </div>

      <div class="wf-filters">
        <div style="display:flex;gap:1mm"><span class="wf-chip active">Todo</span><span class="wf-chip">Películas</span><span class="wf-chip">Series</span></div>
        <div class="wf-select">Periodo ▾</div>
        <div class="wf-select">País o región ▾</div>
        <div class="wf-result">{fmt_int(k['total_titulos'])} títulos</div>
        <span class="wf-pin">4</span>
      </div>
    </div>
  </div>

  <div class="wf-legend-grid">
    <div><b>1</b><div><strong>KPI principal.</strong> Ocupa la primera celda del panel, con borde rojo y el mayor tamaño tipográfico. Es el ancla de lectura.</div></div>
    <div><b>2</b><div><strong>KPIs secundarios.</strong> Formato (dos tarjetas: películas y series), origen, tiempo y duración. Comparten el mismo peso visual y se leen como una sola frase.</div></div>
    <div><b>3</b><div><strong>Ficha técnica.</strong> El titular y la cifra del catálogo completo contextualizan antes de filtrar.</div></div>
    <div><b>4</b><div><strong>Filtros globales.</strong> Tipo, periodo y país; el contador confirma cuántos títulos quedan y alimenta todas las vistas.</div></div>
    <div><b>5</b><div><strong>Retícula.</strong> 12 columnas y 3 franjas. El KPI principal ocupa una celda; el titular, siete; la ficha, cinco.</div></div>
    <div><b>6</b><div><strong>Pliegue.</strong> La primera pantalla termina después de los filtros; el usuario decide si sigue al mapa o al tiempo.</div></div>
  </div>

  <h3 style="margin-top:4.5mm">El mismo KPI, tres selecciones</h3>
  <div class="filter-proof">
    <div><span class="k">Catálogo completo</span><strong>{fmt_int(k['total_titulos'])}</strong><p>100% del catálogo. Es el estado de reposo y el denominador global.</p></div>
    <div><span class="k">Solo series</span><strong>{fmt_int(k['series'])}</strong><p>{fmt_pct(k['porcentaje_series'])} del catálogo. El total cambia y los porcentajes se recalculan.</p></div>
    <div><span class="k">País: Estados Unidos</span><strong>{fmt_int(k['top5_paises'][0]['count'])}</strong><p>{fmt_pct(k['top5_paises'][0]['share'], 1)} del catálogo. El líder geográfico concentra cuatro de cada diez títulos.</p></div>
  </div>

  <p class="tiny" style="margin-top:2.5mm">Medidas de referencia: 1440 px de ancho, 1380 px de contenido, 48 px de margen, 24 px de separación entre columnas, 68 px de cabecera y 3 × 2 KPIs. El wireframe no usa datos inventados: las cifras son las del catálogo.</p>
""",
    )


# ------------------------------------------------------------------
# 11 · Wireframe área de análisis
# ------------------------------------------------------------------

def wireframe_analysis(dashboard: dict) -> str:
    k = dashboard["kpis"]
    return page(
        11,
        "08 · Wireframe · área de análisis",
        f"""
  {sec_head("08", "Wireframe · área de análisis", "Mapa, tiempo y composición")}
  <p class="lead">La segunda pantalla muestra el cuerpo analítico: un riel de sección a la izquierda y un área de gráficas a la derecha. El mapa abre la lectura geográfica; el tiempo, los géneros y la duración completan la composición. Las leyendas y notas viven dentro de cada tarjeta.</p>

  <div class="wf">
    <div class="wf-topbar"><span class="wf-dot"></span><span class="wf-dot"></span><span class="wf-dot"></span><span class="wf-url">catalogo-en-foco / mapa · 1440 px</span></div>
    <div class="wf-canvas" style="min-height:128mm">
      {wf_grid()}

      <div class="wf-rail">
        <div class="num">01</div>
        <div class="wf-h3" style="margin-top:1.4mm">Dónde se produce el catálogo</div>
        <div class="wf-line" style="width:88%"></div>
        <div class="wf-line" style="width:76%"></div>
        <div class="wf-line" style="width:64%"></div>
        <div style="margin-top:3mm;padding-top:1.6mm;border-top:0.5pt solid var(--line)">
          <div class="wf-label">Lectura</div>
          <div class="wf-line" style="width:92%"></div>
          <div class="wf-line" style="width:80%"></div>
          <div class="wf-line" style="width:68%"></div>
        </div>
        <div class="wf-rail-note">
          <div class="wf-label">Riel sticky</div>
          <div class="wf-line" style="width:86%"></div>
          <div class="wf-line" style="width:66%"></div>
        </div>
        <span class="wf-pin">1</span>
      </div>

      <div class="wf-main">
        <div class="wf-block wf-map">
          <div style="display:flex;justify-content:space-between;gap:2mm;align-items:start">
            <div><div class="wf-h3">Mapa mundial de títulos</div><div class="wf-line short"></div></div>
            <span class="wf-pill">Cómo leer</span>
          </div>
          <div class="wf-map-img"></div>
          <div class="wf-legend-row"><span><i></i>Sin títulos</span><span><i></i>1–1</span><span><i></i>2–3</span><span><i></i>4–11</span><span><i></i>12–62</span><span><i></i>63+</span></div>
          <div class="wf-line" style="width:96%"></div>
          <div class="wf-line" style="width:84%"></div>
          <span class="wf-pin">2</span>
        </div>

        <div class="wf-block wf-side white">
          <div class="wf-label">Sin país declarado</div>
          <div class="wf-value">{fmt_int(k['sin_pais']['titulos'])}</div>
          <div class="wf-line short"></div>
          <div style="margin-top:2.4mm;padding-top:1.6mm;border-top:0.5pt solid var(--line)">
            <div class="wf-label">Top países</div>
            <div class="wf-bars" style="height:16mm">
              <span style="height:100%"></span><span style="height:34%"></span><span style="height:26%"></span><span style="height:15%"></span><span style="height:13%"></span><span style="height:11%"></span><span style="height:9%"></span>
            </div>
            <div class="wf-line" style="width:78%"></div>
          </div>
          <span class="wf-pin">3</span>
        </div>

        <div class="wf-block wf-time white">
          <div style="display:flex;justify-content:space-between;gap:2mm;align-items:start">
            <div><div class="wf-h3">Estrenos e incorporaciones por año</div><div class="wf-line short"></div></div>
            <span class="wf-pill">Dos relojes</span>
          </div>
          <div class="wf-line-chart"></div>
          <div class="wf-legend-row"><span><i></i>Estreno</span><span><i></i>Incorporación</span><span><i></i>Corte 2021</span></div>
          <span class="wf-pin">4</span>
        </div>

        <div class="wf-block wf-genres white">
          <div class="wf-h3">Nube y ranking de géneros</div>
          <div class="wf-line short"></div>
          <div style="display:flex;gap:2mm;margin-top:1.4mm;align-items:flex-end">
            <div style="flex:1.1;height:22mm;border:0.4pt dashed var(--line-2);position:relative">
              <span style="position:absolute;left:2mm;top:2mm;font-size:4.6pt;color:var(--muted)">internacional</span>
              <span style="position:absolute;left:8mm;top:6mm;font-size:6pt;color:var(--red)">dramas</span>
              <span style="position:absolute;left:4mm;bottom:2mm;font-size:4.2pt;color:var(--muted)">comedias</span>
            </div>
            <div style="flex:1;display:flex;flex-direction:column;gap:0.8mm">
              <div class="wf-line dark" style="width:100%"></div>
              <div class="wf-line" style="width:82%"></div>
              <div class="wf-line" style="width:68%"></div>
              <div class="wf-line" style="width:54%"></div>
              <div class="wf-line" style="width:42%"></div>
            </div>
          </div>
          <span class="wf-pin">5</span>
        </div>

        <div class="wf-block wf-types white">
          <div class="wf-h3">Películas y series</div>
          <div class="wf-line short"></div>
          <div class="wf-donut"></div>
          <div class="wf-legend-row" style="justify-content:center"><span><i></i>Películas</span><span><i></i>Series</span></div>
          <span class="wf-pin">6</span>
        </div>

        <div class="wf-block wf-duration white">
          <div class="wf-h3">Distribución de duración</div>
          <div class="wf-line short"></div>
          <div class="wf-hist">
            <span style="height:12%"></span><span style="height:28%"></span><span style="height:52%"></span><span style="height:86%"></span><span style="height:100%"></span><span style="height:74%"></span><span style="height:48%"></span><span style="height:26%"></span><span style="height:14%"></span><span style="height:8%"></span>
          </div>
          <div class="wf-line" style="width:64%"></div>
        </div>
      </div>
    </div>
  </div>

  <div class="wf-legend-grid">
    <div><b>1</b><div><strong>Riel de sección.</strong> Título, número y una nota breve. Se mantiene sticky para no perder el contexto al hacer scroll.</div></div>
    <div><b>2</b><div><strong>Mapa como selector.</strong> El color codifica el conteo; la leyenda está debajo y el clic filtra el resto de las vistas.</div></div>
    <div><b>3</b><div><strong>Ranking lateral.</strong> Top países con barras y valores directos; los nombres largos caben sin rotar.</div></div>
    <div><b>4</b><div><strong>Tiempo.</strong> Estreno e incorporación se separan con trazo y leyenda; el corte del snapshot se marca explícitamente.</div></div>
    <div><b>5</b><div><strong>Géneros.</strong> La nube da una impresión; el ranking y la lista ordenada permiten comparar con cifras exactas.</div></div>
    <div><b>6</b><div><strong>Formato y duración.</strong> Dona para dos categorías; histograma para la distribución. Nunca se promedian minutos y temporadas juntos.</div></div>
  </div>
""",
    )


# ------------------------------------------------------------------
# 12 · Cuadrícula y jerarquía
# ------------------------------------------------------------------

def grid_hierarchy() -> str:
    return page(
        12,
        "09 · Cuadrícula y prioridad visual",
        """
  <div class="sec-head">
    <div class="sec-num">09</div>
    <div>
      <p class="sec-label">Cuadrícula y prioridad visual</p>
      <h2>Qué se lee primero, segundo y tercero</h2>
    </div>
  </div>
  <p class="lead">La cuadrícula 3 × 3 no es una plantilla de nueve cajas iguales: es un mapa de prioridades. El nivel 1 recibe el mayor contraste y el mayor tamaño; el nivel 2 sostiene la evidencia; el nivel 3 explica, filtra y contextualiza sin robar atención.</p>

  <div class="priority-grid">
    <div class="pg-cell n1">
      <span class="tag red">N1 · Marca y título</span>
      <h3>Qué es y de qué trata</h3>
      <p>“Catálogo en foco” y el titular editorial. La primera línea responde a “¿qué estoy viendo?”.</p>
      <span class="mark">1</span>
    </div>
    <div class="pg-cell n1">
      <span class="tag red">N1 · KPI principal</span>
      <h3>El ancla de lectura</h3>
      <p>8,807 títulos en el filtro. La cifra más grande del panel y el denominador de todo lo demás.</p>
      <span class="mark">2</span>
    </div>
    <div class="pg-cell n2">
      <span class="tag n2">N2 · Contexto</span>
      <h3>Ficha técnica</h3>
      <p>Fuente, cobertura, registro y actualización. Da credibilidad antes de que el usuario interprete.</p>
      <span class="mark">3</span>
    </div>

    <div class="pg-cell n3">
      <span class="tag n3">N3 · Filtros</span>
      <h3>Tipo, periodo y país</h3>
      <p>La periferia operativa: cambia el conjunto, pero no compite con el titular ni con el KPI.</p>
      <span class="mark">4</span>
    </div>
    <div class="pg-cell n2">
      <span class="tag n2">N2 · Evidencia principal</span>
      <h3>Mapa y tiempo</h3>
      <p>Las dos vistas que responden “dónde” y “cuándo”. Ocupan el centro visual del área de análisis.</p>
      <span class="mark">5</span>
    </div>
    <div class="pg-cell n3">
      <span class="tag n3">N3 · Leyendas</span>
      <h3>Escalas y ayuda</h3>
      <p>La leyenda vive cerca de la marca; la ayuda “cómo leer” está a un clic, no en un manual aparte.</p>
      <span class="mark">6</span>
    </div>

    <div class="pg-cell n2">
      <span class="tag n2">N2 · Composición</span>
      <h3>Géneros y formato</h3>
      <p>Nube, ranking, dona y barras. Cada una añade una dimensión sin repetir la anterior.</p>
      <span class="mark">7</span>
    </div>
    <div class="pg-cell n2">
      <span class="tag n2">N2 · Distribución</span>
      <h3>Duración y patrones</h3>
      <p>Histograma y matrices. El detalle que matiza la historia principal y evita conclusiones planas.</p>
      <span class="mark">8</span>
    </div>
    <div class="pg-cell n3">
      <span class="tag n3">N3 · Método</span>
      <h3>Límites y notas</h3>
      <p>Qué falta, qué no se imputa y qué no se puede afirmar. La honestidad también es jerarquía.</p>
      <span class="mark">9</span>
    </div>
  </div>

  <h3>Peso visual de cada elemento</h3>
  <table class="compact">
    <thead><tr><th style="width:25%">Elemento</th><th style="width:12%">Nivel</th><th style="width:24%">Tamaño / contraste</th><th>Función</th></tr></thead>
    <tbody>
      <tr><td><strong>Titular</strong></td><td>N1</td><td>Display · tinta</td><td>Dar tema y tono editorial.</td></tr>
      <tr><td><strong>KPI principal</strong></td><td>N1</td><td>Mayor cifra · rojo</td><td>Anclar el denominador y el filtro.</td></tr>
      <tr><td><strong>Gráficas principales</strong></td><td>N2</td><td>Tarjeta blanca · tinta</td><td>Mostrar la evidencia del hallazgo.</td></tr>
      <tr><td><strong>KPIs secundarios</strong></td><td>N2</td><td>Cifra media · tinta/ámbar</td><td>Contextualizar el KPI principal.</td></tr>
      <tr><td><strong>Filtros</strong></td><td>N3</td><td>Chips y selects · borde</td><td>Cambiar el conjunto sin competir.</td></tr>
      <tr><td><strong>Leyendas y notas</strong></td><td>N3</td><td>Texto pequeño · gris</td><td>Explicar escalas, límites y método.</td></tr>
    </tbody>
  </table>

  <div class="callout" style="margin-top:3.5mm">
    <h4>El recorrido de lectura</h4>
    <p>El ojo entra por el titular (1), cae al KPI principal (2), recorre la franja de contexto (3) y decide si baja al bloque de evidencia (5). Los filtros (4) y las leyendas (6) están en la periferia para que el usuario los encuentre cuando los necesita, no antes. Esa secuencia es la que convierte una cuadrícula en una narrativa.</p>
  </div>
""",
    )


# ------------------------------------------------------------------
# 13 · Responsive y accesibilidad
# ------------------------------------------------------------------

def responsive_page() -> str:
    return page(
        13,
        "10 · Responsive y accesibilidad",
        """
  <div class="sec-head">
    <div class="sec-num">10</div>
    <div>
      <p class="sec-label">Responsive y accesibilidad</p>
      <h2>La misma jerarquía en 390 px</h2>
    </div>
  </div>
  <p class="lead">El diseño no se “reduce”: se reordena. En móvil, el KPI principal sigue siendo el primero, las gráficas se apilan y las tablas hacen scroll dentro de su tarjeta. La accesibilidad no es una capa final; es una condición de la retícula.</p>

  <div class="device-grid">
    <div class="device desktop">
      <div class="screen">
        <div class="bar"></div>
        <div class="hero-mini"></div>
        <div class="kpis-mini"><span></span><span></span><span></span><span></span><span></span><span></span></div>
        <div class="charts-mini"><span></span><span></span><span></span><span></span></div>
      </div>
      <p class="caption"><strong>1440 px.</strong> 12 columnas, 3 × 2 KPIs, 2 columnas de gráficas, riel lateral.</p>
    </div>
    <div class="device tablet">
      <div class="screen">
        <div class="bar"></div>
        <div class="hero-mini"></div>
        <div class="kpis-mini"><span></span><span></span><span></span><span></span><span></span><span></span></div>
        <div class="charts-mini"><span></span><span></span></div>
      </div>
      <p class="caption"><strong>1024 px.</strong> El riel pasa arriba; KPIs en 2 columnas; gráficas apiladas.</p>
    </div>
    <div class="device phone">
      <div class="screen">
        <div class="bar"></div>
        <div class="hero-mini"></div>
        <div class="kpis-mini"><span></span><span></span><span></span><span></span><span></span><span></span></div>
        <div class="charts-mini"><span></span><span></span><span></span></div>
      </div>
      <p class="caption"><strong>390 px.</strong> Una columna; KPIs 2 × 3; filtros plegables; sin scroll horizontal.</p>
    </div>
  </div>

  <h3>Puntos de quiebre</h3>
  <table class="compact">
    <thead><tr><th style="width:16%">Ancho</th><th style="width:28%">Cambio</th><th>Por qué</th></tr></thead>
    <tbody>
      <tr><td><strong>≤ 1180 px</strong></td><td>La navegación de escritorio se oculta; aparece el menú.</td><td>Evitar que la barra superior se comprima.</td></tr>
      <tr><td><strong>≤ 1100 px</strong></td><td>El riel lateral pasa arriba; las gráficas de 2 columnas se apilan.</td><td>Mantener el título de sección junto al contenido.</td></tr>
      <tr><td><strong>≤ 980 px</strong></td><td>Los filtros avanzados se pliegan.</td><td>Dar prioridad al KPI y al mapa en pantallas medianas.</td></tr>
      <tr><td><strong>≤ 900 px</strong></td><td>El hero pasa de 2 columnas a 1.</td><td>Evitar que el titular y la ficha técnica se aplasten.</td></tr>
      <tr><td><strong>≤ 520 px</strong></td><td>Los KPIs pasan de 3 a 2 columnas; el KPI principal conserva el primer lugar.</td><td>Mantener legibilidad sin perder la jerarquía.</td></tr>
    </tbody>
  </table>

  <div class="grid-2" style="margin-top:3.5mm">
    <div>
      <h3>Accesibilidad</h3>
      <ul class="checklist">
        <li>Contraste AA en texto y controles; el ámbar se reserva para marcas grandes.</li>
        <li>Foco visible de 2 px en rojo; navegación completa por teclado.</li>
        <li>Mapa con <code>role="button"</code>, <code>aria-label</code> y activación con Enter/Espacio.</li>
        <li>Tablas equivalentes para rankings, matrices y nube de palabras.</li>
        <li><code>prefers-reduced-motion</code> desactiva contadores y revelados.</li>
      </ul>
    </div>
    <div>
      <h3>Estados del sistema</h3>
      <div class="states">
        <span class="state-chip">Reposo</span>
        <span class="state-chip active">Activo</span>
        <span class="state-chip focus">Foco</span>
        <span class="state-chip">Sin datos</span>
        <span class="state-chip">Cargando</span>
      </div>
      <p class="tiny" style="margin-top:2mm">El estado vacío explica por qué no hay títulos y ofrece “Limpiar filtros”; el estado de carga muestra el progreso del catálogo; el foco nunca depende solo del color.</p>
      <div class="note-box" style="margin-top:2.5mm">
        <strong>Prueba de 390 px.</strong> La página no debe tener scroll horizontal. Las tablas y matrices hacen scroll dentro de <code>.table-scroll</code>; el resto del contenido se apila en una columna.
      </div>
    </div>
  </div>
""",
    )


# ------------------------------------------------------------------
# Ensamblado
# ------------------------------------------------------------------

def build_html(quality: dict, dashboard: dict) -> str:
    pages = [
        cover(),
        index_page(),
        brief_page(dashboard),
        starting_point(dashboard),
        kpi_hierarchy(dashboard),
        kpi_justification(dashboard),
        chart_selection(dashboard),
        palette_page(),
        type_grid_page(),
        wireframe_first_screen(dashboard),
        wireframe_analysis(dashboard),
        grid_hierarchy(),
        responsive_page(),
    ]
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{BRAND} · Diseño visual Fase 2</title>
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
