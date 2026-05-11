"""图库与缩略图（Streamlit 缓存）。"""
import logging
import os

import streamlit as st
from PIL import Image

logger = logging.getLogger(__name__)

@st.cache_data(show_spinner=False, max_entries=256, ttl=3600)
def _load_thumbnail_cached(file_path: str, max_width: int, mtime_key: float):
    try:
        img = Image.open(file_path)
        if img.width > max_width:
            img.thumbnail((max_width, max_width * 2))
        return img
    except Exception as e:
        logger.warning("缩略图加载失败 %s: %s", file_path, e)
        return None


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
