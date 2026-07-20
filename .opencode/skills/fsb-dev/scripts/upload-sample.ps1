<#
.SYNOPSIS
  上传样本 IFC + 触发 check, 返回 sid + summary (一行 JSON)
.DESCRIPTION
  1) POST /model/upload 上传 samples/<name>.ifc
  2) POST /check/<sid> 触发规则检查
  3) 输出: { sid, total_doors, by_status, error }
.PARAMETER Sample
  samples 目录下的 IFC 文件名 (不带路径), 默认 Clinic_Architectural_IFC2x3.ifc
.PARAMETER BaseUrl
  默认 http://127.0.0.1:8000
.EXAMPLE
  powershell -NoProfile -File .\upload-sample.ps1 Clinic_Architectural_IFC2x3.ifc
  powershell -NoProfile -File .\upload-sample.ps1 Duplex_xeokit.ifc
#>
param(
  [string]$Sample = "Clinic_Architectural_IFC2x3.ifc",
  [string]$BaseUrl = "http://127.0.0.1:8000"
)
$ErrorActionPreference = "Stop"
$samplePath = "D:\ProgramData\ArchiTestMajun\samples\$Sample"
if (-not (Test-Path $samplePath)) {
  Write-Output ('{"error":"sample not found: ' + $samplePath + '"}')
  exit 1
}

# 1. 上传
$uploadResp = curl.exe -s -X POST "$BaseUrl/model/upload" -F "file=@$samplePath"
$sid = ($uploadResp | ConvertFrom-Json).session_id
if (-not $sid) {
  Write-Output ('{"error":"upload failed: ' + ($uploadResp -replace '"','''') + '"}')
  exit 1
}

# 2. 触发 check
$checkResp = curl.exe -s -X POST "$BaseUrl/check/$sid"
$checkJson = $checkResp | ConvertFrom-Json

# 3. 输出
$out = @{
  sid = $sid
  total_doors = $checkJson.summary.total_doors
  pass = $checkJson.summary.by_status.pass
  fail = $checkJson.summary.by_status.fail
  non_passage = $checkJson.summary.by_status.non_passage
  unknown = $checkJson.summary.by_status.unknown
  needs_review = $checkJson.summary.needs_review_count
}
Write-Output ($out | ConvertTo-Json -Compress)