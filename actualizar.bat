@echo off
echo ============================================
echo   Copa Mundial FIFA 2026 - Actualizar datos
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 ( set PYTHON=py -3 ) else ( set PYTHON=python )

echo [1/3] Scrapeando datos frescos de FIFA.com...
cd /d %~dp0
%PYTHON% scraper.py
if %errorlevel% neq 0 (
    echo [ERROR] Fallo el scraping. Verifica tu conexion a internet.
    pause
    exit /b 1
)

echo.
echo [2/3] Regenerando app movil...
%PYTHON% build_mobile.py

echo.
echo [3/3] Publicando en Railway (git push)...
git add matches.json FIFA2026_movil.html
git commit -m "Actualizar resultados FIFA %date% %time:~0,5%"
git push

echo.
echo ============================================
echo   Listo! En ~2 minutos el sitio estara
echo   actualizado en railway.app
echo ============================================
pause
