import os
import streamlit as st
from PIL import Image
from database import get_photos, review_photo, get_template_files, PHOTO_CATEGORIES, _get_conn, get_all_users, update_user_roles

def render_admin_login_page():
    """完全独立的管理员入口，普通用户不可见"""
    # 已登录管理员直接进后台
    if st.session_state.get("admin_logged_in"):
        render_admin_page(st.session_state.get("admin_username"))
        return

    st.title("🔧 管理后台")
    st.divider()
    with st.form("admin_login"):
        username = st.text_input("管理员账号")
        password = st.text_input("密码", type="password")
        submitted = st.form_submit_button("登录", type="primary", use_container_width=True)

    if submitted:
        from database import verify_user, user_has_role
        user = verify_user(username, password)
        if user and user_has_role(username, "admin"):
            st.session_state.admin_logged_in = True
            st.session_state.admin_username = username
            st.rerun()
        else:
            st.error("账号或密码错误，或无管理员权限")

def render_admin_page(username: str):
    st.title("🔧 管理员后台")
    st.markdown(f"欢迎，**{username}**！")
    st.divider()

    tab_users, tab_photos, tab_templates = st.tabs([
        "👥 用户权限",
        "🖼️ 审核图片",
        "📁 查看模版文件",
    ])

    # ── 用户权限管理 ──
    with tab_users:
        st.subheader("用户权限")
        st.caption("普通用户、设计师、摄影师可由用户自助注册；管理员身份只能在这里由管理员分配。")

        role_labels = {
            "user": "普通用户",
            "designer": "设计师",
            "photographer": "摄影师",
            "admin": "管理员",
        }
        role_options = list(role_labels.keys())
        users = get_all_users()

        if not users:
            st.info("暂无用户")
        else:
            for user in users:
                current_roles = [r for r in user["roles"].split(",") if r in role_options]
                with st.expander(f"{user['username']}  |  {', '.join(role_labels[r] for r in current_roles)}"):
                    st.markdown(f"**邮箱：** {user.get('email') or '未填写'}  ")
                    st.markdown(f"**注册时间：** {user['created_at'][:19]}")
                    selected = st.multiselect(
                        "身份",
                        options=role_options,
                        default=current_roles,
                        format_func=lambda role: role_labels[role],
                        key=f"roles_{user['id']}",
                    )
                    if st.button("保存身份", key=f"save_roles_{user['id']}", use_container_width=True, type="primary"):
                        if not selected:
                            st.error("至少保留一个身份")
                        else:
                            update_user_roles(user["username"], selected)
                            st.success("已保存")
                            st.rerun()

    # ── 审核摄影师图片 ──
    with tab_photos:
        st.subheader("摄影师上传的图片")

        filter_status = st.radio(
            "筛选状态",
            ["pending", "approved", "rejected"],
            format_func=lambda x: {"pending": "⏳ 待审核", "approved": "✅ 已通过", "rejected": "❌ 已拒绝"}[x],
            horizontal=True,
        )

        photos = get_photos(status=filter_status)

        if not photos:
            st.info("没有符合条件的图片")
        else:
            st.caption(f"共 {len(photos)} 张")
            for p in photos:
                with st.expander(
                    f"{'⏳' if p['status']=='pending' else '✅' if p['status']=='approved' else '❌'}"
                    f"  {p['filename']}  |  {p['category']}  |  上传者：{p['uploader']}  |  {p['upload_at'][:10]}"
                ):
                    col_img, col_action = st.columns([1, 2])
                    with col_img:
                        if os.path.exists(p["filepath"]):
                            img = Image.open(p["filepath"])
                            img.thumbnail((300, 400))
                            st.image(img, use_container_width=True)
                        else:
                            st.warning("图片文件不存在")

                    with col_action:
                        st.markdown(f"""
                        **分类：** {p['category']}  
                        **上传者：** {p['uploader']}  
                        **上传时间：** {p['upload_at'][:19]}  
                        **当前状态：** {p['status']}  
                        """)
                        if p.get("review_note"):
                            st.info(f"已有备注：{p['review_note']}")

                        if p["status"] == "pending":
                            note = st.text_input(
                                "审核备注（选填）",
                                key=f"note_{p['id']}",
                                placeholder="如拒绝请说明原因"
                            )
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("✅ 通过", key=f"approve_{p['id']}",
                                             use_container_width=True, type="primary"):
                                    review_photo(p["id"], "approve", note)
                                    st.success("已通过")
                                    st.rerun()
                            with col_b:
                                if st.button("❌ 拒绝", key=f"reject_{p['id']}",
                                             use_container_width=True):
                                    if not note:
                                        st.error("拒绝时请填写原因")
                                    else:
                                        review_photo(p["id"], "reject", note)
                                        st.warning("已拒绝")
                                        st.rerun()
                        else:
                            # 已审核的可以撤回重审
                            if st.button("↩️ 撤回重审", key=f"reset_{p['id']}", use_container_width=True):
                                conn = _get_conn()
                                conn.execute("UPDATE photos SET status='pending', reviewed_at=NULL, review_note=NULL WHERE id=?", (p["id"],))
                                conn.commit()
                                conn.close()
                                st.rerun()

    # ── 查看设计师上传的模版文件 ──
    with tab_templates:
        st.subheader("设计师上传的模版文件")
        
        filter_status = st.radio(
            "筛选状态",
            ["pending", "approved", "rejected"],
            format_func=lambda x: {"pending": "⏳ 待审核", "approved": "✅ 已通过", "rejected": "❌ 已拒绝"}[x],
            horizontal=True,
            key="template_status_filter"
        )
        
        from database import review_template_file
        files = get_template_files(status=filter_status)

        if not files:
            st.info("暂无文件")
        else:
            st.caption(f"共 {len(files)} 个文件")
            for f in files:
                with st.expander(f"📄 {f['filename']}  |  {f['filetype']}  |  {f['uploader']}  |  {f['upload_at'][:10]}"):
                    col_cover, col_action = st.columns([1, 2])
                    with col_cover:
                        if f.get("cover_path") and os.path.exists(f["cover_path"]):
                            from PIL import Image as PILImage
                            img = PILImage.open(f["cover_path"])
                            img.thumbnail((300, 400))
                            st.image(img, use_container_width=True, caption="封面图")
                        else:
                            st.info("无封面图")
                    
                    with col_action:
                        st.markdown(f"""
                        **类型：** {f['filetype']}  
                        **上传者：** {f['uploader']}  
                        **上传时间：** {f['upload_at'][:19]}  
                        **说明：** {f.get('description') or '无'}  
                        """)
                        
                        if os.path.exists(f["filepath"]):
                            with open(f["filepath"], "rb") as fd:
                                st.download_button(
                                    "⬇️ 下载查看",
                                    data=fd.read(),
                                    file_name=f["filename"],
                                    key=f"admin_dl_{f['id']}",
                                    use_container_width=True,
                                )
                        
                        if filter_status == "pending":
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("✅ 通过", key=f"tmpl_approve_{f['id']}",
                                            use_container_width=True, type="primary"):
                                    review_template_file(f["id"], "approve")
                                    st.success("已通过")
                                    st.rerun()
                            with col_b:
                                if st.button("❌ 拒绝", key=f"tmpl_reject_{f['id']}",
                                            use_container_width=True):
                                    review_template_file(f["id"], "reject")
                                    st.warning("已拒绝")
                                    st.rerun()
                        else:
                            if st.button("↩️ 撤回重审", key=f"tmpl_reset_{f['id']}",
                                        use_container_width=True):
                                conn = _get_conn()
                                conn.execute("UPDATE template_files SET status='pending' WHERE id=?", (f["id"],))
                                conn.commit()
                                conn.close()
                                st.rerun()
