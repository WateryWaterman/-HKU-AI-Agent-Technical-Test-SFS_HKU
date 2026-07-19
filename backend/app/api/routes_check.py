"""路由 /check + /doors — 检查结果 + 单门详情。

对应 docs/SSD.md §2 点选门、§3 触发检查。
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from ..session import get_session

router = APIRouter(tags=["check"])


@router.post("/check/{sid}")
def run_check(sid: str):
    s = get_session(sid)
    if not s:
        raise HTTPException(status_code=404, detail={
            "error": "session_not_found", "detail": sid})
    results = [d["check_result"] for d in s.result.get("doors", []) if d.get("check_result")]
    return {
        "session_id": sid,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "summary": s.result["summary"],
    }


@router.get("/doors/{gid}")
def get_door(gid: str, session: str = Query(..., description="session_id")):
    s = get_session(session)
    if not s:
        raise HTTPException(status_code=404, detail={
            "error": "session_not_found", "detail": session})
    door = s.find_door(gid)
    if not door:
        raise HTTPException(status_code=404, detail={
            "error": "door_not_found", "detail": gid,
            "hint": "the global_id may exist in xeokit but not in backend model (IFC4 geometry-only case)"})
    related_space = None
    if door.get("space_global_id"):
        related_space = s.find_space(door["space_global_id"])
    storey = None
    if door.get("storey_global_id"):
        storey = s.find_storey(door["storey_global_id"])
    return {"door": door, "related_space": related_space, "storey": storey}
