---
name: mr
license: Apache-2.0
metadata:
  version: 0.4.0
description: (v0.4.0) 현재 브랜치를 push하고 제목/본문을 맞춰 GitHub draft PR 또는 GitLab draft MR을 만드는 스킬. "PR 올려줘", "MR 만들어줘", "리뷰 요청해줘", "/mr" 등 코드 리뷰 요청 관련 말이 나오면 사용한다.
---

# mr

현재 브랜치의 커밋과 diff를 읽고 코드 리뷰 요청을 준비하거나 생성하는 스킬이다.
이 스킬에서 `MR`은 코드 리뷰 요청 단위를 뜻한다. GitHub에서는 Pull Request, GitLab에서는 Merge Request로 생성한다.

## 불변 규칙

- MR/PR 생성은 항상 draft로 한다. — 리뷰가 끝나지 않은 코드가 곧장 merge 대상으로 노출되는 사고를 막기 위해서다.
- 일반 MR/PR 생성으로 fallback하지 않는다. — draft 의도가 사라진 채 리뷰 전 코드가 정식 MR/PR로 열리는 사고를 막기 위해서다.
- draft 생성이 보장되지 않으면 `--go`여도 생성하지 않고 중단한다. — 보장되지 않은 채 강행하면 일반 MR/PR로 새는 길을 남기기 때문이다.
- 커밋은 만들지 않는다. dirty worktree가 있으면 `/commit`을 먼저 안내한다.
- 제목은 Conventional Commits 형식을 유지한다.

## 호출 형태

```text
/mr
/mr --go
/mr -go
```

- `/mr`: 현재 브랜치, base, 커밋, diff, 주변 MR/PR 스타일을 분석하고 계획만 제안한다. 승인 전에는 push나 MR/PR 생성을 하지 않는다.
- `/mr --go`, `/mr -go`: 같은 분석을 수행하되 승인 질문 없이 push와 draft MR/PR 생성을 진행한다.

## 세션 경계

- push와 MR/PR 생성 권한은 현재 사용자 요청 1회에만 적용된다.
- 이전 턴의 승인, `--go`, MR 계획, push 결과, 생성 결과는 다음 사용자 요청에 이월하지 않는다.
- 직전 턴에서 MR/PR을 만들었더라도 다음 구현, 수정, 리뷰 요청은 새 작업으로 본다.
- 다음 작업에서 `/mr`, `/mr --go`, "MR 만들어줘", "PR 올려줘", "리뷰 요청해줘" 같은 명시 요청이 없으면 절대 push하거나 MR/PR을 만들지 않는다.
- 새 커밋이나 파일 수정이 발생한 뒤 MR/PR을 만들려면 사용자가 다시 MR/PR 생성을 요청해야 한다.

## 분석 순서

1. 현재 위치가 git repo인지 확인한다.
2. 작업 트리 상태를 확인한다.
   - `git status --short`
   - 변경사항이 있으면 중단한다. staged 변경도 dirty로 본다.
3. 현재 브랜치와 remote를 확인한다.
   - `git branch --show-current`
   - `git remote -v`
   - 현재 브랜치가 `main`, `master`, remote default branch면 중단한다.
4. base 브랜치를 추론한다.
   - `branch.<current>.gh-merge-base`
   - upstream 또는 tracking 정보
   - remote default branch
   - `main`
   - `master`
   - 애매하면 사용자에게 묻는다.
5. 리뷰 범위를 확인한다.
   - `git log --oneline <base>..HEAD`
   - `git diff --stat <base>...HEAD`
   - `git diff --name-only <base>...HEAD`
   - 필요하면 `git diff <base>...HEAD`
6. 플랫폼과 CLI를 확인한다.
   - GitHub remote: `gh auth status`, `gh pr create --help`
   - GitLab remote: `glab auth status`, `glab mr create --help`
   - `--draft` 플래그가 없거나 확인할 수 없으면 생성하지 않는다.
