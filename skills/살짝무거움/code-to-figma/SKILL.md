---
name: code-to-figma
license: Apache-2.0
metadata:
  version: 0.1.0
description: (v0.1.0) 구현된 웹 화면(로컬 dev/preview URL)을 Figma 파일로 옮길 때 사용한다. "피그마로 옮겨줘", "Figma로 변환해줘", "피그마 디자인 생성해줘", "/code-to-figma" 등 화면을 Figma로 옮기자는 요청이 나오면 사용한다. 단일 화면은 디자인 시스템에 바인딩된 편집 가능한 레이어로, 여러 화면은 픽셀 캡처 후 그리드 정렬로 옮긴다.
---

# code-to-figma

구현된 화면을 Figma로 옮기는 실행 계약을 고정한 스킬이다. Figma 공식 플러그인
(`figma@claude-plugins-official`)의 `figma-generate-design` 스킬과 Figma MCP 위에서 동작한다.

핵심 순서: **작업 계약 확인 → 권한/접근 점검 → 디자인 시스템 탐색 → 실행 → 보고**.
사용자에게 보이는 응답 문구는 `references/response-templates.md`의 톤을 따른다.

## 1. 작업 계약 4칸 확인

`references/input-contract.md`를 읽고 아래 4칸을 채운다. **부족한 칸만** 질문한다.

1. **Figma 권한** — 사용자가 주는 값이 아니라 스킬이 먼저 점검하는 상태
2. **원본 화면** — 무엇을 옮길지 (URL 1개 이상, 또는 현재 작업 컨텍스트)
3. **Figma 목적지** — 어디에 넣을지 (Figma design URL, 선택적으로 node-id)
4. **디자인 시스템** — 어떤 기존 컴포넌트/변수/스타일에 바인딩할지

확인 순서는 `권한 → 원본 → 목적지 → DS`다. 권한이 막혀 있으면 나머지를 받아도 실행이 안 된다.
막힌 칸이 있으면 "작업 실패"처럼 말하지 말고 **어느 칸이 막혔는지**만 알려준다.
이미 받은 입력값은 버리지 말고 보존했다가 이어서 쓴다.

## 2. 권한/접근 점검

- `claude plugin list --json`에서 `figma@claude-plugins-official`이 installed + enabled인지 확인한다.
  - 미설치: `claude plugin install figma@claude-plugins-official --scope user`
  - 설치됐지만 비활성: `claude plugin enable figma@claude-plugins-official --scope <scope>`
- `claude mcp list`에서 `plugin:figma:figma` 연결 상태를 확인한다. 인증이 필요하면
  사용자에게 인증을 안내하고, 완료 후 같은 요청을 이어서 진행한다.
- 목적지 Figma URL을 파싱한다: `figma.com/design/<fileKey>/...` → `fileKey`,
  `?node-id=<a-b>` → `nodeId`(하이픈을 콜론으로 치환). design 링크가 아니면 다시 요청한다.
- 대상 파일에 가벼운 읽기 호출(예: `get_screenshot`)을 시도해 접근/편집 가능 여부를 확인한다.
  파일 권한이 없으면 해당 파일의 편집 권한을 받은 뒤 다시 요청하도록 안내한다.

## 3. 원본 화면 확정과 모드 판정

- 원본 우선순위: 사용자가 지정한 URL > 현재 작업 컨텍스트의 화면 > 질문.
  컨텍스트로 추론했으면 "옮길 화면이 명시되지 않아 현재 화면을 사용하겠습니다"라고 고지한다.
- 원본은 **브라우저로 접근 가능한 URL**이어야 한다. 로컬 전용 화면인데 dev 서버가 떠 있지
  않으면, 접근 가능한 URL을 요청하거나 서버 실행이 필요함을 안내한다.
- **모드 판정**: 원본이 1개면 편집 가능한 레이어 모드, 2개 이상이면 픽셀 캡처 배치 모드.
  배치 모드로 전환할 때는 그 이유(편집 가능한 재구성보다 안정적)를 고지한다.

## 4. 디자인 시스템 탐색

