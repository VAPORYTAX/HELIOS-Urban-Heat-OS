param(
  [string]$Backend = 'http://127.0.0.1:8080/api/v1',
  [string]$Output
)

$ErrorActionPreference='Stop'
$Root = Split-Path -Parent $PSScriptRoot
if(-not $Output){ $Output = Join-Path $Root 'frontend\public\data\verified_snapshot.json' }

function Get-Json([string]$Path){
  Invoke-RestMethod -Uri ($Backend.TrimEnd('/') + $Path) -TimeoutSec 30
}

Write-Host "HELIOS — EXPORT VERIFIED JUDGING SNAPSHOT" -ForegroundColor Cyan
Write-Host "Backend: $Backend"

$system = Get-Json '/system/status'
if($system.status -ne 'ready' -or -not $system.database.ready){ throw 'Backend is not in a verified ready state.' }

$endpoints = [ordered]@{}
function Capture([string]$Key,[string]$Path){
  Write-Host "Capture $Path" -ForegroundColor DarkCyan
  $endpoints[$Key] = Get-Json $Path
}

Capture '/system/status' '/system/status'
Capture '/system/capabilities' '/system/capabilities'
Capture '/provider-ops/metrics' '/provider-ops/metrics'
Capture '/spatial/cells?area_id=phx-downtown' '/spatial/cells?area_id=phx-downtown'
Capture '/interventions/provider-native/candidates?area_id=phx-downtown' '/interventions/provider-native/candidates?area_id=phx-downtown'
Capture '/optimizer/provider-native/latest?area_id=phx-downtown' '/optimizer/provider-native/latest?area_id=phx-downtown'
Capture '/quality/latest?area_id=phx-downtown' '/quality/latest?area_id=phx-downtown'
Capture '/context/packets?area_id=phx-downtown' '/context/packets?area_id=phx-downtown'
Capture '/thermalway/accessibility' '/thermalway/accessibility'
Capture '/thermalway/critical-journeys' '/thermalway/critical-journeys'
Capture '/scenarios?area_id=phx-downtown' '/scenarios?area_id=phx-downtown'

try { Capture '/decision-science/latest?area_id=phx-downtown' '/decision-science/latest?area_id=phx-downtown' } catch { Write-Warning 'Decision science snapshot unavailable; leaving it out.' }
try { Capture '/agents/runs?area_id=phx-downtown' '/agents/runs?area_id=phx-downtown' } catch { Write-Warning 'Agent runs snapshot unavailable; leaving it out.' }
try { Capture '/agents/recommendations/latest?area_id=phx-downtown' '/agents/recommendations/latest?area_id=phx-downtown' } catch { Write-Warning 'Agent recommendation snapshot unavailable; leaving it out.' }

$scenarios = $endpoints['/scenarios?area_id=phx-downtown']
foreach($scenario in @($scenarios)){
  if($scenario.id){
    $key = "/scenarios/$($scenario.id)/result"
    try { Capture $key $key } catch { Write-Warning "Scenario result unavailable: $($scenario.id)" }
  }
}

$payload = [ordered]@{
  schema='helios_verified_snapshot_v1'
  generated_at=(Get-Date).ToUniversalTime().ToString('o')
  area_id='phx-downtown'
  status='verified_snapshot'
  note='Read-only capture from a locally verified HELIOS backend. Never claim this snapshot is live compute.'
  endpoints=$endpoints
}

$dir=Split-Path -Parent $Output
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$payload | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $Output -Encoding UTF8

Write-Host "PASS: verified snapshot written" -ForegroundColor Green
Write-Host $Output -ForegroundColor Yellow
Write-Host "Snapshot time: $($payload.generated_at)" -ForegroundColor Yellow
