# Development Log — FSB Door Check MVP

> 开发过程记录,对应任务要求"代码 + prompts"。
> 项目:`fsb-door-check/`(HKU AI+BIM 技术测试,2026-07-19 至 2026-07-20)

---

## 时间线

### 2026-07-19(第 1 天)

**调研阶段**
- 通读 `taskrequest/door_width_regulation_preset.md`(法规预设需求)
- 通读 `taskrequest/ifc_field_fill_rate.md`(IFC 字段填充率实测,决定哪些字段可用)
- 通读 `taskrequest/occupant_capacity_research.md`(Table B1/B2 完整数据)
- 通过 `ifc-spec-lookup` skill 查本地 `research/IFC4_3/` 确认 IFC2x3/IFC4 字段兼容性

**规划阶段**(commit `648ff83`)
- 写 `docs/PLAN.md`(目标 / 范围 / 架构 / 技术栈 / 阶段 / ID 规范)
- 写 `docs/SSD.md`(系统序列图,Mermaid)
- 决策:**双结构 + 统一 ID**(前端 xeokit 读几何 + 后端 ifcopenshell 读关系,IFC GlobalId 关联)
- 决策:**纯 HTML + xeokit + Alpine.js**(无构建步骤,快速 MVP)

**M1 — 后端核心**(commit `96e0d32`)
- `presets/regulation_presets.json`:Table B1(8 大 UseClass)+ Table B2(14 档)+ Clause B13.4/B30.3
- `presets/longname_to_a1.json`:LongName 关键词→UseClass 映射(含 Revit 缩写覆盖)
- `app/core/`:ifc_loader / space_area / space_use / occupant_capacity / door_width / door_space_link / fire_exit_infer / rule_engine / pipeline
- 跨 IFC2x3/IFC4 兼容,4 样本回归(Duplex/Clinic/SampleHouse/Snowdon)63 测试全绿

**M2 — FastAPI 路由**(commit `c8b937d`)
- `app/main.py` + `app/api/`(routes_model/check/override/presets)
- `app/session.py`:会话内存态 + 覆盖态
- `app/models/schemas.py`:Pydantic schema 对齐 `docs/CONTRACT.md`
- 15 API 测试全绿

**M3 — 前端 viewer**(commit `fbf5530`)
- `frontend/index.html`:左右分栏(左 3D canvas + 右侧栏 Regulation/Door/Results 三 tab)
- `frontend/src/app.js`:Alpine 组件(状态 + API 调用 + 门选取/检查/覆盖/F/U 键)
- `frontend/src/viewer.js`:xeokit 封装(加载/拾取/高亮/X-ray/楼层隔离)
- `frontend/src/api.js`:fetch 后端
- **卡点**:viewer 能初始化但加载 IFC 后深蓝色无模型渲染

### 2026-07-20(第 2 天)

**MCP 集成**(commit `65b52f3`)
- 配置 chrome-devtools MCP server(headless),用浏览器 console 诊断 viewer 卡点

**viewer 修复尝试 1**(commit `5c205c7`)
- 前端 CDN 本地化到 `/lib/`(绕开 Edge Tracking Prevention)
- xeokit 2.6 API 修复(`scene.input` 替代 `viewer.input`)
- 诊断日志 10+ 处 `console.log('[viewer] ...')`
- **仍未解决**:WebIFCLoaderPlugin 构造失败

**交接文档**(commit `2aa7575`)
- 写 `docs/HANDOVER.md`(重启 opencode 后恢复上下文用)

**viewer 修复(根因解决)**(commit `73b61c4`)
- 用 chrome-devtools MCP 读 console:`Parameter expected: WebIFC`
- 根因:xeokit 2.6 `WebIFCLoaderPlugin` 必须显式注入 `{WebIFC, IfcAPI}`,只传 `wasmPath` 不行
- 查 GitHub `xeokit-sdk v2.6.112/examples/buildings/web-ifc_dtx_Duplex.html`(走代理 `curl.exe -x http://127.0.0.1:7890`)
- 修复:
  - 本地化 `web-ifc@0.0.51/web-ifc-api.js`
  - `viewer.js` import WebIFC,懒初始化 IfcAPI(Init() 异步)
  - 改 `load({src: blobURL})` → `load({ifc: ArrayBuffer})`,绕开 WebIFCDefaultDataSource 给 blob URL 加 `?_=ts` 缓存破坏参数导致 `ERR_FILE_NOT_FOUND` 的 bug
- 发现 `samples/Duplex_Apartment_IFC2x3.ifc`(2011 Revit 导出)web-ifc@0.0.51 报 `RangeError: offset is out of bounds`(web-ifc 自身兼容性问题)
- 下载 xeokit 官方 Duplex 副本作为 `samples/Duplex_xeokit.ifc`(1.3MB,IFC Tools Java Toolbox 导出,兼容)
- 验证:SampleHouse(3 门/58 objects)+ Duplex_xeokit(14 门/215 objects)+ Clinic(254 门/2586 objects)全跑通

