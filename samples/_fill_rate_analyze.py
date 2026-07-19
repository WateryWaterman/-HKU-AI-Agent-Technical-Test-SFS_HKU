"""
IFC 字段填充率分析 — 门净宽检查 + Occupant Capacity 推算流水线字段可行性调研
基于 taskrequest/ifc_field_deep_lookup.md 列出的关键字段，统计真实样本中的填充情况。

输出：JSON + 控制台表格，供后续整理为 markdown 报告。
"""
import sys, io, os, json, glob
from collections import OrderedDict, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import ifcopenshell
from ifcopenshell.util import pset

SAMPLES_DIR = r"D:\ProgramData\ArchiTestMajun\samples"

# 标准化属性集名（IFC2x3 与 IFC4 命名基本一致，pset	util 工具会自动适配）
PSET_DOOR_COMMON = "Pset_DoorCommon"
PSET_SPACE_COMMON = "Pset_SpaceCommon"
PSET_SPACE_OCC = "Pset_SpaceOccupancyRequirements"
QTO_SPACE_BASE = "Qto_SpaceBaseQuantities"
QTO_DOOR_BASE = "Qto_DoorBaseQuantities"
PSET_STOREY_COMMON = "Pset_BuildingStoreyCommon"

DOOR_PSET_PROPS = ["FireRating", "FireExit", "SelfClosing", "SmokeStop",
                   "HandicapAccessible", "IsExternal", "Status"]
SPACE_PSET_PROPS = ["IsExternal", "PubliclyAccessible", "HandicapAccessible",
                    "GrossPlannedArea", "NetPlannedArea"]
SPACE_OCC_PROPS = ["OccupancyType", "OccupancyNumber", "OccupancyNumberPeak",
                   "OccupancyTimePerDay", "AreaPerOccupant", "MinimumHeadroom"]
SPACE_QTO_PROPS = ["Height", "FinishCeilingHeight", "FinishFloorHeight",
                   "GrossPerimeter", "NetPerimeter", "GrossFloorArea",
                   "NetFloorArea", "GrossWallArea", "NetWallArea",
                   "GrossCeilingArea", "NetCeilingArea", "GrossVolume", "NetVolume"]
DOOR_QTO_PROPS = ["Width", "Height", "Area"]
STOREY_PSET_PROPS = ["SprinklerProtection", "SprinklerProtectionAutomatic",
                     "EntranceLevel", "AboveGround", "ElevationOfSSLRelative",
                     "ElevationOfFFLRelative"]


def pct(num, denom):
    if denom == 0:
        return "n/a"
    return f"{100.0*num/denom:.1f}%"


def get_psets(elem):
    """返回元素的所有 property set 名称 -> {prop_name: value}
    包含三条路径：
    1. IfcRelDefinesByProperties (occurrence 上的 pset)
    2. IfcRelDefinesByType -> Type.HasPropertySets (type 上的 pset, IFC4)
    3. IfcRelDefinesByType -> IfcDoorStyle.HasPropertySets (IFC2x3)
    """
    result = {}
    # 1. occurrence pset via IfcRelDefinesByProperties
    try:
        for rel in elem.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                pds = rel.RelatingPropertyDefinition
                if pds.is_a("IfcPropertySet"):
                    ps = {}
                    for p in pds.HasProperties:
                        try:
                            nv = p.NominalValue
                            ps[p.Name] = nv.wrappedValue if nv is not None else None
                        except Exception:
                            ps[p.Name] = None
                    result[pds.Name] = ps
    except Exception:
        pass
    # 2/3. type pset via IsTypedBy (IFC4) or IsDefinedBy (IFC2x3 may go through both)
    type_rels = []
    try:
        type_rels.extend(list(elem.IsTypedBy))
    except Exception:
        pass
    # IFC2x3 中 type 关系也通过 IsDefinedBy 但实体名是 IfcRelDefinesByType
    try:
        for rel in elem.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByType"):
                type_rels.append(rel)
    except Exception:
        pass
    for rel in type_rels:
        try:
            t = rel.RelatingType
            if t is None:
                continue
            # IFC4 IfcDoorType.HasPropertySets / IFC2x3 IfcDoorStyle.HasPropertySets
            type_psets = getattr(t, "HasPropertySets", None)
            if type_psets:
                for pds in type_psets:
                    if pds.is_a("IfcPropertySet"):
                        ps = {}
                        for p in pds.HasProperties:
                            try:
                                nv = p.NominalValue
                                ps[p.Name] = nv.wrappedValue if nv is not None else None
                            except Exception:
                                ps[p.Name] = None
                        # occurrence pset 不被覆盖
                        if pds.Name not in result:
                            result[pds.Name] = ps
        except Exception:
            continue
    return result


