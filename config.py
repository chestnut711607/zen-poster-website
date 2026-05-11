"""模版与默认文案、版式常量（无 Streamlit 依赖）。"""

# 信息图表型 C5/C6：专用字体与行距分支（避免散落硬编码）
INFO_CHART_C56_TEMPLATE_NAMES = frozenset({
    "信息图表型C5",
    "信息图表型C6",
})


def is_info_chart_c56(template_name: str) -> bool:
    return template_name in INFO_CHART_C56_TEMPLATE_NAMES


# =========================================================
# 【数据配置】
# =========================================================
DEFAULT_COPY_DATA = {
    "title_text_cn": "以花观心\n体会生命中的\n喜悦之美",
    "title_text_eg": "Observe the Heart\nthrough Flowers:\nSavor the Beauty of Joy\nin Life.",
    "title_text_mm1": "以花观心\n体会生命中的喜悦之美",
    "title_text_mm2": "Observe the Heart through Flowers:\nSaver the Beauty of Joy in Life.",
    "date_num": "09/15", "date_year_week": "2025 周五/Fri.", "date_time": "15:00 - 17:30",
    "prog_label_bil": "内容 PROGRAM", "prog_cont_cn_a": "共创一支花 | 插花五式 | 智慧小读",
    "prog_label_cn": "内容", "prog_label_eg": "PROGRAM",
    "prog_cont_cn_b": "共创一支花 | 插花五式 \n| 智慧小读",
    "prog_cont_eg": "Collaborative Flower Creation\nFive Forms of Flower Arranging\nWisdom Reading",
    "venue_label_bil": "地址 VENUE",
    "venue_cont_cn_a": "Google 曼谷静心学堂\n13.7565044,100.5694018",
    "venue_label_cn": "地址", "venue_label_eg": "VENUE",
    "venue_cont_cn_b": "Google 曼谷静心学堂 13.7565044,100.5694018",
    "venue_cont_cn_c": "Google 曼谷静心学堂\n13.7565044,100.5694018",
    "venue_cont_eg": "Soi 7/1, Rama lX rd.\nKhwaeng Huai Khwang,\nBangkok 10310",
    "qr_label_bil": "报名 REGISTRATION", "qr_label_cn": "报名", "qr_label_eg": "REGISTRATION",
    "qr_tip_a": "扫码预约，限 8 人", "qr_tip_b": "扫码预约\n限 8 人",
    "qr_tip_eg": "Scan QR code to reserve\nLimited to 8 participants",
    "logo": "", "qr": "",

    # ── 信息图表型 C1/C2/C3：单日流程（7步） ──────────────────
    "sched_label_cn":   "流\n程",
    "sched_label_eg":   "Schedule",


    "sched_num_1":      "1。",
    "sched_name_cn_1":  "入场",
    "sched_name_eg_1":  "Entry",
    "sched_time_1":     "14:00 - 14:30",

    "sched_num_2":      "2。",
    "sched_name_cn_2":  "风生水起",
    "sched_name_eg_2":  "Listen",
    "sched_time_2":     "14:30 - 15:00",

    "sched_num_3":      "3。",
    "sched_name_cn_3":  "共饮三杯茶",
    "sched_name_eg_3":  "Tea tasting",
    "sched_time_3":     "15:00 - 15:30",

    "sched_num_4":      "4。",
    "sched_name_cn_4":  "分享讨论20分钟",
    "sched_name_eg_4":  "Discuss for 20 minutes",
    "sched_time_4":     "15:30 - 16:00",

    "sched_num_5":      "5。",
    "sched_name_cn_5":  "你的声音（原创）",
    "sched_name_eg_5":  "Listen",
    "sched_time_5":     "16:30 - 17:00",

    "sched_num_6":      "6。",
    "sched_name_cn_6":  "分享讨论20分钟",
    "sched_name_eg_6":  "Discuss for 20 minutes",
    "sched_time_6":     "17:30 - 18:00",

    "sched_num_7":      "7。",
    "sched_name_cn_7":  "本来空",
    "sched_name_eg_7":  "Empty",
    "sched_time_7":     "18:00 - 18:30",

    # ── 信息图表型 C4–C6：多日课程安排（7天） ────────────
    "course_title_cn":  "课程\n安排",
    "course_title_eg":  "A Journey\nof Mindful\nLiving",
    "course_date_range":"10月20日 - 10月26日",
    "course_slogan":    "",

    "day_date_1":  "10.20", "day_week_1": "周一 Mon.",
    "day_time_1":  "14:00 - 15:00",
    "day_cont_1":  "正念手冲咖啡课",
    "day_time2_1": "15:00 - 16:00",
    "day_cont2_1": "正念瑜伽",

    "day_date_2":  "10.21", "day_week_2": "周二 Tue.",
    "day_time_2":  "08:30 - 11:00",
    "day_cont_2":  "初一诵《金刚经》|祈福素食",
    "day_time2_2": "15:00 - 16:00",
    "day_cont2_2": "正念瑜伽",

    "day_date_3":  "10.22", "day_week_3": "周三 Wed.",
    "day_time_3":  "14:00 - 15:00",
    "day_cont_3":  "正念手冲咖啡课",
    "day_time2_3": "15:00 - 16:00",
    "day_cont2_3": "正念瑜伽",

    "day_date_4":  "10.23", "day_week_4": "周四 Thu.",
    "day_time_4":  "08:30 - 11:00",
    "day_cont_4":  "禅绕画|《心理视角下的佛学世界》",
    "day_time2_4": "15:00 - 16:00",
    "day_cont2_4": "正念瑜伽",

    "day_date_5":  "10.24", "day_week_5": "周五 Fri.",
    "day_time_5":  "08:30 - 11:00",
    "day_cont_5":  "静心插花|《认识自我的意义》",
    "day_time2_5": "15:00 - 16:00",
    "day_cont2_5": "正念瑜伽",

    "day_date_6":  "10.25", "day_week_6": "周六 Sat.",
    "day_time_6":  "14:00 - 15:00",
    "day_cont_6":  "学员活动（可以预约旁听）",
    "day_time2_6": "15:00 - 16:00",
    "day_cont2_6": "正念瑜伽",

    "day_date_7":  "10.26", "day_week_7": "周日 Sun.",
    "day_time_7":  "14:00 - 15:00",
    "day_cont_7":  "安心禅茶|《正念禅修的要领》",
    "day_time2_7": "15:00 - 16:00",
    "day_cont2_7": "正念瑜伽",

    # 左下角二维码说明（C4–C6 共用）
    "course_qr_tip_cn": "扫码预约\nScan QR code\nto reserve",
    "course_qr_tip_eg": "公益活动\nPublic benefit\nactivities",

    # ── 认证证书型 D1：竖版证书文案 ─────────────────────────────
    "cert_brand_tl": "空間主理",
    "cert_greeting": "随喜赞叹!",
    "cert_name": "法名",
    "cert_body": (
        "完成了空间主理人经营路径六步成长的第一步资质所需学习的全部内容及实践，并在传帮带及修学素养、利他素养和业务素养上达到了标准，获得"
    ),
    "cert_title_cn": "空间主理人经营路径\n学人资格",
    "cert_title_eg": "Certified Space Curator\nManagement Path Practitioner",
    "cert_issuer": "空间主理人项目组",
    "cert_issue_date": "2025年9月",
    "cert_footer": "让学堂成为大众的心灵家园",
}

