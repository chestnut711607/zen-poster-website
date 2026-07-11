import os
import streamlit as st
from PIL import Image
from database import save_photo_record, get_photos, PHOTO_CATEGORIES

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_PHOTO_DIR = os.path.join(BASE_DIR, "uploads", "photos")
os.makedirs(UPLOAD_PHOTO_DIR, exist_ok=True)


def render_photographer_page(username: str):
    st.title("📷 摄影师工作台")
    st.markdown(f"欢迎，**{username}**！在这里上传图片到图库，管理员审核通过后即可供大家使用。")
    st.divider()

    tab_upload, tab_mine = st.tabs(["📤 上传新图片", "📋 我的上传记录"])

    # ── 上传新图片 ──
    with tab_upload:
        st.subheader("上传图片到图库")
        st.caption("支持 JPG、PNG 格式，建议尺寸竖版 9:16 比例，大小不超过 20MB")

        # 先在表单外选大分类，这样选禅意项目时能动态显示子分类
        from database import ZEN_PROJECT_SUBCATEGORIES
        main_category = st.selectbox("图片大分类", PHOTO_CATEGORIES, key="photo_main_cat")
        if main_category == "禅意项目":
            sub_category = st.selectbox("禅意项目子分类", ZEN_PROJECT_SUBCATEGORIES, key="photo_sub_cat")
            category = f"禅意项目/{sub_category}"
        else:
            category = main_category

        with st.form("photo_upload_form"):
            uploaded_files = st.file_uploader(
                "选择图片（可多选）",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
            )
            note = st.text_area("备注说明（选填）", height=80,
                                placeholder="描述拍摄地点、时间、特点等，帮助管理员审核")
            submitted = st.form_submit_button("提交上传", type="primary", use_container_width=True)

        if submitted:
            if not uploaded_files:
                st.error("请先选择要上传的图片")
            else:
                success_count = 0
                for f in uploaded_files:
                    try:
                        # 保存文件到本地
                        safe_name = f"{username}_{f.name}"
                        save_path = os.path.join(UPLOAD_PHOTO_DIR, safe_name)
                        with open(save_path, "wb") as out:
                            out.write(f.read())
                        # 写入数据库
                        save_photo_record(
                            filename=safe_name,
                            filepath=save_path,
                            category=category,
                            uploader=username,
                        )
                        success_count += 1
                    except Exception as e:
                        st.error(f"{f.name} 上传失败：{e}")

                if success_count:
                    st.success(f"✅ 成功上传 {success_count} 张图片，等待管理员审核后即可上线")
                    st.balloons()

    # ── 我的上传记录 ──
    with tab_mine:
        st.subheader("我的上传记录")
        all_photos = get_photos()
        my_photos = [p for p in all_photos if p["uploader"] == username]

        if not my_photos:
            st.info("还没有上传记录")
        else:
            status_map = {
                "pending":  ("⏳ 待审核", "#FFF8E1", "#F9A825"),
                "approved": ("✅ 已通过", "#E8F5E9", "#43A047"),
                "rejected": ("❌ 已拒绝", "#FFEBEE", "#E53935"),
            }
            for p in my_photos:
                label, bg, color = status_map.get(p["status"], ("?", "#fff", "#000"))
                with st.expander(f"{label}  |  {p['category']}  |  {p['filename']}  |  {p['upload_at'][:10]}"):
                    col_img, col_info = st.columns([1, 2])
                    with col_img:
                        if os.path.exists(p["filepath"]):
                            img = Image.open(p["filepath"])
                            img.thumbnail((300, 400))
                            st.image(img, use_container_width=True)
                        else:
                            st.warning("图片文件不存在")
                    with col_info:
                        st.markdown(f"""
                        **分类：** {p['category']}  
                        **状态：** <span style="color:{color};font-weight:700">{label}</span>  
                        **上传时间：** {p['upload_at'][:19]}  
                        """, unsafe_allow_html=True)
                        if p.get("review_note"):
                            st.info(f"审核备注：{p['review_note']}")
