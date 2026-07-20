<#
.SYNOPSIS
  对前端三个 JS 文件做 node --check 语法检查
.DESCRIPTION
  检查 app.js / viewer.js / api.js 语法
  输出每个文件 OK/FAIL 和总体 JSON: { ok, files: {name:"ok"|"fail:..."} }
.EXAMPLE
  powershell -NoProfile -File .\check-frontend.ps1
#>
$ErrorActionPreference = "Continue"
$Frontend = "D:\ProgramData\ArchiTestMajun\fsb-door-check\frontend\src"
$files = @("app.js", "viewer.js", "api.js")
$result = @{}
$allOk = $true
foreach ($f in $files) {
  $path = Join-Path $Frontend $f
  if (-not (Test-Path $path)) {
    $result[$f] = "fail: file not found"
    $allOk = $false
    continue
  }
  $err = node --check $path 2>&1
  if ($LASTEXITCODE -eq 0) {
    $result[$f] = "ok"
  } else {
    $result[$f] = "fail: $err"
    $allOk = $false
  }
}
Write-Output ($result | ConvertTo-Json -Compress)
Write-Output ("---")
Write-Output ("overall: $(if ($allOk) {'OK'} else {'FAIL'})")
if (-not $allOk) { exit 1 }