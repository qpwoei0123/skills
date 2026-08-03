---
name: mr
license: Apache-2.0
metadata:
  version: 0.7.0
description: (v0.7.0) 현재 브랜치를 push하고 레포 규칙에 맞는 GitHub draft PR 또는 GitLab draft MR을 만드는 스킬. "PR 올려줘", "MR 만들어줘", "리뷰 올릴 준비해줘", "/mr", "커밋하고 PR까지"처럼 새 리뷰 요청을 만들자는 말에 사용한다. 커밋까지 포함된 요청은 mr이 전체 흐름을 맡고 commit을 먼저 실행한다. 코드 검토는 code-review, 이미 열린 PR/MR 리뷰는 review를 쓴다.
---

# mr

현재 브랜치의 리뷰 범위를 읽고 push한 뒤 draft PR/MR을 계획하거나 생성한다. GitHub에서는 Pull Request, GitLab에서는 Merge Request를 뜻한다.

## 계약

- 항상 draft로 생성한다. draft를 보장할 수 없으면 일반 PR/MR로 fallback하지 않고 중단한다.
- 기여 문서의 브랜치·제목·본문·리뷰 규칙을 기본값보다 우선한다.
- 브랜치 rename은 사용자 동의 없이 하지 않는다.
- push와 PR/MR 생성 권한, dirty worktree 선택, rename 동의는 현재 요청에만 유효하다.
- 새 커밋이나 파일 수정 뒤에는 PR/MR 생성을 다시 요청받는다.

## 호출

```text
/mr
/mr --go
/mr -go
```

- 기본 호출은 base/head, 리뷰 범위, 제목·본문, push 계획만 제안한다.
- `--go`, `-go`는 필요한 선택을 받은 뒤 push와 draft PR/MR 생성을 실행한다.

## 연계 요청 소유권

- PR/MR 생성이 최종 목적이면 `mr`이 전체 흐름을 맡는다.
- "커밋하고 PR까지"처럼 커밋도 명시했으면 `commit` 절차로 먼저 커밋하고 바로 이 흐름을 이어간다. 원 요청의 승인 수준을 커밋 단계에도 적용하며 A/B 선택은 묻지 않는다.
- PR/MR만 요청했고 worktree가 dirty면 자동 커밋하지 않고 아래 A/B 흐름으로 선택받는다.
- 커밋만 요청받았으면 `mr`은 실행하지 않는다.

## 분석

1. git repo와 기여 문서를 확인한다. `scripts/preflight.sh`로 worktree, branch, remote, base 후보, 기여 문서, 플랫폼 후보를 한 번에 읽을 수 있다.
2. dirty worktree면 아래 분기를 준비하되 나머지 분석은 계속한다.
3. 현재 branch·remote·base를 정한다. base 우선순위는 `branch.<name>.gh-merge-base` → upstream → remote default → `main` → `master`다. default branch에서 실행하거나 base가 불명확하면 중단한다.
4. `<base>..HEAD` 커밋과 `<base>...HEAD` diff로 리뷰 범위를 확인한다.
5. GitHub/GitLab 플랫폼, `gh`/`glab` 인증, draft 플래그 지원을 확인한다.
6. 같은 head branch의 열린 PR/MR이 있으면 새로 만들지 않고 URL을 보고한다.
7. [references/branch-conventions.md](references/branch-conventions.md)를 읽고 현재 branch를 판정한다.
8. 최근 PR/MR 목록과 본문 2~3개를 확인한 뒤 [references/review-format.md](references/review-format.md)에 따라 제목과 본문을 만든다.

플랫폼별 핵심 확인 명령:

```text
GitHub: gh auth status, gh pr list --head <branch> --state open, gh pr create --help
GitLab: glab auth status, glab mr list --source-branch <branch>, glab mr create --help
```

## dirty worktree

남은 변경이 있으면 `commit`으로 커밋 계획만 만들고 두 안을 나란히 제시한다.

- A안: 기존 커밋만 리뷰 범위에 포함하고 남은 변경은 그대로 둔다.
- B안: commit 계획대로 커밋한 뒤 리뷰 범위에 포함한다.

두 안에서 달라지는 범위·제목·본문을 보여주고 한 안을 추천한다. 같은 작업의 잔여물이면 B안, 무관한 변경이면 A안을 추천한다. `--go`에서도 이 선택은 생략하지 않는다.

경계:

- 새 커밋이 없고 남은 변경만 있으면 A안은 제시하지 않는다.
- commit 중단 조건에 걸리면 B안을 제시하지 않는다.
- B안 커밋이 실패하면 A안으로 바꿔 진행하지 않고 중단한다.

## 셀프 리뷰

제목과 본문을 확정하기 전에 diff를 리뷰어 시점으로 다시 읽는다.

- 사소한 미해결 문제는 리스크에 공개하고, 심각한 문제는 생성을 멈춘다.
- 여러 의도가 섞여 리뷰하기 어려우면 PR/MR 분할을 먼저 제안한다.
- 리뷰 포인트를 1~3개로 좁히고 기계적 변경은 한 줄로 묶는다.

## 응답 형식

```text
MR 계획
- 플랫폼: GitHub PR | GitLab MR
- base/head: <base> <- <branch>
- 브랜치명: <부합 | 불일치, 제안 | 컨벤션 없음 | 확인 불가>
- 기여 문서: <경로와 반영 규칙 | 없음>
- 제목:
- 본문 기준: <레포 템플릿 | 최근 리뷰 요청 | 기본 템플릿>
- 참고한 PR/MR:
- 본문:

남은 변경 처리 (dirty일 때만)
- A안:
- B안:
- 추천:

검증
- 실행:
- 생략:

생성 방식
- draft
- push 예정:

이대로 draft PR/MR을 만들까요?
```

dirty worktree와 브랜치 불일치가 함께 있으면 A/B와 rename 선택을 질문 하나로 묶는다.

## `--go` 실행

1. 중단 조건을 확인한다.
2. 필요한 A/B와 rename 선택만 한 번 묻는다. 사용자가 처음부터 커밋을 포함했으면 B안으로 확정한다.
3. B안이면 `commit` 절차를 실행하고, 동의받았으면 `git branch -m <new-name>`으로 rename한다.
4. 리뷰 범위에 대응하는 test·lint만 실행하고 본문 검증 항목을 갱신한다.
5. `git push -u origin <branch>`로 현재 branch를 push한다.
6. `body_file=$(mktemp /tmp/mr-body.XXXXXX.md)`로 본문 파일을 만들고 플랫폼별 draft 명령을 실행한다.

```bash
gh pr create --draft --base <base> --head <branch> --title "<title>" --body-file <body-file>
glab mr create --draft --target-branch <base> --source-branch <branch> --title "<title>" --description "$(cat "$body_file")"
```

7. URL, 제목, base/head, 검증, rename, 선행 커밋 해시를 보고한다.
8. mr intent를 종료한다. 다음 작업은 새 요청 없이는 push하거나 PR/MR을 만들지 않는다.

## 중단

- A/B 또는 필요한 rename 선택을 받지 못함
- 선행 커밋 실패
- 같은 branch의 열린 PR/MR이 이미 있음
- default branch이거나 base 대비 새 커밋이 없음
- base, 플랫폼, 인증, draft 지원을 확인할 수 없음
- 일반 PR/MR로 fallback될 위험이 있음
- secret, credential, 개인정보 정황
- submodule, 대형 바이너리, 대량 삭제에 별도 승인이 필요함

중단할 때는 이유와 가능한 다음 행동만 짧게 보고한다.
