import { Check, CircleHelp, X } from "lucide-react";
import {
  Dialog, DialogClose, DialogContent, DialogDescription, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";

const STEPS = ["选择类型", "选背景图", "选择模板", "编辑下载"];

export default function WorkflowHeader({ step, onBack }: {
  step: number;
  onBack: (step: number) => void;
}) {
  return (
    <header className="zp-header">
      <div className="zp-brand"><strong>海报设计小魔方</strong></div>
      <nav className="zp-steps" aria-label="海报制作进度">
        <ol>
          {STEPS.map((label, i) => (
            <li key={label} data-state={i + 1 === step ? "current" : i + 1 < step ? "done" : "upcoming"}>
              <button
                type="button"
                aria-current={i + 1 === step ? "step" : undefined}
                disabled={i + 1 >= step}
                onClick={() => onBack(i + 1)}
              >
                <span className="zp-step-number" aria-hidden="true">
                  {i + 1 < step ? <Check size={15} /> : i + 1}
                </span>
                <span>{label}</span>
              </button>
            </li>
          ))}
        </ol>
      </nav>
      <Dialog>
        <DialogTrigger asChild>
          <button type="button" className="zp-help"><CircleHelp size={18} aria-hidden="true" />使用帮助</button>
        </DialogTrigger>
        <DialogContent className="zp-help-dialog" showCloseButton={false}>
          <DialogTitle>制作一张海报</DialogTitle>
          <DialogDescription>从选择类型到下载，按这四步完成。</DialogDescription>
          <ol className="zp-help-list">
            <li><strong>选择类型</strong><p>根据活动用途，选择文案、信息图表或证书模板。</p></li>
            <li><strong>选择背景</strong><p>上传自己的图片，或打开精选图库挑选。</p></li>
            <li><strong>选择模板</strong><p>比较不同排版，点击喜欢的模板进入编辑。</p></li>
            <li><strong>编辑与下载</strong><p>修改文案、调整背景，按需上传 Logo 和二维码，然后下载海报。</p></li>
          </ol>
          <DialogClose className="zp-dialog-close" aria-label="关闭使用帮助"><X size={20} /></DialogClose>
          <DialogClose className="zp-button zp-button-primary">知道了</DialogClose>
        </DialogContent>
      </Dialog>
    </header>
  );
}
