// 실행 중인 웹 화면(URL)을 Figma 캡처 파이프라인으로 제출한다.
// 브라우저(헤드리스 chromium)에서 capture.js + window.figma.captureForDesign 을 실행해
// mcp.figma.com 캡쳐 엔드포인트로 제출하는 "브라우저 드라이버" 부분을 담당한다.
//
// scripts/figma-capture.ts 의 일반화 버전 — Design Studio project/page/scenario 대신
// 캡쳐할 URL 을 직접 받아 이 레포 밖에서도 쓸 수 있다. playwright 가 필요하다.
//
// 단일 화면:
//   1) Figma 캡처 생성 capability 호출 → captureId 발급
//   2) npm run capture -- <captureId> <url> [label]
//   3) Figma 캡처 상태 capability로 completed가 될 때까지 폴링
//
// 여러 화면(배치):
//   1) 화면마다 Figma 캡처 생성 capability 호출 → captureId N개 발급
//   2) [{ captureId, url, label? }, ...] 를 JSON 파일로 저장
//   3) npm run capture -- --batch <jobs.json>
//      → 브라우저 1개로 순회 캡처·제출, 화면별/전체 소요시간 출력
//   4) 각 captureId를 Figma 캡처 상태 capability로 completed까지 폴링
//
// 주의:
//  - captureForDesign 의 promise 는 끝까지 resolve 되지 않으므로 await 하지 않고,
//    submit POST(.../submit)의 응답을 page.waitForResponse 로 기다려 제출 완료를 감지한다.
//  - CSP 헤더를 제거해 capture.js 의 submit POST 가 막히지 않게 한다.
//  - 긴 페이지를 통째로 담기 위해 높이 사슬을 "세로로만" 풀어 펼친다(가로 클리핑 보존).

import { readFile } from 'node:fs/promises';

import { type Browser, chromium } from 'playwright';

import {
  assertSuccessfulSubmitPayload,
  parseJobs,
  type Job,
} from './capture-contracts.ts';

const CSP_HEADERS = new Set(['content-security-policy', 'content-security-policy-report-only']);
const SUBMIT_TIMEOUT_MS = 90_000;

async function captureJob(
  browser: Browser,
  job: Job,
): Promise<{ job: Job; fullHeight: number; submit: string; ms: number }> {
  const startedAt = Date.now();
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1024 },
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();
  try {
    // 문서(navigation) 응답에서만 CSP 헤더를 제거한다(capture.js 의 submit POST 가
    // 페이지 CSP 에 막히지 않도록). 나머지 요청은 그대로 통과시켜, 동시 캡처 시
    // 모든 에셋을 서버사이드 재요청하느라 원본 서버가 과부하되는 것을 막는다.
    await page.route('**/*', async (route) => {
      if (route.request().resourceType() !== 'document') {
        await route.continue();
        return;
      }
      try {
        const response = await route.fetch();
        const headers: Record<string, string> = {};
        for (const [k, v] of Object.entries(response.headers())) {
          if (!CSP_HEADERS.has(k.toLowerCase())) {
            headers[k] = v;
          }
        }
        await route.fulfill({ response, headers });
      } catch {
        await route.continue();
      }
    });

    await page.goto(job.url, { waitUntil: 'load', timeout: 30_000 });
    await page.waitForTimeout(2000);

    // 세로만 펼치고 가로는 뷰포트로 클립한다. overflow-x:clip 은 overflow-y:visible 과 충돌하지
    // 않아(visible→auto 강제 없음), 가로 스크롤이 있는 페이지가 풀 너비로 넓어지지 않고
    // 앱 화면처럼 뷰포트 폭으로 잘린다.
    await page.evaluate(() => {
      const st = document.createElement('style');
      st.textContent =
        'html,body{height:auto!important;overflow-y:visible!important;overflow-x:clip!important;max-width:100vw!important}' +
        '#preview-root{height:auto!important;overflow-y:visible!important;overflow-x:clip!important;max-width:100vw!important}';
      document.head.appendChild(st);
      for (const e of document.querySelectorAll<HTMLElement>('.h-screen,[class*=h-screen]')) {
        e.style.height = 'auto';
        e.style.minHeight = '100vh';
      }
      for (const e of document.querySelectorAll<HTMLElement>(
        'main,[class*=overflow-y-auto],[class*=overflow-auto]',
      )) {
        e.style.overflowY = 'visible';
        e.style.overflowX = 'clip';
        e.style.height = 'auto';
        e.style.maxHeight = 'none';
      }
      window.dispatchEvent(new Event('resize'));
    });
    await page.waitForTimeout(2500);

    // capture.js 주입 (텍스트 inline)
    const res = await context.request.get('https://mcp.figma.com/mcp/html-to-design/capture.js');
    if (!res.ok()) {
      throw new Error(`capture.js 다운로드 실패: HTTP ${res.status()}`);
    }
    const js = await res.text();
    await page.evaluate((s) => {
      const el = document.createElement('script');
      el.textContent = s;
      document.head.appendChild(el);
    }, js);
    await page.waitForTimeout(1000);

    const fullHeight = await page.evaluate(() => document.documentElement.scrollHeight);

    // captureForDesign 은 resolve 되지 않으므로 fire-and-forget 하고 submit 응답을 기다린다.
    const submitPart = `/mcp/capture/${job.captureId}/submit`;
    const [submitResponse] = await Promise.all([
      page
        .waitForResponse((r) => r.url().includes(submitPart), { timeout: SUBMIT_TIMEOUT_MS })
        .catch(() => {
          throw new Error(
            `Figma submit 응답을 ${Math.round(SUBMIT_TIMEOUT_MS / 1000)}초 안에 받지 못했습니다`,
          );
        }),
      page.evaluate(
        ({ id, endpoint }) => {
          const w = window as unknown as {
            figma: { captureForDesign: (o: unknown) => Promise<unknown> };
          };
          void w.figma.captureForDesign({ captureId: id, endpoint, selector: 'body' });
        },
        { id: job.captureId, endpoint: `https://mcp.figma.com/mcp/capture/${job.captureId}/submit` },
      ),
    ]);
    if (!submitResponse.ok()) {
      throw new Error(`Figma submit 실패: HTTP ${submitResponse.status()}`);
    }
    let submitPayload: unknown;
    try {
      submitPayload = await submitResponse.json();
    } catch {
      throw new Error('Figma submit 응답을 JSON으로 해석하지 못했습니다');
    }
    assertSuccessfulSubmitPayload(submitPayload);
    const submit = `submitted ${submitResponse.status()}`;
    await page.waitForTimeout(500);

    return { job, fullHeight, submit, ms: Date.now() - startedAt };
  } finally {
    await context.close();
  }
}

