import assert from 'node:assert/strict';
import test from 'node:test';
import { resolveDraft } from './drafts.ts';

const template = { include: ['title', 'date', 'venue', 'logo'], field_defaults: { title: 'Template title', venue: 'Template venue' } };
test('new template inherits compatible edited fields but uses its own defaults', () => {
  assert.deepEqual(resolveDraft(template, { date: 'Monday' }, { title: 'My title', unrelated: 'ignore' }),
    { title: 'My title', date: 'Monday', venue: 'Template venue' });
});
test('saved template draft takes priority, including intentionally empty fields', () => {
  assert.deepEqual(resolveDraft(template, {}, { title: 'Other title', date: 'Tuesday' }, { title: '', date: 'Monday' }),
    { title: '', date: 'Monday', venue: 'Template venue' });
});
