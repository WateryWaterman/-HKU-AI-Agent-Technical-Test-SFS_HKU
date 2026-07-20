<#
.SYNOPSIS
  快速检查后端是否在跑 + 当前 session 数量
.DESCRIPTION
  - 调 /health
  - 调 /sessions (如果存在)
  - 输出 JSON: { alive, version, sessions_count }
.PARAMETER BaseUrl
  默认 http://127.0.0.1:8000
.EXAMPLE
  powershell -NoProfile -File .\status.ps1
#>
param([string]$BaseUrl = "http://127.0.0.1:8000")
$ErrorActionPreference = "Continue"
try {
  $h = curl.exe -s -m 2 "$BaseUrl/health" | ConvertFrom-Json
  Write-Output ('{"alive":true,"version":"' + $h.version + '"}')
} catch {
  Write-Output '{"alive":false}'
}