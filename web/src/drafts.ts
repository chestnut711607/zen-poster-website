type Copy = Record<string, string>;
type Template = { include: string[]; field_defaults?: Copy };

export function resolveDraft(template: Template, defaults: Copy, compatible: Copy, saved: Copy = {}): Copy {
  return Object.fromEntries(template.include
    .filter((key) => !['logo', 'qr', 'course_slogan'].includes(key))
    .map((key) => [key, saved[key] ?? compatible[key] ?? template.field_defaults?.[key] ?? defaults[key] ?? '']));
}
