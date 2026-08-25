$ErrorActionPreference = "Stop"
$Root = "D:\HELIOS"
$Frontend = Join-Path $Root "frontend"
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$NodeDir = "C:\Program Files\nodejs"
$Npm = Join-Path $NodeDir "npm.cmd"
$ApiBase = "http://127.0.0.1:8080"
$WebBase = "http://127.0.0.1:3000"
$env:Path = "$NodeDir;$env:Path"

function Wait-Http([string]$Uri, [int]$Seconds = 45) {
    $until = (Get-Date).AddSeconds($Seconds)
    do {
        try { if ((Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec 3).StatusCode -eq 200) { return $true } } catch {}
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $until)
    return $false
}

function Assert-Http([string]$Uri) {
    if (-not (Wait-Http $Uri 10)) { throw "Readiness check failed: $Uri" }
    Write-Host "  OK  $Uri" -ForegroundColor Green
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " HELIOS PRODUCTION STARTUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
if (-not (Test-Path -LiteralPath $Python)) { throw "Python environment missing: $Python" }
if (-not (Test-Path -LiteralPath $Npm)) { throw "Node/npm missing: install Node.js LTS" }

$container = docker ps -a --filter "name=^/helios-postgis$" --format "{{.Status}}"
if (-not $container) { throw "Docker container helios-postgis was not found" }
if ($container -notmatch "^Up") { docker start helios-postgis | Out-Null }
$healthy = $false
for ($i=0; $i -lt 60; $i++) {
    $state = docker inspect --format "{{.State.Health.Status}}" helios-postgis 2>$null
    if ($state -eq "healthy") { $healthy = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $healthy) { throw "PostGIS did not become healthy" }
Write-Host "  OK  PostgreSQL/PostGIS healthy" -ForegroundColor Green

try {
    $models = Invoke-RestMethod -Uri "http://127.0.0.1:1235/api/v0/models" -TimeoutSec 5
    $gemma = $models.data | Where-Object { $_.id -match "gemma.*4.*12b|helios-gemma4" } | Select-Object -First 1
    if ($gemma) { Write-Host "  OK  LM Studio Gemma ready: $($gemma.id)" -ForegroundColor Green }
    else { Write-Host "  CHECK  LM Studio reachable; Gemma 4 12B not reported" -ForegroundColor Yellow }
} catch { Write-Host "  CHECK  LM Studio unavailable; fallback will remain explicit" -ForegroundColor Yellow }

if (-not (Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $Python -ArgumentList @("-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8080") -WorkingDirectory $Root -WindowStyle Hidden
}
Assert-Http "$ApiBase/api/v1/health"

Push-Location $Frontend
try { & $Npm run build; if ($LASTEXITCODE -ne 0) { throw "Frontend production build failed" } } finally { Pop-Location }
if (-not (Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $Npm -ArgumentList @("run","start") -WorkingDirectory $Frontend -WindowStyle Hidden
}
Assert-Http $WebBase

$apis = @(
    "/api/v1/system/status", "/api/v1/system/capabilities", "/api/v1/provider-ops/metrics",
    "/api/v1/spatial/cells?area_id=phx-downtown", "/api/v1/interventions/provider-native/candidates?area_id=phx-downtown",
    "/api/v1/optimizer/provider-native/latest?area_id=phx-downtown", "/api/v1/quality/latest?area_id=phx-downtown",
    "/api/v1/context/packets?area_id=phx-downtown"
)
foreach ($path in $apis) { Assert-Http "$ApiBase$path" }
foreach ($page in @("/","/atlas","/thermalway","/interventions","/investment","/evidence","/ai","/system")) { Assert-Http "$WebBase$page" }

Write-Host "`nHELIOS READY" -ForegroundColor Green
Write-Host "API      $ApiBase/docs"
Write-Host "Frontend $WebBase"
Start-Process $WebBase
