#!/usr/bin/env python3
"""
actualizar_precios.py - Extrae precios del PDF de Goya y actualiza productos.xlsx
Uso: python actualizar_precios.py
"""

import re
import sys
import json
import os
from datetime import datetime

# ── CONFIGURACIÓN ──────────────────────────────────────────────
PDF_PRECIOS   = "PriceList.pdf"
PRODUCTOS_XLSX = "productos.xlsx"
OUTPUT_JSON   = "app/productos.json"
# ───────────────────────────────────────────────────────────────

def log(msg, tipo="INFO"):
    icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERR": "❌"}
    print(f"{icons.get(tipo, '  ')} {msg}")

def extraer_precios_pdf(pdf_path):
    log(f"Leyendo PDF: {pdf_path}")
    try:
        from pypdf import PdfReader
    except ImportError:
        log("Instalando pypdf...", "INFO")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pypdf'], capture_output=True)
        from pypdf import PdfReader

    r = PdfReader(pdf_path)
    log(f"PDF cargado: {len(r.pages)} páginas", "OK")

    # Extraer todo el texto
    all_text = ''
    for page in r.pages:
        all_text += page.extract_text() + '\n'

    # Unir líneas de descripción partidas
    lines = all_text.split('\n')
    joined_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r'^\d{4}\s', line):
            while i + 1 < len(lines):
                next_line = lines[i+1].strip()
                if (next_line and 
                    not re.match(r'^\d{4}\s', next_line) and 
                    not re.match(r'^[A-Z\s]{4,}$', next_line) and
                    not re.match(r'^Week\s', next_line)):
                    line = line + ' ' + next_line
                    i += 1
                else:
                    break
            joined_lines.append(line)
        i += 1

    # Extraer SKU y CASE COST
    pattern = re.compile(r'^(\d{4})\s+.+?\s+(\d{1,4}\.\d{2})\s+\(')
    prices = {}
    for line in joined_lines:
        m = pattern.match(line)
        if m:
            sku, price = m.group(1), float(m.group(2))
            if sku not in prices:  # Primera ocurrencia = precio principal
                prices[sku] = price

    log(f"Precios extraídos: {len(prices)} SKUs", "OK")
    return prices

def actualizar_precios(pdf_path, xlsx_path, json_path):
    import pandas as pd

    # Extraer precios del PDF
    prices = extraer_precios_pdf(pdf_path)

    # Cargar productos
    log(f"Cargando: {xlsx_path}")
    df = pd.read_excel(xlsx_path)
    df = df.dropna(subset=['Sku', 'Nombre'])
    df['Sku'] = df['Sku'].astype(int).astype(str)

    # Actualizar precios
    updated = 0
    not_found = 0
    for idx, row in df.iterrows():
        sku = str(row['Sku'])
        if sku in prices:
            df.at[idx, 'Precio'] = prices[sku]
            updated += 1
        else:
            not_found += 1

    log(f"Precios actualizados: {updated}", "OK")
    if not_found > 0:
        log(f"SKUs sin precio en PDF: {not_found} (se mantiene precio anterior)", "WARN")

    # Guardar Excel
    df.to_excel(xlsx_path, index=False)
    log(f"Excel guardado: {xlsx_path}", "OK")

    # Generar JSON
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    records = []
    for _, row in df.iterrows():
        precio = row.get('Precio')
        try:
            precio = None if pd.isna(precio) else round(float(precio), 2)
        except:
            precio = None

        records.append({
            'Categoria':    str(row.get('Categoria', '') or ''),
            'SubCategoria': str(row.get('SubCategoria', '') or ''),
            'Sku':          str(row['Sku']),
            'Size':         str(row.get('Size', '') or ''),
            'Precio':       precio,
            'Nombre':       str(row['Nombre']),
            'Disponible':   int(row.get('Disponible', 0) or 0),
            'Imagen':       str(row.get('Imagen', '') or ''),
            'Unidades':     int(row.get('Unidades', 0) or 0),
            'Estado':       str(row.get('Estado', '') or '')
        })

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False)
    log(f"JSON generado: {json_path} ({len(records)} productos)", "OK")

    return updated, not_found

def main():
    print("\n" + "="*50)
    print("   ACTUALIZADOR DE PRECIOS")
    print(f"   {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*50 + "\n")

    if not os.path.exists(PDF_PRECIOS):
        log(f"No se encontró '{PDF_PRECIOS}' — ponlo en esta carpeta.", "ERR")
        log("El PDF es el Price List que te manda Goya.", "INFO")
        input("\nPresiona Enter para cerrar...")
        sys.exit(1)

    if not os.path.exists(PRODUCTOS_XLSX):
        log(f"No se encontró '{PRODUCTOS_XLSX}'.", "ERR")
        input("\nPresiona Enter para cerrar...")
        sys.exit(1)

    updated, not_found = actualizar_precios(PDF_PRECIOS, PRODUCTOS_XLSX, OUTPUT_JSON)

    print("\n" + "="*50)
    log("RESUMEN:", "OK")
    log(f"  Precios actualizados: {updated} productos", "OK")
    if not_found > 0:
        log(f"  Sin precio en PDF:    {not_found} productos", "WARN")
    print("="*50)
    print("\n✅ ¡Listo! Ahora haz push a GitHub.")
    input("\nPresiona Enter para cerrar...")

if __name__ == "__main__":
    main()
