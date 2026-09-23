import { useEffect, useState } from 'react';
import { ArrowLeft, ArrowRight, Check } from 'lucide-react';
import { fetchRenderURL, type BgRef, type TemplateItem } from '@/api';

function TemplatePreview({ template, bg, copy, selected, number, onSelect }: {
  template: TemplateItem; bg: BgRef | null; copy: Record<string, string>; selected: boolean; number: string; onSelect: () => void;
}) {
  const [result, setResult] = useState<{ key: string; url?: string; failed?: boolean } | null>(null);
  const [retry, setRetry] = useState(0);
  const data = Object.fromEntries(template.include.filter(key => !['logo','qr','course_slogan'].includes(key)).map(key => [key, copy[key] ?? template.field_defaults?.[key] ?? '']));
  const requestKey = JSON.stringify({ template: template.name, data, bg, width: 540, format: 'jpeg' });
  useEffect(() => {
    let cancelled = false;
    fetchRenderURL(JSON.parse(requestKey)).then(url => { if (!cancelled) setResult({key: requestKey, url}); }).catch(() => { if (!cancelled) setResult({key: requestKey, failed: true}); });
    return () => { cancelled = true; };
  }, [requestKey, retry]);
  const current = result?.key === requestKey ? result : null;
  return <article className={`zp-template-card ${selected ? 'is-selected' : ''}`}>
    <button className="zp-template-pick" aria-label={`选择模板 ${number}`} aria-pressed={selected} onClick={onSelect}><span className="zp-template-image">{current?.url ? <img src={current.url} alt={`模板 ${number} 排版预览`} loading="lazy" /> : <span className="zp-preview-status">{current?.failed ? '预览暂时无法加载' : '正在生成预览…'}</span>}{selected && <span className="zp-gallery-check"><Check size={17} /></span>}</span></button>
    {current?.failed && <button className="zp-preview-retry" onClick={() => setRetry(v => v + 1)}>重新加载预览</button>}
  </article>;
}
export default function TemplateSelection({ templates, bg, copies, selected, loading, failed, onRetry, onSelect, onBack, onEdit }: {
  templates: TemplateItem[]; bg: BgRef | null; copies: Record<string, Record<string,string>>;
  selected: string | null; loading: boolean; failed: boolean; onRetry: () => void; onSelect: (name: string) => void; onBack: () => void; onEdit: (name: string) => void;
}) {
  const numberOf = (t: TemplateItem, index: number) => t.name.match(/^[A-Za-z]+\d+/)?.[0] ?? String(index + 1).padStart(2,'0');
  const selectedIndex = templates.findIndex(t => t.name === selected);
  return <section className="zp-template-page"><div className="zp-workflow-page zp-template-content"><button className="zp-back" onClick={onBack}><ArrowLeft size={17} />返回选择背景</button><div className="zp-page-heading"><h1>选择模板风格</h1><p>同一张背景，不同的排版。选择你喜欢的一款开始编辑。</p></div><div className="zp-current-background">{bg && <img src={bg.url} alt="当前背景" />}<span>当前背景：{bg?.kind === 'gallery' ? bg.name.replace(/\.[^.]+$/, '') : '本地上传'}</span><button className="zp-change-background" onClick={onBack}>更换背景</button></div>
    {loading ? <p className="zp-inline-state" role="status">正在加载模板…</p> : failed ? <div className="zp-inline-state" role="alert"><p>模板暂时无法加载。</p><button className="zp-button zp-button-secondary" onClick={onRetry}>重新加载</button></div> : templates.length === 0 ? <p className="zp-inline-state">暂无可用模板</p> : <div className="zp-template-grid">{templates.map((t, index) => <TemplatePreview key={t.name} template={t} bg={bg} copy={copies[t.name] ?? {}} selected={selected === t.name} number={numberOf(t,index)} onSelect={() => onSelect(t.name)} />)}</div>}
    </div><footer className="zp-selection-footer"><span>{selectedIndex >= 0 ? '已选择模板' : '选择一款喜欢的模板'}</span><button className="zp-button zp-button-primary" disabled={selectedIndex < 0 || loading || failed} onClick={() => { if (selected) onEdit(selected); }}>开始编辑<ArrowRight size={18} /></button></footer></section>;
}
