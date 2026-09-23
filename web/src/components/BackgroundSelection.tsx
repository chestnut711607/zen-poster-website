import { useRef, useState } from 'react';
import { ArrowLeft, ArrowRight, Images, Upload } from 'lucide-react';
import type { BgRef } from '@/api';

export default function BackgroundSelection({ bg, typeName, busy, onUpload, onGallery, onBack, onNext }: {
  bg: BgRef | null; typeName: string | null; busy: boolean;
  onUpload: (file: File) => void; onGallery: () => void; onBack: () => void; onNext: () => void;
}) {
  const input = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  return <section className={`zp-workflow-page zp-background-page ${bg ? "is-confirmed" : ""}`}>
    <button className="zp-back" onClick={onBack}><ArrowLeft size={17} />返回选择类型</button>
    <div className="zp-page-heading"><h1>选择背景图片</h1><p>为海报挑选一张合适的背景，也可以上传自己的图片。</p><span className="zp-type-badge">{typeName}</span></div>
    <input ref={input} type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" tabIndex={-1} aria-label="上传背景图片" disabled={busy} onChange={e => { const file = e.target.files?.[0]; e.target.value = ''; if (file) onUpload(file); }} />
    {bg ? <div className="zp-background-confirm">
      <div className="zp-background-preview"><img src={bg.url} alt="所选背景完整预览" /></div>
      <div className="zp-background-actions"><span className="zp-eyebrow">背景已就绪</span><h2>确认这张背景</h2><p>图片按原始比例完整展示。进入编辑后，还可以调整图片大小与位置。</p><div className="zp-replace-actions"><button className="zp-button zp-button-secondary" disabled={busy} onClick={() => input.current?.click()}><Upload size={17} />{busy ? '上传中…' : '重新上传'}</button><button className="zp-button zp-button-secondary" disabled={busy} onClick={onGallery}><Images size={17} />从图库更换</button></div><button className="zp-button zp-button-primary" disabled={busy} onClick={onNext}>下一步：选择模板<ArrowRight size={18} /></button></div>
    </div> : <div className="zp-background-entries">
      <button className={`zp-source-card ${dragging ? 'is-dragging' : ''}`} disabled={busy} onClick={() => input.current?.click()} onDragOver={e => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={e => { e.preventDefault(); setDragging(false); const file = e.dataTransfer.files?.[0]; if (file && !busy) onUpload(file); }}><span className="zp-source-icon"><Upload size={30} /></span><h2>本地上传</h2><p>点击上传或拖拽图片到这里</p><span className="zp-source-hint">支持 JPG、PNG、WebP</span><span className="zp-source-link">{busy ? '正在上传…' : '选择图片'}<ArrowRight size={18} /></span></button>
      <button className="zp-source-card" disabled={busy} onClick={onGallery}><span className="zp-source-icon"><Images size={30} /></span><h2>精选图库</h2><p>从精选图片中寻找适合活动的背景</p><span className="zp-source-hint">按主题浏览，轻松挑选</span><span className="zp-source-link">打开图库<ArrowRight size={18} /></span></button>
    </div>}
    <p className="zp-home-hint" role="status">{busy ? '正在上传背景，请稍候…' : '建议选择清晰、留有文字空间的图片。'}</p>
  </section>;
}
