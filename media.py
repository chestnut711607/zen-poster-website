"""图库与缩略图（Streamlit 缓存）。"""
import base64
import io
import logging
import os

import streamlit as st
from PIL import Image

logger = logging.getLogger(__name__)

try:
    _RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    _RESAMPLE = Image.LANCZOS


def _resize_to_max_width(img: Image.Image, max_width: int) -> Image.Image:
    if img.width <= max_width:
        return img
    ratio = max_width / float(img.width)
    new_h = max(1, int(round(img.height * ratio)))
    return img.resize((max_width, new_h), _RESAMPLE)


@st.cache_data(show_spinner=False, max_entries=256, ttl=3600)
def _load_thumbnail_cached(file_path: str, max_width: int, mtime_key: float):
    try:
        img = Image.open(file_path)
        if img.width > max_width:
            img.thumbnail((max_width, max_width * 2), _RESAMPLE)
        return img
    except Exception as e:
        logger.warning("缩略图加载失败 %s: %s", file_path, e)
        return None


@st.cache_data(show_spinner=False, max_entries=256, ttl=3600)
def _load_cover_preview_cached(
    file_path: str, display_width: int, pixel_ratio: float, mtime_key: float
):
    """仅缩小、不放大；最长边约为 display_width * pixel_ratio（供高清展示）。"""
    try:
        img = Image.open(file_path)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        max_w = max(display_width, int(round(display_width * pixel_ratio)))
        if img.width > max_w:
            img = _resize_to_max_width(img, max_w)
        return img
    except Exception as e:
        logger.warning("封面预览加载失败 %s: %s", file_path, e)
        return None


def load_cover_preview_image(
    file_path: str, display_width: int = 180, pixel_ratio: float = 3.0
):
    try:
        mt = os.path.getmtime(file_path)
    except OSError:
        mt = 0.0
    return _load_cover_preview_cached(file_path, display_width, pixel_ratio, mt)


def show_cover_preview(
    file_path: str, display_width: int = 180, pixel_ratio: float = 3.0
) -> bool:
    """
    模版封面展示：绕过 st.image 的二次压缩，用 PNG base64 + 固定 CSS 宽度。
    返回是否成功展示。
    """
    img = load_cover_preview_image(file_path, display_width, pixel_ratio)
    if img is None:
        return False
    buf = io.BytesIO()
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    img.save(buf, format="PNG", compress_level=1)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    w = int(display_width)
    st.markdown(
        f'<img src="data:image/png;base64,{b64}" width="{w}" '
        f'style="width:{w}px;max-width:100%;height:auto;display:block;border-radius:8px;" '
        f'alt="模版封面" />',
        unsafe_allow_html=True,
    )
    return True


def load_thumbnail_image(file_path: str, max_width: int = 300):
    try:
        mt = os.path.getmtime(file_path)
    except OSError:
        mt = 0.0
    return _load_thumbnail_cached(file_path, max_width, mt)


@st.cache_data(show_spinner=False, ttl=30)
def get_gallery_file_list(directory: str):
    try:
        if not os.path.exists(directory):
            return []
        files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        files.sort()
        return files
    except Exception as e:
        logger.warning("图库目录扫描失败 %s: %s", directory, e)
        return []
