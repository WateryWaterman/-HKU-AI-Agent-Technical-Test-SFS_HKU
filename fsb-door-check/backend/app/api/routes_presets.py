"""路由 /presets — 默认预设查询。

对应 docs/SSD.md §1 前端首屏展示默认 preset + longname map。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..core.presets import load_longname_map, load_presets
from ..session import get_session

router = APIRouter(prefix="/presets", tags=["presets"])


@router.get("")
def get_presets():
    return {"default": load_presets(), "longname_map": load_longname_map()}


@router.get("/{sid}")
def get_session_presets(sid: str):
    s = get_session(sid)
    if not s:
        raise HTTPException(status_code=404, detail={
            "error": "session_not_found", "detail": sid})
    base = load_presets()
    if s.preset_overrides:
        base = dict(base)
        table = list(base.get("table_b2_thresholds", []))
        for (cmin, cmax), new_w in s.preset_overrides.items():
            for row in table:
                if row.get("capacity_min") == cmin and row.get("capacity_max") == cmax:
                    row["min_width_per_door_mm"] = new_w
                    row["_overridden"] = True
        base["table_b2_thresholds"] = table
    base["active_overrides"] = s.overrides
    return base
