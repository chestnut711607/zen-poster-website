"""海报四步核心流程的 FastAPI 后端（React 前端用）。

Streamlit 版（main.py）保持可用；本服务复用同一套 config.py / poster.py 渲染引擎。
启动：.venv/bin/python -m uvicorn api_server:app --reload --port 8000
"""
from __future__ import annotations

import io
import json
import tempfile
import urllib.parse
import uuid
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps

from config import DEFAULT_COPY_DATA, TEMPLATE_MASTER_CONFIG, TEMPLATE_TYPES
from poster import get_font_cache, paint_poster

ROOT = Path(__file__).resolve().parent
BG_DIR = ROOT / "assets" / "backgrounds"
UPLOAD_DIR = Path(tempfile.gettempdir()) / "zen_poster_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Zen Poster API", version="0.1.0")

# 开发阶段允许任意 localhost 端口（Vite/Kimi Work 预览端口会变）
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if BG_DIR.exists():
    app.mount("/static/backgrounds", StaticFiles(directory=str(BG_DIR)), name="backgrounds")


# ---------------------------------------------------------------- 元数据接口

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
            "template_count": len(cfg.get("templates", [])),
            "preview_bg_color": cfg.get("preview_bg_color", "#F7F8FA"),
            "preview_text_color": cfg.get("preview_text_color", "#111827"),
        }
        for name, cfg in TEMPLATE_TYPES.items()
    ]


@app.get("/api/templates")
def templates(type_name: Annotated[str | None, Query(alias="type")] = None) -> list[dict]:
    if type_name:
        if type_name not in TEMPLATE_TYPES:
            raise HTTPException(status_code=404, detail="Unknown template type")
        names = TEMPLATE_TYPES[type_name].get("templates", [])
    else:
        names = list(TEMPLATE_MASTER_CONFIG.keys())
    return [
        {
            "name": name,
            "color": TEMPLATE_MASTER_CONFIG[name].get("color"),
            "bg_img": TEMPLATE_MASTER_CONFIG[name].get("bg_img"),
            "include": TEMPLATE_MASTER_CONFIG[name].get("include", []),
            "field_defaults": TEMPLATE_MASTER_CONFIG[name].get("field_defaults", {}),
        }
        for name in names
        if name in TEMPLATE_MASTER_CONFIG
    ]


@app.get("/api/gallery")
def gallery() -> dict:
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    items = []
    if BG_DIR.exists():
        for path in sorted(BG_DIR.iterdir()):
            if path.is_file() and path.suffix.lower() in exts:
                items.append({
                    "name": path.name,
                    "url": f"/static/backgrounds/{path.name}",
                    "thumb": f"/api/thumb/{path.name}",
                })
    return {"items": items}


@lru_cache(maxsize=256)
def _thumb_bytes(name: str) -> bytes:
    path = BG_DIR / name
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((480, 480), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=82)
    return buf.getvalue()


@app.get("/api/thumb/{name}")
def thumbnail(name: str) -> Response:
    """图库缩略图：限制 480px + JPEG，列表加载快；选中后渲染仍用原图。"""
    if "/" in name or "\\" in name:
        raise HTTPException(status_code=400, detail="非法文件名")
    if not (BG_DIR / name).is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    return Response(content=_thumb_bytes(name), media_type="image/jpeg",
                    headers={"Cache-Control": "private, max-age=86400"})


# ---------------------------------------------------------------- 模版文件下载

# 每个系列一个子目录，把 PPT / PSD / ZIP 等模版文件放进去即可，前端自动出现下载按钮
TEMPLATE_FILES_DIR = ROOT / "template_files"


def _series_dir(type_name: str) -> Path | None:
    """系列目录：仅允许 TEMPLATE_TYPES 里的名字，杜绝路径穿越。"""
    if type_name not in TEMPLATE_TYPES:
        return None
    d = TEMPLATE_FILES_DIR / type_name
    return d if d.is_dir() else None


@app.get("/api/template-files")
def template_files() -> dict:
    """各系列可下载的模版文件列表（无文件的系列返回空数组）。"""
    result: dict[str, list[dict]] = {}
    for name in TEMPLATE_TYPES:
        d = _series_dir(name)
        files = []
        if d:
            for p in sorted(d.iterdir()):
                if p.is_file() and not p.name.startswith("."):
                    files.append({"name": p.name, "size": p.stat().st_size})
        result[name] = files
    return result


