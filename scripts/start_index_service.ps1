param(
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$Reload
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$appDir = Join-Path $repoRoot "src"
$localEnvPath = Join-Path $repoRoot ".env.local"

if (Test-Path $localEnvPath) {
    Get-Content $localEnvPath | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) {
            return
        }

        $parts = $line -split "=", 2
        if ($parts.Length -ne 2) {
            return
        }

        $name = $parts[0].Trim()
        $value = $parts[1].Trim()
        [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

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
if (Test-Path $localEnvPath) {
    Write-Host "Loaded local env from: $localEnvPath"
}

& python @arguments
