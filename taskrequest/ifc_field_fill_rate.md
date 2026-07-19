# IFC 字段填充率实测报告 — 4 个公开样本上的真实数据

> 调研目的：验证 `taskrequest/ifc_field_deep_lookup.md` 中规划的门净宽检查 + Occupant Capacity 推算流水线，在真实公开 IFC 样本上字段到底填得有多全。
> 工具：`ifcopenshell 0.8.5` + 自写脚本 `samples/_fill_rate_analyze.py`
> 原始数据：`samples/_fill_rate_raw.json`
> 样本出处与许可证：见 `samples/README.md`（两个 IFC2x3 文件 CC BY 4.0，两个 IFC4 文件来自 Revit 示例导出）

## 一、样本概览

| 样本 | 建筑类型 | schema | IfcSpace | IfcDoor | IfcBuildingStorey | IfcDoorLiningProps | IfcDoorPanelProps |
|---|---|---|---:|---:|---:|---:|---:|
| `Clinic_Architectural_IFC2x3.ifc` | 2 层医疗牙科诊所（教学/机构类） | IFC2X3 | 269 | 254 | 4 | 19 | 0 |
| `Duplex_Apartment_IFC2x3.ifc` | 2 层双拼公寓（多层居民楼） | IFC2X3 | 21 | 14 | 4 | 6 | 0 |
| `Revit_SnowdonTower_ARC_FireRating_IFC4.ifc` | 商业多层小大厦（Revit 示例，加 FireRating） | IFC4 | **0** | 16 | 6 | 10 | 10 |
| `SampleHouse_IFC4.ifc` | 单户住宅（Revit 示例） | IFC4 | 4 | 3 | 2 | 3 | 3 |

**第 1 个重大发现**：Snowdon Tower 的"Architecture"导出**完全没有 IfcSpace**——Revit 把空间模型放到了 MEP/Structural 文件里。Architecture-only 导出常见此情况。我们做门净宽检查时若以该样本演示，必须先解决"无空间 → 算不出 capacity"的问题。

## 二、关键字段填充率（百分比，n/a = 该样本无此实体）

### A. Occupant Capacity 推算所需字段

| 字段 | Clinic | Duplex | Snowdon | SampleHouse |
|---|---:|---:|---:|---:|
| `IfcSpace.LongName` | **100%** | **100%** | n/a | **100%** |
| `IfcSpace.ObjectType` | 0% | 0% | n/a | 0% |
| `IfcSpace.PredefinedType` (枚举) | 0% | 0% | n/a | 100% |
| `Pset_SpaceCommon.IsExternal` | 0% | 0% | n/a | 100% |
| `Pset_SpaceOccupancyRequirements.OccupancyType` | **0%** | **0%** | n/a | **0%** |
| `Pset_SpaceOccupancyRequirements.OccupancyNumber` | 0% | 0% | n/a | 0% |
| `Pset_SpaceOccupancyRequirements.AreaPerOccupant` | 0% | 0% | n/a | 0% |
| `Qto_SpaceBaseQuantities.NetFloorArea` | **0%** | **0%** | n/a | **0%** |
| `Qto_SpaceBaseQuantities.GrossFloorArea` | 0% | 0% | n/a | 0% |
| **`IfcSpace` 有 `IfcElementQuantity`** | **100%** | **100%** | n/a | **100%** |
| **`IfcSpace` 有 `IfcQuantityArea`** | **100%** | **100%** | n/a | **100%** |
| `IfcSpace.BoundedBy` 有空间边界关系 | **100%** | **100%** | n/a | 0% |
| `IfcSpace.ContainsElements` 有包含关系 | 28.3% | 52.4% | n/a | 50% |

