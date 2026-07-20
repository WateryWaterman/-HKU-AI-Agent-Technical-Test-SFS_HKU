<#
.SYNOPSIS
  Restart FSB Door Check backend (uvicorn port 8000), wait for health
.DESCRIPTION
  1) Kill python process listening on 8000
  2) Start uvicorn app.main:app --host 127.0.0.1 --port 8000
  3) Poll /health up to 20 seconds
  4) Output JSON: { status, pid, error }
.PARAMETER BackendDir
  Default: D:\ProgramData\ArchiTestMajun\fsb-door-check\backend
#>
param(
  [string]$BackendDir = "D:\ProgramData\ArchiTestMajun\fsb-door-check\backend"
)

$PORT = 8000

# 1. Kill process on 8000
$conns = Get-NetTCPConnection -LocalPort $PORT -State Listen -ErrorAction SilentlyContinue
if ($conns) {
  foreach ($c in $conns) {
    try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction Stop } catch {}
  }
  Start-Sleep -Milliseconds 500
}

# 2. Start uvicorn
if (-not (Test-Path "$BackendDir\app\main.py")) {
  Write-Output '{"status":"fail","error":"backend dir not found"}'
  exit 1
}

$proc = Start-Process -FilePath "python" -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1',"--port",$PORT -WorkingDirectory $BackendDir -WindowStyle Hidden -PassThru

# 3. Poll health
$ok = $false
for ($i = 0; $i -lt 20; $i++) {
  Start-Sleep -Seconds 1
  try {
    $resp = curl.exe -s -m 2 "http://127.0.0.1:$PORT/health" 2>$null
    if ($resp -match '"status"') { $ok = $true; break }
  } catch {}
}

if ($ok) {
  Write-Output ('{"status":"ok","pid":' + $proc.Id + ',"port":' + $PORT + '}')
} else {
  Write-Output ('{"status":"fail","pid":' + $proc.Id + ',"error":"health check timeout"}')
}