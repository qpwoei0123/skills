# Skill Standard

이 문서는 이 저장소에 편입되는 모든 스킬의 최소 형식을 정의한다.
핵심 원칙은 간단하다.

- 창작은 자유롭게 한다.
- 편입은 엄격하게 한다.
- 공통 규격은 레포가 강제한다.
- 개별 스킬의 구조 확장은 성격에 따라 허용한다.

## 목표

- 스킬마다 최소한의 형식을 맞춘다.
- 버전, 변경 이력, 사용자 문서를 일관되게 유지한다.
- `orbit` 같은 복잡한 스킬과 `annotate` 같은 단순한 스킬을 모두 수용한다.
- 이후 `validator(형식 검증 스크립트)`와 `CI(자동 검증 파이프라인)`로 자동 검사할 수 있게 만든다.

## 적용 범위

이 문서는 이 저장소의 모든 정식 스킬에 적용한다.

- 정식 스킬: `skills/<카테고리>/` 아래의 스킬 디렉터리
- 카테고리: 사용 무게 기준 — `데일리함`(가벼운 일상 도구), `살짝무거움`(멀티스텝 워크플로)
- 예시: `skills/데일리함/commit/`, `skills/살짝무거움/orbit/`
- 스킬 디렉터리 이름은 카테고리가 달라도 전역에서 유일해야 한다. 배포와 npx 설치가 이름 기준이기 때문이다.

임시 초안은 이 저장소 밖에서 만들 수 있다.
이 저장소에 들어오는 순간부터 이 표준을 따라야 한다.

## 상태

스킬의 상태는 아래 세 단계로 본다.

### `draft`

- 저장소 밖 또는 별도 작업 공간에서 실험 중인 상태
- 형식 강제 없음

### `accepted`

- 이 저장소에 편입된 정식 스킬
- 이 문서의 `MUST(반드시 지켜야 하는 규칙)`를 만족해야 한다

### `deprecated`

- 더 이상 새 작업에 권장하지 않는 스킬
- 즉시 삭제하지는 않지만 README 또는 changelog에 상태를 남긴다

## Core Standard

아래는 모든 `accepted` 스킬에 공통으로 적용하는 최소 규격이다.

### MUST — 필수 파일

모든 정식 스킬은 아래 파일을 가져야 한다.

```text
skill-name/
├── SKILL.md
├── README.md
└── CHANGELOG.md
```

### MUST — `SKILL.md`

`SKILL.md`는 실행 계약의 기준 문서다.
버전의 `SSOT(단일 기준 원천)`도 여기 둔다.

frontmatter 최소 형식:

```yaml
---
name: orbit
license: Apache-2.0
metadata:
  version: 1.7.0
description: (v1.7.0) 스킬 설명. 트리거 문구 예시 포함.
---
```

필수 키:

- `name`
- `license`
- `metadata.version`
- `description`

규칙:

- `name`은 호출 이름과 일치해야 한다.
- `metadata.version`은 `SemVer(주버전.부버전.수정버전 규칙)` 형식을 따른다.
- 버전 표기의 `SSOT(단일 기준 원천)`는 항상 `metadata.version`이다.
- `description`은 트리거와 용도를 설명해야 한다.
- `description`은 단일행으로 쓰고 `(vx.y.z)` 버전 접두사로 시작한다. 접두사는 `metadata.version`과 같아야 하며 normalize가 자동 동기화한다.
- `description: |`, `description: >` 같은 block scalar는 단일행 규약 위반으로 처리한다.

### MUST — `README.md`

`README.md`는 사람용 사용 설명서다.

최소 포함 섹션:

- 한 줄 소개
- 현재 버전
- Quick Start
- 파일 구조
- 테스트 또는 검증 방법

권장 최소 형태:

```text
# skill-name

`version: x.y.z`

한 줄 소개

## Quick Start
## Structure
## Test
```

### MUST — `CHANGELOG.md`

`CHANGELOG.md`는 사람 읽기용 변경 이력이다.

최소 형식:

```md
# Changelog

## 1.0.0

### Added
- ...
```

규칙:

- 최신 버전 항목이 맨 위에 있어야 한다.
- 최상단 버전은 `SKILL.md.metadata.version`과 같아야 한다.
- 빈 changelog라도 초기 버전 항목은 있어야 한다.

## Optional Capabilities

아래 구조는 스킬 성격에 따라 선택적으로 둔다.
없어도 된다. 다만 있으면 역할이 분명해야 한다.

### `agents/`

- Codex 인터페이스 메타데이터가 필요한 스킬
- 멀티 에이전트 흐름이 있는 스킬
- 역할 분리, 병합, 라운드 규칙이 필요한 경우

`agents/openai.yaml`이 있으면 아래 최소 계약을 지킨다.

```yaml
interface:
  display_name: "Orbit"
  short_description: "레포를 7개 관점으로 점검해 검증된 기술 이슈를 발행합니다"
  default_prompt: "$orbit으로 이 레포를 종합 점검해 주세요."
```

- `display_name`은 비어 있지 않아야 한다.
- `short_description`은 25~64자여야 한다.
- `default_prompt`에는 `$<skill-name>` 호출 예시가 있어야 한다.

### `references/`

- 본문에 다 담기 긴 규칙
- 템플릿
- 예시
- 출력 계약

### `scripts/`

