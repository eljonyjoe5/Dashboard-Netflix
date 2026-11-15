"""
ETL reproducible del Proyecto 3 — "La economía del entretenimiento: Netflix y tendencias globales".

Flujo:
    CSV crudo (Kaggle shivamb/netflix-shows)
      -> staging normalizado en DuckDB
      -> tablas: titles + puentes (géneros, países, directores, reparto)
      -> Parquet por tabla
      -> data/netflix_catalog.duckdb
      -> data/quality_report.json
      -> public/data/dashboard.json

Uso:
    python etl/build_dataset.py
    python etl/build_dataset.py --csv ruta/al/netflix_titles.csv

No inventa datos: todas las cifras se calculan desde el CSV.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PARQUET = DATA / "parquet"
PUBLIC_DATA = ROOT / "public" / "data"
ETL = ROOT / "etl"

TYPE_MAP_SQL = """
CASE trim(type)
  WHEN 'Movie' THEN 'Película'
  WHEN 'TV Show' THEN 'Serie'
  ELSE trim(type)
END
"""

RATING_GROUP_SQL = """
CASE
  WHEN rating IS NULL THEN 'Sin dato'
  WHEN rating IN ('TV-Y', 'TV-Y7', 'TV-Y7-FV', 'G') THEN 'Infantil'
  WHEN rating IN ('TV-G', 'PG', 'TV-PG') THEN 'Familiar'
  WHEN rating IN ('PG-13', 'TV-14') THEN 'Adolescente'
  WHEN rating IN ('R', 'NC-17', 'TV-MA') THEN 'Adulto'
  ELSE 'Sin clasificar'
END
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rows(con: duckdb.DuckDBPyConnection, sql: str, params: list | None = None) -> list[tuple]:
    return con.execute(sql, params or []).fetchall()


def dicts(con: duckdb.DuckDBPyConnection, sql: str, params: list | None = None) -> list[dict]:
    cur = con.execute(sql, params or [])
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def pct(part: float, total: float) -> float:
    return round(100.0 * part / total, 2) if total else 0.0


