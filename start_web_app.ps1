$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Virtual environment not found. Run the setup commands in WEB_APP_SETUP.md first."
}

$backendLog = Join-Path $root "backend-api.log"
$backendErrorLog = Join-Path $root "backend-api-error.log"
$frontendLog = Join-Path $root "frontend-web.log"
$frontendErrorLog = Join-Path $root "frontend-web-error.log"

$apiRunning = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$webRunning = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue

if (-not $apiRunning) {
    Start-Process -FilePath $python -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000" -WorkingDirectory $root -RedirectStandardOutput $backendLog -RedirectStandardError $backendErrorLog -WindowStyle Hidden
}
if (-not $webRunning) {
    Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" -WorkingDirectory (Join-Path $root "frontend") -RedirectStandardOutput $frontendLog -RedirectStandardError $frontendErrorLog -WindowStyle Hidden
}

Write-Host "Starting the API and web interface..."
Write-Host "Open: http://localhost:3000"
Write-Host "API log: $backendLog"
Write-Host "Web log: $frontendLog"