7. 현재 브랜치에 이미 열린 MR/PR이 있는지 확인한다.
   - GitHub: `gh pr list --head <branch> --state open`
   - GitLab: `glab mr list --source-branch <branch>`
   - 이미 있으면 새로 만들지 않고 기존 URL을 보고한다.
8. 주변 MR/PR 목록을 확인한다.
   - GitHub: `gh pr list --limit 10 --json number,title,body,baseRefName,headRefName,url`
   - GitLab: `glab mr list --limit 10`로 최근 MR의 제목과 IID 후보를 확인한다.
   - 목록 확인은 제목과 후보 수집용이다. 본문 구조 확인을 대체하지 않는다.
9. 주변 MR/PR 본문 구조를 확인한다.
   - GitHub: 최근 PR 2~3개의 `body`를 확인한다. 목록 JSON에 본문이 충분하면 그 결과를 사용하고, 비어 있거나 부족하면 `gh pr view <number> --json title,body,url`로 다시 확인한다.
   - GitLab: 최근 MR 2~3개를 골라 `glab mr view <iid> --comments=false`를 실행한다.
   - 로컬 템플릿이 없으면 이 단계는 더 엄격하다. CLI/권한 오류가 아닌 한 건너뛰지 않는다.
   - CLI나 권한 문제로 최근 MR/PR 본문을 볼 수 없으면 기본 템플릿으로 fallback하고, 실패 이유를 계획에 명시한다.

## 제목 규칙

제목은 Conventional Commits 형식을 기본으로 한다.

```text
<type>[(<scope>)]: <한글 요약>
```

예:

```text
feat: 피그마식 디자인 패널 도입
feat(workspace): 피그마식 디자인 패널 도입
fix(auth): 세션 만료 처리 보정
docs(mr): 드래프트 MR 생성 규칙 추가
```

제목 판단 우선순위:

1. 현재 브랜치의 대표 커밋 메시지
2. 최근 MR/PR 제목
3. 최근 git log 제목
4. 변경 파일의 최상위 디렉터리나 도메인

규칙:

- 주변 MR/PR 제목은 스타일 참고용이다. 최종 제목은 항상 Conventional Commits 형식을 유지한다.
- 주변 스타일이 비정형이면 의미만 가져오고 형식은 정규화한다.
- 주변 MR/PR이 `feat: ...`처럼 scope 없이 이어져 있으면 scope를 생략한다.
- 주변 MR/PR이 `feat(workspace): ...`처럼 scope를 쓰면 변경 범위에 맞는 scope를 붙인다.
- 섞여 있으면 변경 범위가 명확할 때만 scope를 붙이고, 애매하면 생략한다.
- 요약은 한글로 쓰고 마침표를 붙이지 않는다.

## 본문 규칙

본문은 레포 템플릿과 주변 MR/PR 구조를 우선 따른다.

우선순위:

