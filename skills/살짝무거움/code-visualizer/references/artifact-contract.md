# HTML 산출물 계약

## 첫 화면

`1440×900`의 첫 viewport 안에 다음을 순서대로 둔다.

1. 한 줄 제목
2. `무엇이 어떻게 동작하고 왜 중요한가`를 말하는 두 줄 이하 결론
3. 조사 범위·revision·검증 상태·가장 큰 미확정 최대 4개 chip
4. 전체 형태가 보이는 주 시각화
5. 범례와 핵심 근거 1~3개

제목·meta는 화면 높이의 20% 이하로 두고 주 시각화는 문서 위쪽 280px 안에서 시작한다. TOC, 파일 통계, 장식용 hero가 결론보다 먼저 나오지 않게 한다. 가장 중요한 실패 경로나 미확정 하나를 첫 화면에서 숨기지 않는다.

## 시각 표식

인식 상태와 변경 상태를 서로 다른 channel로 표현한다.

| 상태 | 표현 | 필수 내용 |
|---|---|---|
| 직접 확인 | 실선 + `E#` | `path:symbol` 또는 line·hunk, 짧은 근거 |
| 추론 | 파선 + `I# · 추론` | 연결된 `E#`와 추론 이유 |
| 미확정 | 점선 + `? · 미확정` | 무엇을 보면 확정되는지 |
| 근거 충돌 | warning callout | 양쪽 근거를 함께 표시 |

변경 상태는 `+ 추가`, `− 제거`, `Δ 수정` text badge로 별도 표시한다. 색만으로 의미를 구분하지 않고, 빨강·초록을 변경과 위험 의미에 동시에 쓰지 않는다. 퍼센트 확신도는 쓰지 않는다.

production code, test expectation, config selection, runtime observation의 근거 종류도 label로 구분한다.

## HTML 안전성

- UTF-8, semantic HTML, `<meta name="viewport">`와 제한적인 CSP를 둔다.
- CSS·JavaScript·SVG와 필요한 icon은 모두 inline한다.
- HTML은 750KB 이하를 목표로 하고 2MB를 넘기지 않는다. 전체 source 대신 필요한 excerpt만 담는다.
- CDN, remote font·stylesheet·script·image, `@import`, `fetch`, XHR, WebSocket, iframe, service worker, form을 넣지 않는다.
- `eval`, `new Function`, `document.write`를 쓰지 않는다.
- repo 문자열과 excerpt는 표준 HTML escaper를 우선 쓴다. 직접 처리할 때는 `&`, `<`, `>`, `"`, `'` 순서로 각각 `&amp;`, `&lt;`, `&gt;`, `&quot;`, `&#39;`로 바꾸고 사용자·repo 값을 inline style·script나 `innerHTML`로 주입하지 않는다.
- HTML에는 저장소 상대 경로만 넣고 home directory, token, signed URL, secret 값을 넣지 않는다.
- JavaScript가 꺼져도 핵심 내용이 보이게 하고, hover 전용 정보를 만들지 않는다.

shell의 고정 script와 CSP hash는 한 쌍이다. script를 수정하지 말고 제공된 node 선택·route 강조만 사용한다. 다른 동작이 필요하면 JavaScript를 늘리기보다 정적 HTML, `<details>`, inline SVG로 단순화한다.

권장 CSP:

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'sha256-8BBuom7rIiJyAIbPv+cLPZRnYHPDi2sQ76UZcPeh8RM='; connect-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'">
```

## 상호작용

기본 상호작용은 두 개까지만 쓴다.

1. node 선택 → 연결된 근거와 excerpt 강조
2. route 선택 또는 `<details>` → 부수 경로·긴 근거 펼치기

선택 상태를 text와 outline으로 표시하고 keyboard focus를 제공한다. `Escape` 또는 `전체` 버튼으로 초기화한다. tooltip과 접힌 영역에 새 주장, 위험, 유일한 출처를 숨기지 않는다. animation은 200ms 이하로 하고 `prefers-reduced-motion`에서 제거한다.

## 반응형·print

- desktop의 가로 flow는 mobile에서 작은 글씨로 축소하지 말고 세로 card flow로 바꾼다.
- content 폭은 제한하되 diagram은 필요한 공간을 갖게 한다.
- 긴 symbol·path는 줄바꿈하고 code는 가로 scroll을 허용한다.
- print에서는 control을 숨기고 모든 detail panel을 표시한다.

## QA checklist

- [ ] 남은 `{{PLACEHOLDER}}`와 삽입 comment가 없음
- [ ] 중요 node·edge가 `E#`, `I#`, `?`에 연결됨
- [ ] source는 상대 경로·symbol 또는 line·hunk로 표시됨
- [ ] secret·개인정보·절대 경로가 없음
- [ ] network dependency와 외부 asset이 없음
- [ ] JavaScript 없이도 결론·주 흐름·위험을 읽을 수 있음
- [ ] node와 route control을 keyboard로 조작할 수 있음
- [ ] desktop·mobile에서 overlap, clipping, 지나친 축소가 없음
- [ ] console error가 없음
- [ ] 조사 범위와 제외 범위가 보임