- 반복 실행이 필요한 스크립트
- 검증, 생성, 동기화 같은 보조 코드

추가 규칙:

- `scripts/`가 있으면 README에 실행 방법이 있어야 한다.
- 가능하면 최소 1개의 테스트 또는 검증 커맨드를 함께 제공한다.

### `assets/`

- 이미지, 템플릿, 샘플 리소스
- 브랜딩용 에셋

### `evals/`

- 스킬 동작을 채점하는 eval 정의 (시나리오, assertion, 트리거 케이스)
- 정의 파일만 추적한다. 실행 결과물(벤치마크, 로그, 리포트)은 추적하지 않고 `.eval-archive/` 등 무시 경로에 둔다.

`evals/trigger-eval.json`이 있으면 비어 있지 않은 JSON 배열이어야 한다.

- 각 항목의 `query`는 비어 있지 않은 문자열이어야 한다.
- 각 항목의 `should_trigger`는 boolean이어야 한다.
- 선택 필드 `expected_behavior`는 비어 있지 않은 문자열이어야 한다.
- positive·negative 경계를 함께 검증하도록 `should_trigger: true`와 `false`를 모두 포함한다.

### `INDEX.md`

- 리소스가 많아 처음 읽는 사람이 길을 잃기 쉬울 때 둔다.
- 작은 스킬에는 필수가 아니다.

## 권장 디렉터리 예시

### 단순 스킬

```text
skills/데일리함/annotate/
├── SKILL.md
├── README.md
├── CHANGELOG.md
└── evals/
```

### 복잡한 워크플로 스킬

```text
skills/살짝무거움/orbit/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── INDEX.md
├── agents/
├── references/
├── scripts/
├── assets/
└── evals/
```

## 버전 규칙

정식 스킬은 `SemVer(주버전.부버전.수정버전 규칙)`를 따른다.

### `MAJOR`

아래처럼 호환성이 깨질 때 올린다.

- 출력 계약이 바뀜
- 호출 방식이 바뀜
- 기존 사용 예시가 더 이상 유효하지 않음

### `MINOR`

기능 추가일 때 올린다.

- 새 옵션
- 새 흐름
- 새 리소스 구조

### `PATCH`

작은 수정일 때 올린다.

- 버그 수정
- 문서 보강
- 테스트 보강
- 표현 수정

## 편입 규칙

밖에서 만든 스킬을 이 저장소에 가져올 때는 아래 순서를 따른다.

1. 스킬 디렉터리를 `skills/<카테고리>/` 아래로 가져온다.
2. `SKILL.md` frontmatter를 표준에 맞춘다.
3. `README.md`, `CHANGELOG.md`를 추가하거나 보강한다.
4. 선택 디렉터리(`agents/`, `references/`, `scripts/`, `assets/`)를 역할에 맞게 정리한다.
5. 이후 `validator(형식 검증 스크립트)`로 검사한다.

## 검증과 배포

- `validate_skills.py`는 필수 문서, 단일행 description, trigger eval, OpenAI manifest 계약을 검사한다.
- `deploy_skills.py --check`는 버전뿐 아니라 배포 디렉터리의 실제 파일 내용 drift도 검사한다.
- 배포는 모든 선택 스킬을 staging에 복사해 다시 검증한 뒤 swap한다.
- swap이 실패하면 이미 교체한 스킬을 역순으로 rollback해 기존 배포본을 복구한다.
- `__pycache__/`, `*.pyc`, `.DS_Store`, `node_modules/`는 배포 콘텐츠와 drift 비교에서 제외한다.

## Autofix Policy

자동 정규화는 구조 보정만 허용한다.
의미를 해석하거나 새 문장을 창작하는 수정은 자동화 대상이 아니다.

자동 수정 가능한 항목:

- `SKILL.md`의 top-level `version`을 `metadata.version`으로 이동
- 단일행 `description`의 `(vx.y.z)` 접두사를 `metadata.version`에 동기화
- 누락된 `README.md`, `CHANGELOG.md` 생성
- README의 `version:` 표기 동기화
- README의 `Quick Start`, `Structure`, `Test` 섹션 보강
- CHANGELOG 최신 버전 헤더 생성 또는 동기화

자동 수정하지 않는 항목:

- `name`
- `license`
- block scalar description과 설명 본문
- README 소개 문장의 의미
- 스킬 트리거와 동작 의미

운영 원칙:

- `validator`는 실패를 판정한다.
- `normalizer`는 자동 수정 가능한 구조만 보정한다.
- 수동 판단이 필요한 오류는 CI가 실패로 남기고 사람이 직접 수정한다.
- 자동 수정은 `main` push 뒤 별도 normalize PR로 제안한다.

## 표준화하지 않는 것

아래는 강제하지 않는다.

- 문체
- README 디자인
- 에셋 존재 여부
- references 파일 개수
- scripts 언어
- 아이콘 사용 여부

즉, 이 표준은 표현보다 계약과 구조를 다룬다.

## 운영 체크리스트

1. `scripts/validate_skills.py`로 전체 스킬 계약을 검사한다.
2. 루트 unittest로 validator·normalizer·deploy 회귀를 확인한다.
3. `templates/skill/`을 현재 표준과 함께 유지한다.
4. `orbit`, `annotate`, `soul-extractor`를 포함한 현재 accepted 스킬의 정합성을 유지한다.