def is_cert_template(template_name: str) -> bool:
    """是否为「认证证书型」系列模版（D1–D4 等）。"""
    return template_name.startswith("认证证书型")


def _make_cert_template_config(bg_cert_filename: str, text_color: str) -> dict:
    """认证证书型 D1–D4 共用版式；仅装饰底图文件名与字色随版本变化。"""
    return {
        "bg_img": bg_cert_filename,
        "color": text_color,
        "align": "ma",
        "cert_body_max_width_px": 840,
        "cert_draw_name_underline": True,
        "field_anchors": {
            "cert_greeting": "ma",
            "cert_name": "ma",
            "cert_body": "multiline_left_la",
            "cert_title_cn": "hcenter_la",
            "cert_title_eg": "hcenter_la",
            "cert_issuer": "ra",
            "cert_issue_date": "ra",
            "cert_footer": "ma",
        },
        "cert_title_cn_tracking_px": 14,
        "include": [
            "logo",
            "cert_greeting",
            "cert_name",
            "cert_body",
            "cert_title_cn",
            "cert_title_eg",
            "cert_issuer",
            "cert_issue_date",
            "cert_footer",
        ],
        "coords": {
            "logo": (72, 80),
            "cert_greeting": (540, 334),
            "cert_name": (540, 430),
            "cert_body": (120, 638),
            "cert_title_cn": (540, 1092),
            "cert_title_eg": (540, 1322),
            "cert_issuer": (998, 1578),
            "cert_issue_date": (998, 1630),
            "cert_footer": (540, 1805),
        },
    }


