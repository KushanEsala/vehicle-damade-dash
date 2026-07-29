param(
    [switch]$Status,
    [switch]$Remove
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
$scriptPath = Join-Path $projectRoot "scripts\configure_vision_key.py"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Virtual environment not found. Create .venv and install requirements.txt first."
}

$arguments = @($scriptPath)
if ($Status) {
    $arguments += "--status"
}
elseif ($Remove) {
    $arguments += "--remove"
}

& $pythonPath @arguments
exit $LASTEXITCODE
