$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ProjectDir

$Python = Join-Path $ProjectDir ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    Write-Host "Virtual environment not found. Run the setup commands in README.md first."
    exit 1
}

Write-Host "Starting training with validation after every epoch."
Write-Host "Open another PowerShell window and run .\watch_training.ps1 to watch charts."
& $Python ".\train.py" --confirm-train

