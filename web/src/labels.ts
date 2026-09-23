// 字段标签与输入规则，与 Streamlit 版 main.py 保持一致
export const FIELD_LABELS: Record<string, string> = {
  title_text_cn: "中文主标题",
  title_text_eg: "英文副标题",
  title_text_mm1: "居中主标题(CN)",
  title_text_mm2: "居中副标题(EN)",
  date_num: "日期数字",
  date_year_week: "年份/星期",
  date_time: "具体时间",
  prog_label_bil: "内容标签(双语)",
  prog_cont_cn_a: "内容详情(单行)",
  prog_label_cn: "内容标签(中)",
  prog_label_eg: "内容标签(英)",
  prog_cont_cn_b: "内容详情(换行)",
  prog_cont_eg: "内容详情(英)",
  venue_label_bil: "地址标签(双语)",
  venue_cont_cn_a: "地址详情(换行)",
  venue_label_cn: "地址标签(中)",
  venue_label_eg: "地址标签(英)",
  venue_cont_cn_b: "地址详情(单行)",
  venue_cont_cn_c: "地址详情(换行)",
  venue_cont_eg: "地址详情(英)",
  qr_label_bil: "报名标签(双语)",
  qr_label_cn: "报名标签(中)",
  qr_label_eg: "报名标签(英)",
  qr_tip_a: "提示语(单行)",
  qr_tip_b: "提示语(换行)",
  qr_tip_eg: "提示语(英)",
  sched_label_cn: "标题（中文，两个字，需换行）",
  sched_label_eg: "标题（英文）",
  course_title_cn: "课程主标题（中文，四个字，换行）",
  course_title_eg: "课程主标题（英文，可换行）",
  course_date_range: "课程日期范围",
  course_qr_tip_cn: "二维码旁说明（中文）",
  course_qr_tip_eg: "二维码旁说明（英文）",
  cert_brand_tl: "左上角品牌字",
  cert_greeting: "祝贺语（如：随喜赞叹）",
  cert_name: "法名 / 姓名",
  cert_body: "证书正文（可换行）",
  cert_title_cn: "证书主标题（中文，可换行）",
  cert_title_eg: "证书副标题（英文）",
  cert_issuer: "落款单位",
  cert_issue_date: "落款日期",
  cert_footer: "底部标语",
};

for (let i = 1; i <= 7; i++) {
  FIELD_LABELS[`sched_num_${i}`] = `流程第${i}项·序号`;
  FIELD_LABELS[`sched_name_cn_${i}`] = `流程第${i}项·中文`;
  FIELD_LABELS[`sched_name_eg_${i}`] = `流程第${i}项·英文`;
  FIELD_LABELS[`sched_time_${i}`] = `流程第${i}项·时段`;
  FIELD_LABELS[`day_date_${i}`] = `第${i}天·日期`;
  FIELD_LABELS[`day_week_${i}`] = `第${i}天·星期`;
  FIELD_LABELS[`day_time_${i}`] = `第${i}天·时间（第1行）`;
  FIELD_LABELS[`day_time2_${i}`] = `第${i}天·时间（第2行）`;
  FIELD_LABELS[`day_cont_${i}`] = `第${i}天·内容（第1行）`;
  FIELD_LABELS[`day_cont2_${i}`] = `第${i}天·内容（第2行）`;
}

/** 多行字段规则：与 main.py 一致 */
export function isTextareaField(key: string): boolean {
  return (
    key.includes("cont") ||
    key.includes("tip") ||
    key.includes("title") ||
    key.includes("sched_label") ||
    ["cert_body", "cert_greeting", "cert_footer"].includes(key)
  );
}

export function wrapTitle(text: string): string {
  const lines: string[] = [];
  for (const line of text.split(/\r\n|\r|\n/)) {
    const chars = Array.from(line);
    if (!chars.length) lines.push('');
    for (let i = 0; i < chars.length; i += 6) lines.push(chars.slice(i, i + 6).join(''));
  }
  return lines.join('\n');
}

/** Validate layout without truncating the user's title. */
export function getTitleStatus(text: string) {
  const lines = text.split(/\r\n|\r|\n/);
  const count = lines.reduce((total, line) => total + Array.from(line).length, 0);
  const issues: string[] = [];
  if (count > 18) issues.push(`超出 ${count - 18} 字，请自行缩短至 18 字以内`);
  if (lines.some((line) => Array.from(line).length > 6)) issues.push('单行超过 6 字，请自行换行或缩短');
  if (lines.length > 3) issues.push('超过 3 行，请自行调整');
  return { count, message: issues.length ? issues.join('；') : null };
}
