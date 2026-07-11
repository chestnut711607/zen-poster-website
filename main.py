import base64
import io
import logging
import os

import streamlit as st
from PIL import Image

from download_fonts import download_fonts
download_fonts()
from config import DEFAULT_COPY_DATA, TEMPLATE_MASTER_CONFIG, TEMPLATE_TYPES
from media import get_gallery_file_list, load_thumbnail_image
from poster import (
    _poster_thumb_for_ui,
    _template_field_default,
    get_font_cache,
    paint_poster,
    paint_poster_step1_preview,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================================
# 【配置与初始化】
# =========================================================
st.set_page_config(page_title="海报矩阵系统", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_BG_DIR = os.path.join(BASE_DIR, "assets", "backgrounds")
FONT_DIR = BASE_DIR
os.makedirs(ASSETS_BG_DIR, exist_ok=True)

# 初始化 State
if 'step' not in st.session_state: st.session_state.step = 1
if 'chosen_template' not in st.session_state: st.session_state.chosen_template = None
if 'user_bg' not in st.session_state: st.session_state.user_bg = None
if 'last_template_name' not in st.session_state: st.session_state.last_template_name = None
# 新增流程状态：
# 'choose_template_type' -> 'choose_bg' -> 'choose_template' -> (step 2)
if 'sub_step' not in st.session_state:
    st.session_state.sub_step = 'choose_template_type'
if 'selected_template_type' not in st.session_state:
    st.session_state.selected_template_type = None

GALLERY_MODAL_PAGE_SIZE = 15


@st.dialog("📚 选择背景图片", width="large")
def gallery_modal():
    if st.session_state.get('user_bg') is not None:
        return
    st.markdown("点击图片下方的 **✏️ 选择** 按钮即可应用并关闭窗口。")
    gallery_files = get_gallery_file_list(ASSETS_BG_DIR)
    if not gallery_files:
        st.warning("图库暂时为空。\n请将图片放入 `assets/backgrounds` 文件夹。")
        return
    n = len(gallery_files)
    n_pages = max(1, (n + GALLERY_MODAL_PAGE_SIZE - 1) // GALLERY_MODAL_PAGE_SIZE)
    page_labels = [
        f"{i * GALLERY_MODAL_PAGE_SIZE + 1}–{min((i + 1) * GALLERY_MODAL_PAGE_SIZE, n)} / 共{n}张"
        for i in range(n_pages)
    ]
    page = st.selectbox(
        "分页",
        range(n_pages),
        format_func=lambda i: page_labels[i],
        label_visibility="collapsed",
        key="gallery_modal_page",
    )
    offset = int(page) * GALLERY_MODAL_PAGE_SIZE
    page_files = gallery_files[offset : offset + GALLERY_MODAL_PAGE_SIZE]

    cols = st.columns(5)
    for j, filename in enumerate(page_files):
        file_path = os.path.join(ASSETS_BG_DIR, filename)
        with cols[j % 5]:
            img = load_thumbnail_image(file_path, max_width=280)
            if img:
                st.image(img, use_container_width=True, caption=None)
                if st.button("选择", key=f"modal_{offset + j}_{filename}", use_container_width=True, type="primary"):
                    st.session_state.user_bg = file_path
                    st.session_state.sub_step = 'choose_template'
                    st.rerun()
            else:
                st.error("加载失败")

# =========================================================
# 【逻辑函数】
# =========================================================
def _sidebar_confirm_row(unique_key: str) -> None:
    """每条文案下：点此重跑脚本，右侧海报用当前输入框内容重绘（点按钮会先失焦，内容已写入）。"""
    if st.button(
        "确认",
        key=f"{unique_key}__ok",
        use_container_width=True,
        type="secondary",
    ):
        st.rerun()


def fix_title_text(key):
    current_text = st.session_state.get(key, "")
    if not current_text:
        for k in [f"{key}_fixed", f"{key}_msg"]:
            if k in st.session_state: del st.session_state[k]
        return
    lines = current_text.split('\n')
    new_lines = []
    needs_fix = False
    fix_reasons = []
    for line in lines:
        while len(line) > 6:
            new_lines.append(line[:6])
            line = line[6:]
            needs_fix = True
        new_lines.append(line)
    if len(new_lines) > 3:
        new_lines = new_lines[:3]
        needs_fix = True
        fix_reasons.append("超过3行")
    final_text = "\n".join(new_lines)
    char_count = len(final_text.replace('\n', ''))
    if char_count > 24:
        temp_chars = list(final_text.replace('\n', ''))[:24]
        temp_str = "".join(temp_chars)
        new_lines_final = [temp_str[i:i+6] for i in range(0, len(temp_str), 6)]
        final_text = "\n".join(new_lines_final)
        needs_fix = True
        if "总字数超过24字" not in fix_reasons:
            fix_reasons.append("总字数超过24字")
    if needs_fix:
        st.session_state[key] = final_text
        st.session_state[f"{key}_fixed"] = True
        st.session_state[f"{key}_msg"] = "、".join(fix_reasons) + "自动换行。"
    else:
        for k in [f"{key}_fixed", f"{key}_msg"]:
            if k in st.session_state: del st.session_state[k]


def _apply_progress_nav_click(target_step_num: int) -> None:
    """target_step_num: 1=选类型 2=选底图 3=选模版 4=编辑。仅处理返回/跳转，末尾统一 rerun。"""
    step = st.session_state.step
    if step == 2:
        if target_step_num == 1:
            st.session_state.step = 1
            st.session_state.sub_step = "choose_template_type"
            st.session_state.user_bg = None
            st.session_state.chosen_template = None
            st.session_state.selected_template_type = None
        elif target_step_num == 2:
            st.session_state.step = 1
            st.session_state.sub_step = "choose_bg"
            st.session_state.user_bg = None
            st.session_state.chosen_template = None
        elif target_step_num == 3:
            st.session_state.step = 1
            st.session_state.sub_step = "choose_template"
            st.session_state.chosen_template = None
        st.rerun()
        return

    sub = st.session_state.sub_step
    smap = {"choose_template_type": 1, "choose_bg": 2, "choose_template": 3}
    cur = smap.get(sub, 1)
    if target_step_num >= cur:
        return
    if target_step_num == 1:
        st.session_state.sub_step = "choose_template_type"
        st.session_state.user_bg = None
    elif target_step_num == 2:
        st.session_state.sub_step = "choose_bg"
        st.session_state.user_bg = None
    elif target_step_num == 3:
        st.session_state.sub_step = "choose_template"
    st.rerun()


def _inject_progress_nav_css(current_num: int, step: int) -> None:
    """为主区唯一四列进度条的按钮着色：绿=已过、蓝=当前、灰=未到。"""
    # 仅匹配「恰好 4 列」的横条；类型选择页每行最多 3 列，避免误伤「选择类型」primary 红按钮（勿改回 4 列类型行）
    hbar = (
        'section[data-testid="stMain"] '
        'div[data-testid="stHorizontalBlock"]:has(> :nth-child(4):last-child)'
    )
    parts: list[str] = []
    for i in range(4):
        num = i + 1
        n = i + 1
        if step == 2:
            clickable = num < 4
            is_current = num == 4
        else:
            clickable = num < current_num
            is_current = num == current_num
        if is_current:
            bg, fg, bd = "#1565c0", "#ffffff", "#0d47a1"
        elif clickable:
            bg, fg, bd = "#2e7d32", "#ffffff", "#1b5e20"
        else:
            bg, fg, bd = "#eceff1", "#546e7a", "#cfd8dc"
        # 列可能是 stColumn 外包一层，用「第 n 个直接子元素」包住按钮即可
        col = f'{hbar} > *:nth-child({n}) button'
        parts.append(
            f"""
        {col} {{
            background-color: {bg} !important;
            color: {fg} !important;
            border: 2px solid {bd} !important;
            opacity: 1 !important;
        }}
        """
        )
        if clickable and not is_current:
            parts.append(
                f"""
        {col}:hover {{
            filter: brightness(1.07);
            cursor: pointer;
        }}
        """
            )
    st.markdown("<style>" + "".join(parts) + "</style>", unsafe_allow_html=True)


def render_progress_nav(current_sub_step, step):
    """顶部一行四步：按钮颜色区分；✓ 可返回，▶ 当前，○ 未到。"""
    steps_map = {
        "choose_template_type": 1,
        "choose_bg": 2,
        "choose_template": 3,
    }
    if step == 2:
        current_num = 4
    else:
        current_num = steps_map.get(current_sub_step, 1)

    _inject_progress_nav_css(current_num, step)

    labels = ["① 选择类型", "② 选背景图", "③ 选择模版", "④ 编辑下载"]

    subtag = f"{step}_{current_sub_step if step == 1 else 'edit'}"
    c1, c2, c3, c4 = st.columns(4)
    for i, (col, label) in enumerate(zip((c1, c2, c3, c4), labels)):
        num = i + 1
        with col:
            if step == 2:
                clickable = num < 4
                is_current = num == 4
            else:
                clickable = num < current_num
                is_current = num == current_num
            if is_current:
                st.button(
                    f"▶ {label}",
                    key=f"pgnav_cur_{num}_{subtag}",
                    use_container_width=True,
                    type="primary",
                    disabled=True,
                )
            elif clickable:
                if st.button(
                    f"✓ {label}",
                    key=f"pgnav_go_{num}_{subtag}",
                    use_container_width=True,
                    type="secondary",
                ):
                    _apply_progress_nav_click(num)
            else:
                st.button(
                    f"○ {label}",
                    key=f"pgnav_dis_{num}_{subtag}",
                    use_container_width=True,
                    disabled=True,
                )

# =========================================================
# --- 【主程序界面 Step 1】 ---
# =========================================================
if st.session_state.step == 1:
    # Step1 预览由 paint_poster_step1_preview_cached 内部按需加载字体，此处不再预加载整包字体

    # ======================================================
    # 阶段 A：选择模版类型（新增第一步，显示缩略图卡片）
    # ======================================================
    if st.session_state.sub_step == 'choose_template_type':
        render_progress_nav("choose_template_type", 1)
        st.title("Step 1 · 选择模版类型")
        st.markdown("请先了解各类模版风格，选择最适合您活动的类型。")
        st.divider()

        # 用于生成类型预览的简单占位图（使用 bg 装饰层渲染）
        preview_defaults = {k: v for k, v in DEFAULT_COPY_DATA.items() if v != ""}

        # 每行最多 3 个类型（避免与顶部四列进度条同为「4 列横条」而被进度条 CSS 误改按钮颜色）
        type_items = list(TEMPLATE_TYPES.items())
        for row_start in range(0, len(type_items), 3):
            if row_start > 0:
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            row_slice = type_items[row_start : row_start + 3]
            cols = st.columns(3)
            for slot_idx in range(3):
                with cols[slot_idx]:
                    if slot_idx >= len(row_slice):
                        continue
                    type_name, type_info = row_slice[slot_idx]
                    col_idx = row_start + slot_idx
                    rep_templates = type_info["templates"]
                    is_available = type_info.get("available", False)

                    if is_available:
                        # ── 已上线：正常卡片 + 缩略图 + 选择按钮 ──
                        st.markdown(f"""
                        <div style="background:{type_info['preview_bg_color']}; border-radius:12px;
                            padding:16px 12px 8px; margin-bottom:8px; text-align:center;
                            border:2px solid #C8B89A;">
                            <div style="font-size:36px; margin-bottom:6px;">{type_info['emoji']}</div>
                            <div style="font-size:17px; font-weight:700; color:{type_info['preview_text_color']};
                                margin-bottom:6px;">{type_name}</div>
                            <div style="font-size:12px; color:#666; margin-bottom:10px; line-height:1.5;">
                                {type_info['desc']}</div>
                            <div style="display:inline-block; background:#28a745; color:#fff;
                                font-size:11px; font-weight:600; padding:2px 10px; border-radius:20px;">
                                {type_info['tag']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # 缩略图：至多 4 个（认证证书型 4 张底图各一版；其它类型取前 4 个代表）
                        n_thumb = min(4, len(rep_templates))
                        thumb_cols = st.columns(n_thumb)
                        for t_idx, tname in enumerate(rep_templates[:n_thumb]):
                            tcfg = TEMPLATE_MASTER_CONFIG.get(tname)
                            if tcfg:
                                with thumb_cols[t_idx % n_thumb]:
                                    p_data = {k: _template_field_default(tcfg, k, preview_defaults) for k in tcfg["include"]}
                                    img_p = paint_poster_step1_preview(tname, p_data, None)
                                    thumb = _poster_thumb_for_ui(img_p, max_side=260)
                                    if thumb:
                                        st.image(thumb, use_container_width=True, caption=tname)

                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(
                            f"选择「{type_name}」→",
                            key=f"type_{col_idx}",
                            use_container_width=True,
                            type="primary",
                        ):
                            st.session_state.selected_template_type = type_name
                            st.session_state.sub_step = 'choose_bg'
                            st.rerun()

                    else:
                        # ── 未上线：灰色占位卡片，不可点击 ──
                        st.markdown(f"""
                        <div style="background:#F2F2F2; border-radius:12px;
                            padding:16px 12px 8px; margin-bottom:8px; text-align:center;
                            border:2px dashed #CCCCCC; opacity:0.65;">
                            <div style="font-size:36px; margin-bottom:6px; filter:grayscale(1);">
                                {type_info['emoji']}</div>
                            <div style="font-size:17px; font-weight:700; color:#999; margin-bottom:6px;">
                                {type_name}</div>
                            <div style="font-size:12px; color:#AAA; margin-bottom:14px; line-height:1.5;">
                                {type_info['desc']}</div>
                            <div style="display:inline-block; background:#E0E0E0; color:#999;
                                font-size:11px; font-weight:600; padding:2px 10px; border-radius:20px;">
                                {type_info['tag']}
                            </div>
                        </div>
                        <div style="background:#ECECEC; border-radius:8px; margin-top:8px;
                            height:220px; display:flex; align-items:center; justify-content:center;
                            color:#BBBBBB; font-size:13px; font-style:italic;">
                            模版预览即将开放
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)
                        st.button(
                            f"🔒 {type_name}（敬请期待）",
                            key=f"type_{col_idx}",
                            use_container_width=True,
                            disabled=True,
                        )

    # ======================================================
    # 阶段 B：选择/上传背景图
    # ======================================================
    elif st.session_state.sub_step == 'choose_bg':
        render_progress_nav("choose_bg", 1)
        st.title("Step 2 · 选择背景图片")

        type_name = st.session_state.selected_template_type or "（未选择）"
        st.markdown(f"已选类型：**{type_name}**　|　请为您的海报选择一张背景图片。")
        st.divider()

        col_ops, col_empty = st.columns([1, 2])
        with col_ops:
            st.subheader("1️⃣ 本地上传")
            st.markdown("""
            <style>
                div[data-testid="stFileUploaderDropzone"] p {
                    visibility: hidden !important; height: 0 !important; margin: 0 !important;
                }
                div[data-testid="stFileUploaderDropzone"] {
                    display: flex; flex-direction: column;
                    justify-content: center; align-items: center; min-height: 140px;
                }
                .custom-upload-text {
                    text-align: center; color: #555; font-size: 14px;
                    line-height: 1.6; pointer-events: none; margin-top: -10px;
                }
                .custom-upload-text strong { color: #FF4B4B; font-weight: 600; }
            </style>
            <div class="custom-upload-text">
                <strong>点击或拖拽图片至此</strong><br>
                限制 200MB • 支持 JPG, PNG 格式
            </div>
            """, unsafe_allow_html=True)

            bg_file = st.file_uploader(
                "点击或拖拽图片至此",
                type=["jpg", "png", "jpeg"],
                key="step1_upload",
                label_visibility="collapsed",
                help="支持 JPG, PNG 格式"
            )
            if bg_file:
                st.session_state.user_bg = bg_file
                st.session_state.sub_step = 'choose_template'
                st.rerun()

            st.divider()
            st.subheader("2️⃣ 精选图库")
            st.markdown("使用系统预设的高质量背景。")
            if st.session_state.user_bg is None:
                if st.button("🖼️ 打开图库选择", use_container_width=True, type="secondary"):
                    gallery_modal()
            else:
                st.success("✅ 背景已选定，正在跳转...")
                st.session_state.sub_step = 'choose_template'
                st.rerun()

        with col_empty:
            st.markdown("""
            <div style="display:flex; justify-content:center; align-items:center; height:300px;
                color:#888; font-style:italic; text-align:center;">
                <h3>👈 请在左侧操作<br>选择您喜欢的背景</h3>
            </div>
            """, unsafe_allow_html=True)
        st.stop()

    # ======================================================
    # 阶段 C：在所选类型内选择具体模版
    # ======================================================
    elif st.session_state.sub_step == 'choose_template':
        render_progress_nav("choose_template", 1)
        st.title("Step 3 · 搭配模版风格")

        type_name = st.session_state.selected_template_type
        # 若未选类型（直接跳转旧逻辑），则显示所有模版
        if type_name and type_name in TEMPLATE_TYPES:
            available_template_names = TEMPLATE_TYPES[type_name]["templates"]
        else:
            available_template_names = list(TEMPLATE_MASTER_CONFIG.keys())

        with st.sidebar:
            st.header("✅ 已选背景")
            try:
                if isinstance(st.session_state.user_bg, str):
                    st.image(st.session_state.user_bg, use_container_width=True)
                else:
                    st.image(st.session_state.user_bg, use_container_width=True)
            except:
                st.error("图片加载失败")

            st.divider()
            st.markdown(f"**类型：** {type_name or '全部'}")
            st.divider()

            if st.button("🔄 更换背景图片", use_container_width=True, type="secondary"):
                st.session_state.user_bg = None
                st.session_state.sub_step = 'choose_bg'
                st.rerun()

            st.markdown("👉 在右侧查看预览并选择模版")

        st.markdown(f"### 「{type_name}」预览效果（基于当前背景）")
        preview_defaults = {k: v for k, v in DEFAULT_COPY_DATA.items() if v != ""}
        items = [(n, TEMPLATE_MASTER_CONFIG[n]) for n in available_template_names if n in TEMPLATE_MASTER_CONFIG]

        if not items:
            st.error("未找到该类型的模版配置！")
        else:
            cols = st.columns(3)
            for i, (name, cfg) in enumerate(items):
                with cols[i % 3]:
                    p_data = {k: _template_field_default(cfg, k, preview_defaults) for k in cfg["include"]}
                    img_p = paint_poster_step1_preview(name, p_data, st.session_state.user_bg)
                    thumb = _poster_thumb_for_ui(img_p, max_side=420)
                    if thumb:
                        st.image(thumb, use_container_width=True, caption=name)
                        if st.button(f"编辑此模版", key=f"sel_{i}", use_container_width=True):
                            st.session_state.chosen_template = (name, cfg)
                            st.session_state.last_template_name = name
                            st.session_state.step = 2
                            st.session_state.sub_step = None
                            st.rerun()
                    else:
                        st.error("生成失败")

# ================= STEP 2: 编辑与下载 =================
elif st.session_state.step == 2:
    font_cache = get_font_cache(FONT_DIR)
    if not st.session_state.get('chosen_template'):
        st.warning("未选择模版，正在返回...")
        st.session_state.step = 1
        st.rerun()

    name, cfg = st.session_state.chosen_template
    if st.session_state.last_template_name != name:
        st.session_state.last_template_name = name

    render_progress_nav("edit", 2)

    st.markdown("""
    <style>
        /* 主区：整体下移 50px；顶底留白与步骤条、工具栏、分隔线形成统一节奏 */
        .block-container { padding-top: calc(50px + 0.5rem) !important; padding-bottom: 0.75rem !important; max-width: 95% !important; }
        header, footer, .stApp > header { visibility: hidden !important; display: none !important; }
        .stApp { overflow: hidden !important; height: 100vh; }
        /* 勿在外层 section 设 overflow-y + 固定高度：会与 Streamlit 内部滚动区叠成双滚动条 */
        section[data-testid="stSidebar"] {
            overflow-x: hidden !important;
            border-right: 1px solid #ddd;
        }
        section[data-testid="stSidebar"] > div { padding-top: calc(50px + 0.35rem) !important; }
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"]::-webkit-scrollbar { width: 4px; }
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {
            background-color: #ccc;
            border-radius: 4px;
        }
        /* 侧栏每条文案下的「确认」：浅绿底（secondary + 自定义） */
        section[data-testid="stSidebar"] button[kind="secondary"],
        section[data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
            background-color: #e8f5e9 !important;
            color: #1b5e20 !important;
            border: 1px solid #a5d6a7 !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"]:hover,
        section[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover {
            background-color: #dcedc8 !important;
            border-color: #81c784 !important;
            color: #145214 !important;
        }
        /* 分隔线：与上下区块各留约 12px 等效空隙 */
        hr { margin-top: 0.55rem !important; margin-bottom: 0.65rem !important; }
        .preview-wrapper {
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            gap: 14px;
            height: min(66vh, calc(100vh - 200px));
            width: 100%;
            position: relative;
            box-sizing: border-box;
            margin-top: 1.75rem;
            padding-bottom: 0.5rem;
        }
        .poster-img {
            max-height: calc(100% - 58px);
            max-width: 100%;
            width: auto;
            height: auto;
            object-fit: contain;
            box-shadow: 0 8px 24px rgba(0,0,0,0.18);
            border-radius: 8px;
        }
        .top-controls { margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; height: 5vh; }
        .bottom-controls {
            margin-top: 1.25rem;
            height: auto;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"#### ✍️ 编辑：**{name}** &nbsp;&nbsp;|&nbsp;&nbsp; 👁️ 预览")

    st.divider()

    with st.sidebar:
        st.subheader("🖼️ 素材上传")
        u_logo = st.file_uploader("Logo", type=["png", "jpg"], key="edit_logo")
        u_qr = None
        if "qr" in cfg.get("include", []):
            u_qr = st.file_uploader("二维码", type=["png", "jpg"], key="edit_qr")
        st.divider()
        st.subheader("✍️ 文案修改")
        st.caption("改完后点该字段下方的「确认」更新右侧预览。")

        user_input_data = {}
        label_map = {
            "title_text_cn": "中文主标题", "title_text_eg": "英文副标题",
            "title_text_mm1": "居中主标题(CN)", "title_text_mm2": "居中副标题(EN)",
            "date_num": "日期数字", "date_year_week": "年份/星期", "date_time": "具体时间",
            "prog_label_bil": "内容标签(双语)", "prog_cont_cn_a": "内容详情(单行)",
            "prog_label_cn": "内容标签(中)", "prog_label_eg": "内容标签(英)",
            "prog_cont_cn_b": "内容详情(换行)", "prog_cont_eg": "内容详情(英)",
            "venue_label_bil": "地址标签(双语)", "venue_cont_cn_a": "地址详情(换行)",
            "venue_label_cn": "地址标签(中)", "venue_label_eg": "地址标签(英)",
            "venue_cont_cn_b": "地址详情(单行)", "venue_cont_cn_c": "地址详情(换行)",
            "venue_cont_eg": "地址详情(英)",
            "qr_label_bil": "报名标签(双语)", "qr_label_cn": "报名标签(中)", "qr_label_eg": "报名标签(英)",
            "qr_tip_a": "提示语(单行)", "qr_tip_b": "提示语(换行)", "qr_tip_eg": "提示语(英)",
            # 信息图表型 C1–C3：单日流程
            "sched_label_cn": "标题（中文，两个字，需换行）",
            "sched_label_eg": "标题（英文）",
            # 信息图表型 C4–C6：多日课程
            "course_title_cn": "课程主标题（中文，四个字，换行）",
            "course_title_eg": "课程主标题（英文，可换行）",
            "course_date_range": "课程日期范围",
            "course_qr_tip_cn": "二维码旁说明（中文）",
            "course_qr_tip_eg": "二维码旁说明（英文）",
            # 认证证书型
            "cert_brand_tl": "左上角品牌字",
            "cert_greeting": "祝贺语（如：随喜赞叹）",
            "cert_name": "法名 / 姓名",
            "cert_body": "证书正文（可换行）",
            "cert_title_cn": "证书主标题（中文，可换行）",
            "cert_title_eg": "证书副标题（英文）",
            "cert_issuer": "落款单位",
            "cert_issue_date": "落款日期",
            "cert_footer": "底部标语",
        }
        for _i in range(1, 8):
            label_map[f"sched_num_{_i}"] = f"流程第{_i}项·序号"
            label_map[f"sched_name_cn_{_i}"] = f"流程第{_i}项·中文"
            label_map[f"sched_name_eg_{_i}"] = f"流程第{_i}项·英文"
            label_map[f"sched_time_{_i}"] = f"流程第{_i}项·时段"
            label_map[f"day_date_{_i}"] = f"第{_i}天·日期"
            label_map[f"day_week_{_i}"] = f"第{_i}天·星期"
            label_map[f"day_time_{_i}"] = f"第{_i}天·时间（第1行）"
            label_map[f"day_time2_{_i}"] = f"第{_i}天·时间（第2行）"
            label_map[f"day_cont_{_i}"] = f"第{_i}天·内容（第1行）"
            label_map[f"day_cont2_{_i}"] = f"第{_i}天·内容（第2行）"

        for key in cfg["include"]:
            if key not in ["logo", "qr", "course_slogan"]:
                default_val = _template_field_default(cfg, key, DEFAULT_COPY_DATA)
                label_name = label_map.get(key, key)
                unique_key = f"inp_{name}_{key}"
                if key == "title_text_cn":
                    msg = st.session_state.get(f"{unique_key}_msg", "")
                    if msg: st.warning(f"⚠️ {msg}", icon="⚠️")
                    val = st.text_area(
                        label_name,
                        value=st.session_state.get(unique_key, default_val),
                        height=50,
                        key=unique_key,
                        on_change=fix_title_text,
                        args=(unique_key,),
                    )
                    _sidebar_confirm_row(unique_key)
                    user_input_data[key] = val
                elif (
                    "cont" in key
                    or "tip" in key
                    or "title" in key
                    or "sched_label" in key
                    or key in ("cert_body", "cert_greeting", "cert_footer")
                ):
                    val = st.text_area(label_name, value=default_val, height=50, key=unique_key)
                    _sidebar_confirm_row(unique_key)
                    user_input_data[key] = val
                else:
                    val = st.text_input(label_name, value=default_val, key=unique_key)
                    _sidebar_confirm_row(unique_key)
                    user_input_data[key] = val

    final_img = paint_poster(name, cfg, st.session_state.user_bg, u_logo, u_qr, user_input_data, font_cache, font_dir=FONT_DIR)

    if final_img:
        buf = io.BytesIO()
        final_img.save(buf, format='PNG')
        img_bytes = buf.getvalue()
        b64_data = base64.b64encode(img_bytes).decode('utf-8')

        html_code = f"""
        <div class="preview-wrapper">
            <img src="data:image/png;base64,{b64_data}" class="poster-img" alt="Poster Preview">
            <div class="bottom-controls">
                <a href="data:image/png;base64,{b64_data}" download="{name}_final.png" style="text-decoration: none;">
                    <button style="
                        background-color: #28a745; color: white; border: none;
                        padding: 10px 28px; border-radius: 22px; font-size: 15px;
                        font-weight: 600; cursor: pointer; box-shadow: 0 3px 12px rgba(0,0,0,0.18);
                        transition: transform 0.2s;">
                        💾 下载高清原图
                    </button>
                </a>
            </div>
        </div>
        """
        st.markdown(html_code, unsafe_allow_html=True)
    else:
        st.info("正在生成预览...")