def get_pset_prop(psets_dict, pset_name, prop_name):
    """返回某 pset 的某属性值，未找到返回 None"""
    ps = psets_dict.get(pset_name) or psets_dict.get(pset_name.upper())
    if not ps:
        return None
    v = ps.get(prop_name)
    if v is None:
        return None
    # ifcopenshell 可能返回 IfcValue wrapper，提取真实值
    try:
        if hasattr(v, "wrappedValue"):
            return v.wrappedValue
    except Exception:
        pass
    return v


def analyze_pset_props(elements, pset_name, prop_list):
    """统计 elements 中某 pset 的各属性填充率"""
    total = len(elements)
    if total == 0:
        return {"_total": 0, "_has_pset": 0}
    has_pset = 0
    prop_counts = {p: 0 for p in prop_list}
    prop_samples = {p: None for p in prop_list}
    for elem in elements:
        ps = get_psets(elem)
        if pset_name in ps or pset_name.upper() in ps:
            has_pset += 1
        for p in prop_list:
            v = get_pset_prop(ps, pset_name, p)
            if v is not None and v != "":
                prop_counts[p] += 1
                if prop_samples[p] is None:
                    prop_samples[p] = str(v)[:60]
    return {
        "_total": total,
        "_has_pset": has_pset,
        "_has_pset_pct": pct(has_pset, total),
        **{p: {"count": prop_counts[p], "pct": pct(prop_counts[p], total),
               "sample": prop_samples[p]} for p in prop_list}
    }


def analyze_explicit_attrs(elements, attr_list):
    """统计元素显式属性填充率"""
    total = len(elements)
    if total == 0:
        return {"_total": 0}
    counts = {a: 0 for a in attr_list}
    samples = {a: None for a in attr_list}
    for elem in elements:
        for a in attr_list:
            v = getattr(elem, a, None)
            if v is not None:
                counts[a] += 1
                if samples[a] is None:
                    samples[a] = str(v)[:60]
    return {
        "_total": total,
        **{a: {"count": counts[a], "pct": pct(counts[a], total),
               "sample": samples[a]} for a in attr_list}
    }


def count_relationships(spaces):
    """统计 IfcRelSpaceBoundary / IfcRelContainedInSpatialStructure 关系填充率"""
    total = len(spaces)
    if total == 0:
        return {"_total": 0}
    has_boundary = 0
    has_contained = 0
    boundary_counts = []
    contained_counts = []
    for sp in spaces:
        try:
            bnd = list(sp.BoundedBy) if sp.BoundedBy else []
            if bnd:
                has_boundary += 1
                boundary_counts.append(len(bnd))
        except Exception:
            bnd = []
        try:
            cont = list(sp.ContainsElements) if sp.ContainsElements else []
            if cont:
                has_contained += 1
                # 计算包含的元素总数
                n = sum(len(c.RelatedElements) for c in cont)
                contained_counts.append(n)
        except Exception:
            cont = []
            contained_counts.append(0)
    avg_bnd = sum(boundary_counts)/len(boundary_counts) if boundary_counts else 0
    avg_cont = sum(contained_counts)/len(contained_counts) if contained_counts else 0
    return {
        "_total": total,
        "has_BoundedBy": {"count": has_boundary, "pct": pct(has_boundary, total)},
        "has_ContainsElements": {"count": has_contained, "pct": pct(has_contained, total)},
        "avg_BoundedBy_per_space": round(avg_bnd, 1),
        "avg_Contained_per_space": round(avg_cont, 1),
    }


