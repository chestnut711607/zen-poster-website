import assert from 'node:assert/strict';
import test from 'node:test';
import { getTitleStatus, wrapTitle } from './labels.ts';

test('automatically wraps every six characters without dropping text', () => {
  assert.equal(wrapTitle('一二三四五六七'), '一二三四五六\n七');
  const source = '一二三四五六七八九十一二三四五六七八';
  assert.equal(wrapTitle(source).split('\n').length, 3);
  assert.equal(wrapTitle(source).replace(/\n/g, ''), source);
  assert.equal(wrapTitle('𠮷一二三四五六'), '𠮷一二三四五\n六');
});

test('18 characters in three lines fit without warnings', () => {
  assert.deepEqual(getTitleStatus('一二三四五六\n一二三四五六\n一二三四五六'), { count: 18, message: null });
});
test('preserves manual breaks, blank lines and trailing Enter', () => {
  assert.equal(wrapTitle('以花观心\n体会生命中的\n喜悦之美'), '以花观心\n体会生命中的\n喜悦之美');
  assert.equal(wrapTitle('一二\n三四五六七八九\n'), '一二\n三四五六七八\n九\n');
  assert.equal(wrapTitle('一\n\n二\n'), '一\n\n二\n');
  assert.equal(wrapTitle(''), '');
});
test('long titles report overflow without returning replacement text', () => {
  const title = '一二三四五六七八九十一二三四五六七八九十';
  const status = getTitleStatus(title);
  assert.equal(status.count, 20);
  assert.match(status.message, /超出 2 字/);
  assert.equal('text' in status, false);
});
test('line limits and Unicode counts are checked independently', () => {
  assert.match(getTitleStatus('一二三四五六七').message, /单行超过 6 字/);
  assert.match(getTitleStatus('一\n二\n三\n四').message, /超过 3 行/);
  assert.equal(getTitleStatus('𠮷\r\n好').count, 2);
  assert.deepEqual(getTitleStatus(''), { count: 0, message: null });
});
