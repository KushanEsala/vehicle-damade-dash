$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $ProjectDir

$TensorBoard = Join-Path $ProjectDir ".venv\Scripts\tensorboard.exe"
if (-not (Test-Path -LiteralPath $TensorBoard)) {
    Write-Host "TensorBoard not found. Activate the environment and run:"
    Write-Host "pip install -r requirements.txt"
    exit 1
}

Write-Host "Opening live training dashboard at http://localhost:6006"
Start-Process "http://localhost:6006"
& $TensorBoard --logdir ".\runs" --port 6006
