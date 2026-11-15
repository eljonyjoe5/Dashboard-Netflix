import duckdb

con = duckdb.connect()
con.execute("CREATE TABLE t AS SELECT 's1' id, 'Dramas, Comedies, Action & Adventure' g")
print(con.execute("""
SELECT id, trim(list_extract(parts, i)) AS genre, i AS position
FROM (SELECT id, string_split(g, ',') AS parts FROM t),
     generate_series(1, len(parts)) AS s(i)
ORDER BY i
""").fetchall())

print(con.execute("""
SELECT id, trim(v) AS genre, ord
FROM t, unnest(string_split(g, ',')) WITH ORDINALITY AS u(v, ord)
ORDER BY ord
""").fetchall())
