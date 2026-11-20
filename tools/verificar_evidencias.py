#!/usr/bin/env python
"""Pre-revisión de evidencias (la misma lógica básica que usa Integra2).

Uso:  python tools/verificar_evidencias.py            → revisa la unidad en curso
      python tools/verificar_evidencias.py --unidad 2
      python tools/verificar_evidencias.py --todas
Se ejecuta también en GitHub Actions en cada push (pestaña Actions del repositorio).
Este script NO califica: sólo te avisa a tiempo de lo que Integra2 marcará como faltante.
"""
import argparse
import json
import re
import struct
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REGLAS = json.loads((Path(__file__).parent / "integra2.json").read_text(encoding="utf-8"))
MIN_KB_IMAGEN = 25


def seccion(texto, n):
    titulos = list(re.finditer(r"^(#{1,3})\s*Unidad\s+([1-4])\b", texto, re.I | re.M))
    for i, m in enumerate(titulos):
        if int(m.group(2)) == n:
            fin = titulos[i + 1].start() if i + 1 < len(titulos) else len(texto)
            return texto[m.end():fin]
    return ""


def imagenes(texto):
    rutas = re.findall(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)", texto) + re.findall(r"<img[^>]+src=[\"']([^\"']+)", texto, re.I)
    return {r.strip().lstrip("./").split("?")[0] for r in rutas}


def tiene_exif(ruta):
    datos = ruta.read_bytes()[:65536]
    return b"Exif\x00\x00" in datos


def tamano_imagen(ruta):
    d = ruta.read_bytes()
    if d[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", d[16:24])
    i = 2
    while i < len(d) - 9:
        if d[i] != 0xFF:
            i += 1
            continue
        marca = d[i + 1]
        if marca in (0xC0, 0xC1, 0xC2):
            alto, ancho = struct.unpack(">HH", d[i + 5:i + 9])
            return ancho, alto
        i += 2 + struct.unpack(">H", d[i + 2:i + 4])[0]
    return 0, 0


def revisar(u, readme):
    errores, avisos = [], []
    sec = seccion(readme, u["numero"])
    if not sec:
        errores.append(f"README sin la sección «## Unidad {u['numero']}»")
    refs = imagenes(sec)
    for e in u["evidencias"]:
        p = RAIZ / e["archivo"]
        if not p.exists():
            errores.append(f"falta {e['archivo']} ({e['titulo']})")
            continue
        if e["archivo"] not in refs:
            errores.append(f"{e['archivo']} existe pero no está insertada en la sección Unidad {u['numero']} del README")
        if p.stat().st_size < MIN_KB_IMAGEN * 1024:
            errores.append(f"{e['archivo']} pesa menos de {MIN_KB_IMAGEN} KB")
        try:
            w, h = tamano_imagen(p)
            if max(w, h) < 800:
                avisos.append(f"{e['archivo']} tiene resolución baja ({w}×{h}); mínimo 800 px en el lado mayor")
        except Exception:
            avisos.append(f"{e['archivo']} no parece una imagen JPG/PNG válida")
        if e["tipo"] == "foto" and not tiene_exif(p):
            avisos.append(f"{e['archivo']} no tiene metadatos EXIF (vale la mitad): súbela original desde la cámara")
    for en in u["entregables"]:
        if en["archivo"].startswith("tag:"):
            continue
        p = RAIZ / en["archivo"]
        if not p.exists():
            errores.append(f"falta el entregable {en['archivo']} ({en['titulo']})")
        elif p.stat().st_size < en["min_kb"] * 1024:
            errores.append(f"{en['archivo']} es muy pequeño (mínimo {en['min_kb']} KB)")
    return errores, avisos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unidad", type=int)
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--estricto", action="store_true", help="falla (exit 1) si hay errores")
    a = ap.parse_args()
    ahora = datetime.now().astimezone()
    if a.todas:
        unidades = REGLAS["unidades"]
    elif a.unidad:
        unidades = [u for u in REGLAS["unidades"] if u["numero"] == a.unidad]
    else:
        unidades = [u for u in REGLAS["unidades"] if datetime.fromisoformat(u["inicio"]) <= ahora <= datetime.fromisoformat(u["cierre"])]
        if not unidades:
            print("No hay unidad en curso; usa --unidad N o --todas.")
            return 0
    readme = (RAIZ / "README.md").read_text(encoding="utf-8") if (RAIZ / "README.md").exists() else ""
    total = 0
    for u in unidades:
        errores, avisos = revisar(u, readme)
        total += len(errores)
        print(f"\n== Unidad {u['numero']} · cierre {u['cierre'][:16].replace('T', ' ')} ==")
        for e in errores:
            print(f"  ❌ {e}")
            if "GITHUB_ACTIONS" in __import__("os").environ:
                print(f"::warning title=Integra2 U{u['numero']}::{e}")
        for w in avisos:
            print(f"  ⚠️  {w}")
        if not errores and not avisos:
            print("  ✅ Todo en orden")
    return 1 if (a.estricto and total) else 0


if __name__ == "__main__":
    sys.exit(main())
