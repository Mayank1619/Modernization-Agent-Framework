param(
    [int]$ApiPort = 8000,
    [int]$UiPort = 5173
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$apiCommand = "Set-Location '$repoRoot'; & '$pythonExe' -m uvicorn agent_visual_api:app --reload --port $ApiPort"
$uiCommand = "Set-Location '$repoRoot\agent-visual-ui'; npm run dev -- --host 127.0.0.1 --port $UiPort"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiCommand | Out-Null
Start-Process powershell -ArgumentList "-NoExit", "-Command", $uiCommand | Out-Null

Write-Host "Started dashboard services in new PowerShell windows."
Write-Host "API health: http://127.0.0.1:$ApiPort/api/health"
Write-Host "UI: http://127.0.0.1:$UiPort"
