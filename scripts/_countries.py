import duckdb
from pathlib import Path

csv = Path("netflix_titles.csv").resolve().as_posix()
con = duckdb.connect()
con.execute(
    f"CREATE VIEW raw AS SELECT * FROM read_csv('{csv}', header=true, all_varchar=true, strict_mode=false)"
)
rows = con.execute(
    """
    SELECT trim(e) pais, count(*) c FROM (
      SELECT unnest(string_split(country, ',')) e FROM raw WHERE trim(country) <> ''
    ) WHERE trim(e) <> '' GROUP BY 1 ORDER BY 1
    """
).fetchall()
for pais, c in rows:
    print(f"{pais}|{c}")
print("TOTAL", len(rows))