**第 2 个重大发现**：标准化的 `Qto_SpaceBaseQuantities` 与 `Pset_SpaceOccupancyRequirements` 在所有 4 个样本中**填充率都是 0%**——业界不按 IFC4 标准数量集命名，而用 `IfcElementQuantity.Quantities` 里的 `IfcQuantityArea`。
- IFC2x3 Revit 导出: Quantity Name 全部是 `"GSA BIM Area"`（269/269 与 21/21，面积样本 139.75 / 182.28 / 589.76 / 17.94 / 7.80 m² 等）
- IFC4 Revit 2015 导出: Quantity Name 全部是 `"NetFloorArea"`（4/4，面积样本 51.99 / 15.42 / 8.69 / 76.47 m²）

→ **算法层必须改用动态读取 `IfcElementQuantity` + 识别 Quantity Name 的方式**，而不是直接查 `Qto_SpaceBaseQuantities`。推荐匹配顺序：
1. 任何 `IfcQuantityArea.Name` ∈ {`NetFloorArea`, `净面积`, `GSA BIM Area`}（IFC2x3 GSA BIM Area 即 NetFloorArea 的同义词，Revit 默认走 GSA BIM Area schema）
2. 退化到 `GrossFloorArea` / `GrossFloorArea` 字符串
3. 退化到几何 footprint 面积

