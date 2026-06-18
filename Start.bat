@echo off
title Interview Practice Coach
color 0A
echo ============================================================
echo  Interview Practice Coach
echo ============================================================
echo.
echo  Starting... your browser will open automatically.
echo.
echo  IMPORTANT: Keep this window open while you use the app.
echo             Close it when you are done with your session.
echo.

:: Detect Python
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=py
    goto :run
)
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=python
    goto :run
)

color 0C
echo  ERROR: Python not found.
echo  Please run Install.bat first.
pause
exit /b 1

:run
%PYTHON% app.py

if %errorlevel% neq 0 (
    echo.
    color 0C
    echo  Something went wrong. Common fixes:
    echo.
    echo  1. Run Install.bat again (models may be incomplete)
    echo  2. Check TROUBLESHOOTING.md for your specific error
    echo  3. Make sure your internet connection is working
    echo.
    echo  If the error mentions "port", try closing any other app
    echo  windows and running Start.bat again.
    echo.
    pause
)
