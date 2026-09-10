# code-to-figma

`version: 1.0.0`

구현된 웹 화면을 Figma로 옮기고 필요한 편집 구조와 디자인 시스템 연결을 확인합니다. 여러 화면에서도 요청한 결과 수준을 유지합니다.

## Quick Start

```text
$code-to-figma 현재 localhost 대시보드를 이 Figma 파일로 옮겨줘.
목적지: https://www.figma.com/design/abc123/My-File?node-id=12-34
```

```text
$code-to-figma 현재 네 화면을 새 Figma 파일에 편집 가능한 레이어로 옮겨줘.
```

원본과 목적지는 현재 맥락에서 먼저 확인하고, 실제로 빠진 정보만 묻습니다. 새 파일을 요청하면 생성하며, DS가 지정되지 않으면 목적지의 실제 매핑을 탐색합니다. 매핑이 없는 부분은 새 레이어로 만들고 연결 상태를 보고합니다. 필수 DS 요구는 조용히 대체하지 않습니다.

현재 호스트의 Figma 읽기·쓰기·결과 확인 capability와 목적지 편집 권한이 필요합니다. 읽기 성공을 편집 권한으로 해석하지 않습니다. 도구별 필수 skill과 사용자 환경의 동의 규칙도 따릅니다.

## Structure

```text
code-to-figma/
├── SKILL.md, README.md, CHANGELOG.md
├── package.json, package-lock.json
├── agents/openai.yaml
├── evals/trigger-eval.json
├── references/
│   ├── input-contract.md
│   ├── design-system-discovery.md
│   └── response-templates.md
└── scripts/
    ├── capture-url.ts              # Playwright 기반 DOM-to-design 제출
    ├── capture-contracts.ts        # batch 입력·submit 응답 계약
    └── capture-contracts.test.ts   # 기존 회귀 테스트
```

## Scripts

capture 경로를 사용할 때만 Node.js 20+와 lockfile 의존성·Chromium을 준비합니다. 이미 준비된 환경은 재설치하지 않습니다.

```bash
npm ci
npm exec -- playwright install chromium
```

현재 Figma capture 도구에서 ID를 받은 뒤 스킬 폴더에서 실행합니다.

```bash
npm run capture -- <captureId> <url> [label]
npm run capture -- --batch <jobs.json> [--concurrency N]
```

`jobs.json`은 `[{ "captureId": "...", "url": "...", "label": "..." }]` 배열입니다. 드라이버는 DOM을 Figma endpoint로 제출합니다. screenshot 업로드와 다르며, 제출 이후 실제 생성 완료·node 구조·DS 연결은 도구 응답과 결과로 확인해야 합니다.

submit timeout·HTTP·본문 오류는 실패로 집계합니다. 배치 중 하나라도 실패하면 나머지를 시도한 뒤 non-zero로 종료합니다. 독립된 생성 결과는 보존하고 실패분만 구분해 보고합니다.

## Test

형식 검사는 저장소 루트, Node 명령은 스킬 폴더에서 실행합니다. 기존 계약 테스트와 help smoke는 브라우저를 실행하거나 Figma에 제출하지 않습니다.

```bash
python3 scripts/validate_skills.py --skill code-to-figma
```

```bash
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci
npm test
npm run smoke
```
