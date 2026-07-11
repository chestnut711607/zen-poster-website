import os
import streamlit as st
from database import save_template_file_record, get_template_files, get_approved_photos, PHOTO_CATEGORIES

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_TEMPLATE_DIR = os.path.join(BASE_DIR, "uploads", "templates")
os.makedirs(UPLOAD_TEMPLATE_DIR, exist_ok=True)

TEMPLATE_EXTENSIONS = {
    "PPT / PPTX": [".ppt", ".pptx"],
    "PSD": [".psd"],
    "AI": [".ai"],
    "其他": [],
}

FONT_FILE_TYPES = ["ttf", "otf", "woff", "woff2"]
FONT_FILETYPE_LABEL = "字体文件"

# 浏览模版：固定展示宽度；源图按 3× 宽度缩小（不放大），HTML PNG 展示避免 Streamlit 压糊
TEMPLATE_COVER_DISPLAY_WIDTH = 180
TEMPLATE_COVER_PIXEL_RATIO = 4.0


def _template_cover_card():
    """窄卡片容器：图片与下载按钮同宽（需 Streamlit >= 1.33 的 width 参数）。"""
    try:
        return st.container(width=TEMPLATE_COVER_DISPLAY_WIDTH)
    except TypeError:
        return st.container()

def _get_local_photo_category(filename: str) -> str:
    from database import ZEN_PROJECT_SUBCATEGORIES
    if filename.startswith("禅意空间"):
        return "禅意空间"
    elif filename.startswith("自然风光"):
        return "自然风光"
    else:
        for sub in ZEN_PROJECT_SUBCATEGORIES:
            if filename.startswith(sub):
                return f"禅意项目/{sub}"
        return "其他"

