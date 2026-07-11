import os
import json
import streamlit as st
from PIL import Image
from database import get_user_history, delete_history_record


def render_history_page(username: str):
    """
    历史记录页面。
    在 main.py 的普通用户流程中，侧栏加一个「历史记录」入口调用此函数。
    """
    st.title("📋 我的历史记录")
    st.caption("点击任意记录可重新下载，或加载配置继续编辑")
    st.divider()

    records = get_user_history(username)

    if not records:
        st.info("还没有制作过海报，去制作第一张吧！")
        return

    st.caption(f"共 {len(records)} 条记录")

    for rec in records:
        date_str = rec["created_at"][:19]
        with st.expander(f"🖼️ {rec['template_name']}  |  {date_str}"):
            col_img, col_action = st.columns([1, 2])

            with col_img:
                if rec["poster_path"] and os.path.exists(rec["poster_path"]):
                    img = Image.open(rec["poster_path"])
                    img.thumbnail((400, 600))
                    st.image(img, use_container_width=True)
                else:
                    st.warning("海报文件不存在（可能已被清理）")

            with col_action:
                st.markdown(f"""
                **模版：** {rec['template_name']}  
                **制作时间：** {date_str}  
                """)

                # 下载按钮
                if rec["poster_path"] and os.path.exists(rec["poster_path"]):
                    with open(rec["poster_path"], "rb") as f:
                        st.download_button(
                            label="⬇️ 下载此海报",
                            data=f.read(),
                            file_name=f"{rec['template_name']}_{date_str[:10]}.png",
                            key=f"dl_hist_{rec['id']}",
                            use_container_width=True,
                            type="primary",
                        )

                # 继续编辑按钮（恢复当时的配置）
                if st.button("✏️ 继续编辑", key=f"edit_hist_{rec['id']}", use_container_width=True):
                    _restore_session(rec)
                    st.rerun()

                # 删除按钮
                if st.button("🗑️ 删除记录", key=f"del_hist_{rec['id']}", use_container_width=True):
                    delete_history_record(rec["id"], username)
                    st.success("已删除")
                    st.rerun()


def _restore_session(rec: dict):
    """把历史记录中的配置恢复到 session_state，让用户回到 step2 编辑页"""
    from config import TEMPLATE_MASTER_CONFIG

    template_name = rec["template_name"]
    if template_name not in TEMPLATE_MASTER_CONFIG:
        st.error(f"模版「{template_name}」已不存在，无法继续编辑")
        return

    cfg = TEMPLATE_MASTER_CONFIG[template_name]
    st.session_state.chosen_template = (template_name, cfg)
    st.session_state.last_template_name = template_name
    st.session_state.step = 2
    st.session_state.sub_step = None

    # 恢复背景图路径
    if rec.get("bg_path") and os.path.exists(rec["bg_path"]):
        st.session_state.user_bg = rec["bg_path"]
    else:
        st.session_state.user_bg = None

    # 恢复文案输入（写入 session_state 的 key，让 step2 的 text_input 预填值）
    if rec.get("user_inputs"):
        try:
            inputs = json.loads(rec["user_inputs"])
            for k, v in inputs.items():
                st.session_state[f"inp_{template_name}_{k}"] = v
        except Exception:
            pass

    st.session_state.history_restored = True
    st.session_state.show_history = False

def render_designer_history_page(username: str):
    """设计师历史记录：显示上传过的模版文件"""
    st.title("📋 我的上传记录")
    st.caption("这里显示你上传过的所有模版文件")
    st.divider()

    from database import get_template_files
    all_files = get_template_files()
    my_files = [f for f in all_files if f["uploader"] == username]

    if not my_files:
        st.info("还没有上传过模版文件")
        return

    st.caption(f"共 {len(my_files)} 个文件")

    for f in my_files:
        with st.expander(f"📄 {f['filename']}  |  {f['filetype']}  |  {f['upload_at'][:10]}"):
            col_info, col_action = st.columns([2, 1])
            with col_info:
                st.markdown(f"""
                **文件名：** {f['filename']}  
                **类型：** {f['filetype']}  
                **说明：** {f['description'] or '无'}  
                **上传时间：** {f['upload_at'][:19]}  
                """)
            with col_action:
                if os.path.exists(f["filepath"]):
                    with open(f["filepath"], "rb") as fd:
                        st.download_button(
                            "⬇️ 下载",
                            data=fd.read(),
                            file_name=f["filename"],
                            key=f"hist_dl_{f['id']}",
                            use_container_width=True,
                            type="primary",
                        )
                    if st.button("🗑️ 删除", key=f"hist_del_{f['id']}",
                                 use_container_width=True):
                        os.remove(f["filepath"])
                        # 从数据库删除记录
                        from database import _get_conn
                        conn = _get_conn()
                        conn.execute("DELETE FROM template_files WHERE id=?", (f["id"],))
                        conn.commit()
                        conn.close()
                        st.success("已删除")
                        st.rerun()
                else:
                    st.warning("文件不存在")
