---
name: mr
license: Apache-2.0
metadata:
  version: 1.0.0
description: (v1.0.0) 요청한 작업을 push하고 저장소 관례에 맞는 GitHub Draft PR 또는 GitLab Draft MR을 만드는 스킬. "PR 올려줘", "MR 만들어줘", "커밋하고 PR까지", "$mr" 요청에 사용한다. 결함 리뷰는 review, 기존 Draft 본문 갱신은 ship이 맡는다.
---

# mr

작업을 리뷰 가능한 범위와 설명으로 묶어 Draft PR/MR로 제출한다.

## 요청과 범위

- `$mr`, `/mr`, "올려줘"는 필요한 커밋·push·Draft 생성까지 완료한다. "계획만", "본문만", "준비해줘"이면 원격 변경과 커밋 없이 요청한 결과만 만든다.
- `--go`, `-go`도 실행 표기로 받지만 명시된 계획·범위 제한을 우선한다. 진행 중인 요청의 승인은 완료까지 유지하며, 완료 후 다른 작업을 자동 제출하지 않는다.
- 항상 Draft로 생성한다. Draft를 보장할 수 없으면 일반 PR/MR로 바꾸지 않는다.
- 사용자 지시와 기여 문서가 기본값보다 우선한다. branch rename과 force push는 이 작업에 포함하지 않는다.
- "현재 작업을 올려줘"라면 같은 작업의 미커밋 변경도 포함해 `commit` 절차를 선행한다. "기존 커밋만"이면 HEAD 범위만 다룬다. 포함 범위가 모호할 때만 묻는다.
- 단순화·주석·재설계를 제출의 자동 선행 단계로 추가하지 않는다.

## 1. 대상 확인

1. git 상태와 기여 문서를 읽는다. `scripts/preflight.sh`는 읽기 전용 개요를 제공한다.
2. 사용자 지정 base → `branch.<name>.gh-merge-base` → 원격 기본 branch → `main` → `master` 순으로 base를 정한다. 현재 branch의 원격 추적 ref를 base로 쓰지 않는다. detached HEAD, default branch 또는 불분명한 base면 먼저 해결한다.
3. 플랫폼과 source/head·target/base 저장소를 식별한다. 원격 조회와 인증은 이미 인증된 `gh`/`glab`을 우선하고, push도 CLI 인증을 사용할 수 있는 HTTPS 경로를 확인한다. SSH를 먼저 시도하거나 편의를 위해 원격 URL·전역 git 설정을 임의 변경하지 않는다.
4. 같은 source repository와 head branch의 열린 PR/MR을 확인한다. 이미 있으면 중복 생성하지 않고 URL을 보고한다. 인증과 Draft 생성 지원은 실제 CLI 도움말로 확인한다.
5. 명시적인 branch 규칙이 있거나 이름이 제출을 막는 경우에만 [references/branch-conventions.md](references/branch-conventions.md)를 읽는다.

## 2. 리뷰 범위와 본문

필요한 커밋을 마친 뒤 `<base>..HEAD`와 `<base>...HEAD`로 실제 제출 범위를 확인한다. 요청 밖 변경은 포함하지 않는다.

[references/review-format.md](references/review-format.md)를 읽고 제목과 본문을 만든다. 상위 흐름이 준비한 제목·본문이 있으면 그 내용과 실제 범위가 맞는지 확인해 사용한다. 셀프 리뷰에서 심각한 결함이 발견되면 push 전에 해결하거나 중단하고, 남은 중요한 문제는 본문에 드러낸다.

현재 코드에 유효한 검증 결과를 재사용한다. 코드가 달라졌거나 새로 확인할 문제가 있을 때만 관련 검증을 다시 실행한다.

## 3. 제출

1. 제출 범위, base/head와 완성된 제목·본문을 준비한다. 계획 요청이면 여기까지 보고한다.
2. 원격 변경 직전에 같은 source/head의 열린 요청과 로컬 범위를 다시 확인한다. 작업 중 대상이나 범위가 예상 밖으로 달라졌으면 덮어쓰거나 중복 생성하지 않는다.
3. 확인한 저장소의 현재 branch만 push한다. 거절되면 force push하지 않는다.
4. push 후에도 같은 source/head의 열린 요청이 없는지 확인한 뒤 준비한 제목·본문으로 Draft를 생성한다. 본문은 임시 파일로 전달한다.

```bash
gh pr create --draft --base <base> --head <branch> --title "<title>" --body-file <body-file>
glab mr create --draft --target-branch <base> --source-branch <branch> --title "<title>" --description "$(cat "<body-file>")"
```

5. 생성된 URL, Draft 상태, source/target과 remote head SHA가 의도한 저장소·로컬 HEAD와 일치하는지 확인한다.
6. URL과 변경 요약, 필요한 검증 결과를 보고한다. 실패했다면 완료된 commit·push와 실행하지 못한 단계를 구분한다.

충돌, 비밀 정보 노출, 요청 범위의 검증 실패나 잘못된 원격 대상은 실제 문제를 해결하기 전까지 진행하지 않는다. 의도와 범위가 명확한 작업에 고정된 A/B 선택이나 별도 실행 승인을 덧붙이지 않는다.
