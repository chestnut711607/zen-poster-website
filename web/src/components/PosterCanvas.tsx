// 海报画布：背景 + 文字层实时合成预览；编辑模式下可拖拽/四角缩放背景图。
// 移植自 Streamlit 版 image_editor/index.html，交互与参数（bg_transform）完全一致。
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import type { Transform } from "@/api";

const CANVAS_W = 1080;
const CANVAS_H = 1920;
const FADE = 48; // 上下渐变遮罩高度（px）
const FIT_MARGIN = FADE + 16; // 100% 预览时海报与渐变区间的距离

type DragState = {
  pointerId: number;
  startX: number;
  startY: number;
  initial: Transform;
  corner?: "nw" | "ne" | "sw" | "se";
  ratio: number;
  bounds: { x: number; y: number; w: number; h: number };
};

export type PosterCanvasProps = {
  bgUrl: string | null;
  overlayUrl: string | null;
  transform: Transform;
  editing: boolean;
  canUndo: boolean;
  canRedo: boolean;
  onTransformChange: (t: Transform) => void;
  onTransformCommit: (t: Transform) => void;
  onTransformNudge: (t: Transform) => void;
  onGestureBegin: () => void;
  onGestureEnd: () => void;
  onUndo: () => void;
  onRedo: () => void;
  onEditingChange: (editing: boolean) => void;
};

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

