Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

if (-not (Test-Path (Join-Path $repoRoot "node_modules"))) {
    Write-Host "Installing Electron dependencies..."
    & npm install
}

Write-Host "Starting Electron shell..."
& npm run electron
