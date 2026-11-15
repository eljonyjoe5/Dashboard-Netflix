"""
Perfilado del CSV crudo de Netflix (solo lectura, no transforma nada).

Uso:
    python scripts/profile_raw.py

Genera: data/profile_raw.json
"""
from __future__ import annotations

import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "netflix_titles.csv"
OUT = ROOT / "data" / "profile_raw.json"

COLUMNS = [
    "show_id",
    "type",
    "title",
    "director",
    "cast",
    "country",
    "date_added",
    "release_year",
    "rating",
    "duration",
    "listed_in",
    "description",
]


def main() -> None:
    con = duckdb.connect()
    con.execute("PRAGMA threads=4")
    # all_varchar=true para perfilar el texto tal cual viene del archivo.
    con.execute(
        f"""
        CREATE VIEW raw AS
        SELECT * FROM read_csv('{CSV.as_posix()}', header=true, all_varchar=true,
                               quote='"', escape='"', strict_mode=false)
        """
    )

    profile: dict = {"archivo": CSV.name, "bytes": CSV.stat().st_size}

    profile["filas"] = con.execute("SELECT count(*) FROM raw").fetchone()[0]
    profile["columnas"] = [r[0] for r in con.execute("DESCRIBE raw").fetchall()]
    profile["columnas_esperadas"] = COLUMNS

    # --- Nulos / vacíos por campo ---
    nulls = []
    for col in COLUMNS:
        total, nulos = con.execute(
            f"""
            SELECT count(*),
                   count(*) FILTER (WHERE "{col}" IS NULL OR trim("{col}") = '')
            FROM raw
            """
        ).fetchone()
        nulls.append(
            {
                "campo": col,
                "nulos": nulos,
                "porcentaje": round(100 * nulos / total, 2),
            }
        )
    profile["nulos_por_campo"] = nulls

    # --- Duplicados ---
    profile["show_id_duplicados"] = con.execute(
        "SELECT count(*) FROM (SELECT show_id FROM raw GROUP BY 1 HAVING count(*) > 1)"
    ).fetchone()[0]
    profile["filas_duplicadas_completas"] = con.execute(
        "SELECT count(*) FROM (SELECT * FROM raw GROUP BY ALL HAVING count(*) > 1)"
    ).fetchone()[0]

    # --- type ---
    profile["type_valores"] = [
        {"valor": v, "conteo": c}
        for v, c in con.execute(
            "SELECT type, count(*) c FROM raw GROUP BY 1 ORDER BY c DESC"
        ).fetchall()
    ]

    # --- release_year ---
    ry = con.execute(
        """
        SELECT min(try_cast(trim(release_year) AS INTEGER)),
               max(try_cast(trim(release_year) AS INTEGER)),
               count(*) FILTER (WHERE try_cast(trim(release_year) AS INTEGER) IS NULL),
               count(DISTINCT release_year)
        FROM raw
        """
    ).fetchone()
    profile["release_year"] = {
        "min": ry[0],
        "max": ry[1],
        "no_numericos": ry[2],
        "valores_distintos": ry[3],
    }
    profile["release_year_conteo"] = [
        {"anio": int(a), "titulos": c}
        for a, c in con.execute(
            """
            SELECT try_cast(trim(release_year) AS INTEGER) a, count(*) c
            FROM raw GROUP BY 1 ORDER BY 1
            """
        ).fetchall()
    ]

    # --- date_added: formatos y rango ---
    da = con.execute(
        """
        SELECT count(*) FILTER (WHERE trim(date_added) <> ''),
               count(*) FILTER (WHERE trim(date_added) <> ''
                    AND try_strptime(trim(date_added), '%B %d, %Y') IS NULL),
               min(try_strptime(trim(date_added), '%B %d, %Y')),
               max(try_strptime(trim(date_added), '%B %d, %Y')),
               count(DISTINCT try_strptime(trim(date_added), '%B %d, %Y'))
        FROM raw
        """
    ).fetchone()
    profile["date_added"] = {
        "no_vacios": da[0],
        "no_parseables_formato_B_d_Y": da[1],
        "min": str(da[2]) if da[2] else None,
        "max": str(da[3]) if da[3] else None,
        "fechas_distintas": da[4],
    }
    profile["date_added_ejemplos_no_parseables"] = [
        r[0]
        for r in con.execute(
            """
            SELECT date_added FROM raw
            WHERE trim(date_added) <> ''
              AND try_strptime(trim(date_added), '%B %d, %Y') IS NULL
            LIMIT 20
            """
        ).fetchall()
    ]
    # Patrones de formato (mes escrito vs numérico, etc.)
    profile["date_added_patrones"] = [
        {"patron": p, "conteo": c}
        for p, c in con.execute(
            r"""
            SELECT
              CASE
                WHEN trim(date_added) = '' THEN 'vacio'
                WHEN regexp_matches(trim(date_added), '^[A-Za-z]+ \d{1,2}, \d{4}$') THEN 'Month D, YYYY'
                WHEN regexp_matches(trim(date_added), '^\d{1,2}/\d{1,2}/\d{4}$') THEN 'D/M/YYYY'
                WHEN regexp_matches(trim(date_added), '^\d{4}-\d{2}-\d{2}$') THEN 'YYYY-MM-DD'
                ELSE 'otro'
              END patron,
              count(*) c
            FROM raw GROUP BY 1 ORDER BY c DESC
            """
        ).fetchall()
    ]

    # --- duration ---
    profile["duration"] = {
        "vacios": con.execute(
            "SELECT count(*) FROM raw WHERE trim(duration) = ''"
        ).fetchone()[0],
        "con_min": con.execute(
            "SELECT count(*) FROM raw WHERE regexp_matches(trim(duration), '^\d+ min$')"
        ).fetchone()[0],
        "con_seasons": con.execute(
            "SELECT count(*) FROM raw WHERE regexp_matches(trim(duration), '^\d+ Seasons?$')"
        ).fetchone()[0],
        "otros": [
            {"valor": v, "conteo": c}
            for v, c in con.execute(
                r"""
                SELECT duration, count(*) c FROM raw
                WHERE trim(duration) <> ''
                  AND NOT regexp_matches(trim(duration), '^\d+ min$')
                  AND NOT regexp_matches(trim(duration), '^\d+ Seasons?$')
                GROUP BY 1 ORDER BY c DESC LIMIT 20
                """
            ).fetchall()
        ],
    }
    # Cruce type x formato de duration
    profile["type_x_duration"] = [
        {"type": t, "formato": f, "conteo": c}
        for t, f, c in con.execute(
            r"""
            SELECT type,
              CASE
                WHEN regexp_matches(trim(duration), '^\d+ min$') THEN 'minutos'
                WHEN regexp_matches(trim(duration), '^\d+ Seasons?$') THEN 'temporadas'
                WHEN trim(duration) = '' THEN 'vacio'
                ELSE 'otro'
              END f,
              count(*) c
            FROM raw GROUP BY 1,2 ORDER BY 1,2
            """
        ).fetchall()
    ]

    # --- rating ---
    profile["rating_valores"] = [
        {"valor": v, "conteo": c}
        for v, c in con.execute(
            "SELECT coalesce(nullif(trim(rating), ''), '(vacio)') v, count(*) c FROM raw GROUP BY 1 ORDER BY c DESC"
        ).fetchall()
    ]
    profile["rating_anomalias"] = [
        {"show_id": s, "rating": r, "duration": d, "type": t}
        for s, r, d, t in con.execute(
            r"""
            SELECT show_id, rating, duration, type FROM raw
            WHERE regexp_matches(trim(rating), '^\d+ min$')
               OR regexp_matches(trim(rating), '^\d+ Seasons?$')
            ORDER BY show_id
            """
        ).fetchall()
    ]

    # --- multivaluados ---
    for col in ("country", "listed_in", "cast", "director"):
        profile[f"multivaluado_{col}"] = {
            "con_coma": con.execute(
                f"SELECT count(*) FROM raw WHERE \"{col}\" LIKE '%,%'"
            ).fetchone()[0],
            "distintos_brutos": con.execute(
                f"SELECT count(DISTINCT trim(\"{col}\")) FROM raw WHERE trim(\"{col}\") <> ''"
            ).fetchone()[0],
            "max_elementos": con.execute(
                f"""
                SELECT coalesce(max(len(string_split(trim("{col}"), ','))), 0)
                FROM raw WHERE trim("{col}") <> ''
                """
            ).fetchone()[0],
        }

    profile["paises_distintos_brutos"] = con.execute(
        """
        SELECT count(DISTINCT trim(e)) FROM (
          SELECT unnest(string_split(country, ',')) e FROM raw WHERE trim(country) <> ''
        )
        """
    ).fetchone()[0]

    # Espacios sobrantes alrededor de elementos multivaluados
    profile["elementos_con_espacio_extra"] = con.execute(
        """
        SELECT count(*) FROM (
          SELECT unnest(string_split(country, ',')) e FROM raw WHERE trim(country) <> ''
        ) WHERE e <> trim(e)
        """
    ).fetchone()[0]

    # Primeras filas para inspección
    profile["muestra_5"] = [
        dict(zip(COLUMNS, row))
        for row in con.execute("SELECT * FROM raw LIMIT 5").fetchall()
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in profile.items() if k not in ("muestra_5", "release_year_conteo", "rating_valores", "date_added_patrones", "type_x_duration")}, ensure_ascii=False, indent=2))
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
