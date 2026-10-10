"""Parche 4: respuestas del catalogo no se cortan a la mitad."""
import os, shutil, sys
mp = os.path.expanduser("~/Ellie/main.py")
src = open(mp, encoding="utf-8").read()
if "maximo 8 productos" in src:
    sys.exit("Parche 4 ya aplicado, no hago nada.")
shutil.copy(mp, mp + ".bak4")

def reemplaza(s, viejo, nuevo):
    if s.count(viejo) != 1:
        sys.exit(f"No encontre exactamente una vez: {viejo[:70]!r}. No cambie nada.")
    return s.replace(viejo, nuevo)

src = reemplaza(src, "r = client.messages.create(model=CHAT_MODEL, max_tokens=500, system=sistema,\n                               messages=[{\"role\": \"user\", \"content\": pregunta}])",
                     "r = client.messages.create(model=CHAT_MODEL, max_tokens=1200, system=sistema,\n                               messages=[{\"role\": \"user\", \"content\": pregunta}])")
src = reemplaza(src, "Si hay varios productos, lista los mas relevantes (SKU, nombre, precio, disponible). ",
                     "Si hay varios productos, lista maximo 8 productos, una linea por producto (SKU, nombre, precio, disponible), sin intro larga ni categorias extra. ")
open(mp, "w", encoding="utf-8").write(src)
print("Listo. Ahora: sudo systemctl restart ellie")
