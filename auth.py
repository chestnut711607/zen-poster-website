import streamlit as st
from database import get_login_lock_message, init_db, register_user, verify_user

# 三种业务身份可由用户自助注册；管理员身份只由管理员后台分配。
ROLES = {
    "user": {
        "label": "普通用户",
        "emoji": "🙋",
        "desc": "制作和下载海报",
        "color": "#E3F2FD",
        "border": "#90CAF9",
    },
    "designer": {
        "label": "设计师",
        "emoji": "🎨",
        "desc": "上传模版文件和素材",
        "color": "#FFF8E1",
        "border": "#FFD54F",
    },
    "photographer": {
        "label": "摄影师",
        "emoji": "📷",
        "desc": "上传图片到图库",
        "color": "#F3E5F5",
        "border": "#CE93D8",
    },
}

SELF_SERVICE_ROLES = ("user", "designer", "photographer")


def _role_options_for(user_roles: list[str] | None = None) -> list[str]:
    if user_roles is None:
        return list(SELF_SERVICE_ROLES)
    return [role for role in SELF_SERVICE_ROLES if role in user_roles]


def _inject_auth_css() -> None:
    st.markdown("""
    <style>
        .block-container { max-width: 860px !important; padding-top: 2rem !important; }
        .role-card {
            border-radius: 12px;
            padding: 16px 12px 12px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.15s;
            margin-bottom: 8px;
        }
        .role-card:hover { transform: translateY(-2px); }
        .role-emoji { font-size: 32px; margin-bottom: 6px; }
        .role-title { font-size: 15px; font-weight: 700; margin-bottom: 4px; }
        .role-desc  { font-size: 12px; color: #666; }
    </style>
    """, unsafe_allow_html=True)


def _complete_auth(username: str, roles: list[str]) -> None:
    """登录/注册完成后：单身份直接进入，多身份进入身份选择页。"""
    self_roles = _role_options_for(roles)
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.user_roles = roles
    st.session_state.switching_role = False
    st.session_state.selected_role = None

    if len(self_roles) == 1:
        st.session_state.current_role = self_roles[0]
        st.session_state.choosing_role = False
    else:
        st.session_state.current_role = None
        st.session_state.choosing_role = True


def init_auth():
    """在 main.py 顶部调用，确保数据库已初始化"""
    init_db()


