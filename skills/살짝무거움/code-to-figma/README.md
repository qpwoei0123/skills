# code-to-figma

`version: 0.1.1`

구현된 웹 화면(URL)을 Figma 파일로 옮기는 스킬. 단일 화면은 디자인 시스템에 바인딩된
편집 가능한 레이어로, 여러 화면은 픽셀 캡처 후 한 Figma 페이지에 그리드 정렬로 옮긴다.

## Quick Start

요구사항:

- 현재 호스트에 연결된 Figma 읽기·편집 capability(도구명은 무관)
- 결과를 넣을 Figma 파일의 편집 권한
- 여러 화면 배치 모드만: Node.js 20+, `npm ci`, `npm exec -- playwright install chromium`

사용 예:

```text
이 화면 피그마로 옮겨줘.
원본: http://localhost:3000/dashboard
목적지: https://www.figma.com/design/abc123/My-File?node-id=12-34
```

```text
/code-to-figma 이 4개 화면을 피그마로 일괄 추출해줘. https://... https://... https://... https://...
```

스킬은 작업 계약 4칸(Figma 권한 / 원본 화면 / Figma 목적지 / 디자인 시스템)을 확인하고,
부족한 칸만 되물은 뒤 실행 전 요약을 보여주고 진행한다.

## Structure

```text
code-to-figma/
├── SKILL.md                              # 실행 계약 (5단계 워크플로)
├── README.md
├── CHANGELOG.md
├── package.json                          # 캡처 CLI·고정 의존성
├── package-lock.json
├── agents/
│   └── openai.yaml                      # OpenAI 스킬 메타데이터
├── evals/
│   └── trigger-eval.json                 # 트리거 경계 케이스
├── references/
│   ├── input-contract.md                 # 작업 계약 4칸 + 조합별 응답 기준
│   ├── design-system-discovery.md        # DS 발견 우선순위·매핑표·연동 정의
│   └── response-templates.md             # 상황별 사용자 응답 문구
└── scripts/
    ├── capture-contracts.ts              # batch 입력·submit 응답 계약
    ├── capture-contracts.test.ts         # 캡처 계약 회귀 테스트
    └── capture-url.ts                    # URL → Figma 픽셀 캡처 드라이버 (Playwright)
```

## Scripts

`scripts/capture-url.ts`는 여러 화면 배치 모드에서 헤드리스 chromium으로 화면을 열어
Figma 캡처 엔드포인트에 제출한다. 스킬 폴더에서 아래를 한 번 실행해 재현 가능한
의존성과 chromium을 준비한다.

```bash
npm ci
npm exec -- playwright install chromium
```

`captureId`는 현재 환경의 Figma 캡처 생성 capability로 먼저 발급받는다.

```bash
# 단일 화면
npm run capture -- <captureId> <url> [label]

# 여러 화면 (jobs.json = [{ "captureId", "url", "label"? }, ...])
npm run capture -- --batch <jobs.json> [--concurrency N]
```

submit 응답 timeout·HTTP·본문 오류는 실패로 집계하고, 배치 중 하나라도 실패하면 나머지를
시도한 뒤 프로세스를 non-zero로 종료한다.

## Test

```bash
# 스킬 형식 검증 (레포 루트에서)
python3 scripts/validate_skills.py --skill code-to-figma

# 캡처 드라이버 smoke (스킬 폴더에서, usage 출력 + exit 0)
npm ci
npm test
npm run smoke
```
