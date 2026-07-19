"""路由 /override — 人工覆盖(防火门/用途/人数/阈值/楼层标记)。

对应 docs/SSD.md §4 阈值覆盖、§5 标记防火门、§6 用途/人数覆盖。
对应 docs/CONTRACT.md §4 OverrideRequest schema。
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from ..core.presets import compute_capacity, get_default_factor_for_use_class
from ..core.rule_engine import check_door
from ..models.schemas import OverrideRequest
from ..session import Session, get_session

router = APIRouter(prefix="/override", tags=["override"])


@router.post("/{sid}")
def apply_override(sid: str, req: OverrideRequest):
    s = get_session(sid)
    if not s:
        raise HTTPException(status_code=404, detail={
            "error": "session_not_found", "detail": sid})

    affected: list[dict[str, Any]] = []

    if req.type == "fire_exit":
        affected = _override_fire_exit(s, req)
    elif req.type == "space_use":
        affected = _override_space_use(s, req)
    elif req.type == "occupancy":
        affected = _override_occupancy(s, req)
    elif req.type == "threshold":
        affected = _override_threshold(s, req)
    elif req.type in ("storey_sprinkler", "storey_entrance"):
        affected = _override_storey(s, req)
    else:
        raise HTTPException(status_code=400, detail={
            "error": "invalid_override_type", "detail": req.type,
            "hint": "valid types: fire_exit | space_use | occupancy | threshold | storey_sprinkler | storey_entrance"})

    s.overrides.append(req.model_dump())
    s.result["summary"] = _rebuild_summary(s.result.get("doors", []))
    return {"session_id": sid, "applied": req.model_dump(), "affected_results": affected}


def _override_fire_exit(s: Session, req: OverrideRequest) -> list[dict[str, Any]]:
    s.door_fire_exit_overrides[req.global_id] = bool(req.value)
    door = s.find_door(req.global_id)
    if door:
        door["is_fire_exit"] = bool(req.value)
        door["fire_exit_source"] = "user_override" if bool(req.value) else "not_fire_exit"
        if door.get("check_result"):
            return [door["check_result"]]
    return []


def _override_space_use(s: Session, req: OverrideRequest) -> list[dict[str, Any]]:
    s.space_use_overrides[req.global_id] = str(req.value)
    space = s.find_space(req.global_id)
    if not space:
        return []
    factor_info = get_default_factor_for_use_class(str(req.value))
    space["use_class"] = str(req.value)
    space["use_class_source"] = "user_override"
    space["use_class_accommodation"] = factor_info.get("accommodation") if factor_info else None
    if factor_info:
        space["factor"] = factor_info["factor"]
        space["factor_type"] = factor_info["factor_type"]
        if factor_info["factor_type"] == "area_per_person_m2" and space.get("area_m2"):
            cap, _ = compute_capacity(space["area_m2"], factor_info["factor"], factor_info["factor_type"])
            space["occupant_capacity"] = cap
            space["capacity_source"] = "table_b1_factor"
    return _recheck_doors_of_space(s, req.global_id, space)


def _override_occupancy(s: Session, req: OverrideRequest) -> list[dict[str, Any]]:
    s.space_occupancy_overrides[req.global_id] = int(req.value)
    space = s.find_space(req.global_id)
    if not space:
        return []
    space["occupant_capacity"] = int(req.value)
    space["capacity_source"] = "user_input"
    return _recheck_doors_of_space(s, req.global_id, space)


def _override_threshold(s: Session, req: OverrideRequest) -> list[dict[str, Any]]:
    to = req.value
    if not isinstance(to, dict) or "capacity_min" not in to or "min_width_per_door_mm" not in to:
        raise HTTPException(status_code=400, detail={
            "error": "invalid_threshold_override", "detail": "value must have capacity_min, capacity_max(optional), min_width_per_door_mm"})
    cmin = int(to["capacity_min"])
    cmax = to.get("capacity_max")
    new_w = float(to["min_width_per_door_mm"])
    s.preset_overrides[(cmin, cmax)] = new_w
    affected: list[dict[str, Any]] = []
    for d in s.result.get("doors", []):
        cr = d.get("check_result") or {}
        cap = cr.get("occupant_capacity")
        if cap is None:
            continue
        upper = cmax if cmax is not None else 999999
        if cmin <= cap <= upper:
            space = s.find_space(d.get("space_global_id")) or {
                "capacity": cap, "capacity_source": cr.get("capacity_source", "unknown")}
            new_result = check_door(
                d, space,
                override_threshold_mm=new_w,
                override_threshold_source=f"user_override row[{cmin}-{cmax}]",
            )
            d["check_result"] = new_result
            affected.append(new_result)
    return affected


def _override_storey(s: Session, req: OverrideRequest) -> list[dict[str, Any]]:
    if req.type == "storey_sprinkler":
        s.storey_sprinkler_overrides[req.global_id] = bool(req.value)
    else:
        s.storey_entrance_overrides[req.global_id] = bool(req.value)
    storey = s.find_storey(req.global_id)
    if storey:
        if req.type == "storey_sprinkler":
            storey["has_sprinkler"] = bool(req.value)
        else:
            storey["is_entrance_level"] = bool(req.value)
    return []


def _recheck_doors_of_space(s: Session, space_gid: str, space: dict) -> list[dict[str, Any]]:
    affected: list[dict[str, Any]] = []
    for d in s.result.get("doors", []):
        if d.get("space_global_id") != space_gid:
            continue
        override_threshold = _match_preset_override(s, space.get("occupant_capacity"))
        new_result = check_door(
            d, space,
            override_threshold_mm=override_threshold.get("threshold"),
            override_threshold_source=override_threshold.get("source"),
        )
        d["check_result"] = new_result
        affected.append(new_result)
    return affected


def _match_preset_override(s: Session, capacity) -> dict[str, Any]:
    if capacity is None:
        return {}
    for (cmin, cmax), new_w in s.preset_overrides.items():
        upper = cmax if cmax is not None else 999999
        if cmin <= capacity <= upper:
            return {"threshold": new_w, "source": f"user_override row[{cmin}-{cmax}]"}
    return {}


def _rebuild_summary(doors: list[dict[str, Any]]) -> dict[str, Any]:
    by_status = {"pass": 0, "fail": 0, "unknown": 0, "overridden": 0}
    fire_exit_count = 0
    needs_review_count = 0
    fails: list[dict[str, Any]] = []
    for d in doors:
        cr = d.get("check_result") or {}
        status = cr.get("status", "unknown")
        if status in by_status:
            by_status[status] += 1
        if d.get("is_fire_exit"):
            fire_exit_count += 1
        if cr.get("needs_human_review"):
            needs_review_count += 1
        if status == "fail":
            fails.append(cr)
    fails.sort(key=lambda c: c.get("deficit_mm") or 0, reverse=True)
    return {
        "total_doors": len(doors),
        "checked_doors": fire_exit_count,
        "by_status": by_status,
        "needs_review_count": needs_review_count,
        "top_fails": fails[:5],
    }
