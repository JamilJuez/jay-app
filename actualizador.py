#!/usr/bin/env python3
"""
actualizador.py - Script de automatización del catálogo
Uso: python actualizador.py
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime

# ── CONFIGURACIÓN ──────────────────────────────────────────────
PRODUCTOS_XLSX = "productos.xlsx"       # Tu archivo principal
GOYA_XLS       = "sqlexec.xls"         # Archivo de Goya
OUTPUT_JSON    = "app/productos.json"  # JSON para la app
# ───────────────────────────────────────────────────────────────

def log(msg, tipo="INFO"):
    icons = {"INFO": "ℹ️ ", "OK": "✅", "NEW": "🆕", "WARN": "⚠️ ", "ERR": "❌"}
    print(f"{icons.get(tipo, '  ')} {msg}")

def cargar_goya():
    log(f"Cargando archivo de Goya: {GOYA_XLS}")
    try:
        # Try openpyxl first (works if file is actually xlsx)
        try:
            df = pd.read_excel(GOYA_XLS, engine='openpyxl')
            log("Leído con openpyxl", "OK")
        except Exception:
            # Fall back to xlrd for true .xls files
            try:
                import xlrd
                df = pd.read_excel(GOYA_XLS, engine='xlrd')
                log("Leído con xlrd", "OK")
            except ImportError:
                log("Instalando xlrd...", "INFO")
                import subprocess
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'xlrd'],
                             capture_output=True, check=True)
                import xlrd
                df = pd.read_excel(GOYA_XLS, engine='xlrd')
                log("Leído con xlrd", "OK")

        df.columns = df.columns.str.strip()
        df['PRODUCT NUMBER'] = df['PRODUCT NUMBER'].astype(int).astype(str)
        df['QUANTITY ON HAND'] = pd.to_numeric(df['QUANTITY ON HAND'], errors='coerce').fillna(0).astype(int)
        df['QUANTITY ON ORDER'] = pd.to_numeric(df['QUANTITY ON ORDER'], errors='coerce').fillna(0).astype(int)
        log(f"Goya: {len(df)} productos cargados", "OK")
        return df.set_index('PRODUCT NUMBER')
    except Exception as e:
        log(f"Error leyendo Goya: {e}", "ERR")
        sys.exit(1)

def cargar_productos():
    log(f"Cargando productos: {PRODUCTOS_XLSX}")
    try:
        df = pd.read_excel(PRODUCTOS_XLSX)
        cols = ['Categoria','SubCategoria','Sku','Size','Precio','Nombre','Disponible','Imagen','Unidades','Estado']
        if 'Kosher' in df.columns:
            cols.append('Kosher')
        df = df[cols].copy()
        df = df.dropna(subset=['Sku','Nombre'])
        df['Sku'] = df['Sku'].astype(int).astype(str)
        df['Disponible'] = pd.to_numeric(df['Disponible'], errors='coerce').fillna(0).astype(int)
        df['Precio'] = pd.to_numeric(df['Precio'], errors='coerce')
        df['Unidades'] = pd.to_numeric(df['Unidades'], errors='coerce').fillna(0).astype(int)
        df['Estado'] = df['Estado'].fillna('')
        df['Categoria'] = df['Categoria'].fillna('SIN CATEGORIA')
        df['SubCategoria'] = df['SubCategoria'].fillna('')
        df['Size'] = df['Size'].fillna('')
        df['Imagen'] = df['Imagen'].fillna('')
        log(f"Productos: {len(df)} SKUs cargados", "OK")
        return df
    except Exception as e:
        log(f"Error leyendo productos: {e}", "ERR")
        sys.exit(1)

def actualizar(productos_df, goya_df):
    skus_productos = set(productos_df['Sku'].tolist())
    skus_goya = set(goya_df.index.tolist())

    # Productos nuevos en Goya (no están en tu Excel)
    nuevos = skus_goya - skus_productos
    # Productos en tu Excel pero no en Goya (posibles eliminados)
    eliminados = skus_productos - skus_goya
    # Productos en ambos (actualizar inventario)
    comunes = skus_productos & skus_goya

    log(f"Actualizando inventario de {len(comunes)} productos...", "INFO")
    
    # Actualizar inventario de productos existentes
    for idx, row in productos_df.iterrows():
        sku = row['Sku']
        if sku in goya_df.index:
            productos_df.at[idx, 'Disponible'] = goya_df.loc[sku, 'QUANTITY ON HAND']

    # Agregar productos nuevos
    nuevos_rows = []
    if nuevos:
        log(f"\n{'='*50}", "INFO")
        log(f"PRODUCTOS NUEVOS DETECTADOS: {len(nuevos)}", "NEW")
        log(f"{'='*50}", "INFO")
        for sku in sorted(nuevos):
            g = goya_df.loc[sku]
            nombre = g.get('PRODUCT DESCRIPTION', f'PRODUCTO {sku}')
            size   = g.get('PRODUCT SIZE', '')
            units  = int(g.get('PACK SIZE', 0)) if pd.notna(g.get('PACK SIZE', 0)) else 0
            inv    = int(g.get('QUANTITY ON HAND', 0))
            log(f"  SKU {sku}: {nombre} ({size})", "NEW")
            nuevos_rows.append({
                'Categoria':    '⚠️ ASIGNAR CATEGORIA',
                'SubCategoria': '⚠️ ASIGNAR SUBCATEGORIA',
                'Sku':          sku,
                'Size':         size,
                'Precio':       None,
                'Nombre':       nombre,
                'Disponible':   inv,
                'Imagen':       f"{sku}_A1C1.webp",
                'Unidades':     units,
                'Estado':       'New'
            })
        if nuevos_rows:
            nuevos_df = pd.DataFrame(nuevos_rows)
            productos_df = pd.concat([productos_df, nuevos_df], ignore_index=True)
            log(f"\n👉 Recuerda: descarga las fotos y nómbralas {'{SKU}_A1C1.webp'}", "INFO")

    # Eliminar automáticamente productos que ya no están en Goya
    if eliminados:
        log(f"\n{'='*50}", "INFO")
        log(f"PRODUCTOS ELIMINADOS DE GOYA: {len(eliminados)}", "WARN")
        log(f"{'='*50}", "INFO")
        for sku in sorted(eliminados):
            row = productos_df[productos_df['Sku'] == sku].iloc[0]
            log(f"  SKU {sku}: {row['Nombre']} — REMOVIDO", "WARN")
        productos_df = productos_df[~productos_df['Sku'].isin(eliminados)]
        log(f"\n👉 {len(eliminados)} productos removidos del catálogo.", "INFO")

    return productos_df, len(nuevos), len(eliminados), len(comunes)

def guardar_todo(productos_df):
    # Guardar Excel actualizado
    productos_df.to_excel(PRODUCTOS_XLSX, index=False)
    log(f"Excel guardado: {PRODUCTOS_XLSX}", "OK")

    # Generar JSON para la app
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    records = []
    for _, row in productos_df.iterrows():
        precio = row['Precio']
        records.append({
            'Categoria':    row['Categoria'],
            'SubCategoria': row['SubCategoria'],
            'Sku':          str(row['Sku']),
            'Size':         row['Size'],
            'Precio':       None if pd.isna(precio) else round(float(precio), 2),
            'Nombre':       row['Nombre'],
            'Disponible':   int(row['Disponible']),
            'Imagen':       row['Imagen'],
            'Unidades':     int(row['Unidades']),
            'Estado':       row['Estado'],
            'Kosher':       str(row.get('Kosher', 'NO')) if 'Kosher' in row else 'NO'
        })

    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "productos": records
    }
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
    log(f"JSON generado: {OUTPUT_JSON} ({len(records)} productos)", "OK")

def main():
    print("\n" + "="*50)
    print("   ACTUALIZADOR DE CATÁLOGO")
    print(f"   {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*50 + "\n")

    if not os.path.exists(GOYA_XLS):
        log(f"No se encontró {GOYA_XLS} — ponlo en la misma carpeta.", "ERR")
        sys.exit(1)

    goya_df     = cargar_goya()
    productos_df = cargar_productos()
    productos_df, nuevos, eliminados, actualizados = actualizar(productos_df, goya_df)
    guardar_todo(productos_df)

    print("\n" + "="*50)
    log(f"RESUMEN FINAL:", "OK")
    log(f"  Inventario actualizado: {actualizados} productos", "OK")
    log(f"  Productos nuevos:       {nuevos}", "NEW" if nuevos else "OK")
    log(f"  Posibles eliminados:    {eliminados}", "WARN" if eliminados else "OK")
    print("="*50)
    print("\n✅ ¡Listo! Ahora haz push a GitHub.")
    input("\nPresiona Enter para cerrar...")

if __name__ == "__main__":
    main()
