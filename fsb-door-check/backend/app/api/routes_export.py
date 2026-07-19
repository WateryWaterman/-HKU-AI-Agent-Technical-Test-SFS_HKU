"""路由 /export — 导出检查结果(BCF/HTML/JSON)。

MVP 阶段返回 501 + EXPORT_DESIGN.md 链接,设计文档先行。
对应 docs/EXPORT_DESIGN.md。
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..session import get_session

router = APIRouter(tags=["export"])


@router.post("/export/{sid}")
def export_session(
    sid: str,
    fmt: str = Query(..., alias="format", description="bcf | html | json"),
):
    s = get_session(sid)
    if not s:
        raise HTTPException(status_code=404, detail={
            "error": "session_not_found", "detail": sid})
    fmt_lower = fmt.lower()
    if fmt_lower not in {"bcf", "html", "json"}:
        raise HTTPException(status_code=400, detail={
            "error": "invalid_format",
            "detail": f"unsupported format: {fmt_lower}",
            "hint": "choose one of: bcf, html, json",
        })
    raise HTTPException(status_code=501, detail={
        "error": "export_not_implemented",
        "detail": f"{fmt_lower} export is designed but not implemented in MVP",
        "hint": "see docs/EXPORT_DESIGN.md for the full design (BCF > HTML > JSON)",
        "design_doc": "docs/EXPORT_DESIGN.md",
        "planned_formats": {
            "bcf": "BIM Collaboration Format — Revit/Navisworks/Solibri native (首选)",
            "html": "self-contained single HTML report, email-friendly (次选)",
            "json": "machine-readable, same schema as /check/{sid} (兜底)",
        },
        "session_id": sid,
        "requested_format": fmt_lower,
    })