// 동시성 제한 풀: 최대 limit 개의 worker 를 동시에 돌리며 items 를 소진한다.
async function runPool<T, R>(
  items: T[],
  limit: number,
  worker: (item: T, index: number) => Promise<R>,
): Promise<R[]> {
  const out = new Array<R>(items.length);
  let next = 0;
  async function run(): Promise<void> {
    for (;;) {
      const i = next;
      next += 1;
      if (i >= items.length) {
        return;
      }
      out[i] = await worker(items[i] as T, i);
    }
  }
  await Promise.all(Array.from({ length: Math.max(1, Math.min(limit, items.length)) }, run));
  return out;
}

const USAGE =
  'usage: npm run capture -- <captureId> <url> [label]\n' +
  '       npm run capture -- --batch <jobs.json> [--concurrency N]\n' +
  '  jobs.json = [{ "captureId", "url", "label"? }, ...]\n' +
  '  동시 캡처 개수: --concurrency N (기본 1=순차 권장; 캡처가 CPU-bound라 병렬은 보통 더 느림)';

async function main(): Promise<void> {
  const argv = process.argv.slice(2);
  if (argv.includes('--help') || argv.includes('-h')) {
    console.log(USAGE);
    return;
  }

  const batch = argv[0] === '--batch';
  let jobs: Job[];
  let concurrency = 1;
  if (batch) {
    const jobsPath = argv[1];
    if (!jobsPath) {
      throw new Error(USAGE);
    }
    // 캡처(captureForDesign 직렬화)는 CPU-bound 라, 로컬 dev 서버 대상 병렬은 실측상 오히려
    // 느리고 submit 이 밀려 실패한다(2개 동시 → 각 153s/실패 vs 순차 ~10s/성공). 기본 순차(1).
    const cIdx = argv.findIndex((a) => a === '--concurrency' || a === '-c');
    const cRaw = cIdx >= 0 ? argv[cIdx + 1] : undefined;
    concurrency = Math.max(1, Number(cRaw ?? '1') || 1);
    jobs = parseJobs(await readFile(jobsPath, 'utf8'));
  } else {
    const captureId = argv[0];
    const url = argv[1];
    if (!captureId || !url) {
      throw new Error(`${USAGE}\n  captureId는 Figma 캡처 생성 capability로 먼저 발급받습니다.`);
    }
    jobs = [{ captureId, url, label: argv[2] ?? url }];
  }

  const browser = await chromium.launch({
    // 헤드리스 동시 실행 시 /dev/shm 고갈로 인한 브라우저 크래시("Target page ... closed")를 막는다.
    args: ['--disable-dev-shm-usage'],
    ...(process.env.CAPTURE_CHROMIUM_PATH
      ? { executablePath: process.env.CAPTURE_CHROMIUM_PATH }
      : {}),
  });
  try {
    const t0 = Date.now();
    let done = 0;
    const results = await runPool(jobs, concurrency, async (job) => {
      try {
        const r = await captureJob(browser, job);
        done += 1;
        console.log(
          `  [${done}/${jobs.length}] ${r.job.label} ` +
            `${r.fullHeight}px, ${r.ms}ms — ${r.submit} → captureId ${r.job.captureId}`,
        );
        return { ok: true, ms: r.ms };
      } catch (error) {
        done += 1;
        console.error(
          `  [${done}/${jobs.length}] ${job.label} FAILED: ${
            error instanceof Error ? error.message : String(error)
          }`,
        );
        return { ok: false, ms: 0 };
      }
    });
    const totalMs = Date.now() - t0;
    const okCount = results.filter((result) => result.ok).length;
    const sumMs = results.reduce((sum, result) => sum + result.ms, 0);
    console.log(
      `done: ${okCount}/${jobs.length} captured in ${totalMs}ms wall ` +
        `(concurrency ${concurrency}, 순차합 ${sumMs}ms)\n` +
        '  성공한 captureId만 Figma 캡처 상태 capability로 completed까지 폴링하세요.',
    );
    if (okCount !== jobs.length) {
      process.exitCode = 1;
    }
  } finally {
    await browser.close();
  }
}

void main().catch((error) => {
  console.error('[capture-url] failed:', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
