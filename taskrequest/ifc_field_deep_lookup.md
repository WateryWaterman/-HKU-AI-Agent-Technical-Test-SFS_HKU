# IFC 4.3 ADD2 字段深查 — 门净宽检查与 Occupant Capacity 推算可行性

> 调研依据：本地 `research\IFC4_3\`（IFC4X3_ADD2 盖章版）+ `research\IFC4.3.x-development\docs`（master 快查层）
> 用 ifc-spec-lookup skill 完成全部查询，未联网 buildingsmart.org
> 调研目标：验证 Occupant Capacity 推算 + 门净宽检查流水线在 IFC 字段层是否可落地，并指明每一项的来源与不确定点。

---

## 一、字段可用性总表（核心结论）

| 法规概念 | IFC 字段 / 属性集 | 类型 | 来源标记 | 可信度 |
|---|---|---|---|---|
| 房间净面积 | `Qto_SpaceBaseQuantities.NetFloorArea` | Q_AREA | PSD | **高** |
| 房间毛面积（备用） | `Qto_SpaceBaseQuantities.GrossFloorArea` | Q_AREA | PSD | **高** |
| 房间功能用途 | `Pset_SpaceOccupancyRequirements.OccupancyType` | IfcLabel | PSD | 中（自由文本，需映射） |
| 房间设计人数（直接给） | `Pset_SpaceOccupancyRequirements.OccupancyNumber` | IfcCountMeasure | PSD | 中（若填了可直接用，跳过算式） |
| 房间人均面积（直接给） | `Pset_SpaceOccupancyRequirements.AreaPerOccupant` | IfcAreaMeasure | PSD | 中（与 Table B1 系数等价，若填了可直接用） |
| 房间峰值人数 | `Pset_SpaceOccupancyRequirements.OccupancyNumberPeak` | IfcCountMeasure | PSD | 中（疏散应取峰值） |
| 房间编号/名称 | `IfcSpace.Name` / `LongName` / `Description` / `ObjectType` | IfcLabel | exp 显式 | 高 |
| 房间空间类型（仅 SPACE/PARKING/GFA/INTERNAL/EXTERNAL） | `IfcSpace.PredefinedType` (IfcSpaceTypeEnum) | ENUM | exp 显式 | **低**（用途分类粒度远不够） |
| 房间所属楼层 | `IfcRelAggregates` → `IfcBuildingStorey` | 关系 | exp | 高 |
| 楼层喷淋保护 | `Pset_BuildingStoreyCommon.SprinklerProtection` | IfcBoolean | PSD | 高（影响 Table B3/B4 选型） |
| 楼层是否地面层 | `Pset_BuildingStoreyCommon.EntranceLevel` | IfcBoolean | PSD | 高（Clause B9） |
| 楼层是否地上 | `Pset_BuildingStoreyCommon.AboveGround` | IfcLogical | PSD | 高（地库 Clause B17） |
| 门洞口宽（非净宽！） | `IfcDoor.OverallWidth` | IfcPositiveLengthMeasure | exp 显式 | 中（**是 bounding box X 维，非门框间净宽**） |
| 门洞口高 | `IfcDoor.OverallHeight` | IfcPositiveLengthMeasure | exp 显式 | 中 |
| 门宽（Qto） | `Qto_DoorBaseQuantities.Width` | Q_LENGTH | PSD | 中（"outer width of door lining"，仍是外缘） |
| 门框厚度 | `IfcDoorLiningProperties.LiningThickness` | IfcNonNegativeLengthMeasure | exp 显式 | 中（可推算净宽） |
| 门面板宽（多扇） | `IfcDoorPanelProperties.PanelWidth` | IfcNormalisedRatioMeasure (0..1) | exp 显式 | 中（**比例**，需乘 OverallWidth） |
| 是否疏散门 | `Pset_DoorCommon.FireExit` | IfcBoolean | PSD | **高**（这是唯一标识） |
| 耐火等级 | `Pset_DoorCommon.FireRating` | IfcLabel | PSD | 高（与 HK FRR 对应需映射） |
| 是否自闭 | `Pset_DoorCommon.SelfClosing` | IfcBoolean | PSD | 高（Clause B13.7 需要） |
| 是否挡烟 | `Pset_DoorCommon.SmokeStop` | IfcBoolean | PSD | 高 |
| 无障碍 | `Pset_DoorCommon.HandicapAccessible` | IfcBoolean | PSD | 高（Clause B30.3 相关） |
| 门外开方向 | `IfcDoor.ObjectPlacement` + `IfcDoorType.OperationType` | 几何 + ENUM | exp | 低-中（需几何运算） |
| 门所在空间（关联） | `IfcRelContainedInSpatialStructure` / `IfcRelSpaceBoundary` | 关系 | exp | 高 |

---

## 二、关键事实详解（依据源文档原文）

### 2.1 IfcSpace 用途分类的真相（重要陷阱）

- `IfcSpaceTypeEnum`（exp L2752）仅含：`SPACE / PARKING / GFA / INTERNAL / EXTERNAL / BERTH / USERDEFINED / NOTDEFINED`。
  → **INTERNAL/EXTERNAL 已在 IFC4.3.2.0 DEPRECATED**，应改用 `Pset_SpaceCommon.IsExternal`（Boolean）。
  → 这个枚举**不能区分办公/餐厅/旅馆/病房等用途**，粒度远不够 Table B1。
- **真正的用途字段是** `Pset_SpaceOccupancyRequirements.OccupancyType`（IfcLabel 自由文本），定义原文：
  > "Occupancy type for this object. It is defined according to the presiding national building code."
  → 即规范明确要求按当地建筑法规来填，正好对应香港 Table A1 的 Use Classification。
- 备选渠道：`IfcClassificationReference`（指向外部分类体系，如 UniClass、OmniClass）。`Pset_SpaceCommon` 注释明确写："space classification according to national building code by IfcClassificationReference."
- **结论**：自动用途识别必须读 `OccupancyType` 字符串 + 人工映射表（"Office"→4a, "Restaurant"→4b factor=1, …），无标准枚举可硬编码。

### 2.2 IfcSpace 面积

- `Qto_SpaceBaseQuantities.NetFloorArea`（Q_AREA）原文定义：
  > "Sum of all net usable floor areas. It excludes the area covered by elements inside the space (columns, inner walls, built-in's etc.), slab openings, or other protruding elements. Varying heights are not taking into account."
  → 这与香港 FSB 的 "usable floor area" 定义（排除楼梯、公共通道、升降机等候处、卫生间、厨房、设备机械空间）**并不完全一致**。
  - IFC 的 NetFloorArea 只扣除空间内的柱/内墙/嵌入式家具/楼板洞口。
  - 香港 usable floor area 还要扣除公共区域、卫生间、单位内厨房、设备机房。
  → **不确定点**：实务中常用 NetFloorArea 作为最接近的代理量，但需在结果中标注 `area_source: NetFloorArea` 并提示人工复核。若样本提供 `GrossFloorArea` 或自定义 Pset，应允许用户在 UI 切换。

### 2.3 IfcDoor.OverallWidth 的关键语义陷阱（重要！）

源文档原文（IfcDoor.md L46-48）：
> "Overall measure of the width, it reflects the **X Dimension of a bounding box**, enclosing the body of the **door opening**. If omitted, the OverallWidth should be taken from the geometric representation of the IfcOpeningElement in which the door is inserted.
> NOTE The body of the door might be wider then the door opening (e.g. in cases where the door lining includes a casing). In these cases the OverallWidth shall still be given as the **door opening width**, and not as the total width of the door lining."

且 IfcDoor.md L91 又写：
> "NOTE The OverallWidth and OverallHeight parameters are for informational purpose only."

而 `Qto_DoorBaseQuantities.Width`（PSD）原文：
> "Total outer width of the door lining. It should only be provided, if it is a rectangular door."

→ 这与香港 Table B2 Note 2 要求的 **"least clear width measured between the vertical members of the door frame"** **不是同一个量**！
  - `IfcDoor.OverallWidth` = 门洞口宽（含框外侧或洞口）。
  - 法规 clear width = 门框竖向构件之间的内净宽。

### 2.4 推算 clear width 的可行路径（按优先级）

1. **首选**：模型里直接有自定义 Pset（如 `Pset_DoorCommonClearWidth` 或类似），但 IFC4.3 ADD2 PSD **没有标准 clear width 属性**——需在样本里检测。
2. **次选**：`IfcDoor.OverallWidth − 2 × IfcDoorLiningProperties.LiningThickness`（若 lining 数据存在）。
   - `IfcDoorLiningProperties.LiningThickness` 是 `IfcNonNegativeLengthMeasure`（exp L5956），可能为 0/未填。
3. **再次**：从门的几何 representation（'Profile' Curve3D / Brep）直接量两框内距——几何分析法。
4. **降级**：用 `OverallWidth` 作粗估，**状态标为 `unknown` / `needs_human_review`**，不得直接判 pass/fail。
5. **绝对失败**：连 OverallWidth 都没有 → 取 `IfcOpeningElement` 几何 → 仍无则 `unknown`。

→ **建议在系统里把 width 来源打 4 档标签**：`clear_width / overall_minus_lining / overall_estimate / unknown`，每档对应不同 `needs_human_review` 程度。

### 2.5 多扇门的处理（Clause B13.4 双扇门任一扇 ≥600mm）

- `IfcDoorPanelProperties.PanelWidth`（exp L5982）类型为 `IfcNormalisedRatioMeasure`（0..1 比例），定义"panel width as ratio of total door width"。
- 推算每扇宽：`panel_width_mm = OverallWidth × PanelWidth`。
- **Clause B13.4 要求**：双扇门任一扇 ≥600mm，企口门须装顺序闭门器。检查逻辑：
  - 取 `IfcDoorType` 的 `HasPropertySets` 里所有 `IfcDoorPanelProperties`，逐 panel 算宽度。
  - 任一 <600mm → fail。
  - 企口门（rebatable）→ 检查是否有 checking device（无标准 IFC 字段，需自定义 Pset 或人工复核）。

### 2.6 门↔空间关联（门属于哪个房间？）

两条互补路径：
1. **`IfcRelSpaceBoundary`**（exp L9934）：
   - `RelatingSpace` → `IfcSpace`
   - `RelatedBuildingElement` → `IfcDoor`（强制必填，IFC4 起 mandatory）
   - 这是"门作为空间边界"的关系，最权威。1st/2nd level 区分用于热工，疏散检查用 1st level 即可。
2. **`IfcRelContainedInSpatialStructure`**（exp L9788）：
   - IfcDoor 可直接被 `IfcBuildingStorey` 或 `IfcSpace` 包含（IfcDoor 文档 "Spatial Containment" 概念明确"门 may also be assigned to space"）。
   - 实务中门常归在楼层，需通过 `IfcRelSpaceBoundary` 才能精确到房间。
3. **几何法**：若上述关系缺失，可用门 bounding box 中心点与空间多边形做 point-in-polygon 反推。

→ **建议主用 `IfcRelSpaceBoundary`，回退 `IfcRelContainedInSpatialStructure`，最终回退几何**。

### 2.7 FireExit 字段是疏散门识别的唯一标准途径

- `IfcDoorTypeEnum`（exp L1364）只有 `DOOR / GATE / TRAPDOOR / BOOM_BARRIER / TURNSTILE / USERDEFINED / NOTDEFINED`，**无 FIRE_EXIT 枚举值**。
- 因此识别疏散门**必须读** `Pset_DoorCommon.FireExit`（IfcBoolean）。源文档定义：
  > "Indication whether this object is designed to serve as an exit in the case of fire (TRUE) or not (FALSE). Here it defines an exit door in accordance to the national building code."
- 这正好对应香港 FSB 的 "exit door" 语义。
- **风险**：若建模时未填 `FireExit=True`，系统会漏检疏散门。建议：把"容量 >3 房间的所有通向走廊/外部的门"也作为候选疏散门，并标 `inferred_fire_exit` 待人工确认。

### 2.8 楼层喷淋信息（Table B3 vs B4）

- `Pset_BuildingStoreyCommon.SprinklerProtection`（IfcBoolean）原文：
  > "Indication whether this object is sprinkler protected (TRUE) or not (FALSE)."
- `Pset_BuildingStoreyCommon.SprinklerProtectionAutomatic` 进一步细化。
- 这直接驱动 Table B3（非喷淋）/ Table B4（喷淋）选型（Clause B12.3/B12.4），进而影响楼梯疏散能力核算（本次 MVP 不做楼梯，但留接口）。

---

## 三、修正后的推算流水线（含字段来源标记）

```python
# ============ Occupant Capacity ============
def occupant_capacity(space):
    # 优先级 1: 直接给的人数
    n = pset_get(space, "Pset_SpaceOccupancyRequirements", "OccupancyNumber")
    if n is not None:
        return ceil(n), {"src": "OccupancyNumber", "needs_review": False}

    # 优先级 2: 直接给的人均面积 (= 反算 factor)
    apo = pset_get(space, "Pset_SpaceOccupancyRequirements", "AreaPerOccupant")
    if apo is not None:
        area = get_space_net_area(space)
        if area is not None:
            return ceil(area / apo), {"src": "AreaPerOccupant+NetFloorArea", "needs_review": False}

    # 优先级 3: OccupancyType 字符串 → 映射 Table B1 factor
    occ_type = pset_get(space, "Pset_SpaceOccupancyRequirements", "OccupancyType")
    if occ_type is not None:
        factor = HK_TABLE_B1_MAP.get(normalize(occ_type))  # "office"->4a factor=9
        if factor is not None and isinstance(factor, (int, float)):
            area = get_space_net_area(space)
            if area is not None:
                return ceil(area / factor), {"src": f"TableB1[{occ_type}]+NetFloorArea", "needs_review": True}

    # 优先级 4: 退回 IfcClassificationReference → 外部分类映射
    cls = classification_reference(space)
    if cls:
        factor = HK_TABLE_B1_MAP.get(cls)
        ...

    # 优先级 5: 都缺 → unknown
    return None, {"src": "missing", "needs_review": True, "status": "unknown"}

