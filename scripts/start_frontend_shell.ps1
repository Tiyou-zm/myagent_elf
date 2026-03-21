param(
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 4173
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$playgroundDir = Join-Path $repoRoot "playground"

Write-Host "Starting frontend shell at http://$BindHost`:$Port"
Write-Host "Serving directory: $playgroundDir"

& python -m http.server $Port --bind $BindHost --directory $playgroundDir