def count_space_quantities(spaces):
    """统计 IfcElementQuantity / IfcQuantityArea / IfcQuantityLength 等数量填充率
    IFC2x3 常用 IfcElementQuantity.Quantities 里的 IfcQuantityArea (Name='GSA BIM Area' 等)
    IFC4 推荐 Qto_SpaceBaseQuantities，但实际可能两种都遇到。
    """
    total = len(spaces)
    if total == 0:
        return {"_total": 0}
    has_elem_qty = 0
    has_quantity_area = 0
    area_names = defaultdict(int)
    area_samples = []
    for sp in spaces:
        try:
            for rel in sp.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    pds = rel.RelatingPropertyDefinition
                    if pds.is_a("IfcElementQuantity"):
                        has_elem_qty += 1
                        for q in pds.Quantities:
                            if q.is_a("IfcQuantityArea"):
                                has_quantity_area += 1
                                area_names[q.Name] += 1
                                if len(area_samples) < 5:
                                    area_samples.append((q.Name, float(q.AreaValue) if q.AreaValue else None))
                                break  # 每个空间只计一次
                        break
        except Exception:
            pass
    return {
        "_total": total,
        "has_IfcElementQuantity": {"count": has_elem_qty, "pct": pct(has_elem_qty, total)},
        "has_IfcQuantityArea": {"count": has_quantity_area, "pct": pct(has_quantity_area, total)},
        "area_quantity_names": dict(area_names),
        "area_samples": area_samples,
    }


def door_space_links(doors):
    """统计门↔空间关联的可用路径"""
    total = len(doors)
    if total == 0:
        return {"_total": 0}
    fills = list(spaces_filled)
    cont_in_space = 0   # IfcRelContainedInSpatialStructure -> IfcSpace
    cont_in_storey = 0  # IfcRelContainedInSpatialStructure -> IfcBuildingStorey
    fills_opening = 0   # IfcRelFillsElement -> IfcOpeningElement
    for d in doors:
        # ContainedInStructure (inverse)
        try:
            rels = d.ContainedInStructure
            if rels:
                rel = rels[0]
                rel_elem = rel.RelatingStructure
                if rel_elem.is_a("IfcSpace"):
                    cont_in_space += 1
                elif rel_elem.is_a("IfcBuildingStorey"):
                    cont_in_storey += 1
        except Exception:
            pass
        # FillsVoids (inverse)
        try:
            fills_rel = d.FillsVoids
            if fills_rel:
                fills_opening += 1
        except Exception:
            pass
    return {
        "_total": total,
        "contained_in_space": {"count": cont_in_space, "pct": pct(cont_in_space, total)},
        "contained_in_storey": {"count": cont_in_storey, "pct": pct(cont_in_storey, total)},
        "fills_opening": {"count": fills_opening, "pct": pct(fills_opening, total)},
    }


# 用来兜底记录
spaces_filled = []