TEMPLATE_MASTER_CONFIG = {
    "文案主导型B1": {
        "bg_img": "bg1.png", "color": "#1A1A1A", "align": "la",
        "include": ["title_text_cn", "title_text_eg", "date_num", "date_year_week", "date_time", "prog_label_bil", "prog_cont_cn_a", "venue_label_bil", "venue_cont_cn_a", "qr", "logo"],
        "coords": {"logo": (75, 62), "title_text_cn": (92, 235), "title_text_eg": (95, 525), "date_num": (95, 1258), "date_year_week": (95, 1212), "date_time":(95, 1350), "prog_label_bil":(92, 1495), "prog_cont_cn_a":(92, 1560), "venue_label_bil": (92, 1655), "venue_cont_cn_a": (92, 1720), "qr": (855, 1619)},
        "fixed_text1": [{"content": "扫码预约\nScan QR code\nto reserve", "pos": (860, 1525), "font": "f_qr_text"}, {"content": "公益活动\nPublic benefit\nactivities", "pos": (860, 1755), "font": "f_qr_text"}]
    },
    "文案主导型B2": {
        "bg_img": "bg2.png", "color": "#FFFFFF", "align": "la",
        "include": ["title_text_cn", "title_text_eg", "date_num", "date_year_week", "date_time", "prog_label_bil", "prog_cont_cn_a", "venue_label_bil", "venue_cont_cn_a", "qr", "logo"],
        "coords": {"logo": (75,62), "title_text_cn": (92, 235), "title_text_eg": (95, 525), "date_num": (95, 1258), "date_year_week": (95, 1212), "date_time":(95, 1350), "prog_label_bil":(92, 1495), "prog_cont_cn_a":(92, 1560), "venue_label_bil": (92, 1655), "venue_cont_cn_a": (92, 1720), "qr": (855, 1619)},
        "fixed_text1": [{"content": "扫码预约\nScan QR code\nto reserve", "pos": (860, 1525), "font": "f_qr_text"}, {"content": "公益活动\nPublic benefit\nactivities", "pos": (860, 1755), "font": "f_qr_text"}]
    },
    "文案主导型B3": {
        "bg_img": "bg3.png", "color": "#1A1A1A", "align": "la",
        "include": ["title_text_cn", "title_text_eg", "date_num", "date_year_week", "date_time", "prog_label_bil", "prog_cont_cn_a", "venue_label_bil", "venue_cont_cn_b", "qr_label_bil", "qr_tip_a", "qr", "logo"],
        "coords": {"logo": (75, 62), "title_text_cn": (92, 235), "title_text_eg": (95, 525), "date_num": (95, 1200), "date_year_week": (95, 1156), "date_time":(95, 1292), "prog_label_bil":(92, 1440), "prog_cont_cn_a":(92, 1492), "venue_label_bil": (92, 1583), "venue_cont_cn_b": (92, 1635), "qr_label_bil":(92, 1726), "qr_tip_a":(92, 1781), "qr": (886, 1690)},
        "fixed_text2": [{"content": "公益活动", "pos": (900, 1835), "font": "f_qr_text"}]
    },
    "文案主导型B4": {
        "bg_img": "bg4.png", "color": "#FFFFFF", "align": "la",
        "include": ["title_text_cn", "title_text_eg", "date_num", "date_year_week", "date_time", "prog_label_bil", "prog_cont_cn_a", "venue_label_bil", "venue_cont_cn_b", "qr_label_bil", "qr_tip_a", "qr", "logo"],
        "coords": {"logo": (75, 62), "title_text_cn": (92, 235), "title_text_eg": (95, 525), "date_num": (95, 1200), "date_year_week": (95, 1156), "date_time":(95, 1292), "prog_label_bil":(92, 1440), "prog_cont_cn_a":(92, 1492), "venue_label_bil": (92, 1583), "venue_cont_cn_b": (92, 1635), "qr_label_bil":(92, 1726), "qr_tip_a":(92, 1781), "qr": (886, 1690)},
        "fixed_text2": [{"content": "公益活动", "pos": (900, 1835), "font": "f_qr_text"}]
    },
    "文案主导型B5": {
        "bg_img": "bg5.png", "color": "#1A1A1A", "align": "la",
        "include": ["title_text_cn", "title_text_eg", "date_num", "date_year_week", "date_time", "prog_label_bil", "prog_cont_cn_a", "venue_label_bil", "venue_cont_cn_b", "qr_label_bil", "qr_tip_a", "qr", "logo"],
        "coords": {"logo": (75, 62), "title_text_cn": (92, 235), "title_text_eg": (95, 525), "date_num": (95, 1139), "date_year_week": (95, 1095), "date_time":(95, 1231), "prog_label_bil":(92, 1440), "prog_cont_cn_a":(92, 1492), "venue_label_bil": (92, 1583), "venue_cont_cn_b": (92, 1635), "qr_label_bil":(92, 1726), "qr_tip_a":(92, 1781), "qr": (886, 1690)},
        "fixed_text2": [{"content": "公益活动", "pos": (900, 1835), "font": "f_qr_text"}]
    },
    "文案主导型B6": {
        "bg_img": "bg6.png", "color": "#FFFFFF", "align": "la",
        "include": ["title_text_cn", "title_text_eg", "date_num", "date_year_week", "date_time", "prog_label_bil", "prog_cont_cn_a", "venue_label_bil", "venue_cont_cn_b", "qr_label_bil", "qr_tip_a", "qr", "logo"],
        "coords": {"logo": (75, 62), "title_text_cn": (92, 235), "title_text_eg": (95, 525), "date_num": (95, 1139), "date_year_week": (95, 1095), "date_time":(95, 1231), "prog_label_bil":(92, 1440), "prog_cont_cn_a":(92, 1492), "venue_label_bil": (92, 1583), "venue_cont_cn_b": (92, 1635), "qr_label_bil":(92, 1726), "qr_tip_a":(92, 1781), "qr": (886, 1690)},
        "fixed_text2": [{"content": "公益活动", "pos": (900, 1835), "font": "f_qr_text"}]
    },
    "文案主导型B7": {
        "bg_img": "bg7.png", "color": "#1A1A1A", "align": "la",
        "include": ["title_text_cn", "title_text_eg", "date_num", "date_year_week", "date_time", "prog_label_cn", "prog_cont_cn_b", "venue_label_cn", "venue_cont_cn_c", "prog_label_eg", "prog_cont_eg", "venue_label_eg", "venue_cont_eg", "qr_label_cn", "qr_label_eg", "qr_tip_b", "qr_tip_eg", "qr", "logo"],
        "coords": {"logo": (75, 62), "title_text_cn": (585, 1006), "title_text_eg": (80, 1022), "date_num": (80, 728), "date_year_week": (80, 684), "date_time":(80, 820), "prog_label_cn": (585, 1350), "prog_cont_cn_b": (585, 1398), "venue_label_cn": (585, 1533), "venue_cont_cn_c": (585, 1581), "prog_label_eg": (80,1342), "prog_cont_eg": (80, 1390), "venue_label_eg": (80, 1534), "venue_cont_eg": (80, 1582), "qr_label_cn":(585, 1716), "qr_tip_b":(585, 1764), "qr_label_eg": (80,1726), "qr_tip_eg":(80, 1774), "qr": (886, 1690)},
        "fixed_text2": [{"content": "公益活动", "pos": (900, 1835), "font": "f_qr_text"}]
    },
    "文案主导型B8": {
        "bg_img": "bg8.png", "color": "#000000", "align": "la",
        "field_colors": {
            "date_num": "#FFFFFF",
            "date_year_week": "#FFFFFF",
            "date_time": "#FFFFFF",
        },
        "include": ["title_text_cn", "title_text_eg", "date_num", "date_year_week", "date_time", "prog_label_cn", "prog_cont_cn_b", "venue_label_cn", "venue_cont_cn_c", "prog_label_eg", "prog_cont_eg", "venue_label_eg", "venue_cont_eg", "qr_label_cn", "qr_label_eg", "qr_tip_b", "qr_tip_eg", "qr", "logo"],
        "coords": {"logo": (75, 62), "title_text_cn": (585, 1006), "title_text_eg": (80, 1022), "date_num": (80, 728), "date_year_week": (80, 684), "date_time":(80, 820), "prog_label_cn": (585, 1350), "prog_cont_cn_b": (585, 1398), "venue_label_cn": (585, 1533), "venue_cont_cn_c": (585, 1581), "prog_label_eg": (80,1342), "prog_cont_eg": (80, 1390), "venue_label_eg": (80, 1534), "venue_cont_eg": (80, 1582), "qr_label_cn":(585, 1716), "qr_tip_b":(585, 1764), "qr_label_eg": (80,1726), "qr_tip_eg":(80, 1774), "qr": (886, 1690)},
        "fixed_text2": [{"content": "公益活动", "pos": (900, 1835), "font": "f_qr_text"}]
    },
    "文案主导型B9": {
        "bg_img": "bg9.png", "color": "#1A1A1A", "align": "la",
        # 中英标题：水平居中 + 顶边对齐 y（见 field_anchors 的 hcenter_la 绘制分支）
        "field_anchors": {"title_text_mm1": "hcenter_la", "title_text_mm2": "hcenter_la"},
        "include": ["title_text_mm1", "title_text_mm2", "date_num", "date_year_week", "date_time", "prog_label_bil", "prog_cont_cn_a", "venue_label_bil", "venue_cont_cn_b", "qr_label_bil", "qr_tip_a", "qr", "logo"],
        "coords": {"logo": (75, 62), "title_text_mm1": (540, 218), "title_text_mm2": (540, 385), "date_num": (80, 619), "date_year_week": (80, 575), "date_time":(80, 711), "prog_label_bil":(92, 1440), "prog_cont_cn_a":(92, 1492), "venue_label_bil": (92, 1583), "venue_cont_cn_b": (92, 1635), "qr_label_bil":(92, 1726), "qr_tip_a":(92, 1781), "qr":  (886, 1690)},
        "fixed_text2": [{"content": "公益活动", "pos": (900, 1835), "font": "f_qr_text"}]
    },

    # ================================================================
    # 信息图表型 C1：单日流程 · 浅底左对齐版（幻灯片1）
    # 「流程/Schedule」左上；7 步为两列网格：左序号+时间同 x，右中英名称同 x，上下行等距
    # ================================================================
    "信息图表型C1": {
        "bg_img": "bg_info1.png", "color": "#1A1A1A", "align": "la",
        "include": [
            "logo",
            "sched_label_cn", "sched_label_eg",
            "sched_num_1", "sched_name_cn_1", "sched_name_eg_1", "sched_time_1",
            "sched_num_2", "sched_name_cn_2", "sched_name_eg_2", "sched_time_2",
            "sched_num_3", "sched_name_cn_3", "sched_name_eg_3", "sched_time_3",
            "sched_num_4", "sched_name_cn_4", "sched_name_eg_4", "sched_time_4",
            "sched_num_5", "sched_name_cn_5", "sched_name_eg_5", "sched_time_5",
            "sched_num_6", "sched_name_cn_6", "sched_name_eg_6", "sched_time_6",
            "sched_num_7", "sched_name_cn_7", "sched_name_eg_7", "sched_time_7",

        ],
        "coords": {
            # 左上「流程」竖排 +「Schedule」横排，英文与流程左缘对齐（参照稿）
            "sched_label_cn":  (175, 100),
            "sched_label_eg":  (100, 318),
            # 左列：序号与时间同 x；右列：中英名称同 x。每行 name_cn 顶对齐序号，name_eg 顶对齐时间
            "sched_num_1":     (380, 203),  "sched_time_1":    (380, 320),  "sched_name_cn_1": (600, 236),  "sched_name_eg_1": (600, 312),
            "sched_num_2":     (380, 405),  "sched_time_2":    (380, 522),  "sched_name_cn_2": (600, 438),  "sched_name_eg_2": (600, 514),
            "sched_num_3":     (380, 607),  "sched_time_3":    (380, 724),  "sched_name_cn_3": (600, 640),  "sched_name_eg_3": (600, 716),
            "sched_num_4":     (380, 809),  "sched_time_4":    (380, 926),  "sched_name_cn_4": (600, 842),  "sched_name_eg_4": (600, 918),
            "sched_num_5":     (380, 1011),  "sched_time_5":   (380, 1128),  "sched_name_cn_5": (600, 1044),  "sched_name_eg_5": (600, 1120),
            "sched_num_6":     (380, 1213), "sched_time_6":    (380, 1330), "sched_name_cn_6": (600, 1246), "sched_name_eg_6": (600, 1322),
            "sched_num_7":     (380, 1415), "sched_time_7":    (380, 1532), "sched_name_cn_7": (600, 1448), "sched_name_eg_7": (600, 1524),
            "logo": (500, 1810),
        },
    },

    # ================================================================
    # 信息图表型C2：单日流程 · 深底卡片白字版（幻灯片2）
    # 参照半透明卡片：列表偏左；「流程」竖排 +「Schedule」靠右、压在列表区块上方；两列网格顶对齐
    # ================================================================
    "信息图表型C2": {
        "bg_img": "bg_info2.png", "color": "#FFFFFF", "align": "la",
        "include": [
            "logo",
            "sched_label_cn", "sched_label_eg",
            "sched_num_1", "sched_name_cn_1", "sched_name_eg_1", "sched_time_1",
            "sched_num_2", "sched_name_cn_2", "sched_name_eg_2", "sched_time_2",
            "sched_num_3", "sched_name_cn_3", "sched_name_eg_3", "sched_time_3",
            "sched_num_4", "sched_name_cn_4", "sched_name_eg_4", "sched_time_4",
            "sched_num_5", "sched_name_cn_5", "sched_name_eg_5", "sched_time_5",
            "sched_num_6", "sched_name_cn_6", "sched_name_eg_6", "sched_time_6",
            "sched_num_7", "sched_name_cn_7", "sched_name_eg_7", "sched_time_7",

        ],
        "coords": {
            "sched_label_cn":  (810, 305),
            "sched_label_eg":  (730, 498),
            "sched_num_1":     (328, 464),  "sched_time_1":    (218, 582),  "sched_name_cn_1": (448, 496),  "sched_name_eg_1": (448, 576),
            "sched_num_2":     (328, 641),  "sched_time_2":    (218, 759),  "sched_name_cn_2": (448, 673),  "sched_name_eg_2": (448, 753),
            "sched_num_3":     (328, 818),  "sched_time_3":    (218, 936),  "sched_name_cn_3": (448, 850),  "sched_name_eg_3": (448, 930),
            "sched_num_4":     (328, 995),  "sched_time_4":    (218, 1113), "sched_name_cn_4": (448, 1027),  "sched_name_eg_4": (448, 1107),
            "sched_num_5":     (328, 1172), "sched_time_5":    (218, 1290), "sched_name_cn_5": (448, 1204), "sched_name_eg_5": (448, 1284),
            "sched_num_6":     (328, 1349), "sched_time_6":    (218, 1467), "sched_name_cn_6": (448, 1381), "sched_name_eg_6": (448, 1461),
            "sched_num_7":     (328, 1526), "sched_time_7":    (218, 1644), "sched_name_cn_7": (448, 1558), "sched_name_eg_7": (448, 1638),
            "logo": (500, 48),
        },
    },

    # ================================================================
    # 信息图表型C3：单日流程 · 浅底卡片深字版（幻灯片3）
    # 与 C2 坐标一致，仅底图与字色不同（bg_info3 + 深色字）
    # ================================================================
    "信息图表型C3": {
        "bg_img": "bg_info3.png", "color": "#1A1A1A", "align": "la",
        "include": [
            "logo",
            "sched_label_cn", "sched_label_eg",
            "sched_num_1", "sched_name_cn_1", "sched_name_eg_1", "sched_time_1",
            "sched_num_2", "sched_name_cn_2", "sched_name_eg_2", "sched_time_2",
            "sched_num_3", "sched_name_cn_3", "sched_name_eg_3", "sched_time_3",
            "sched_num_4", "sched_name_cn_4", "sched_name_eg_4", "sched_time_4",
            "sched_num_5", "sched_name_cn_5", "sched_name_eg_5", "sched_time_5",
            "sched_num_6", "sched_name_cn_6", "sched_name_eg_6", "sched_time_6",
            "sched_num_7", "sched_name_cn_7", "sched_name_eg_7", "sched_time_7",
        ],
        "coords": {
            "sched_label_cn":  (810, 305),
            "sched_label_eg":  (730, 498),
            "sched_num_1":     (328, 464),  "sched_time_1":    (218, 582),  "sched_name_cn_1": (448, 496),  "sched_name_eg_1": (448, 576),
            "sched_num_2":     (328, 641),  "sched_time_2":    (218, 759),  "sched_name_cn_2": (448, 673),  "sched_name_eg_2": (448, 753),
            "sched_num_3":     (328, 818),  "sched_time_3":    (218, 936),  "sched_name_cn_3": (448, 850),  "sched_name_eg_3": (448, 930),
            "sched_num_4":     (328, 995),  "sched_time_4":    (218, 1113), "sched_name_cn_4": (448, 1027), "sched_name_eg_4": (448, 1107),
            "sched_num_5":     (328, 1172), "sched_time_5":    (218, 1290), "sched_name_cn_5": (448, 1204), "sched_name_eg_5": (448, 1284),
            "sched_num_6":     (328, 1349), "sched_time_6":    (218, 1467), "sched_name_cn_6": (448, 1381), "sched_name_eg_6": (448, 1461),
            "sched_num_7":     (328, 1526), "sched_time_7":    (218, 1644), "sched_name_cn_7": (448, 1558), "sched_name_eg_7": (448, 1638),
            "logo": (500, 48),
        },
    },

    # ================================================================
    # 信息图表型C4：多日课程 · 浅底左标题双行版（每天两行：每行「时间 + 内容」）
    # ================================================================
    "信息图表型C4": {
        "bg_img": "bg_info4.png", "color": "#1A1A1A", "align": "la",
        "include": [
            "course_title_cn", "course_title_eg",
            "day_date_1", "day_week_1", "day_time_1", "day_cont_1", "day_time2_1", "day_cont2_1",
            "day_date_2", "day_week_2", "day_time_2", "day_cont_2", "day_time2_2", "day_cont2_2",
            "day_date_3", "day_week_3", "day_time_3", "day_cont_3", "day_time2_3", "day_cont2_3",
            "day_date_4", "day_week_4", "day_time_4", "day_cont_4", "day_time2_4", "day_cont2_4",
            "day_date_5", "day_week_5", "day_time_5", "day_cont_5", "day_time2_5", "day_cont2_5",
            "day_date_6", "day_week_6", "day_time_6", "day_cont_6", "day_time2_6", "day_cont2_6",
            "day_date_7", "day_week_7", "day_time_7", "day_cont_7", "day_time2_7", "day_cont2_7",
            "course_qr_tip_cn", "course_qr_tip_eg", "qr", "logo",
        ],
        "coords": {
            "course_title_cn": (88,  68),
            "course_title_eg": (88,  289),
            "day_date_1":  (347, 173),  "day_week_1":  (570, 202),
            "day_time_1":  (351, 277),  "day_cont_1":  (570, 277),  "day_time2_1": (351, 320),  "day_cont2_1": (570, 320),
            "day_date_2":  (347, 362),  "day_week_2":  (570, 391),
            "day_time_2":  (351, 466),  "day_cont_2":  (570, 466),  "day_time2_2": (351, 509),  "day_cont2_2": (570, 509),
            "day_date_3":  (341, 551),  "day_week_3":  (570, 580),
            "day_time_3":  (351, 655),  "day_cont_3":  (570, 655),  "day_time2_3": (351, 698),  "day_cont2_3": (570, 698),
            "day_date_4":  (347, 740),  "day_week_4":  (570, 769),
            "day_time_4":  (351, 844),  "day_cont_4":  (570, 844),  "day_time2_4": (351, 887),  "day_cont2_4": (570, 887),
            "day_date_5":  (347, 929),  "day_week_5":  (570, 958),
            "day_time_5":  (351, 1033), "day_cont_5":  (570, 1033), "day_time2_5": (351, 1076), "day_cont2_5": (570, 1076),
            "day_date_6":  (347, 1118), "day_week_6":  (570, 1147),
            "day_time_6":  (351, 1222), "day_cont_6":  (570, 1222), "day_time2_6": (351, 1265), "day_cont2_6": (570, 1265),
            "day_date_7":  (347, 1307), "day_week_7":  (570, 1336),
            "day_time_7":  (351, 1411), "day_cont_7":  (570, 1411), "day_time2_7": (351, 1454), "day_cont2_7": (570, 1454),
            "course_qr_tip_cn": (81, 1400),
            "course_qr_tip_eg": (81, 1640),
            "qr":   (80, 1502),
            "logo": (500, 1810),
        },
    },

    # ================================================================
    # 信息图表型C5：多日课程 · 深底竖排标题版（幻灯片5）
    # 顶部 logo + slogan.png，日期范围，左侧「课程安排」，右侧 7 天，左下二维码
    # ================================================================
    "信息图表型C5": {
        "bg_img": "bg_info5.png", "color": "#FFFFFF", "align": "la",
        "field_defaults": {"course_title_cn": "课\n程\n安\n排"},
        "include": [
            "logo", "course_slogan", "course_date_range", "course_title_cn",
            "day_date_1", "day_week_1", "day_time_1", "day_cont_1",
            "day_date_2", "day_week_2", "day_time_2", "day_cont_2",
            "day_date_3", "day_week_3", "day_time_3", "day_cont_3",
            "day_date_4", "day_week_4", "day_time_4", "day_cont_4",
            "day_date_5", "day_week_5", "day_time_5", "day_cont_5",
            "day_date_6", "day_week_6", "day_time_6", "day_cont_6",
            "day_date_7", "day_week_7", "day_time_7", "day_cont_7",
            "course_qr_tip_cn", "course_qr_tip_eg", "qr",
        ],
        "coords": {
            "logo":             (80,  46),
            "course_slogan":    (500, 48),
            "course_date_range":(185,  242),
            "course_title_cn":  (160,  695),
            "day_date_1":  (350, 464),  "day_week_1":  (568, 490),  "day_time_1":  (350, 566),  "day_cont_1":  (568, 566),
            "day_date_2":  (350, 650),  "day_week_2":  (568, 676),  "day_time_2":  (350, 752),  "day_cont_2":  (568, 752),
            "day_date_3":  (350, 836),  "day_week_3":  (568, 862),  "day_time_3":  (350, 938),  "day_cont_3":  (568, 938),
            "day_date_4":  (350, 1022), "day_week_4":  (568, 1048), "day_time_4":  (350, 1124), "day_cont_4":  (568, 1124),
            "day_date_5":  (350, 1208), "day_week_5":  (568, 1234), "day_time_5":  (350, 1310), "day_cont_5":  (568, 1310),
            "day_date_6":  (350, 1394), "day_week_6":  (568, 1420), "day_time_6":  (350, 1496), "day_cont_6":  (568, 1496),
            "day_date_7":  (350, 1580), "day_week_7":  (568, 1606), "day_time_7":  (350, 1682), "day_cont_7":  (568, 1682),
            "course_qr_tip_cn": (130, 1400),
            "course_qr_tip_eg": (130, 1640),
            "qr":               (130, 1502),
        },
    },

    # ================================================================
    # 信息图表型C6：多日课程 · 浅底竖排标题版（幻灯片6）
    # 与 C5 布局相同，深色字 + bg_info6；slogan 用浅色底专用图 slogan_black.png
    # ================================================================
    "信息图表型C6": {
        "bg_img": "bg_info6.png", "color": "#1A1A1A", "align": "la",
        "slogan_filename": "slogan_black.png",
        "field_defaults": {"course_title_cn": "课\n程\n安\n排"},
        "include": [
            "logo", "course_slogan", "course_date_range", "course_title_cn",
            "day_date_1", "day_week_1", "day_time_1", "day_cont_1",
            "day_date_2", "day_week_2", "day_time_2", "day_cont_2",
            "day_date_3", "day_week_3", "day_time_3", "day_cont_3",
            "day_date_4", "day_week_4", "day_time_4", "day_cont_4",
            "day_date_5", "day_week_5", "day_time_5", "day_cont_5",
            "day_date_6", "day_week_6", "day_time_6", "day_cont_6",
            "day_date_7", "day_week_7", "day_time_7", "day_cont_7",
            "course_qr_tip_cn", "course_qr_tip_eg", "qr",
        ],
        "coords": {
            "logo":             (80,  46),
            "course_slogan":    (500, 48),
            "course_date_range":(185,  242),
            "course_title_cn":  (160,  695),
            "day_date_1":  (350, 464),  "day_week_1":  (568, 490),  "day_time_1":  (350, 566),  "day_cont_1":  (568, 566),
            "day_date_2":  (350, 650),  "day_week_2":  (568, 676),  "day_time_2":  (350, 752),  "day_cont_2":  (568, 752),
            "day_date_3":  (350, 836),  "day_week_3":  (568, 862),  "day_time_3":  (350, 938),  "day_cont_3":  (568, 938),
            "day_date_4":  (350, 1022), "day_week_4":  (568, 1048), "day_time_4":  (350, 1124), "day_cont_4":  (568, 1124),
            "day_date_5":  (350, 1208), "day_week_5":  (568, 1234), "day_time_5":  (350, 1310), "day_cont_5":  (568, 1310),
            "day_date_6":  (350, 1394), "day_week_6":  (568, 1420), "day_time_6":  (350, 1496), "day_cont_6":  (568, 1496),
            "day_date_7":  (350, 1580), "day_week_7":  (568, 1606), "day_time_7":  (350, 1682), "day_cont_7":  (568, 1682),
            "course_qr_tip_cn": (130, 1400),
            "course_qr_tip_eg": (130, 1640),
            "qr":               (130, 1502),
        },
    },

    # 认证证书型 D1–D4：版式见 _make_cert_template_config；bg_cert*.png 叠在用户背景之上
    "认证证书型D1": _make_cert_template_config("bg_cert1.png", "#000000"),
    "认证证书型D2": _make_cert_template_config("bg_cert2.png", "#FFFFFF"),
    "认证证书型D3": _make_cert_template_config("bg_cert3.png", "#000000"),
    "认证证书型D4": _make_cert_template_config("bg_cert4.png", "#FFFFFF"),
}

