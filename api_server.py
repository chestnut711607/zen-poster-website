"""Lightweight API layer for the Next.js migration.

Streamlit remains the current production UI. This FastAPI app exposes the
existing template config, gallery assets, and poster renderer so the new
Next.js frontend can be developed without rewriting the poster engine.
"""
from __future__ import annotations

import io
import json
import os
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from config import DEFAULT_COPY_DATA, TEMPLATE_MASTER_CONFIG, TEMPLATE_TYPES
from database import PHOTO_CATEGORIES, ZEN_PROJECT_SUBCATEGORIES, get_approved_photos
from poster import get_font_cache, paint_poster

ROOT = Path(__file__).resolve().parent
BACKGROUND_DIR = ROOT / "assets" / "backgrounds"

app = FastAPI(title="Poster Matrix API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if BACKGROUND_DIR.exists():
    app.mount("/static/backgrounds", StaticFiles(directory=str(BACKGROUND_DIR)), name="backgrounds")


def _public_background_url(path: Path) -> str:
    return f"/static/backgrounds/{path.name}"


def _local_backgrounds(category: str | None = None) -> list[dict]:
    if not BACKGROUND_DIR.exists():
        return []

    image_exts = {".jpg", ".jpeg", ".png", ".webp"}
    items = []
    for path in sorted(BACKGROUND_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in image_exts:
            continue
        guessed_category = next((c for c in PHOTO_CATEGORIES if c in path.stem), "其他")
        if category and category not in ("全部", guessed_category) and category not in path.stem:
            continue
        items.append(
            {
                "id": f"local-{path.name}",
                "filename": path.name,
                "category": guessed_category,
                "source": "local",
                "url": _public_background_url(path),
            }
        )
    return items


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/default-copy")
def default_copy() -> dict:
    return DEFAULT_COPY_DATA


@app.get("/api/template-types")
def template_types() -> list[dict]:
    return [
        {
            "name": name,
            "desc": cfg.get("desc", ""),
            "emoji": cfg.get("emoji", ""),
            "tag": cfg.get("tag", ""),
            "available": bool(cfg.get("available")),
            "templates": cfg.get("templates", []),
            "template_count": len(cfg.get("templates", [])),
            "preview_bg_color": cfg.get("preview_bg_color", "#F7F8FA"),
            "preview_text_color": cfg.get("preview_text_color", "#111827"),
        }
        for name, cfg in TEMPLATE_TYPES.items()
    ]


@app.get("/api/templates")
def templates(type_name: Annotated[str | None, Query(alias="type")] = None) -> list[dict]:
    names = list(TEMPLATE_MASTER_CONFIG.keys())
    if type_name:
        if type_name not in TEMPLATE_TYPES:
            raise HTTPException(status_code=404, detail="Unknown template type")
        names = TEMPLATE_TYPES[type_name].get("templates", [])

    return [
        {
            "name": name,
            "color": TEMPLATE_MASTER_CONFIG[name].get("color"),
            "bg_img": TEMPLATE_MASTER_CONFIG[name].get("bg_img"),
            "include": TEMPLATE_MASTER_CONFIG[name].get("include", []),
        }
        for name in names
        if name in TEMPLATE_MASTER_CONFIG
    ]


@app.get("/api/gallery")
def gallery(category: str | None = None) -> dict:
    local_items = _local_backgrounds(category)
    db_items = []
    for item in get_approved_photos(category=None if category in (None, "全部") else category):
        filepath = item.get("filepath") or ""
        db_items.append(
            {
                "id": f"db-{item.get('id')}",
                "filename": item.get("filename"),
                "category": item.get("category"),
                "source": "database",
                "filepath": filepath,
            }
        )
    return {
        "categories": ["全部", *PHOTO_CATEGORIES],
        "project_subcategories": ZEN_PROJECT_SUBCATEGORIES,
        "items": [*local_items, *db_items],
    }


def _save_upload(upload: UploadFile | None) -> str | None:
    if upload is None or not upload.filename:
        return None
    suffix = Path(upload.filename).suffix or ".png"
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        handle.write(upload.file.read())
        return handle.name
    finally:
        handle.close()


@app.post("/api/poster/render")
def render_poster(
    template_name: Annotated[str, Form()],
    data_json: Annotated[str, Form()] = "{}",
    background: Annotated[UploadFile | None, File()] = None,
    logo: Annotated[UploadFile | None, File()] = None,
    qr: Annotated[UploadFile | None, File()] = None,
):
    if template_name not in TEMPLATE_MASTER_CONFIG:
        raise HTTPException(status_code=404, detail="Unknown template")

    try:
        incoming = json.loads(data_json) if data_json else {}
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid data_json") from exc

    bg_path = _save_upload(background)
    logo_path = _save_upload(logo)
    qr_path = _save_upload(qr)
    data = {**DEFAULT_COPY_DATA, **incoming}

    try:
        image = paint_poster(
            template_name,
            TEMPLATE_MASTER_CONFIG[template_name],
            bg_path,
            logo_path,
            qr_path,
            data,
            get_font_cache(str(ROOT)),
            font_dir=str(ROOT),
        )
    finally:
        for path in (bg_path, logo_path, qr_path):
            if path and os.path.exists(path):
                os.unlink(path)

    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")
