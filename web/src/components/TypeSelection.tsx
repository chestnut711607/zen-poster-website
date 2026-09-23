import { useState } from "react";
import { ArrowRight, Download, ImageOff, RefreshCw } from "lucide-react";
import type { TemplateFileItem, TemplateType } from "@/api";

const PRESENTATION: Record<string, { image: string; description: string }> = {
  文案主导型: { image: "/type-previews/copy.jpg", description: "适合活动宣传与主题分享" },
  信息图表型: { image: "/type-previews/infographic.jpg", description: "适合课程安排与活动流程" },
  认证证书型: { image: "/type-previews/cert.jpg", description: "适合结业、荣誉与成长记录" },
};

function TypePreview({ name }: { name: string }) {
  const [failed, setFailed] = useState(false);
  const src = PRESENTATION[name]?.image;
  return (
    <span className="zp-type-preview">
      {src && !failed ? (
        <img src={src} alt={`${name}海报示例`} width="540" height="960" onError={() => setFailed(true)} />
      ) : (
        <span className="zp-preview-fallback"><ImageOff size={28} aria-hidden="true" /><span>暂无预览，可继续选择</span></span>
      )}
    </span>
  );
}

export default function TypeSelection({ types, files, loading, failed, onRetry, onPick }: {
  types: TemplateType[];
  files: Record<string, TemplateFileItem[]>;
  loading: boolean;
  failed: boolean;
  onRetry: () => void;
  onPick: (name: string) => void;
}) {
  const available = types.filter((type) => type.available);
  const upcoming = types.filter((type) => !type.available);
  return (
    <section className="zp-home" aria-labelledby="home-title">
      <div className="zp-page-heading">
        <h1 id="home-title">选择海报类型</h1>
        <p>从适合活动的版式开始，几步完成一张海报。</p>
      </div>

      {loading ? (
        <div role="status" aria-label="正在加载海报类型">
          <span className="sr-only">正在加载海报类型…</span>
          <div className="zp-type-grid" aria-hidden="true">
            {[0, 1, 2].map((i) => <div className="zp-type-skeleton" key={i}><div /><span /><span /></div>)}
          </div>
        </div>
      ) : failed || available.length === 0 ? (
        <div className="zp-empty-state" role={failed ? "alert" : "status"}>
          <h2>{failed ? "暂时无法加载海报类型" : "暂无可用模板"}</h2>
          <p>{failed ? "请检查网络连接后重试。" : "请稍后刷新，查看最新的模板。"}</p>
          <button type="button" className="zp-button zp-button-primary" onClick={onRetry}><RefreshCw size={17} aria-hidden="true" />重新加载</button>
        </div>
      ) : (
        <div className="zp-type-grid">
          {available.map((type) => (
            <article key={type.name} className="zp-type-card">
              <button type="button" className="zp-type-pick" onClick={() => onPick(type.name)} aria-label={`选择${type.name}，开始制作`}>
                <TypePreview name={type.name} />
                <span className="zp-type-copy">
                  <span className="zp-type-title">{type.name}</span>
                  <span className="zp-type-description">{PRESENTATION[type.name]?.description ?? type.desc}</span>
                </span>
                <span className="zp-type-footer">
                  <span className="zp-template-count">{type.template_count} 个模板</span>
                  <span className="zp-card-action" aria-hidden="true"><span>开始制作</span><ArrowRight size={20} /></span>
                </span>
              </button>
              {(files[type.name]?.length ?? 0) > 0 && (
                <a className="zp-template-download" href={`/api/template-files/${encodeURIComponent(type.name)}/download`} title={files[type.name].map((file) => file.name).join("、")}>
                  <Download size={15} aria-hidden="true" />下载模板文件（{files[type.name].length}）
                </a>
              )}
            </article>
          ))}
        </div>
      )}

      {!loading && !failed && upcoming.length > 0 && (
        <div className="zp-coming-soon">{upcoming.map((type) => <p key={type.name}><span>{type.name} · 即将推出</span></p>)}</div>
      )}
      <p className="zp-home-hint">选择类型后，可继续挑选背景和模板。</p>
    </section>
  );
}
