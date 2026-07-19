"""路由 /model — 上传 IFC + 摘要。

对应 docs/SSD.md §1 上传初始化。
"""
from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from ..core.pipeline import analyze_ifc
from ..session import create_session, get_session

router = APIRouter(prefix="/model", tags=["model"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_model(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".ifc"):
        raise HTTPException(status_code=400, detail={
            "error": "invalid_file", "detail": "only .ifc files accepted",
            "hint": "see samples/ directory for test files",
        })
    dest = UPLOAD_DIR / Path(file.filename).name
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        result = analyze_ifc(dest)
    except Exception as e:
        raise HTTPException(status_code=422, detail={
            "error": "ifc_parse_failed", "detail": str(e),
            "hint": "check IFC schema version or try another sample",
        })
    session = create_session(str(dest), file.filename, result)
    return {
        "session_id": session.id,
        "ifc_schema": result["schema"],
        "counts": result["counts"],
        "storeys": result["storeys"],
        "spaces": result["spaces"],
        "doors": result["doors"],
        "summary": result["summary"],
        "warnings": result.get("warnings", []),
    }


@router.get("/{sid}/summary")
def get_summary(sid: str):
    s = get_session(sid)
    if not s:
        raise HTTPException(status_code=404, detail={
            "error": "session_not_found", "detail": sid,
            "hint": "POST /model/upload to create a session",
        })
    r = s.result
    return {
        "session_id": s.id,
        "filename": s.filename,
        "ifc_schema": s.schema,
        "counts": {
            "spaces": len(r.get("spaces", [])),
            "doors": len(r.get("doors", [])),
            "storeys": len(r.get("storeys", [])),
        },
        "summary": r["summary"],
        "overrides": s.overrides,
    }
