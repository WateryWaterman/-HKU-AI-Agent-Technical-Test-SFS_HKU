# IFC_INDEX — MVP 热点关键词直达表

> 路径相对 `D:\ProgramData\ArchiTestMajun\research\`。
> 权威依据 = `IFC4_3`（IFC4X3_ADD2 盖章版）；快查层 = `IFC4.3.x-development\docs`（master 分支，引用条文以 ADD2 为准）。
> 每完成一个规则调研，回填新关键词。

| Keyword | Kind | 快查 md（docs） | 权威来源（IFC4_3） | Notes |
|---|---|---|---|---|
| IfcDoor | Entity | `IFC4.3.x-development\docs\schemas\shared\IfcSharedBldgElements\Entities\IfcDoor.md` | `IFC4_3\HTML\IFC4X3_ADD2.exp` L5939；`IFC4_3\HTML\lexical\IfcDoor.htm` | 门主实体，显式属性含 OverallHeight/OverallWidth |
| IfcWall | Entity | `IFC4.3.x-development\docs\schemas\shared\IfcSharedBldgElements\Entities\IfcWall.md` | `IFC4_3\HTML\lexical\IfcWall.htm` | 墙主实体，碰撞检测常用 |
| IfcSpace | Entity | `IFC4.3.x-development\docs\schemas\core\IfcProductExtension\Entities\IfcSpace.md` | `IFC4_3\HTML\lexical\IfcSpace.htm` | 空间，疏散/面积规则用 |
| IfcOpeningElement | Entity | `IFC4.3.x-development\docs\schemas\core\IfcProductExtension\Entities\IfcOpeningElement.md` | `IFC4_3\HTML\lexical\IfcOpeningElement.htm` | 洞口，门窗与墙的关联桥 |
| Pset_DoorCommon | PropertySet | `IFC4.3.x-development\docs\schemas\shared\IfcSharedBldgElements\PropertySets\Pset_DoorCommon.md` | `IFC4_3\HTML\psd\Pset_DoorCommon.xml` | 含 FireRating、FireExit、IsExternal 等 |
| Qto_DoorBaseQuantities | QuantitySet | `IFC4.3.x-development\docs\schemas\shared\IfcSharedBldgElements\QuantitySets\Qto_DoorBaseQuantities.md` | `IFC4_3\HTML\psd\Qto_DoorBaseQuantities.xml` | 门宽/高/面积数量 |
| FireRating | Property | `IFC4.3.x-development\docs\properties\f\FireRating.md` | `psd\` 内多个 Pset（脚本 `prop FireRating` 列全） | 耐火等级，消防规则核心字段 |
| FireExit | Property | `IFC4.3.x-development\docs\properties\f\FireExit.md` | `IFC4_3\HTML\psd\Pset_DoorCommon.xml` 等 | 疏散门标识 |
| OverallWidth | Attribute | （IfcDoor 显式属性，非 Pset） | `IFC4X3_ADD2.exp` ENTITY IfcDoor 内 (L5941) | 门宽优先读此，再退 Qto/几何。⚠️ 是 bounding box X 维=门洞口宽，**非门框间净宽** |
| IfcSpaceTypeEnum | Type | `IFC4.3.x-development\docs\schemas\core\IfcProductExtension\Types\IfcSpaceTypeEnum.md` | `IFC4X3_ADD2.exp` L2752 | 仅 SPACE/PARKING/GFA/INTERNAL/EXTERNAL/BERTH；用途粒度不够 Table B1；INTERNAL/EXTERNAL 已 DEPRECATED |
| IfcDoorTypeEnum | Type | `IFC4.3.x-development\docs\schemas\shared\IfcSharedBldgElements\Types\IfcDoorTypeEnum.md` | `IFC4X3_ADD2.exp` L1364 | 仅 DOOR/GATE/TRAPDOOR/BOOM_BARRIER/TURNSTILE；无 FIRE_EXIT 枚举值，疏散门靠 Pset_DoorCommon.FireExit |
| Pset_SpaceOccupancyRequirements | PropertySet | `IFC4.3.x-development\docs\schemas\core\IfcProductExtension\PropertySets\Pset_SpaceOccupancyRequirements.md` | `IFC4_3\HTML\psd\Pset_SpaceOccupancyRequirements.xml` | OccupancyType/Number/Peak + AreaPerOccupant（直接给 factor 反算）→ Occupant Capacity 推算核心 |
| Pset_SpaceCommon | PropertySet | `IFC4.3.x-development\docs\schemas\core\IfcProductExtension\PropertySets\Pset_SpaceCommon.md` | `IFC4_3\HTML\psd\Pset_SpaceCommon.xml` | IsExternal/PubliclyAccessible/HandicapAccessible/GrossPlannedArea/NetPlannedArea |
| Pset_BuildingStoreyCommon | PropertySet | `IFC4.3.x-development\docs\schemas\core\IfcProductExtension\PropertySets\Pset_BuildingStoreyCommon.md` | `IFC4_3\HTML\psd\Pset_BuildingStoreyCommon.xml` | SprinklerProtection（→Table B3/B4 选型）/EntranceLevel/AboveGround/ElevationOfSSLRelative/FFL |
| Qto_SpaceBaseQuantities | QuantitySet | `IFC4.3.x-development\docs\schemas\core\IfcProductExtension\QuantitySets\Qto_SpaceBaseQuantities.md` | `IFC4_3\HTML\psd\Qto_SpaceBaseQuantities.xml` | NetFloorArea/GrossFloorArea/NetPerimeter/GrossPerimeter/Height/Volume — 疏散人数算式分子 |
| IfcDoorLiningProperties | Entity | （属 IfcPreDefinedPropertySet 子类） | `IFC4X3_ADD2.exp` L5954 | LiningThickness/Depth + CasingThickness + ThresholdThickness → 推算 clear_width = OverallWidth − 2×LiningThickness |
| IfcDoorPanelProperties | Entity | （属 IfcPreDefinedPropertySet 子类） | `IFC4X3_ADD2.exp` L5981 | PanelWidth 是 0..1 比例（IfcNormalisedRatioMeasure），需乘 OverallWidth 得每扇宽；Clause B13.4 双扇门任一≥600mm 用 |
| IfcDoorType | Entity | （IfcBuiltElementType 子类） | `IFC4X3_ADD2.exp` L5994 | PredefinedType + OperationType + ParameterTakesPrecedence；门的疏散方向靠 OperationType + ObjectPlacement 几何 |
| IfcRelSpaceBoundary | Relationship | `IFC4.3.x-development\docs\schemas\core\IfcProductExtension\Entities\IfcRelSpaceBoundary.md` | `IFC4X3_ADD2.exp` L9934 | RelatingSpace→RelatedBuildingElement；门↔空间最权威关联，疏散检查用 1st level |
| IfcRelContainedInSpatialStructure | Relationship | `IFC4.3.x-development\docs\schemas\core\IfcProductExtension\Entities\IfcRelContainedInSpatialStructure.md` | `IFC4X3_ADD2.exp` L9788 | 门↔楼层/空间包含关系（回退路径，门常被分到 storey 而非 space） |
| AreaPerOccupant | Property | （单属性 md） | `IFC4_3\HTML\psd\Pset_SpaceOccupancyRequirements.xml` | 即香港 Table B1 occupancy factor 的反算，模型可直接填 |
| OccupancyType | Property | （单属性 md） | `IFC4_3\HTML\psd\Pset_SpaceOccupancyRequirements.xml` | IfcLabel 自由文本，按当地建筑法规填 → 需映射到 HK Table A1 |
| FireExit | Property | `IFC4.3.x-development\docs\properties\f\FireExit.md` | `IFC4_3\HTML\psd\Pset_DoorCommon.xml` | IfcBoolean，疏散门唯一标准标识。**实测 4 个公开样本 0% 填充**——MVP 必须用推断（跨空间+名字+通向楼梯） |
| IfcElementQuantity | Entity | （旧 IFC2x3 数量载体） | `IFC4X3_ADD2.exp` 中 IfcPhysicalQuantity 子类 | IFC2x3 Revit 导出把面积塞在 IfcElementQuantity.Quantities 里的 IfcQuantityArea，**Name="GSA BIM Area"**（=NetFloorArea 同义词），**不是** Qto_SpaceBaseQuantities。实测 Clinic/Duplex 100% 命中 |

## 碰撞检测常用对象类别（待逐个建条目）

IfcWall / IfcBeam / IfcColumn / IfcSlab / IfcPipeSegment / IfcDuctSegment / IfcCableCarrierSegment / IfcFlowTerminal — 用 `ifc-lookup.ps1 entity <名称>` 查询。
