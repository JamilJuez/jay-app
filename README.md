# 📦 Catálogo Goya — Guía Completa

## Estructura de carpetas

```
tu-proyecto/
├── app/
│   ├── index.html          ← La app PWA
│   ├── manifest.json       ← Configuración PWA
│   ├── productos.json      ← Datos generados (no editar)
│   ├── promociones.json    ← Promociones activas
│   └── icons/
│       ├── logo.png        ← Tu logo de Ellie
│       ├── icon-192.png    ← Ícono app iPhone
│       └── icon-512.png    ← Ícono app iPad
├── images/                 ← TODAS tus fotos .webp aquí
│   ├── 1103_A1C1.webp
│   ├── 1105_A1C1.webp
│   └── ...
├── promociones/            ← Fotos de promociones
├── sw.js                   ← Service Worker (offline)
├── productos.xlsx          ← Tu catálogo principal
├── sqlexec.xls             ← Archivo de Goya (reemplazar cada vez)
└── actualizador.py         ← Script de automatización
```

---

## 🔄 Actualizar inventario (flujo normal)

1. Descarga el nuevo `sqlexec.xls` de Goya
2. Reemplaza el `sqlexec.xls` en la carpeta
3. Doble click en `actualizador.py`
4. Revisa el resumen en pantalla
5. Haz push a GitHub → Netlify despliega automáticamente

---

## 🆕 Cuando Goya agrega un producto nuevo

El script lo detecta automáticamente y:
- Lo agrega al Excel con `⚠️ ASIGNAR CATEGORIA`
- Le asigna la imagen `{SKU}_A1C1.webp` automáticamente

**Tú haces:**
1. Descarga la foto, nómbrala `{SKU}_A1C1.webp`, ponla en `/images/`
2. Abre `productos.xlsx` y asigna Categoría y SubCategoría
3. Corre el actualizador de nuevo para regenerar el JSON

---

## 🔥 Agregar una promoción

Edita `app/promociones.json`:

```json
[
  {
    "titulo": "Especial Aceite de Oliva",
    "descripcion": "10% de descuento en aceites seleccionados",
    "imagen": "promo-aceite.jpg"
  }
]
```

Pon la imagen en `/promociones/promo-aceite.jpg` y haz push.

---

## 📱 Instalar en iPhone

1. Abre Safari → ve a tu URL de Netlify
2. Toca el botón de compartir (cuadrado con flecha)
3. "Agregar a pantalla de inicio"
4. Ya tienes el ícono de Ellie en tu iPhone 🐺

---

## 🖼️ Íconos de la app

Necesitas poner en `app/icons/`:
- `logo.png` — tu logo de Ellie (cualquier tamaño)
- `icon-192.png` — 192×192px (para la pantalla de inicio)
- `icon-512.png` — 512×512px (para la splash screen)

Puedes usar tu logo PNG original y redimensionarlo.
