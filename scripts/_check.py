import json
from pathlib import Path

d = json.loads(Path("public/data/dashboard.json").read_text(encoding="utf-8"))
q = json.loads(Path("data/quality_report.json").read_text(encoding="utf-8"))

print("== KPIs ==")
print(json.dumps(d["kpis"], ensure_ascii=False, indent=2)[:4000])
print("\n== findings ==")
for f in d["findings"]:
    print("-", f["titulo"], "|", f["cifra"], "|", f["texto"])
print("\n== meta ==")
print(json.dumps(d["meta"], ensure_ascii=False, indent=2))
print("\n== aggregates keys ==")
for k, v in d["aggregates"].items():
    print(k, len(v), (v[0] if v else None))
print("\n== dimensions ==")
print("genres", len(d["dimensions"]["genres"]), d["dimensions"]["genres"][:3])
print("countries", len(d["dimensions"]["countries"]), d["dimensions"]["countries"][:3])
print("regions", d["dimensions"]["regions"])
print("ratings", d["dimensions"]["ratings"])
print("directors", len(d["dimensions"]["directors"]))
print("rows", len(d["titles"]["rows"]), d["titles"]["rows"][0])
print("\n== quality ==")
print(json.dumps({k: q[k] for k in ("totales", "duplicados", "cobertura")}, ensure_ascii=False, indent=2))
print("\n== campos ==")
for f in q["campos"]:
    print(f)
print("\n== anomalias ==")
print(json.dumps(q["anomalias"], ensure_ascii=False, indent=2)[:3000])
