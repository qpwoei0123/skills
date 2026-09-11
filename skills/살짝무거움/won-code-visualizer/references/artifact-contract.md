# HTML 산출물 계약

## 읽는 순서와 근거

제목과 결론 다음에 조사 범위·revision과 주 시각화를 둔다. 첫 화면에서 관계의 전체 형태와 중요한 미확정을 볼 수 있게 하고, 파일 통계나 장식이 앞서지 않게 한다. `1440×900`과 `390×844`는 desktop·mobile 확인에 쓸 수 있는 대표 크기다. 특정 pixel 좌표에 맞추기보다 실제 가독성을 확인한다.

인식 상태와 변경 상태를 다른 표식으로 표현한다.

| 상태 | 표현 | 연결할 근거 |
|---|---|---|
| 직접 확인 | 실선 + `E#` | 상대 경로·symbol·line·hunk와 짧은 근거 |
| 추론 | 파선 + `I# · 추론` | 출발 근거와 아직 직접 확인하지 못한 관계 |
| 미확정 | 점선 + `? · 미확정` | 무엇을 보면 확정할 수 있는지 |
| 근거 충돌 | callout | 서로 충돌하는 양쪽 근거 |

대화만 근거라면 그 출처와 코드 미검증 상태를 표시한다. production code, test expectation, config selection, runtime observation도 구분한다. 변경은 `+ 추가`, `− 제거`, `Δ 수정`으로 별도 표시한다. 색만으로 의미를 전달하거나 퍼센트 확신도를 붙이지 않는다.

## 오프라인과 안전한 내용 삽입

- UTF-8, semantic HTML, viewport meta와 제한적인 CSP를 사용한다.
- CSS·JavaScript·SVG·icon은 inline한다. 전체 source 대신 설명에 필요한 excerpt만 담는다.
- 외부 asset, CDN, remote font, `@import`, `fetch`, XHR, WebSocket, iframe, service worker, form을 사용하지 않는다.
- `eval`, `new Function`, `document.write`를 사용하지 않는다.
- 저장소 문자열과 excerpt는 표준 HTML escaper로 처리한다. 사용자·repo 문자열을 inline style·script나 `innerHTML`에 삽입하지 않는다.
- 근거에는 저장소 상대 경로를 쓴다. home 경로, token, signed URL, secret·개인정보를 포함하지 않는다.
- JavaScript가 꺼져도 결론·주 흐름·핵심 근거는 읽을 수 있어야 한다.

## shell과 CSP

제공된 shell의 고정 script와 CSP hash는 한 쌍이다. 그대로 쓰면 아래 hash를 유지한다. 다른 HTML에서 script를 제거하면 `script-src 'none'`을 사용할 수 있다. script를 실제로 변경했다면 정확한 inline script bytes로 SHA-256 hash를 다시 계산하고 CSP와 일치하는지 확인한다. 기능이 필요 없으면 정적 HTML·`<details>`·SVG로 끝내는 편이 단순하다.

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'sha256-8BBuom7rIiJyAIbPv+cLPZRnYHPDi2sQ76UZcPeh8RM='; connect-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'">
```

pattern을 복사했다면 `*_CLASS`, `*_LABEL`, `{{PLACEHOLDER}}`와 삽입 comment를 실제 근거에 맞게 교체한다. 필요 없는 panel과 control은 제거한다. node 선택과 route 강조의 attribute는 [시각 문법](visual-grammar.md)의 markup recipe를 참고한다.

## 상호작용·반응형·print

상호작용은 긴 근거를 탐색하거나 경로를 비교하는 데 도움이 될 때 넣는다. keyboard로 조작할 수 있고 선택 상태가 text와 outline으로 보여야 한다. tooltip이나 접힌 영역에 유일한 근거·핵심 위험을 숨기지 않는다. motion을 썼다면 `prefers-reduced-motion`을 따른다.

가로 flow는 mobile에서 작은 글씨로 축소하기보다 세로로 재배치한다. 긴 path는 줄바꿈하고 code에는 가로 scroll을 허용한다. print에서는 불필요한 control을 숨기고 근거 panel을 펼친다.

## 확인할 것

placeholder·중복 ID·깨진 참조, escaping, network dependency와 CSP를 정적으로 확인한다. 중요한 node·edge가 근거와 연결되는지도 다시 본다. 허용된 브라우저 검증 수단이 있으면 keyboard, console, desktop·mobile의 겹침과 잘림을 확인한다. 수행하지 못한 검증은 실제 확인한 범위와 구분해 짧게 전달한다.
