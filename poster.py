"""海报渲染、字体缓存与 Step1 预览。"""
import logging
import os

import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps

from config import (
    CERT_BODY_MAX_WIDTH_PX_DEFAULT,
    CERT_TITLE_CN_TRACKING_PX_DEFAULT,
    COURSE_QR_TIP_SPACING_CN,
    COURSE_QR_TIP_SPACING_EG,
    COURSE_TITLE_C56_VERT_SPACING,
    COURSE_TITLE_CN_MULTILINE_SPACING,
    DAY_DATE_C56_TRACKING_PX,
    SIZE_QR,
    SLOGAN_FILENAME,
    SLOGAN_MIN_EDGE_GAP,
    SLOGAN_TARGET_WIDTH_PX,
    TEMPLATE_MASTER_CONFIG,
    is_cert_template,
    is_info_chart_c56,
)

logger = logging.getLogger(__name__)

_POSTER_ROOT = os.path.dirname(os.path.abspath(__file__))


def _poster_font_dir(font_dir: str | None) -> str:
    return font_dir if font_dir is not None else _POSTER_ROOT

@st.cache_resource
def get_font_cache(path):
    fonts = {}
    font_files = {
        'main': 'SourceHanSerifSC-SemiBold.otf',
        'sub': 'SourceHanSerifSC-SemiBold.otf',
        'sub2': 'SourceHanSerifSC-SemiBold.otf',
        'label': 'HarmonyOS_Sans_SC_Medium.ttf',
        'content': 'HarmonyOS_Sans_SC_Light.ttf',
        'date_big': 'HarmonyOS_Sans_SC_Light.ttf',
        'time': 'HarmonyOS_Sans_SC_Light.ttf',
        'qr_text': 'HarmonyOS_Sans_SC_Light.ttf',
        'sched_label_cn': 'SourceHanSerifCN-Medium.otf',
        'sched_label_eg': 'HarmonyOS_Sans_SC_Light.ttf',
        'sched_num': 'SourceHanSerifCN-Medium.otf',
        'sched_name_cn': 'HarmonyOS_Sans_SC_Light.ttf',
        'sched_name_eg': 'HarmonyOS_Sans_SC_Light.ttf',
        'sched_time': 'HarmonyOS_Sans_SC_Regular.ttf',
        'day_time': 'HarmonyOS_Sans_SC_Light.ttf',
        'day_cont': 'HarmonyOS_Sans_SC_Light.ttf',
        # C5/C6「课程安排」竖排四字（与 C4 的 course_title_cn 字体区分）
        'course_title_c56_cn': 'Huiwen-MinchoGBK-Regular.ttf',
        'course_date_range': 'Huiwen-MinchoGBK-Regular.ttf',
        # C5/C6 每日日期 day_date_*：与 sched_label_cn 同字族，字号 56
        'day_date_c56': 'SourceHanSerifCN-Medium.otf',
    }
    sizes = {
        'main': 64, 'sub': 36, 'sub2': 32,
        'label': 32,
        'content': 32, 'date_big': 80, 'time': 40, 'qr_text': 25,
        'sched_label_cn': 72,
        'sched_label_eg': 36,
        'sched_num': 72,
        'sched_name_cn': 50,
        'sched_name_eg': 36,
        'sched_time': 30,
        'day_time': 30,
        'day_cont': 28,
        'course_title_c56_cn': 72,
        'course_date_range': 88,
        'day_date_c56': 64,
    }
    for key, filename in font_files.items():
        full_path = os.path.join(path, filename)
        try:
            size = sizes[key]
            fonts[key] = ImageFont.truetype(full_path, size)
        except IOError:
            fonts[key] = ImageFont.load_default()
    try:
        fonts['label_34'] = ImageFont.truetype(os.path.join(path, 'HarmonyOS_Sans_SC_Medium.ttf'), 34)
    except:
        fonts['label_34'] = fonts['label']
    return fonts