`references/design-system-discovery.md`의 우선순위대로 증거를 모아 매핑표(후보 + 확신도)를 만든다.
요약: 사용자 지정 > Code Connect > 목적지 파일의 기존 instance > 연결된 라이브러리 >
`search_design_system` > 실패 시 새 레이어 + 미연동 보고.

배치(픽셀 캡처) 모드는 DS 연동 대상이 아니다 — 미리 명확히 말한다.

## 5. 실행 전 요약

실행 직전에 원본 / 목적지 / 방식 / 디자인 시스템(+근거)을 한 번에 요약해 보여준다.
목적지가 없으면 진행하지 않는다 — 새 Figma 파일 자동 생성은 하지 않는다.

## 6. 실행

### 단일 화면 — 편집 가능한 레이어

1. 원본 화면을 열어 전체 높이와 섹션 경계(위→아래)를 파악한다. 측정이 어려우면 DOM 구조를
   위→아래로 직접 분할한다.
2. wrapper frame을 만든다: width = viewport 폭, layoutMode = VERTICAL,
   primaryAxisSizingMode = AUTO, itemSpacing = 0.
3. 섹션을 순서대로, 한 섹션당 `use_figma` 한 번으로 wrapper에 append한다.
   긴 페이지를 한 번에 만들지 않는다. **단일 스크린샷/단일 이미지 fill로 변환하지 않는다.**
4. 색/간격/타이포/반경은 하드코딩하지 말고 매핑표의 DS 컴포넌트 instance, variable,
   text/effect style에 바인딩한다. 매핑 실패분만 새 레이어로 만든다.
5. `generate_figma_design`의 픽셀 캡처는 섹션별 시각 대조용으로만 쓴다.
6. 각 섹션 추가 후 `get_screenshot`으로 텍스트 잘림·겹침·색을 검증한다.
7. (선택) Code Connect: DS instance를 사용한 경우에만 `get_code_connect_suggestions`를 1회
   프로브한다. 'Organization or Enterprise'/'Developer seat'/권한 거부가 나오면 미지원 계정 —
   한 줄 고지 후 즉시 건너뛴다(재시도 금지). 스킵/실패는 전체 실패로 취급하지 않는다.

배치 위치: `nodeId`가 있으면 그 위치(또는 근처), 없으면 대상 파일에 새 페이지를 만들어 배치한다.

### 여러 화면 — 픽셀 캡처 배치

캡처 드라이버는 `tsx`, `playwright`, chromium이 필요하다 — 없으면 실행 전에
`npx playwright install chromium`으로 설치를 먼저 시도한다.

1. 화면마다 `generate_figma_design(fileKey)`를 호출해 `captureId`를 1개씩 발급받는다.
2. `[{ "captureId", "url", "label"? }]` 배열을 JSON 파일(예: `/tmp/figma-batch-jobs.json`)로
   쓰고, 이 스킬 폴더의 캡처 드라이버를 실행한다:
   `npx tsx <이 스킬 폴더>/scripts/capture-url.ts --batch <jobs.json>`
   (기본 순차 캡처 — 캡처가 CPU-bound라 병렬은 보통 더 느리다.)
3. 각 `captureId`를 `generate_figma_design(fileKey, captureId)`로 status=completed까지 5초
   간격 폴링하고, 완성된 frame nodeId를 모은다.
4. `use_figma`로 정리한다: 새 Figma 페이지를 만들고, 캡처된 frame들을 3열 그리드로 배치
   (간격 일정, 각 frame 위에 label 표기). 캡처가 자동 생성한 빈 페이지는 제거한다.
5. 특정 화면 캡처가 실패해도 나머지는 계속 진행하고, 실패분은 마지막에 보고한다.

## 7. 결과 보고

- 생성 위치 (Figma 페이지/frame)
- 사용한 DS 컴포넌트, 바인딩한 변수/스타일
- 매칭 실패해 새 레이어로 만든 **미연동 목록**
- 실패/스킵한 화면과 사유
- 사용자가 확인해야 할 권한/품질 이슈
