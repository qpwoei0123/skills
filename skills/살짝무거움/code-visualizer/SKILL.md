---
name: code-visualizer
license: Apache-2.0
metadata:
  version: 0.1.0
description: (v0.1.0) 현재 대화의 설명, 붙여 넣은 코드, 코드베이스와 diff를 근거로 아키텍처·호출 순서·데이터 흐름·상태 전이·의존성·전후 변화를 가장 알맞은 시각 문법으로 골라, 브라우저에서 바로 여는 단일 self-contained HTML 설명서로 만드는 스킬. "방금 설명을 HTML로 보여줘", "글로 안 와닿으니 시각화해줘", "이 코드 흐름을 한눈에 보여줘", "diff 전후를 그림으로 보여줘", "$code-visualizer"처럼 코드 이해를 시각 산출물로 요청할 때 사용한다. 텍스트 설명만, 제품 UI 구현, 코드 결함 리뷰, 재설계 제안, Figma·슬라이드·이미지 제작에는 사용하지 않는다.
---

# code-visualizer

현재 대화와 코드에서 확인한 관계를 사람이 30초 안에 방향을 잡을 수 있는 HTML 지도로 바꾼다. 장식보다 인과관계, 노드 수보다 질문에 대한 답, 그럴듯함보다 근거 추적 가능성을 우선한다.

## 계약

- 소스와 설정은 읽기 전용으로 조사하고 애플리케이션 코드는 수정하지 않는다. 이 스킬이 쓰는 파일은 설명용 HTML뿐이다.
- 결과물은 CSS·JavaScript·SVG를 inline한 `.html` 한 파일로 만든다. CDN, 외부 font·script·stylesheet·image, network 요청, package 설치, build server를 사용하지 않는다.
- 관찰한 사실, 근거에서 도출한 추론, 확인하지 못한 runtime 동작을 시각적으로 구분한다. 정적 호출 가능성을 실제 호출 사실로 표현하지 않는다.
- 중요한 노드와 화살표마다 저장소 상대 경로와 symbol 또는 line·diff hunk 근거를 연결한다. 절대 경로와 secret·credential·개인정보 값은 넣지 않는다.
- source를 받지 못한 설명은 `대화에서 제공됨 · 미검증`으로 표시하고 코드에서 확인한 사실처럼 표현하지 않는다.
- JavaScript가 없어도 결론·주 흐름·핵심 위험과 근거를 읽을 수 있게 만든다. 상호작용은 밀도를 줄이는 보조 수단으로만 쓴다.
- 설명 대상이 현재 맥락에서 하나로 좁혀지면 바로 진행한다. 후보가 여럿이라 결과가 달라질 때만 한 번 짧게 묻는다.

## 경계

```text
code-visualizer  이미 있는 코드·diff·설계를 이해시키는 단일 HTML 설명서
code-review      코드의 버그·회귀 finding
context-review   PR/MR에서 사람이 답해야 할 고맥락 질문
wow              구조를 다시 정의하는 재설계 제안
impeccable       실제 제품 UI의 설계·구현·개선
```

Mermaid 원문, Figma, 이미지, PDF, slide, 배포 사이트가 최종 산출물이면 해당 전용 도구를 쓴다. 이 스킬은 hosting이나 공유 URL 생성을 맡지 않는다.

## 1. 질문과 범위 고정

1. 사용자가 알고 싶은 한 문장을 먼저 적는다. 예: `요청이 어디서 검증되고 DB에 쓰이는가?`
2. 현재 대화, 붙여 넣은 코드, 사용자가 지정한 파일·symbol·diff 순으로 입력을 확인한다. 저장소가 있으면 지침, revision과 dirty 상태도 확인한다.
3. 지정 대상이 없으면 현재 대화와 diff에서 단일 후보를 찾는다. 후보가 여러 개면 시각화 종류를 묻지 말고 설명할 대상만 묻는다.
4. 원격 PR/MR이면 base/head 또는 diff version을 고정한다. 생성 HTML에 조사 revision과 범위를 표시한다.

로컬에서 `현재 diff`라고만 하면 `HEAD → working tree`를 기본으로 하여 staged·unstaged를 함께 보고, untracked 포함 여부를 범위에 적는다. branch 전체 변화가 질문이면 merge-base(`origin/main` 또는 저장소 기본 branch) → `HEAD`를 쓴다.

전체 저장소를 읽었다고 가장하지 않는다. 큰 저장소는 대표 entrypoint, 프로세스 경계, 핵심 모듈과 한 개의 end-to-end 흐름을 우선하고 제외 범위를 밝힌다.

## 2. 근거 지도 만들기

source가 있으면 처음에는 핵심 파일 3~8개만 읽고, 관계가 끊긴 지점에서만 다음 hop으로 확장한다. 대화나 설계 설명만 있으면 그 입력을 evidence로 쓰고 source 검증이 없었음을 범위에 표시한다.

1. entrypoint와 직접 호출자·소비자를 찾는다.
2. 핵심 함수·타입·상태와 public contract를 읽는다.
3. API, DB, queue, filesystem, cache, 외부 service 같은 side-effect 경계를 찾는다.
4. 분기·flag·async·retry·error·fallback이 질문의 답을 바꾸면 포함한다.
5. test는 production 동작의 직접 증거가 아니라 기대 계약과 경계 사례를 보충할 때만 쓴다.

HTML을 쓰기 전에 아래 ledger를 내부적으로 만든다.