@st.cache_resource
def _cert_draw_fonts(base_path: str):
    """认证证书型（is_cert_template）字段专用字体（字号按设计稿）。"""
    specs = {
        "cert_greeting": ("Huiwen-MinchoGBK-Regular.ttf", 48),
        "cert_name": ("SourceHanSerifSC-SemiBold.otf", 56),
        "cert_body": ("Huiwen-MinchoGBK-Regular.ttf", 40),
        "cert_title_cn": ("SourceHanSerifCN-Heavy.otf", 62),
        "cert_title_eg": ("SourceHanSerifSC-SemiBold.otf", 32),
        "cert_issuer": ("SourceHanSerifSC-SemiBold.otf", 36),
        "cert_issue_date": ("SourceHanSerifSC-SemiBold.otf", 36),
        "cert_footer": ("HarmonyOS_Sans_SC_Light.ttf", 36),
    }
    out = {}
    for key, (fn, sz) in specs.items():
        fp = os.path.join(base_path, fn)
        try:
            out[key] = ImageFont.truetype(fp, sz)
        except OSError:
            out[key] = ImageFont.load_default()
    return out

def _cert_char_pixel_width(draw, ch, font) -> float:
    if hasattr(font, "getlength"):
        return float(font.getlength(ch))
    b = draw.textbbox((0, 0), ch, font=font, anchor="la")
    return float(b[2] - b[0])


def _cert_wrap_single_line(draw, line: str, font, max_w: float) -> str:
    """单行按字累加宽度，超过 max_w 则换行（中文为主）。"""
    if not line or max_w <= 0:
        return line
    parts = []
    buf = ""
    run = 0.0
    for ch in line:
        w = _cert_char_pixel_width(draw, ch, font)
        if buf and run + w > max_w:
            parts.append(buf)
            buf = ch
            run = w
        else:
            buf += ch
            run += w
    if buf:
        parts.append(buf)
    return "\n".join(parts)


def _cert_wrap_body_text(draw, text: str, font, max_w: float) -> str:
    """保留用户原有换行，再在每一行内按宽度折行。"""
    if not text:
        return text
    return "\n".join(_cert_wrap_single_line(draw, seg, font, max_w) for seg in text.split("\n"))


def _draw_text_tracked_horizontal(draw, xy, text, font, fill, anchor, extra_px):
    """单行横向逐字绘制并在字间加入 extra_px（PIL 的 draw.text 无字距参数）。"""
    if not text:
        return
    x, y = float(xy[0]), float(xy[1])
    chars = list(text)
    if len(chars) == 1:
        draw.text(xy, text, font=font, fill=fill, anchor=anchor)
        return

    def _advance(ch):
        if hasattr(font, "getlength"):
            return float(font.getlength(ch))
        bbox = draw.textbbox((0, 0), ch, font=font, anchor="la")
        return float(bbox[2] - bbox[0])

    n = len(chars)
    gaps = max(0, n - 1)
    total = sum(_advance(ch) for ch in chars) + float(extra_px) * gaps
    a = (anchor or "la").lower()
    if a == "la":
        x0 = x
    elif a == "ra":
        x0 = x - total
    elif a in ("ma", "mm", "md", "mt", "mb", "lm", "rm"):
        x0 = x - total / 2.0
    else:
        x0 = x

    cx = x0
    for i, ch in enumerate(chars):
        draw.text((cx, y), ch, font=font, fill=fill, anchor="la")
        cx += _advance(ch)
        if i < n - 1:
            cx += float(extra_px)


def _draw_multiline_line_gap(draw, xy, text, font, fill, anchor, gap_px):
    """多行竖排：按行绘制，行距 = 上行油墨框底边 + gap_px（与模版 anchor 一致）。"""
    lines = text.split("\n")
    if not any(lines):
        return
    if len(lines) == 1:
        draw.text(xy, lines[0], font=font, fill=fill, anchor=anchor)
        return
    x, y = float(xy[0]), float(xy[1])
    cur = y
    for i, line in enumerate(lines):
        draw.text((x, cur), line, font=font, fill=fill, anchor=anchor)
        if i >= len(lines) - 1:
            break
        b = draw.textbbox((x, cur), line, font=font, anchor=anchor)
        cur = float(b[3]) + float(gap_px)