@app.get("/api/template-files/{type_name}/download")
def download_template_files(type_name: str) -> Response:
    """把该系列目录下的所有模版文件打成 ZIP 返回。"""
    d = _series_dir(type_name)
    if d is None:
        raise HTTPException(status_code=404, detail="未知系列")
    files = [p for p in sorted(d.iterdir()) if p.is_file() and not p.name.startswith(".")]
    if not files:
        raise HTTPException(status_code=404, detail="该系列暂无可下载文件")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zf.write(p, arcname=p.name)
    zip_name = f"静心学堂-{type_name}模版.zip"
    quoted = urllib.parse.quote(zip_name)
    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quoted}"},
    )


# ---------------------------------------------------------------- 上传

_UPLOAD_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    """上传一次，后续渲染用返回的 id 引用，避免逐字预览时重复传图。"""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _UPLOAD_EXTS:
        raise HTTPException(status_code=400, detail="仅支持 JPG / PNG / WebP")
    file_id = f"{uuid.uuid4().hex}{suffix}"
    (UPLOAD_DIR / file_id).write_bytes(await file.read())
    return {"id": file_id}


def _resolve_ref(kind: str, ref: str | None) -> str | None:
    """kind='bg' 找图库，kind='upload' 找上传目录；拒绝路径穿越。"""
    if not ref:
        return None
    if "/" in ref or "\\" in ref:
        raise HTTPException(status_code=400, detail="非法文件名")
    base = BG_DIR if kind == "bg" else UPLOAD_DIR
    path = base / ref
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"文件不存在: {ref}")
    return str(path)


# ---------------------------------------------------------------- 渲染

@lru_cache(maxsize=128)
def _render_cached(template_name: str, data_tuple: tuple, bg_path: str | None,
                   logo_path: str | None, qr_path: str | None,
                   transform_tuple: tuple, width: int, fmt: str,
                   overlay_only: bool) -> bytes:
    cfg = TEMPLATE_MASTER_CONFIG[template_name]
    data = dict(data_tuple)
    transform = dict(transform_tuple)
    font_cache = get_font_cache(str(ROOT))
    if overlay_only:
        img = paint_poster(template_name, cfg, None, logo_path, qr_path, data,
                           font_cache, font_dir=str(ROOT), transparent_background=True)
        out_fmt, mode = "PNG", "RGBA"
    else:
        img = paint_poster(template_name, cfg, bg_path, logo_path, qr_path, data,
                           font_cache, font_dir=str(ROOT), bg_transform=transform)
        if width and width != img.width:
            img = img.resize((width, int(width * img.height / img.width)),
                             Image.Resampling.LANCZOS)
        if fmt == "jpeg":
            out_fmt, mode = "JPEG", "RGB"
        else:
            out_fmt, mode = "PNG", "RGBA"
    buf = io.BytesIO()
    if out_fmt == "JPEG":
        img.convert(mode).save(buf, format=out_fmt, quality=88)
    else:
        img.convert(mode).save(buf, format=out_fmt)
    return buf.getvalue()


@app.post("/api/render")
def render(
    template_name: Annotated[str, Form()],
    data_json: Annotated[str, Form()] = "{}",
    bg_name: Annotated[str | None, Form()] = None,
    bg_upload_id: Annotated[str | None, Form()] = None,
    logo_upload_id: Annotated[str | None, Form()] = None,
    qr_upload_id: Annotated[str | None, Form()] = None,
    transform_json: Annotated[str, Form()] = "{}",
    width: Annotated[int, Form()] = 1080,
    format: Annotated[str, Form()] = "png",
    overlay_only: Annotated[bool, Form()] = False,
) -> Response:
    if template_name not in TEMPLATE_MASTER_CONFIG:
        raise HTTPException(status_code=404, detail="Unknown template")
    try:
        incoming = json.loads(data_json) if data_json else {}
        transform = json.loads(transform_json) if transform_json else {}
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="JSON 参数不合法") from exc

    bg_path = _resolve_ref("bg", bg_name) if bg_name else _resolve_ref("upload", bg_upload_id)
    logo_path = _resolve_ref("upload", logo_upload_id)
    qr_path = _resolve_ref("upload", qr_upload_id)

    data = {**DEFAULT_COPY_DATA, **incoming}
    transform = {k: float(transform.get(k, 0 if k != "scale" else 1))
                 for k in ("scale", "x", "y")}
    width = max(135, min(1080, int(width)))
    fmt = "jpeg" if format == "jpeg" else "png"

    payload = _render_cached(
        template_name, tuple(sorted(data.items())), bg_path, logo_path, qr_path,
        tuple(sorted(transform.items())), width, fmt, overlay_only,
    )
    media = "image/jpeg" if fmt == "jpeg" else "image/png"
    return Response(content=payload, media_type=media,
                    headers={"Cache-Control": "private, max-age=3600"})
