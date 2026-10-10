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
echo Actualizando a Ellie...
scp "C:\Users\jamil\Jay-APP\app\productos.json" jamil@177.7.46.93:~/Ellie/
if errorlevel 1 goto ellie_error
ssh jamil@177.7.46.93 "cd ~/Ellie && venv/bin/python catalogo.py cargar productos.json"
goto ellie_fin
:ellie_error
echo AVISO: no se pudo actualizar a Ellie
:ellie_fin

echo.
echo Enviando notificacion a usuarios...
node enviar_notificacion.js "Jay App" "Inventario Actualizado Hoy"

echo.
echo ================================================
echo    LISTO! La app se actualiza en 1-2 minutos.
echo ================================================
echo.
pause
