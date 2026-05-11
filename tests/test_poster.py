"""Smoke tests for poster rendering (no Streamlit server)."""
from __future__ import annotations

import os
import sys

# Ensure repo root is importable when pytest cwd is project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_paint_poster_b1_canvas_size():
    from config import DEFAULT_COPY_DATA, TEMPLATE_MASTER_CONFIG
    from poster import _template_field_default, get_font_cache, paint_poster

    name = "文案主导型B1"
    cfg = TEMPLATE_MASTER_CONFIG[name]
    data = {
        k: _template_field_default(cfg, k, DEFAULT_COPY_DATA)
        for k in cfg["include"]
        if k not in ("logo", "qr")
    }
    font_cache = get_font_cache(ROOT)
    img = paint_poster(name, cfg, None, None, None, data, font_cache, font_dir=ROOT)
    assert img is not None
    assert img.size == (1080, 1920)
