---
name: trim
license: Apache-2.0
metadata:
  version: 0.1.0
description: 동작 유지하며 변경분의 코드량과 복잡도를 줄일 때 사용한다.
---

# trim

이미 끝난 diff를 대상으로 동작은 유지하면서 코드량, 중복, 불필요한 복잡도를 줄이는 스킬이다.
목표는 줄 수 자체가 아니라 같은 동작을 더 단순한 코드로 표현하는 것이다.

## 불변 규칙

- 동작을 바꾸지 않는다.
- 공개 API, 데이터 계약, UX 의도, 접근성 의미를 바꾸지 않는다.
- 테스트 의미를 약하게 만들지 않는다.
- 새 기능을 추가하지 않는다.
- 요구사항을 다시 해석하지 않는다.
- 줄 수가 줄어도 의미가 흐려지면 실패로 본다.

## 호출 형태

```text
/trim
/trim --go
/trim -go
```

- `/trim`: 현재 diff를 분석하고 줄일 수 있는 후보와 검증 계획만 제안한다. 승인 전에는 파일을 수정하지 않는다.
- `/trim --go`, `/trim -go`: 같은 분석을 수행하되 승인 질문 없이 안전한 단순화만 적용한다.

## 대상 범위

기본 대상은 현재 작업 diff다.

1. dirty worktree가 있으면 `HEAD` 대비 변경을 본다.
   - `git diff --stat`
   - `git diff --name-only`
   - `git diff`
   - `git ls-files --others --exclude-standard`
2. worktree가 깨끗하고 현재 브랜치가 base보다 앞서 있으면 브랜치 diff를 본다.
   - `git log --oneline <base>..HEAD`
   - `git diff --stat <base>...HEAD`
   - `git diff <base>...HEAD`
3. 범위가 애매하면 사용자에게 기준 diff를 묻는다.

전체 코드베이스를 무작정 줄이지 않는다. 현재 diff와 그 주변 코드만 다룬다.

## 분석 순서

1. 현재 repo와 diff 범위를 확인한다.
2. 변경 전 검증 명령을 찾는다.
   - package script, test script, lint, typecheck, build, 기존 CI 문서
   - 명확한 명령이 없으면 "검증 명령 없음"으로 기록한다.
3. `git diff --stat`으로 변경량 기준을 기록한다.
4. diff와 주변 코드를 읽고 단순화 후보를 분류한다.
5. 후보별로 "동작 보존 근거"와 "검증 방법"을 적는다.
6. `--go`가 아니면 계획을 제안하고 멈춘다.

diff가 크거나 여러 영역이 섞였으면 Gemini CLI가 있을 때 보조 분석을 맡길 수 있다.

```bash
git diff | gemini -p "이 diff에서 동작을 바꾸지 않고 줄일 수 있는 단순화 포인트를 찾아줘. 위험한 변경과 안전한 변경을 분리해서 설명해줘."
```

Gemini 결과는 참고용이다. 최종 판단과 수정은 직접 diff를 읽고 결정한다.

## 단순화 포인트

우선적으로 찾는다:

- 파생 state: props나 기존 state에서 계산 가능한 값을 state로 들고 있는 경우
- 불필요한 effect: 렌더 중 계산하면 되는 값을 `useEffect`로 동기화하는 경우
- 과한 memoization: 이득 없는 `useMemo`, `useCallback`, `memo`
- 중복 로직: 같은 조건, 매핑, 변환, setup이 반복되는 경우
- 불필요한 wrapper: props를 그대로 전달하는 component, hook, helper
- 과한 추상화: 한 번만 쓰이거나 호출부보다 복잡한 helper
- 장황한 조건문: guard clause, lookup table, 단순 boolean 식으로 표현 가능한 경우
- 의미 없는 방어 코드: 실제 입력 계약상 도달하지 않는 null/undefined 분기
- 중복 스타일: 반복되는 class, style 객체, 상수
- 테스트 장황함: assertion에 기여하지 않는 mock, setup, 중복 케이스
- 타입 과설계: 실제 사용보다 복잡한 generic, mapped type, conditional type

## 상태 단순화 기준

수정해도 된다:

- state가 항상 다른 값에서 계산된다.
- effect가 state를 단순 복사한다.
- 여러 boolean이 사실 하나의 status로 표현된다.
- 같은 서버 상태를 로컬 state에 중복 저장한다.

수정하면 안 된다:

- 사용자가 입력 중인 임시 값이다.
- optimistic update, animation, transition, debounce 같은 시간 의미가 있다.
- 외부 store나 URL, storage와 동기화하는 의도적 상태다.
- reference identity가 memoized child나 effect dependency에 의미 있게 쓰인다.

## 구조 단순화 기준

수정해도 된다:

- helper가 호출부 하나뿐이고 호출부보다 복잡하다.
- wrapper component가 의미 있는 semantic, accessibility, layout 책임 없이 그대로 감싼다.
- 파일 분리가 이해를 돕지 않고 이동 비용만 만든다.
- 반복 코드를 합쳐도 이름과 책임이 더 명확해진다.

수정하면 안 된다:

- public API이거나 외부에서 import될 가능성이 있다.
- design system, route boundary, lazy loading boundary처럼 구조 자체가 의미를 가진다.
- 테스트 fixture나 story가 문서 역할을 한다.
- 접근성, semantic tag, layout containment를 위한 wrapper다.

## 금지 변경

아래는 trim 대상이 아니다.

- UX 문구 변경
- 에러 처리 의미 축소
- 접근성 속성 제거
- 타입 안정성 약화
- 테스트 assertion 약화
- public interface 변경
- 데이터 shape 변경
- API 호출 순서나 timing 변경
- 성능 최적화라는 명목의 동작 변경
- "아마 필요 없을 것"이라는 추측만으로 삭제

## `/trim` 응답 형식

기본 호출에서는 아래를 제안하고 멈춘다.

```text
trim 계획
1. <후보>
   - 파일: ...
   - 단순화: ...
   - 동작 보존 근거: ...
   - 위험도: 낮음/보통/높음

검증
- 사전 실행: ...
- 사후 실행: ...
- diff stat 비교: ...

이대로 trim할까요?
```

위험도가 높은 후보는 기본 계획에서 제외하거나 별도 선택지로 둔다.

## `--go` 실행 규칙

`--go` 또는 `-go`가 있으면 다음 순서로 진행한다.

1. baseline을 기록한다.
   - `git diff --stat`
   - 가능한 검증 명령 결과
2. 낮은 위험도의 단순화만 적용한다.
3. 같은 검증 명령을 다시 실행한다.
4. `git diff --stat` 전후를 비교한다.
5. 실패하면 원인을 파악해 고치거나, 방금 적용한 trim 변경만 안전하게 되돌린다. 기존 사용자 변경은 임의로 revert하지 않는다.
6. 최종 보고에는 줄어든 파일, 단순화 종류, 실행한 검증, 남긴 리스크를 포함한다.

## 중단 조건

아래 상황에서는 `--go`여도 수정하지 않는다.

- baseline 빌드나 테스트가 실패했고 실패 원인을 파악할 수 없음
- diff 범위를 판단할 수 없음
- secret, credential, 개인 정보가 diff에 포함된 정황
- 생성물, lockfile, 대형 바이너리만 바뀌어 코드 단순화 대상이 아님
- 동작 보존을 확인할 방법이 없고 변경 위험이 보통 이상임
- 사용자가 만든 기존 변경과 trim 대상이 얽혀 있어 안전하게 분리할 수 없음

중단할 때는 이유와 다음 행동을 짧게 제시한다.