```text
ID | 주장/관계 | 확인됨·추론·미확정 | 근거 path:symbol/line | 사용자에게 중요한 이유
```

근거가 충돌하면 하나를 고르지 말고 충돌 자체를 보여준다. `.env`, private key, token, credential 파일은 열지 않으며 excerpt에 민감 값이 있으면 값만 마스킹한다.

## 3. 시각 문법 선택

[references/visual-grammar.md](references/visual-grammar.md)를 전부 읽고 질문에 가장 직접 답하는 주 시각화 하나를 고른다.

- 관계·소유권: 계층형 architecture map
- 시간 순서·행위자: sequence
- guard·분기·실패 경로: decision flow
- lifecycle: state diagram
- 데이터 shape 변화: pipeline
- 모듈·디렉터리 구조: tree 또는 grouped dependency
- 변경 의도: aligned before/after
- 작은 범위: annotated code excerpt 또는 comparison table

두 문법이 필요하면 관계를 보여주는 주 시각화 하나와 정확성을 보완하는 표·보조 도식 하나만 쓴다. 예산을 넘으면 글씨를 줄이지 말고 subsystem으로 묶고, 그래도 흐리면 표로 바꾼다.

## 4. HTML 만들기

[references/artifact-contract.md](references/artifact-contract.md)를 전부 읽고 [assets/explainer-shell.html](assets/explainer-shell.html)을 복사해 시작한다. 선택한 문법이 architecture·sequence·decision-flow·state·pipeline·before-after 중 하나면 같은 이름의 `assets/patterns/*.html` fragment를 주 시각화 자리에 복사한다. tree·matrix·annotated excerpt는 shell의 group·table·code primitive로 충분하므로 새 JavaScript를 만들지 않는다.

pattern의 `*_CLASS`는 ledger에 맞춰 `fact`, `inference`, `unknown` 중 하나로, `*_LABEL`은 대응하는 `E#`, `I# · 추론`, `? · 미확정`으로 반드시 교체한다. pattern의 모양이 인식 상태를 결정하게 두지 않는다.

사용자가 경로를 지정하지 않았으면 `.context/`가 이미 있고 git에서 무시되는 workspace에만 `<workspace>/.context/code-visualizer/<slug>.html`을 쓴다. 그 외에는 `/tmp/codex-code-visualizer/<repo-or-topic>/<slug>.html`을 쓴다. 기존 파일을 암묵적으로 덮지 말고 숫자 suffix를 붙인다.

다음 정보 순서를 지킨다.

1. 한 줄 제목과 두 줄 이하의 결론
2. 조사 범위·revision·검증 상태·가장 큰 미확정 최대 4개 chip
3. 첫 viewport에서 형태가 보이는 주 시각화
4. 선택한 노드의 근거와 최소 code excerpt
5. 읽는 순서, 예외·위험, 미확정, 조사한 source

template의 모든 `{{PLACEHOLDER}}`와 대문자 삽입 comment를 실제 내용으로 교체한다. 고정 script는 수정하지 않아 CSP hash를 유지한다. 저장소 문자열과 code excerpt는 HTML escape하고, 사용자 입력을 `innerHTML`, `eval`, `new Function`, `document.write`로 처리하지 않는다.

## 5. 검증

1. 남은 placeholder, duplicate `id`, 닫히지 않은 주요 tag를 확인한다.
2. remote asset, `@import`, `fetch`, XHR, WebSocket, iframe, form, service worker가 없는지 확인한다.
3. 브라우저에서 로컬 HTML을 열어 console error와 node 선택·경로 강조·keyboard focus를 확인한다.
4. `1440×900`에서 결론과 주 시각화가 첫 화면에 보이고 겹치거나 잘리지 않는지 확인한다.
5. 다열 layout이면 `390×844`에서도 작은 글씨로 축소되지 않고 세로 흐름으로 바뀌는지 확인한다.
6. 마지막으로 모든 핵심 주장과 화살표가 `E#`, `I#`, `?` 중 하나로 추적되는지 확인한다.

검증 때문에 dependency를 설치하거나 source project 설정을 바꾸지 않는다. 브라우저를 사용할 수 없으면 구조·offline 검증까지만 하고 `시각 QA 미수행`을 보고한다. 깨진 HTML은 완료물로 전달하지 않는다.

## 보고

긴 설명을 다시 쓰지 않고 HTML이 설명의 본문이 되게 한다.

```text
시각화 완료
- HTML: <절대 경로 링크>
- 관점: <architecture | sequence | flow | state | pipeline | tree | before/after | evidence>
- 범위: <revision과 핵심 source>
- 미확정: <없음 | 가장 중요한 한 가지>
```

사용자가 `보여줘`라고 했고 브라우저 도구를 쓸 수 있으면 완성 파일을 직접 연 뒤 링크를 준다.

## 하지 않는다

- 모든 입력을 같은 flowchart나 카드 dashboard로 바꾸기
- 작은 글씨·zoom·drag로 spaghetti graph를 한 화면에 욱여넣기
- 원시 diff나 파일 목록을 붙이고 시각화라고 부르기
- 수치 없는 Sankey·pie·장식용 KPI, 의미 없는 gradient와 animation 사용
- 위험·미확정을 접힌 영역이나 hover 안에 숨기기
- test assertion, comment, 이름 유사성을 production runtime의 사실로 단정하기
- 추론과 삭제, 위험과 변경 상태에 같은 시각 표식을 재사용하기
