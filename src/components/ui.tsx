import { useId, useState, type ReactNode } from "react";
import { useInView } from "../hooks/useUi";

export function Section({
  id,
  num,
  title,
  intro,
  children,
  className = "",
}: {
  id: string;
  num: string;
  title: string;
  intro?: string;
  children: ReactNode;
  className?: string;
}) {
  const { ref, inView } = useInView<HTMLElement>();
  return (
    <section id={id} ref={ref} className={`section ${inView ? "is-visible" : ""} ${className}`.trim()}>
      <header className="section-head">
        <span className="section-num" aria-hidden="true">
          {num}
        </span>
        <div className="section-head-text">
          <h2>{title}</h2>
          {intro ? <p>{intro}</p> : null}
        </div>
      </header>
      <div className="section-body">{children}</div>
    </section>
  );
}

export function ChartCard({
  title,
  subtitle,
  help,
  legend,
  axis,
  note,
  actions,
  children,
  className = "",
}: {
  title: string;
  subtitle?: string;
  help: string[];
  legend?: ReactNode;
  axis?: string;
  note?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  const [open, setOpen] = useState(false);
  const panelId = useId();

  return (
    <article className={`chart-card ${className}`.trim()}>
      <div className="chart-card-head">
        <div className="chart-card-title">
          <h3>{title}</h3>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
        <div className="chart-card-actions">
          {actions}
          <button
            type="button"
            className="help-btn"
            aria-expanded={open}
            aria-controls={panelId}
            onClick={() => setOpen((v) => !v)}
          >
            <span className="help-icon" aria-hidden="true">
              ?
            </span>
            ¿Cómo leer esta gráfica?
          </button>
        </div>
      </div>

      {open ? (
        <div className="help-panel" id={panelId}>
          <ul>
            {help.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="chart-body">{children}</div>

      {legend ? <div className="chart-legend">{legend}</div> : null}
      {axis ? <p className="axis-caption">{axis}</p> : null}
      {note ? <p className="chart-note">{note}</p> : null}
    </article>
  );
}

export function Legend({
  items,
}: {
  items: Array<{ color: string; label: string; shape?: "square" | "circle" | "line" }>;
}) {
  return (
    <ul className="legend-list" aria-label="Leyenda">
      {items.map((item) => (
        <li key={item.label}>
          <span
            className={`legend-swatch ${item.shape ?? "square"}`}
            style={{ background: item.color }}
            aria-hidden="true"
          />
          {item.label}
        </li>
      ))}
    </ul>
  );
}

export function Segmented<T extends string>({
  options,
  value,
  onChange,
  ariaLabel,
}: {
  options: Array<{ value: T; label: string }>;
  value: T;
  onChange: (value: T) => void;
  ariaLabel: string;
}) {
  return (
    <div className="segmented" role="group" aria-label={ariaLabel}>
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          className={option.value === value ? "is-active" : ""}
          aria-pressed={option.value === value}
          onClick={() => onChange(option.value)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

export function Note({ children }: { children: ReactNode }) {
  return <p className="data-note">{children}</p>;
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="empty-state" role="status">
      <span aria-hidden="true">◌</span>
      <p>{message}</p>
    </div>
  );
}
