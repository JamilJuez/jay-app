"""Catalogo de productos para Ellie: carga JSON a SQLite y busca."""
import json, re, sqlite3, unicodedata, os

DB = os.environ.get("ELLIE_DB", os.path.expanduser("~/Ellie/datos.db"))

def _norm(s):
    s = unicodedata.normalize("NFD", str(s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def cargar(ruta_json):
    d = json.load(open(ruta_json, encoding="utf-8"))
    con = sqlite3.connect(DB)
    con.executescript("""
    DROP TABLE IF EXISTS catalogo;
    CREATE TABLE catalogo(sku TEXT PRIMARY KEY, upc TEXT, nombre TEXT, categoria TEXT,
      subcategoria TEXT, size TEXT, precio REAL, disponible INTEGER, unidades INTEGER,
      nuevo INTEGER, kosher TEXT, busca TEXT);
    CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);""")
    for p in d["productos"]:
        busca = _norm(" ".join(str(p.get(k) or "") for k in
                ("Sku", "UPC", "Nombre", "Categoria", "SubCategoria", "Size")))
        con.execute("INSERT OR REPLACE INTO catalogo VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (
            str(p["Sku"]), p.get("UPC") or "", p["Nombre"], p.get("Categoria") or "",
            p.get("SubCategoria") or "", p.get("Size") or "", p.get("Precio"),
            p.get("Disponible") or 0, p.get("Unidades") or 0,
            1 if p.get("Estado") == "New" else 0, p.get("Kosher") or "", busca))
    con.execute("INSERT OR REPLACE INTO meta VALUES('catalogo_fecha',?)", (str(d.get("last_updated")),))
    con.commit()
    return len(d["productos"]), d.get("last_updated")

STOP = set("""otros otro otra otras algun alguna algunos algunas que cual cuales tenemos tienes tiene tienen
hay ahi hacen tengo tenga quiero busco dame dime sabes saber precio precios cuanto cuantos cuantas cuesta cuestan
the and for with any some other have what del las los una uno unos unas por con sin para como esta este esos esas
has are how much many does de el la en un y a o se es al lo le su mi tu""".split())
UNIDADES = {"oz", "lb", "lbs", "ml", "gr", "kg", "pack", "ct", "und"}

def _tokens(q):
    return [w for w in re.findall(r"[a-z0-9.]+", q) if len(w) >= 2 and w not in STOP]

def _raiz(w):
    return w[:-1] if len(w) >= 5 and w.endswith("s") else w   # chips->chip, tostones->tostone

def buscar(consulta, limite=8):
    """Devuelve (filas, fecha). SKU/UPC exacto, o palabras: primero todas (AND), si no hay, las que mas coincidan."""
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    try:
        fecha = (con.execute("SELECT v FROM meta WHERE k='catalogo_fecha'").fetchone() or [None])[0]
        q = _norm(consulta)
        filas = []
        for tok in re.findall(r"\d{3,}", q):
            filas += con.execute("SELECT * FROM catalogo WHERE sku=? OR upc=?", (tok, tok)).fetchall()
        if filas:
            return filas[:limite], fecha
        raices = [_raiz(w) for w in _tokens(q)]
        if not raices:
            return [], fecha
        like = [f"%{w}%" for w in raices]
        en_nombre = " AND ".join("lower(nombre) LIKE ?" for _ in raices)
        where = " AND ".join("busca LIKE ?" for _ in raices)
        filas = con.execute(f"SELECT * FROM catalogo WHERE {where} ORDER BY ({en_nombre}) DESC, nombre LIMIT ?",
                            like * 2 + [limite]).fetchall()
        nucleo = [f"%{_raiz(w)}%" for w in _tokens(q) if w.isalpha() and w not in UNIDADES]
        if not filas and len(nucleo) > 1:      # ninguna coincide con todas: las que coinciden con mas palabras
            puntos = " + ".join("(busca LIKE ?)" for _ in nucleo)
            minimo = (len(nucleo) + 1) // 2
            filas = con.execute(f"SELECT *, ({puntos}) AS pts FROM catalogo WHERE pts >= ? ORDER BY pts DESC, nombre LIMIT ?",
                                nucleo + [minimo, limite]).fetchall()
        return filas, fecha
    finally:
        con.close()

def formatear(filas, fecha):
    if not filas:
        return "Sin coincidencias en el catalogo."
    out = [f"Catalogo actualizado: {fecha}"]
    for r in filas:
        precio = f"${r['precio']:.2f}" if r["precio"] else "sin precio en catalogo"
        out.append(f"SKU {r['sku']} | {r['nombre']} | {r['size']} | {precio} | "
                   f"disponible {r['disponible']} | {r['unidades']} und/caja | "
                   f"{'NUEVO' if r['nuevo'] else ''} | UPC {r['upc']}")
    return "\n".join(out)

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "cargar":
        print(cargar(sys.argv[2]))
    else:
        print(formatear(*buscar(" ".join(sys.argv[1:]))))
