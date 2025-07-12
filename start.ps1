$ErrorActionPreference = "Stop"

Write-Host "Inicializando ambiente..." -ForegroundColor Green

try {
    python --version | Out-Null
} catch {
    Write-Host "Python não instalado ou não está no PATH." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".\Lib")) {
    Write-Host "Criando venv..." -ForegroundColor Yellow
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1

if (Test-Path ".\requirements.txt") {
    Write-Host "Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host "Iniciando aplicação..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "D:\repositorios-github\novela\src\main.py" -WindowStyle Hidden

if ($LASTEXITCODE -ne 0) {
    Write-Host "Application exited with code $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
