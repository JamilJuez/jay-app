@echo off
echo.
echo ================================================
echo    ACTUALIZANDO PRECIOS...
echo ================================================
echo.

cd /d "C:\Users\jamil\Jay-APP"

echo Corriendo actualizador de precios...
python actualizar_precios.py

echo.
echo Subiendo a GitHub...
git add .
git commit -m "actualizar precios"
git push

echo.
echo ================================================
echo    LISTO! La app se actualiza en 1-2 minutos.
echo ================================================
echo.
pause
