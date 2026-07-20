<#
.SYNOPSIS
  清理后端所有 session (开发环境会话堆积时使用)
.DESCRIPTION
  - 调 /sessions 拿到所有 sid (如果端点存在)
  - 逐个 DELETE /model/session/<sid>
  - 输出清理数量
.PARAMETER BaseUrl
  默认 http://127.0.0.1:8000
.EXAMPLE
  powershell -NoProfile -File .\clear-sessions.ps1
#>
param([string]$BaseUrl = "http://127.0.0.1:8000")
$ErrorActionPreference = "Continue"
try {
  $list = curl.exe -s "$BaseUrl/sessions" | ConvertFrom-Json
  $count = 0
  foreach ($s in $list) {
    try {
      curl.exe -s -X DELETE "$BaseUrl/model/session/$($s.id)" | Out-Null
      $count++
    } catch { }
  }
  Write-Output ('{"cleared":' + $count + '}')
} catch {
  Write-Output '{"error":"sessions endpoint not found"}'
}