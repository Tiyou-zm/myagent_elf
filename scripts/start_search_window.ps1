param(
    [string]$BindHost = "127.0.0.1",
    [int]$ApiPort = 8000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$dotnetBackendScript = Join-Path $repoRoot "scripts\start_index_service.ps1"
$electronExe = Join-Path $repoRoot "node_modules\electron\dist\electron.exe"
$searchEntry = Join-Path $repoRoot "electron\search-main.js"

function Test-ApiReady {
    param(
        [string]$HostName,
        [int]$Port
    )

    try {
        $response = Invoke-RestMethod -Method Get -Uri "http://$HostName`:$Port/healthz"
        return $response.status -eq "ok"
    }
    catch {
        return $false
    }
}

if (-not (Test-Path $electronExe)) {
    Write-Host "Installing Electron dependencies..."
    & npm install
}

if (-not (Test-ApiReady -HostName $BindHost -Port $ApiPort)) {
    Write-Host "Starting backend at http://$BindHost`:$ApiPort"
    $backendArgs = @(
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $dotnetBackendScript,
        "-BindHost",
        $BindHost,
        "-Port",
        $ApiPort
    )

    Start-Process -FilePath powershell -ArgumentList $backendArgs -WorkingDirectory $repoRoot | Out-Null

    $ready = $false
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-ApiReady -HostName $BindHost -Port $ApiPort) {
            $ready = $true
            break
        }
    }

    if (-not $ready) {
        throw "Backend did not become ready in time."
    }
}

Write-Host "Starting search window..."
Start-Process -FilePath $electronExe -ArgumentList $searchEntry -WorkingDirectory $repoRoot | Out-Null
