Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$statePath = Join-Path $repoRoot "data\runtime\wpf-pet.json"

if (-not (Test-Path $statePath)) {
    Write-Host "No WPF pet state file found."
    return
}

$state = Get-Content $statePath -Raw | ConvertFrom-Json

if ($state.pid) {
    $process = Get-Process -Id $state.pid -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $state.pid -Force -ErrorAction SilentlyContinue
        Wait-Process -Id $state.pid -Timeout 5 -ErrorAction SilentlyContinue
    }
}

Remove-Item $statePath -Force
Write-Host "WPF pet shell stopped."
