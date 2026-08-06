# 시각 문법 라우터

사용자가 답을 원하는 질문을 최우선으로 두고 주 시각화 하나를 고른다. 질문이 없으면 가장 많은 변경 hunk를 관통하는 인과 경로를 기준으로 삼는다.

## 선택표

| 입력 신호 | 주 문법 | 하드 예산 | 주의 |
|---|---|---:|---|
| 이전·이후 구현과 추가·삭제가 핵심 | aligned before/after | 핵심 변경 5개, excerpt 각 10줄 | 관계 변화가 더 중요하면 architecture map 사용 |
| 호출·event의 시간 순서와 행위자 | sequence | lane 5, message 9 | 실제 순서를 확정할 수 없으면 병렬·미확정 표시 |
| `if`, `switch`, guard, flag, error path | decision flow | node 8, 깊이 4, node당 branch 3 | 상태 전이가 핵심이면 state 사용 |
| enum, lifecycle, transition 함수 | state diagram | state 8, transition 12 | 단순 직선 단계면 pipeline 사용 |
| import, 호출, 소유권, service 간 이동 | layered architecture/data flow | node 9, edge 12 | 방향 근거가 없으면 연결하지 않음 |
| parser→normalizer→writer처럼 shape 변화 | pipeline + shape card | stage 6, card당 field 6 | 양이 없으면 Sankey 금지 |
| 디렉터리·component·route·소유 구조 | tree | 깊이 4, 형제 6 | cycle이 중요하면 grouped dependency 사용 |
| 3개 이상 구현의 contract 비교 | matrix table | 열 6, 행 12 | 인과 설명이 필요하면 flow를 주로 사용 |
| UI 배치가 동작 이해의 핵심 | low-fi wireframe | region 8 | 코드 구조를 화면처럼 꾸미기만 하지 않음 |
| 실제 측정 수치 비교 | sorted bar 또는 table | category 8, series 3 | 추정치를 측정값처럼 표시하지 않음 |
| entity 2개 이하·변경 30줄 이하 | annotated excerpt | excerpt 3개, 각 10줄 | 다이어그램을 억지로 만들지 않음 |
| 근거가 약하거나 충돌 | conclusion + evidence ledger | claim 7 | 허구의 단일 흐름을 만들지 않음 |

두 문법이 동률이면 관계 시각화 하나와 정확성을 보완하는 표 하나만 쓴다. 노드 예산을 넘으면 subsystem으로 묶고, 묶어서 의미가 사라지면 표로 전환한다.

## 문법별 핵심 질문

### Layered architecture

- 누가 진입하고 어느 경계를 지나 어떤 side effect에 도달하는가?
- lane은 client·application·domain·data·external처럼 책임으로 나눈다.
- import와 runtime call을 같은 edge로 섞지 않는다.

### Sequence

- 행위자와 시간 순서가 무엇인가?
- async 병렬 구간은 별도 band로 두고 `순서 미보장`을 표시한다.
- return value보다 control handoff가 중요한 경우에만 응답 화살표를 넣는다.

### Decision flow

- 어떤 조건이 경로를 갈라놓는가?
- edge label은 `있음/없음`보다 실제 predicate를 짧게 쓴다.
- 성공 경로와 가장 중요한 실패 경로를 함께 첫 화면에 둔다.

### State diagram

- 상태를 누가 어떤 event와 guard로 바꾸는가?
- state와 화면·component를 혼동하지 않는다.
- 불가능하거나 코드 밖에서 결정되는 전이는 `미확정`으로 둔다.

### Pipeline

- 각 단계에서 데이터 shape·ownership·저장 위치가 어떻게 변하는가?
- stage마다 input/output field 차이만 보여주고 전체 schema를 복사하지 않는다.
- retry·buffer·batch가 semantics를 바꾸면 별도 표시한다.

### Before/after

- 같은 책임이 어디로 이동했고 contract가 무엇을 유지·변경했는가?
- 좌우에서 같은 대상을 같은 색·세로 위치로 맞춘다.
- rename-only는 추가·삭제가 아니라 path mapping으로 표현한다.

