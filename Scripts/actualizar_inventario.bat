@echo off
echo.
echo ================================================
echo    ACTUALIZANDO INVENTARIO...
echo ================================================
echo.

cd /d "C:\Users\jamil\Jay-APP"

echo Corriendo actualizador...
python actualizador.py

echo.
echo Subiendo a GitHub...
git add .
git commit -m "actualizar inventario"
git push

echo.
echo Enviando notificacion a usuarios...
node enviar_notificacion.js "Jay App" "Inventario Actualizado Hoy"

echo.
echo ================================================
echo    LISTO! La app se actualiza en 1-2 minutos.
echo ================================================
echo.
pause