1. 레포 템플릿
   - `.github/pull_request_template.md`
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/PULL_REQUEST_TEMPLATE/*.md`
   - `.gitlab/merge_request_templates/*.md`
2. 최근 MR/PR 본문 구조
3. 현재 브랜치 커밋과 diff 내용
4. 기본 템플릿

기본 템플릿:

```md
## 요약
-

## 변경 사항
-

## 검증
- [ ]

## 리스크
-
```

템플릿이 있으면 필수 섹션을 삭제하지 말고 실제 내용으로 채운다.
로컬 템플릿이 없으면 최근 MR/PR 본문 2~3개의 섹션 순서, 체크리스트, 검증 표기 방식을 확인한 뒤 본문 구조를 정한다.
`gh pr list`, `glab mr list`처럼 제목 목록만 확인한 상태에서는 "최근 MR/PR 본문 구조 확인"을 완료한 것으로 보지 않는다.
주변 본문을 확인하지 못했으면 기본 템플릿으로 fallback하고, "본문 확인 실패: <이유>"를 계획에 적는다.
검증을 실행했으면 `[x]`로 표시하고, 실행하지 못했으면 이유를 적는다.
리스크가 낮아도 "낮음"처럼 명시한다.

본문은 diff 요약이 아니라 리뷰어의 질문에 먼저 답하는 문서다.

- 왜 이 접근인지 적고, 버린 대안이 있으면 한 줄로 남긴다.
- 리뷰어가 집중해야 할 파일과 위험 지점을 "리뷰 포인트"로 명시한다. 전부 똑같이 중요하다는 본문은 실패다.
- 기계적으로 따라간 변경(rename 여파, import 정리)은 한 줄로 묶어 리뷰어의 주의를 아낀다.

## 셀프 리뷰

본문을 쓰기 전에 diff를 리뷰어 시점으로 한 번 다시 읽는다.

- 스스로 발견한 문제는 숨기지 않는다. 사소하면 본문 리스크에 적고, 심각하면 생성을 멈추고 보고한다.
- 커밋이 여러 의도로 섞인 대형 diff면 MR 분할을 먼저 제안한다. 리뷰 불가능한 MR을 만드는 것보다 낫다.

## `/mr` 응답 형식

기본 호출에서는 아래를 제안하고 멈춘다.

```text
MR 계획
- 플랫폼: GitHub PR 또는 GitLab MR
- base/head: <base> <- <branch>
- 제목: <title>
- 참고한 주변 MR/PR: <번호 또는 URL, 본문 확인 여부>
- 채택한 본문 구조: <레포 템플릿/최근 MR 구조/기본 템플릿>, <주요 섹션>
- 본문:
  ...

검증
- 실행: ...
- 생략: ...

생성 방식
- draft로 생성
- push 예정: ...

후속 작업
- 자동 push/MR 생성 없음
- 다음 MR/PR 생성은 사용자가 다시 요청해야 함

이대로 draft MR을 만들까요?
```

## `--go` 실행 규칙

`--go` 또는 `-go`가 있으면 다음 순서로 진행한다.

1. 중단 조건을 확인한다.
2. 필요한 검증을 실행한다.
3. 현재 브랜치를 push한다.

```bash
git push -u origin <branch>
```

4. 본문을 임시 파일에 저장한다.

```bash
body_file=$(mktemp /tmp/mr-body.XXXXXX.md)
```

5. GitHub면 draft PR을 생성한다.

```bash
gh pr create \
  --draft \
  --base <base> \
  --head <branch> \
  --title "<title>" \
  --body-file "$body_file"
```

6. GitLab이면 draft MR을 생성한다.

```bash
glab mr create \
  --draft \
  --target-branch <base> \
  --source-branch <branch> \
  --title "<title>" \
  --description "$(cat "$body_file")"
```

7. 생성된 URL, 제목, base/head, 실행한 검증을 보고한다.
8. MR intent를 종료한다. 최종 보고에는 "MR 작업은 여기서 종료됐습니다. 다음 작업은 별도 요청 없이는 push하거나 MR/PR을 만들지 않습니다."를 포함한다.

## 중단 조건

아래 상황에서는 `--go`여도 생성하지 않는다.

- dirty worktree가 있음
- 현재 브랜치에 이미 열린 MR/PR이 있음
- 현재 브랜치가 default branch임
- base 브랜치를 판단할 수 없음
- base 대비 새 커밋이 없음
- remote 플랫폼이 GitHub/GitLab인지 판단할 수 없음
- `gh` 또는 `glab` 인증이 안 됨
- draft 생성 플래그를 확인할 수 없음
- push 또는 MR/PR 생성 명령이 일반 MR/PR로 fallback될 위험이 있음
- secret, credential, 개인 정보가 리뷰 범위에 포함된 정황
- submodule, 대형 바이너리, 대량 삭제처럼 사용자의 명시 승인이 필요한 변경이 포함됨

중단할 때는 이유와 다음 행동을 짧게 제시한다.
