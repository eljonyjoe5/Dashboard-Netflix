import duckdb

con = duckdb.connect("data/netflix_catalog.duckdb", read_only=True)
print("sin primary pero con pais:")
for r in con.execute(
    """
    SELECT t.show_id, t.title, t.country_raw
    FROM titles t
    WHERE t.primary_country IS NULL AND EXISTS (SELECT 1 FROM title_countries c WHERE c.show_id = t.show_id)
    LIMIT 20
    """
).fetchall():
    print(r)
print(con.execute(
    """
    SELECT count(*) FROM titles t
    WHERE t.primary_country IS NULL AND EXISTS (SELECT 1 FROM title_countries c WHERE c.show_id = t.show_id)
    """
).fetchone())
print("country_raw raros:")
for r in con.execute(
    """
    SELECT show_id, title, '[' || country_raw || ']'
    FROM titles
    WHERE country_raw IS NOT NULL AND (country_raw LIKE ',%' OR country_raw LIKE '%,' OR country_raw LIKE '%,,%')
    LIMIT 20
    """
).fetchall():
    print(r)
print("titulos con country_raw no nulo pero sin bridge:")
print(con.execute(
    """
    SELECT count(*) FROM titles t
    WHERE t.country_raw IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM title_countries c WHERE c.show_id = t.show_id)
    """
).fetchone())
print("titulos con title duplicado:")
for r in con.execute(
    "SELECT title, count(*) c FROM titles GROUP BY 1 HAVING count(*) > 1"
).fetchall():
    print(r)
print("share directores base:", con.execute("SELECT count(*) FROM titles WHERE has_director").fetchone())
