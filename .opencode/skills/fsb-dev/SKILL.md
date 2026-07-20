---
name: fsb-dev
description: Use when working on the FSB Door Check MVP project (under fsb-door-check/) — restarting backend, checking frontend syntax, running tests, uploading sample IFC files for verification, or checking server status. Replaces multi-step bash/powershell dance with single-script calls that return compact JSON.
---

# FSB Door Check 开发工具

项目根目录 `D:\ProgramData\ArchiTestMajun\fsb-door-check\`,后端 Python+FastAPI 端口 8000,前端纯 HTML+xeokit+Alpine。

## 何时使用

满足以下任一条件就调用本 skill 的脚本,**不要手动拼接 powershell 多步命令**:

- 修改了后端代码 → `restart-backend` 或 `verify-all`
- 修改了前端 JS → `check-frontend`(语法验证)
- 验证规则引擎/Endpoint → `run-tests`
- 端到端冒烟测试 → `upload-sample`
- 不确定后端是否在跑 → `status`
- 测试会话堆积 → `clear-sessions`

## 脚本一览 (路径: `.opencode/skills/fsb-dev/scripts/`)

| 脚本 | 用途 | 输出 | 耗时 |
|---|---|---|---|
| `check-frontend.ps1` | `node --check` 三个前端 JS | `{"app.js":"ok","viewer.js":"ok","api.js":"ok"}` | <1s |
| `run-tests.ps1` | `pytest --tb=short -q` | 最后 5 行进度 + `RESULT: N passed` | ~11s |
| `restart-backend.ps1` | 杀旧 8000 + 启动新 uvicorn + /health | `{"status":"ok","pid":N,"port":8000}` | ~3-5s |
| `upload-sample.ps1 <name>` | 上传 samples/ 下 IFC + POST /check | `{"sid":"...","total_doors":N,"pass":N,"fail":N,"non_passage":N}` | ~3-30s |
| `verify-all.ps1` | 一键: 语法 + 测试 + 重启 | 三段输出,末行 `ALL OK` 或 `FAIL at ...` | ~15-20s |
| `status.ps1` | 调 /health | `{"alive":true,"version":"0.1.0"}` 或 `{"alive":false}` | <1s |
| `clear-sessions.ps1` | 删掉所有后端 session | `{"cleared":N}` | <2s |

## 调用方式

在 bash 工具中这样调用(注意 `& powershell -NoProfile -File` 前缀):

```bash
$here = "D:\ProgramData\ArchiTestMajun\.opencode\skills\fsb-dev\scripts"
& powershell -NoProfile -File "$here\check-frontend.ps1" 2>&1
& powershell -NoProfile -File "$here\run-tests.ps1" 2>&1
& powershell -NoProfile -File "$here\restart-backend.ps1" 2>&1
& powershell -NoProfile -File "$here\upload-sample.ps1" "Clinic_Architectural_IFC2x3.ifc" 2>&1
& powershell -NoProfile -File "$here\verify-all.ps1" 2>&1
```

## 典型工作流

### 改了后端代码 (规则引擎/路由/Session)

```
1. run-tests.ps1          # 验证不破坏 86 测试
2. restart-backend.ps1    # 重启加载新代码
3. upload-sample.ps1     # 端到端冒烟
```

或一行: `verify-all.ps1` + `upload-sample.ps1`

### 改了前端 (app.js/viewer.js/api.js)

```
1. check-frontend.ps1   # 语法验证
2. 在 chrome-devtools 里 reload + 截 snapshot
```

无需重启后端(前端是静态文件,改完浏览器 reload 即可)。

### 同时改了前后端

```
1. verify-all.ps1                  # 一键三连
2. upload-sample.ps1 Clinic_...     # 冒烟
3. chrome-devtools 打开 http://127.0.0.1:8000/ 做视觉验证
```

## 行为约束

- **不要**手动拼接多步 powershell 实现这些相同操作 — 全部走脚本,省 token
- **不要**改脚本前先 `cat` 看内容 — SKILL.md 已经说明输入输出
- 脚本失败先看输出中的 `error` 或 `fail` 字段,不要立刻读脚本排查
- 测试通过了想跑前端 UI,把 sid 从 `upload-sample.ps1` 输出中复制给 chrome-devtools 的 fetch 即可

## 已知端点速查 (供 chrome-devtools evaluate_script 直接调)

```javascript
// 上传 (用脚本更方便)
fetch('/model/upload', { method:'POST', body: fd })
// summary
fetch(`/model/${sid}/summary`).then(r=>r.json())
// 触发检查
fetch(`/check/${sid}`, { method:'POST' }).then(r=>r.json())
// 覆盖(防火门/阈值/勾选...)
fetch(`/override/${sid}`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({type:'checked', global_id, value}) })
// 阈值表保存/重置
fetch(`/override/${sid}/threshold/table`, { method:'PUT',  headers:{'Content-Type':'application/json'}, body: JSON.stringify({bands}) })
fetch(`/override/${sid}/threshold/table`, { method:'DELETE' })
```