# 香港 FSB 2011 (2024) — Occupant Capacity 推算与门净宽检查调研

> 来源：Buildings Department《Code of Practice for Fire Safety in Buildings 2011 (2024 Edition)》Part B – Means of Escape
> 本地存档：`taskrequest/fs_code2011.pdf`（246 页全文，已通过代理下载）
> 权威条文页：Table B1 在 PDF 第 34–36 页；Table B2 在第 43 页；Clause B4/B7/B13 在第 34/41/50–52 页

---

## 一、Occupant Capacity 推算算法（Clause B4.1 + Table B1）

### 核心公式

```
occupant_capacity = usable_floor_area (m²) ÷ occupancy_factor (m²/person)
```

三种取值方式：
1. **面积 ÷ 密度系数**（最常见）：`capacity = floor_area / factor`，向上取整为人。
2. **按固定设施计数**：factor 写作 "Number of bedspaces"（病床/旅馆床）/ "Number of seats"（影院/剧场座位）→ 直接用设施数。
3. **按线性长度**：bench seating 为 `450mm/person` → `capacity = bench_length / 0.45m`。

### "Usable Floor Area" 定义（Part A 释义）
 usable floor area = 一层/一幢内一个或多个楼面面积总和，**不包括**：楼梯、公共通道、升降机等候处、盥洗室/水厕、单位内厨房，以及升降机/空调等设备机械所占空间。

### Table B1 完整 Occupancy Factor 表

| Use Class | Type of Accommodation | Occupancy Factor (m²/人) |
|---|---|---:|
| 1b | Flats — 走廊/阳台式且每梯服务≥5户 | 4.5 |
| 1b | Flats — 其他 | 9 |
| 1c | Tenement houses（唐楼） | 3 |
| 2 | Hotels/guesthouses/hostels 等 | Number of bedspaces |
| 2 | Dormitories | 3 |
| 3a | Day care / nurseries / child care | 4 |
| 3a | Hospitals — 非病人区 | 9 |
| 3a | Hospitals — 病人区 | Number of bedspaces |
| 3b | Detention / Correctional | Number of bedspaces |
| 4a | Offices | 9 |
| 4a | Board rooms / conference / function rooms | 10 |
| 4a | Staff rooms | 9 |
| 4b | Retail shops / department stores — 地库/GF/1F/2F | 3 |
| 4b | Retail shops — 3F 及以上 | 4.5 |
| 4b | Markets / supermarkets / showrooms / 金铺 | 2 |
| 4b | Café / restaurants / dining / lounges / bars | 1 |
| 4b | Banking halls（公众区） | 0.5 |
| 4b | Betting halls（公众区） | 0.5 |
| 4b | 公共信息/服务柜台（公众区） | 0.5 |
| 5a | Art galleries / exhibition / museums | 2 |
| 5a | Cinemas — 座位区 | Number of seats |
| 5a | Cinemas — foyer | 0.5 |
| 5a | Dance floors | 0.75 |
| 5a | Sports stadia — standing / removable | 0.5 / 0.5 |
| 5a | Sports stadia — fixed seating | Number of seats |
| 5a | Sports stadia — bench seating | 450mm/person |
| 5a | Indoor sports — sports/activity area | 10 |
| 5a | Indoor sports — standing/removable/fixed/bench | 0.5 / 0.5 / seats / 450mm |
| 5a | Theatres — seating | Number of seats |
| 5a | Theatres — foyer | 0.5 |
| 5b | Libraries | 2 |
| 5b | Reading / study rooms | 1 |
| 5b | Classrooms（非教育条例管辖）/ lecture rooms | 2 或 seats |
| 5c | Transport facilities / passenger terminals | 按实际设计布局 |
| 5d | Public/assembly/conference halls — removable | 0.5 |
| 5d | Public halls — fixed seating | Number of seats |
| 5d | Gymnasia | 3 |
| 5d | Swimming pool（按水面面积） | 3 |
| 5d | Columbaria | 2 |
| 5d | Viewing galleries | 0.5 |
| 6a | Commercial laundries | 10 |
| 6a | Commercial laboratories | 10 |
| 6a | Factories / workshops | 4.5 |
| 6a | Commercial kitchens | 4.5 |
| 6b | Warehouses | 30 |
| 6c | 危险品存储/制造 | 30 |
| 7 | Carparks | 30 |
| 8 | Plant rooms / switch rooms / transformer | 30 |

