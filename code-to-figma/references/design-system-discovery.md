# 디자인 시스템 발견 절차

스킬이 "알아서" 아는 게 아니라, **증거를 단계적으로 모아 디자인 시스템 후보를 확정**한다.
결과물은 실행 전에 만드는 매핑표(후보 + 확신도 + 근거)다.

## 발견 우선순위

```
1. 사용자 지정 라이브러리/기준 frame
2. Code Connect
3. 목적지 파일의 기존 instance
4. 연결된 라이브러리 목록
5. search_design_system
6. 실패 시 새 레이어 + 미연동 보고
```

### 1. 사용자가 지정한 DS

- "Exem DS 써서 옮겨줘"
- "이 Figma 라이브러리 기준으로"
- "이 기존 화면이 기준이야" — 기존 frame 하나를 기준 화면으로 받으면 제일 정확하다

### 2. 코드 쪽 단서

- React import: `Button`, `Input`, `Table`, `Tabs` 같은 컴포넌트명
- 디자인 토큰: CSS 변수, theme token, Tailwind config
- Code Connect 파일: `Button.figma.tsx`, `*.figma.ts` — 여기서
  "코드 컴포넌트 → Figma 컴포넌트 URL/key" 매핑을 얻을 수 있으면 가장 강한 증거다

### 3. 목적지 Figma 파일의 단서

- 이미 연결된 라이브러리 목록
- 기존 화면 안의 component instance들
- 로컬 변수, text style, effect style

### 4~5. Figma 라이브러리 검색

- `get_libraries`로 사용 가능한 라이브러리 확인
- `search_design_system`으로 `button`, `input`, `table`, `surface`, `text`, `radius`,
  `space` 같은 이름 검색
- 찾은 컴포넌트는 임시 instance로 만들어 properties까지 확인한다

## 매핑표

실행 전에 내부적으로 이런 표를 만들고, 확신도 높은 매핑만 사용한다.
애매한 컴포넌트는 새 레이어로 만들거나 사용자 확인을 요청한다.

```text
Source UI        Figma DS 후보        확신도
Button           Exem DS / Button     높음 - Code Connect 있음
Input            Exem DS / TextField  중간 - 이름/속성 매칭
Table            Exem DS / DataTable  높음 - 기존 화면 instance와 일치
SQL Plan Chart   없음                 낮음 - 새 editable layer 필요
Color/bg/base    var: surface/default 높음 - 기존 화면 bound variable
```

실행 전 요약에는 DS 추정 결과와 **근거**(예: 목적지 파일 연결 라이브러리 + 기존 화면
instance + 코드 컴포넌트명)를 함께 보여준다. 그래야 사용자가 "왜 이 컴포넌트를 썼는지"
납득할 수 있다.

## "연동"의 정의

- 컴포넌트는 **Figma component instance**로 만든다
- 색/간격/반경은 **variable binding**으로 묶는다
- 텍스트는 **text style**을 적용한다
- 그림자 등은 **effect style**을 적용한다
- 못 찾은 것은 새 레이어로 만들되, 마지막에 **미연동 목록**으로 보고한다

## 실패/제한 시 정책

- 지정한 라이브러리에 접근 불가: 선택지 두 개를 제시한다 —
  (1) 라이브러리 권한을 받은 뒤 다시 실행, (2) 목적지 파일의 로컬 스타일만 사용해 진행.
  디자인 시스템 일관성이 중요하면 1번을 권한다.
- 목적지 파일에서 아무 DS도 못 찾음: 편집 가능한 레이어는 만들 수 있지만 기존 컴포넌트
  instance/변수 연결은 제한된다고 **고지**한 뒤, 사용할 라이브러리나 기준 frame이 있는지
  묻는다. 조용히 대충 만들지 않는다.
- 배치 픽셀 캡처 모드는 raw frame이라 DS 연동 대상이 아니다 — 시작 전에 명확히 말한다.
