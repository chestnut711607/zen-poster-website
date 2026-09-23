import { ArrowLeft, Download, Images, RotateCcw, Upload, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
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
import { FIELD_LABELS, getTitleStatus, isTextareaField, wrapTitle } from "@/labels";
import BackgroundSelection from "@/components/BackgroundSelection";
import GalleryModal from "@/components/GalleryModal";
import TemplateSelection from "@/components/TemplateSelection";
import WorkflowHeader from "@/components/WorkflowHeader";
import TypeSelection from "@/components/TypeSelection";
import PosterCanvas from "@/components/PosterCanvas";
import { resolveDraft } from "@/drafts";

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
  const [typesLoading, setTypesLoading] = useState(true);
  const [typesFailed, setTypesFailed] = useState(false);
  const [types, setTypes] = useState<TemplateType[]>([]);
  const [typeName, setTypeName] = useState<string | null>(null);
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [templateName, setTemplateName] = useState<string | null>(null);
  const [gallery, setGallery] = useState<GalleryItem[]>([]);
  const [uploadingBg, setUploadingBg] = useState(false);
  const [galleryLoading, setGalleryLoading] = useState(true);
  const [galleryFailed, setGalleryFailed] = useState(false);
  const [templatesLoading, setTemplatesLoading] = useState(false);
  const [templatesFailed, setTemplatesFailed] = useState(false);
  const [templatesRetry, setTemplatesRetry] = useState(0);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [defaultCopy, setDefaultCopy] = useState<Record<string, string>>({});
  const [templateFiles, setTemplateFiles] = useState<Record<string, TemplateFileItem[]>>({});
  const [bg, setBg] = useState<BgRef | null>(null);
  const [copy, setCopy] = useState<Record<string, string>>({});
  const [drafts, setDrafts] = useState<Record<string, Record<string, string>>>({});
  const [compatibleCopy, setCompatibleCopy] = useState<Record<string, string>>({});
  const [transform, setTransform] = useState<Transform>({ scale: 1, x: 0, y: 0 });
  const [editing, setEditing] = useState(false);
  const [editorTab, setEditorTab] = useState<"copy" | "background" | "assets">("copy");
  const backgroundInput = useRef<HTMLInputElement>(null);

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
  const titleStatus = getTitleStatus(copy.title_text_cn ?? '');
  const [titleNotice, setTitleNotice] = useState<string | null>(null);
  const [composingTitle, setComposingTitle] = useState<string | null>(null);
  const titleComposing = useRef(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTypes = useCallback(async () => {
    setTypesLoading(true);
    setTypesFailed(false);
    try { setTypes(await fetchTemplateTypes()); }
    catch { setTypesFailed(true); }
    finally { setTypesLoading(false); }
  }, []);

  const loadGallery = useCallback(async () => {
    setGalleryLoading(true);
    setGalleryFailed(false);
    try { setGallery(await fetchGallery()); }
    catch { setGalleryFailed(true); }
    finally { setGalleryLoading(false); }
  }, []);
  useEffect(() => { void loadTypes(); void loadGallery(); }, [loadTypes, loadGallery]);

  useEffect(() => {
    fetchDefaultCopy().then(setDefaultCopy).catch(() => {});
    fetchTemplateFiles().then(setTemplateFiles).catch(() => {});
  }, []);

  useEffect(() => {
    if (!typeName) return;
    let cancelled = false;
    setTemplatesLoading(true);
    setTemplatesFailed(false);
    setTemplates([]);
    fetchTemplates(typeName).then((items) => {
      if (cancelled) return;
      setTemplates(items);
    }).catch(() => { if (!cancelled) setTemplatesFailed(true); }).finally(() => { if (!cancelled) setTemplatesLoading(false); });
    return () => { cancelled = true; };
  }, [typeName, templatesRetry]);

  const activeTemplate = useMemo(
    () => templates.find((t) => t.name === templateName) ?? null,
    [templates, templateName]
  );

  const templateCopies = useMemo(() => Object.fromEntries(templates.map((template) => [
    template.name, resolveDraft(template, defaultCopy, compatibleCopy, drafts[template.name]),
  ])), [templates, defaultCopy, compatibleCopy, drafts]);

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
    if (!templateName || step < 3 || copy !== debouncedCopy) return;
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
    return () => { overlayReqRef.current += 1; };
  }, [templateName, copy, debouncedCopy, logo, qr, step]);

  const pickTemplate = (name: string) => {
    const next = templateCopies[name];
    if (!next) return;
    setCopy(next);
    setDrafts((prev) => ({ ...prev, [name]: next }));
    setOverlayUrl(null);
    setTemplateName(name);
    setEditing(false);
    setEditorTab("copy");
    setStep(4);
  };

  const handleUploadBg = async (file: File) => {
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('请选择 JPG、PNG 或 WebP 图片。');
      return;
    }
    setUploadingBg(true);
    setError(null);
    try {
      const { id, url } = await uploadFile(file);
      setBg({ kind: "upload", id, url });
      setTransform({ scale: 1, x: 0, y: 0 });
      undoStack.current = [];
      redoStack.current = [];
      syncUndoFlags();
    } catch {
      setError("背景上传失败，请重试。");
    } finally { setUploadingBg(false); }
  };

  const handleDownload = async () => {
    if (!templateName) return;
    if (activeTemplate?.include.includes('title_text_cn') && titleStatus.count > 18) {
      setError('中文主标题最多 18 字，请缩短后再下载。');
      return;
    }
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
      setStep(n);
    }
  };

  const onCopyChange = (key: string, value: string) => {
    if (key === 'title_text_cn') {
      if (titleComposing.current) {
        setComposingTitle(value);
        return;
      }
      const count = getTitleStatus(value).count;
      if (count > 18 && count >= titleStatus.count) {
        setTitleNotice('最多 18 字，本次超限输入未应用，请缩短后再输入。');
        return;
      }
      value = wrapTitle(value);
      setTitleNotice(null);
    }
    setCopy((prev) => ({ ...prev, [key]: value }));
    setCompatibleCopy((prev) => ({ ...prev, [key]: value }));
    if (templateName) setDrafts((prev) => ({
      ...prev, [templateName]: { ...prev[templateName], [key]: value },
    }));
  };

  return (
    <div className="zp-app flex h-screen flex-col bg-white text-neutral-900">
      <WorkflowHeader step={step} onBack={goStep} />

      {error && (
        <div className="shrink-0 border-b border-amber-200 bg-amber-50 px-6 py-2 text-sm text-amber-800">
          {error}
          <button className="ml-3 underline" onClick={() => setError(null)}>知道了</button>
        </div>
      )}

      <main key={step} className={`min-h-0 flex-1 ${step <= 3 ? "zp-main-home" : "overflow-hidden"}`}>
        {/* Step 1 · 选择类型 */}
        {step === 1 && (
          <TypeSelection types={types} files={templateFiles} loading={typesLoading}
            failed={typesFailed} onRetry={loadTypes}
            onPick={(name) => { if (name !== typeName) setSelectedTemplate(null); setTypeName(name); setStep(2); }} />
        )}

        {step === 2 && <BackgroundSelection bg={bg} typeName={typeName} busy={uploadingBg}
          onUpload={handleUploadBg} onGallery={() => setGalleryOpen(true)} onBack={() => goStep(1)} onNext={() => setStep(3)} />}
        {step === 3 && <TemplateSelection templates={templates} bg={bg} copies={templateCopies}
          selected={selectedTemplate} loading={templatesLoading} failed={templatesFailed}
          onRetry={() => setTemplatesRetry(v => v + 1)} onSelect={setSelectedTemplate}
          onBack={() => goStep(2)} onEdit={pickTemplate} />}

        {/* Step 4 · 编辑下载 */}
        {step === 4 && activeTemplate && (
          <div className="zp-editor">
            <aside className="zp-editor-sidebar">
              <div className="zp-editor-heading"><h1>编辑内容</h1><p>修改内容，预览同步更新</p></div>
              <div className="zp-editor-tabs" role="tablist" aria-label="编辑类别">
                {([{ key: 'copy', label: '文案' }, { key: 'background', label: '背景' }, { key: 'assets', label: 'Logo / 二维码' }] as const).map((tab, index, tabs) => <button key={tab.key} id={`editor-tab-${tab.key}`} role="tab" aria-selected={editorTab === tab.key} aria-controls={`editor-panel-${tab.key}`} tabIndex={editorTab === tab.key ? 0 : -1} onClick={() => { setEditorTab(tab.key); setEditing(tab.key === 'background'); }} onKeyDown={e => {
                  const next = e.key === 'ArrowRight' ? (index + 1) % 3 : e.key === 'ArrowLeft' ? (index + 2) % 3 : e.key === 'Home' ? 0 : e.key === 'End' ? 2 : -1;
                  if (next < 0) return;
                  e.preventDefault();
                  setEditorTab(tabs[next].key); setEditing(tabs[next].key === 'background');
                  document.getElementById(`editor-tab-${tabs[next].key}`)?.focus();
                }}>{tab.label}</button>)}
              </div>
              {editorTab === 'copy' && <div className="zp-editor-panel" id="editor-panel-copy" role="tabpanel" aria-labelledby="editor-tab-copy">
              <div className="mt-3 space-y-4">
                {editableFields.map((key) => (
                  <div key={key}>
                    <label htmlFor={`copy-${key}`} className="mb-1 block text-[13px] font-medium text-neutral-700">
                      {FIELD_LABELS[key]}
                    </label>
                    {key === "title_text_cn" && (
                      <div id="title-status" aria-live="polite" className={`mb-1 text-xs ${titleStatus.message ? 'text-amber-800' : 'text-neutral-500'}`}>
                        <span>{titleStatus.count} / 18 字（不含换行）</span>
                        {titleStatus.count > 18 && <p className="mt-1">已有标题超出 {titleStatus.count - 18} 字，请缩短至 18 字以内。</p>}
                        {(copy.title_text_cn ?? '').split('\n').length > 3 && <p className="mt-1">标题超过 3 行，可能超出模板区域，请检查预览。</p>}
                        {composingTitle === null && titleNotice && <p className="mt-1 text-amber-800">{titleNotice}</p>}
                      </div>
                    )}
                    {isTextareaField(key) ? (
                      <textarea
                        id={`copy-${key}`}
                        rows={key.includes("title") ? 3 : 2}
                        className="w-full resize-y rounded-md border border-neutral-300 bg-neutral-50 px-2.5 py-2 text-sm outline-none focus:border-[#74B7D9] focus:ring-2 focus:ring-[#74B7D9]/25"
                        value={key === 'title_text_cn' ? composingTitle ?? copy[key] ?? '' : copy[key] ?? ''}
                        onCompositionStart={key === 'title_text_cn' ? (e) => {
                          titleComposing.current = true;
                          setTitleNotice(null);
                          setComposingTitle(e.currentTarget.value);
                        } : undefined}
                        onCompositionEnd={key === 'title_text_cn' ? (e) => {
                          titleComposing.current = false;
                          setComposingTitle(null);
                          onCopyChange(key, e.currentTarget.value);
                        } : undefined}
                        onChange={(e) => {
                          const composing = titleComposing.current || (e.nativeEvent as InputEvent).isComposing;
                          if (key === 'title_text_cn' && composing) {
                            titleComposing.current = true;
                            setComposingTitle(e.target.value);
                          } else onCopyChange(key, e.target.value);
                        }}
                        aria-describedby={key === 'title_text_cn' ? 'title-status' : undefined}
                      />
                    ) : (
                      <input
                        id={`copy-${key}`}
                        className="w-full rounded-md border border-neutral-300 bg-neutral-50 px-2.5 py-2 text-sm outline-none focus:border-[#74B7D9] focus:ring-2 focus:ring-[#74B7D9]/25"
                        value={copy[key] ?? ""}
                        onChange={(e) => onCopyChange(key, e.target.value)}
                      />
                    )}
                  </div>
                ))}
              </div>
              </div>}
              {editorTab === 'background' && <div className="zp-editor-panel" id="editor-panel-background" role="tabpanel" aria-labelledby="editor-tab-background">
                <h2>背景图片</h2>
                {bg && <div className="zp-editor-bg-preview"><img src={bg.url} alt="当前背景" /></div>}
                <input ref={backgroundInput} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={e => { const file = e.target.files?.[0]; e.target.value = ''; if (file) void handleUploadBg(file); }} />
                <div className="zp-editor-replace"><button className="zp-button zp-button-secondary" disabled={uploadingBg} onClick={() => backgroundInput.current?.click()}><Upload size={16} />{uploadingBg ? '上传中…' : '重新上传'}</button><button className="zp-button zp-button-secondary" disabled={uploadingBg} onClick={() => setGalleryOpen(true)}><Images size={16} />从图库更换</button></div>
                <div className="zp-editor-section"><h2>调整构图</h2><p>拖动预览中的图片调整位置，拖动四角调整大小。</p><div className="zp-background-scale">图片比例<span>{Math.round(transform.scale * 100)}%</span></div><button className="zp-button zp-button-primary" onClick={() => setEditing(v => !v)}>{editing ? '完成调整' : '调整图片'}</button><button className="zp-button zp-button-secondary" onClick={() => commitTransform({scale: 1, x: 0, y: 0})}><RotateCcw size={16} />恢复默认构图</button></div>
              </div>}
              {editorTab === 'assets' && <div className="zp-editor-panel" id="editor-panel-assets" role="tabpanel" aria-labelledby="editor-tab-assets"><p className="zp-panel-intro">按需添加品牌标识和二维码，上传后同步显示在海报中。</p>
                {activeTemplate.include.includes('logo') && <MiniUpload label="Logo" value={logo} onChange={setLogo} />}
                {activeTemplate.include.includes('qr') && <MiniUpload label="二维码" value={qr} onChange={setQr} />}
                {!activeTemplate.include.includes('logo') && !activeTemplate.include.includes('qr') && <p className="zp-panel-intro">当前模板没有 Logo 或二维码位置，可更换模板后添加。</p>}
              </div>}
            </aside>

            {/* 画布 + 下载 */}
            <section className="zp-editor-workspace" aria-label="海报预览">
              <div className="zp-editor-toolbar"><button className="zp-editor-template" onClick={() => goStep(3)}><ArrowLeft size={16} />更换模板</button><button className="zp-button zp-button-primary" disabled={downloading} onClick={handleDownload}><Download size={18} />{downloading ? '正在生成…' : '下载海报'}</button></div>
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
              <p className="zp-export-note">1080 × 1920 px · PNG</p>
            </section>
          </div>
        )}
      </main>

      {galleryOpen && <GalleryModal gallery={gallery} current={bg?.kind === 'gallery' ? bg.name : undefined}
        loading={galleryLoading} failed={galleryFailed} onRetry={loadGallery}
        onClose={() => setGalleryOpen(false)} onPick={g => {
          setBg({ kind: 'gallery', name: g.name, url: g.url });
          setTransform({ scale: 1, x: 0, y: 0 });
          undoStack.current = [];
          redoStack.current = [];
          syncUndoFlags();
          setGalleryOpen(false);
        }} />}
    </div>
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
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const input = useRef<HTMLInputElement>(null);
  return <div className="zp-asset-upload"><h2>{label}</h2><p>{label === 'Logo' ? '建议使用透明背景的 PNG 图片。' : '上传清晰的二维码图片，保留四周留白。'}</p>
    {value && <div className="zp-asset-preview"><img src={value.url} alt={label} /></div>}
    <input ref={input} type="file" accept="image/png,image/jpeg,image/webp" className="hidden" onChange={async e => {
      const file = e.target.files?.[0]; e.target.value = ''; if (!file) return;
      setBusy(true); setError(null);
      try { onChange(await uploadFile(file)); } catch { setError('上传失败，请重试。'); } finally { setBusy(false); }
    }} />
    <div className="zp-editor-replace"><button className="zp-button zp-button-secondary" disabled={busy} onClick={() => input.current?.click()}><Upload size={16} />{busy ? '上传中…' : value ? `更换${label}` : `上传${label}`}</button>{value && <button className="zp-button zp-button-secondary" disabled={busy} onClick={() => onChange(null)}><X size={16} />移除</button>}</div>
    {error && <p role="alert" className="zp-upload-error">{error}</p>}
  </div>;
}