Notes（Table B1 注）：
- N1 单用户专用工业场所由劳工处长按工艺核定。
- N2 表中未列用途由建筑事务监督（Building Authority）核定。
- N3 建筑事务监督认可 **实际点算** 作为人数的可靠方式。
- N4 卡拉OK见食环署指引；N5 游泳池面积指水面面积。

---

## 二、Table B2 — 门/出口路线最小数量与宽度（Clause B7, B8）

### 完整 Table B2

| Occupant Capacity (人) | 最小出口门/路线数 | 出口门总宽 (mm) | 出口路线总宽 (mm) | 每个门最小宽 (mm) | 每条路线最小宽 (mm) |
|---:|---:|---:|---:|---:|---:|
| 4–30 | 1 | 750 | 1050 | 750 | 1050 |
| 31–200 | 2 | 1750 | 2100 | 850 | 1050 |
| 201–300 | 2 | 2500 | 2500 | 1050 | 1050 |
| 301–500 | 2 | 3000 | 3000 | 1050 | 1050 |
| 501–750 | 3 | 4500 | 4500 | 1200 | 1200 |
| 751–1000 | 4 | 6000 | 6000 | 1200 | 1200 |
| 1001–1250 | 5 | 7500 | 7500 | 1350 | 1350 |
| 1251–1500 | 6 | 9000 | 9000 | 1350 | 1350 |
| 1501–1750 | 7 | 10500 | 10500 | 1500 | 1500 |
| 1751–2000 | 8 | 12000 | 12000 | 1500 | 1500 |
| 2001–2250 | 9 | 13500 | 13500 | 1500 | 1500 |
| 2251–2500 | 10 | 15000 | 15000 | 1500 | 1500 |
| 2501–2750 | 11 | 16500 | 16500 | 1500 | 1500 |
| 2751–3000 | 12 | 18000 | 18000 | 1500 | 1500 |
| >3000 | — | 由 Building Authority 个案核定 | | | |

> ⚠️ **重要修正**：之前预设文档里"1–3 人：门 750mm / 路线 750mm"一档**在 Table B2 中并不存在**。Table B2 起始档为 **4–30 人**。
> - Clause B7.1：Table B2 仅适用于 occupant capacity **超过 3 人** 的房间/防火隔间。
> - Clause B13.4：任何 capacity **超过 3 人** 的房间/楼层出口门，宽度**不得小于 750mm**（双扇门任一扇≥600mm）。
> - 即 1–3 人房间无法规强制门宽下限；4–30 人为第一档（单门 ≥750mm，路线 ≥1050mm）。

### Table B2 关键注释
- **Note 2（clear width 定义）**："The width of an exit door should be the **least clear width measured between the vertical members of the door frame**." — 这是法规意义上的门宽，对应 IFC 检查时应取的值。
- Note 3：路线宽度量自墙面完工面之间；扶手突出≤90mm 可不计。
- Note 4：前提是门可被火警时自由打开。

### Clause B7.3（多门差异限制）
若 Table B2 要求≥2 门且门宽不等，则任一门超出最窄门宽度 50% 以上的部分，**不计入**"最小总宽"核算。

---

## 三、其它与门相关的硬性条款（Clause B13）

| 条款 | 要求 |
|---|---|
| B13.1 | capacity >30 的房间/楼层，门须**向疏散方向开启**；或双向开且带上部观察窗。 |
| B13.2 | 出口门外锁须可从内无需钥匙即开；电锁须火警/断电自动释放，并设手动旁路。 |
| B13.3 | 门开向楼梯休息平台时，任何摆动位置不得使平台有效半径<楼梯宽度。 |
| **B13.4** | capacity >3 人房间/楼层出口门 **≥750mm**；双扇门任一扇 ≥600mm，企口门须设顺序闭门器。 |
| B13.5 | 通向防护门廊的门须带上部观察窗（满足 FRR）。 |
| B13.6 | 工厂（须通知劳工处）出口门须外开；≥10 人工作间门须外开。 |
| B13.7 | 通向规定楼梯/防护门廊的门：自闭器不得被常开装置卡住；双面贴"常闭"告示。 |
| B13.8 | 其它出口门如需自闭，可用 hold-open 装置，须火警/断电/烟感自动释放。 |

### 特殊场景：临时避难空间门（Clause B30.3）
通向 temporary refuge space 的门 **clear width ≥850mm** 或 Table B2 要求，**取较大者**；门把手高度 950–1050mm。

### Use Classification 5a 高位场景（Clause B21, Table B5）
5a 位于地面以上 ≥12m 时用 Table B5（总宽更宽），但每门最小宽仍按 Table B2 ≥1050mm。