**清理交接文档**(commit `393e5ea`)
- 任务完成,HANDOVER.md 移入 `trash/`(保持本体干净)

**M5 — 侧栏完善 + 导出占位**(commit `cbf3230`)
- 后端 `app/api/routes_export.py`:`POST /export/{sid}?format=bcf|html|json` 返 501 + `docs/EXPORT_DESIGN.md` 链接
- 前端 ctxbar:Storey 下拉(含每层门数)+ Export 三按钮 + Reset View
- Regulation tab:Threshold Override 面板(15 档下拉 + 新阈值输入 + Apply)
- viewer.focusDoors():聚焦楼层门不透明,其它 x-ray 弱化
- 4 新测试,82 全绿

**viewer fallback normalize + 单模型隔离 + 关闭清理**(commit `04a1bf3`)
- 后端 `POST /model/normalize`:ifcopenshell 重写 STEP,返 octet-stream
- 后端 `DELETE /model/{sid}` + 启动时清空 `uploads/normalized/`
- 前端 `_destroyCurrentModel()`:加载新模型前 destroy 旧的
- 前端 fallback:primary 失败 → normalize → 重试(零误判)
- 前端 `beforeunload` 清理 session
- 验证:Duplex_xeokit → SampleHouse 切换,scene.objects 215 → 58(单模型隔离)
- 4 新测试,86 全绿

**仓库整理**(本次 commit)
- 重写 `fsb-door-check/README.md`(从"计划阶段"更新到"已完成 MVP",反映纯 HTML 架构)
- 新建 `fsb-door-check/prompts/development-log.md`(本文件)

---

## 关键决策与原因

| 决策 | 原因 |
|---|---|
| 纯 HTML + xeokit + Alpine.js(无 Vite) | 快速 MVP,避免构建步骤;xeokit 2.6 ES module 本地化绕开 Edge Tracking Prevention |
| 双结构(前端 xeokit + 后端 ifcopenshell) | 各取所长:xeokit 擅长渲染,ifcopenshell 擅长关系链/Pset/规则 |
| 门宽用 OverallWidth | 实测 ClearWidth / LiningThickness 0%,OverallWidth 100% |
| 防火门 UI 手动标记 + 推断 | Pset_DoorCommon.FireExit 实测 0% |
| 导出 501 + 设计文档先行 | MVP 不实现,但 BCF 设计体现"懂行业标准" |
| normalize fallback 而非预测 | 零误判,只在真失败时触发;大文件 Clinic 能跑,小文件也可能挂 |
| 单模型隔离 | 避免叠加分析,确保每次只针对单一 IFC |
| 关闭清理 双保险 | beforeunload DELETE + 后端启动清空 uploads/normalized/ |

---

## 遇到的坑

1. **Edge Tracking Prevention 拦截 CDN**:xeokit/web-ifc 从 jsdelivr 加载被拦 → 全部本地化到 `/lib/`
2. **xeokit 2.6 API 变更**:`WebIFCLoaderPlugin` 必须显式注入 `{WebIFC, IfcAPI}`,老版本只需 `wasmPath`
3. **blob URL + 缓存破坏参数**:xeokit `WebIFCDefaultDataSource` 给 URL 加 `?_=timestamp`,blob URL 不支持参数 → `ERR_FILE_NOT_FOUND` → 改用 `load({ifc: ArrayBuffer})`
4. **web-ifc@0.0.51 兼容性**:对 2011 Revit 导出的 IFC2x3 报 `RangeError: offset is out of bounds`;ifcopenshell 重写后仍报 `TypeError`(web-ifc 自身限制)→ 用 xeokit 官方 Duplex 副本演示
5. **SceneModel 残留冲突**:primary 失败后不 destroy,normalize 重试时 id 冲突 → 失败时立即 `model.destroy()` + 用唯一 modelId

---

## 测试覆盖

```
86 tests全绿
├── test_presets.py        Table B1/B2 数据完整性
├── test_samples.py        4 样本回归 + GlobalId 唯一性 + 跨 IFC2x3/IFC4
└── test_api.py
    ├── TestBasic          /health /api /presets
    ├── TestUpload         upload + summary
    ├── TestDoorsAndCheck  /doors/{gid} + /check/{sid}
    ├── TestOverride       fire_exit / space_use / occupancy / threshold
    ├── TestEndToEnd       Duplex 全流程
    ├── TestExport         501 + 400(无效格式)+ 404(unknown session)
    └── TestNormalizeAndCleanup  normalize 返 bytes / 拒绝非 IFC / delete 清理
```

---

## 后续(非 MVP)

- [ ] 演示视频(用户自录,用 Duplex_xeokit.ifc)
- [ ] Docker 部署(单容器 Python 3.13 + ifcopenshell + uvicorn)
- [ ] 邮件提交(junnaifj@hku.hk)
- [ ] 导出实现(BCF > HTML > JSON,见 `docs/EXPORT_DESIGN.md`)
- [ ] 升级 web-ifc 到新版(可能解决 2011 Revit 兼容性)