def analyze_file(path):
    print(f"\n========== {os.path.basename(path)} ==========", flush=True)
    f = ifcopenshell.open(path)
    schema = f.schema
    print(f"  schema: {schema}")

    # 空间结构元素
    spaces = f.by_type("IfcSpace")
    storeys = f.by_type("IfcBuildingStorey")
    doors = f.by_type("IfcDoor")

    # 门类型 (IFC4: IfcDoorType, IFC2x3: IfcDoorStyle) — 用于拿 IfcDoorLiningProperties / IfcDoorPanelProperties
    door_types = []
    for tname in ("IfcDoorType", "IfcDoorStyle"):
        try:
            door_types = f.by_type(tname)
            if door_types:
                break
        except RuntimeError:
            continue
    lining_props = f.by_type("IfcDoorLiningProperties")
    panel_props = f.by_type("IfcDoorPanelProperties")

    # 元素总数概览
    print(f"  IfcSpace: {len(spaces)}, IfcBuildingStorey: {len(storeys)}, IfcDoor: {len(doors)}")
    print(f"  IfcDoorType: {len(door_types)}, IfcDoorLiningProperties: {len(lining_props)}, IfcDoorPanelProperties: {len(panel_props)}")

    spaces_filled.clear()
    spaces_filled.extend(spaces)

    # 1. IfcSpace 显式属性
    space_attrs = analyze_explicit_attrs(spaces, ["Name", "LongName", "Description",
                                                  "ObjectType", "PredefinedType",
                                                  "ElevationWithFlooring"])
    # 2. IfcSpace Pset
    space_common = analyze_pset_props(spaces, PSET_SPACE_COMMON, SPACE_PSET_PROPS)
    space_occ = analyze_pset_props(spaces, PSET_SPACE_OCC, SPACE_OCC_PROPS)
    space_qto = analyze_pset_props(spaces, QTO_SPACE_BASE, SPACE_QTO_PROPS)
    # 3. IfcSpace 关系
    space_rels = count_relationships(spaces)
    # 3b. IfcSpace 数量(IfcElementQuantity / IfcQuantityArea)
    space_qtys = count_space_quantities(spaces)

    # 4. IfcDoor 显式属性
    door_attrs = analyze_explicit_attrs(doors, ["Name", "LongName", "Description",
                                                "ObjectType", "OverallWidth", "OverallHeight",
                                                "PredefinedType", "OperationType"])
    # 5. IfcDoor Pset
    door_common = analyze_pset_props(doors, PSET_DOOR_COMMON, DOOR_PSET_PROPS)
    door_qto = analyze_pset_props(doors, QTO_DOOR_BASE, DOOR_QTO_PROPS)
    # 6. IfcDoor 关系
    door_rels = door_space_links(doors)

    # 7. IfcBuildingStorey
    storey_attrs = analyze_explicit_attrs(storeys, ["Name", "LongName", "Description",
                                                    "Elevation"])
    storey_common = analyze_pset_props(storeys, PSET_STOREY_COMMON, STOREY_PSET_PROPS)

    # 8. IfcDoorLiningProperties / Panel 显式属性
    lining_attrs = analyze_explicit_attrs(lining_props,
                                          ["LiningThickness", "LiningDepth",
                                           "ThresholdThickness", "ThresholdDepth",
                                           "CasingThickness", "CasingDepth"])
    panel_attrs = analyze_explicit_attrs(panel_props,
                                         ["PanelDepth", "PanelWidth",
                                          "PanelOperation", "PanelPosition"])

    return OrderedDict([
        ("file", os.path.basename(path)),
        ("schema", schema),
        ("counts", {
            "IfcSpace": len(spaces),
            "IfcBuildingStorey": len(storeys),
            "IfcDoor": len(doors),
            "IfcDoorType": len(door_types),
            "IfcDoorLiningProperties": len(lining_props),
            "IfcDoorPanelProperties": len(panel_props),
        }),
        ("IfcSpace_explicit", space_attrs),
        ("Pset_SpaceCommon", space_common),
        ("Pset_SpaceOccupancyRequirements", space_occ),
        ("Qto_SpaceBaseQuantities", space_qto),
        ("IfcSpace_relationships", space_rels),
        ("IfcSpace_quantities", space_qtys),
        ("IfcDoor_explicit", door_attrs),
        ("Pset_DoorCommon", door_common),
        ("Qto_DoorBaseQuantities", door_qto),
        ("IfcDoor_relationships", door_rels),
        ("IfcBuildingStorey_explicit", storey_attrs),
        ("Pset_BuildingStoreyCommon", storey_common),
        ("IfcDoorLiningProperties_explicit", lining_attrs),
        ("IfcDoorPanelProperties_explicit", panel_attrs),
    ])


