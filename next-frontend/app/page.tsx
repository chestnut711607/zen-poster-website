"use client";

import {
  ArrowRight,
  BadgeCheck,
  ChevronRight,
  Download,
  FileText,
  GalleryHorizontalEnd,
  ImagePlus,
  LayoutTemplate,
  Paintbrush,
  Settings2,
  Sparkles,
  Upload
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

type TemplateType = {
  name: string;
  desc: string;
  emoji: string;
  tag: string;
  available: boolean;
  template_count: number;
  preview_bg_color: string;
  preview_text_color: string;
};

type TemplateItem = {
  name: string;
  color: string;
  bg_img: string;
  include: string[];
};

type GalleryItem = {
  id: string;
  filename: string;
  category: string;
  source: string;
  url?: string;
};

const fallbackTypes: TemplateType[] = [
  {
    name: "文案主导型",
    desc: "以文字排版为核心，信息层次清晰，适合活动宣传推广。",
    emoji: "✍️",
    tag: "9 个模版",
    available: true,
    template_count: 9,
    preview_bg_color: "#F9F6F1",
    preview_text_color: "#1A1A1A"
  },
  {
    name: "信息图表型",
    desc: "结合数据可视化与图形元素，让活动信息一目了然。",
    emoji: "📊",
    tag: "6 个模版",
    available: true,
    template_count: 6,
    preview_bg_color: "#EEF4FB",
    preview_text_color: "#1A1A1A"
  },
  {
    name: "认证证书型",
    desc: "适合结业、资质与荣誉场景。",
    emoji: "📜",
    tag: "4 个模版",
    available: true,
    template_count: 4,
    preview_bg_color: "#E8F4F8",
    preview_text_color: "#1A1A1A"
  }
];

const fieldLabels: Record<string, string> = {
  title_text_cn: "中文标题",
  title_text_eg: "英文标题",
  date_num: "日期",
  date_year_week: "年份 / 星期",
  date_time: "时间",
  prog_cont_cn_a: "活动内容",
  venue_cont_cn_a: "活动地址",
  qr_tip_a: "报名提示"
};

const brandSwatches = ["#82C1E7", "#1C76A6", "#928178", "#DA9E85"];

export default function Home() {
  const [templateTypes, setTemplateTypes] = useState<TemplateType[]>(fallbackTypes);
  const [selectedType, setSelectedType] = useState("文案主导型");
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [gallery, setGallery] = useState<GalleryItem[]>([]);
  const [selectedBackground, setSelectedBackground] = useState<GalleryItem | null>(null);
  const [copy, setCopy] = useState<Record<string, string>>({});

  useEffect(() => {
    fetch("/api/template-types")
      .then((res) => (res.ok ? res.json() : fallbackTypes))
      .then(setTemplateTypes)
      .catch(() => setTemplateTypes(fallbackTypes));

    fetch("/api/default-copy")
      .then((res) => (res.ok ? res.json() : {}))
      .then(setCopy)
      .catch(() => setCopy({}));

    fetch("/api/gallery")
      .then((res) => (res.ok ? res.json() : { items: [] }))
      .then((data) => setGallery(data.items || []))
      .catch(() => setGallery([]));
  }, []);

  useEffect(() => {
    fetch(`/api/templates?type=${encodeURIComponent(selectedType)}`)
      .then((res) => (res.ok ? res.json() : []))
      .then((items: TemplateItem[]) => {
        setTemplates(items);
        setSelectedTemplate((prev) => prev || items[0]?.name || "");
      })
      .catch(() => setTemplates([]));
  }, [selectedType]);

  const activeType = useMemo(
    () => templateTypes.find((item) => item.name === selectedType) || templateTypes[0],
    [selectedType, templateTypes]
  );

  const activeTemplate = useMemo(
    () => templates.find((item) => item.name === selectedTemplate) || templates[0],
    [selectedTemplate, templates]
  );

  const editableFields = useMemo(() => {
    const include = activeTemplate?.include || Object.keys(fieldLabels);
    return include.filter((field) => fieldLabels[field]).slice(0, 8);
  }, [activeTemplate]);

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">MP</div>
          <div>
            <p>Mindful Peace</p>
            <strong>海报矩阵</strong>
          </div>
        </div>

        <nav className="nav-list" aria-label="主导航">
          <a className="active" href="#">
            <LayoutTemplate size={18} />
            海报工作台
          </a>
          <a href="#">
            <GalleryHorizontalEnd size={18} />
            素材图库
          </a>
          <a href="#">
            <FileText size={18} />
            历史记录
          </a>
          <a href="#">
            <BadgeCheck size={18} />
            审核中心
          </a>
        </nav>

        <div className="brand-panel">
          <span>品牌色彩</span>
          <div className="swatches">
            {brandSwatches.map((color) => (
              <i key={color} style={{ background: color }} />
            ))}
          </div>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Poster Matrix Workspace</p>
            <h1>生成静心学堂活动海报</h1>
          </div>
          <button className="ghost-button">
            <Settings2 size={18} />
            偏好设置
          </button>
        </header>

        <section className="hero-strip">
          <div>
            <p className="eyebrow">当前流程</p>
            <h2>选择类型、背景与模板后，直接进入文案编辑。</h2>
          </div>
          <div className="steps">
            {["类型", "背景", "模板", "编辑"].map((step, index) => (
              <span key={step} className={index === 0 ? "current" : ""}>
                {index + 1}. {step}
              </span>
            ))}
          </div>
        </section>

        <div className="main-grid">
          <section className="panel type-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Step 1</p>
                <h3>模板类型</h3>
              </div>
              <Sparkles size={18} />
            </div>

            <div className="type-list">
              {templateTypes.map((item) => (
                <button
                  className={item.name === selectedType ? "type-card selected" : "type-card"}
                  disabled={!item.available}
                  key={item.name}
                  onClick={() => {
                    setSelectedType(item.name);
                    setSelectedTemplate("");
                  }}
                >
                  <span className="type-icon">{item.emoji}</span>
                  <span>
                    <strong>{item.name}</strong>
                    <small>{item.desc}</small>
                  </span>
                  <em>{item.tag}</em>
                </button>
              ))}
            </div>
          </section>

          <section className="panel gallery-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Step 2</p>
                <h3>背景素材</h3>
              </div>
              <button className="icon-button" aria-label="上传背景">
                <Upload size={18} />
              </button>
            </div>

            <label className="dropzone">
              <ImagePlus size={22} />
              <span>拖拽上传背景图</span>
              <small>或先从精选图库选择一张</small>
            </label>

            <div className="gallery-grid">
              {gallery.slice(0, 8).map((item) => (
                <button
                  className={selectedBackground?.id === item.id ? "thumb selected" : "thumb"}
                  key={item.id}
                  onClick={() => setSelectedBackground(item)}
                >
                  {item.url ? <img src={item.url} alt={item.filename} /> : <span>{item.category}</span>}
                </button>
              ))}
            </div>
          </section>

          <section className="panel template-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Step 3</p>
                <h3>模板风格</h3>
              </div>
              <Paintbrush size={18} />
            </div>

            <div className="template-list">
              {templates.map((item) => (
                <button
                  className={item.name === selectedTemplate ? "template-row selected" : "template-row"}
                  key={item.name}
                  onClick={() => setSelectedTemplate(item.name)}
                >
                  <span className="mini-preview" style={{ color: item.color || "#111827" }}>
                    Aa
                  </span>
                  <span>
                    <strong>{item.name}</strong>
                    <small>{item.include.length} 个可编辑字段</small>
                  </span>
                  <ChevronRight size={16} />
                </button>
              ))}
            </div>
          </section>

          <section className="panel editor-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Step 4</p>
                <h3>文案编辑</h3>
              </div>
              <button className="primary-button">
                <Download size={18} />
                下载高清图
              </button>
            </div>

            <div className="editor-grid">
              <div className="form-stack">
                {editableFields.map((field) => (
                  <label key={field}>
                    <span>{fieldLabels[field]}</span>
                    <textarea
                      rows={field.includes("title") ? 3 : 2}
                      value={copy[field] || ""}
                      onChange={(event) => setCopy({ ...copy, [field]: event.target.value })}
                    />
                  </label>
                ))}
              </div>

              <div className="poster-preview">
                <div
                  className="poster-canvas"
                  style={{
                    background: selectedBackground?.url
                      ? `linear-gradient(180deg, rgba(255,255,255,.1), rgba(255,255,255,.82)), url(${selectedBackground.url}) center/cover`
                      : activeType?.preview_bg_color
                  }}
                >
                  <span>{activeTemplate?.name || "选择模板"}</span>
                  <h4>{copy.title_text_cn || "以花观心\n体会生命中的喜悦之美"}</h4>
                  <p>{copy.date_time || "15:00 - 17:30"}</p>
                  <button>
                    继续生成
                    <ArrowRight size={15} />
                  </button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
