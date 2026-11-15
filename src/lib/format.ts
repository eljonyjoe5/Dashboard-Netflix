const intFmt = new Intl.NumberFormat("es-MX", { maximumFractionDigits: 0 });
const oneDecimal = new Intl.NumberFormat("es-MX", { maximumFractionDigits: 1 });
const twoDecimals = new Intl.NumberFormat("es-MX", { maximumFractionDigits: 2 });

export const fmtInt = (n: number): string => intFmt.format(n);
export const fmt1 = (n: number): string => oneDecimal.format(n);
export const fmt2 = (n: number): string => twoDecimals.format(n);

export const fmtPct = (n: number): string => `${oneDecimal.format(n)}%`;
export const fmtMin = (n: number): string => `${intFmt.format(Math.round(n))} min`;

export const fmtCompact = (n: number): string =>
  n >= 1000 ? `${oneDecimal.format(n / 1000)} mil` : intFmt.format(n);

const MONTHS = [
  "enero",
  "febrero",
  "marzo",
  "abril",
  "mayo",
  "junio",
  "julio",
  "agosto",
  "septiembre",
  "octubre",
  "noviembre",
  "diciembre",
];

const MONTHS_SHORT = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

export const monthName = (m: number): string => MONTHS[m - 1] ?? "";
export const monthShort = (m: number): string => MONTHS_SHORT[m - 1] ?? "";

export function fmtDateEs(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  if (!y || !m || !d) return iso;
  return `${d} de ${MONTHS[m - 1]} de ${y}`;
}

export function decadeLabel(decade: number): string {
  return `Década de ${decade}`;
}

export function decadeRange(decade: number, snapshotYear: number): string {
  if (decade === 2020) return `2020–${snapshotYear} (parcial)`;
  return `${decade}–${decade + 9}`;
}

export const signedPct = (n: number | null): string => {
  if (n === null || !Number.isFinite(n)) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${oneDecimal.format(n)}%`;
};
