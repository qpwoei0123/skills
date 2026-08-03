export type Job = { captureId: string; url: string; label: string };

export function parseJobs(raw: string): Job[] {
  const data: unknown = JSON.parse(raw);
  if (!Array.isArray(data)) {
    throw new Error('jobs JSON 은 배열이어야 합니다');
  }
  if (data.length === 0) {
    throw new Error('jobs JSON 에는 캡처 작업이 1개 이상 필요합니다');
  }
  return data.map((item, index) => {
    if (
      !item ||
      typeof item.captureId !== 'string' ||
      !item.captureId.trim() ||
      typeof item.url !== 'string' ||
      !item.url.trim()
    ) {
      throw new Error(`jobs[${index}] 에 비어 있지 않은 captureId/url 문자열이 필요합니다`);
    }
    return {
      captureId: item.captureId,
      url: item.url,
      label: typeof item.label === 'string' ? item.label : item.url,
    } satisfies Job;
  });
}

export function assertSuccessfulSubmitPayload(payload: unknown): void {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new Error('Figma submit 응답 형식이 올바르지 않습니다');
  }
  const submitError = (payload as { error?: unknown }).error;
  if (submitError) {
    const detail = typeof submitError === 'string' ? submitError : JSON.stringify(submitError);
    throw new Error(`Figma submit 실패: ${detail}`);
  }
}
