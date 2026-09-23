// API 层：与 zen-poster-mvp/api_server.py 对应
export type TemplateType = {
  name: string;
  desc: string;
  emoji: string;
  tag: string;
  available: boolean;
  template_count: number;
  preview_bg_color: string;
  preview_text_color: string;
};

export type TemplateItem = {
  name: string;
  color: string;
  bg_img: string;
  include: string[];
  field_defaults: Record<string, string>;
};

export type GalleryItem = { name: string; url: string; thumb?: string; width?: number; height?: number };

export type TemplateFileItem = { name: string; size: number };

export type BgRef =
  | { kind: "gallery"; name: string; url: string }
  | { kind: "upload"; id: string; url: string };

export type Transform = { scale: number; x: number; y: number };

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json() as Promise<T>;
}

export const fetchTemplateTypes = () => getJson<TemplateType[]>("/api/template-types");
export const fetchTemplates = (type: string) =>
  getJson<TemplateItem[]>(`/api/templates?type=${encodeURIComponent(type)}`);
export const fetchDefaultCopy = () => getJson<Record<string, string>>("/api/default-copy");
export const fetchGallery = () =>
  getJson<{ items: GalleryItem[] }>("/api/gallery").then((d) => d.items);
export const fetchTemplateFiles = () =>
  getJson<Record<string, TemplateFileItem[]>>("/api/template-files");

export async function uploadFile(file: File): Promise<{ id: string; url: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/upload", { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  const { id } = (await res.json()) as { id: string };
  return { id, url: URL.createObjectURL(file) };
}

export type RenderParams = {
  template: string;
  data: Record<string, string>;
  bg?: BgRef | null;
  logoId?: string | null;
  qrId?: string | null;
  transform?: Transform;
  width: number;
  format: "png" | "jpeg";
  overlayOnly?: boolean;
};

function buildForm(p: RenderParams): FormData {
  const form = new FormData();
  form.append("template_name", p.template);
  form.append("data_json", JSON.stringify(p.data));
  if (p.bg?.kind === "gallery") form.append("bg_name", p.bg.name);
  if (p.bg?.kind === "upload") form.append("bg_upload_id", p.bg.id);
  if (p.logoId) form.append("logo_upload_id", p.logoId);
  if (p.qrId) form.append("qr_upload_id", p.qrId);
  form.append("transform_json", JSON.stringify(p.transform ?? { scale: 1, x: 0, y: 0 }));
  form.append("width", String(p.width));
  form.append("format", p.format);
  if (p.overlayOnly) form.append("overlay_only", "true");
  return form;
}

// 渲染结果缓存：相同参数直接复用 objectURL，避免逐字预览时重复请求/闪烁
const imageCache = new Map<string, string>();
const CACHE_LIMIT = 60;

export async function fetchRenderURL(p: RenderParams): Promise<string> {
  const key = JSON.stringify(p);
  const hit = imageCache.get(key);
  if (hit) return hit;
  const res = await fetch("/api/render", { method: "POST", body: buildForm(p) });
  if (!res.ok) throw new Error(await res.text());
  const url = URL.createObjectURL(await res.blob());
  if (imageCache.size >= CACHE_LIMIT) {
    const oldest = imageCache.keys().next().value!;
    URL.revokeObjectURL(imageCache.get(oldest)!);
    imageCache.delete(oldest);
  }
  imageCache.set(key, url);
  return url;
}

export async function downloadPoster(p: RenderParams, filename: string): Promise<void> {
  const res = await fetch("/api/render", { method: "POST", body: buildForm(p) });
  if (!res.ok) throw new Error(await res.text());
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}
