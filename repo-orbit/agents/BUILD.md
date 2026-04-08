# BUILD

빌드/배포 재현성 view다.
로컬과 CI와 배포 환경이 같은 경로를 타는지 본다.

## Agent A — 로컬 vs CI 빌드 스크립트 비교

찾을 것:

- `package.json scripts`와 CI 빌드 커맨드 일치 여부
- 로컬에서는 되는데 CI에서는 빠지는 플래그
- build/test/lint 순서 차이

## Agent B — 환경별 분기 명확성

찾을 것:

- dev/staging/prod 설정 분리 여부
- 환경 감지 로직의 일관성
- 브랜치나 호스트명에 과도하게 의존하는 분기

## Agent C — 컨테이너 설정 일관성

찾을 것:

- Dockerfile 또는 컨테이너 설정 존재 여부
- 베이스 이미지 버전 고정 여부
- 런타임과 빌드 이미지 차이로 생기는 드리프트

## 우선 조사 경로

- `package.json` scripts, Makefile, task runner 설정
- `.github/workflows`, `.gitlab-ci.yml`, deploy 스크립트
- Dockerfile, compose, 배포 플랫폼 설정 파일

## finding으로 올릴 최소 조건

- 로컬과 CI/배포가 서로 다른 명령 또는 다른 입력을 쓰는 근거가 있다.
- 차이가 결과물 경로나 실패 조건에 영향을 준다고 설명할 수 있다.
- 수정해야 할 스크립트, job, Dockerfile 라인을 `next_step`에 적을 수 있다.

## 문제로 보지 않는 경우

- 캐시, 병렬화, 출력 로그 옵션만 다른 경우
- lint/test/build를 분리했지만 전체 파이프라인으로는 동일 집합을 보장하는 경우
- dev 전용 분기를 prod drift로 과장하는 경우

## 축소 조사 규칙

- CI가 없어도 release script, deploy script, README 실행법과 로컬 명령을 비교한다.
- 컨테이너가 없으면 Node, pnpm, Python 버전 선언 파일로 환경 drift를 대신 본다.

## 스킵 조건

- CI 없음 → A를 로컬 스크립트만으로 축소
- 컨테이너 없음 → C 스킵

## Orchestrator 메모

- 로컬/CI 경로 불일치는 impact를 높게 본다.
- 환경 분기 모호성과 컨테이너 드리프트가 함께 나오면 다음 배포 위험으로 묶을 수 있다.
