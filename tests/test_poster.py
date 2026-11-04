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


def test_editor_refreshes_stale_template_config_without_losing_copy():
    from copy import deepcopy
    from unittest.mock import patch

    from streamlit.testing.v1 import AppTest
    from config import TEMPLATE_MASTER_CONFIG

    for number in range(1, 5):
        name = f"信息图表型C{number}"
        current = TEMPLATE_MASTER_CONFIG[name]
        stale = deepcopy(current)
        stale.pop("logo_anchor")
        stale["coords"]["logo"] = (500, current["coords"]["logo"][1])
        field = "sched_label_eg" if number <= 3 else "course_title_eg"
        app = AppTest.from_file(os.path.join(ROOT, "main.py"))
        app.session_state["step"] = 2
        app.session_state["chosen_template"] = (name, stale)
        app.session_state["last_template_name"] = name
        app.session_state[f"inp_{name}_{field}"] = "My schedule"

        with patch("download_fonts.download_fonts"), patch("poster.paint_poster", return_value=None) as render:
            app.run(timeout=20)
            assert not app.exception
            rendered_config = render.call_args.args[1]
            assert rendered_config["coords"]["logo"][0] == 540
            assert rendered_config["logo_anchor"] == "mm"
            assert render.call_args.args[5][field] == "My schedule"