def _draw_multiline_hcenter_top_la(draw, center_x, y_top, text, font, fill, spacing):
    """多行：每一行单独水平居中于 center_x；y_top 为第一行油墨顶边；行间加 spacing（与 draw.text 多行行距一致）。"""
    if not text:
        return
    lines = text.split("\n")
    cur_top = float(y_top)
    for i, line in enumerate(lines):
        if line == "":
            tb_spc = draw.textbbox((0, 0), "\u3000", font=font, anchor="la")
            cur_top += float(tb_spc[3] - tb_spc[1]) + float(spacing)
            continue
        tb0 = draw.textbbox((0, 0), line, font=font, anchor="la")
        x = float(center_x) - (tb0[0] + tb0[2]) / 2.0
        y = cur_top - float(tb0[1])
        draw.text((x, y), line, font=font, fill=fill, anchor="la")
        if i >= len(lines) - 1:
            break
        b = draw.textbbox((x, y), line, font=font, anchor="la")
        cur_top = float(b[3]) + float(spacing)


def _draw_multiline_left_top_la(draw, left_x, y_top, text, font, fill, spacing):
    """多行：各行左对齐于 left_x；y_top 为第一行油墨顶边；行间加 spacing。"""
    if not text:
        return
    lines = text.split("\n")
    cur_top = float(y_top)
    for i, line in enumerate(lines):
        if line == "":
            tb_spc = draw.textbbox((0, 0), "\u3000", font=font, anchor="la")
            cur_top += float(tb_spc[3] - tb_spc[1]) + float(spacing)
            continue
        tb0 = draw.textbbox((0, 0), line, font=font, anchor="la")
        x = float(left_x)
        y = cur_top - float(tb0[1])
        draw.text((x, y), line, font=font, fill=fill, anchor="la")
        if i >= len(lines) - 1:
            break
        b = draw.textbbox((x, y), line, font=font, anchor="la")
        cur_top = float(b[3]) + float(spacing)


def _draw_multiline_hcenter_tracked_top_la(draw, center_x, y_top, text, font, fill, spacing, extra_px):
    """多行：各行相对 center_x 水平居中，行内字间距 extra_px（与 _draw_text_tracked_horizontal 一致）。"""
    if not text:
        return
    lines = text.split("\n")
    cur_top = float(y_top)
    for i, line in enumerate(lines):
        if line == "":
            tb_spc = draw.textbbox((0, 0), "\u3000", font=font, anchor="la")
            cur_top += float(tb_spc[3] - tb_spc[1]) + float(spacing)
            continue
        tb0 = draw.textbbox((0, 0), line, font=font, anchor="la")
        y = cur_top - float(tb0[1])
        _draw_text_tracked_horizontal(draw, (center_x, y), line, font, fill, "ma", extra_px)
        x_left = float(center_x) - (tb0[0] + tb0[2]) / 2.0
        b = draw.textbbox((x_left, y), line, font=font, anchor="la")
        cur_top = float(b[3]) + float(spacing)



def _template_field_default(cfg, key, fallback_dict):
    fd = cfg.get("field_defaults", {})
    if key in fd:
        return fd[key]
    return fallback_dict.get(key, "")


