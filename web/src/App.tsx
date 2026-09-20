import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import {
  downloadPoster,
  fetchDefaultCopy,
  fetchGallery,
  fetchRenderURL,
  fetchTemplateTypes,
  fetchTemplates,
  fetchTemplateFiles,
  uploadFile,
  type BgRef,
  type GalleryItem,
  type TemplateFileItem,
  type TemplateItem,
  type TemplateType,
  type Transform,
} from "@/api";
import { FIELD_LABELS, fixTitleText, isTextareaField } from "@/labels";
import PosterCanvas from "@/components/PosterCanvas";

const STEPS = ["选择类型", "选背景图", "选择模版", "编辑下载"];

// Step 1 类型缩略图：把图片（建议 540×960 或任意 9:16 竖图）放进
// web/public/type-previews/ 目录，然后把下面对应的 null 改成 "/type-previews/文件名.jpg"
const TYPE_PREVIEWS: Record<string, string | null> = {
  "文案主导型": "/type-previews/copy.jpg",
  "信息图表型": "/type-previews/infographic.jpg",
  "认证证书型": "/type-previews/cert.jpg",
  "意境主导型": null,
};
const GREEN = "#2B7BA8";

function useDebouncedValue<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

export default function App() {
  const [step, setStep] = useState(1);
  const [types, setTypes] = useState<TemplateType[]>([]);
  const [typeName, setTypeName] = useState<string | null>(null);
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [templateName, setTemplateName] = useState<string | null>(null);
  const [gallery, setGallery] = useState<GalleryItem[]>([]);
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [defaultCopy, setDefaultCopy] = useState<Record<string, string>>({});
  const [templateFiles, setTemplateFiles] = useState<Record<string, TemplateFileItem[]>>({});
  const [bg, setBg] = useState<BgRef | null>(null);
  const [copy, setCopy] = useState<Record<string, string>>({});
  const [transform, setTransform] = useState<Transform>({ scale: 1, x: 0, y: 0 });
  const [editing, setEditing] = useState(false);

  // ---- 背景位置的撤回 / 重做 ----
  const transformRef = useRef(transform);
  useEffect(() => { transformRef.current = transform; }, [transform]);
  const undoStack = useRef<Transform[]>([]);
  const redoStack = useRef<Transform[]>([]);
  const gestureSnapshot = useRef<Transform | null>(null);
  const lastNudgeAt = useRef(0);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  const syncUndoFlags = useCallback(() => {
    setCanUndo(undoStack.current.length > 0);
    setCanRedo(redoStack.current.length > 0);
  }, []);
  const pushUndo = useCallback((snapshot: Transform) => {
    undoStack.current = [...undoStack.current.slice(-49), snapshot];
    redoStack.current = [];
    syncUndoFlags();
  }, [syncUndoFlags]);
  /** 拖拽过程中的实时预览：不入历史 */
  const previewTransform = useCallback((t: Transform) => setTransform(t), []);
  /** 离散操作（恢复默认等）：入历史 */
  const commitTransform = useCallback((t: Transform) => {
    const cur = transformRef.current;
    if (t.scale === cur.scale && t.x === cur.x && t.y === cur.y) return;
    pushUndo(cur);
    setTransform(t);
  }, [pushUndo]);
  const beginTransformGesture = useCallback(() => {
    gestureSnapshot.current = transformRef.current;
  }, []);
  const endTransformGesture = useCallback(() => {
    const snap = gestureSnapshot.current;
    gestureSnapshot.current = null;
    const cur = transformRef.current;
    if (snap && (snap.scale !== cur.scale || snap.x !== cur.x || snap.y !== cur.y)) pushUndo(snap);
  }, [pushUndo]);
  /** 方向键微调：800ms 内的连续按键合并为一步历史 */
  const nudgeTransform = useCallback((t: Transform) => {
    const now = Date.now();
    if (now - lastNudgeAt.current > 800) pushUndo(transformRef.current);
    lastNudgeAt.current = now;
    setTransform(t);
  }, [pushUndo]);
  const undoTransform = useCallback(() => {
    const stack = undoStack.current;
    if (!stack.length) return;
    redoStack.current = [...redoStack.current, transformRef.current];
    undoStack.current = stack.slice(0, -1);
    setTransform(stack[stack.length - 1]);
    syncUndoFlags();
  }, [syncUndoFlags]);
  const redoTransform = useCallback(() => {
    const stack = redoStack.current;
    if (!stack.length) return;
    undoStack.current = [...undoStack.current, transformRef.current];
    redoStack.current = stack.slice(0, -1);
    setTransform(stack[stack.length - 1]);
    syncUndoFlags();
  }, [syncUndoFlags]);
  const [logo, setLogo] = useState<{ id: string; url: string } | null>(null);
  const [qr, setQr] = useState<{ id: string; url: string } | null>(null);
  const [titleMsg, setTitleMsg] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplateTypes().then(setTypes).catch(() => setError("后端未启动？请先运行 uvicorn api_server:app --port 8000"));
    fetchDefaultCopy().then(setDefaultCopy).catch(() => {});
    fetchGallery().then(setGallery).catch(() => {});
    fetchTemplateFiles().then(setTemplateFiles).catch(() => {});
  }, []);

  useEffect(() => {
    if (!typeName) return;
    fetchTemplates(typeName).then((items) => {
      setTemplates(items);
      setTemplateName(items[0]?.name ?? null);
    }).catch(() => setTemplates([]));
  }, [typeName]);

  const activeTemplate = useMemo(
    () => templates.find((t) => t.name === templateName) ?? null,
    [templates, templateName]
  );

  // 切换模版：按 field_defaults + DEFAULT_COPY_DATA 初始化文案
  useEffect(() => {
    if (!activeTemplate) return;
    const next: Record<string, string> = {};
    for (const key of activeTemplate.include) {
      if (["logo", "qr", "course_slogan"].includes(key)) continue;
      next[key] = activeTemplate.field_defaults?.[key] ?? defaultCopy[key] ?? "";
    }
    setCopy(next);
    setTransform({ scale: 1, x: 0, y: 0 });
    undoStack.current = [];
    redoStack.current = [];
    syncUndoFlags();
    setEditing(false);
  }, [activeTemplate, defaultCopy, syncUndoFlags]);

  const editableFields = useMemo(
    () =>
      (activeTemplate?.include ?? []).filter(
        (k) => !["logo", "qr", "course_slogan"].includes(k) && FIELD_LABELS[k]
      ),
    [activeTemplate]
  );

  // ---- 文字层（overlay）逐字实时预览：防抖 300ms ----
  const debouncedCopy = useDebouncedValue(copy, 300);
  const [overlayUrl, setOverlayUrl] = useState<string | null>(null);
  const overlayReqRef = useRef(0);
  useEffect(() => {
    if (!templateName || step < 3) return;
    const reqId = ++overlayReqRef.current;
    fetchRenderURL({
      template: templateName,
      data: debouncedCopy,
      logoId: logo?.id,
      qrId: qr?.id,
      width: 1080,
      format: "png",
      overlayOnly: true,
    })
      .then((url) => {
        if (overlayReqRef.current === reqId) setOverlayUrl(url);
      })
      .catch(() => {});
  }, [templateName, debouncedCopy, logo, qr, step]);

  const pickTemplate = (name: string) => {
    setTemplateName(name);
    setStep(4);
  };

  const handleUploadBg = async (file: File) => {
    try {
      const { id, url } = await uploadFile(file);
      setBg({ kind: "upload", id, url });
      setStep(3);
    } catch {
      setError("背景上传失败");
    }
  };

  const handleDownload = async () => {
    if (!templateName) return;
    setDownloading(true);
    try {
      await downloadPoster(
        {
          template: templateName,
          data: copy,
          bg,
          logoId: logo?.id,
          qrId: qr?.id,
          transform,
          width: 1080,
          format: "png",
        },
        `${templateName}_final.png`
      );
    } catch {
      setError("下载失败，请重试");
    } finally {
      setDownloading(false);
    }
  };

  const goStep = (n: number) => {
    if (n < step) {
      if (n <= 2) setBg(null);
      if (n <= 1) setTypeName(null);
      setStep(n);
    }
  };

  const onCopyChange = (key: string, value: string) =>
    setCopy((prev) => ({ ...prev, [key]: value }));

  const onTitleBlur = (key: string) => {
    const { text, message } = fixTitleText(copy[key] ?? "");
    if (text !== (copy[key] ?? "")) onCopyChange(key, text);
    setTitleMsg(message);
  };

  return (
    <div className="flex h-screen flex-col bg-white text-neutral-900">
      {/* 进度条：四个连体分段按钮，区分 已完成 / 进行中 / 未开始 */}
      <header className="shrink-0 border-b border-neutral-200 px-6 py-4">
        <div className="grid grid-cols-4 overflow-hidden rounded-xl border border-neutral-200 shadow-sm">
          {STEPS.map((label, i) => {
            const num = i + 1;
            const done = num < step;
            const current = num === step;
            return (
              <button
                key={label}
                onClick={() => goStep(num)}
                disabled={!done}
                className={`border-r border-neutral-200 py-3 text-[15px] font-semibold tracking-wide transition-colors last:border-r-0 ${
                  current
                    ? "bg-[#74B7D9] text-[#0D3A52]"
                    : done
                      ? "bg-[#E3F1FA] text-[#2B7BA8] hover:bg-[#CFE8F6]"
                      : "cursor-default bg-white text-neutral-400"
                }`}
              >
                {done ? "✓ " : `${num} · `}{label}
              </button>
            );
          })}
        </div>
      </header>

      {error && (
        <div className="shrink-0 border-b border-amber-200 bg-amber-50 px-6 py-2 text-sm text-amber-800">
          {error}
          <button className="ml-3 underline" onClick={() => setError(null)}>知道了</button>
        </div>
      )}

      <main className="min-h-0 flex-1 overflow-hidden">
        {/* Step 1 · 选择类型 */}
        {step === 1 && (
          <div className="mx-auto max-w-5xl overflow-auto p-8">
            <h1 className="text-3xl font-bold tracking-tight">Step 1 · 选择模板类型</h1>
            <p className="mt-3 text-sm text-neutral-500">选择最符合您活动气质的模板类型。</p>
            <div className="mt-8 grid grid-cols-2 gap-4">
              {types.map((t) => {
                const preview = TYPE_PREVIEWS[t.name] ?? null;
                const files = templateFiles[t.name] ?? [];
                return (
                  <div
                    key={t.name}
                    className={`rounded-xl border border-neutral-200 bg-[#F7FBFD] transition ${
                      t.available ? "hover:border-[#74B7D9] hover:shadow-md" : "opacity-60"
                    }`}
                  >
                    <button
                      disabled={!t.available}
                      onClick={() => { setTypeName(t.name); setStep(2); }}
                      className={`flex w-full items-center gap-5 p-5 text-left ${t.available ? "" : "cursor-default"}`}
                    >
                      {/* 类型缩略图：未配置图片时用纯色块占位（9:16 海报比例） */}
                      <div className="w-28 shrink-0 overflow-hidden rounded-lg border border-neutral-200 shadow-sm">
                        {preview ? (
                          <img src={preview} alt={`${t.name}预览`} className="block aspect-[9/16] w-full object-cover" />
                        ) : (
                          <div
                            className="flex aspect-[9/16] w-full items-center justify-center"
                            style={{ background: t.preview_bg_color }}
                          >
                            <span className="text-xs tracking-widest text-neutral-400">
                              {t.available ? "缩略图占位" : "敬请期待"}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="min-w-0">
                        <div className="text-lg font-semibold text-neutral-800">{t.name}</div>
                        <div className="mt-1.5 text-sm leading-relaxed text-neutral-500">{t.desc}</div>
                        <div className="mt-3 text-xs font-medium" style={{ color: GREEN }}>{t.tag}</div>
                      </div>
                    </button>
                    {/* 模版文件下载：后端 template_files/<系列>/ 里有文件才显示 */}
                    {t.available && files.length > 0 && (
                      <div className="border-t border-neutral-200/80 px-5 py-2.5">
                        <a
                          href={`/api/template-files/${encodeURIComponent(t.name)}/download`}
                          className="inline-flex items-center gap-1.5 text-[13px] font-medium text-[#2B7BA8] transition hover:text-[#155e85]"
                          title={files.map((f) => f.name).join("、")}
                        >
                          ↓ 下载模版文件（{files.length} 个文件）
                        </a>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 2 · 选背景图 */}
        {step === 2 && (
          <div className="mx-auto max-w-5xl overflow-auto p-8">
            <h1 className="text-3xl font-bold tracking-tight">Step 2 · 选择背景图片</h1>
            <p className="mt-3 text-sm text-neutral-500">
              已选类型：<strong className="text-neutral-800">{typeName}</strong>
              <span className="mx-2 text-neutral-300">|</span>请为您的海报选择一张背景图片。
            </p>
            <div className="mt-8 grid grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold">本地上传</h3>
                <p className="mt-1 mb-3 text-sm text-neutral-500">从电脑选择或拖拽一张图片作为海报背景。</p>
                <label
                  className="flex h-40 cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-[1.5px] border-dashed border-[#a9cfe2] bg-[#f7fbfd] transition hover:border-[#74B7D9] hover:bg-[#EDF6FC]"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    const f = e.dataTransfer.files?.[0];
                    if (f) handleUploadBg(f);
                  }}
                >
                  <span className="text-[16px] font-medium text-[#2f5d75]">点击或拖拽图片至此</span>
                  <span className="text-[13px] text-neutral-400">支持 JPG / PNG / WebP</span>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      const f = e.target.files?.[0];
                      if (f) handleUploadBg(f);
                    }}
                  />
                </label>
              </div>
              <div>
                <h3 className="text-lg font-semibold">精选图库</h3>
                <p className="mt-1 mb-3 text-sm text-neutral-500">使用系统预设的高质量背景。</p>
                <button
                  onClick={() => setGalleryOpen(true)}
                  className="flex h-40 w-full cursor-pointer items-center justify-center rounded-xl border-[1.5px] border-dashed border-[#a9cfe2] bg-[#f7fbfd] text-[16px] font-semibold text-[#2f5d75] transition hover:border-[#74B7D9] hover:bg-[#EDF6FC] hover:text-[#2B7BA8]"
                >
                  打开图库选择
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3 · 选择模版 */}
        {step === 3 && (
          <div className="h-full overflow-auto p-8">
            <div className="mx-auto max-w-6xl">
            <h1 className="text-3xl font-bold tracking-tight">Step 3 · 选择模版风格</h1>
            <p className="mt-3 text-sm text-neutral-500">点击缩略图进入编辑，预览均为所选背景的实时渲染。</p>
            <div className="mt-8 grid grid-cols-4 gap-8">
              {templates.map((t) => (
                <TemplateThumb
                  key={t.name}
                  template={t}
                  bg={bg}
                  copy={defaultCopy}
                  onPick={pickTemplate}
                />
              ))}
            </div>
            </div>
          </div>
        )}

        {/* Step 4 · 编辑下载 */}
        {step === 4 && activeTemplate && (
          <div className="flex h-full">
            {/* 侧栏 */}
            <aside className="w-[340px] shrink-0 overflow-y-auto border-r border-neutral-200 p-4">
              <h3 className="text-base font-semibold">修改图片大小及位置</h3>
              <button
                className={`mt-2 w-full rounded-md border px-3 py-2 text-sm font-medium transition ${
                  editing
                    ? "border-[#74B7D9] bg-[#74B7D9] text-[#0D3A52]"
                    : "border-[#A8D3EA] bg-[#E3F1FA] text-[#2B7BA8] hover:border-[#74B7D9] hover:bg-[#D9EDF9]"
                }`}
                onClick={() => setEditing((v) => !v)}
              >
                {editing ? "退出编辑" : "编辑图片"}
              </button>

              <h3 className="mt-6 text-base font-semibold">素材上传</h3>
              <div className="mt-2 space-y-3">
                <MiniUpload label="Logo" value={logo} onChange={setLogo} />
                {activeTemplate.include.includes("qr") && (
                  <MiniUpload label="二维码" value={qr} onChange={setQr} />
                )}
              </div>

              <hr className="my-5 border-neutral-200" />
              <h3 className="text-base font-semibold">文案修改</h3>
              <p className="mt-1 text-xs text-neutral-500">边输入边更新，右侧预览实时刷新。</p>
              <div className="mt-3 space-y-4">
                {editableFields.map((key) => (
                  <div key={key}>
                    <label className="mb-1 block text-[13px] font-medium text-neutral-700">
                      {FIELD_LABELS[key]}
                    </label>
                    {key === "title_text_cn" && titleMsg && (
                      <div className="mb-1 rounded bg-amber-50 px-2 py-1 text-xs text-amber-800">⚠️ {titleMsg}</div>
                    )}
                    {isTextareaField(key) ? (
                      <textarea
                        rows={key.includes("title") ? 3 : 2}
                        className="w-full resize-y rounded-md border border-neutral-300 bg-neutral-50 px-2.5 py-2 text-sm outline-none focus:border-[#74B7D9] focus:ring-2 focus:ring-[#74B7D9]/25"
                        value={copy[key] ?? ""}
                        onChange={(e) => onCopyChange(key, e.target.value)}
                        onBlur={key === "title_text_cn" ? () => onTitleBlur(key) : undefined}
                      />
                    ) : (
                      <input
                        className="w-full rounded-md border border-neutral-300 bg-neutral-50 px-2.5 py-2 text-sm outline-none focus:border-[#74B7D9] focus:ring-2 focus:ring-[#74B7D9]/25"
                        value={copy[key] ?? ""}
                        onChange={(e) => onCopyChange(key, e.target.value)}
                      />
                    )}
                  </div>
                ))}
              </div>
            </aside>

            {/* 画布 + 下载 */}
            <section className="flex min-w-0 flex-1 flex-col bg-[#f5f7f8] p-3">
              <div className="min-h-0 flex-1">
                <PosterCanvas
                  bgUrl={bg?.url ?? null}
                  overlayUrl={overlayUrl}
                  transform={transform}
                  editing={editing}
                  canUndo={canUndo}
                  canRedo={canRedo}
                  onTransformChange={previewTransform}
                  onTransformCommit={commitTransform}
                  onTransformNudge={nudgeTransform}
                  onGestureBegin={beginTransformGesture}
                  onGestureEnd={endTransformGesture}
                  onUndo={undoTransform}
                  onRedo={redoTransform}
                  onEditingChange={setEditing}
                />
              </div>
              <div
                className="flex shrink-0 justify-center px-3 pb-2 pt-6"
                style={{ background: "linear-gradient(to bottom, rgba(245,247,248,0), #f5f7f8 24px)" }}
              >
                <button
                  disabled={downloading}
                  onClick={handleDownload}
                  className="rounded-lg bg-[#277957] px-10 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#1e6045] disabled:opacity-45"
                >
                  {downloading ? "正在生成…" : "下载高清原图"}
                </button>
              </div>
            </section>
          </div>
        )}
      </main>

      {/* 图库弹窗：portal 到 body，避免任何祖先样式影响定位；按文件名前缀分类筛选 */}
      {galleryOpen &&
        createPortal(
          <GalleryModal
            gallery={gallery}
            onClose={() => setGalleryOpen(false)}
            onPick={(g) => {
              setBg({ kind: "gallery", name: g.name, url: g.url });
              setGalleryOpen(false);
              setStep(3);
            }}
          />,
          document.body
        )}
    </div>
  );
}

/** 图库弹窗：分类筛选 + 图片网格 */
function GalleryModal({
  gallery,
  onClose,
  onPick,
}: {
  gallery: GalleryItem[];
  onClose: () => void;
  onPick: (g: GalleryItem) => void;
}) {
  const [category, setCategory] = useState("全部");
  const categories = useMemo(() => {
    const set = new Set(gallery.map((g) => g.name.replace(/\.[^.]+$/, "").replace(/[\d\s]+$/, "")));
    return ["全部", ...Array.from(set)];
  }, [gallery]);
  const filtered = useMemo(
    () =>
      category === "全部"
        ? gallery
        : gallery.filter((g) => g.name.replace(/\.[^.]+$/, "").replace(/[\d\s]+$/, "") === category),
    [gallery, category]
  );

  return (
    <div
      style={{ position: "fixed", inset: 0, zIndex: 50, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.4)", padding: 24 }}
      onClick={onClose}
    >
      <div
        style={{ display: "flex", flexDirection: "column", width: "100%", maxWidth: 1280, maxHeight: "90vh", borderRadius: 16, background: "white", boxShadow: "0 25px 50px rgba(0,0,0,0.25)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-neutral-200 px-5 py-3">
          <h3 className="text-base font-semibold">精选图库</h3>
          <button className="rounded-md px-2 py-1 text-neutral-500 hover:bg-neutral-100" onClick={onClose} aria-label="关闭">
            ✕
          </button>
        </div>
        <div className="flex flex-wrap gap-2 border-b border-neutral-100 px-5 py-3">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={`rounded-full border px-3 py-1 text-[13px] transition ${
                category === c
                  ? "border-[#74B7D9] bg-[#74B7D9] text-[#0D3A52]"
                  : "border-neutral-300 bg-white text-neutral-600 hover:border-[#74B7D9] hover:text-[#2B7BA8]"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
        {/* 瀑布流：保留图片原始宽高比，竖版/横版都完整显示 */}
        <div className="columns-5 gap-3 overflow-y-auto p-5">
          {filtered.map((g) => (
            <button
              key={g.name}
              title={g.name}
              onClick={() => onPick(g)}
              className="mb-3 block w-full break-inside-avoid overflow-hidden rounded-lg border-2 border-transparent p-0 transition hover:border-[#74B7D9]"
            >
              <img src={g.thumb ?? g.url} alt={g.name} className="block h-auto w-full" loading="lazy" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

/** 模版缩略图：实时渲染预览 */
function TemplateThumb({
  template,
  bg,
  copy,
  onPick,
}: {
  template: TemplateItem;
  bg: BgRef | null;
  copy: Record<string, string>;
  onPick: (name: string) => void;
}) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    const data: Record<string, string> = {};
    for (const key of template.include) {
      if (["logo", "qr", "course_slogan"].includes(key)) continue;
      data[key] = template.field_defaults?.[key] ?? copy[key] ?? "";
    }
    fetchRenderURL({ template: template.name, data, bg, width: 540, format: "jpeg" })
      .then((u) => { if (!cancelled) setUrl(u); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, [template, bg, copy]);

  return (
    <button
      onClick={() => onPick(template.name)}
      className="group overflow-hidden rounded-xl border-2 border-transparent bg-white text-left shadow-sm transition hover:shadow-md"
    >
      <div className="relative flex aspect-[9/16] items-center justify-center bg-neutral-100">
        {url ? (
          <img src={url} alt={template.name} className="h-full w-full object-cover" loading="lazy" />
        ) : (
          /* 骨架屏：呼吸渐变 + 居中提示 */
          <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-neutral-100 via-neutral-200 to-neutral-100 bg-[length:200%_200%] animate-[pulse_1.6s_ease-in-out_infinite]">
            <span className="rounded-full bg-white/70 px-3 py-1 text-xs text-neutral-400">渲染中…</span>
          </div>
        )}
        {/* 悬浮变暗 + 编辑按钮 */}
        <div className="absolute inset-0 flex items-center justify-center bg-black/0 opacity-0 transition-all duration-150 group-hover:bg-black/45 group-hover:opacity-100">
          <span className="rounded-md bg-white/95 px-4 py-2 text-sm font-semibold text-neutral-800 shadow">
            编辑此模版
          </span>
        </div>
      </div>
      <div className="px-3 py-2 text-center text-sm text-neutral-700 group-hover:text-[#2B7BA8]">
        {template.name}
      </div>
    </button>
  );
}

/** 小图上传（Logo / 二维码） */
function MiniUpload({
  label,
  value,
  onChange,
}: {
  label: string;
  value: { id: string; url: string } | null;
  onChange: (v: { id: string; url: string } | null) => void;
}) {
  return (
    <div className="flex items-center gap-3">
      <label className="flex-1 cursor-pointer rounded-md border border-dashed border-neutral-300 px-3 py-2 text-sm text-neutral-600 transition hover:border-[#74B7D9] hover:text-[#2B7BA8]">
        {value ? "重新上传" : `上传${label}`}
        <input
          type="file"
          accept="image/png,image/jpeg"
          className="hidden"
          onChange={async (e) => {
            const f = e.target.files?.[0];
            if (!f) return;
            try {
              onChange(await uploadFile(f));
            } catch { /* 忽略 */ }
          }}
        />
      </label>
      {value && (
        <img src={value.url} alt={label} className="h-10 w-10 rounded border border-neutral-200 object-contain" />
      )}
    </div>
  );
}
