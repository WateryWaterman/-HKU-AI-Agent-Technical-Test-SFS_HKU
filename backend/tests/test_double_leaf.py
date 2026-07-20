"""双扇门(double-leaf)识别 + Clause B13.4 每扇 >=600mm 校验的测试。

对应 2026-07-20 code review 修复: app/core/door_leaf.py (新增) +
app/core/rule_engine.py 的双扇门补充校验分支。

覆盖:
1. door_leaf.get_door_leaf_info() 在 4 个真实样本模型上的识别结果
   (人工用 ifcopenshell 逐一核对过, 见 fsb_door_check_code_review.md §4)。
2. rule_engine.check_door() 对双扇门的三种典型场景:
   - 总宽通过 + 逐扇估算通过 -> pass (仍标记 needs_human_review)
   - 总宽通过 + 逐扇估算不足 600mm -> fail(B13.4), 即使 Table B2 总宽达标
   - 单扇门(is_double_leaf=False/None) -> 行为与修复前一致, 不受影响
"""
from __future__ import annotations

from pathlib import Path

import ifcopenshell
import pytest

from app.core.door_leaf import get_door_leaf_info
from app.core.rule_engine import check_door

SAMPLES_DIR = Path(__file__).parent.parent / "uploads"


def _count_double_leaf(filename: str) -> tuple[int, int]:
    f = ifcopenshell.open(str(SAMPLES_DIR / filename))
    doors = f.by_type("IfcDoor")
    double_leaf = sum(1 for d in doors if get_door_leaf_info(d)[0] is True)
    return len(doors), double_leaf


class TestDoorLeafDetectionOnRealSamples:
    """人工核对过的真实样本双扇门数量(见 code review 报告)。"""

    def test_clinic_8_double_leaf_of_254(self):
        total, dl = _count_double_leaf("Clinic_Architectural_IFC2x3.ifc")
        assert total == 254
        assert dl == 8

    def test_snowdon_1_double_leaf_of_16(self):
        total, dl = _count_double_leaf("Revit_SnowdonTower_ARC_FireRating_IFC4.ifc")
        assert total == 16
        assert dl == 1

    def test_samplehouse_1_double_leaf_of_3(self):
        total, dl = _count_double_leaf("SampleHouse_IFC4.ifc")
        assert total == 3
        assert dl == 1

    def test_duplex_0_double_leaf_of_14(self):
        total, dl = _count_double_leaf("Duplex_Apartment_IFC2x3.ifc")
        assert total == 14
        assert dl == 0

    def test_double_swing_single_leaf_not_misclassified(self):
        """DOUBLE_SWING_LEFT/RIGHT 是单扇双向摆动, 不应被误判为双扇门。

        Snowdon 样本里存在这类门, 用于回归防止子串匹配误判
        (door_leaf.py 要求 'DOUBLE_DOOR' 前缀, 而非 'DOUBLE' 子串)。
        """
        f = ifcopenshell.open(
            str(SAMPLES_DIR / "Revit_SnowdonTower_ARC_FireRating_IFC4.ifc")
        )
        doors = f.by_type("IfcDoor")
        found_double_swing_single_leaf = False
        for d in doors:
            op = getattr(d, "OperationType", None)
            if op and str(op) in ("DOUBLE_SWING_LEFT", "DOUBLE_SWING_RIGHT"):
                found_double_swing_single_leaf = True
                is_double, _ = get_door_leaf_info(d)
                assert is_double is False
        assert found_double_swing_single_leaf, (
            "expected sample to contain a DOUBLE_SWING_LEFT/RIGHT door for this "
            "regression check; if the sample changed, adjust the test"
        )


class TestDoubleLeafRuleEngine:
    """rule_engine.check_door() 双扇门补充校验(合成场景, 覆盖真实样本没触发的边界)。"""

    SPACE_INFO = {"capacity": 10, "capacity_source": "test"}  # Table B2 threshold=750mm

    def test_total_width_pass_leaf_estimate_pass(self):
        door_info = {
            "global_id": "D1",
            "measured_width_mm": 1800.0,  # leaf estimate 900mm >= 600mm
            "width_source": "overall_estimate",
            "is_double_leaf": True,
        }
        r = check_door(door_info, self.SPACE_INFO)
        assert r["status"] == "pass"
        assert r["needs_human_review"] is True
        assert any("double-leaf" in n for n in r["human_review_notes"])

    def test_total_width_pass_but_leaf_estimate_fails_b13_4(self):
        """核心修复场景: 总宽 900mm >= 750mm 阈值(Table B2 通过),
        但假设均分后每扇估算 450mm < Clause B13.4 的 600mm 下限 -> 必须判 fail。
        修复前, 代码只看总宽, 会错误判定为 pass。
        """
        door_info = {
            "global_id": "D2",
            "measured_width_mm": 900.0,
            "width_source": "overall_estimate",
            "is_double_leaf": True,
        }
        r = check_door(door_info, self.SPACE_INFO)
        assert r["status"] == "fail"
        assert r["rule_clause"] == "B13.4"
        assert r["needs_human_review"] is True

    def test_single_leaf_door_unaffected(self):
        """is_double_leaf=False/None 时行为与修复前完全一致。"""
        door_info = {
            "global_id": "D3",
            "measured_width_mm": 900.0,
            "width_source": "overall_estimate",
            "is_double_leaf": False,
        }
        r = check_door(door_info, self.SPACE_INFO)
        assert r["status"] == "pass"
        assert not any("double-leaf" in n for n in r["human_review_notes"])

    def test_double_leaf_missing_field_defaults_to_unaffected(self):
        """door_info 里没有 is_double_leaf 字段时(向前兼容旧数据), 不应报错也不应误判。"""
        door_info = {
            "global_id": "D4",
            "measured_width_mm": 900.0,
            "width_source": "overall_estimate",
        }
        r = check_door(door_info, self.SPACE_INFO)
        assert r["status"] == "pass"
