"""Parche 3: si Haiku no devuelve JSON valido, no mostrar error; intentar rescatarlo y, si no, seguir como conversacion."""
import os, shutil, sys
mp = os.path.expanduser("~/Ellie/main.py")
src = open(mp, encoding="utf-8").read()
if "rescatar_json" in src:
    sys.exit("Parche 3 ya aplicado, no hago nada.")
shutil.copy(mp, mp + ".bak3")

def reemplaza(s, viejo, nuevo):
    if s.count(viejo) != 1:
        sys.exit(f"No encontre exactamente una vez: {viejo[:70]!r}. No cambie nada.")
    return s.replace(viejo, nuevo)

src = reemplaza(src, "max_tokens=300, system=sistema,", "max_tokens=500, system=sistema,")
src = reemplaza(src, "    return parse_json(texto_out)\n", '''    return rescatar_json(texto_out)
''')
src = reemplaza(src, "def interpretar(texto: str) -> dict:", '''def rescatar_json(texto_out: str) -> dict:
    import json as _json, re as _re
    try:
        return parse_json(texto_out)
    except Exception:
        pass
    m = _re.search(r"\\{.*\\}", texto_out, _re.S)      # primer { hasta el ultimo }
    if m:
        try:
            return _json.loads(m.group(0))
        except Exception:
            pass
    log.warning("Haiku no devolvio JSON valido: %r", texto_out[:400])
    return {"accion": "otro"}


def interpretar(texto: str) -> dict:''')
open(mp, "w", encoding="utf-8").write(src)
print("Listo. Ahora: sudo systemctl restart ellie")
