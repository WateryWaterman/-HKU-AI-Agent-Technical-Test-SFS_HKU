<#
.SYNOPSIS
  跑后端 pytest (86 个测试, 期望 ~11 秒)
.DESCRIPTION
  - 跑 pytest --tb=short -q
  - 输出最后 5 行 + 通过数
.PARAMETER BackendDir
  后端目录, 默认 D:\ProgramData\ArchiTestMajun\fsb-door-check\backend
.EXAMPLE
  powershell -NoProfile -File .\run-tests.ps1
#>
param(
  [string]$BackendDir = "D:\ProgramData\ArchiTestMajun\fsb-door-check\backend"
)
$ErrorActionPreference = "Continue"
if ($PSBoundParameters.ContainsKey('BackendDir')) {
  Set-Location $BackendDir
} elseif ($BackendDir) {
  Set-Location $BackendDir
}
$out = & python -m pytest --tb=short -q 2>&1
$out | Select-Object -Last 5 | ForEach-Object { Write-Output $_ }
$allText = ($out | Out-String)
if ($allText -match "(\d+) passed") {
  Write-Output "---"
  Write-Output "RESULT: $($matches[1]) passed"
} elseif ($allText -match "(\d+) failed") {
  Write-Output "---"
  Write-Output "RESULT: $($matches[1]) failed"
  exit 1
} else {
  Write-Output "---"
  Write-Output "RESULT: unknown"
  exit 1
}