def render_designer_page(username: str):
    st.title("🎨 设计师工作台")
    st.markdown(f"欢迎，**{username}**！在这里上传模版素材、下载模版、或下载图库中的图片。")
    st.divider()

    tab_upload, tab_download, tab_gallery = st.tabs([
        "📤 上传模版文件",
        "📥 下载模版",
        "🖼️ 浏览图库",
    ])

    # ── 上传模版文件 ──
    with tab_upload:
        st.subheader("上传模版文件")
        st.caption("支持 PPT、PSD、AI 等模版文件；字体须单独上传（必填）。管理员收到后会将合适的开发上线")

        # 封面图在表单外选（这样可以预览）
        cover_file = st.file_uploader(
            "📸 封面图（必填，让大家能看到模版样式）",
            type=["jpg", "jpeg", "png"],
            key="template_cover"
        )
        if cover_file:
            from PIL import Image as PILImage
            img = PILImage.open(cover_file)
            img.thumbnail((1080, 1920))
            st.image(img, caption="封面图预览", width=200)

        with st.form("template_upload_form"):
            filetype = st.selectbox("模版文件类型", list(TEMPLATE_EXTENSIONS.keys()))
            description = st.text_area("文件说明", height=80,
                                    placeholder="说明模版的用途、风格、适用场景等")
            template_file_types = ["ppt", "pptx", "psd", "ai", "zip", "pdf", "png", "jpg"]
            uploaded_files = st.file_uploader(
                "模版文件（必填，可多选）",
                type=template_file_types,
                accept_multiple_files=True,
            )
            font_files = st.file_uploader(
                "字体文件（必填，可多选）",
                type=FONT_FILE_TYPES,
                accept_multiple_files=True,
            )
            submitted = st.form_submit_button("提交上传", type="primary", use_container_width=True)

        if submitted:
            if not uploaded_files:
                st.error("请先选择模版文件")
            elif not font_files:
                st.error("请上传字体文件（必填）")
            elif not cover_file:
                st.error("请上传封面图")
            else:
                cover_save_path = None
                try:
                    cover_file.seek(0)
                    cover_name = f"{username}_cover_{cover_file.name}"
                    cover_save_path = os.path.join(UPLOAD_TEMPLATE_DIR, cover_name)
                    with open(cover_save_path, "wb") as out:
                        out.write(cover_file.read())
                except Exception as e:
                    st.error(f"封面图保存失败：{e}")

                if cover_save_path:
                    success_count = 0

                    def _save_upload_batch(files, record_filetype: str) -> None:
                        nonlocal success_count
                        for f in files:
                            try:
                                safe_name = f"{username}_{f.name}"
                                save_path = os.path.join(UPLOAD_TEMPLATE_DIR, safe_name)
                                with open(save_path, "wb") as out:
                                    out.write(f.read())
                                save_template_file_record(
                                    filename=safe_name,
                                    filepath=save_path,
                                    filetype=record_filetype,
                                    description=description,
                                    uploader=username,
                                    cover_path=cover_save_path,
                                )
                                success_count += 1
                            except Exception as e:
                                st.error(f"{f.name} 上传失败：{e}")

                    _save_upload_batch(uploaded_files, filetype)
                    _save_upload_batch(font_files, FONT_FILETYPE_LABEL)

                    if success_count:
                        st.success(f"✅ 成功上传 {success_count} 个文件，管理员会尽快处理")

    # ── 下载自己上传的模版 ──
    with tab_download:
        st.subheader("浏览模版文件")
        st.caption("所有设计师上传并审核通过的模版")
        
        approved_files = get_template_files(status="approved")
        
        if not approved_files:
            st.info("暂无已审核通过的模版")
        else:
            cols = st.columns(3)
            for i, f in enumerate(approved_files):
                with cols[i % 3]:
                    with _template_cover_card():
                        w = TEMPLATE_COVER_DISPLAY_WIDTH
                        if f.get("cover_path") and os.path.exists(f["cover_path"]):
                            from media import show_cover_preview

                            if not show_cover_preview(
                                f["cover_path"],
                                display_width=w,
                                pixel_ratio=TEMPLATE_COVER_PIXEL_RATIO,
                            ):
                                st.warning("封面图加载失败")
                        else:
                            st.markdown(
                                f"""
                                <div style="background:#f0f0f0;width:{w}px;height:240px;display:flex;
                                    align-items:center;justify-content:center;border-radius:8px;
                                    color:#999;font-size:13px;">无封面图</div>
                                """,
                                unsafe_allow_html=True,
                            )

                        if os.path.exists(f["filepath"]):
                            with open(f["filepath"], "rb") as fd:
                                st.download_button(
                                    "⬇️ 下载",
                                    data=fd.read(),
                                    file_name=f["filename"],
                                    key=f"dl_tmpl_{f['id']}",
                                    use_container_width=True,
                                )

                    st.markdown(f"**{f['filetype']}** | {f['upload_at'][:10]}")
                    if f.get("description"):
                        st.caption(f["description"][:30] + "...")

    # ── 浏览图库（已审核通过的图片）──
    with tab_gallery:
        st.subheader("图库浏览与下载")

        # 一级分类
        from database import PHOTO_CATEGORIES, ZEN_PROJECT_SUBCATEGORIES, get_approved_photos
        main_cat = st.selectbox("大分类", ["全部"] + PHOTO_CATEGORIES, key="main_cat")

        # 二级分类（只有禅意项目才显示）
        category = None
        sub_cat = None
        if main_cat == "禅意项目":
            sub_cat = st.selectbox("子分类", ["全部"] + ZEN_PROJECT_SUBCATEGORIES, key="sub_cat")
            if sub_cat == "全部":
                category = "禅意项目"
            else:
                category = f"禅意项目/{sub_cat}"
        elif main_cat != "全部":
            category = main_cat

        # 来源1：摄影师上传并审核通过的图片
        approved = get_approved_photos(category=category)
        db_photos = [{"path": p["filepath"], "name": p["filename"],
                    "category": p["category"]} for p in approved
                    if os.path.exists(p["filepath"])]

        # 来源2：assets/backgrounds/ 原有图片
        from media import get_gallery_file_list
        bg_dir = os.path.join(BASE_DIR, "assets", "backgrounds")
        local_files = get_gallery_file_list(bg_dir)
        local_photos = [{"path": os.path.join(bg_dir, f), "name": f,
                        "category": _get_local_photo_category(f)} for f in local_files]

        # 按分类筛选本地图片
        if main_cat == "全部":
            filtered_local = local_photos
        elif main_cat == "禅意项目":
            if sub_cat == "全部" or sub_cat is None:
                filtered_local = [p for p in local_photos if p["category"].startswith("禅意项目")]
            else:
                filtered_local = [p for p in local_photos if p["category"] == f"禅意项目/{sub_cat}"]
        else:
            filtered_local = [p for p in local_photos if p["category"] == main_cat]

        all_photos = filtered_local + db_photos

        if not all_photos:
            st.info("暂无图片")
        else:
            st.caption(f"共 {len(all_photos)} 张")
            cols = st.columns(4)
            for i, p in enumerate(all_photos):
                with cols[i % 4]:
                    from PIL import Image as PILImage
                    img = PILImage.open(p["path"])
                    img.thumbnail((300, 400))
                    st.image(img, use_container_width=True,
                            caption=p['category'].split("/")[-1])
                    with open(p["path"], "rb") as fd:
                        st.download_button(
                            "⬇️ 下载",
                            data=fd.read(),
                            file_name=p["name"],
                            key=f"dl_photo_{i}_{p['name']}",
                            use_container_width=True,
                        )