def paint_poster(name, cfg, up_bg, up_logo, up_qr, data, font_cache, font_dir: str | None = None):
    path = _poster_font_dir(font_dir)
    bg_rel = (cfg.get("bg_img") or "").strip()
    bg_file = os.path.join(path, bg_rel) if bg_rel else ""
    canvas_size = (1080, 1920)
    if up_bg:
        try:
            if isinstance(up_bg, str):
                user_bg_img = Image.open(up_bg).convert("RGBA")
            else:
                user_bg_img = Image.open(up_bg).convert("RGBA")
            canvas = ImageOps.fit(user_bg_img, canvas_size)
        except Exception:
            canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 255))
    else:
        if is_cert_template(name):
            # 无用户底图时：浅灰蓝底 + 深色字，便于类型页/选模版预览（非用户提供的参考图）
            canvas = Image.new("RGBA", canvas_size, (236, 242, 248, 255))
        else:
            canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 255))
    # 装饰层（含认证证书 bg_cert*.png）：画在用户背景之上，RGBA 透明区域可透出下层
    if bg_file and os.path.exists(bg_file):
        try:
            decoration = Image.open(bg_file).convert("RGBA")
            if decoration.size != canvas_size:
                decoration = decoration.resize(canvas_size, Image.Resampling.LANCZOS)
            canvas.paste(decoration, (0, 0), decoration)
        except Exception:
            logger.debug("装饰层加载失败: %s", bg_file, exc_info=True)
    draw = ImageDraw.Draw(canvas)
    color = cfg["color"]
    anchor = cfg["align"]
    c = cfg["coords"]
    inc = cfg["include"]
    try:
        t_num = int(''.join(filter(str.isdigit, name)))
    except:
        t_num = 0
    f_main = font_cache['main']
    f_sub = font_cache['sub']
    f_sub2 = font_cache['sub2']
    f_content = font_cache['content']
    f_date_big = font_cache['date_big']
    f_time = font_cache['time']
    f_sched_label_cn=font_cache['sched_label_cn']
    f_sched_label_eg=font_cache['sched_label_eg']
    f_sched_time=font_cache['sched_time']
    f_day_time=font_cache.get('day_time', font_cache['sched_time'])
    f_sched_num=font_cache['sched_num']
    f_sched_name_cn=font_cache['sched_name_cn']
    f_sched_name_eg=font_cache['sched_name_eg']
    f_day_cont = font_cache['day_cont']
    f_course_title_c56_cn = font_cache.get('course_title_c56_cn', f_sched_label_cn)
    f_course_date_range = font_cache.get(
        'course_date_range', font_cache.get('course_title_c56_cn', f_sched_label_cn)
    )
    f_day_date_c56 = font_cache.get('day_date_c56', f_sched_label_cn)
    f_qr_text = font_cache['qr_text']
    cert_draw_fonts = _cert_draw_fonts(path) if is_cert_template(name) else None
    label_size = 32 if 3 <= t_num <= 8 else 34
    f_label = font_cache['label'] if label_size == 32 else font_cache.get('label_34', font_cache['label'])
    if up_logo and "logo" in c and "logo" in inc:
        try:
            l_img = Image.open(up_logo).convert("RGBA")
            target_h = 68
            ratio = target_h / float(l_img.size[1])
            target_w = int(float(l_img.size[0]) * ratio)
            l_img = l_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            lx, ly = c["logo"]
            if anchor == "mm": paste_x = lx - (target_w // 2)
            elif anchor == "ra": paste_x = lx - target_w
            else: paste_x = lx
            canvas.paste(l_img, (paste_x, ly), l_img)
        except Exception: pass
    fields = [
        "title_text_cn", "title_text_eg", "title_text_mm1", "title_text_mm2",
        "date_year_week", "date_num", "date_time",
        "prog_label_bil", "prog_cont_cn_a", "prog_cont_cn_b", "prog_cont_eg",
        "prog_label_cn", "prog_label_eg",
        "venue_label_bil", "venue_label_cn", "venue_label_eg",
        "venue_cont_cn_a", "venue_cont_cn_b", "venue_cont_cn_c", "venue_cont_eg",
        "qr_label_bil", "qr_label_cn", "qr_label_eg",
        "qr_tip_a", "qr_tip_b", "qr_tip_eg",
        # ── 信息图表型 C1/C2/C3：单日流程 ──
        "sched_label_cn", "sched_label_eg",
        "sched_num_1", "sched_name_cn_1", "sched_name_eg_1", "sched_time_1",
        "sched_num_2", "sched_name_cn_2", "sched_name_eg_2", "sched_time_2",
        "sched_num_3", "sched_name_cn_3", "sched_name_eg_3", "sched_time_3",
        "sched_num_4", "sched_name_cn_4", "sched_name_eg_4", "sched_time_4",
        "sched_num_5", "sched_name_cn_5", "sched_name_eg_5", "sched_time_5",
        "sched_num_6", "sched_name_cn_6", "sched_name_eg_6", "sched_time_6",
        "sched_num_7", "sched_name_cn_7", "sched_name_eg_7", "sched_time_7",
        # ── 信息图表型 C4–C6：多日课程安排 ──
        "course_title_cn", "course_title_eg", "course_date_range", "course_slogan",
        "course_qr_tip_cn", "course_qr_tip_eg",
        "day_date_1", "day_week_1", "day_time_1", "day_cont_1", "day_time2_1", "day_cont2_1",
        "day_date_2", "day_week_2", "day_time_2", "day_cont_2", "day_time2_2", "day_cont2_2",
        "day_date_3", "day_week_3", "day_time_3", "day_cont_3", "day_time2_3", "day_cont2_3",
        "day_date_4", "day_week_4", "day_time_4", "day_cont_4", "day_time2_4", "day_cont2_4",
        "day_date_5", "day_week_5", "day_time_5", "day_cont_5", "day_time2_5", "day_cont2_5",
        "day_date_6", "day_week_6", "day_time_6", "day_cont_6", "day_time2_6", "day_cont2_6",
        "day_date_7", "day_week_7", "day_time_7", "day_cont_7", "day_time2_7", "day_cont2_7",
        # ── 认证证书型 D1–D4 ──
        "cert_brand_tl",
        "cert_greeting",
        "cert_name",
        "cert_body",
        "cert_title_cn",
        "cert_title_eg",
        "cert_issuer",
        "cert_issue_date",
        "cert_footer",
    ]
    for field in fields:
        if field in inc and field in c:
            if field == "course_slogan":
                slogan_fn = cfg.get("slogan_filename", SLOGAN_FILENAME)
                slogan_path = os.path.join(path, slogan_fn)
                if os.path.exists(slogan_path):
                    try:
                        s_img = Image.open(slogan_path).convert("RGBA")
                        w0, h0 = s_img.size
                        if w0 <= 0:
                            continue
                        cw, _ = canvas.size
                        g = SLOGAN_MIN_EDGE_GAP
                        lx, ly = c["course_slogan"]
                        if anchor == "ra":
                            room = max(80, lx - g)
                        elif anchor == "mm":
                            room = max(80, 2 * min(lx - g, cw - lx - g))
                        else:
                            room = max(80, cw - lx - g)
                        target_w = min(SLOGAN_TARGET_WIDTH_PX, room)
                        r = target_w / float(w0)
                        nh = max(1, int(round(h0 * r)))
                        s_img = s_img.resize((target_w, nh), Image.Resampling.LANCZOS)
                        w, h = s_img.size
                        if anchor == "mm":
                            paste_x = lx - (w // 2)
                        elif anchor == "ra":
                            paste_x = lx - w
                        else:
                            paste_x = lx
                        canvas.paste(s_img, (paste_x, ly), s_img)
                    except Exception:
                        pass
                continue

            val = data.get(field, "")
            if not val: continue
            field_anchor_mode = cfg.get("field_anchors", {}).get(field)
            if field_anchor_mode == "hcenter_la":
                field_anchor = anchor
            elif field_anchor_mode == "multiline_left_la":
                field_anchor = anchor
            elif field_anchor_mode:
                field_anchor = field_anchor_mode
            else:
                field_anchor = anchor
            fill_color = cfg.get("field_colors", {}).get(field, color)
            if field.startswith("cert_"):
                if cert_draw_fonts is not None and field in cert_draw_fonts:
                    font = cert_draw_fonts[field]
                elif field == "cert_brand_tl":
                    font = f_sched_label_cn
                else:
                    font = f_content
            # course_title_* 含子串「title」，须排除，否则会误用主标题 f_main
            elif "title" in field and "course_title" not in field:
                if "mm1" in field or ("cn" in field and "mm" not in field): font = f_main
                elif "mm2" in field or "eg" in field: font = f_sub2 if "mm" in field else f_sub
                else: font = f_main
            elif "date_num" in field: font = f_date_big
            # 勿用 "date" in field：会误匹配 day_date_*、course_date_range
            elif "date_year_week" in field or "date_time" in field: font = f_time
            # sched_* 须先于 "label"：字段名含 "label" 会被误判为 prog/venue 的 f_label
            elif "sched_label_cn" in field:  font = f_sched_label_cn
            elif "sched_label_eg" in field:  font = f_sched_label_eg
            elif "sched_num" in field:       font = f_sched_num
            elif "sched_name_cn" in field:   font = f_sched_name_cn
            elif "sched_name_eg" in field:   font = f_sched_name_eg
            elif "sched_time" in field:      font = f_sched_time
            elif "label" in field: font = f_label
            elif "course_title_cn" in field:
                font = f_course_title_c56_cn if is_info_chart_c56(name) else f_sched_label_cn
            elif "course_title_eg" in field: font = f_sub
            elif "course_date_range" in field: font = f_course_date_range
            elif "day_date" in field:        font = (
                f_day_date_c56 if is_info_chart_c56(name) else f_sched_label_cn
            )
            elif "day_week" in field:        font = f_sched_name_cn
            elif "day_time" in field:        font = f_day_time
            elif "day_cont" in field:        font =  f_day_cont
            elif "course_qr_tip" in field:   font = f_qr_text
            else: font = f_content
            spacing = 0
            if field.startswith("cert_"):
                if field == "cert_body":
                    spacing = 58
                elif field == "cert_title_cn":
                    spacing = 50
                elif field == "cert_title_eg":
                    spacing = 24
                elif field == "cert_footer":
                    spacing = 4
            elif field == "course_title_cn":
                spacing = (
                    COURSE_TITLE_C56_VERT_SPACING
                    if is_info_chart_c56(name)
                    else COURSE_TITLE_CN_MULTILINE_SPACING
                )
            elif field in ("course_qr_tip_cn", "course_qr_tip_eg"):
                spacing = (
                    COURSE_QR_TIP_SPACING_CN
                    if field == "course_qr_tip_cn"
                    else COURSE_QR_TIP_SPACING_EG
                )
            elif "title" in field and not field.startswith("cert_"):
                spacing = 19 if "cn" in field else 8
            elif "cont" in field or "tip" in field:
                if "_b" in field or "_c" in field: spacing = 14
                elif "eg" in field: spacing = 10
                else: spacing = 20
            use_day_date_track = (
                "day_date" in field
                and is_info_chart_c56(name)
                and "\n" not in val
            )
            use_course_title_c56_line_gap = (
                field == "course_title_cn"
                and is_info_chart_c56(name)
                and "\n" in val
            )
            draw_val = val
            if field == "cert_body":
                max_bw = float(cfg.get("cert_body_max_width_px", CERT_BODY_MAX_WIDTH_PX_DEFAULT))
                draw_val = _cert_wrap_body_text(draw, val, font, max_bw)
            try:
                if use_day_date_track:
                    _draw_text_tracked_horizontal(
                        draw, c[field], val, font, fill_color, anchor, DAY_DATE_C56_TRACKING_PX
                    )
                elif use_course_title_c56_line_gap:
                    _draw_multiline_line_gap(
                        draw,
                        c[field],
                        val,
                        font,
                        fill_color,
                        anchor,
                        COURSE_TITLE_C56_VERT_SPACING,
                    )
                elif field_anchor_mode == "multiline_left_la":
                    lx, y_top = float(c[field][0]), float(c[field][1])
                    _draw_multiline_left_top_la(
                        draw, lx, y_top, draw_val, font, fill_color, spacing
                    )
                elif (
                    field == "cert_title_cn"
                    and is_cert_template(name)
                    and field_anchor_mode == "hcenter_la"
                ):
                    cx, y_top = float(c[field][0]), float(c[field][1])
                    tk = float(
                        cfg.get("cert_title_cn_tracking_px", CERT_TITLE_CN_TRACKING_PX_DEFAULT)
                    )
                    _draw_multiline_hcenter_tracked_top_la(
                        draw, cx, y_top, draw_val, font, fill_color, spacing, tk
                    )
                elif field_anchor_mode == "hcenter_la":
                    cx, y_top = float(c[field][0]), float(c[field][1])
                    _draw_multiline_hcenter_top_la(
                        draw, cx, y_top, draw_val, font, fill_color, spacing
                    )
                else:
                    draw.text(
                        c[field],
                        draw_val,
                        font=font,
                        fill=fill_color,
                        spacing=spacing,
                        anchor=field_anchor,
                    )
            except Exception:
                try:
                    draw.text(
                        c[field], draw_val, font=font, fill=fill_color, anchor=field_anchor
                    )
                except Exception:
                    pass
    if cfg.get("cert_draw_name_underline") and "cert_name" in inc and "cert_name" in c:
        val = (data.get("cert_name") or "").strip()
        if val:
            xy = c["cert_name"]
            fa = cfg.get("field_anchors", {}).get("cert_name", cfg.get("align", "ma"))
            u_fill = cfg.get("field_colors", {}).get("cert_name", color)
            f_nm = (
                cert_draw_fonts["cert_name"]
                if cert_draw_fonts and "cert_name" in cert_draw_fonts
                else font_cache["main"]
            )
            try:
                bbox = draw.textbbox(xy, val, font=f_nm, anchor=fa)
                y_line = int(bbox[3]) + 8
                draw.line(
                    [(int(bbox[0]), y_line), (int(bbox[2]), y_line)],
                    fill=u_fill,
                    width=2,
                )
            except Exception:
                pass
    if up_qr and "qr" in inc:
        try:
            q_pos = c["qr"]
            q_img = Image.open(up_qr).convert("RGBA").resize(SIZE_QR)
            canvas.paste(q_img, q_pos, q_img)
        except Exception: pass
    for item in cfg.get("fixed_text1", []):
        draw.text(item["pos"], item["content"], font=f_qr_text, fill=color, anchor=anchor)
    for item in cfg.get("fixed_text2", []):
        draw.text(item["pos"], item["content"], font=f_qr_text, fill=color, anchor=anchor)
    return canvas

def _preview_copy_tuple(p_data: dict) -> tuple[tuple[str, str], ...]:
    """稳定序列化，供 Step1 预览 st.cache_data 作为键。"""
    return tuple(sorted((str(k), str(v)) for k, v in p_data.items()))


def _step1_preview_bg_cache_key(up_bg) -> tuple | None:
    """可缓存背景：None 或磁盘路径 + mtime。上传文件对象返回 None（不缓存）。"""
    if up_bg is None:
        return None
    if isinstance(up_bg, str):
        try:
            ap = os.path.abspath(up_bg)
            return ("p", ap, int(os.path.getmtime(ap)))
        except OSError:
            return ("p", str(up_bg), 0)
    return None

@st.cache_data(show_spinner=False, max_entries=128, ttl=300)
def paint_poster_step1_preview_cached(
    template_name: str,
    data_tuple: tuple[tuple[str, str], ...],
    bg_key: tuple | None,
):
    """Step1 类型卡片 / 模版网格：相同模版+底图+文案命中缓存（编辑页不走此函数）。"""
    font_cache = get_font_cache(_poster_font_dir(None))
    cfg = TEMPLATE_MASTER_CONFIG[template_name]
    data = dict(data_tuple)
    up_bg = None
    if bg_key is not None and bg_key[0] == "p":
        up_bg = bg_key[1]
    return paint_poster(template_name, cfg, up_bg, None, None, data, font_cache, font_dir=None)


def paint_poster_step1_preview(template_name: str, p_data: dict, user_bg) -> Image.Image | None:
    """Step1 预览：磁盘底图可走缓存；本地上传底图每次现算。"""
    dt = _preview_copy_tuple(p_data)
    bk = _step1_preview_bg_cache_key(user_bg)
    if user_bg is not None and bk is None:
        font_cache = get_font_cache(_poster_font_dir(None))
        cfg = TEMPLATE_MASTER_CONFIG[template_name]
        return paint_poster(template_name, cfg, user_bg, None, None, p_data, font_cache, font_dir=None)
    return paint_poster_step1_preview_cached(template_name, dt, bk)

def _poster_thumb_for_ui(img: Image.Image | None, max_side: int = 400) -> Image.Image | None:
    """列表展示用：缩小分辨率减轻浏览器与重绘压力（编辑页仍用全尺寸）。"""
    if img is None:
        return None
    t = img.copy()
    sz = (max_side, int(max_side * 1920 / 1080))
    try:
        t.thumbnail(sz, Image.Resampling.LANCZOS)
    except TypeError:
        t.thumbnail(sz)
    return t