def get_space_net_area(space):
    # Qto_SpaceBaseQuantities.NetFloorArea 优先
    q = qto_get(space, "Qto_SpaceBaseQuantities", "NetFloorArea")
    if q is not None: return q, "NetFloorArea"
    q = qto_get(space, "Qto_SpaceBaseQuantities", "GrossFloorArea")
    if q is not None: return q, "GrossFloorArea(fallback)"
    # 几何计算
    return geometry_footprint_area(space), "geometry_estimate"

# ============ 门 clear width ============
def door_clear_width(door):
    # 优先级 1: 自定义 clear width Pset (样本检测)
    w = pset_get_any(door, ["ClearWidth", "NetWidth"])
    if w is not None: return w, "clear_width"

    # 优先级 2: OverallWidth - 2*LiningThickness
    overall = door.OverallWidth
    lining = pset_get(door_type, "IfcDoorLiningProperties", "LiningThickness")
    if overall and lining is not None:
        return overall - 2*lining, "overall_minus_lining"

    # 优先级 3: OverallWidth 作粗估
    if overall: return overall, "overall_estimate"

    # 优先级 4: 几何
    g = geometry_clear_width(door)
    if g: return g, "geometry"

    return None, "unknown"

# ============ 状态判定 ============
def check_door(space, door):
    cap, cap_meta = occupant_capacity(space)
    if cap is None:
        return {"status": "unknown", "reason": "cannot derive occupant capacity", **cap_meta}
    if cap <= 3:
        return {"status": "info", "reason": "Table B2 not applicable (cap<=3)",
                "b13_4_min_750": door_clear_width(door)[0] >= 750 if door_clear_width(door)[0] else None}

    w, w_src = door_clear_width(door)
    row = table_b2_lookup(cap)
    result = {
        "occupant_capacity": cap, "capacity_source": cap_meta["src"],
        "clear_width_mm": w, "width_source": w_src,
        "threshold_per_door_mm": row.min_width_per_door,
        "threshold_total_mm": row.min_total_width,
        "rule_source": "HK FSB 2011 (2024) Table B2 + Clause B7.1",
    }
    if w is None:
        result["status"] = "unknown"; result["needs_human_review"] = True
    elif w >= row.min_width_per_door:
        result["status"] = "pass"; result["needs_human_review"] = (w_src != "clear_width")
    else:
        result["status"] = "fail"; result["deficit_mm"] = row.min_width_per_door - w
        result["needs_human_review"] = (w_src != "clear_width")
    return result
