param(
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$Reload
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$appDir = Join-Path $repoRoot "src"

$arguments = @(
    "-m",
    "uvicorn",
    "index_service.main:app",
    "--app-dir",
    $appDir,
    "--host",
    $BindHost,
    "--port",
    $Port
)

if ($Reload) {
    $arguments += "--reload"
}

Write-Host "Starting index service at http://$BindHost`:$Port"
Write-Host "App dir: $appDir"

& python @arguments
