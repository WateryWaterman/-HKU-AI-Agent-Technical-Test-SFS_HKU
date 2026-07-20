<#
.SYNOPSIS
  一键验证后端 (语法检查 + 测试 + 重启 + 健康检查)
.DESCRIPTION
  执行顺序:
    1) check-frontend.ps1 (前端语法)
    2) run-tests.ps1 (后端测试)
    3) restart-backend.ps1 (重启 + 健康检查)
  任一步失败立即停止并报错
.EXAMPLE
  powershell -NoProfile -File .\verify-all.ps1
#>
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Output "=== 1/3 Frontend syntax check ==="
& powershell -NoProfile -File "$here\check-frontend.ps1"
if ($LASTEXITCODE -ne 0) { Write-Output "FAIL at frontend"; exit 1 }

Write-Output ""
Write-Output "=== 2/3 Backend tests ==="
& powershell -NoProfile -File "$here\run-tests.ps1"
if ($LASTEXITCODE -ne 0) { Write-Output "FAIL at tests"; exit 1 }

Write-Output ""
Write-Output "=== 3/3 Restart backend + health ==="
& powershell -NoProfile -File "$here\restart-backend.ps1"
if ($LASTEXITCODE -ne 0) { Write-Output "FAIL at restart"; exit 1 }

Write-Output ""
Write-Output "ALL OK"