@echo off
echo ============================================
echo   Copa Mundial FIFA 2026 - Actualizar datos
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 ( set PYTHON=py -3 ) else ( set PYTHON=python )

cd /d %~dp0

echo [1/3] Consultando API ESPN (sin navegador)...
%PYTHON% scraper.py
if %errorlevel% neq 0 (
    echo ERROR: No se pudo consultar la API de ESPN.
    pause
    exit /b 1
)

echo.
echo [2/3] Regenerando app movil...
%PYTHON% build_mobile.py

echo.
echo [3/3] Publicando en GitHub/Railway...
git add matches.json FIFA2026_movil.html
for /f "tokens=*" %%i in ('gh auth token') do set TOKEN=%%i
git commit -m "Actualizar resultados %date%"
git push https://%TOKEN%@github.com/murbina83-web/mundial-fifa-2026.git master

echo.
echo ============================================
echo   Listo! En ~2 minutos Railway se actualiza:
echo   https://mundial-fifa-2026-production-bea6.up.railway.app
echo ============================================
pause
