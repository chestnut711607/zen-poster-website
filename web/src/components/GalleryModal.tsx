import { useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Check, X } from 'lucide-react';
import type { ReactNode } from 'react';
import type { GalleryItem } from '@/api';
import { Dialog, DialogContent, DialogTitle, DialogDescription } from '@/components/ui/dialog';
const categoryOf = (name: string) => name.replace(/\.[^.]+$/, '').replace(/[\d\s]+$/, '');
function OrderedGallery({ children }: { children: ReactNode }) {
  const container = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    const root = container.current;
    if (!root) return;
    const layout = () => {
      const styles = getComputedStyle(root);
      const columns = Number(styles.getPropertyValue('--gallery-columns'));
      const gap = Number(styles.getPropertyValue('--gallery-gap'));
      const width = (root.clientWidth - gap * (columns - 1)) / columns;
      const heights = Array<number>(columns).fill(0);
      Array.from(root.children).forEach((child, index) => {
        const card = child as HTMLElement;
        const column = index % columns;
        card.style.width = `${width}px`;
        card.style.left = `${column * (width + gap)}px`;
        card.style.top = `${heights[column]}px`;
        heights[column] += card.offsetHeight + gap;
      });
      root.style.height = `${Math.max(0, ...heights) - gap}px`;
    };
    layout();
    const observer = new ResizeObserver(layout);
    observer.observe(root);
    Array.from(root.children).forEach(child => observer.observe(child));
    return () => observer.disconnect();
  }, [children]);
  return <div ref={container} className="zp-gallery-grid">{children}</div>;
}

export default function GalleryModal({ gallery, current, loading, failed, onRetry, onClose, onPick }: {
  gallery: GalleryItem[]; current?: string; loading: boolean; failed: boolean;
  onRetry: () => void; onClose: () => void; onPick: (item: GalleryItem) => void;
}) {
  const [category, setCategory] = useState('全部');
  const [selected, setSelected] = useState(current ?? '');
  const [returnFocus] = useState(() => document.activeElement as HTMLElement | null);
  const categories = useMemo(() => ['全部', ...new Set(gallery.map(g => categoryOf(g.name)))], [gallery]);
  const filtered = gallery.filter(g => category === '全部' || categoryOf(g.name) === category);
  const item = gallery.find(g => g.name === selected);
  return <Dialog open onOpenChange={open => { if (!open) onClose(); }}><DialogContent className="zp-gallery-dialog" showCloseButton={false} onCloseAutoFocus={e => { e.preventDefault(); returnFocus?.focus(); }}>
    <div className="zp-gallery-heading"><DialogTitle>精选图库</DialogTitle><DialogDescription>挑选一张背景，确认后查看完整预览。</DialogDescription><button className="zp-dialog-close" aria-label="关闭图库" onClick={onClose}><X size={20} /></button></div>
    <div className="zp-gallery-filters" aria-label="图库分类">{categories.map(c => <button key={c} aria-pressed={category === c} onClick={() => setCategory(c)}>{c}</button>)}</div>
    <div className="zp-gallery-scroll" key={category}>
      {loading ? <p className="zp-inline-state" role="status">正在加载图库…</p> : failed ? <div className="zp-inline-state" role="alert"><p>图库暂时无法加载。</p><button className="zp-button zp-button-secondary" onClick={onRetry}>重新加载</button></div> : filtered.length === 0 ? <p className="zp-inline-state">暂无图片</p> : <OrderedGallery>{filtered.map(g => <button className="zp-gallery-item" key={g.name} aria-label={`选择背景 ${g.name.replace(/\.[^.]+$/, '')}`} aria-pressed={selected === g.name} onClick={() => setSelected(g.name)}><span className="zp-gallery-image" style={g.width && g.height ? { aspectRatio: `${g.width} / ${g.height}` } : undefined}><img src={g.thumb ?? g.url} width={g.width} height={g.height} alt="" loading="lazy" />{selected === g.name && <span className="zp-gallery-check"><Check size={17} /></span>}</span><span>{g.name.replace(/\.[^.]+$/, '')}</span></button>)}</OrderedGallery>}
    </div>
    <div className="zp-gallery-footer"><span>{item ? `已选：${item.name.replace(/\.[^.]+$/, '')}` : '请选择一张背景'}</span><button className="zp-button zp-button-primary" disabled={!item || loading || failed} onClick={() => { if (item) onPick(item); }}>使用这张背景</button></div>
  </DialogContent></Dialog>;
}
