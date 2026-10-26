@echo off
setlocal
title Croplytics - Smart Agriculture Assistant Launcher
color 0A

echo ============================================================
echo        CROPLYTICS - SMART AGRICULTURE ASSISTANT
echo ============================================================
echo.

REM Step 1: Check Python
echo [1/5] Checking Python installation...

python --version
if errorlevel 1 (
color 0C
echo [ERROR] Python is not installed or is not on PATH.
echo Install Python 3.10, 3.11, or 3.12 from:
echo https://www.python.org/downloads/
echo Enable Add Python to PATH during installation.
pause
exit /b 1
)

REM Step 2: Create virtual environment if needed
echo.
echo [2/5] Checking virtual environment...

if not exist ".venv\Scripts\python.exe" (
echo Creating virtual environment...
python -m venv .venv

```
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)
```

)

REM Step 3: Activate virtual environment
echo.
echo [3/5] Activating virtual environment...

call ".venv\Scripts\activate.bat"

if errorlevel 1 (
echo [ERROR] Failed to activate virtual environment.
pause
exit /b 1
)

REM Step 4: Install dependencies
echo.
echo [4/5] Installing project dependencies...

if not exist "requirements.txt" (
echo [ERROR] requirements.txt was not found.
pause
exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 (
echo [ERROR] Failed to update pip.
pause
exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
echo [ERROR] Dependency installation failed.
pause
exit /b 1
)

REM Train model only if the model file is missing
if not exist "models\crop_yield_model.joblib" (
if exist "models\train_yield_model.py" (
echo.
echo Training crop yield model...
python "models\train_yield_model.py"

```
    if errorlevel 1 (
        echo [ERROR] Model training failed.
        pause
        exit /b 1
    )
) else (
    echo [WARNING] Model training script was not found.
)
```

)

REM Step 5: Start Flask
echo.
echo [5/5] Starting Croplytics...
echo.
echo Website: http://127.0.0.1:5000
echo Keep this window open while using the application.
echo Press CTRL+C to stop the server.
echo.

REM Start a background process that waits for Flask to respond
start "" powershell -NoProfile -ExecutionPolicy Bypass -Command "$url='http://127.0.0.1:5000'; for ($i=0; $i -lt 60; $i++) { try { $r=Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { Start-Process $url; exit 0 } } catch {}; Start-Sleep -Seconds 1 }; Write-Host 'The website did not respond within 60 seconds.'"

python app.py

if errorlevel 1 (
echo.
echo [ERROR] Flask stopped with an error.
pause
)

endlocal