SIZE_QR = (130, 130)
# course_slogan：与脚本同目录；默认 slogan.png；模版可设 slogan_filename 覆盖（如 C6 的 slogan_black.png）
SLOGAN_FILENAME = "slogan.png"
SLOGAN_TARGET_WIDTH_PX = 500
SLOGAN_MIN_EDGE_GAP = 12

# 「课程\n安排」等 course_title_cn 多行：draw.text(..., spacing=)。越小行距越紧（主标题 title_text_cn 仍为 19）。
COURSE_TITLE_CN_MULTILINE_SPACING = 10
# C5/C6「课\n程\n安\n排」：上一行 textbbox 底边到下一行锚点之间的额外像素（逐行绘制；PIL 的 spacing+anchor 多行不可靠）
COURSE_TITLE_C56_VERT_SPACING = 35
# course_qr_tip_cn / course_qr_tip_eg 多行：PIL draw.text(..., spacing=)，数值越小行距越紧
COURSE_QR_TIP_SPACING_CN = 8
COURSE_QR_TIP_SPACING_EG = 6
# C5/C6 day_date_* 单行：字符间额外间距（像素），越大越疏
DAY_DATE_C56_TRACKING_PX = 6
# 认证证书 cert_body：海报上正文块最大行宽（像素）；左对齐时 x 取块左缘（如 120）
CERT_BODY_MAX_WIDTH_PX_DEFAULT = 840
# 认证证书 cert_title_cn：逐行居中绘制时的字间距（像素）
CERT_TITLE_CN_TRACKING_PX_DEFAULT = 6

