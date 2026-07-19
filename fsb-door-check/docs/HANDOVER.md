# 交接文档 — FSB Door Check MVP(重启 opencode 后粘贴此文件给新会话)

> 本文件供 opencode 重启后,粘贴给新会话以恢复上下文。内容:项目背景 + 当前进度 + 卡点 + 下一步任务。
> 路径:`D:\ProgramData\ArchiTestMajun\fsb-door-check\docs\HANDOVER.md`

---

## 一句话任务

HKU AI+BIM 技术测试(截止 2026-07-20 23:59):2 天内做一个 Web 微原型,对建筑 IFC 模型做香港 FSB 2011 (2024) Part B 的**门净宽检查 + Occupant Capacity 自动推算**。考察"可运行+有思考+有品味"。

## 必读(按顺序)

1. `D:\ProgramData\ArchiTestMajun\AGENTS.md` — 项目级指南(IFC 规范查询走本地 research/、外网走代理 http://127.0.0.1:7890)
2. `fsb-door-check/docs/PLAN.md` — 初版计划(目标/架构/技术栈/阶段)
3. `fsb-door-check/docs/SSD.md` — 系统序列图
4. `fsb-door-check/docs/CONTRACT.md` — **前后端 JSON 契约 + 高亮映射(字段名严格对齐,前端禁止发明字段名)**
5. `fsb-door-check/docs/EXPORT_DESIGN.md` — 导出设计(BCF>HTML>JSON,暂不实现)
6. `taskrequest/door_width_regulation_preset.md` — 法规预设需求
7. `taskrequest/ifc_field_fill_rate.md` — 字段填充率实测(决定哪些 IFC 字段可用)
8. `taskrequest/occupant_capacity_research.md` — Table B1/B2 完整数据

## 技术栈

- **后端**:Python 3.13 + FastAPI + ifcopenshell 0.8.5(已装)+ Pydantic v2 + uvicorn
- **前端**:纯 HTML + xeokit-sdk 2.6.112(ES module,本地 lib/)+ Alpine.js 3.14(本地 lib/),**无构建步骤**
- **通信**:REST + JSON,统一 ID = IFC GlobalId
- **部署**:FastAPI 挂载 frontend/ 静态文件,单一端口 http://127.0.0.1:8000/

## 已完成里程碑(git log)

```
5c205c7 fix: 前端 CDN 本地化 + xeokit 2.6 API 修复 + 诊断日志  ← HEAD
65b52f3 feat: add chrome-devtools MCP server (headless)
fbf5530 feat: 完成前端 viewer + 端到端联调 (M3)
c8b937d feat: 完成 FastAPI 路由层 + API 集成测试 (M2)
96e0d32 feat: 完成法规预设层 + IFC 解析规则引擎 (M1)
648ff83 plan: 初始化 MVP 项目骨架与设计文档
```

### M1(96e0d32)— 后端核心完成,63 测试全绿
- `backend/presets/regulation_presets.json` — Table B1(8 大 Use Class)+ Table B2(14 档)+ Clause B13.4/B30.3
- `backend/presets/longname_to_a1.json` — LongName 关键词→Table A1 映射(v1.1,含 Revit 缩写覆盖)
- `backend/app/core/` — ifc_loader/space_area/space_use/occupant_capacity/door_width/door_space_link/fire_exit_infer/rule_engine/pipeline
- 跨 IFC2x3/IFC4 兼容,4 样本回归(Clinic 269空间254门/Duplex/SampleHouse/Snowdon)全绿
- **验证命令**:`cd fsb-door-check/backend && python -m pytest tests/ -v`(63 测试)

### M2(c8b937d)— FastAPI 路由完成,15 API 测试全绿
- `backend/app/main.py` + `app/api/`(routes_model/check/override/presets)
- `backend/app/session.py` — 会话内存态
- `backend/app/models/schemas.py` — Pydantic schema 对齐 CONTRACT.md
- 端点:POST /model/upload、GET /doors/{gid}、POST /check/{sid}、POST /override/{sid}、GET /presets
- 覆盖类型:fire_exit/space_use/occupancy/threshold/storey_sprinkler/storey_entrance
- **验证命令**:`cd fsb-door-check/backend && python -m pytest tests/test_api.py -v`(15 测试)

### M3(fbf5530)+ 修复(5c205c7)— 前端完成,但 viewer 加载 IFC 卡住
- `frontend/index.html` — 左右分栏(左 3D canvas + 右侧栏 Regulation/Door/Results 三 tab)
- `frontend/src/app.js` — Alpine 组件(状态 + API 调用 + 门选取/检查/覆盖/快速定位 F/U 键)
- `frontend/src/viewer.js` — xeokit 封装(加载/拾取/高亮/X-ray/楼层隔离)
- `frontend/src/api.js` — fetch 后端
- `frontend/lib/` — xeokit-sdk.es.min.js(1.76MB)+ alpine.cdn.min.js + web-ifc.wasm(本地化,绕开 Edge Tracking Prevention)
- `backend/app/main.py` — 挂载 StaticFiles 到 /,注册 wasm MIME

## 当前卡点(关键!新会话首要任务)

**viewer 能初始化(无 init error),但加载 IFC 文件后画面保持深蓝色,无模型渲染。**

### 已排除的问题
- ✅ CDN 拦截(已本地化到 /lib/)
- ✅ xeokit 未加载(已用 ES module import)
- ✅ viewer.input 报错(已改 scene.input)
- ✅ summary null 报错(已用 template x-if)
- ✅ canvas 尺寸 0(已移除 x-cloak)

### 诊断日志已就位
`frontend/src/viewer.js` 的 `loadIfcUrl` 有 10+ 处 `console.log('[viewer] ...')`,覆盖:
- WebIFCLoaderPlugin 构造
- load() 返回值类型(Promise/EventEmitter/同步)
- model.on("loaded") / await model
- _indexDoorsAndStoreys
- cameraFlight.flyTo
- scene.objects 计数(为 0 则 IFC 解析失败)

### 下一步任务(按优先级)

1. **用 chrome-devtools MCP 诊断**(用户已装,commit 65b52f3):
   - 启动 uvicorn:`cd D:\ProgramData\ArchiTestMajun\fsb-door-check\backend && uvicorn app.main:app --port 8000`(或确认已在跑:`curl http://127.0.0.1:8000/health`)
   - 用 MCP 打开 http://127.0.0.1:8000/,加载 `samples/Duplex_Apartment_IFC2x3.ifc`
   - 读 console 所有 `[viewer]` 日志 + 红色错误
   - 根据日志定位卡在哪步

2. **最可能的根因**(按概率):
   - **xeokit 2.6 WebIFCLoaderPlugin 的 API 变了**:`load()` 可能返回 Promise 或需要不同参数。查 https://github.com/xeokit/xeokit-sdk/blob/master/examples/buildings/web-ifc_vbo_Duplex.html 的实际用法(用 `curl.exe -x http://127.0.0.1:7890 -sL <url>` 抓,或 webfetch)
   - **wasm 加载失败**:`/lib/web-ifc.wasm` 路径或 MIME。已验证 curl 返回 200 + application/wasm,但浏览器可能因路径解析失败。检查 Network 面板 web-ifc.wasm 请求
   - **web-ifc.wasm 版本不匹配**:xeokit 2.6.112 可能需要特定版本的 web-ifc.wasm。我下载的是 @xeokit/xeokit-sdk/dist/web-ifc.wasm,应该匹配,但可能要单独从 web-ifc 包下载
   - **WebIFCLoaderPlugin 需要 WebIFC 全局对象**:xeokit 2.6 可能要求构造时传 `{WebIFC, IfcAPI}`(见 GitHub discussion #1667)。当前只传了 wasmPath

3. **备选方案**(如果 WebIFCLoaderPlugin 实在搞不定):
   - **方案 A**:换用 xeokit 的 `XKTLoaderPlugin` + 预转换 XKT(但需要转换工具,偏离 MVP)
   - **方案 B**:换用 web-ifc 直接 + three.js(更底层,但要自己写渲染)
   - **方案 C**:换用 https://thatopen.com 的 @thatopen/components(更现代,但新栈)
   - **推荐**:先死磕 WebIFCLoaderPlugin(查 2.6 文档/例子),用 MCP 看 console 精准定位

4. **修好后继续**:
   - 阶段 5:侧栏联调完善(阈值编辑器 UI、楼层选择器、导出按钮占位)
   - 导出设计文档已在 `docs/EXPORT_DESIGN.md`,代码端点返回 501
   - 演示视频脚本(用户明天自己录,用 Duplex 样本)
   - GitHub 仓库整理 + prompts/ 目录补 development-log.md
   - 邮件提交(junnaifj@hku.hk,主题【HKU AI Agent Technical Test】姓名_学校)

## 关键约束(不可违反)

### IFC 字段(实测结论,来自 taskrequest/ifc_field_fill_rate.md)
- ✅ 可用:`IfcDoor.OverallWidth`(100%)、`IfcSpace.LongName`(100%)、`IfcElementQuantity.IfcQuantityArea`(100%)、`IfcRelSpaceBoundary`(IFC2x3 100%)
- ❌ 不可依赖(实测 0%):`Qto_SpaceBaseQuantities`、`Pset_SpaceOccupancyRequirements`、`IfcDoorLiningProperties.LiningThickness`、`Pset_DoorCommon.FireExit`/`FireRating`、`Pset_BuildingStoreyCommon`
- 门宽用 OverallWidth 作代理,必须标 `width_source="overall_estimate"` + `needs_human_review=true`
- 疏散门用推断(跨空间+名字+通向楼梯),标 `inferred_fire_exit`
- **所有门默认可选取**,UI 让用户手动标记防火门(FireExit 字段 0%)
- Table B2 起始档 4–30 人(1–3 人档不存在,capacity≤3 用 Clause B13.4 绝对下限 750mm)
- 跨版本:IFC2x3/IFC4/IFC4.3 同一套代码

### 网络
- 外网走代理:`curl.exe -x http://127.0.0.1:7890`
- 禁止联网 buildingsmart.org,IFC 规范查询走本地 `research/`(用 `ifc-spec-lookup` skill)

## 验证命令速查

```powershell
# 后端测试(63 + 15 = 78 测试)
cd D:\ProgramData\ArchiTestMajun\fsb-door-check\backend
python -m pytest tests/ -v

# 启动 uvicorn
cd D:\ProgramData\ArchiTestMajun\fsb-door-check\backend
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 验证后端 + 静态文件
curl.exe -s http://127.0.0.1:8000/health
curl.exe -s -I http://127.0.0.1:8000/lib/web-ifc.wasm  # 应 200 + application/wasm
curl.exe -s -I http://127.0.0.1:8000/lib/xeokit-sdk.es.min.js  # 应 200 + text/javascript

# 上传 IFC 测试 API
curl.exe -s -X POST http://127.0.0.1:8000/model/upload -F "file=@D:/ProgramData/ArchiTestMajun/samples/Duplex_Apartment_IFC2x3.ifc"
```

## 样本

- `samples/Duplex_Apartment_IFC2x3.ifc` — **演示视频用**(21 空间 + 14 门,跑得快)
- `samples/Clinic_Architectural_IFC2x3.ifc` — **功能验证**(269 空间 + 254 门)
- `samples/SampleHouse_IFC4.ifc` — IFC4 路径验证(4 空间 + 3 门)
- `samples/Revit_SnowdonTower_ARC_FireRating_IFC4.ifc` — 无 IfcSpace,不适合门检查

## 用户偏好(重要)

- 前端用**纯 HTML + xeokit + Alpine.js**,不要 Vite/构建步骤
- 前后端**双结构 + 统一 ID**(IFC GlobalId)
- 导出**设计文档先行**(BCF>HTML>JSON),代码端点 501
- 演示视频用户明天自己录
- 关键步骤完成后**自己 commit**(带备注,看 git log)
- 写代码要**参考 sample 实际案例**确保能运行

## 粘贴给新会话的简短版

> 继续 FSB Door Check MVP 项目。读 `fsb-door-check/docs/HANDOVER.md` 了解全貌。当前卡点:前端 viewer 加载 IFC 后深蓝色无模型渲染。用 chrome-devtools MCP 打开 http://127.0.0.1:8000/(先确保 uvicorn 在跑),加载 samples/Duplex_Apartment_IFC2x3.ifc,读 console 的 `[viewer]` 日志定位 xeokit 2.6 WebIFCLoaderPlugin 加载失败的原因,然后修复。修好后继续阶段 5(侧栏完善)+ 演示准备。约束见 AGENTS.md(外网走代理、IFC 规范走本地 research/)。