export default function PosterCanvas({
  bgUrl,
  overlayUrl,
  transform,
  editing,
  canUndo,
  canRedo,
  onTransformChange,
  onTransformCommit,
  onTransformNudge,
  onGestureBegin,
  onGestureEnd,
  onUndo,
  onRedo,
  onEditingChange,
}: PosterCanvasProps) {
  const viewportRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const bgImgRef = useRef<HTMLImageElement | null>(null);
  const overlayImgRef = useRef<HTMLImageElement | null>(null);
  const dragRef = useRef<DragState | null>(null);
  const transformRef = useRef(transform);
  const editingRef = useRef(editing);
  useLayoutEffect(() => {
    transformRef.current = transform;
    editingRef.current = editing;
  }, [transform, editing]);
  const [bgSize, setBgSize] = useState({ width: 0, height: 0 });

  const [zoom, setZoom] = useState(100);
  const [scale, setScale] = useState(0.2); // 海报 css 像素 / 画布像素
  const [ready, setReady] = useState(0); // 图片加载计数，触发重绘

  // 加载图片
  useEffect(() => {
    let cancelled = false;
    if (!bgUrl) {
      bgImgRef.current = null;
      return;
    }
    loadImage(bgUrl).then((img) => {
      if (!cancelled) {
        bgImgRef.current = img;
        setBgSize({ width: img.naturalWidth, height: img.naturalHeight });
        setReady((n) => n + 1);
      }
    }).catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [bgUrl]);

  useEffect(() => {
    let cancelled = false;
    if (!overlayUrl) {
      overlayImgRef.current = null;
      return;
    }
    loadImage(overlayUrl).then((img) => {
      if (!cancelled) {
        overlayImgRef.current = img;
        setReady((n) => n + 1);
      }
    }).catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [overlayUrl]);

  // 视口尺寸变化 → 重算 fit 比例
  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) return;
    const compute = () => {
      const w = viewport.clientWidth;
      const h = viewport.clientHeight;
      const fit = Math.min((w - 48) / CANVAS_W, Math.max(160, h - 2 * FIT_MARGIN) / CANVAS_H);
      setScale(Math.max(0.08, fit) * (zoom / 100));
    };
    compute();
    const ro = new ResizeObserver(compute);
    ro.observe(viewport);
    return () => ro.disconnect();
  }, [zoom]);

  const bounds = useCallback(() => {
    const img = bgImgRef.current;
    const t = transformRef.current;
    if (!img) return { x: 0, y: 0, w: 0, h: 0 };
    const ratio = Math.max(CANVAS_W / img.naturalWidth, CANVAS_H / img.naturalHeight) * t.scale;
    const w = img.naturalWidth * ratio;
    const h = img.naturalHeight * ratio;
    return { x: (CANVAS_W - w) / 2 + t.x, y: (CANVAS_H - h) / 2 + t.y, w, h };
  }, []);

  /** 约束位置：任何方向都不允许露出画布白边。
   *  注意 t.x/t.y 是相对「居中位置」的偏移（与后端 render_background 一致），
   *  因此可移动范围是 ±(图尺寸-画布尺寸)/2；某方向等宽/高时该方向锁死。 */
  const clampToCover = useCallback((t: Transform): Transform => {
    const img = bgImgRef.current;
    if (!img) return t;
    const ratio = Math.max(CANVAS_W / img.naturalWidth, CANVAS_H / img.naturalHeight) * t.scale;
    const w = img.naturalWidth * ratio;
    const h = img.naturalHeight * ratio;
    const rangeX = Math.max(0, (w - CANVAS_W) / 2);
    const rangeY = Math.max(0, (h - CANVAS_H) / 2);
    return {
      scale: t.scale,
      x: Math.max(-rangeX, Math.min(rangeX, t.x)),
      y: Math.max(-rangeY, Math.min(rangeY, t.y)),
    };
  }, []);

  // 重绘画布
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
    if (bgImgRef.current) {
      const b = bounds();
      ctx.drawImage(bgImgRef.current, b.x, b.y, b.w, b.h);
    }
    if (overlayImgRef.current) {
      ctx.drawImage(overlayImgRef.current, 0, 0, CANVAS_W, CANVAS_H);
    }
  }, [ready, transform, scale, bounds, bgUrl, overlayUrl]);

  // 缩放（保持指针下的点不动），移植自 zoomPreview；显示与状态均取整
  const zoomTo = useCallback((value: number, clientX?: number, clientY?: number) => {
    const viewport = viewportRef.current;
    if (!viewport) return;
    const clamped = Math.round(Math.max(30, Math.min(200, value)));
    const rect = viewport.getBoundingClientRect();
    const cx = clientX ?? rect.left + viewport.clientWidth / 2;
    const cy = clientY ?? rect.top + viewport.clientHeight / 2;
    const before = (scale * 100) / zoom; // fit 部分
    setZoom(clamped);
    // 状态更新后浏览器再滚动画面的比例换算在 effect 后进行；此处按新旧比例直接修正滚动
    const fit = before * clamped;
    const oldS = (before * zoom) / 100;
    const newS = fit / 100;
    if (oldS > 0) {
      const k = newS / oldS;
      viewport.scrollLeft = (viewport.scrollLeft + (cx - rect.left)) * k - (cx - rect.left);
      viewport.scrollTop = (viewport.scrollTop + (cy - rect.top)) * k - (cy - rect.top);
    }
  }, [scale, zoom]);

  // Ctrl+滚轮 / 触控板捏合缩放预览；普通滚轮保持滚动
  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) return;
    let gestureStart: number | null = null;
    const onWheel = (e: WheelEvent) => {
      if (!e.ctrlKey) return;
      e.preventDefault();
      if (gestureStart !== null) return;
      const unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? viewport.clientHeight : 1;
      zoomTo(zoom * Math.exp(-e.deltaY * unit * 0.01), e.clientX, e.clientY);
    };
    const onGestureStart = (e: Event) => {
      e.preventDefault();
      gestureStart = zoom;
    };
    const onGestureChange = (e: Event) => {
      e.preventDefault();
      if (gestureStart !== null) zoomTo(gestureStart * (e as unknown as { scale: number }).scale, (e as unknown as MouseEvent).clientX, (e as unknown as MouseEvent).clientY);
    };
    const onGestureEnd = (e: Event) => {
      e.preventDefault();
      gestureStart = null;
    };
    viewport.addEventListener("wheel", onWheel, { passive: false });
    viewport.addEventListener("gesturestart", onGestureStart, { passive: false });
    viewport.addEventListener("gesturechange", onGestureChange, { passive: false });
    viewport.addEventListener("gestureend", onGestureEnd, { passive: false });
    return () => {
      viewport.removeEventListener("wheel", onWheel);
      viewport.removeEventListener("gesturestart", onGestureStart);
      viewport.removeEventListener("gesturechange", onGestureChange);
      viewport.removeEventListener("gestureend", onGestureEnd);
    };
  }, [zoom, zoomTo]);

  // 编辑模式下：方向键微调背景位置（2px/次，按住 Shift 为 10px/次）；
  // Cmd/Ctrl+Z 撤回，Cmd/Ctrl+Shift+Z 重做
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!editingRef.current) return;
      const target = e.target as HTMLElement | null;
      if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) return;
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "z") {
        e.preventDefault();
        if (e.shiftKey) onRedo();
        else onUndo();
        return;
      }
      const step = e.shiftKey ? 10 : 2;
      let dx = 0;
      let dy = 0;
      if (e.key === "ArrowUp") dy = -step;
      else if (e.key === "ArrowDown") dy = step;
      else if (e.key === "ArrowLeft") dx = -step;
      else if (e.key === "ArrowRight") dx = step;
      else return;
      e.preventDefault();
      const t = transformRef.current;
      onTransformNudge(clampToCover({ ...t, x: t.x + dx, y: t.y + dy }));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onTransformNudge, onUndo, onRedo, clampToCover]);

  // 拖拽 / 四角缩放背景（编辑模式）
  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!editingRef.current) return;
    e.preventDefault();
    const corner = (e.target as HTMLElement).dataset.corner as DragState["corner"];
    onGestureBegin();
    dragRef.current = {
      pointerId: e.pointerId,
      startX: e.clientX,
      startY: e.clientY,
      initial: { ...transformRef.current },
      corner,
      ratio: scale,
      bounds: bounds(),
    };
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  };

  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== e.pointerId) return;
    const dx = (e.clientX - drag.startX) / drag.ratio;
    const dy = (e.clientY - drag.startY) / drag.ratio;
    if (drag.corner) {
      const sx = drag.corner.includes("e") ? 1 : -1;
      const sy = drag.corner.includes("s") ? 1 : -1;
      const { w, h } = drag.bounds;
      const change = ((sx * dx * w + sy * dy * h) / (w ** 2 + h ** 2)) * 2;
      // 缩放下限 1 倍：再小图片就铺不满画布，必然露白边
      const next = Math.max(1, Math.min(5, drag.initial.scale * (1 + change)));
      onTransformChange(clampToCover({ ...drag.initial, scale: next }));
    } else {
      onTransformChange(
        clampToCover({ ...drag.initial, x: drag.initial.x + dx, y: drag.initial.y + dy })
      );
    }
  };

  const onPointerEnd = (e: React.PointerEvent<HTMLDivElement>) => {
    if (dragRef.current?.pointerId === e.pointerId) {
      dragRef.current = null;
      onGestureEnd();
    }
  };

  // 选框位置（裁到画布内），用于编辑模式的边框与把手
  const ratio = bgUrl && bgSize.width && bgSize.height
    ? Math.max(CANVAS_W / bgSize.width, CANVAS_H / bgSize.height) * transform.scale
    : 0;
  const b = {
    w: bgSize.width * ratio,
    h: bgSize.height * ratio,
    x: (CANVAS_W - bgSize.width * ratio) / 2 + transform.x,
    y: (CANVAS_H - bgSize.height * ratio) / 2 + transform.y,
  };
  const sel = {
    left: Math.max(0, b.x) * scale,
    top: Math.max(0, b.y) * scale,
    width: Math.max(20, (Math.min(CANVAS_W, b.x + b.w) - Math.max(0, b.x)) * scale),
    height: Math.max(20, (Math.min(CANVAS_H, b.y + b.h) - Math.max(0, b.y)) * scale),
  };

  const posterW = CANVAS_W * scale;
  const posterH = CANVAS_H * scale;
  const handleCls =
    "absolute w-4 h-4 bg-white border-2 border-[#74B7D9] rounded-sm p-0 touch-none";
  const handles = [
    { corner: "nw", style: { left: -2, top: -2 }, cursor: "nwse-resize" },
    { corner: "ne", style: { right: -2, top: -2 }, cursor: "nesw-resize" },
    { corner: "sw", style: { left: -2, bottom: -2 }, cursor: "nesw-resize" },
    { corner: "se", style: { right: -2, bottom: -2 }, cursor: "nwse-resize" },
  ] as const;

  return (
    <div className="flex h-full flex-col">
      {/* 工具栏 */}
      <div className="flex min-h-11 shrink-0 flex-wrap items-center gap-3 px-1 py-1">
        <label className="flex shrink-0 items-center gap-2 whitespace-nowrap text-sm text-neutral-700">
          预览缩放
          <input
            type="range"
            min={30}
            max={200}
            value={zoom}
            onChange={(e) => zoomTo(Number(e.target.value))}
            className="w-32 accent-[#74B7D9]"
            aria-label="预览缩放"
          />
          <span className="w-11 tabular-nums">{zoom}%</span>
        </label>
        <div className="ml-auto flex shrink-0 items-center gap-2 whitespace-nowrap">
          {editing ? (
            <>
              <button
                className="rounded-md border border-neutral-300 bg-white px-2.5 py-1.5 text-sm leading-none hover:bg-neutral-50 disabled:opacity-35"
                onClick={onUndo}
                disabled={!canUndo}
                title="撤回（⌘Z）"
                aria-label="撤回"
              >
                ↶
              </button>
              <button
                className="rounded-md border border-neutral-300 bg-white px-2.5 py-1.5 text-sm leading-none hover:bg-neutral-50 disabled:opacity-35"
                onClick={onRedo}
                disabled={!canRedo}
                title="重做（⇧⌘Z）"
                aria-label="重做"
              >
                ↷
              </button>
              <div className="mx-1 h-5 w-px bg-neutral-200" />
              <button
                className="rounded-md border border-neutral-300 bg-white px-3.5 py-1.5 text-sm hover:bg-neutral-50"
                onClick={() => onTransformCommit({ scale: 1, x: 0, y: 0 })}
              >
                恢复默认
              </button>
              <button
                className="rounded-md bg-[#74B7D9] px-3.5 py-1.5 text-sm text-[#0D3A52] hover:bg-[#5AA5CC]"
                onClick={() => onEditingChange(false)}
              >
                确认
              </button>
            </>
          ) : null}
        </div>
      </div>

      {/* 视口：唯一可滚动区域，上下 48px 渐变遮罩 */}
      <div
        ref={viewportRef}
        className="relative min-h-0 flex-1 overflow-auto"
        style={{
          overscrollBehavior: "contain",
          WebkitMaskImage: `linear-gradient(to bottom, transparent, #000 ${FADE}px, #000 calc(100% - ${FADE}px), transparent)`,
          maskImage: `linear-gradient(to bottom, transparent, #000 ${FADE}px, #000 calc(100% - ${FADE}px), transparent)`,
        }}
      >
        <div
          className="flex min-h-full items-center justify-center p-6"
          style={{ minWidth: posterW + 48 }}
        >
          <div
            className="relative shrink-0 touch-none bg-white shadow-[0_3px_16px_rgba(0,0,0,0.14)]"
            style={{
              width: posterW,
              height: posterH,
              cursor: editing ? "move" : "default",
            }}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerEnd}
            onPointerCancel={onPointerEnd}
          >
            <canvas ref={canvasRef} width={CANVAS_W} height={CANVAS_H} className="block h-full w-full" />
            {editing && (
              <div
                className="pointer-events-none absolute border-2 border-[#74B7D9]"
                style={{ left: sel.left, top: sel.top, width: sel.width, height: sel.height }}
              >
                {handles.map(({ corner, style, cursor }) => (
                  <button
                    key={corner}
                    data-corner={corner}
                    aria-label={`${corner} 缩放`}
                    className={handleCls}
                    style={{ ...style, cursor, pointerEvents: "auto" }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