**第 3 个重大发现**：`Pset_SpaceOccupancyRequirements` 完全空白——意味着深查报告里规划的"顶层 OccupancyNumber / AreaPerOccupant 直接用"路径**在真实样本上无效**，必须强依赖"OccupancyType 字符串 + Table B1 映射"路径；但 OccupancyType 也是 0%。所以**真正可用的用途识别来源只剩 `IfcSpace.LongName`**（100% 填充，样本如 "CENTRAL WAITING" / "Foyer" / "Living room"）。这意味着：
- 必须建一张 **`IfcSpace.LongName` 关键词 → 香港 Table A1 Use Class` 映射表**（"office"→4a, "kitchen"→4a staff room=9, "dining"/"restaurant"→4b factor=1, "lobby"/"foyer"→cinema foyer=0.5, "living room"→1b=9, "waiting"→4b banking hall=0.5 等）。
- 退一步：让用户在 UI 里手工指定房间用途作为 fallback。

### B. 门 clear width 推算所需字段

| 字段 | Clinic | Duplex | Snowdon | SampleHouse |
|---|---:|---:|---:|---:|
| `IfcDoor.OverallWidth` | **100%** | **100%** | **100%** | **100%** |
| `IfcDoor.OverallHeight` | 100% | 100% | 100% | 100% |
| `IfcDoor.PredefinedType` | 0% | 0% | 100% | 100% |
| `Qto_DoorBaseQuantities.Width` | 0% | 0% | 0% | 0% |
| `IfcDoorLiningProperties.LiningThickness` | **0%** | **0%** | **0%** | **0%** |
| `IfcDoorPanelProperties.PanelWidth` | n/a | n/a | 0% | 0% |

**第 4 个重大发现**：`IfcDoor.OverallWidth` 在所有 4 个样本里都 100% 填充——这是**唯一稳定可用**的门宽数据源。但深查报告已确认它是 **bounding box X 维 = 门洞口宽**，**不是门框间净宽**。

**第 5 个重大发现**：`IfcDoorLiningProperties.LiningThickness` 在所有样本里都是 **0%** 填充，意味着深查报告规划的"clear_width = OverallWidth − 2×LiningThickness"路径**在真实样本上无效**。`IfcDoorPanelProperties.PanelWidth`（用于 Clause B13.4 双扇门检查）也是 0%。

→ **clear width 推算路径需要重新排序**：
1. **首选：直接用 `OverallWidth` 作为门宽代理**，状态标 `width_source="overall_estimate"`、`needs_human_review=True`。
2. 次选：自定义 Pset 检测（如 `Pset_DoorSecurityClassification` 等含 clear width 字段）—— 但本批样本未发现此类自定义 Pset。
3. 退化：从 `IfcDoor` 的 'Profile'/'Body' 几何 representation 直接量两框内距。
4. 多扇门 Clause B13.4 检查：在 IFC2x3 样本上 IfcDoorPanelProperties 完全不存在；在 IFC4 样本上存在但 PanelWidth 也未填——**多扇门检查 MVP 阶段建议降级为人工复核项**。

### C. 疏散门识别字段

| 字段 | Clinic | Duplex | Snowdon | SampleHouse |
|---|---:|---:|---:|---:|
| `Pset_DoorCommon.FireRating` | **100%** | **100%** | 0% | 0% |
| `Pset_DoorCommon.FireExit` | **0%** | **0%** | **0%** | **0%** |
| `Pset_DoorCommon.SelfClosing` | 0% | 0% | 0% | 0% |
| `Pset_DoorCommon.SmokeStop` | 0% | 0% | 0% | 0% |

**第 6 个重大发现**：`Pset_DoorCommon.FireExit` 在 4 个样本里**全部 0%** —— 疏散门识别在真实样本上**根本拿不到 FireExit 字段**。
**第 7 个重大发现**：`Pset_DoorCommon.FireRating` 在 IFC2x3 样本上 100% 填充，但**值是字面字符串 `"Fire Rating"`**（占位符，不是真实耐火等级如 "M2"/"F60"）——属于 Revit 导出未配置时的默认填充，对法规检查无效。Snowdon Tower 的 "FireRatingAdded" 版本**只给墙加了 FireRating（Pset_WallCommon = M2），并没有给门加**——文件名有误导性。

→ **疏散门识别策略改用推断**：
- 主信号：`IfcDoor` 通过 `IfcRelSpaceBoundary` 连到两个不同空间（"门跨越两个空间"）+ 该空间不是储藏/管道井。
- 辅信号：门名（`IfcDoor.Name` / `LongName`）包含 "exit" / "Entry" / "Corridor" / "Stair" 关键词。
- 强信号：门通向 `IfcStairFlight` / `IfcStair` 所在空间。
- 标 `inferred_fire_exit` 状态，提示人工复核。

### D. 门↔空间关联

| 字段 | Clinic | Duplex | Snowdon | SampleHouse |
|---|---:|---:|---:|---:|
| `IfcDoor.contained_in_space` | **0%** | **0%** | **0%** | **0%** |
| `IfcDoor.contained_in_storey` | 98% | 100% | 68.8% | 100% |
| `IfcDoor.fills_opening` | 96.1% | 100% | 56.2% | 100% |
| `IfcSpace.BoundedBy` (反向) | 100% | 100% | n/a | 0% |

**第 8 个重大发现**：门几乎**从不**通过 `IfcRelContainedInSpatialStructure` 直接挂在 IfcSpace 上（4/4 样本 0%）——绝大多数门挂在 IfcBuildingStorey 上，或通过 `IfcRelFillsElement` 填充 IfcOpeningElement。要拿到"门属于哪个房间"，必须走 `IfcRelSpaceBoundary`：
- IFC2x3 样本上 100% 空间都有 BoundedBy 关系，且 Clinic 有 480 条边界关系链接到 IfcDoor（实际可用）。
- Snowdon Tower 没有 IfcSpace，BoundedBy 关系也跟着缺失。
- SampleHouse 的 IfcSpace 不带 BoundedBy 关系（4 空间全无），只能退到几何反推（门中心点是否落在空间多边形内）。

→ **门↔房间关联实现策略**：
1. 主路径：`IfcRelSpaceBoundary`（IFC2x3 大样本最稳）。
2. 退化：`IfcRelContainedInSpatialStructure` 直接挂 IfcSpace（4/4 样本 0%，几乎不会命中）。
3. 退化：`IfcRelContainedInSpatialStructure` 挂 IfcBuildingStorey → 同 storey 内查所有 IfcSpace → 几何 point-in-polygon。
4. 最终：纯几何反推门 bounding box 与空间多边形相交。

### E. 楼层信息字段

| 字段 | Clinic | Duplex | Snowdon | SampleHouse |
|---|---:|---:|---:|---:|
| `Pset_BuildingStoreyCommon.SprinklerProtection` | 0% | 0% | 0% | 0% |
| `Pset_BuildingStoreyCommon.EntranceLevel` | 0% | 0% | 0% | 0% |
| `Pset_BuildingStoreyCommon.AboveGround` | 0% | 0% | 100% | 100% |

→ 楼层信息**基本未填**。MVP 阶段需在 UI 让用户为每个 storey 手工标注：是否地面层 / 是否地上 / 是否喷淋保护。这关系到 Clause B9/B12/B17 与 Table B3/B4 选型。

## 三、修正后的流水线（针对真实样本可用性重排）

```python
# === 房间面积 ===
def get_space_area(space):
    # 优先级 1: IfcElementQuantity.Quantities 中名为 NetFloorArea 的 IfcQuantityArea
    #          (IFC4 SampleHouse 命中)
    # 优先级 2: IfcElementQuantity.Quantities 中名为 "GSA BIM Area" 的 IfcQuantityArea
    #          (IFC2x3 Revit 导出命中, 是 NetFloorArea 的 Revit 同义词)
    # 优先级 3: 名为 GrossFloorArea 的 IfcQuantityArea
    # 优先级 4: Qto_SpaceBaseQuantities.NetFloorArea (本批样本全无, 留作未来兼容)
    # 优先级 5: 几何 footprint
    ...

