# Life Inbox - Windows PowerShell Setup Script
# Usage: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Life Inbox - Local Development Setup   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Create virtual environment (.venv) if one doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "`n[1/5] Creating Python virtual environment (.venv)..." -ForegroundColor Yellow
    $pythonCmd = if (Get-Command py -ErrorAction SilentlyContinue) { "py -3.11" } elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
    & $pythonCmd -m venv .venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "`n[1/5] Virtual environment (.venv) already exists." -ForegroundColor Green
}

$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"

# 2. Install requirements.txt
Write-Host "`n[2/5] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -r requirements.txt --quiet
Write-Host "Dependencies successfully installed." -ForegroundColor Green

# 3. Copy .env.example to .env if .env doesn't exist
Write-Host "`n[3/5] Checking environment configuration (.env)..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example." -ForegroundColor Green
} else {
    Write-Host ".env already exists." -ForegroundColor Green
}

# 4. Run database migrations (alembic upgrade head)
Write-Host "`n[4/5] Running database migrations (alembic upgrade head)..." -ForegroundColor Yellow
& $venvPython -m alembic upgrade head
Write-Host "Database migrations up to date." -ForegroundColor Green

# 5. Instructions
Write-Host "`n[5/5] Setup Complete! 🎉" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Configure your NVIDIA NIM API key:" -ForegroundColor White
Write-Host "   Open .env and set: NVIDIA_API_KEY=nvapi-your-key-here" -ForegroundColor Yellow
Write-Host "   (If left blank, Life Inbox runs in offline mode with deterministic fallback)" -ForegroundColor Gray
Write-Host "2. Start the development server:" -ForegroundColor White
Write-Host "   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000" -ForegroundColor Green
Write-Host "3. Open your browser:" -ForegroundColor White
Write-Host "   http://localhost:8000" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