def print_summary_table(results):
    """打印关键字段填充率简表"""
    print("\n" + "=" * 80)
    print("关键字段填充率汇总（行=字段，列=样本）")
    print("=" * 80)
    files = [r["file"] for r in results]
    print(f"{'Field':<55} | " + " | ".join(f"{fn[:18]:<18}" for fn in files))
    print("-" * (55 + 4 + 20*len(files)))

    def get_val(r, *keys):
        cur = r
        for k in keys:
            if cur is None: return None
            cur = cur.get(k) if isinstance(cur, dict) else None
        return cur

    field_paths = [
        ("IfcSpace 总数", ("counts", "IfcSpace")),
        ("IfcDoor 总数", ("counts", "IfcDoor")),
        ("IfcBuildingStorey 总数", ("counts", "IfcBuildingStorey")),
        ("IfcDoorLiningProperties 总数", ("counts", "IfcDoorLiningProperties")),
        ("IfcDoorPanelProperties 总数", ("counts", "IfcDoorPanelProperties")),
        ("IfcSpace.PredefinedType 填充", ("IfcSpace_explicit", "PredefinedType", "pct")),
        ("IfcSpace.ObjectType 填充", ("IfcSpace_explicit", "ObjectType", "pct")),
        ("IfcSpace.LongName 填充", ("IfcSpace_explicit", "LongName", "pct")),
        ("Pset_SpaceCommon.IsExternal 填充", ("Pset_SpaceCommon", "IsExternal", "pct")),
        ("Pset_SpaceOccupancyRequirements.OccupancyType", ("Pset_SpaceOccupancyRequirements", "OccupancyType", "pct")),
        ("Pset_SpaceOccupancyRequirements.OccupancyNumber", ("Pset_SpaceOccupancyRequirements", "OccupancyNumber", "pct")),
        ("Pset_SpaceOccupancyRequirements.AreaPerOccupant", ("Pset_SpaceOccupancyRequirements", "AreaPerOccupant", "pct")),
        ("Qto_SpaceBaseQuantities.NetFloorArea", ("Qto_SpaceBaseQuantities", "NetFloorArea", "pct")),
        ("Qto_SpaceBaseQuantities.GrossFloorArea", ("Qto_SpaceBaseQuantities", "GrossFloorArea", "pct")),
        ("IfcSpace.has_IfcElementQuantity", ("IfcSpace_quantities", "has_IfcElementQuantity", "pct")),
        ("IfcSpace.has_IfcQuantityArea", ("IfcSpace_quantities", "has_IfcQuantityArea", "pct")),
        ("IfcSpace.BoundedBy 有关系", ("IfcSpace_relationships", "has_BoundedBy", "pct")),
        ("IfcSpace.ContainsElements 有关系", ("IfcSpace_relationships", "has_ContainsElements", "pct")),
        ("IfcDoor.OverallWidth 填充", ("IfcDoor_explicit", "OverallWidth", "pct")),
        ("IfcDoor.OverallHeight 填充", ("IfcDoor_explicit", "OverallHeight", "pct")),
        ("IfcDoor.PredefinedType 填充", ("IfcDoor_explicit", "PredefinedType", "pct")),
        ("Pset_DoorCommon.FireRating 填充", ("Pset_DoorCommon", "FireRating", "pct")),
        ("Pset_DoorCommon.FireExit 填充", ("Pset_DoorCommon", "FireExit", "pct")),
        ("Pset_DoorCommon.SelfClosing 填充", ("Pset_DoorCommon", "SelfClosing", "pct")),
        ("Pset_DoorCommon.SmokeStop 填充", ("Pset_DoorCommon", "SmokeStop", "pct")),
        ("Qto_DoorBaseQuantities.Width 填充", ("Qto_DoorBaseQuantities", "Width", "pct")),
        ("IfcDoor.contained_in_space", ("IfcDoor_relationships", "contained_in_space", "pct")),
        ("IfcDoor.contained_in_storey", ("IfcDoor_relationships", "contained_in_storey", "pct")),
        ("IfcDoor.fills_opening", ("IfcDoor_relationships", "fills_opening", "pct")),
        ("Pset_BuildingStoreyCommon.SprinklerProtection", ("Pset_BuildingStoreyCommon", "SprinklerProtection", "pct")),
        ("Pset_BuildingStoreyCommon.EntranceLevel", ("Pset_BuildingStoreyCommon", "EntranceLevel", "pct")),
        ("Pset_BuildingStoreyCommon.AboveGround", ("Pset_BuildingStoreyCommon", "AboveGround", "pct")),
        ("IfcDoorLiningProperties.LiningThickness", ("IfcDoorLiningProperties_explicit", "LiningThickness", "pct")),
        ("IfcDoorPanelProperties.PanelWidth", ("IfcDoorPanelProperties_explicit", "PanelWidth", "pct")),
    ]

    for label, path in field_paths:
        vals = []
        for r in results:
            v = get_val(r, *path)
            vals.append(v if v is not None else "n/a")
        print(f"{label:<55} | " + " | ".join(f"{str(v)[:18]:<18}" for v in vals))


def main():
    files = sorted(glob.glob(os.path.join(SAMPLES_DIR, "*.ifc")))
    print(f"Found {len(files)} IFC files in {SAMPLES_DIR}")
    results = []
    for path in files:
        try:
            r = analyze_file(path)
            results.append(r)
        except Exception as e:
            print(f"  ERROR on {path}: {e}")
            import traceback; traceback.print_exc()
            results.append({"file": os.path.basename(path), "error": str(e)})

    print_summary_table(results)

    # 输出 JSON
    out_json = os.path.join(SAMPLES_DIR, "_fill_rate_raw.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nRaw JSON saved to: {out_json}")


if __name__ == "__main__":
    main()
