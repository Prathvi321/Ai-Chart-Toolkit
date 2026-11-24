@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Local AI Chart Studio (Qwen 2.5 + ai-chart-toolkit)

echo =====================================================================
echo  Local AI Chart Studio - Automated Setup and Runner
echo  Powered by Qwen 2.5 (3B / 1.9GB) + ai-chart-toolkit
echo  100%% Local, Offline, Zero API Keys
echo =====================================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found in your PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

:: 2. Ensure ai-chart-toolkit and dependencies are installed
echo [1/4] Checking Python dependencies...
python -c "import ai_chart_toolkit" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing ai-chart-toolkit from PyPI...
    pip install ai-chart-toolkit
)

:: 3. Check Ollama
echo [2/4] Checking Ollama local runtime...
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Ollama"
    ) else (
        echo Ollama was not found on your system.
        echo Attempting automatic installation via winget...
        winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements
        set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Ollama"
    )
)

:: Check if Ollama server is running
curl -s http://127.0.0.1:11434/api/tags >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Starting Ollama local background service...
    start "" /b ollama serve
    timeout /t 3 >nul
)

:: 4. Ensure Qwen 2.5 (3B) is pulled
echo [3/4] Checking Qwen 2.5 model weights (~1.9 GB)...
ollama list | findstr "qwen2.5:3b" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Downloading Qwen 2.5 (3B) local model (no account or API key needed)...
    ollama pull qwen2.5:3b
)

:: 5. Launch Web Studio & Open Browser
echo [4/4] Launching Local AI Chart Studio on http://localhost:8501...
start "" http://localhost:8501
python server.py

pause
