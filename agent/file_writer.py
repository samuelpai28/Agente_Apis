"""Escritura de archivos generados."""

from __future__ import annotations

from pathlib import Path


def write_generated_api(code: str, *, root: Path | None = None) -> Path:
    """
    Guarda el código en generated_api/main.py relativo a la carpeta del agente
    (o a `root` si se indica).
    """
    base = root if root is not None else Path(__file__).resolve().parent
    out_dir = base / "generated_api"
    out_dir.mkdir(parents=True, exist_ok=True)
    init_path = out_dir / "__init__.py"
    if not init_path.exists():
        init_path.write_text("", encoding="utf-8")
    out_path = out_dir / "main.py"
    out_path.write_text(code, encoding="utf-8")
    return out_path
