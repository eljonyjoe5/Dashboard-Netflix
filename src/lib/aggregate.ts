import type { CountryDim, DashboardData, TitleRow } from "../types";

export type TypeFilter = "todo" | "pelicula" | "serie";

export type PeriodFilter =
  | { kind: "all" }
  | { kind: "decade"; decade: number }
  | { kind: "range"; from: number; to: number };

export type PlaceFilter =
  | { kind: "all" }
  | { kind: "region"; region: string }
  | { kind: "country"; index: number }
  | { kind: "unknown" };

export interface Filters {
  type: TypeFilter;
  period: PeriodFilter;
  place: PlaceFilter;
}

export const DEFAULT_FILTERS: Filters = {
  type: "todo",
  period: { kind: "all" },
  place: { kind: "all" },
};

export interface CountryStat {
  index: number;
  name: string;
  label: string;
  iso3: string;
  isoN: number;
  region: string;
  count: number;
  share: number;
  topGenre: string;
  topGenreLabel: string;
  avgDuration: number | null;
}

export interface GenreStat {
  index: number;
  name: string;
  label: string;
  count: number;
  share: number;
}

export interface DirectorStat {
  index: number;
  name: string;
  count: number;
  share: number;
  topGenre: string;
}

export interface RatingStat {
  name: string;
  count: number;
  share: number;
}

export interface YearStat {
  year: number;
  movies: number;
  series: number;
  total: number;
}

export interface DecadeStat {
  decade: number;
  total: number;
  movies: number;
  series: number;
  variation: number | null;
  partial: boolean;
}

export interface Derived {
  count: number;
  movies: number;
  series: number;
  seriesShare: number;
  countryCount: number;
  noCountry: number;
  noDirector: number;
  noDirectorShare: number;
  directorTitles: number;
  topCountries: CountryStat[];
  byCountry: CountryStat[];
  topGenres: GenreStat[];
  byGenre: GenreStat[];
  topDirectors: DirectorStat[];
  peakRelease: { year: number; count: number } | null;
  peakAdded: { year: number; count: number } | null;
  movieDuration: { n: number; avg: number; median: number };
  seasons: { n: number; median: number };
  topRating: RatingStat | null;
  byRating: RatingStat[];
  last5: { from: number; to: number; count: number; share: number };
  byYearRelease: YearStat[];
  byYearAdded: YearStat[];
  byDecade: DecadeStat[];
  durationHist: Array<{ bin: string; from: number; to: number; count: number }>;
  seasonsDist: Array<{ seasons: number; count: number }>;
  decadeGenre: Array<{ decade: number; genre: string; label: string; count: number }>;
  yearMonth: Array<{ year: number; month: number; count: number }>;
  typeCounts: Array<{ type: string; count: number; share: number }>;
  regionCounts: Array<{ region: string; count: number; share: number }>;
}

const RELEASE_MIN = 1925;
const RELEASE_MAX = 2021;
const ADDED_MIN = 2008;
const ADDED_MAX = 2021;
const DECADES = [1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020];

