import duckdb
from pathlib import Path

csv = Path("netflix_titles.csv").resolve().as_posix()
con = duckdb.connect()
con.execute(
    f"CREATE VIEW raw AS SELECT * FROM read_csv('{csv}', header=true, all_varchar=true, strict_mode=false)"
)

print("--- duration NULL o vacio ---")
for r in con.execute(
    "SELECT show_id,type,title,rating,duration,date_added FROM raw WHERE duration IS NULL OR trim(duration)=''"
).fetchall():
    print(r)

print("--- rating NULL o vacio ---")
for r in con.execute(
    "SELECT show_id,type,title,rating,duration FROM raw WHERE rating IS NULL OR trim(rating)=''"
).fetchall():
    print(r)

print("--- date_added NULL o vacio ---")
for r in con.execute(
    "SELECT show_id,type,title,date_added,release_year FROM raw WHERE date_added IS NULL OR trim(date_added)=''"
).fetchall():
    print(r)

print("--- ratings distintos ---")
for r in con.execute(
    "SELECT rating, count(*) c FROM raw GROUP BY 1 ORDER BY c DESC"
).fetchall():
    print(r)

print("--- top paises (trim, sin nulos) ---")
for r in con.execute(
    """
    SELECT trim(e) pais, count(*) c FROM (
      SELECT unnest(string_split(country, ',')) e FROM raw WHERE trim(country) <> ''
    ) WHERE trim(e) <> '' GROUP BY 1 ORDER BY c DESC LIMIT 30
    """
).fetchall():
    print(r)

print("--- paises con variantes sospechosas ---")
for r in con.execute(
    """
    SELECT pais, c FROM (
      SELECT trim(e) pais, count(*) c FROM (
        SELECT unnest(string_split(country, ',')) e FROM raw WHERE trim(country) <> ''
      ) WHERE trim(e) <> '' GROUP BY 1
    )
    WHERE pais ILIKE '%korea%' OR pais ILIKE '%united%' OR pais ILIKE '%kingdom%'
       OR pais ILIKE '%russia%' OR pais ILIKE '%soviet%' OR pais ILIKE '%german%'
       OR pais ILIKE '%viet%' OR pais ILIKE '%iran%' OR pais ILIKE '%taiwan%'
       OR pais ILIKE '%hong%' OR pais ILIKE '%congo%' OR pais ILIKE '%dominican%'
    ORDER BY c DESC
    """
).fetchall():
    print(r)

print("--- anios de estreno faltantes entre 1925 y 2021 ---")
years = [r[0] for r in con.execute("SELECT DISTINCT CAST(release_year AS INT) FROM raw ORDER BY 1").fetchall()]
print(sorted(set(range(1925, 2022)) - set(years)))

print("--- anio incorporacion: rango y conteo por anio ---")
for r in con.execute(
    """
    SELECT CAST(strftime(try_strptime(trim(date_added), '%B %d, %Y'), '%Y') AS INT) a, count(*) c
    FROM raw GROUP BY 1 ORDER BY 1
    """
).fetchall():
    print(r)

print("--- filas con date_added anterior a release_year ---")
print(con.execute(
    """
    SELECT count(*) FROM raw
    WHERE trim(date_added) <> ''
      AND CAST(strftime(try_strptime(trim(date_added), '%B %d, %Y'), '%Y') AS INT) < CAST(release_year AS INT)
    """
).fetchone())

print("--- tipos de contenido por anio de incorporacion (ultimos) ---")
for r in con.execute(
    """
    SELECT CAST(strftime(try_strptime(trim(date_added), '%B %d, %Y'), '%Y') AS INT) a, type, count(*)
    FROM raw GROUP BY 1,2 ORDER BY 1 DESC,2 LIMIT 12
    """
).fetchall():
    print(r)