# === 房间用途 ===
def get_space_use(space):
    # 优先级 1: Pset_SpaceOccupancyRequirements.OccupancyType  (实测 0%, 留作未来兼容)
    # 优先级 2: IfcClassificationReference (本批未测, 推测也很稀疏)
    # 优先级 3: IfcSpace.LongName 关键词映射  ← MVP 主路径
    #          "office" / "meeting" / "conference" -> 4a (factor=9)
    #          "kitchen" -> 4a staff room (factor=9) 或单独 kitchen (4b commercial kitchen factor=4.5)
    #          "dining" / "restaurant" / "cafe" / "lounge" / "bar" -> 4b (factor=1)
    #          "lobby" / "foyer" -> cinema foyer=0.5 / general assembly foyer
    #          "living" / "bedroom" / "master" -> 1b flat (factor=9)
    #          "bath" / "toilet" / "restroom" -> 不计入 (usable floor area 排除)
    #          "corridor" / "hall" -> 公共通道 (排除)
    #          "waiting" / "banking" -> 4b banking hall (factor=0.5)
    #          "classroom" / "lecture" -> 5b classroom (factor=2 或 seats)
    #          "gym" / "sports" -> 5d gymnasia (factor=3)
    # 优先级 4: 用户在 UI 手工指定 (强制 fallback)
    ...

# === 门宽 ===
def get_door_width(door):
    # 优先级 1: 自定义 Pset 中的 ClearWidth/NetWidth (本批样本未发现, 留作兼容)
    # 优先级 2: OverallWidth - 2*LiningThickness (LiningThickness 本批 0%, 留作未来兼容)
    # 优先级 3: OverallWidth 直接用作代理  ← MVP 主路径
    #          标 width_source="overall_estimate", needs_human_review=True
    # 优先级 4: 几何分析 (Body / Profile representation)
    # 优先级 5: unknown
    return door.OverallWidth, "overall_estimate"

# === 疏散门识别 ===
def is_fire_exit(door):
    # 优先级 1: Pset_DoorCommon.FireExit == True  (本批 0%, 留作未来兼容)
    # 优先级 2: 推断  ← MVP 主路径
    #          a) 通过 IfcRelSpaceBoundary 跨两个空间
    #          b) 名字含 exit/entry/corridor/stair
    #          c) 连到 IfcStair/IfcStairFlight 所在空间
    # 标 inferred_fire_exit=True, needs_human_review=True
    ...

