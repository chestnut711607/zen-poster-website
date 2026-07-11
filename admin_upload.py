# admin_upload.py
import streamlit as st
import os
import shutil
from PIL import Image

# 配置目录
ASSETS_DIR = "assets/backgrounds"
os.makedirs(ASSETS_DIR, exist_ok=True)

st.set_page_config(page_title="后台管理 - 上传背景图库", layout="centered")

st.title("🖼️ 背景图库管理后台")
st.markdown("在此处上传的图片将出现在主程序的 **'从图库选择'** 列表中。")

# 1. 上传功能区
uploaded_file = st.file_uploader("选择一张新背景图 (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 保存文件
    # 为了文件名不冲突，可以使用时间戳或让用户输入名称，这里简化为原文件名
    file_name = uploaded_file.name
    # 简单的文件名清洗，防止特殊字符
    safe_name = "".join(c for c in file_name if c.isalnum() or c in ('.', '_', '-'))
    
    save_path = os.path.join(ASSETS_DIR, safe_name)
    
    try:
        # 验证是否为图片
        image = Image.open(uploaded_file)
        image.verify() 
        
        # 重新打开并保存 (因为 verify 后需要 reload)
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        img.save(save_path)
        
        st.success(f"✅ 成功上传：{safe_name}")
        st.image(img, width=300, caption="预览")
        
    except Exception as e:
        st.error(f"❌ 上传失败：{e}")

st.divider()

# 2. 现有图库管理区
st.subheader("📂 现有图库列表")
if os.path.exists(ASSETS_DIR):
    files = [f for f in os.listdir(ASSETS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        st.info("图库为空，请上方上传。")
    else:
        cols = st.columns(4)
        for i, file in enumerate(files):
            with cols[i % 4]:
                file_path = os.path.join(ASSETS_DIR, file)
                try:
                    img = Image.open(file_path)
                    st.image(img, use_container_width=True, caption=file)
                    
                    if st.button("🗑️ 删除", key=f"del_{file}", type="secondary"):
                        os.remove(file_path)
                        st.rerun()
                except Exception:
                    st.write(f"无法加载：{file}")
else:
    st.warning("图库目录不存在。")

st.markdown("---")
st.caption("💡 提示：主程序会自动读取此文件夹下的所有图片。")