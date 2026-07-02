# code-to-figma

`version: 0.1.0`

구현된 웹 화면(URL)을 Figma 파일로 옮기는 스킬. 단일 화면은 디자인 시스템에 바인딩된
편집 가능한 레이어로, 여러 화면은 픽셀 캡처 후 한 Figma 페이지에 그리드 정렬로 옮긴다.

## Quick Start

요구사항:

- Claude Code + Figma 공식 플러그인(`figma@claude-plugins-official`) 인증 1회
  (플러그인 설치/활성화는 스킬이 직접 수행하고, 로그인 승인만 사용자가 한다)
- 결과를 넣을 Figma 파일의 편집 권한
- 여러 화면 배치 모드만: `tsx` + `playwright` + chromium (`npx playwright install chromium`)

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
├── references/
│   ├── input-contract.md                 # 작업 계약 4칸 + 조합별 응답 기준
│   ├── design-system-discovery.md        # DS 발견 우선순위·매핑표·연동 정의
│   └── response-templates.md             # 상황별 사용자 응답 문구
└── scripts/
    └── capture-url.ts                    # URL → Figma 픽셀 캡처 드라이버 (Playwright)
```

## Scripts

`scripts/capture-url.ts`는 여러 화면 배치 모드에서 헤드리스 chromium으로 화면을 열어
Figma 캡처 엔드포인트에 제출한다. `captureId`는 `generate_figma_design(fileKey)` MCP
호출로 먼저 발급받는다.

```bash
# 단일 화면
npx tsx scripts/capture-url.ts <captureId> <url> [label]

# 여러 화면 (jobs.json = [{ "captureId", "url", "label"? }, ...])
npx tsx scripts/capture-url.ts --batch <jobs.json> [--concurrency N]
```

## Test

```bash
# 스킬 형식 검증 (레포 루트에서)
python3 scripts/validate_skills.py --skill code-to-figma

# 캡처 드라이버 인자 파싱 확인 (usage 출력 + exit 1)
npx tsx code-to-figma/scripts/capture-url.ts
```