# === 门↔房间 ===
def get_door_space(door, all_spaces):
    # 优先级 1: IfcRelSpaceBoundary.RelatingSpace  ← MVP 主路径 (IFC2x3 大样本 100%)
    # 优先级 2: IfcRelContainedInSpatialStructure -> IfcSpace  (本批 0%, 留作兼容)
    # 优先级 3: 同 storey 内几何 point-in-polygon  ← SampleHouse 退化路径
    ...
```

## 四、对项目落地的最终判断（修正版）

| 调研假设 | 实测结果 | 修正 |
|---|---|---|
| Qto_SpaceBaseQuantities.NetFloorArea 是面积主源 | **0%** 填充 | 改用 `IfcElementQuantity` 里的 `IfcQuantityArea`，按 Quantity Name 动态匹配 ("NetFloorArea" / "GSA BIM Area" / "GrossFloorArea") |
| Pset_SpaceOccupancyRequirements 三件套可用 | **0%** 填充 | 改用 `IfcSpace.LongName` 关键词 → 香港 Table A1 映射表，UI 允许人工覆盖 |
| clear_width = OverallWidth − 2×LiningThickness | LiningThickness **0%** | MVP 直接用 OverallWidth 作代理，状态标 `overall_estimate` + `needs_human_review`；几何分析作为后续 enhancement |
| Pset_DoorCommon.FireExit 识别疏散门 | **0%** 填充 | 改用推断（跨空间 + 名字 + 通向楼梯），标 `inferred_fire_exit` |
| IfcRelContainedInSpatialStructure 拿门↔房间 | 门→Space **0%** | 主路径改用 `IfcRelSpaceBoundary`；几何 point-in-polygon 兜底 |
| Pset_DoorCommon.FireRating 真值可用 | IFC2x3 是字符串占位符 "Fire Rating"；IFC4 0% | MVP **不依赖** FireRating，把它列为"未来 Pset 属性完善时再启用"的字段 |
| Pset_BuildingStoreyCommon 楼层信息 | 全 0% (除 AboveGround) | MVP 在 UI 让用户为每个 storey 手工标注 |

### 真正稳定可用的字段（4 样本实测 ≥50%）
- ✅ `IfcDoor.OverallWidth` / `OverallHeight` (100% × 4)
- ✅ `IfcSpace.LongName` (100% × 3 有空间的样本)
- ✅ `IfcSpace` 有 `IfcElementQuantity` + `IfcQuantityArea` (100% × 3 有空间的样本)
- ✅ `IfcRelSpaceBoundary` (IFC2x3 大样本 100%，IFC4 小样本 0%)
- ✅ `IfcDoor` 通过 `IfcRelFillsElement` 填充 `IfcOpeningElement` (56–100%)
- ✅ `IfcDoor` 通过 `IfcRelContainedInSpatialStructure` 挂在 IfcBuildingStorey (68–100%)

### MVP 阶段必须人工补的项
1. 房间用途（基于 LongName 推断 + UI 覆盖）
2. 门是否疏散门（推断 + UI 确认）
3. 楼层喷淋/地面层/地上属性（UI 手工标）
4. 门 clear width 复核（OverallWidth 作代理后的现场复核）

### 推荐的 MVP 演示样本优先级
1. **`Clinic_Architectural_IFC2x3.ifc`** ← 最优选：269 空间 + 254 门 + 100% BoundedBy + 100% 面积 + 100% FireRating 占位 → 演示"推断 + 占位提示"非常合适
2. `Duplex_Apartment_IFC2x3.ifc` ← 备选：体量小（21 空间 + 14 门），跑得快，适合做演示视频
3. `SampleHouse_IFC4.ifc` ← IFC4 路径验证用：4 空间 + 3 门 + 几何兜底路径
4. `Revit_SnowdonTower_ARC_FireRating_IFC4.ifc` ← **不适合**门净宽检查演示（无 IfcSpace），留作后续门/墙属性研究用
