---
name: trim
license: Apache-2.0
metadata:
  version: 0.4.1
description: (v0.4.1) 동작을 유지하면서 현재 diff의 군더더기를 덜어내고, 흩어진 중복·패턴을 같은 이유로 변하는 단위로 엮는 스킬. "코드 줄여줘", "단순하게 해줘", "중복 합쳐줘", "공통화해줘", "/trim" 등 변경분을 간결하게 정리하자는 말이 나오면 사용한다(변경분 단순화 요청에는 내장 simplify보다 우선). 글·문서 다듬기에는 쓰지 않고, 설계 모델 재정의는 wow, 버그 리뷰는 code-review를 쓴다.
---

# trim

이미 끝난 diff를 대상으로, 동작은 유지하면서 군더더기를 덜어내고 흩어진 중복과 패턴을 엮는 스킬이다.
목표는 줄 수가 아니라 읽는 사람이 머리에 들고 있어야 하는 개념 수와, 같은 정책을 고칠 때 손대야 하는 변경 지점 수를 줄이는 것이다.

## 불변 규칙

- 동작을 바꾸지 않는다.
- 판단 기준은 줄 수가 아니라 읽는 사람이 머리에 들고 있어야 하는 개념 수다. 줄이 줄어도 추적할 상태가 늘면 실패다.
- 공개 API, 데이터 계약, UX 의도, 접근성 의미를 바꾸지 않는다.
- 테스트 의미를 약하게 만들지 않는다.
- 새 기능을 추가하지 않는다. 요구사항을 다시 해석하지 않는다.
- git index와 staging 구분을 임의로 바꾸지 않으며, rollback 시 실행 전 staged·unstaged·untracked 상태를 정확히 복원한다.
- 엮기는 비슷해서 묶지 않는다. 같은 이유로 변하는 것만 묶고, 애매하면 묶지 않는다.
- 작은 중복을 없애려고 큰 추상화를 만들지 않는다. 읽기 쉬운 로컬 코드를 멀리 보내지 않는다.

## 호출 형태

```text
/trim
/trim --go
/trim -go
```

- `/trim`: 현재 diff를 분석하고 덜어내기·엮기 후보와 검증 계획만 제안한다. 승인 전에는 파일을 수정하지 않는다.
- `/trim --go`, `/trim -go`: 같은 분석을 수행하되 승인 질문 없이 근거 1·2등급 후보만 적용한다. 엮기 후보 중 feature 경계, public API, 의존성 방향이 바뀌는 것은 계획으로만 남긴다.

## wow와의 차이

```text
trim = 기존 설계 안에서 덜어내고(빼기) 엮는다(모으기)
wow  = 문제 정의와 설계 모델 자체를 다시 잡는다
```

## 대상 범위

기본 대상은 현재 작업 diff다.

1. dirty worktree가 있으면 `HEAD` 대비 변경을 본다. staged 변경도 포함한다.
   - `git diff HEAD --stat`
   - `git diff HEAD --name-only`
   - `git diff HEAD`
   - `git ls-files --others --exclude-standard`
2. worktree가 깨끗하고 현재 브랜치가 base보다 앞서 있으면 브랜치 diff를 본다.
   - `git log --oneline <base>..HEAD`
   - `git diff --stat <base>...HEAD`
   - `git diff <base>...HEAD`
   - base는 `git symbolic-ref refs/remotes/origin/HEAD` → `main` → `master` 순으로 정한다.
3. 사용자가 파일, 디렉터리, 모듈을 지목했으면 diff가 없어도 그 범위의 중복·흩어진 패턴을 본다.
4. 셋 다 아니면 "어느 변경분이나 범위를 정리할까요?" 질문 하나만 하고 멈춘다.

전체 코드베이스를 무작정 정리하지 않는다.

## 분석 순서

1. 현재 repo와 대상 범위를 확인한다. git 저장소가 아니면 중단하고 보고한다.
2. 변경 전 검증 명령을 찾는다.
   - package script, test script, lint, typecheck, build, 기존 CI 문서
   - 명확한 명령이 없으면 "검증 명령 없음"으로 기록한다.
3. `git diff HEAD --stat`으로 변경량 기준을 기록한다.
4. diff와 주변 코드를 읽고 후보를 두 갈래로 분류한다.
   - 덜어내기 후보: 같은 동작을 더 단순한 코드로
   - 엮기 후보: 흩어진 중복·패턴을 같은 이유로 변하는 단위로