---

## 四、推算 → 检查 的完整流水线（用于实现）

```
[IFC 输入]                                              [法规预设]
IfcSpace / IfcBuildingStorey              Table B1: Use Classification +
  ├── 面积(NetFloorArea / 几何计算)  ──┐    Type of Accommodation
  ├── 用途(Pset_SpaceOccupancyRequirements     │    → Occupancy Factor
  │   / IfcSpace.ElevationWithQuantities等)    │
  └── (可选)床位数/座位数/ bench长度 ─────────┤
                                                ├──→ occupant_capacity = area / factor
                                                │    (或 bedspaces/seats/bench_len÷0.45)
                                                │    向上取整
                                                ▼
                              Table B2: 按 capacity 区间取
                              min_doors, min_total_width,
                              min_width_per_door, min_route_width
                                                │
                                                ▼
[门对象 IfcDoor]                              [比较]
  ├── OverallWidth / ClearWidth ──────────────┤
  │   (Pset_DoorCommon 等;                     │ clear_width = 门框竖向构件间最小净宽
  │    优先 ClearWidth, 否则几何估算, 标来源)   │
  └── FireExit / FireRating (辅助判断)         │
                                                ▼
                              结果状态: pass / fail / unknown / overridden
                              附: preset_id, rule_source, threshold, needs_human_review
```

### 算法伪代码
```python
def occupant_capacity(use_class, accom_type, area_m2, beds=None, seats=None, bench_len_m=None):
    factor = TABLE_B1[use_class][accom_type]  # m²/person | "bedspaces" | "seats" | "450mm/person"
    if factor == "bedspaces":  return beds
    if factor == "seats":      return seats
    if factor == "450mm/person": return ceil(bench_len_m / 0.45)
    return ceil(area_m2 / factor)

def door_rule(capacity, clear_width_mm, route_width_mm=None):
    if capacity <= 3:
        return status_unknown_or_info  # Table B2 不适用;B13.4 也不触发
    row = lookup_table_b2(capacity)
    # 单门场景: width >= row.min_width_per_door (通常即 row.exit_door_total_width)
    # 多门场景: total >= row.min_total_width 且 each >= row.min_width_per_door
    if clear_width_mm is None:  return "unknown"  # 字段缺失
    if clear_width_mm >= row.min_width_per_door: return "pass"
    return "fail", row.min_width_per_door - clear_width_mm  # 差值
```

---

## 五、IFC 字段对应建议（已通过 ifc-spec-lookup 深查 + 4 公开样本实测）

| 法规概念 | 候选 IFC 来源（标准定义） | 实测填充率（4 样本） | MVP 实际可用路径 |
|---|---|---|---|
| 房间面积 | `Qto_SpaceBaseQuantities.NetFloorArea`（IFC4 标准） | **0%** | **`IfcElementQuantity.Quantities` 里的 `IfcQuantityArea`**：IFC2x3 Revit 名为 `"GSA BIM Area"`，IFC4 名为 `"NetFloorArea"`。实测 100% 命中 |
| 房间用途 | `Pset_SpaceOccupancyRequirements.OccupancyType`（IfcLabel） | **0%** | **`IfcSpace.LongName` 关键词 → Table A1 映射表**（实测 100% 填充，样本如 "CENTRAL WAITING"/"Foyer"/"Living room"）+ UI 人工覆盖 |
| 直接给的人数 | `Pset_SpaceOccupancyRequirements.OccupancyNumber` / `AreaPerOccupant` | **0%** | 留作未来兼容，MVP 不依赖 |
| 床位数/座位数 | 无标准属性，多为自定义 Pset | 未测 | 低优先级，MVP 不依赖 |
| 门净宽 | 标准无 clear width 字段；`IfcDoor.OverallWidth`（洞口宽） | **100%** | **直接用 `OverallWidth` 作代理**，状态标 `overall_estimate` + `needs_human_review=True` |
| 是否疏散门 | `Pset_DoorCommon.FireExit` (Boolean) | **0%** | **推断**：IfcRelSpaceBoundary 跨两空间 + 名字含 exit/corridor/stair + 通向 IfcStair，标 `inferred_fire_exit` |
| 门耐火等级 | `Pset_DoorCommon.FireRating` | IFC2x3 是字符串占位符 `"Fire Rating"`；IFC4 0% | MVP 不依赖；可借门→洞口→墙关系链间接推断（门所在墙的 FireRating 高 → 可能是防火门） |
| 楼层喷淋 | `Pset_BuildingStoreyCommon.SprinklerProtection` | 0% | UI 手工标 |
| 楼层是否地面层 | `Pset_BuildingStoreyCommon.EntranceLevel` / `AboveGround` | AboveGround 100%（IFC4），其余 0% | UI 手工标 |

