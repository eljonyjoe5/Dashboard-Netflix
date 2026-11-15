import { useState } from "react";
import type { DashboardData } from "../types";
import { fmtInt } from "../lib/format";
import type { Filters, PeriodFilter, PlaceFilter, TypeFilter } from "../lib/aggregate";
import { hasActiveFilters } from "../lib/aggregate";

function periodValue(period: PeriodFilter): string {
  if (period.kind === "all") return "all";
  if (period.kind === "decade") return `d:${period.decade}`;
  return "custom";
}

function placeValue(place: PlaceFilter): string {
  if (place.kind === "all") return "all";
  if (place.kind === "unknown") return "unknown";
  if (place.kind === "region") return `r:${place.region}`;
  return `c:${place.index}`;
}

export function Filters({
  data,
  filters,
  onChange,
  resultCount,
  onClear,
}: {
  data: DashboardData;
  filters: Filters;
  onChange: (filters: Filters) => void;
  resultCount: number;
  onClear: () => void;
}) {
  const [open, setOpen] = useState(false);
  const snapshotYear = Number(data.meta.snapshot.slice(0, 4));
  const decades = data.aggregates.by_decade.filter((d) => d.total > 0);
  const customFrom = filters.period.kind === "range" ? filters.period.from : 2000;
  const customTo = filters.period.kind === "range" ? filters.period.to : snapshotYear;
  const active = hasActiveFilters(filters);

  const setType = (type: TypeFilter) => onChange({ ...filters, type });

  const setPeriod = (raw: string) => {
    if (raw === "all") onChange({ ...filters, period: { kind: "all" } });
    else if (raw === "custom")
      onChange({ ...filters, period: { kind: "range", from: customFrom, to: customTo } });
    else {
      const decade = Number(raw.replace("d:", ""));
      onChange({ ...filters, period: { kind: "decade", decade } });
    }
  };

  const setRange = (from: number, to: number) => {
    onChange({
      ...filters,
      period: { kind: "range", from: Math.min(from, to), to: Math.max(from, to) },
    });
  };

  const setPlace = (raw: string) => {
    if (raw === "all") onChange({ ...filters, place: { kind: "all" } });
    else if (raw === "unknown") onChange({ ...filters, place: { kind: "unknown" } });
    else if (raw.startsWith("r:")) onChange({ ...filters, place: { kind: "region", region: raw.slice(2) } });
    else onChange({ ...filters, place: { kind: "country", index: Number(raw.slice(2)) } });
  };

  const typeOptions: Array<{ value: TypeFilter; label: string }> = [
    { value: "todo", label: "Todo" },
    { value: "pelicula", label: "Películas" },
    { value: "serie", label: "Series" },
  ];

  return (
    <div className="filters-wrap">
      <div className="filters" aria-label="Filtros globales del tablero">
        <div className="filter-group filter-type">
          <span className="filter-label" id="filtro-tipo">
            Tipo
          </span>
          <div className="type-chips" role="group" aria-labelledby="filtro-tipo">
            {typeOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`chip ${filters.type === option.value ? "is-active" : ""}`}
                aria-pressed={filters.type === option.value}
                onClick={() => setType(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        <button
          type="button"
          className="filter-toggle"
          aria-expanded={open}
          aria-controls="filtros-avanzados"
          onClick={() => setOpen((v) => !v)}
        >
          <span aria-hidden="true">⌁</span> Filtros
          {active ? <span className="filter-dot" aria-hidden="true" /> : null}
        </button>

        <div className={`filter-advanced ${open ? "is-open" : ""}`} id="filtros-avanzados">
          <div className="filter-group">
            <label className="filter-label" htmlFor="filtro-periodo">
              Periodo <span className="filter-hint">(año de estreno)</span>
            </label>
            <select id="filtro-periodo" value={periodValue(filters.period)} onChange={(e) => setPeriod(e.target.value)}>
              <option value="all">Todo el periodo</option>
              {decades.map((d) => (
                <option key={d.decade} value={`d:${d.decade}`}>
                  Década de {d.decade}
                  {d.is_partial ? ` (2020–${snapshotYear}, parcial)` : ""}
                </option>
              ))}
              <option value="custom">Rango personalizado…</option>
            </select>
          </div>

          {filters.period.kind === "range" ? (
            <div className="filter-group filter-range">
              <span className="filter-label">Entre</span>
              <div className="range-row">
                <select
                  aria-label="Año inicial"
                  value={customFrom}
                  onChange={(e) => setRange(Number(e.target.value), customTo)}
                >
                  {Array.from({ length: snapshotYear - 1925 + 1 }, (_, i) => 1925 + i).map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
                <span aria-hidden="true">y</span>
                <select aria-label="Año final" value={customTo} onChange={(e) => setRange(customFrom, Number(e.target.value))}>
                  {Array.from({ length: snapshotYear - 1925 + 1 }, (_, i) => 1925 + i).map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          ) : null}

          <div className="filter-group filter-place">
            <label className="filter-label" htmlFor="filtro-pais">
              País o región
            </label>
            <select id="filtro-pais" value={placeValue(filters.place)} onChange={(e) => setPlace(e.target.value)}>
              <option value="all">Todos los países y regiones</option>
              <option value="unknown">Sin país declarado ({fmtInt(data.kpis.sin_pais.titulos)})</option>
              <optgroup label="Regiones">
                {data.dimensions.regions.map((region) => (
                  <option key={region} value={`r:${region}`}>
                    {region}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Países">
                {data.dimensions.countries.map((country, index) => (
                  <option key={country.name} value={`c:${index}`}>
                    {country.label}
                  </option>
                ))}
              </optgroup>
            </select>
          </div>
        </div>

        <div className="filter-result" aria-live="polite">
          <strong>{fmtInt(resultCount)}</strong>
          <span>títulos en el filtro</span>
        </div>

        {active ? (
          <button type="button" className="clear-btn" onClick={onClear}>
            Limpiar
          </button>
        ) : null}
      </div>

      {active ? (
        <div className="active-filters" aria-label="Filtros activos">
          {filters.type !== "todo" ? (
            <button type="button" className="active-chip" onClick={() => setType("todo")}>
              {filters.type === "pelicula" ? "Películas" : "Series"} <span aria-hidden="true">×</span>
            </button>
          ) : null}
          {filters.period.kind !== "all" ? (
            <button
              type="button"
              className="active-chip"
              onClick={() => onChange({ ...filters, period: { kind: "all" } })}
            >
              {filters.period.kind === "decade"
                ? `Década de ${filters.period.decade}`
                : `${filters.period.from}–${filters.period.to}`}{" "}
              <span aria-hidden="true">×</span>
            </button>
          ) : null}
          {filters.place.kind !== "all" ? (
            <button
              type="button"
              className="active-chip"
              onClick={() => onChange({ ...filters, place: { kind: "all" } })}
            >
              {filters.place.kind === "region"
                ? filters.place.region
                : filters.place.kind === "country"
                  ? data.dimensions.countries[filters.place.index].label
                  : "Sin país"}{" "}
              <span aria-hidden="true">×</span>
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
