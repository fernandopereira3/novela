##Start-Process -FilePath "python" -ArgumentList "D:\repositorios-github\novela\main.py" -WindowStyle Hidden

$ErrorActionPreference = "Stop"


Write-Host "Initializing novela environment..." -ForegroundColor Green

try {
    $pythonVersion = python --version
    Write-Host "Python nao encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH. Please install Python first." -ForegroundColor Red
    exit 
}

if (-not (Test-Path "\Lib")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv .
} else {
    Write-Host "Ambiente virtual já existe." -ForegroundColor Green
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\Scripts\Activate.ps1

if (Test-Path ".\requirements.txt") {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host "Starting novela application..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "D:\repositorios-github\novela\main.py" -WindowStyle Hidden

if ($LASTEXITCODE -ne 0) {
    Write-Host "Application exited with code $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
