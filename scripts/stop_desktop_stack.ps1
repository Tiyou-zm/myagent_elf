Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$statePath = Join-Path $repoRoot "data\runtime\desktop-stack.json"

function Get-ListeningPids {
    param(
        [int]$Port
    )

    $pids = @()

    if (Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue) {
        $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        foreach ($connection in $connections) {
            if ($connection.OwningProcess) {
                $pids += [int]$connection.OwningProcess
            }
        }
    }

    if (-not $pids) {
        $matches = netstat -ano | Select-String ":$Port\s+.*LISTENING"
        foreach ($match in $matches) {
            $parts = ($match.Line -split "\s+") | Where-Object { $_ }
            if ($parts.Count -ge 5) {
                $pids += [int]$parts[-1]
            }
        }
    }

    return $pids | Select-Object -Unique
}

function Stop-TrackedProcess {
    param(
        [int]$TargetProcessId
    )

    if (-not $TargetProcessId) {
        return
    }

    $process = Get-Process -Id $TargetProcessId -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        return
    }

    Stop-Process -Id $TargetProcessId -Force -ErrorAction SilentlyContinue
    Wait-Process -Id $TargetProcessId -Timeout 5 -ErrorAction SilentlyContinue
}

if (-not (Test-Path $statePath)) {
    Write-Host "No desktop stack state file found."
    return
}

$state = Get-Content $statePath -Raw | ConvertFrom-Json

foreach ($targetPid in @($state.electron_pid, $state.api_pid)) {
    Stop-TrackedProcess -TargetProcessId $targetPid
}

$apiPort = [int]([Uri]$state.api_url).Port
for ($attempt = 0; $attempt -lt 6; $attempt++) {
    $listenerPids = Get-ListeningPids -Port $apiPort
    if (-not $listenerPids) {
        break
    }

    foreach ($targetPid in $listenerPids) {
        Stop-TrackedProcess -TargetProcessId $targetPid
    }

    Start-Sleep -Milliseconds 400
}

$remainingListeners = Get-ListeningPids -Port $apiPort
if ($remainingListeners) {
    throw "Desktop stack stop timed out. Port $apiPort is still listening on PID(s): $($remainingListeners -join ', ')."
}

Remove-Item $statePath -Force
Write-Host "Desktop stack stopped."