function median(values: number[]): number {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

function matchesType(row: TitleRow, type: TypeFilter): boolean {
  if (type === "todo") return true;
  return type === "serie" ? row[0] === 1 : row[0] === 0;
}

function matchesPeriod(row: TitleRow, period: PeriodFilter): boolean {
  if (period.kind === "all") return true;
  if (period.kind === "decade") return row[1] >= period.decade && row[1] <= period.decade + 9;
  return row[1] >= period.from && row[1] <= period.to;
}

function matchesPlace(row: TitleRow, place: PlaceFilter, countries: CountryDim[]): boolean {
  if (place.kind === "all") return true;
  if (place.kind === "unknown") return row[9].length === 0;
  if (place.kind === "country") return row[9].includes(place.index);
  return row[9].some((ci) => countries[ci].region === place.region);
}

export function derive(data: DashboardData, filters: Filters): Derived {
  const { countries, genres, ratings, regions } = data.dimensions;
  const G = genres.length;
  const C = countries.length;
  const R = ratings.length;
  const D = data.dimensions.directors.length;

  const regionIndex = new Map(regions.map((r, i) => [r, i]));
  const regionOfCountry = new Int32Array(C);
  countries.forEach((c, i) => {
    regionOfCountry[i] = regionIndex.get(c.region) ?? 0;
  });

  const rows = data.titles.rows.filter(
    (row) =>
      matchesType(row, filters.type) &&
      matchesPeriod(row, filters.period) &&
      matchesPlace(row, filters.place, countries),
  );

  const count = rows.length;

  // Acumuladores
  const relMovies = new Int32Array(RELEASE_MAX - RELEASE_MIN + 1);
  const relSeries = new Int32Array(RELEASE_MAX - RELEASE_MIN + 1);
  const addMovies = new Int32Array(ADDED_MAX - ADDED_MIN + 1);
  const addSeries = new Int32Array(ADDED_MAX - ADDED_MIN + 1);
  const genreCounts = new Int32Array(G);
  const countryCounts = new Int32Array(C);
  const countryDurSum = new Float64Array(C);
  const countryDurN = new Int32Array(C);
  const countryGenre = new Int32Array(C * G);
  const ratingCounts = new Int32Array(R);
  const decadeMovies = new Int32Array(DECADES.length);
  const decadeSeries = new Int32Array(DECADES.length);
  const decadeGenre = new Int32Array(DECADES.length * (10 + 1));
  const yearMonth = new Int32Array((ADDED_MAX - ADDED_MIN + 1) * 12);
  const durationBins = new Int32Array(data.aggregates.duration_hist.length);
  const seasonsCounts = new Int32Array(18);
  const directorCounts = new Int32Array(D);
  const regionCounts = new Int32Array(regions.length);

  const durations: number[] = [];
  const seasonValues: number[] = [];

  let movies = 0;
  let series = 0;
  let noCountry = 0;
  let noDirector = 0;
  let last5 = 0;
  const last5From = Number(data.meta.snapshot.slice(0, 4)) - 4;

  for (const row of rows) {
    const [type, releaseYear, addedYear, addedMonth, durationMin, seasons, rating, , rowGenres, rowCountries, hasDirector, rowDirectors] = row;

    if (type === 0) {
      movies += 1;
      relMovies[releaseYear - RELEASE_MIN] += 1;
    } else {
      series += 1;
      relSeries[releaseYear - RELEASE_MIN] += 1;
    }

    if (addedYear !== null) {
      if (type === 0) addMovies[addedYear - ADDED_MIN] += 1;
      else addSeries[addedYear - ADDED_MIN] += 1;
      if (addedMonth !== null) {
        yearMonth[(addedYear - ADDED_MIN) * 12 + (addedMonth - 1)] += 1;
      }
      if (addedYear >= last5From) last5 += 1;
    }

    const decadeIdx = Math.floor((releaseYear - 1920) / 10);
    if (decadeIdx >= 0 && decadeIdx < DECADES.length) {
      if (type === 0) decadeMovies[decadeIdx] += 1;
      else decadeSeries[decadeIdx] += 1;
      for (const gi of rowGenres) {
        const topTen = gi < 10 ? gi : 10;
        decadeGenre[decadeIdx * 11 + topTen] += 1;
      }
    }

    for (const gi of rowGenres) genreCounts[gi] += 1;

    if (rowCountries.length === 0) noCountry += 1;

    let regionMask = 0;
    for (const ci of rowCountries) {
      countryCounts[ci] += 1;
      regionMask |= 1 << regionOfCountry[ci];
      if (type === 0 && durationMin !== null) {
        countryDurSum[ci] += durationMin;
        countryDurN[ci] += 1;
      }
      const base = ci * G;
      for (const gi of rowGenres) countryGenre[base + gi] += 1;
    }
    for (let ri = 0; ri < regions.length; ri += 1) {
      if (regionMask & (1 << ri)) regionCounts[ri] += 1;
    }

    if (rating >= 0) {
      ratingCounts[rating] += 1;
    } else {
      const unknown = ratings.indexOf("Sin dato");
      if (unknown >= 0) ratingCounts[unknown] += 1;
    }

    if (hasDirector === 1) {
      for (const di of rowDirectors) directorCounts[di] += 1;
    } else {
      noDirector += 1;
    }

    if (type === 0 && durationMin !== null) {
      durations.push(durationMin);
      for (let bi = 0; bi < durationBins.length; bi += 1) {
        const bin = data.aggregates.duration_hist[bi];
        if (durationMin >= bin.from && durationMin <= bin.to) {
          durationBins[bi] += 1;
          break;
        }
      }
    }

    if (type === 1 && seasons !== null) {
      seasonValues.push(seasons);
      if (seasons < seasonsCounts.length) seasonsCounts[seasons] += 1;
    }
  }

  // Países
  const byCountry: CountryStat[] = countries.map((c, i) => {
    let topGenreIdx = -1;
    let topGenreCount = 0;
    const base = i * G;
    for (let gi = 0; gi < G; gi += 1) {
      if (countryGenre[base + gi] > topGenreCount) {
        topGenreCount = countryGenre[base + gi];
        topGenreIdx = gi;
      }
    }
    return {
      index: i,
      name: c.name,
      label: c.label,
      iso3: c.iso3,
      isoN: c.isoN,
      region: c.region,
      count: countryCounts[i],
      share: count ? (100 * countryCounts[i]) / count : 0,
      topGenre: topGenreIdx >= 0 ? genres[topGenreIdx].name : "—",
      topGenreLabel: topGenreIdx >= 0 ? genres[topGenreIdx].label : "Sin dato",
      avgDuration: countryDurN[i] ? countryDurSum[i] / countryDurN[i] : null,
    };
  });
  const topCountries = byCountry.filter((c) => c.count > 0).sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));

  // Géneros
  const byGenre: GenreStat[] = genres.map((g, i) => ({
    index: i,
    name: g.name,
    label: g.label,
    count: genreCounts[i],
    share: count ? (100 * genreCounts[i]) / count : 0,
  }));
  const topGenres = [...byGenre].sort((a, b) => b.count - a.count || a.label.localeCompare(b.label));

  // Directores
  const directorTitles = rows.length - noDirector;
  const directorRanking: DirectorStat[] = [];
  for (let di = 0; di < D; di += 1) {
    if (directorCounts[di] > 0) {
      directorRanking.push({
        index: di,
        name: data.dimensions.directors[di],
        count: directorCounts[di],
        share: directorTitles ? (100 * directorCounts[di]) / directorTitles : 0,
        topGenre: "—",
      });
    }
  }
  directorRanking.sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
  const topDirectors = directorRanking.slice(0, 12);
  if (topDirectors.length) {
    const counts = new Map<number, Int32Array>();
    for (const d of topDirectors) counts.set(d.index, new Int32Array(G));
    for (const row of rows) {
      for (const di of row[11]) {
        const arr = counts.get(di);
        if (arr) for (const gi of row[8]) arr[gi] += 1;
      }
    }
    for (const d of topDirectors) {
      const arr = counts.get(d.index);
      if (!arr) continue;
      let best = -1;
      let bestCount = 0;
      for (let gi = 0; gi < G; gi += 1) {
        if (arr[gi] > bestCount) {
          bestCount = arr[gi];
          best = gi;
        }
      }
      if (best >= 0) d.topGenre = genres[best].label;
    }
  }

  // Ratings
  const byRating: RatingStat[] = ratings.map((name, i) => ({
    name,
    count: ratingCounts[i],
    share: count ? (100 * ratingCounts[i]) / count : 0,
  }));
  const rated = byRating.filter((r) => r.name !== "Sin dato" && r.count > 0);
  const topRating = rated.length ? rated.reduce((a, b) => (b.count > a.count ? b : a)) : null;

  // Series temporales
  const byYearRelease: YearStat[] = [];
  for (let y = RELEASE_MIN; y <= RELEASE_MAX; y += 1) {
    const i = y - RELEASE_MIN;
    byYearRelease.push({
      year: y,
      movies: relMovies[i],
      series: relSeries[i],
      total: relMovies[i] + relSeries[i],
    });
  }
  const byYearAdded: YearStat[] = [];
  for (let y = ADDED_MIN; y <= ADDED_MAX; y += 1) {
    const i = y - ADDED_MIN;
    byYearAdded.push({
      year: y,
      movies: addMovies[i],
      series: addSeries[i],
      total: addMovies[i] + addSeries[i],
    });
  }

  const peakOf = (seriesData: YearStat[]) =>
    seriesData.reduce<YearStat | null>((best, item) => {
      if (item.total === 0) return best;
      if (!best || item.total > best.total) return item;
      return best;
    }, null);

  const peakReleaseRow = peakOf(byYearRelease);
  const peakAddedRow = peakOf(byYearAdded);

  // Décadas
  const byDecade: DecadeStat[] = DECADES.map((decade, i) => {
    const total = decadeMovies[i] + decadeSeries[i];
    return {
      decade,
      total,
      movies: decadeMovies[i],
      series: decadeSeries[i],
      variation: null,
      partial: decade === 2020,
    };
  });
  byDecade.forEach((d, i) => {
    if (i > 0 && byDecade[i - 1].total > 0) {
      d.variation = (100 * (d.total - byDecade[i - 1].total)) / byDecade[i - 1].total;
    }
  });

  const top10 = topGenres.slice(0, 10);
  const decadeGenreOut: Array<{ decade: number; genre: string; label: string; count: number }> = [];
  DECADES.forEach((decade, di) => {
    top10.forEach((g, gi) => {
      decadeGenreOut.push({
        decade,
        genre: g.name,
        label: g.label,
        count: decadeGenre[di * 11 + gi],
      });
    });
    decadeGenreOut.push({
      decade,
      genre: "__OTROS__",
      label: "Otros géneros",
      count: decadeGenre[di * 11 + 10],
    });
  });

  const yearMonthOut: Array<{ year: number; month: number; count: number }> = [];
  for (let y = ADDED_MIN; y <= ADDED_MAX; y += 1) {
    for (let m = 1; m <= 12; m += 1) {
      yearMonthOut.push({ year: y, month: m, count: yearMonth[(y - ADDED_MIN) * 12 + (m - 1)] });
    }
  }

  const seasonsDist = data.aggregates.seasons_dist.map((s) => ({
    seasons: s.seasons,
    count: seasonsCounts[s.seasons] ?? 0,
  }));

  return {
    count,
    movies,
    series,
    seriesShare: count ? (100 * series) / count : 0,
    countryCount: topCountries.length,
    noCountry,
    noDirector,
    noDirectorShare: count ? (100 * noDirector) / count : 0,
    directorTitles,
    topCountries: topCountries.slice(0, 12),
    byCountry,
    topGenres: topGenres.slice(0, 12),
    byGenre,
    topDirectors,
    peakRelease: peakReleaseRow ? { year: peakReleaseRow.year, count: peakReleaseRow.total } : null,
    peakAdded: peakAddedRow ? { year: peakAddedRow.year, count: peakAddedRow.total } : null,
    movieDuration: {
      n: durations.length,
      avg: durations.length ? durations.reduce((a, b) => a + b, 0) / durations.length : 0,
      median: median(durations),
    },
    seasons: { n: seasonValues.length, median: median(seasonValues) },
    topRating,
    byRating,
    last5: {
      from: last5From,
      to: Number(data.meta.snapshot.slice(0, 4)),
      count: last5,
      share: count ? (100 * last5) / count : 0,
    },
    byYearRelease,
    byYearAdded,
    byDecade,
    durationHist: data.aggregates.duration_hist.map((b, i) => ({ ...b, count: durationBins[i] })),
    seasonsDist,
    decadeGenre: decadeGenreOut,
    yearMonth: yearMonthOut,
    typeCounts: [
      { type: "Película", count: movies, share: count ? (100 * movies) / count : 0 },
      { type: "Serie", count: series, share: count ? (100 * series) / count : 0 },
    ],
    regionCounts: regions.map((region, i) => ({
      region,
      count: regionCounts[i],
      share: count ? (100 * regionCounts[i]) / count : 0,
    })),
  };
}

export function filtersLabel(filters: Filters, data: DashboardData): string {
  const type =
    filters.type === "todo" ? "Todo el contenido" : filters.type === "pelicula" ? "Solo películas" : "Solo series";
  let period = "Todos los años";
  if (filters.period.kind === "decade") period = `Década de ${filters.period.decade}`;
  if (filters.period.kind === "range") period = `${filters.period.from}–${filters.period.to}`;
  let place = "Todos los países";
  if (filters.place.kind === "region") place = filters.place.region;
  if (filters.place.kind === "country") place = data.dimensions.countries[filters.place.index].label;
  if (filters.place.kind === "unknown") place = "Sin país declarado";
  return `${type} · ${period} · ${place}`;
}

export function hasActiveFilters(filters: Filters): boolean {
  return filters.type !== "todo" || filters.period.kind !== "all" || filters.place.kind !== "all";
}
