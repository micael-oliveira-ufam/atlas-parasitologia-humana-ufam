#!/usr/bin/env python3
"""Copia os dados e as imagens do site (../public) para os assets do app e grava um manifesto
com sha256 (reprodutibilidade: o app mostra o hash dos dados em 'Sobre').

Uso (a partir de flutter_app/):  python3 tool/sync_assets.py
Sem dependências além da biblioteca padrão. Não grava data/hora, para o resultado ser determinístico."""
import hashlib, json, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SRC = HERE.parent / "public"
DST = HERE / "assets"

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    if not (SRC / "data" / "modulos.json").exists():
        print(f"ERRO: {SRC}/data/modulos.json não encontrado (rode a partir do projeto completo).", file=sys.stderr)
        return 1
    for sub in ("data", "img"):
        if (DST / sub).exists():
            shutil.rmtree(DST / sub)
    shutil.copytree(SRC / "data", DST / "data")
    shutil.copytree(SRC / "assets" / "img", DST / "img")
    files = sorted(p for p in DST.rglob("*") if p.is_file() and p.name != "manifest.json")
    entries = {str(p.relative_to(DST)).replace("\\", "/"): sha(p) for p in files}
    combined = hashlib.sha256("".join(f"{k}\0{v}\n" for k, v in sorted(entries.items())).encode()).hexdigest()
    manifest = {"source": "public/ (site Atlas de Parasitologia)", "fileCount": len(entries), "combinedSha256": combined, "files": entries}
    (DST / "data" / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(entries)} arquivos | sha256 combinado {combined}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