# =========================================================
# 【模版类型定义（新增）】
# 每种类型对应哪些模版，以及用于缩略图展示的描述
# =========================================================
TEMPLATE_TYPES = {
    "文案主导型": {
        "desc": "以文字排版为核心，信息层次清晰，适合各类活动宣传推广",
        "emoji": "✍️",
        "templates": [
            "文案主导型B1", "文案主导型B2", "文案主导型B3",
            "文案主导型B4", "文案主导型B5", "文案主导型B6",
            "文案主导型B7", "文案主导型B8", "文案主导型B9"
        ],
        "preview_bg_color": "#F9F6F1",
        "preview_text_color": "#1A1A1A",
        "available": True,
        "tag": "9 个模版",
    },
    "信息图表型": {
        "desc": "结合数据可视化与图形元素，让活动信息一目了然",
        "emoji": "📊",
        "templates": [
            "信息图表型C1", "信息图表型C2", "信息图表型C3",
            "信息图表型C4", "信息图表型C5", "信息图表型C6",
        ],
        "preview_bg_color": "#EEF4FB",
        "preview_text_color": "#1A1A1A",
        "available": True,
        "tag": "6 个模版",
    },
    "认证证书型": {
        "desc": "适合结业、资质与荣誉场景",
        "emoji": "📜",
        "templates": [
            "认证证书型D1",
            "认证证书型D2",
            "认证证书型D3",
            "认证证书型D4",
        ],
        "preview_bg_color": "#E8F4F8",
        "preview_text_color": "#1A1A1A",
        "available": True,
        "tag": "4 个模版",
    },
    "意境主导型": {
        "desc": "以氛围图像为主角，文字点缀，打造沉浸式视觉体验",
        "emoji": "🌿",
        "templates": [],
        "preview_bg_color": "#F0F5EE",
        "preview_text_color": "#1A1A1A",
        "available": False,
        "tag": "即将推出",
    },
}
