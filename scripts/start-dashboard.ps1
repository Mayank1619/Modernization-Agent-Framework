param(
    [int]$ApiPort = 8000,
    [int]$UiPort = 5173
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

function Get-BootstrapPythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @("py", "-3")
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @("python")
    }
    throw "Python executable not found. Install Python 3.11+ and retry."
}

if (-not (Test-Path $venvPython)) {
    Write-Host "[setup] Creating local .venv..."
    $bootstrap = Get-BootstrapPythonCommand
    if ($bootstrap.Length -eq 1) {
        & $bootstrap[0] -m venv (Join-Path $repoRoot ".venv")
    }
    else {
        & $bootstrap[0] $bootstrap[1] -m venv (Join-Path $repoRoot ".venv")
    }
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPython)) {
        throw "Failed to create virtual environment at $venvPython"
    }
}

$pythonExe = $venvPython

Write-Host "[setup] Validating backend dependencies..."
& $pythonExe -c "import fastapi, uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[setup] Installing Python requirements..."
    & $pythonExe -m pip install -r (Join-Path $repoRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install Python requirements."
    }
}

$uiRoot = Join-Path $repoRoot "agent-visual-ui"
$viteCmd = Join-Path $uiRoot "node_modules\.bin\vite.cmd"

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm not found. Install Node.js 18+ and retry."
}

if (-not (Test-Path $viteCmd)) {
    Write-Host "[setup] Installing UI dependencies..."
    Push-Location $uiRoot
    try {
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw "npm install failed for agent-visual-ui"
        }
    }
    finally {
        Pop-Location
    }
}

$apiCommand = "Set-Location '$repoRoot'; & '$pythonExe' -m uvicorn agent_visual_api:app --reload --port $ApiPort"
$uiCommand = "Set-Location '$repoRoot\agent-visual-ui'; npm run dev -- --host 127.0.0.1 --port $UiPort"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiCommand | Out-Null
Start-Process powershell -ArgumentList "-NoExit", "-Command", $uiCommand | Out-Null

Write-Host "Started dashboard services in new PowerShell windows."
Write-Host "API health: http://127.0.0.1:$ApiPort/api/health"
Write-Host "UI: http://127.0.0.1:$UiPort"