5. 후보별로 "동작 보존 근거 등급"과 "검증 방법"을 적는다.
6. `--go`가 아니면 계획을 제안하고 멈춘다.

## 동작 보존 근거 등급

후보마다 등급을 매긴다. 이 등급이 적용 여부를 정하는 유일한 척도다.

1. 타입, 테스트, lint가 기계적으로 보장한다.
2. 호출부와 입력 계약을 전수 확인했다.
3. 코드만 읽은 추론이다.

`--go`에서는 1, 2등급만 적용한다. 3등급은 계획 모드에서 사용자 판단에 맡긴다.

같아 보여도 동작이 바뀌는 전형 사례를 후보마다 점검한다: 평가 순서와 단락 평가, null/undefined와 falsy의 구분, 예외 전파 경로, async 타이밍, 객체 identity 의존, 반복 중 mutation.

## 덜어내기 후보

아래는 스택 중립 원리다. 괄호 안 예시는 React/TS 관용구이며, 백엔드·CLI·라이브러리에서는 같은 원리를 그 스택의 형태로 찾는다.

- 파생 값을 별도 상태로 저장: 다른 값에서 계산 가능한데 따로 들고 있는 경우 (예: React 파생 state, 서버 응답을 로컬에 중복 캐시, 계산 가능한 멤버 필드)
- 불필요한 동기화: 필요할 때 계산하면 되는 값을 별도 단계로 동기화하는 경우 (예: `useEffect`로 state 복사, setter에서 파생 필드 갱신, 캐시 무효화 콜백)
- 이득 없는 메모이제이션: 비용보다 효과가 작은 캐싱 (예: `useMemo`, `useCallback`, `memo`, 불필요한 lazy/precompute)
- 불필요한 wrapper: 입력을 그대로 넘기기만 하는 중간 계층 (예: props를 그대로 전달하는 component, hook, 인자만 포워딩하는 함수)
- 과한 추상화: 한 번만 쓰이거나 호출부보다 복잡한 helper
- 장황한 조건문: guard clause, lookup table, 단순 boolean 식으로 표현 가능한 경우
- 의미 없는 방어 코드: 실제 입력 계약상 도달하지 않는 null/undefined, 빈 값, 예외 분기
- 테스트 장황함: assertion에 기여하지 않는 mock, setup, 중복 케이스
- 타입 과설계: 실제 사용보다 복잡한 타입 구성 (예: generic, mapped type, conditional type)

## 엮기 후보

엮는 것이 매우 좋을 때만 제안한다. 핵심 판정은 하나다: 한 정책·규칙이 바뀔 때 둘 이상의 파일을 항상 함께 고쳐야 하면 같은 이유로 변하는 것이고, 한쪽만 따로 바뀔 수 있으면 묶지 않는다.

- 같은 정책이나 규칙, 같은 조건·매핑·변환·setup이 여러 곳에 반복됨
- 한 도메인의 타입, 상수, schema, formatter, mapper가 흩어짐
- 화면마다 로딩, 에러, empty 처리 방식이 제각각임
- 같은 역할의 helper나 hook이 이름만 다르게 여러 곳에 있음
- 반복되는 상수·설정·스타일이 변경 비용을 만듦
- 테스트 setup이나 fixture가 반복되어 변경 비용을 만듦

세부 판정 기준, 엮지 말 것 목록, 좋은 엮기의 조건은 `references/weave-criteria.md`를 따른다. 애매한 후보는 엮지 않고 "보류한 후보"로 남긴다.

## 상태 단순화 기준

수정해도 된다:

- 어떤 값이 항상 다른 값에서 계산된다. (예: 파생 state, 중복 멤버 필드)
- 동기화 단계가 값을 단순 복사하기만 한다. (예: state를 복사하는 effect)
- 여러 boolean이 사실 하나의 status로 표현된다.
- 같은 출처의 상태를 두 곳에 중복 저장한다. (예: 서버 상태를 로컬 state에 캐시, 같은 데이터를 두 변수에 보관)

수정하면 안 된다:

- 사용자가 입력 중인 임시 값이다.
- 시간 의미가 있는 상태다. (예: optimistic update, animation, transition, debounce)
- 외부 시스템과 동기화하는 의도적 상태다. (예: 외부 store, URL, storage)
- reference identity가 동작에 의미 있게 쓰인다. (예: memoized child, effect dependency, 캐시 키)

## 구조 단순화 기준

수정해도 된다:

- helper가 호출부 하나뿐이고 호출부보다 복잡하다.
- wrapper가 의미 있는 책임 없이 그대로 감싸기만 한다. (예: semantic, accessibility, layout 책임 없는 component)
- 파일 분리가 이해를 돕지 않고 이동 비용만 만든다.
- 반복 코드를 합쳐도 이름과 책임이 더 명확해진다.

수정하면 안 된다:

- public API이거나 외부에서 import될 가능성이 있다.
- 경계 자체가 의미를 갖는 구조다. (예: design system, route boundary, lazy loading boundary, 모듈/패키지 경계)
- 테스트 fixture나 story가 문서 역할을 한다.
- 의도적 책임을 가진 wrapper다. (예: 접근성, semantic tag, layout containment)

## 금지 변경

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
- 순환 import나 역방향 의존성을 만드는 공통화

## `/trim` 응답 형식

기본 호출에서는 아래를 제안하고 멈춘다.

```text
trim 계획

덜어내기 후보
1. <후보>
   - 파일: ...
   - 단순화: ...
   - 동작 보존 근거: <내용>, 등급 1/2/3

엮기 후보
1. <후보>
   - 흩어진 위치: ...
   - 공통으로 묶을 개념: ...
   - 엮을 때 줄어드는 변경 지점: ...
   - 동작 보존 근거: <내용>, 등급 1/2/3

보류한 후보
- <왜 덜어내거나 엮지 않는지>

검증
- 사전 실행: ...
- 사후 실행: ...
- diff stat 비교: ...

이대로 trim할까요?
```

근거 3등급 후보는 기본 계획에서 제외하거나 별도 선택지로 둔다.

## `--go` 실행 규칙

`--go` 또는 `-go`가 있으면 다음 순서로 진행한다.

1. baseline을 기록한다.
   - `git diff HEAD --stat`
   - `git diff --cached --binary`와 `git diff --binary`를 서로 다른 `mktemp` 파일에 기록해 staged와 unstaged baseline을 분리한다.
   - 첫 쓰기 전에 수정할 모든 경로의 작업 트리 내용·존재 여부·파일 종류를 `backup=$(mktemp -d /tmp/pre-trim.XXXXXX)`에 기록한다. 기존 untracked도 같이 백업한다.
   - trim 중에는 `git add`, `git rm`, `git restore`, `git checkout`, `git reset`을 실행하지 않고 index를 건드리지 않는다. baseline과 백업이 없으면 trim을 시작하지 않는다.
   - 가능한 검증 명령 결과
2. 근거 1·2등급 후보만 적용한다. feature 경계, public API, 의존성 방향이 바뀌는 엮기 후보는 계획으로만 남긴다.
3. 엮기를 적용했으면 import, export, 테스트 fixture도 함께 정리한다.
4. 같은 검증 명령을 다시 실행하고 `git diff HEAD --stat` 전후를 비교한다.
5. 실패하면 원인을 파악해 고치거나, trim이 만든 델타만 되돌린다. 수정한 tracked·기존 untracked는 작업 트리 백업으로 복원하고 trim이 새로 만든 경로만 제거하되, index는 처음부터 건드리지 않아 staged 상태를 보존한다. 시작 후 사용자가 같은 경로를 다시 수정했거나 복원이 그 변경을 덮을 수 있으면 자동 복원하지 말고 중단·보고한다. `git restore`/`checkout`/`reset`으로 전체 경로를 되돌리지 않는다.
6. 최종 보고에는 덜어낸 것, 엮은 개념과 줄어든 변경 지점, 실행한 검증, 남긴 리스크를 포함한다.

## 중단 조건

아래 상황에서는 `--go`여도 수정하지 않는다.

- git 저장소가 아니거나, diff가 비어 있고 지목된 범위도 없음
- baseline 빌드나 테스트가 실패했고 실패 원인을 파악할 수 없음
- secret, credential, 개인 정보가 diff에 포함된 정황
- 생성물, lockfile, 대형 바이너리만 바뀌어 정리 대상이 아님
- 같은 이유로 변한다는 근거가 약한 엮기 후보뿐임
- feature boundary나 public API 변경이 필요함
- 의존성 방향이 나빠지거나 순환 import 위험이 있음
- 동작 보존 근거가 3등급뿐임
- 사용자가 만든 기존 변경과 trim 대상이 얽혀 있어 안전하게 분리할 수 없음

중단할 때는 이유와 다음 행동을 짧게 제시한다.
