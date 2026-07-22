# AGENTS.md

## IFC 规范查询（重要）

- 一切 IFC 4.3 规范查询使用 `ifc-spec-lookup` skill（本地检索，禁止抓取 buildingsmart.org）。
- 权威依据：`research\IFC4_3\`（IFC4X3_ADD2 盖章版：`HTML\IFC4X3_ADD2.exp`、`HTML\psd\`、`HTML\lexical\*.htm`）。
- 快查层：`research\IFC4.3.x-development\docs\`（纯 markdown，master 分支；正式引用条文以 ADD2 为准）。
- 旧版本兼容：`research\IFC4.3.x-development\reference_schemas\`。
- `research\IFC4x3_DEV-build_NOT-normative\` 已废弃，勿引用。
- 热点关键词直达表：`research\IFC_INDEX.md`（调研新规则后回填）；版本差异记录：`research\VERSION_MAP.md`。
- `research\ifc_local_agent_protocol.md` 是初版协议草案，路径已过时，仅作历史参考。

## FSB Door Check 开发（fsb-door-check/）

- 修改 fsb-door-check 项目时用 `fsb-dev` skill 的固定脚本（重启后端 / 跑测试 / 上传样本 / 语法检查等），不要手动拼接 powershell 多步命令。
- 后端: Python 3.13 + FastAPI + ifcopenshell + httpx + python-dotenv, 端口 8000, 115 个 pytest 全绿基线。
- 前端: 纯 HTML + xeokit 2.6.112 (本地 lib/) + Alpine.js 3.14, 无构建步骤, 改完浏览器 reload 即可。
- 样本: `samples/Clinic_Architectural_IFC2x3.ifc` (254 门, 有空间边界, PASS/non_passage 都有) / `samples/Duplex_xeokit.ifc` (14 门, 无空间边界, 全 non_passage)。
- 测试基线: 115 个 pytest, 重启后端约 3-5s, 完整跑约 35s。
- 文件速查: 改 API → `backend/app/api/routes_*.py`; 改规则 → `backend/app/core/rule_engine.py`; 改前端逻辑 → `frontend/src/app.js`; 改 3D 渲染 → `frontend/src/viewer.js`。
- 环境变量: `backend/.env` (被 gitignore), 模板见 `backend/.env.example`。DeepSeek/Resend key 配好后邮件报告功能才可用。
- 邮件报告: `POST /export/{sid}/email_report` (DeepSeek 生成 Markdown + Resend 发邮件), 不配 key 则降级纯逻辑报告 + 502。

## 部署仓库同步（fsb-door-check remote）

- `origin` remote = 完整工作区仓库（含 research/ trash/ .opencode/ 等），日常开发用。
- `fsb-door-check` remote = **纯部署仓库**，根目录只含 `backend/ frontend/ docs/ samples/ Dockerfile Procfile railway.json README.md`，**不含** `fsb-door-check/` 前缀和 research/trash 等。Railway 从此仓库自动部署。
- **同步方法**（在 main 分支上操作，不要在 deploy-fsb 分支开发）:
  1. `git fetch fsb-door-check` — 获取部署仓库最新状态
  2. `git checkout -b deploy-fsb fsb-door-check/main` — 基于部署仓库建临时分支
  3. `git checkout main -- fsb-door-check/` — 取出 main 的项目子目录
  4. 用 robocopy 将 `fsb-door-check/` 下各目录覆盖到根目录: `robocopy .\fsb-door-check\backend .\backend /MIR` (同理 frontend/ docs/ samples/)
  5. 复制根级文件: `Copy-Item fsb-door-check\README.md, Procfile, Dockerfile, railway.json`
  6. `Remove-Item -Recurse -Force fsb-door-check` — 删掉中间目录
  7. `git add -A && git commit -m "sync: ..."`
  8. `git push fsb-door-check deploy-fsb:main` — fast-forward push（通常不需要 force）
  9. `git checkout main && git branch -D deploy-fsb` — 回到 main, 删临时分支
- **注意**: 不要直接 `git push fsb-door-check main` — main 含完整工作区, 会破坏部署仓库结构。
- **Railway 配置**: Root Directory 留空（用根目录）, Procfile = `web: cd backend && python -m app.main`。

## 网络

- 外网访问需走代理 `http://127.0.0.1:7890`（curl.exe -x）。
