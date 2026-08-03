import assert from 'node:assert/strict';
import test from 'node:test';

import { assertSuccessfulSubmitPayload, parseJobs } from './capture-contracts.ts';

test('빈 batch를 거절한다', () => {
  assert.throws(() => parseJobs('[]'), /1개 이상/);
});

test('비어 있는 capture ID와 URL을 거절한다', () => {
  assert.throws(
    () => parseJobs('[{"captureId":" ","url":"http://localhost"}]'),
    /비어 있지 않은/,
  );
});

test('2xx 응답 본문의 error를 실패로 처리한다', () => {
  assert.throws(
    () => assertSuccessfulSubmitPayload({ error: 'capture denied' }),
    /capture denied/,
  );
});

test('정상 submit 응답을 허용한다', () => {
  assert.doesNotThrow(() => assertSuccessfulSubmitPayload({ claimUrl: 'https://figma.com/file' }));
});