def render_login_page():
    """首页：只显示账号登录/注册。"""
    _inject_auth_css()

    st.markdown("<h2 style='text-align:center;margin-bottom:0'>MPI设计中心</h2>", unsafe_allow_html=True)
    st.divider()

    st.markdown("#### 登录 / 注册")
    tab_login, tab_register = st.tabs(["🔑 登录", "📝 注册新账号"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            submitted = st.form_submit_button("登录", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("请填写用户名和密码")
            else:
                user = verify_user(username, password)
                if not user:
                    st.error(get_login_lock_message(username) or "用户名或密码错误")
                else:
                    roles = [role for role in user["roles"].split(",") if role]
                    _complete_auth(username, roles)
                    st.rerun()

    with tab_register:
        with st.form("register_form"):
            new_username = st.text_input("用户名", key="reg_username")
            new_email = st.text_input("邮箱（选填）", key="reg_email")
            new_password = st.text_input("密码", type="password", key="reg_pw")
            new_password2 = st.text_input("确认密码", type="password", key="reg_pw2")
            role_choices = st.multiselect(
                "注册身份（可多选）",
                options=list(SELF_SERVICE_ROLES),
                default=["user"],
                format_func=lambda role: ROLES[role]["label"],
                key="reg_roles",
            )
            reg_submitted = st.form_submit_button("注册并登录", use_container_width=True, type="primary")

        if reg_submitted:
            if not new_username or not new_password:
                st.error("请填写用户名和密码")
            elif new_password != new_password2:
                st.error("两次密码不一致")
            elif len(new_password) < 6:
                st.error("密码至少6位")
            elif not role_choices:
                st.error("请至少选择一个身份")
            else:
                roles = [role for role in SELF_SERVICE_ROLES if role in set(role_choices)]
                ok, msg = register_user(new_username, new_password, new_email, roles)
                if ok:
                    _complete_auth(new_username, roles)
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    return False


def render_role_selection_page():
    """登录后选择已注册身份；只有多身份或主动切换时出现。"""
    _inject_auth_css()

    username = st.session_state.get("username", "")
    user_roles = st.session_state.get("user_roles", [])
    role_keys = _role_options_for(user_roles)

    st.markdown("<h2 style='text-align:center;margin-bottom:0'>选择进入身份</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#888;margin-top:4px'>当前账号：{username}</p>",
                unsafe_allow_html=True)
    st.divider()

    if not role_keys:
        st.warning("当前账号暂无可进入的业务身份，请联系管理员分配权限。")
        if st.button("退出登录", use_container_width=True):
            _clear_auth_state()
            st.rerun()
        return

    if len(role_keys) == 1 and not st.session_state.get("switching_role"):
        st.session_state.current_role = role_keys[0]
        st.session_state.choosing_role = False
        st.rerun()

    cols = st.columns(len(role_keys))
    for i, role_key in enumerate(role_keys):
        role_info = ROLES[role_key]
        with cols[i]:
            st.markdown(f"""
            <div class="role-card" style="background:{role_info['color']};border:1px solid {role_info['border']};">
                <div class="role-emoji">{role_info['emoji']}</div>
                <div class="role-title">{role_info['label']}</div>
                <div class="role-desc">{role_info['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"进入「{role_info['label']}」", key=f"enter_role_{role_key}",
                         use_container_width=True, type="primary"):
                st.session_state.current_role = role_key
                st.session_state.switching_role = False
                st.session_state.choosing_role = False
                st.rerun()

    st.divider()
    if st.button("退出登录", use_container_width=True):
        _clear_auth_state()
        st.rerun()


def _clear_auth_state() -> None:
    for key in ["logged_in", "username", "current_role", "user_roles",
                "selected_role", "switching_role", "choosing_role", "step",
                "chosen_template", "user_bg", "sub_step", "selected_template_type"]:
        st.session_state.pop(key, None)


def require_login():
    init_auth()
    if not st.session_state.get("logged_in"):
        render_login_page()
        st.stop()
    if st.session_state.get("switching_role") or st.session_state.get("choosing_role") or not st.session_state.get("current_role"):
        render_role_selection_page()
        st.stop()
    render_user_bar()
    return st.session_state.get("username", ""), st.session_state.get("current_role", "user")


def render_user_bar():
    """
    在已登录页面的侧栏顶部调用，显示当前用户信息和切换身份/登出按钮。
    """
    username = st.session_state.get("username", "")
    current_role = st.session_state.get("current_role", "user")
    role_info = ROLES.get(current_role, ROLES["user"])

    with st.sidebar:
        st.markdown(f"""
        <div style="background:{role_info['color']};border:1px solid {role_info['border']};
            border-radius:10px;padding:10px 12px;margin-bottom:12px;">
            <div style="font-size:13px;color:#555;">当前登录</div>
            <div style="font-size:16px;font-weight:700;">{username}</div>
            <div style="font-size:12px;color:#777;">{role_info['emoji']} {role_info['label']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("current_role") == "user":
            if st.button("📋 我的历史记录", use_container_width=True, type="secondary"):
                st.session_state.show_history = True
                st.rerun()
        elif st.session_state.get("current_role") == "designer":
            if st.button("📋 我的上传记录", use_container_width=True, type="secondary"):
                st.session_state.show_history = True
                st.rerun()

        if st.button("🔄 切换身份", key="switch_role_btn", use_container_width=True, type="secondary"):
            st.session_state.switching_role = True
            st.rerun()

        if st.button("🚪 登出", use_container_width=True):
            _clear_auth_state()
            st.rerun()
