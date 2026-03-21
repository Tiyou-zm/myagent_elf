Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$statePath = Join-Path $repoRoot "data\runtime\desktop-stack.json"

function Get-ListeningPids {
    param(
        [int]$Port
    )

    $matches = netstat -ano | Select-String "127.0.0.1:$Port\s+0.0.0.0:0\s+LISTENING"
    $pids = @()
    foreach ($match in $matches) {
        $parts = ($match.Line -split "\s+") | Where-Object { $_ }
        $pids += [int]$parts[-1]
    }
    return $pids | Select-Object -Unique
}

if (-not (Test-Path $statePath)) {
    Write-Host "No desktop stack state file found."
    return
}

$state = Get-Content $statePath -Raw | ConvertFrom-Json

foreach ($targetPid in @($state.electron_pid, $state.api_pid)) {
    if (-not $targetPid) {
        continue
    }

    $process = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
    if ($null -ne $process) {
        Stop-Process -Id $targetPid -Force
    }
}

$apiPort = [int]([Uri]$state.api_url).Port
foreach ($targetPid in Get-ListeningPids -Port $apiPort) {
    $process = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
    if ($null -ne $process) {
        Stop-Process -Id $targetPid -Force
    }
}

Remove-Item $statePath -Force
Write-Host "Desktop stack stopped."
