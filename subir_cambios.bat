@echo off
echo.
echo ================================================
echo    SUBIENDO CAMBIOS A GITHUB...
echo ================================================
echo.

cd /d "C:\Users\jamil\Jay-APP"

git add .
git commit -m "actualizar app"
git push

echo.
echo ================================================
echo    LISTO! Netlify despliega en 1-2 minutos.
echo ================================================
echo.
pause
