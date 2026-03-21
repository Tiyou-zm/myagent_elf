param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$RootPath = "",
    [string]$ContentQuery = "Python",
    [string]$FileQuery = "README"
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not $RootPath) {
    $RootPath = $repoRoot
}

function Invoke-JsonPost {
    param(
        [string]$Url,
        [object]$Body
    )

    return Invoke-RestMethod `
        -Method Post `
        -Uri $Url `
        -ContentType "application/json; charset=utf-8" `
        -Body ($Body | ConvertTo-Json -Depth 5)
}

try {
    $health = Invoke-RestMethod -Method Get -Uri "$BaseUrl/healthz"
}
catch {
    throw "Health check failed. Make sure the FastAPI service is running at $BaseUrl. $($_.Exception.Message)"
}

Write-Host ""
Write-Host "== Health =="
$health | ConvertTo-Json -Depth 5

$indexResult = Invoke-JsonPost -Url "$BaseUrl/api/v1/index" -Body @{
    roots = @($RootPath)
}

Write-Host ""
Write-Host "== Index =="
$indexResult | ConvertTo-Json -Depth 5

$contentResult = Invoke-JsonPost -Url "$BaseUrl/api/v1/search" -Body @{
    query = $ContentQuery
    limit = 3
}

Write-Host ""
Write-Host "== Content Search =="
$contentResult | ConvertTo-Json -Depth 5

$fileResult = Invoke-JsonPost -Url "$BaseUrl/api/v1/search/files" -Body @{
    query = $FileQuery
    limit = 3
}

Write-Host ""
Write-Host "== File Search =="
$fileResult | ConvertTo-Json -Depth 5

$rootsResult = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/v1/roots"

Write-Host ""
Write-Host "== Roots =="
$rootsResult | ConvertTo-Json -Depth 5
