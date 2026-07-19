# 门净宽检查 — 法规预设与 Occupant Capacity 推算需求

## 默认法规来源
- **Jurisdiction**: Hong Kong
- **Code**: Buildings Department《Code of Practice for Fire Safety in Buildings 2011 (2024 Edition)》
- **Scope**: Part B – Means of Escape
- **Primary Table**: Table B2 — Minimum number and width of exit doors and exit routes from a room / fire compartment / storey

## Table B2 基础阈值（可作为默认 preset）

| 场景 | Occupant Capacity | 每个 Exit Door 最小净宽 | Exit Route 最小宽度 |
|---|---:|---:|---:|
| 房间/防火分隔区/楼层出口 | 4–30 | 750 mm | 1050 mm |
| 房间/防火分隔区/楼层出口 | 31–200 | 850 mm | 1050 mm |
| 房间/防火分隔区/楼层出口 | 201–300 | 1050 mm | 1050 mm |
| 房间/防火分隔区/楼层出口 | 301–500 | 1050 mm | 1050 mm |
| 房间/防火分隔区/楼层出口 | 501–750 | 1200 mm | 1200 mm |
| 房间/防火分隔区/楼层出口 | 751–1000 | 1200 mm | 1200 mm |
| 房间/防火分隔区/楼层出口 | >1000 | 1350–1500 mm | 1350–1500 mm |

> **修正**：早期预设里"1–3 人：750mm / 750mm"一档在 Table B2 中**并不存在**。Table B2 起始档为 4–30 人。1–3 人房间无法规门宽下限；Clause B13.4 给绝对下限：capacity >3 人则门 ≥750mm，双扇门任一扇 ≥600mm。
- 完整 Table B2（4–30 一直到 >3000）见 `occupant_capacity_research.md`
- 特殊场景（如 temporary refuge space 相关门）clear width 不小于 850 mm，或取 Table B2 较大者（Clause B30.3）
- 门宽要求随 **人数区间** 变化，不是单一全局数值

## 核心系统设计要求

1. **法规预设 + 用户覆盖**：内置 jurisdiction preset（默认阈值、适用条件、条文来源、说明文字）；允许用户覆盖阈值、人数区间、场景参数；输出明确区分"规范默认值"与"用户自定义值"。
2. **Occupant Capacity 自动推算**：需要一套算法，根据建筑/房间本身的属性（用途 classification、面积、楼层等）估算设计人数，作为 Table B2 人数区间选择的依据——此为本次推进重点，待调研。
3. **规则四层结构**：法规预设层 → 用户覆盖层 → 执行层（读 IFC 门字段） → 解释层（来源、依据、人工复核提示）。
4. **字段语义谨慎**：法规要 clear width；IFC 中 `Pset_DoorCommon` 有 FireRating/FireExit 等字段，但宽度是否即 clear width 取决于建模质量。需区分"标准阈值已知 / 模型宽度已知 / 语义不可信 / 字段缺失"。
5. **输出四状态**：`pass` / `fail` / `unknown`（字段缺失或不可信，待人工复核）/ `overridden`（用户自定义阈值）——避免把"数据不完整"误判为"不合规"。
6. **人工复核保留**：人数区间是否适用、宽度字段是否可作 clear width、样本是否为完整审图模型等，不全自动判定。

## 待调研
- ~~香港 FSB 中 Occupant Capacity 的官方算法（按用途 × 面积密度系数？occupant load factor 表？）~~ → 已完成，见 `occupant_capacity_research.md`
- ~~IFC 中如何表达房间用途与面积~~ → 已完成，见 `ifc_field_deep_lookup.md` + `ifc_field_fill_rate.md`

## 实测修正（2026-07-19，基于 4 个公开样本的 ifcopenshell 字段填充率分析）

| 原假设 | 实测结果 | 修正策略 |
|---|---|---|
| `Pset_DoorCommon.FireExit` 识别疏散门 | 4 样本全 0% 填充 | 改用**推断**：IfcRelSpaceBoundary 跨两空间 + 名字含 exit/corridor/stair + 通向 IfcStair，标 `inferred_fire_exit` |
| `IfcDoorLiningProperties.LiningThickness` 推算 clear width | 全 0% | MVP 直接用 `OverallWidth` 作代理，状态标 `overall_estimate` + `needs_human_review=True` |
| `Pset_DoorCommon.FireRating` 真值可用 | IFC2x3 是字符串占位符 `"Fire Rating"`；Snowdon Tower 派生版只给**墙**加了 FireRating，门没加 | MVP **不依赖** FireRating；但可利用 IfcDoor→IfcOpeningElement→IfcWall 关系链做辅助推断（门所在墙是防火墙 → 这扇门可能是防火门） |
| `Qto_SpaceBaseQuantities.NetFloorArea` 是面积主源 | 全 0% | 改用 `IfcElementQuantity.Quantities` 里的 `IfcQuantityArea`，按 Quantity Name 动态匹配（IFC2x3 Revit 叫 `"GSA BIM Area"`，IFC4 叫 `"NetFloorArea"`） |
| `Pset_SpaceOccupancyRequirements` 三件套可用 | 全 0% | 改用 `IfcSpace.LongName` 关键词 → 香港 Table A1 映射表，UI 允许人工覆盖 |
| 门↔房间靠 `IfcRelContainedInSpatialStructure` 挂 IfcSpace | 全 0% | 主用 `IfcRelSpaceBoundary`（IFC2x3 大样本 100%），几何 point-in-polygon 兜底 |

### 跨版本兼容性确认（重要）
通过 ifc-spec-lookup `old` 命令查 `reference_schemas/` 验证：`Pset_DoorCommon`（含 FireRating/FireExit）与 `Pset_SpaceOccupancyRequirements`（含 OccupancyType/Number/AreaPerOccupant）在 **IFC2x3 TC1 就已经存在**，字段定义与 IFC4.3 ADD2 一致。
→ **同一套读取代码可跨 IFC2x3 / IFC4 / IFC4.3 工作，不需要为 IFC4.3 做额外特殊设计**。问题在业界没填这些字段，不在标准没有。

### 概念澄清（修正之前可能的误解）
- 门**不是**墙的附属品，是独立的 IfcElement
- `Pset_WallCommon.FireRating` = **墙**的耐火等级（如防火墙 M2）
- `Pset_DoorCommon.FireRating` = **门本身**的耐火等级（如防火门 60min）
- 两者是不同的属性，不能混用
- IFC 里**没有"消防通道"标准实体**；疏散路径靠 IfcSpace 组合 + FireExit=True 的门来表达，或用 IfcZone + 自定义 Pset
- 门↔墙关系链：`IfcDoor` →（`IfcRelFillsElement`）→ `IfcOpeningElement` →（`IfcRelVoidsElement`）→ `IfcWall`，可借此间接推断

### MVP 演示样本首选
`Clinic_Architectural_IFC2x3.ifc`（269 空间 + 254 门 + 100% 空间边界 + 100% 面积）；演示视频用 `Duplex_Apartment_IFC2x3.ifc`（21 空间 + 14 门，跑得快）。详见 `samples/README.md`。