### Dependency tree/network

- hierarchy가 있으면 tree를 쓰고 cycle 자체가 핵심일 때만 network를 쓴다.
- cycle·recursion은 노드를 복제하지 말고 loop 하나로 접는다.
- generated·vendor·minified 파일은 주 도식에서 제외하고 범위에 적는다.

## 전역 예산

- 주 시각화 1개, 보조 시각화 최대 2개
- 최상위 section 최대 6개
- 동시에 보이는 code excerpt 최대 3개, 각 10줄
- 의미 색상 최대 4개와 neutral
- label 최대 40자, 본문 최소 16px, metadata 최소 12px
- disclosure 중첩 깊이 1, 상호작용 종류 최대 2개
- drag·pan·zoom·carousel·자동 재생 금지

## 빠른 markup recipe

shell의 고정 script는 아래 attribute만 읽는다.

- node의 `data-detail="x"` ↔ inspector의 `data-detail-panel="x"`
- route 버튼의 `data-route-filter="main"` ↔ 강조할 요소의 `data-route="main failure"`
- 선택 가능한 node는 `<div>`가 아니라 `<button type="button" class="node">`로 만든다.
- detail이나 route가 필요 없으면 해당 control을 제거하고 정적 본문으로 끝낸다.

### 인과 flow

```html
<div class="flow-row" style="--columns: 5">
  <button type="button" class="node entry" data-detail="entry" data-route="main">
    <span class="node-title">HTTP handler</span>
    <span class="node-meta"><span class="badge fact">E1</span></span>
  </button>
  <div class="connector fact" data-route="main"><span>E2 · 호출</span></div>
  <button type="button" class="node domain" data-detail="service" data-route="main failure">
    <span class="node-title">Application service</span>
    <span class="node-meta"><span class="badge fact">E2</span></span>
  </button>
  <div class="connector unknown" data-route="failure"><span>? · runtime 확인 필요</span></div>
  <button type="button" class="node unknown" data-detail="sink" data-route="failure">
    <span class="node-title">External sink</span>
    <span class="node-meta"><span class="badge unknown">?</span></span>
  </button>
</div>
<section data-detail-panel="entry"><h2>E1 · 진입점</h2><p>근거와 최소 excerpt</p></section>
```

### Sequence

lane을 억지로 선으로 잇지 말고 시간 순서가 읽히는 표를 기본으로 쓴다. 병렬 실행은 같은 step과 `순서 미보장` label로 표시한다.

```html
<table aria-label="요청 처리 순서">
  <thead><tr><th>순서</th><th>행위자</th><th>handoff</th><th>근거</th></tr></thead>
  <tbody>
    <tr data-route="main"><td>1</td><td>Router</td><td>요청 검증</td><td><span class="badge fact">E1</span></td></tr>
    <tr data-route="main"><td>2a · 병렬</td><td>Worker</td><td>두 task 시작 · 순서 미보장</td><td><span class="badge inference">I1</span></td></tr>
  </tbody>
</table>
```

### Before/after

```html
<div class="compare-grid">
  <article class="compare-column"><p class="group-title">Before</p><!-- 이전 책임·근거 --></article>
  <article class="compare-column"><p class="group-title">After</p><!-- 같은 책임의 새 위치·근거 --></article>
</div>
```

recipe로 관계가 표현되지 않으면 고정 script를 늘리지 말고 작은 inline SVG 또는 table을 쓴다. SVG의 node·edge에도 보이는 `E#`, `I#`, `?` text를 넣고 접근 가능한 제목을 제공한다.

## 경계 사례

- reflection·DI·dynamic import: 가능한 target을 파선 `추론`으로 표시한다.
- feature flag·environment branch: 활성 환경을 모르면 모든 조건부 경로를 남긴다.
- comment와 구현, test와 production이 충돌: 충돌 자체를 callout으로 보여준다.
- line이 움직이는 diff: `path + symbol + hunk`를 line number보다 우선한다.
- 단일 인과 경로를 입증할 수 없음: `확정된 경로 없음`을 결론으로 두고 evidence ledger를 쓴다.
