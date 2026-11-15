@echo off
cd /d "%~dp0"
echo === Instalacja Sztab-SAR ===
python tools\setup_sztab.py %*
if errorlevel 1 (
    echo Blad instalacji. Sprawdz czy Python 3.10+ jest zainstalowany.
    pause
    exit /b 1
)
echo.
echo Uruchamiam Sztab-SAR...
python app.py
pause
