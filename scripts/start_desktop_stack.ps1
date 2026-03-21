param(
    [string]$BindHost = "127.0.0.1",
    [int]$ApiPort = 8000,
    [switch]$Reload
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$runtimeDir = Join-Path $repoRoot "data\runtime"
$statePath = Join-Path $runtimeDir "desktop-stack.json"
$backendScript = Join-Path $repoRoot "scripts\start_index_service.ps1"

function Get-ListeningPid {
    param(
        [int]$Port
    )

    $match = netstat -ano | Select-String "127.0.0.1:$Port\s+0.0.0.0:0\s+LISTENING"
    if ($null -eq $match) {
        return $null
    }

    $parts = ($match.Line -split "\s+") | Where-Object { $_ }
    return [int]$parts[-1]
}

New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

if (Test-Path $statePath) {
    $existing = Get-Content $statePath -Raw | ConvertFrom-Json
    $apiAlive = $false
    $electronAlive = $false

    if ($existing.api_pid) {
        $apiAlive = $null -ne (Get-Process -Id $existing.api_pid -ErrorAction SilentlyContinue)
    }
    if ($existing.electron_pid) {
        $electronAlive = $null -ne (Get-Process -Id $existing.electron_pid -ErrorAction SilentlyContinue)
    }

    if ($apiAlive -or $electronAlive) {
        throw "Desktop stack already seems to be running. Use .\scripts\stop_desktop_stack.ps1 first."
    }

    Remove-Item $statePath -Force
}

$appDir = Join-Path $repoRoot "src"
$electronExe = Join-Path $repoRoot "node_modules\electron\dist\electron.exe"
if (-not (Test-Path $electronExe)) {
    Write-Host "Installing Electron dependencies..."
    & npm install
}

Write-Host "Starting backend at http://$BindHost`:$ApiPort"
$backendArgs = @(
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $backendScript,
    "-BindHost",
    $BindHost,
    "-Port",
    $ApiPort
)

if ($Reload) {
    $backendArgs += "-Reload"
}

$apiProc = Start-Process -FilePath powershell -ArgumentList $backendArgs -WorkingDirectory $repoRoot -PassThru

$healthReady = $false
for ($i = 0; $i -lt 40; $i++) {
    try {
        $response = Invoke-RestMethod -Method Get -Uri "http://$BindHost`:$ApiPort/healthz"
        if ($response.status -eq "ok") {
            $healthReady = $true
            break
        }
    }
    catch {
        Start-Sleep -Milliseconds 500
    }
}

if (-not $healthReady) {
    Stop-Process -Id $apiProc.Id -Force -ErrorAction SilentlyContinue
    throw "Backend health check did not become ready in time."
}

$apiListenerPid = Get-ListeningPid -Port $ApiPort
if ($null -eq $apiListenerPid) {
    Stop-Process -Id $apiProc.Id -Force -ErrorAction SilentlyContinue
    throw "Backend became healthy, but no listening PID was found for port $ApiPort."
}

Write-Host "Starting Electron shell..."
$electronProc = Start-Process -FilePath $electronExe -ArgumentList "." -WorkingDirectory $repoRoot -PassThru

$state = @{
    api_pid = $apiListenerPid
    electron_pid = $electronProc.Id
    api_url = "http://$BindHost`:$ApiPort"
    started_at = (Get-Date).ToString("s")
}

$state | ConvertTo-Json | Set-Content -Path $statePath -Encoding UTF8

Write-Host ""
Write-Host "Desktop stack started."
Write-Host "Backend PID: $apiListenerPid"
Write-Host "Electron PID: $($electronProc.Id)"
Write-Host "State file: $statePath"
