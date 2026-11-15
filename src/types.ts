export type TitleRow = [
  type: number, // 0 = película, 1 = serie
  releaseYear: number,
  addedYear: number | null,
  addedMonth: number | null,
  durationMin: number | null,
  seasons: number | null,
  rating: number, // índice en dimensions.ratings, -1 = sin dato
  primaryCountry: number, // índice en dimensions.countries, -1 = sin dato
  genres: number[],
  countries: number[],
  hasDirector: number,
  directors: number[],
];

export interface CountryDim {
  name: string;
  label: string;
  iso3: string;
  isoN: number;
  region: string;
  count: number;
}

export interface GenreDim {
  name: string;
  label: string;
  count: number;
}

export interface Finding {
  id: string;
  titulo: string;
  texto: string;
  cifra: string;
  detalle: string;
}

export interface QualityField {
  campo: string;
  tipo: string;
  nulos: number;
  porcentaje_nulos: number;
  valores_distintos: number;
  nota?: string | null;
}

export interface QualityReport {
  generado_en: string;
  archivo: { nombre: string; bytes: number; sha256: string };
  snapshot: {
    corte: string;
    min_date_added: string;
    max_date_added: string;
    fechas_distintas: number;
    nota: string;
  };
  totales: {
    filas: number;
    titulos_unicos: number;
    columnas: number;
    peliculas: number;
    series: number;
    porcentaje_series: number;
    muestreo: string;
  };
  duplicados: { show_id: number; filas_completas: number };
  campos: QualityField[];
  cobertura: {
    release_year_min: number;
    release_year_max: number;
    anios_con_titulos: number;
    anios_sin_titulos: number[];
    nota: string;
    paises_distintos: number;
    generos_distintos: number;
    directores_distintos: number;
    titulos_sin_pais: number;
    titulos_sin_director: number;
    porcentaje_sin_director: number;
  };
  anomalias: {
    rating_con_duracion: Array<{
      show_id: string;
      title: string;
      rating_was_duration: boolean;
      duration_min: number;
    }>;
    date_added_antes_de_release_year: Array<{
      show_id: string;
      title: string;
      release_year: number;
      added_date: string;
    }>;
    rating_nulos: Array<{ show_id: string; title: string }>;
    date_added_nulos: Array<{ show_id: string; title: string }>;
    paises_historicos_normalizados: Array<{ country_raw: string; titles: number }>;
    elementos_multivaluados_con_espacios: number;
    nota: string;
  };
  multivaluados: {
    generos_por_titulo: { min: number; max: number; tabla: string };
    paises_por_titulo: { min: number; max: number; tabla: string; nota: string };
    directores_por_titulo: { max: number };
    regla_porcentajes: string;
  };
  normalizaciones: Array<{ regla: string; detalle: string }>;
}

export interface Kpis {
  total_titulos: number;
  peliculas: number;
  series: number;
  porcentaje_series: number;
  paises_distintos: number;
  top5_paises: Array<{ name: string; count: number; share: number }>;
  anio_mas_estrenos: { year: number; count: number };
  anio_mas_incorporaciones: { year: number; count: number };
  top5_generos: Array<{ name: string; count: number; share: number }>;
  top5_directores: Array<{ name: string; count: number; share: number }>;
  directores_distintos: number;
  titulos_sin_director: number;
  porcentaje_sin_director: number;
  duracion_peliculas: {
    n: number;
    promedio_min: number;
    mediana_min: number;
    min: number;
    max: number;
  };
  temporadas_series: { n: number; mediana: number; max: number };
  rating_mas_frecuente: { name: string; count: number; share: number };
  ultimos_5_anios: { desde: number; hasta: number; titulos: number; porcentaje: number };
  variacion_por_decada: Array<{ decade: number; total: number; variation_pct: number | null }>;
  sin_pais: { titulos: number; porcentaje: number };
  definiciones: Record<string, string>;
}

export interface DashboardData {
  meta: {
    titulo: string;
    subtitulo: string;
    fuente: string;
    url_fuente: string;
    snapshot: string;
    snapshot_nota: string;
    generado_en: string;
    total_titulos: number;
    peliculas: number;
    series: number;
    moneda: string;
  };
  kpis: Kpis;
  findings: Finding[];
  dimensions: {
    genres: GenreDim[];
    countries: CountryDim[];
    ratings: string[];
    regions: string[];
    decades: number[];
    directors: string[];
  };
  titles: {
    columns: string[];
    rows: TitleRow[];
  };
  aggregates: {
    by_year_release: Array<{ year: number; movies: number; series: number; total: number }>;
    by_year_added: Array<{ year: number; movies: number; series: number; total: number }>;
    by_country: Array<{
      name: string;
      label: string;
      iso3: string;
      isoN: number;
      region: string;
      titles: number;
      avg_duration_min: number | null;
      top_genre: string;
      top_genre_es: string;
      share: number;
    }>;
    by_genre: Array<{ name: string; label: string; count: number; share: number }>;
    by_rating: Array<{ name: string; count: number; share: number }>;
    by_decade: Array<{
      decade: number;
      total: number;
      movies: number;
      series: number;
      variation_pct: number | null;
      is_partial: boolean;
    }>;
    by_region: Array<{ region: string; titles: number; share: number }>;
    duration_hist: Array<{ bin: string; from: number; to: number; count: number }>;
    seasons_dist: Array<{ seasons: number; count: number }>;
    directors_top: Array<{ name: string; count: number; share: number }>;
    decade_genre: Array<{ decade: number; genre: string; count: number }>;
    year_month: Array<{ year: number; month: number; count: number }>;
    type_counts: Array<{ type: string; count: number; share: number }>;
  };
  quality: QualityReport;
}
