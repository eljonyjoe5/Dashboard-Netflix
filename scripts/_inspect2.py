import duckdb
from pathlib import Path

csv = Path("netflix_titles.csv").resolve().as_posix()
con = duckdb.connect()
con.execute(
    f"CREATE VIEW raw AS SELECT * FROM read_csv('{csv}', header=true, all_varchar=true, strict_mode=false)"
)

print("--- titulos con genero repetido ---")
print(con.execute(
    """
    SELECT count(*) FROM (
      SELECT show_id FROM raw, unnest(string_split(listed_in, ',')) AS t(e)
      GROUP BY show_id, trim(e) HAVING count(*) > 1
    )
    """
).fetchone())

print("--- titulos con pais repetido ---")
print(con.execute(
    """
    SELECT count(*) FROM (
      SELECT show_id FROM raw, unnest(string_split(country, ',')) AS t(e)
      WHERE trim(country) <> ''
      GROUP BY show_id, trim(e) HAVING count(*) > 1
    )
    """
).fetchone())

print("--- campos con solo espacios ---")
for col in ["director", "cast", "country", "date_added", "rating", "duration", "listed_in"]:
    n = con.execute(f"SELECT count(*) FROM raw WHERE \"{col}\" IS NOT NULL AND trim(\"{col}\") = ''").fetchone()[0]
    print(col, n)

print("--- rating en filas con duration en rating: type/duracion ---")
for r in con.execute(
    "SELECT show_id, type, rating, duration FROM raw WHERE regexp_matches(trim(rating), '^[0-9]+ min$')"
).fetchall():
    print(r)

print("--- top generos ---")
for r in con.execute(
    """
    SELECT trim(e) g, count(*) c FROM (
      SELECT unnest(string_split(listed_in, ',')) e FROM raw
    ) WHERE trim(e) <> '' GROUP BY 1 ORDER BY c DESC LIMIT 25
    """
).fetchall():
    print(r)

print("--- top directores (sin nulos) ---")
for r in con.execute(
    """
    SELECT trim(e) d, count(*) c FROM (
      SELECT unnest(string_split(director, ',')) e FROM raw WHERE trim(director) <> ''
    ) WHERE trim(e) <> '' GROUP BY 1 ORDER BY c DESC LIMIT 15
    """
).fetchall():
    print(r)

print("--- filas con 1 solo genero / 2 / 3 ---")
for r in con.execute(
    """
    SELECT len(string_split(listed_in, ',')) n, count(*) FROM raw GROUP BY 1 ORDER BY 1
    """
).fetchall():
    print(r)

print("--- paises por titulo: distribucion ---")
for r in con.execute(
    """
    SELECT CASE WHEN trim(country) = '' THEN 0 ELSE len(string_split(country, ',')) END n, count(*)
    FROM raw GROUP BY 1 ORDER BY 1
    """
).fetchall():
    print(r)

print("--- generos: lista completa ---")
for r in con.execute(
    """
    SELECT trim(e) g, count(*) c FROM (
      SELECT unnest(string_split(listed_in, ',')) e FROM raw
    ) WHERE trim(e) <> '' GROUP BY 1 ORDER BY c DESC
    """
).fetchall():
    print(r)
