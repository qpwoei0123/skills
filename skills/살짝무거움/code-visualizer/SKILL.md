---
name: code-visualizer
license: Apache-2.0
metadata:
  version: 1.0.0
description: (v1.0.0) 대화·코드·diff의 구조, 호출, 데이터, 상태, 전후 변화를 근거가 연결된 단일 HTML 설명서로 만든다. "방금 설명을 HTML로 보여줘", "이 코드 흐름을 한눈에 보여줘", "diff 전후를 시각화해줘", "$code-visualizer" 요청에 사용한다. 제품 UI 구현, 결함 리뷰, 재설계 제안, Figma·슬라이드·이미지 제작은 각 전용 스킬이 맡는다.
---

# code-visualizer

사용자가 알고 싶은 관계를 먼저 고르고, 확인한 근거를 따라 읽을 수 있는 HTML로 설명한다. 문법과 템플릿은 질문에 맞춰 선택한다.

## 결과의 기준

- 결과는 CSS·JavaScript·SVG를 inline한 HTML 한 파일이다. 오프라인에서 열리고 JavaScript 없이도 결론·주 흐름·핵심 근거를 읽을 수 있어야 한다.
- 조사 대상 소스와 설정은 수정하지 않는다. 설명을 위해 package를 설치하거나 source project에 build server를 추가하지 않는다.
- 직접 확인, 추론, 미확정을 구분한다. 중요한 관계는 상대 경로와 symbol·line·diff hunk 또는 제공된 대화 근거로 추적할 수 있어야 한다.
- 정적 호출 가능성, 테스트의 기대, 실행에서 관찰한 사실은 서로 다르다. 충돌하는 근거는 충돌로 표시한다.
- 대화나 설계 설명만 받았으면 `제공된 설명 · 코드 미검증`으로 표시한다. 없는 소스를 요구하며 설명 자체를 멈추지 않는다.

## 질문과 근거

대상이 현재 맥락에서 하나면 바로 진행한다. 후보가 여럿이고 선택에 따라 설명이 달라질 때만 대상에 관해 묻는다.

현재 diff는 기본적으로 `HEAD → working tree`의 staged·unstaged 변경을 함께 보고, untracked 포함 여부를 밝힌다. branch 전체 변화는 저장소 기준 branch와의 merge-base → HEAD를 쓴다. 원격 PR/MR은 base/head와 diff version을 고정한다.

질문에 답하는 entrypoint와 핵심 계약부터 읽고, 관계가 끊기거나 분기·오류·side effect가 답을 바꾸는 곳으로 조사 범위를 넓힌다. 읽을 파일 개수나 전체 저장소 조사량을 미리 강제하지 않는다. 각 핵심 주장에 근거와 `확인됨·추론·미확정` 상태를 연결하고, 조사 revision과 제외 범위를 남긴다.

민감 파일을 설명용으로 수집하지 않는다. 근거에 포함된 secret·credential·개인정보는 값 대신 필요한 구조만 표시한다.

## 시각화와 HTML

질문에 맞는 문법은 [선택표](references/visual-grammar.md)와 해당 문법 부분을 참고한다.

- 소유권·경계는 architecture map, 시간 순서는 sequence
- 조건·실패 경로는 decision flow, lifecycle은 state
- 데이터 shape 변화는 pipeline, 구조는 tree·dependency
- 변경의 의미는 before/after, 작은 범위는 annotated excerpt·table

주 시각화가 질문의 답을 전달하게 한다. 노드가 많아 읽기 어려우면 의미 단위로 묶거나 보조 표를 쓴다. 정확성에 필요한 관계를 숫자 제한에 맞춰 지우지 않는다.

[산출물 계약](references/artifact-contract.md)의 오프라인·escaping·접근성 기준을 적용한다. [shell](assets/explainer-shell.html)과 `assets/patterns/`는 빠른 출발점이며, 적합한 것만 쓴다. shell의 고정 script를 사용하면 CSP hash도 함께 유지한다. 불필요한 제어와 빈 panel은 제거한다.

첫 화면에 제목, 결론, 조사 범위와 주 시각화를 둔다. 근거와 excerpt는 필요한 만큼 이어 붙이고 중요한 위험·미확정을 hover나 접힌 영역에만 숨기지 않는다. `E#`, `I# · 추론`, `? · 미확정`은 근거 상태를, `+ 추가`, `− 제거`, `Δ 수정`은 변경 상태를 구분해 표시한다.

사용자가 지정한 경로가 없으면 이미 존재하고 gitignored인 `.context` 아래 `code-visualizer/<slug>.html`에 저장한다. 그런 workspace가 아니면 `/tmp/codex-code-visualizer/<repo-or-topic>/<slug>.html`을 쓴다. 이번에 만든 산출물의 후속 수정은 같은 파일에 반영하고, 무관한 기존 파일은 suffix로 보존한다.

## 확인과 전달

placeholder·중복 ID·깨진 참조, HTML escaping, 외부 asset·network 요청, 핵심 주장과 근거 연결을 정적으로 확인한다. 사용한 script가 있으면 CSP와의 일치도 확인한다.

브라우저 검증이 가능하면 desktop·mobile에서 잘림·겹침과 keyboard 동작을 확인한다. 사용자 환경을 직접 조작하는 도구는 해당 환경의 사전 동의 규칙을 따른다. 브라우저를 사용할 수 없어도 구조 검증을 끝낸 HTML은 전달하고, 실제로 못 한 시각 확인만 명시한다.

최종 답변은 HTML 링크, 설명 관점과 범위, 중요한 미확정이나 검증 한계만 짧게 쓴다. 긴 설명은 HTML 안에 둔다.
