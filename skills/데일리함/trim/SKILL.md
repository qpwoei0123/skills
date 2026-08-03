---
name: trim
license: Apache-2.0
metadata:
  version: 0.4.2
description: (v0.4.2) 동작을 유지하면서 현재 diff의 군더더기를 덜어내고 흩어진 중복·패턴을 같은 이유로 변하는 단위로 엮는 스킬. "코드 줄여줘", "단순하게 해줘", "중복 합쳐줘", "공통화해줘", "/trim" 등 변경분 단순화 요청에 사용한다(내장 simplify보다 우선). 주석까지 함께 요청하면 trim이 코드 정리와 검증을 맡고 annotate가 최종 diff를 잇는다. 설계 모델 재정의는 wow, 버그 리뷰는 code-review를 쓴다.
---

# trim

이미 구현된 변경의 동작을 유지하면서 개념 수와 같은 정책의 변경 지점을 줄인다. 줄 수만 줄고 추적할 상태나 추상화가 늘면 실패다.

## 계약

- 공개 API, 데이터 계약, UX, 접근성, 예외·타이밍 의미를 바꾸지 않는다.
- 테스트와 타입의 보장 수준을 낮추거나 새 기능을 추가하지 않는다.
- 비슷한 모양이 아니라 같은 이유로 변하는 코드만 엮는다.
- 작은 중복을 없애려고 더 큰 추상화나 역방향 의존성을 만들지 않는다.
- git index를 건드리지 않고 기존 staged·unstaged·untracked 상태를 보존한다.

## 호출

```text
/trim
/trim --go
/trim -go
```

- 기본 호출은 덜어내기·엮기 후보와 검증 계획만 제안한다.
- `--go`, `-go`는 동작 보존 근거 1·2등급 후보만 적용한다. public API, feature 경계, 의존성 방향이 바뀌는 후보는 계획에만 남긴다.

## 연계 요청

```text
wow      문제 정의와 설계 모델을 다시 제안함
trim     기존 동작 안에서 코드를 덜고 엮음
annotate 최종 코드에 필요한 이유와 제약만 설명함
```

- 코드 정리와 주석을 함께 요청하면 `trim`이 전체 수정 흐름을 맡는다.
- trim 적용과 검증을 끝낸 뒤 최종 diff에만 `annotate`를 실행한다.
- 주석만 요청받았으면 `trim`을 자동 실행하지 않는다.

## 범위

1. dirty worktree가 있으면 `HEAD` 대비 staged·unstaged 변경과 untracked 파일을 본다.
2. worktree가 깨끗하고 현재 branch가 base보다 앞서면 `<base>...HEAD`를 본다. base는 remote default → `main` → `master` 순으로 정한다.
3. 사용자가 파일·디렉터리·모듈을 지정했으면 diff 없이도 그 범위를 본다.
4. 어느 조건도 없으면 정리할 범위를 질문 하나로 묻는다.

전체 코드베이스를 임의로 정리하지 않는다.

## 분석

1. repo와 범위를 확인하고 diff stat을 기록한다.
2. 변경 파일에 대응하는 test, lint, typecheck, build 명령을 찾는다. 없으면 그대로 기록한다.
3. diff와 필요한 주변 코드를 읽고 `덜어내기`와 `엮기` 후보로 나눈다.
4. 후보마다 동작 보존 근거 등급과 검증 방법을 적는다.
5. 기본 호출이면 계획에서 멈추고, `--go`면 1·2등급만 적용한다.

## 동작 보존 근거

1. 타입, 테스트, lint가 기계적으로 보장함
2. 호출부와 입력 계약을 전수 확인함
3. 코드만 읽은 추론임

`--go`는 1·2등급만 적용한다. 후보마다 평가 순서, 단락 평가, null과 falsy, 예외 전파, async timing, 객체 identity, 반복 중 mutation이 달라지지 않는지 확인한다.
3등급은 적용 후보와 섞지 않고 보류 항목으로 분리한다.

## 후보 판정

덜어내기 후보:

- 다른 값에서 계산 가능한 중복 상태와 복사 동기화
- 효과가 비용보다 작은 메모이제이션·캐시
- 입력을 그대로 전달하는 wrapper와 한 번만 쓰이는 과한 helper
- guard, 단순 boolean, lookup으로 직접 표현 가능한 장황한 분기
- 실제 입력 계약상 도달하지 않는 방어 분기
- assertion에 기여하지 않는 테스트 setup·mock과 사용보다 복잡한 타입

엮기 후보가 보이면 [references/weave-criteria.md](references/weave-criteria.md)를 읽는다. 한 정책 변경 때 여러 위치를 항상 함께 고쳐야 하고, 합친 뒤 실제 변경 지점이 줄어들 때만 적용한다.

수정하지 않는다:

- 사용자 입력 중간값, optimistic update, animation, debounce처럼 시간 의미가 있는 상태
- 외부 store·URL·storage와 의도적으로 동기화하는 상태
- 접근성·semantic·layout·route·lazy loading 책임이 있는 경계
- public API, 데이터 shape, UX 문구, 테스트 assertion, 접근성 속성
- 추측만으로 하는 삭제나 순환 import를 만드는 공통화

## 응답 형식

```text
trim 계획

덜어내기 후보
1. <후보>
   - 파일:
   - 단순화:
   - 동작 보존 근거: <내용>, 등급 1 | 2 | 3

엮기 후보
1. <후보>
   - 흩어진 위치:
   - 묶을 개념:
   - 줄어드는 변경 지점:
   - 동작 보존 근거: <내용>, 등급 1 | 2 | 3

보류한 후보
- <이유>

검증
- 사전/사후:
- diff stat 비교:

이대로 trim할까요?
```

## `--go` 실행

1. `git diff HEAD --stat`, staged·unstaged binary patch를 각각 기록한다.
2. 첫 수정 전에 대상 경로의 내용·존재 여부·파일 종류와 기존 untracked를 `mktemp -d` 아래 백업한다. baseline이나 백업이 없으면 시작하지 않는다.
3. 실행 중 `git add`, `git rm`, `git restore`, `git checkout`, `git reset`을 쓰지 않는다.
4. 근거 1·2등급만 적용하고 import, export, fixture까지 일관되게 정리한다.
5. 같은 검증과 diff stat 비교를 실행한다.
6. 실패하면 trim이 만든 델타만 복원한다. 동시 사용자 변경을 덮을 수 있으면 자동 복원하지 않고 중단한다.
7. 덜어낸 개념, 엮은 정책과 줄어든 변경 지점, 검증, 남은 리스크를 보고한다.

## 중단

- git repo가 아니거나 대상 범위가 없음
- baseline 검증 실패 원인을 파악할 수 없음
- secret, credential, 개인정보 정황
- 생성물·lockfile·대형 바이너리만 바뀜
- 근거 3등급 후보나 약한 엮기 후보뿐임
- public API·feature 경계 변경 또는 순환 의존성이 필요함
- 사용자의 기존 변경과 trim 델타를 안전하게 분리할 수 없음

중단할 때는 이유와 가능한 다음 행동만 짧게 보고한다.
