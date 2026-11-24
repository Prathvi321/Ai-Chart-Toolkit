# Local AI Chart Studio - Automated Setup & Runner
# Powered by Qwen 2.5 (3B / 1.9GB) + ai-chart-toolkit
# 100% Local, Offline, Zero API Keys

Set-Location $PSScriptRoot

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " Local AI Chart Studio - Automated Setup and Runner" -ForegroundColor Cyan
Write-Host " Powered by Qwen 2.5 (3B / 1.9GB) + ai-chart-toolkit" -ForegroundColor Green
Write-Host " 100% Local, Offline, Zero API Keys" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python was not found in PATH. Please install Python 3.10+ from python.org" -ForegroundColor Red
    pause
    exit 1
}

# 2. Check dependencies
Write-Host "[1/4] Checking Python dependencies..." -ForegroundColor Gray
$hasPkg = python -c "import ai_chart_toolkit" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing ai-chart-toolkit from PyPI..." -ForegroundColor Yellow
    pip install ai-chart-toolkit
}

# 3. Check Ollama
Write-Host "[2/4] Checking Ollama local runtime..." -ForegroundColor Gray
$ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama"
if (Test-Path "$ollamaPath\ollama.exe") {
    $env:PATH = "$env:PATH;$ollamaPath"
}
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue

if (-not $ollamaCmd) {
    Write-Host "Installing Ollama via winget..." -ForegroundColor Yellow
    winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements
    $env:PATH = "$env:PATH;$ollamaPath"
}

# Check if Ollama is running
$ollamaActive = $false
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method Get -TimeoutSec 2 -ErrorAction Stop
    $ollamaActive = $true
} catch {
    Write-Host "Starting Ollama background daemon..." -ForegroundColor Yellow
    Start-Process -FilePath "$ollamaPath\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# 4. Check Qwen model
Write-Host "[3/4] Checking Qwen 2.5 (3B / 1.9GB) model..." -ForegroundColor Gray
$models = (ollama list) | Out-String
if ($models -notmatch "qwen2.5:3b") {
    Write-Host "Pulling Qwen 2.5 (3B) model (Offline & Free)..." -ForegroundColor Yellow
    ollama pull qwen2.5:3b
}

# 5. Launch Server & Browser
Write-Host "[4/4] Launching Studio Web Interface on http://localhost:8501..." -ForegroundColor Green
Start-Process "http://localhost:8501"
python server.py