def fmt_int(n: int) -> str:
    """Formato es-MX: 8807 -> 8,807 (coma de miles, punto decimal)."""
    return f"{n:,}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(ROOT / "netflix_titles.csv"))
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise SystemExit(f"No se encontró el CSV: {csv_path}")

    for d in (DATA, PARQUET, PUBLIC_DATA):
        d.mkdir(parents=True, exist_ok=True)

    country_meta = load_json(ETL / "country_meta.json")
    genre_labels = load_json(ETL / "genre_labels.json")["labels"]

    db_path = DATA / "netflix_catalog.duckdb"
    if db_path.exists():
        db_path.unlink()

    con = duckdb.connect(str(db_path))
    con.execute("PRAGMA threads=4")

    # ---------------------------------------------------------------- staging
    con.execute(
        f"""
        CREATE VIEW raw AS
        SELECT * FROM read_csv('{csv_path.as_posix()}',
                               header=true, all_varchar=true, nullstr='',
                               quote='"', escape='"', strict_mode=false)
        """
    )

    con.execute(
        f"""
        CREATE TABLE stg_titles AS
        SELECT
            trim(show_id)                                        AS show_id,
            trim(type)                                           AS type_source,
            {TYPE_MAP_SQL}                                       AS type,
            trim(title)                                          AS title,
            nullif(trim(director), '')                           AS director_raw,
            nullif(trim("cast"), '')                             AS cast_raw,
            nullif(trim(country), '')                            AS country_raw,
            try_strptime(trim(date_added), '%B %d, %Y')::DATE    AS added_date,
            try_cast(trim(release_year) AS INTEGER)              AS release_year,
            nullif(trim(description), '')                        AS description,
            trim(listed_in)                                      AS listed_in_raw,
            trim(duration)                                       AS duration_raw,
            CASE
                WHEN regexp_matches(trim(rating), '^[0-9]+ min$') THEN NULL
                ELSE nullif(trim(rating), '')
            END                                                  AS rating,
            CASE
                WHEN regexp_matches(trim(rating), '^[0-9]+ min$')
                    THEN CAST(regexp_extract(trim(rating), '([0-9]+)', 1) AS INTEGER)
                WHEN regexp_matches(trim(duration), '^[0-9]+ min$')
                    THEN CAST(regexp_extract(trim(duration), '([0-9]+)', 1) AS INTEGER)
            END                                                  AS duration_min,
            CASE
                WHEN regexp_matches(trim(duration), '^[0-9]+ Seasons?$')
                    THEN CAST(regexp_extract(trim(duration), '([0-9]+)', 1) AS INTEGER)
            END                                                  AS seasons,
            regexp_matches(trim(rating), '^[0-9]+ min$')         AS rating_was_duration,
            CAST(floor(try_cast(trim(release_year) AS INTEGER) / 10.0) * 10 AS INTEGER) AS decade,
            EXTRACT(YEAR  FROM try_strptime(trim(date_added), '%B %d, %Y'))::INTEGER   AS added_year,
            EXTRACT(MONTH FROM try_strptime(trim(date_added), '%B %d, %Y'))::INTEGER   AS added_month,
            EXTRACT(QUARTER FROM try_strptime(trim(date_added), '%B %d, %Y'))::INTEGER AS added_quarter
        FROM raw
        """
    )

    # ------------------------------------------------------------ dimensiones
    con.execute("CREATE TABLE country_meta (name VARCHAR, name_es VARCHAR, iso3 VARCHAR, iso_n INTEGER, region VARCHAR)")
    con.executemany(
        "INSERT INTO country_meta VALUES (?, ?, ?, ?, ?)",
        [(c["name"], c["name_es"], c["iso3"], c["iso_n"], c["region"]) for c in country_meta["countries"]],
    )
    con.execute("CREATE TABLE country_alias (source VARCHAR, target VARCHAR)")
    con.executemany(
        "INSERT INTO country_alias VALUES (?, ?)",
        list(country_meta["aliases"].items()),
    )
    con.execute("CREATE TABLE genre_labels (genre VARCHAR, genre_es VARCHAR)")
    con.executemany(
        "INSERT INTO genre_labels VALUES (?, ?)",
        list(genre_labels.items()),
    )

    # --------------------------------------------------------------- puentes
    con.execute(
        """
        CREATE TABLE title_genres AS
        SELECT show_id, trim(v) AS genre, CAST(ord AS INTEGER) AS position
        FROM stg_titles, unnest(string_split(listed_in_raw, ',')) WITH ORDINALITY AS u(v, ord)
        WHERE trim(v) <> ''
        """
    )
    con.execute(
        """
        ALTER TABLE title_genres ADD COLUMN genre_es VARCHAR;
        UPDATE title_genres SET genre_es = coalesce(g.genre_es, title_genres.genre)
        FROM genre_labels g WHERE g.genre = title_genres.genre;
        """
    )

    con.execute(
        """
        CREATE TABLE title_countries AS
        WITH exploded AS (
            SELECT show_id, trim(v) AS country_raw, CAST(ord AS INTEGER) AS position
            FROM stg_titles, unnest(string_split(country_raw, ',')) WITH ORDINALITY AS u(v, ord)
            WHERE trim(v) <> ''
        ),
        mapped AS (
            SELECT e.show_id, coalesce(a.target, e.country_raw) AS country, e.position
            FROM exploded e LEFT JOIN country_alias a ON a.source = e.country_raw
        )
        SELECT m.show_id, m.country, coalesce(cm.name_es, m.country) AS country_es,
               cm.iso3, cm.iso_n, cm.region, m.position,
               (row_number() OVER (PARTITION BY m.show_id ORDER BY m.position) = 1) AS is_primary
        FROM mapped m LEFT JOIN country_meta cm ON cm.name = m.country
        """
    )
    unknown = rows(con, "SELECT DISTINCT country FROM title_countries WHERE iso3 IS NULL")
    if unknown:
        raise SystemExit(f"Países sin metadatos ISO/región: {unknown}")

    con.execute(
        """
        CREATE TABLE title_directors AS
        SELECT show_id, trim(v) AS director, CAST(ord AS INTEGER) AS position
        FROM stg_titles, unnest(string_split(director_raw, ',')) WITH ORDINALITY AS u(v, ord)
        WHERE trim(v) <> ''
        """
    )
    con.execute(
        """
        CREATE TABLE title_cast AS
        SELECT show_id, trim(v) AS actor, CAST(ord AS INTEGER) AS position
        FROM stg_titles, unnest(string_split(cast_raw, ',')) WITH ORDINALITY AS u(v, ord)
        WHERE trim(v) <> ''
        """
    )

    # ---------------------------------------------------------------- titles
    con.execute(
        f"""
        CREATE TABLE titles AS
        SELECT
            t.show_id, t.type, t.type_source, t.title,
            t.director_raw, t.cast_raw, t.country_raw, t.listed_in_raw,
            t.added_date, t.added_year, t.added_month, t.added_quarter,
            t.release_year, t.decade, t.rating,
            {RATING_GROUP_SQL} AS rating_group,
            t.duration_raw, t.duration_min, t.seasons, t.description,
            pc.country AS primary_country,
            coalesce(cc.n_countries, 0) AS n_countries,
            coalesce(gg.n_genres, 0)    AS n_genres,
            (t.director_raw IS NOT NULL) AS has_director,
            (t.added_year IS NOT NULL AND t.added_year < t.release_year) AS date_anomaly,
            t.rating_was_duration
        FROM stg_titles t
        LEFT JOIN (
            SELECT show_id, country FROM title_countries WHERE is_primary
        ) pc ON pc.show_id = t.show_id
        LEFT JOIN (SELECT show_id, count(*) n_countries FROM title_countries GROUP BY 1) cc ON cc.show_id = t.show_id
        LEFT JOIN (SELECT show_id, count(*) n_genres    FROM title_genres    GROUP BY 1) gg ON gg.show_id = t.show_id
        """
    )

    # ------------------------------------------------------------- parquet
    for table in ("titles", "title_genres", "title_countries", "title_directors", "title_cast"):
        con.execute(
            f"COPY {table} TO '{(PARQUET / (table + '.parquet')).as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )

    # ------------------------------------------------------- cifras base
    total = rows(con, "SELECT count(*) FROM titles")[0][0]
    by_type = {r[0]: r[1] for r in rows(con, "SELECT type, count(*) FROM titles GROUP BY 1")}
    movies = by_type.get("Película", 0)
    series = by_type.get("Serie", 0)

    n_countries = rows(con, "SELECT count(DISTINCT country) FROM title_countries")[0][0]
    n_genres = rows(con, "SELECT count(DISTINCT genre) FROM title_genres")[0][0]
    n_directors = rows(con, "SELECT count(DISTINCT director) FROM title_directors")[0][0]

    top_countries = dicts(
        con,
        """
        SELECT c.country AS name, c.country_es AS label, c.iso3, c.iso_n AS isoN, c.region,
               count(*) AS count
        FROM title_countries c
        GROUP BY 1,2,3,4,5
        ORDER BY count DESC, name
        """,
    )
    for row in top_countries:
        row["share"] = pct(row["count"], total)

    country_details = dicts(
        con,
        """
        WITH base AS (
            SELECT c.country, count(*) AS titles,
                   avg(CASE WHEN t.type = 'Película' THEN t.duration_min END) AS avg_duration
            FROM title_countries c JOIN titles t USING (show_id)
            GROUP BY 1
        ),
        genre_counts AS (
            SELECT c.country, g.genre, g.genre_es, count(*) AS n,
                   row_number() OVER (PARTITION BY c.country ORDER BY count(*) DESC, g.genre) AS rn
            FROM title_countries c
            JOIN title_genres g USING (show_id)
            GROUP BY 1,2,3
        )
        SELECT b.country AS name, cm.name_es AS label, cm.iso3, cm.iso_n AS isoN, cm.region,
               b.titles, round(b.avg_duration, 1) AS avg_duration_min,
               gc.genre AS top_genre, gc.genre_es AS top_genre_es
        FROM base b
        JOIN country_meta cm ON cm.name = b.country
        LEFT JOIN genre_counts gc ON gc.country = b.country AND gc.rn = 1
        ORDER BY b.titles DESC, b.country
        """,
    )
    for row in country_details:
        row["share"] = pct(row["titles"], total)

    by_genre = dicts(
        con,
        """
        SELECT g.genre AS name, g.genre_es AS label, count(*) AS count
        FROM title_genres g GROUP BY 1,2 ORDER BY count DESC, name
        """,
    )
    for row in by_genre:
        row["share"] = pct(row["count"], total)

    top_directors = dicts(
        con,
        """
        SELECT d.director AS name, count(*) AS count
        FROM title_directors d GROUP BY 1 ORDER BY count DESC, name LIMIT 50
        """,
    )
    director_count = rows(con, "SELECT count(*) FROM titles WHERE has_director")[0][0]
    for row in top_directors:
        row["share"] = pct(row["count"], director_count)

    by_rating = dicts(
        con,
        """
        SELECT coalesce(rating, 'Sin dato') AS name, count(*) AS count
        FROM titles GROUP BY 1 ORDER BY count DESC, name
        """,
    )
    for row in by_rating:
        row["share"] = pct(row["count"], total)

    decade_counts = {
        r[0]: (r[1], r[2], r[3])
        for r in rows(
            con,
            """
            SELECT decade, count(*) AS total,
                   count(*) FILTER (WHERE type = 'Película') AS movies,
                   count(*) FILTER (WHERE type = 'Serie')    AS series
            FROM titles GROUP BY 1
            """,
        )
    }
    by_decade = []
    prev = None
    for dec in range(1920, 2030, 10):
        d_total, d_movies, d_series = decade_counts.get(dec, (0, 0, 0))
        by_decade.append(
            {
                "decade": dec,
                "total": d_total,
                "movies": d_movies,
                "series": d_series,
                "variation_pct": None if prev in (None, 0) else round(100.0 * (d_total - prev) / prev, 2),
                "is_partial": dec == 2020,
            }
        )
        prev = d_total

    # Serie temporal: estreno (todos los años del rango, sin interpolar: 0 si no hay títulos)
    years = rows(con, "SELECT min(release_year), max(release_year) FROM titles")[0]
    year_counts = {
        r[0]: (r[1], r[2])
        for r in rows(
            con,
            """
            SELECT release_year,
                   count(*) FILTER (WHERE type = 'Película'),
                   count(*) FILTER (WHERE type = 'Serie')
            FROM titles GROUP BY 1
            """,
        )
    }
    by_year_release = [
        {"year": y, "movies": year_counts.get(y, (0, 0))[0], "series": year_counts.get(y, (0, 0))[1],
         "total": sum(year_counts.get(y, (0, 0)))}
        for y in range(years[0], years[1] + 1)
    ]

    added_counts = {
        r[0]: (r[1], r[2])
        for r in rows(
            con,
            """
            SELECT added_year,
                   count(*) FILTER (WHERE type = 'Película'),
                   count(*) FILTER (WHERE type = 'Serie')
            FROM titles WHERE added_year IS NOT NULL GROUP BY 1
            """,
        )
    }
    added_years = sorted(added_counts)
    by_year_added = [
        {"year": y, "movies": added_counts[y][0], "series": added_counts[y][1], "total": sum(added_counts[y])}
        for y in added_years
    ]

    snapshot = dicts(
        con,
        """
        SELECT min(added_date) AS min_date, max(added_date) AS max_date,
               count(*) FILTER (WHERE added_date IS NULL) AS nulls,
               count(DISTINCT added_date) AS distinct_dates
        FROM titles
        """,
    )[0]
    snapshot_max = snapshot["max_date"]

    # Año pico de estreno / incorporación
    peak_release = max(by_year_release, key=lambda r: r["total"])
    peak_added = max(by_year_added, key=lambda r: r["total"])

    # Duración de películas y temporadas
    dur_stats = dicts(
        con,
        """
        SELECT count(duration_min) AS n,
               round(avg(duration_min), 1) AS avg,
               median(duration_min) AS median,
               min(duration_min) AS min,
               max(duration_min) AS max
        FROM titles WHERE type = 'Película'
        """,
    )[0]
    season_stats = dicts(
        con,
        """
        SELECT count(seasons) AS n, median(seasons) AS median, max(seasons) AS max
        FROM titles WHERE type = 'Serie'
        """,
    )[0]

    # Histograma de duración (películas)
    duration_bins = [
        (0, 30, "≤ 30 min"),
        (31, 60, "31–60 min"),
        (61, 90, "61–90 min"),
        (91, 120, "91–120 min"),
        (121, 150, "121–150 min"),
        (151, 180, "151–180 min"),
        (181, 10_000, "> 180 min"),
    ]
    duration_hist = []
    for lo, hi, label in duration_bins:
        n = rows(
            con,
            "SELECT count(*) FROM titles WHERE type = 'Película' AND duration_min BETWEEN ? AND ?",
            [lo, hi],
        )[0][0]
        duration_hist.append({"bin": label, "from": lo, "to": hi, "count": n})

    seasons_dist = [
        {"seasons": r[0], "count": r[1]}
        for r in rows(
            con,
            """
            SELECT seasons, count(*) FROM titles WHERE type = 'Serie' AND seasons IS NOT NULL
            GROUP BY 1 ORDER BY 1
            """,
        )
    ]

    # Rating más frecuente (excluye "Sin dato" para el KPI)
    top_rating = next((r for r in by_rating if r["name"] != "Sin dato"), by_rating[0])

    # Últimos 5 años del snapshot
    last5_from = int(str(snapshot_max)[:4]) - 4
    last5 = rows(
        con,
        "SELECT count(*) FROM titles WHERE added_year >= ?",
        [last5_from],
    )[0][0]
    last5_pct = pct(last5, total)

    nulls = {r[0]: r[1] for r in rows(con, "SELECT 'director', count(*) FROM titles WHERE director_raw IS NULL")}
    nulls["cast"] = rows(con, "SELECT count(*) FROM titles WHERE cast_raw IS NULL")[0][0]
    nulls["country"] = rows(con, "SELECT count(*) FROM titles WHERE country_raw IS NULL")[0][0]
    nulls["date_added"] = rows(con, "SELECT count(*) FROM titles WHERE added_date IS NULL")[0][0]
    nulls["rating"] = rows(con, "SELECT count(*) FROM titles WHERE rating IS NULL")[0][0]
    nulls["duration"] = rows(con, "SELECT count(*) FROM titles WHERE duration_min IS NULL AND seasons IS NULL")[0][0]

    no_country = rows(con, "SELECT count(*) FROM titles WHERE primary_country IS NULL")[0][0]
    no_director = nulls["director"]
    no_director_pct = pct(no_director, total)

    # Matriz década × género (top 10 géneros + resto agrupado)
    top10_genres = [g["name"] for g in by_genre[:10]]
    placeholders = ",".join(["?"] * len(top10_genres))
    decade_genre = dicts(
        con,
        f"""
        SELECT t.decade,
               CASE WHEN g.genre IN ({placeholders}) THEN g.genre ELSE '__OTROS__' END AS genre,
               count(*) AS count
        FROM titles t JOIN title_genres g USING (show_id)
        GROUP BY 1,2 ORDER BY 1,2
        """,
        top10_genres,
    )

    # Año × mes de incorporación
    year_month = dicts(
        con,
        """
        SELECT added_year AS year, added_month AS month, count(*) AS count
        FROM titles WHERE added_year IS NOT NULL
        GROUP BY 1,2 ORDER BY 1,2
        """,
    )

    by_region = dicts(
        con,
        """
        SELECT c.region, count(DISTINCT c.show_id) AS titles
        FROM title_countries c GROUP BY 1 ORDER BY titles DESC
        """,
    )
    for row in by_region:
        row["share"] = pct(row["titles"], total)

    # --------------------------------------------------- informe de calidad
    field_specs = [
        ("show_id", "show_id", "identificador"),
        ("type", "type", "tipo"),
        ("title", "title", "texto"),
        ("director", "director_raw", "multivaluado"),
        ("cast", "cast_raw", "multivaluado"),
        ("country", "country_raw", "multivaluado"),
        ("date_added", "added_date", "fecha"),
        ("release_year", "release_year", "entero"),
        ("rating", "rating", "categórico"),
        ("duration", "duration_raw", "texto"),
        ("listed_in", "listed_in_raw", "multivaluado"),
        ("description", "description", "texto"),
    ]
    field_notes = {
        "title": "El título 'Consequences' aparece dos veces con show_id distinto; no es un duplicado.",
        "director": "Valores distintos sobre el texto original; al separar por comas resultan 4,993 nombres.",
        "country": "Valores distintos sobre el texto original; tras separar, limpiar y agrupar países históricos quedan 119 países.",
        "duration": "3 nulos en el texto original; sus minutos se recuperaron desde el campo rating. Tras la corrección, 0 títulos quedan sin duración.",
        "rating": "7 títulos sin rating tras corregir 3 filas desalineadas (la duración estaba en rating).",
    }
    fields = []
    for source, col, kind in field_specs:
        n_null = rows(con, f'SELECT count(*) FROM titles WHERE "{col}" IS NULL')[0][0]
        n_distinct = rows(con, f'SELECT count(DISTINCT "{col}") FROM titles WHERE "{col}" IS NOT NULL')[0][0]
        fields.append(
            {
                "campo": source,
                "tipo": kind,
                "nulos": n_null,
                "porcentaje_nulos": pct(n_null, total),
                "valores_distintos": n_distinct,
                "nota": field_notes.get(source),
            }
        )

    rating_anomalies = dicts(
        con,
        """
        SELECT show_id, title, rating_was_duration, duration_min
        FROM titles WHERE rating_was_duration ORDER BY show_id
        """,
    )
    date_anomalies = dicts(
        con,
        """
        SELECT show_id, title, release_year, strftime(added_date, '%Y-%m-%d') AS added_date
        FROM titles WHERE date_anomaly ORDER BY show_id
        """,
    )
    missing_years = sorted(set(range(years[0], years[1] + 1)) - set(year_counts))
    hist_countries = dicts(
        con,
        """
        SELECT trim(e) AS country_raw, count(*) AS titles FROM (
            SELECT unnest(string_split(country_raw, ',')) AS e
            FROM titles WHERE country_raw IS NOT NULL
        )
        WHERE trim(e) IN ('West Germany', 'East Germany', 'Soviet Union')
        GROUP BY 1 ORDER BY 1
        """,
    )
    extra_spaces = rows(
        con,
        """
        SELECT count(*) FROM (
            SELECT unnest(string_split(country_raw, ',')) AS e FROM titles WHERE country_raw IS NOT NULL
        ) WHERE e <> trim(e)
        """,
    )[0][0]

    quality = {
        "generado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "archivo": {
            "nombre": csv_path.name,
            "bytes": csv_path.stat().st_size,
            "sha256": sha256(csv_path),
        },
        "snapshot": {
            "corte": str(snapshot_max),
            "min_date_added": str(snapshot["min_date"]),
            "max_date_added": str(snapshot_max),
            "fechas_distintas": snapshot["distinct_dates"],
            "nota": (
                "El snapshot de Kaggle termina el 25 de septiembre de 2021. "
                "2021 está incompleto y no debe compararse como año cerrado."
            ),
        },
        "totales": {
            "filas": total,
            "titulos_unicos": rows(con, "SELECT count(DISTINCT show_id) FROM titles")[0][0],
            "columnas": 12,
            "peliculas": movies,
            "series": series,
            "porcentaje_series": pct(series, total),
            "muestreo": "100% del catálogo; no se aplicó muestreo",
        },
        "duplicados": {
            "show_id": rows(con, "SELECT count(*) FROM (SELECT show_id FROM titles GROUP BY 1 HAVING count(*) > 1)")[0][0],
            "filas_completas": rows(
                con,
                "SELECT count(*) FROM (SELECT * FROM raw GROUP BY ALL HAVING count(*) > 1)",
            )[0][0],
        },
        "campos": fields,
        "cobertura": {
            "release_year_min": years[0],
            "release_year_max": years[1],
            "anios_con_titulos": len(year_counts),
            "anios_sin_titulos": missing_years,
            "nota": "Los años sin títulos se muestran en 0; no se interpola ni se extrapola.",
            "paises_distintos": n_countries,
            "generos_distintos": n_genres,
            "directores_distintos": n_directors,
            "titulos_sin_pais": no_country,
            "titulos_sin_director": no_director,
            "porcentaje_sin_director": no_director_pct,
        },
        "anomalias": {
            "rating_con_duracion": rating_anomalies,
            "date_added_antes_de_release_year": date_anomalies,
            "rating_nulos": [
                {"show_id": r[0], "title": r[1]}
                for r in rows(
                    con,
                    "SELECT show_id, title FROM titles WHERE rating IS NULL ORDER BY show_id",
                )
            ],
            "date_added_nulos": [
                {"show_id": r[0], "title": r[1]}
                for r in rows(
                    con,
                    "SELECT show_id, title FROM titles WHERE added_date IS NULL ORDER BY show_id",
                )
            ],
            "paises_historicos_normalizados": hist_countries,
            "elementos_multivaluados_con_espacios": extra_spaces,
            "nota": (
                "Los 3 registros con la duración en el campo rating se corrigieron moviendo el valor "
                "a duration_min; su rating queda como desconocido. Los 14 casos con incorporación "
                "anterior al estreno se conservan y se marcan (casi todos son series cuya "
                "release_year corresponde a la última temporada)."
            ),
        },
        "multivaluados": {
            "generos_por_titulo": {"min": 1, "max": 3, "tabla": "title_genres"},
            "paises_por_titulo": {
                "min": 1,
                "max": rows(con, "SELECT max(n_countries) FROM titles")[0][0],
                "tabla": "title_countries",
                "nota": "Un título puede sumar en varios países; los totales por país no suman el total del catálogo.",
            },
            "directores_por_titulo": {
                "max": rows(con, "SELECT max(cnt) FROM (SELECT show_id, count(*) cnt FROM title_directors GROUP BY 1)")[0][0],
            },
            "regla_porcentajes": (
                "Los porcentajes de género y país usan como denominador el total de títulos (8,807); "
                "por eso pueden sumar más de 100%."
            ),
        },
        "normalizaciones": [
            {"regla": "type", "detalle": "Movie -> Película; TV Show -> Serie"},
            {"regla": "date_added", "detalle": "Formato Month D, YYYY parseado a fecha; se derivan año, mes y trimestre."},
            {"regla": "duration", "detalle": "Películas: minutos; series: temporadas. Nunca se promedian juntos."},
            {"regla": "country", "detalle": "Separación por comas, trim y primary_country = primer país."},
            {"regla": "paises_historicos", "detalle": "West Germany y East Germany -> Germany; Soviet Union -> Russia."},
            {"regla": "rating", "detalle": "Se conservan valores fuente; rating_group es una agrupación derivada para lectura."},
            {"regla": "generos", "detalle": "Se conserva el nombre original y se agrega etiqueta en español para la interfaz."},
            {"regla": "sin_pais", "detalle": "Los títulos sin país se excluyen de rankings y mapa, pero permanecen en los totales."},
            {"regla": "sin_director", "detalle": "Los nulos de director no se imputan; se excluyen del ranking de directores."},
        ],
    }

    (DATA / "quality_report.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # -------------------------------------------------------------- KPIs
    top5_countries = top_countries[:5]
    top5_genres = by_genre[:5]
    top5_directors = top_directors[:5]

    kpis = {
        "total_titulos": total,
        "peliculas": movies,
        "series": series,
        "porcentaje_series": pct(series, total),
        "paises_distintos": n_countries,
        "top5_paises": [{"name": c["label"], "count": c["count"], "share": c["share"]} for c in top5_countries],
        "anio_mas_estrenos": {"year": peak_release["year"], "count": peak_release["total"]},
        "anio_mas_incorporaciones": {"year": peak_added["year"], "count": peak_added["total"]},
        "top5_generos": [{"name": g["label"], "count": g["count"], "share": g["share"]} for g in top5_genres],
        "top5_directores": [
            {"name": d["name"], "count": d["count"], "share": d["share"]} for d in top5_directors
        ],
        "directores_distintos": n_directors,
        "titulos_sin_director": no_director,
        "porcentaje_sin_director": no_director_pct,
        "duracion_peliculas": {
            "n": dur_stats["n"],
            "promedio_min": dur_stats["avg"],
            "mediana_min": dur_stats["median"],
            "min": dur_stats["min"],
            "max": dur_stats["max"],
        },
        "temporadas_series": {"n": season_stats["n"], "mediana": season_stats["median"], "max": season_stats["max"]},
        "rating_mas_frecuente": {"name": top_rating["name"], "count": top_rating["count"], "share": top_rating["share"]},
        "ultimos_5_anios": {
            "desde": last5_from,
            "hasta": int(str(snapshot_max)[:4]),
            "titulos": last5,
            "porcentaje": last5_pct,
        },
        "variacion_por_decada": [
            {"decade": d["decade"], "total": d["total"], "variation_pct": d["variation_pct"]} for d in by_decade
        ],
        "sin_pais": {"titulos": no_country, "porcentaje": pct(no_country, total)},
        "definiciones": {
            "porcentaje_series": "series / total de títulos del catálogo",
            "ultimos_5_anios": f"títulos con added_year >= {last5_from} (2017–2021) / total",
            "duracion_peliculas": "solo películas con duration_min; se excluyen series",
            "temporadas_series": "solo series con seasons; no se mezcla con minutos",
            "top_paises": "conteo por tabla puente; un título puede sumar en varios países",
        },
    }

    findings = [
        {
            "id": "pais",
            "titulo": "Estados Unidos lidera, pero el catálogo es global",
            "texto": (
                f"{top_countries[0]['label']} concentra {fmt_int(top_countries[0]['count'])} títulos "
                f"({top_countries[0]['share']}% del catálogo), seguido por {top_countries[1]['label']} "
                f"({fmt_int(top_countries[1]['count'])}) y {top_countries[2]['label']} "
                f"({fmt_int(top_countries[2]['count'])}). Hay {n_countries} países representados, "
                f"aunque {fmt_int(no_country)} títulos no declaran país."
            ),
            "cifra": f"{top_countries[0]['share']}%",
            "detalle": "participación de Estados Unidos",
        },
        {
            "id": "crecimiento",
            "titulo": "El catálogo creció muy rápido en pocos años",
            "texto": (
                f"El {last5_pct}% del catálogo se incorporó entre {last5_from} y 2021. "
                f"El pico fue {peak_added['year']}, con {fmt_int(peak_added['total'])} incorporaciones; "
                f"2021 solo llega al 25 de septiembre y está incompleto."
            ),
            "cifra": f"{last5_pct}%",
            "detalle": "incorporado en los últimos 5 años",
        },
        {
            "id": "series",
            "titulo": "Las series ganan terreno",
            "texto": (
                f"Las series son el {pct(series, total)}% del catálogo "
                f"({fmt_int(series)} de {fmt_int(total)} títulos)."
            ),
            "cifra": f"{pct(series, total)}%",
            "detalle": "del catálogo son series",
        },
        {
            "id": "genero",
            "titulo": "Drama e internacional mandan",
            "texto": (
                f"El género más frecuente es {by_genre[0]['label']} "
                f"({fmt_int(by_genre[0]['count'])} títulos, {by_genre[0]['share']}%), "
                f"seguido por {by_genre[1]['label']} y {by_genre[2]['label']}. "
                f"Un título puede pertenecer a varios géneros."
            ),
            "cifra": fmt_int(by_genre[0]["count"]),
            "detalle": f"títulos en {by_genre[0]['label']}",
        },
        {
            "id": "duracion",
            "titulo": "Películas de hora y media, series de una temporada",
            "texto": (
                f"La mediana de duración de las películas es {dur_stats['median']} minutos "
                f"(promedio {dur_stats['avg']}); la mediana de las series es "
                f"{season_stats['median']} temporada(s). Son dos unidades distintas y no se promedian juntas."
            ),
            "cifra": f"{dur_stats['median']} min",
            "detalle": "mediana de películas",
        },
        {
            "id": "calidad",
            "titulo": "El dato que falta también informa",
            "texto": (
                f"{no_director_pct}% de los títulos no registra director y {pct(no_country, total)}% "
                f"no declara país. No se imputan: se excluyen de los rankings y se reportan "
                f"en la metodología."
            ),
            "cifra": f"{no_director_pct}%",
            "detalle": "sin director",
        },
    ]

    # Serie 2021 por tipo (para el hallazgo de series)
    s2021 = dicts(
        con,
        """
        SELECT type, count(*) AS n FROM titles WHERE added_year = 2021 GROUP BY 1
        """,
    )
    s2021_map = {r["type"]: r["n"] for r in s2021}
    if s2021_map:
        share2021 = pct(s2021_map.get("Serie", 0), sum(s2021_map.values()))
        findings[2]["texto"] = (
            f"Las series son el {pct(series, total)}% del catálogo ({fmt_int(series)} de {fmt_int(total)} títulos). "
            f"Entre las incorporaciones de 2021 (hasta el 25 de septiembre) representan el {share2021}%."
        )

    # --------------------------------------------------- tabla compacta
    genre_index = {g["name"]: i for i, g in enumerate(by_genre)}
    country_index = {c["name"]: i for i, c in enumerate(top_countries)}
    rating_list = [r["name"] for r in by_rating]
    rating_index = {r: i for i, r in enumerate(rating_list)}
    director_list = [d["name"] for d in dicts(
        con, "SELECT director AS name, count(*) AS count FROM title_directors GROUP BY 1 ORDER BY count DESC, name"
    )]
    director_index = {d: i for i, d in enumerate(director_list)}

    genres_by_title: dict[str, list[int]] = {}
    for sid, genre in rows(con, "SELECT show_id, genre FROM title_genres ORDER BY show_id, position"):
        genres_by_title.setdefault(sid, []).append(genre_index[genre])
    countries_by_title: dict[str, list[int]] = {}
    for sid, country in rows(con, "SELECT show_id, country FROM title_countries ORDER BY show_id, position"):
        countries_by_title.setdefault(sid, []).append(country_index[country])
    directors_by_title: dict[str, list[int]] = {}
    for sid, director in rows(con, "SELECT show_id, director FROM title_directors ORDER BY show_id, position"):
        directors_by_title.setdefault(sid, []).append(director_index[director])

    compact = rows(
        con,
        """
        SELECT show_id, type, release_year, added_year, added_month, duration_min, seasons,
               rating, primary_country, has_director
        FROM titles ORDER BY CAST(substr(show_id, 2) AS INTEGER)
        """,
    )
    compact_rows = []
    for sid, typ, ry, ay, am, dm, se, rating, pc, hd in compact:
        compact_rows.append(
            [
                1 if typ == "Serie" else 0,
                ry,
                ay,
                am,
                dm,
                se,
                rating_index.get(rating, -1) if rating is not None else -1,
                country_index.get(pc, -1) if pc is not None else -1,
                genres_by_title.get(sid, []),
                countries_by_title.get(sid, []),
                1 if hd else 0,
                directors_by_title.get(sid, []),
            ]
        )

    dashboard = {
        "meta": {
            "titulo": "La economía del entretenimiento: Netflix y tendencias globales",
            "subtitulo": "Un análisis académico del catálogo de Netflix",
            "fuente": "Kaggle — Netflix Movies and TV Shows (shivamb/netflix-shows)",
            "url_fuente": "https://www.kaggle.com/datasets/shivamb/netflix-shows",
            "snapshot": str(snapshot_max),
            "snapshot_nota": "El catálogo termina el 25 de septiembre de 2021; 2021 está incompleto.",
            "generado_en": quality["generado_en"],
            "total_titulos": total,
            "peliculas": movies,
            "series": series,
            "moneda": "No aplica: el dataset no contiene ingresos ni precios.",
        },
        "kpis": kpis,
        "findings": findings,
        "dimensions": {
            "genres": [{"name": g["name"], "label": g["label"], "count": g["count"]} for g in by_genre],
            "countries": [
                {
                    "name": c["name"], "label": c["label"], "iso3": c["iso3"], "isoN": c["isoN"],
                    "region": c["region"], "count": c["count"],
                }
                for c in top_countries
            ],
            "ratings": rating_list,
            "regions": sorted({c["region"] for c in top_countries}),
            "decades": [d["decade"] for d in by_decade],
            "directors": director_list,
        },
        "titles": {
            "columns": ["type", "release_year", "added_year", "added_month", "duration_min", "seasons",
                        "rating", "primary_country", "genres", "countries", "has_director", "directors"],
            "rows": compact_rows,
        },
        "aggregates": {
            "by_year_release": by_year_release,
            "by_year_added": by_year_added,
            "by_country": country_details,
            "by_genre": by_genre,
            "by_rating": by_rating,
            "by_decade": by_decade,
            "by_region": by_region,
            "duration_hist": duration_hist,
            "seasons_dist": seasons_dist,
            "directors_top": top_directors,
            "decade_genre": decade_genre,
            "year_month": year_month,
            "type_counts": [
                {"type": "Película", "count": movies, "share": pct(movies, total)},
                {"type": "Serie", "count": series, "share": pct(series, total)},
            ],
        },
        "quality": quality,
    }

    out = PUBLIC_DATA / "dashboard.json"
    out.write_text(json.dumps(dashboard, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    # Copia del informe de calidad para enlazarlo desde el tablero.
    (PUBLIC_DATA / "quality_report.json").write_text(
        (DATA / "quality_report.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    size_mb = out.stat().st_size / (1024 * 1024)

    print(f"OK  filas={total}  películas={movies}  series={series}")
    print(f"    países={n_countries}  géneros={n_genres}  directores={n_directors}")
    print(f"    snapshot={snapshot_max}  pico estreno={peak_release['year']}  pico incorporación={peak_added['year']}")
    print(f"    dashboard.json = {size_mb:.2f} MB")
    print(f"    quality_report.json = {(DATA / 'quality_report.json').stat().st_size / 1024:.0f} KB")
    if size_mb > 1:
        print("    ADVERTENCIA: dashboard.json supera 1 MB; revisar compactación.")


if __name__ == "__main__":
    main()
