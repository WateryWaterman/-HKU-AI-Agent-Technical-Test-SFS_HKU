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
| OverallWidth | Attribute | （IfcDoor 显式属性，非 Pset） | `IFC4X3_ADD2.exp` ENTITY IfcDoor 内 | 门宽优先读此，再退 Qto/几何 |

## 碰撞检测常用对象类别（待逐个建条目）

IfcWall / IfcBeam / IfcColumn / IfcSlab / IfcPipeSegment / IfcDuctSegment / IfcCableCarrierSegment / IfcFlowTerminal — 用 `ifc-lookup.ps1 entity <名称>` 查询。