```

---

## 四、对项目落地的最终判断（已按 4 公开样本实测修正）

### 实测修正补丁（2026-07-19）
本文档原假设在 4 个公开样本（Clinic_IFC2x3 / Duplex_IFC2x3 / Snowdon_IFC4 / SampleHouse_IFC4）上用 ifcopenshell 0.8.5 跑过填充率分析后，发现以下假设在真实业界导出上**不成立**，详见 `ifc_field_fill_rate.md`：

| 原假设 | 实测结果 | 修正策略 |
|---|---|---|
| `Qto_SpaceBaseQuantities.NetFloorArea` 是面积主源 | 全 0% | 改用 `IfcElementQuantity.Quantities` 里的 `IfcQuantityArea`，按 Quantity Name 动态匹配：IFC2x3 Revit 名为 `"GSA BIM Area"`，IFC4 名为 `"NetFloorArea"`（实测 100% 命中） |
| `Pset_SpaceOccupancyRequirements.OccupancyType/Number/AreaPerOccupant` 可直接用 | 全 0% | 改用 `IfcSpace.LongName` 关键词 → Table A1 映射表（实测 100% 填充），UI 允许人工覆盖 |
| `Pset_DoorCommon.FireExit` 识别疏散门 | 全 0% | 改用**推断**：IfcRelSpaceBoundary 跨两空间 + 名字含 exit/corridor/stair + 通向 IfcStair，标 `inferred_fire_exit` |
| `Pset_DoorCommon.FireRating` 真值可用 | IFC2x3 是字符串占位符 `"Fire Rating"`；Snowdon Tower 派生版只给墙加了 FireRating，门没加 | MVP 不依赖；可借门→洞口→墙关系链间接推断（门所在墙 FireRating 高 → 这扇门可能是防火门） |
| `IfcDoorLiningProperties.LiningThickness` 推算 clear width | 全 0% | MVP 直接用 `IfcDoor.OverallWidth` 作代理（实测 100% 填充），标 `overall_estimate` + `needs_human_review=True` |
| `IfcDoorPanelProperties.PanelWidth` 做多扇门检查 | IFC2x3 无此实体；IFC4 实体存在但 PanelWidth 0% 填充 | MVP 阶段多扇门 Clause B13.4 检查降级为人工复核项 |
| 门↔房间靠 `IfcRelContainedInSpatialStructure` 挂 IfcSpace | 门→Space 全 0% | 主用 `IfcRelSpaceBoundary`（IFC2x3 大样本 100%），几何 point-in-polygon 兜底 |
| `Pset_BuildingStoreyCommon.SprinklerProtection` / `EntranceLevel` | 全 0%（除 AboveGround 在 IFC4 100%） | UI 让用户为每个 storey 手工标注 |

### 跨版本兼容性（重要）
通过 ifc-spec-lookup `old` 命令查 `reference_schemas/`（IFC2x3 TC1 / IFC4x1 / IFC4x2 / IFC4 ADD2 TC1）验证：
- `Pset_DoorCommon`（含 FireRating/FireExit/SelfClosing/SmokeStop）在 **IFC2x3 TC1 就已经存在**，字段定义一致
- `Pset_SpaceOccupancyRequirements`（含 OccupancyType/Number/Peak/AreaPerOccupant）在 **IFC2x3 TC1 就已经存在**，字段定义一致

→ **同一套读取代码可跨 IFC2x3/IFC4/IFC4.3 工作，不需要为 IFC4.3 做额外特殊设计**。问题在业界没填这些字段，不在标准没有。

### 概念澄清（修正之前可能的误解）
- **门不是墙的附属品**——门和墙是独立的 `IfcElement` 实例，各自有 `Pset_DoorCommon` 和 `Pset_WallCommon`
- 关系链：`IfcDoor` →（`IfcRelFillsElement`）→ `IfcOpeningElement` →（`IfcRelVoidsElement`）→ `IfcWall`
- `Pset_WallCommon.FireRating`（墙耐火等级，如防火墙 M2）**≠** `Pset_DoorCommon.FireRating`（门耐火等级，如防火门 60min）——是两个不同属性，不能混用
- IFC 里**没有"消防通道"标准实体**；疏散路径靠 IfcSpace 组合 + `FireExit=True` 的 IfcDoor 表达，或用 `IfcZone` + 自定义 Pset
- Snowdon Tower "FireRatingAdded" 版本的"FireRating 在墙上"特指该派生版本的做法——它只给墙加了 FireRating='M2'，门没加；不代表"消防门属性应该挂在墙上"

### 修正后的最终判断

1. **Occupant Capacity 推算可行但有降级路径**，三层降级重排：
   - 顶层：`Pset_SpaceOccupancyRequirements.OccupancyNumber/AreaPerOccupant` 直接给（实测 0%，留作未来兼容）
   - 中层：`IfcSpace.LongName` 关键词 → 香港 Table A1 映射表（**MVP 主路径**，实测 100% 填充）
   - 底层：UI 人工指定（强制 fallback）
2. **门 clear width 是最大的工程难点**：标准无 clear width 字段；`IfcDoorLiningProperties.LiningThickness` 实测全 0%；**MVP 直接用 `OverallWidth` 作代理**（实测 100% 填充），标 `overall_estimate` + `needs_human_review=True`。几何分析作为后续 enhancement。
3. **Use Classification 映射是第二难点**：IFC 无标准枚举；MVP 主路径是 `IfcSpace.LongName` 关键词 → 香港 Table A1 映射表，UI 允许人工覆盖。
4. **门↔房间关联主用 `IfcRelSpaceBoundary`**（IFC2x3 大样本 100%），`IfcRelContainedInSpatialStructure` 挂 IfcSpace 实测 0%，几何 point-in-polygon 兜底。
5. **FireExit 是疏散门识别的唯一标准字段**（实测 0%）；MVP 改用推断（跨空间 + 名字 + 通向楼梯），标 `inferred_fire_exit`。可借门→洞口→墙关系链辅助（门所在墙 FireRating 高 → 可能是防火门）。
6. **多扇门 Clause B13.4 检查**：IFC2x3 无 IfcDoorPanelProperties，IFC4 实体存在但 PanelWidth 0%；MVP 阶段降级为人工复核项。
7. **楼层信息实测基本未填**：`Pset_BuildingStoreyCommon.SprinklerProtection`/`EntranceLevel` 全 0%（除 AboveGround 在 IFC4 100%）；UI 让用户为每个 storey 手工标注。

→ **结论：流水线在 IFC 字段层可落地，但 clear width、Use Classification、FireExit、楼层喷淋信息四点必须保留人工复核通道，输出明确字段来源标签。MVP 演示首选 `Clinic_Architectural_IFC2x3.ifc`（269 空间 + 254 门 + 100% 空间边界 + 100% 面积），演示视频用 `Duplex_Apartment_IFC2x3.ifc`（21 空间 + 14 门，跑得快）。`Revit_SnowdonTower_ARC_FireRating_IFC4.ifc` 无 IfcSpace，不适合门净宽检查演示。**

---

## 五、需回填到 IFC_INDEX.md 的新关键词（已回填）

- IfcSpaceTypeEnum / IfcDoorTypeEnum（用途/门类枚举，已查清边界）
- Pset_SpaceOccupancyRequirements（OccupancyType/OccupancyNumber/AreaPerOccupant/OccupancyNumberPeak）— 实测 0% 填充
- Pset_SpaceCommon（IsExternal/PubliclyAccessible/HandicapAccessible/GrossPlannedArea/NetPlannedArea）
- Pset_BuildingStoreyCommon（SprinklerProtection/EntranceLevel/AboveGround）— 实测基本 0%
- Qto_SpaceBaseQuantities（NetFloorArea/GrossFloorArea/NetPerimeter/GrossPerimeter）— 实测 0%；真实面积在 IfcElementQuantity.Quantities 里的 IfcQuantityArea（IFC2x3 Revit Name="GSA BIM Area"，IFC4 Name="NetFloorArea"）
- IfcDoorLiningProperties（LiningThickness/LiningDepth/CasingThickness → 推算 clear width）— 实测 0%
- IfcDoorPanelProperties（PanelWidth/PanelPosition/PanelOperation → 多扇门分扇）— 实测 0%
- IfcRelSpaceBoundary（门↔空间边界关系）— IFC2x3 大样本 100% 命中
- IfcRelContainedInSpatialStructure（门↔空间包含关系）— 门→Space 实测 0%，门→Storey 68-100%
- IfcDoorType（OperationType/ParameterTakesPrecedence）
- IfcElementQuantity / IfcQuantityArea（IFC2x3 真实面积载体，实测 100%）
- FireExit（实测 0%，疏散门识别必须用推断）