> 关键风险修正：原报告假设 `Qto_SpaceBaseQuantities` 与 `Pset_SpaceOccupancyRequirements` 是主源，实测全 0%；真正稳定可用的是 `IfcSpace.LongName`（用途）和 `IfcElementQuantity` 里的 `IfcQuantityArea`（面积）。详见 `ifc_field_fill_rate.md`。

### 跨版本兼容性（重要）
`Pset_DoorCommon`（含 FireRating/FireExit）与 `Pset_SpaceOccupancyRequirements`（含 OccupancyType/Number/AreaPerOccupant）在 **IFC2x3 TC1 就已经存在**，字段定义与 IFC4.3 ADD2 一致（已用 ifc-spec-lookup `old` 命令验证 `reference_schemas/`）。→ 同一套代码可跨 IFC2x3/IFC4/IFC4.3 工作，**不需要为 IFC4.3 做额外特殊设计**。问题在业界没填，不在标准没有。

### 概念澄清
- 门**不是**墙的附属品，是独立的 IfcElement
- `Pset_WallCommon.FireRating`（墙耐火等级）≠ `Pset_DoorCommon.FireRating`（门耐火等级），是两个不同属性
- IFC 里**没有"消防通道"标准实体**；疏散路径靠 IfcSpace 组合 + FireExit=True 的门表达，或用 IfcZone + 自定义 Pset
- 门↔墙关系链：`IfcDoor` →（`IfcRelFillsElement`）→ `IfcOpeningElement` →（`IfcRelVoidsElement`）→ `IfcWall`，可借此间接推断

---

## 六、对项目的直接结论（已按实测修正）

1. **Occupant Capacity 推算可行但有降级路径**：标准 `Pset_SpaceOccupancyRequirements` 在真实样本上全空，必须改用 `IfcSpace.LongName` 关键词 → Table A1 映射作为 MVP 主路径，UI 允许人工覆盖。
2. **最大的工程判断点（确认）**：把 `IfcSpace.LongName` 字符串映射到香港 Table A1 的 8 大类 + 子类。建议建一张关键词映射表（"office"→4a factor=9, "kitchen"→4a staff=9 / 4b commercial=4.5, "dining"/"restaurant"→4b factor=1, "lobby"/"foyer"→5a foyer=0.5, "living"/"bedroom"→1b=9, "waiting"/"banking"→4b banking=0.5, "classroom"→5b=2 或 seats, "gym"→5d gymnasia=3 等），关键词未命中时 UI 提示人工指定。
3. **门净宽检查可落地**：MVP 阶段直接用 `IfcDoor.OverallWidth` 作代理（100% 填充），但必须标 `width_source="overall_estimate"` + `needs_human_review=True`。`IfcDoorLiningProperties.LiningThickness` 全 0%，深查报告里的 `clear_width = OverallWidth − 2×LiningThickness` 路径在真实样本上不适用。
4. **疏散门识别必须靠推断**：`Pset_DoorCommon.FireExit` 实测全 0%；改用 IfcRelSpaceBoundary 跨两空间 + 名字 + 通向楼梯推断，标 `inferred_fire_exit`。
5. **预设文件应包含**：Table B1（完整 occupancy factor）+ Table A1 用途分类 + Table B2（完整阈值）+ Clause B13.4（750mm 绝对下限）+ Clause B30.3（避难空间 850mm）+ IfcSpace.LongName → Table A1 关键词映射表。
6. **MVP 起步档建议**：4–30 人（单门 ≥750mm，路线 ≥1050mm）+ 31–200 人（2 门，每门 ≥850mm，总 ≥1750mm），覆盖最常见办公/小型商业场景。
7. **MVP 演示样本首选**：`Clinic_Architectural_IFC2x3.ifc`（269 空间 + 254 门 + 100% 空间边界 + 100% 面积，演示"推断+占位提示"非常合适）；演示视频用 `Duplex_Apartment_IFC2x3.ifc`（21 空间 + 14 门，跑得快）。
8. **不适合的样本**：`Revit_SnowdonTower_ARC_FireRating_IFC4.ifc` 无 IfcSpace，做不了 capacity 推算；其 "FireRatingAdded" 版本只给墙加了 FireRating，门没加，文件名有误导性。
