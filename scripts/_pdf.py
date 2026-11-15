from pypdf import PdfReader
from pathlib import Path

r = PdfReader("Proyectos (1).pdf")
out = []
for i, p in enumerate(r.pages):
    out.append(f"\n--- pagina {i + 1} ---\n")
    out.append(p.extract_text() or "")
Path("data/_pdf_text.txt").write_text("".join(out), encoding="utf-8")
print("paginas:", len(r.pages))
