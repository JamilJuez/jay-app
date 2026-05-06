#!/usr/bin/env python3
"""
crear_iconos.py - Genera los iconos para la PWA
Pon este script en Jay-APP\app\icons\ y correlo ahi
"""

from PIL import Image
import os

logo = "logonb.png"

if not os.path.exists(logo):
    print(f"❌ No se encontró {logo} en esta carpeta")
    input("Presiona Enter para cerrar...")
    exit()

img = Image.open(logo).convert("RGBA")

for size, name in [(192, "icon-192.png"), (512, "icon-512.png")]:
    resized = img.resize((size, size), Image.LANCZOS)
    resized.save(name)
    print(f"✅ {name} creado ({size}x{size}px)")

print("\n✅ ¡Listo! Iconos generados.")
input("Presiona Enter para cerrar...")
