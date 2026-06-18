@echo off
title Interview Practice Coach — Setup
color 0A
echo ============================================================
echo  Interview Practice Coach — First-Time Setup
echo ============================================================
echo.
echo  This will install everything needed to run the app.
echo  It will take 3-5 minutes (downloads ~165MB of AI models).
echo  Please keep this window open until it says "Setup complete!"
echo.

:: ── Check for Python ────────────────────────────────────────────────────────
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=py
    goto :python_found
)
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=python
    goto :python_found
)

color 0C
echo  ERROR: Python is not installed or not in PATH.
echo.
echo  Please follow these steps:
echo    1. Open your browser and go to: https://www.python.org/downloads/
echo    2. Click "Download Python 3.x.x" (the big yellow button)
echo    3. Run the installer
echo    4. IMPORTANT: On the FIRST screen, tick "Add Python to PATH"
echo    5. Complete the installation
echo    6. Come back and double-click Install.bat again
echo.
echo  See TROUBLESHOOTING.md for more help.
echo.
pause
exit /b 1

:python_found
for /f "tokens=2" %%i in ('%PYTHON% --version 2^>^&1') do set PYVER=%%i
echo  Python %PYVER% found. Good to go.
echo.

:: ── Check pip ───────────────────────────────────────────────────────────────
%PYTHON% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo  ERROR: pip is not available. Try running this as Administrator.
    echo  (Right-click Install.bat and select "Run as administrator")
    pause
    exit /b 1
)

:: ── Install packages ─────────────────────────────────────────────────────────
echo  Installing required packages (this may take a minute)...
%PYTHON% -m pip install --upgrade pip --quiet
%PYTHON% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ERROR: Package installation failed.
    echo.
    echo  Common fixes:
    echo    - Check your internet connection
    echo    - Run this as Administrator (right-click -> Run as administrator)
    echo    - If on a corporate network, see TROUBLESHOOTING.md for proxy setup
    echo.
    pause
    exit /b 1
)
echo  Packages installed successfully.
echo.

:: ── Download Whisper model ────────────────────────────────────────────────────
echo  Downloading speech recognition model (Whisper ~75MB)...
echo  (This recognises your voice during the interview)
%PYTHON% -c "from faster_whisper import WhisperModel; WhisperModel('tiny', download_root='models/whisper', device='cpu', compute_type='int8'); print('  Speech recognition model ready.')"
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ERROR: Could not download the Whisper model.
    echo  Check your internet connection and run Install.bat again.
    echo  See TROUBLESHOOTING.md item #4 for more help.
    pause
    exit /b 1
)

:: ── Download Kokoro TTS model ─────────────────────────────────────────────────
echo.
echo  Downloading voice model (Kokoro ~90MB)...
echo  (This is the AI voice that reads questions aloud)
%PYTHON% scripts\download_models.py
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ERROR: Could not download the voice model.
    echo  Check your internet connection and run Install.bat again.
    echo  See TROUBLESHOOTING.md item #4 for more help.
    pause
    exit /b 1
)

:: ── All done ──────────────────────────────────────────────────────────────────
color 0A
echo.
echo ============================================================
echo  Setup complete!
echo.
echo  To start the app: double-click Start.bat
echo.
echo  First time? You will need a free Gemini API key.
echo  Instructions are shown inside the app when it opens.
echo ============================================================
echo.
pause
