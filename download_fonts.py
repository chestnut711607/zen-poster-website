import os
import gdown

FONT_URLS = {
    "HarmonyOS_Sans_SC_Light.ttf": "1AjDV1ZWGm8obYB2Ikvq1h_OamMT2Gty4",
    "HarmonyOS_Sans_SC_Medium.ttf": "1Ud1ZS87nesMS5hS1PKIjIj-KpHBJBQC9",
    "HarmonyOS_Sans_SC_Regular.ttf": "1JN-3hm12NmUUmR762x0INRwPNXA_pj6j",
    "Huiwen-MinchoGBK-Regular.ttf": "13JtVLiu7rThR5DPshBfxXmzCbNIk3tZv",
    "SourceHanSerifCN-Heavy.otf": "1cintt5Qeisz9XqtPVisBzae5Evh3w7jF",
    "SourceHanSerifCN-Medium.otf": "1uHAPnvcgTWAs5t439vYnwLt0WmKjeEZB",
    "SourceHanSerifSC-SemiBold.otf": "1tRHFz0iMA0kA_BMO_vw6aBtlmlRE2ujP",
}

def download_fonts(font_dir="."):
    for filename, file_id in FONT_URLS.items():
        filepath = os.path.join(font_dir, filename)
        if not os.path.exists(filepath):
            print(f"下载字体: {filename}")
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, filepath, quiet=False)
        else:
            print(f"字体已存在: {filename}")