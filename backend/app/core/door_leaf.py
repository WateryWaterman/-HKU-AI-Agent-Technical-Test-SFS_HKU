"""双扇门(double-leaf)识别 — 用于 Clause B13.4 每扇 >=600mm 校验。

对应 docs/CONTRACT.md §2.3 Door.is_double_leaf。
对应 taskrequest/occupant_capacity_research.md Clause B13.4:
    "In the case of a double leaf door, no leaf of such door should be
    less than 600 mm in width..."

实测(ifcopenshell 0.8.5, 4 个样本模型)验证的取值路径:
    1. IfcDoor.OperationType (IFC4 部分导出工具直接写在 occurrence 上)
    2. 经 IsTypedBy(IFC4) / IsDefinedBy+IfcRelDefinesByType(IFC2x3)
       关联的 IfcDoorType / IfcDoorStyle.OperationType
枚举值形如 DOUBLE_DOOR_SINGLE_SWING / DOUBLE_DOOR_DOUBLE_SWING 等,
前缀为 "DOUBLE_DOOR" 才是真正的双扇门。

**易错点**: IfcDoorTypeOperationEnum 里的 DOUBLE_SWING_LEFT / DOUBLE_SWING_RIGHT
指的是"单扇门可双向摆动"(double-acting single leaf),不是双扇门,
不能用简单的 "DOUBLE" 子串匹配,必须要求 "DOUBLE_DOOR" 前缀。
"""
from __future__ import annotations

from typing import Optional

_UNDEFINED = ("NOTDEFINED", "USERDEFINED")


def _raw_operation_type(door) -> tuple[Optional[str], str]:
    """返回 (operation_type_str, source)。

    source ∈ {"occurrence", "type", "none"}
    """
    op = getattr(door, "OperationType", None)
    if op is not None and str(op) not in _UNDEFINED:
        return str(op), "occurrence"

    type_rels: list = []
    try:
        type_rels.extend(list(door.IsTypedBy))
    except Exception:
        pass
    try:
        for rel in door.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByType"):
                type_rels.append(rel)
    except Exception:
        pass

    for rel in type_rels:
        try:
            t = rel.RelatingType
        except Exception:
            continue
        if t is None:
            continue
        op = getattr(t, "OperationType", None)
        if op is not None and str(op) not in _UNDEFINED:
            return str(op), "type"

    return None, "none"


def get_door_leaf_info(door) -> tuple[Optional[bool], str]:
    """返回 (is_double_leaf, leaf_source)。

    is_double_leaf:
        True  — OperationType 前缀为 "DOUBLE_DOOR" (真正双扇门)
        False — OperationType 已知且不是双扇门 (含 DOUBLE_SWING_LEFT/RIGHT 等单扇双向摆动)
        None  — OperationType 未定义/缺失, 无法判断

    leaf_source ∈ {"operation_type_occurrence", "operation_type_type", "unknown"}
    """
    op, src = _raw_operation_type(door)
    if op is None:
        return None, "unknown"
    is_double = op.upper().startswith("DOUBLE_DOOR")
    source = f"operation_type_{src}"
    return is_double, source
