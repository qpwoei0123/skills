---
name: ship
license: Apache-2.0
metadata:
  version: 0.2.0
description: (v0.2.0) 현재 작업을 정리·주석·검증·커밋한 뒤 push하고 새 Draft PR/MR을 만들거나 현재 branch의 기존 Draft 본문을 갱신하는 제출 오케스트레이션 스킬. "출항해줘", "기존 드래프트에 이어서 출항해줘", "트림하고 주석 달아 커밋·PR까지", "$ship", "/ship"처럼 구현 완료 후 리뷰 요청을 만들거나 최신화하라는 요청에 사용한다. 커밋만은 commit, 새 Draft 생성만은 mr을 쓴다.
---

# ship

현재 작업을 리뷰 가능한 상태로 다듬고 새 Draft PR/MR을 만들거나 현재 branch의 기존 Draft를 최신화한다. 각 단계의 세부 판단은 `trim`, `annotate`, `commit`, `mr`에 맡기고 이 스킬은 범위, 순서, 승인, 중단과 최종 보고를 소유한다.

## 호출

```text
$ship
$ship --go
$ship -go
```

- 기본 호출은 같은 사전 점검으로 정리·커밋 계획과 새 Draft의 제목·본문 또는 기존 Draft의 본문 수정안을 만들고 멈춘다.
- `--go`, `-go`는 정리, 주석, 검증, 커밋, push 뒤 새 Draft 생성 또는 기존 Draft 본문 갱신까지 실행한다. 이 호출 자체를 해당 흐름의 승인으로 본다.
- `/ship`도 같은 호출로 취급한다.

`--go`의 승인은 처음 확인한 리뷰 범위와 그 범위를 다듬으며 생긴 변경, 사전에 보여준 기존 Draft 본문 수정에만 유효하다. branch rename, force push, 일반 PR/MR 생성, 기존 Draft의 제목·상태·리뷰어·라벨 변경, 예상 밖 파일 수정으로 확대하지 않는다.

아래 흐름에서 기본 호출은 쓰기 단계를 후보와 예상 결과로만 계산한다. 실제 파일 수정과 git·원격 작업은 `--go`, `-go`에서만 수행한다.

## 연계 계약

각 단계 직전에 사용할 수 있는 `trim`, `annotate`, `commit`, `mr`의 `SKILL.md`를 읽고 중단·검증·복원 규칙을 따른다.

```text
ship
  -> trim --go
  -> annotate --go
  -> commit --go
  -> push
     -> 열린 리뷰 요청 없음: mr --go로 새 Draft 생성
     -> 현재 branch의 Draft 있음: 기존 Draft 본문 갱신
```

- 위 연결은 실행 모드 기준이다. 기본 호출에서는 각 하위 스킬과 원격 변경도 계획으로만 계산한다.
- `ship`이 전체 요청을 소유하므로 하위 단계 사이에 승인을 다시 묻지 않는다.
- dirty worktree는 현재 리뷰 범위 전부를 커밋하는 안으로 고정한다. 무관한 변경이 섞여 이 기본값을 적용할 수 없으면 중단한다.
- `mr`의 branch rename 선택은 `아니오`로 고정한다. 기여 문서상 rename이 필수라면 중단한다.
- `mr --go`는 새 Draft 경로에서만 실행한다. 기존 Draft 경로에서는 `mr`의 제목·본문 형식 규칙만 따르며, `ship`이 대상 고정·동시 변경 감지·본문 병합·플랫폼별 갱신·사후 검증을 소유한다. `mr`의 열린 요청 중단 조건은 중복 생성을 막는 신호로 해석한다.
- 필요한 하위 스킬을 찾을 수 없으면 빠진 이름을 보고하고 시작하지 않는다.
- 후보 없음, 남길 주석 없음, 새로 커밋할 diff 없음은 정상적인 생략이다.
- `ship` 실행 중에는 검증 근거를 만들기 위한 테스트를 새로 작성하지 않는다.

## 1. 사전 점검

외부 변경 전에 실패 조건을 최대한 먼저 찾는다.

1. git repo, 충돌 상태, staged·unstaged·untracked, 현재 branch와 remote를 확인한다. detached HEAD면 중단한다.
2. base는 `branch.<name>.gh-merge-base` → remote default → `main` → `master` 순으로 정한다. `@{upstream}`이 같은 branch의 원격 추적 ref면 base로 쓰지 않는다.
3. 기여 문서, 플랫폼, 인증과 현재 branch를 source/head로 쓰는 열린 PR/MR을 확인한다. 열린 요청의 ID·URL·상태·Draft 여부·source repository와 branch·target·remote head SHA·제목·본문을 기록한다.
4. 현재 branch가 default branch면 중단한다. branch 이름이 관례와 달라도 자동 rename하지 않으며, 기여 문서가 해당 이름을 금지하면 중단하고 아니면 리스크로 보고한다.
5. 열린 리뷰 요청이 없으면 Draft 생성 지원과 권한을 확인하고 `새 Draft` 경로를 선택한다. 정확히 하나의 열린 Draft가 있으면 조회·본문 편집 권한을 확인하고 `기존 Draft` 경로를 선택해 그 target branch를 base로 사용한다.
6. 기존 Draft의 source repository가 push할 `origin`과 같고 source branch가 현재 branch인지 확인한다. 같은 branch 이름의 다른 fork이거나 `origin` push가 Draft head를 갱신하지 않으면 중단한다.
7. 열린 요청이 일반 PR/MR이거나 둘 이상이면 수정 대상을 추측하지 않고 중단한다. 기존 Draft의 target이 기여 규칙과 충돌해도 중단한다.

선택한 `새 Draft` 또는 `기존 Draft + ID/IID` 경로는 이 실행 동안 고정한다. 기존 Draft가 사라지거나 갱신에 실패해도 새 Draft 생성으로 전환하지 않는다.

## 2. 범위 결정

base에 없는 커밋과 현재 worktree 변경을 합쳐 `리뷰 범위`로 정한다.

1. worktree가 dirty면 `<base>...HEAD`와 staged·unstaged·untracked를 함께 본다.
2. worktree가 깨끗하고 branch가 base보다 앞서면 `<base>...HEAD`를 본다.
3. 둘 다 비어 있으면 빈 커밋을 만들지 않고 `출항할 변경 없음`으로 종료한다.
4. 사용자 작업과 무관한 변경이 섞였고 안전하게 분리할 수 없으면 중단한다.

이 범위는 이후 모든 단계에서 고정한다. 실행 중 사용자나 다른 프로세스가 범위 파일을 바꾸면 자동 병합하거나 덮지 않는다.

## 3. 다듬기

1. 리뷰 범위에 대응하는 빠른 test, lint, typecheck, build와 실행 비용을 찾고 가능한 baseline을 기록한다.
2. 전체 리뷰 범위를 지정해 `trim --go`를 실행하고 동작 보존 근거 1·2등급 변경만 반영한다.
3. trim이 끝난 최종 코드에 같은 리뷰 범위를 지정해 `annotate --go`를 실행하고 낮은 위험도의 숨은 이유·제약만 남긴다.
4. baseline과 같은 검증을 다시 실행한다. 실패하면 커밋과 원격 작업으로 넘어가지 않는다.

### 새 테스트 판정

base에는 없고 리뷰 범위에서 추가된 테스트만 아래 기준으로 본다.

- 구현 분기를 그대로 재현함
- mock이 반환하도록 설정한 값을 다시 확인함
- 기존 테스트와 같은 실패를 중복해서 잡음
- 실제 입력 계약상 도달하지 않는 사례만 다룸

독립적인 회귀 방지 가치가 없다는 근거를 코드와 기존 테스트로 확인할 수 있으면 덜어내기 후보로 다룬다. 외부 계약, 과거 버그, 중요한 경계값을 고장 시 실제로 잡는 테스트와 base에 있던 assertion은 보존한다. 작성 주체를 삭제 근거로 삼지 않는다.

이 절은 `ship`이 `trim`에 전달하는 범위 제한 규칙이다. `trim`의 assertion 보호는 base에 있던 테스트에 그대로 적용하고, 리뷰 범위에서 새로 생긴 테스트만 위 근거로 삭제할 수 있다.

## 4. 커밋과 셀프 리뷰

1. 다듬기 뒤 dirty worktree가 있으면 `commit --go` 절차로 한 의도씩 커밋한다.
2. worktree가 깨끗하고 기존 커밋만 있으면 새 커밋이나 amend 없이 계속한다.
3. 커밋 뒤 worktree가 깨끗한지 확인하고 `<base>...HEAD` 범위를 다시 계산한다. 남은 변경이 있거나 base 대비 커밋이 없으면 중단한다.
4. 검증 결과를 tree에 귀속한다. commit hook 등으로 최종 tree가 검증한 tree와 달라졌으면 관련 검증을 다시 실행하고, 같으면 `mr` 단계에서 결과를 재사용한다.
5. 최종 범위를 다시 읽고 누락, 회귀, secret, 대량 삭제, 리뷰 불가능한 혼합 의도를 점검한다.
6. 심각한 문제는 push 전에 중단한다. 사소한 미해결 문제는 Draft 본문의 리스크에 공개한다.

## 5. 제목과 본문

`mr`의 제목·본문 규칙에 따라 push 전에 최종안을 완성한다.

- 기여 문서와 레포 템플릿을 우선하고, 없으면 최근 PR/MR 2~3개의 실제 본문 구조를 참고한다.
- 요약에는 결과와 이유를, 변경 사항에는 리뷰 가능한 의미 단위를 쓴다.
- 검증에는 실행 결과와 생략 이유를 구분한다.
- 리뷰 포인트는 1~3개로 좁히고 리스크가 낮아도 명시한다.
- `ship`이 만드는 요약·변경 사항·검증·리뷰 포인트·리스크는 `<!-- ship:managed:start -->`와 `<!-- ship:managed:end -->` 사이에 둔다. 새 Draft도 이 관리 블록을 포함해 이후 갱신 범위를 명확히 한다.
- 새 Draft 경로의 기본 호출은 제목과 전체 본문, 커밋 계획, 검증 계획, 리스크를 보여주고 `이대로 출항할까요?`로 끝낸다.
- 기존 Draft에 관리 블록이 정확히 하나 있으면 그 블록만 전체 리뷰 범위에 맞게 교체한다. 블록이 없으면 새 관리 블록을 본문 끝에 추가하고 기존 본문은 그대로 보존한다. marker가 중복되거나 짝이 맞지 않으면 자동 수정하지 않고 중단한다.
- 관리 블록 밖의 issue 링크·체크리스트·수동 안내와 사용자 작성 내용은 위치와 내용을 바꾸지 않는다. marker가 없던 본문에 오래된 요약이나 검증이 남으면 삭제하지 않고 계획의 리스크로 알린다.
- 기존 Draft의 제목은 기본적으로 보존한다. 제목 변경이 필요하면 이번 출항 범위에서 제외하고 리스크로 보고한다.
- 기존 Draft 경로의 기본 호출은 Draft URL, 커밋 계획, 본문에서 바꿀 절, 본문 diff와 수정 후 전체 본문을 보여주고 `이대로 기존 Draft를 갱신할까요?`로 끝낸다. 새 Draft 생성은 생략한다고 명시한다.
- 현재 본문과 수정안이 같으면 `본문 변경 없음`으로 표시하고 원격 본문 수정을 생략한다. 사용자 작성 내용을 안전하게 보존하며 모순을 해소할 수 없으면 계획 단계에서 중단한다.
- `--go`는 외부 변경 직전에 같은 내용을 사용자에게 보여주되 확인을 기다리지 않고 계속한다.

## 6. 출항

1. push 직전에 현재 branch의 열린 PR/MR을 다시 조회한다. `새 Draft` 경로에서 요청이 생겼거나 `기존 Draft` 경로에서 정확히 하나인 같은 ID의 요청이 open·Draft가 아니거나 source repository와 branch·target·본문이 사전 점검과 달라졌으면 원격을 바꾸지 않고 중단한다.
2. `git push -u origin <현재-branch>`로 현재 branch만 push한다.
3. push 뒤 현재 branch의 열린 PR/MR을 다시 조회한다.
4. `새 Draft` 경로에서는 예상하지 못한 리뷰 요청이 생겼으면 중복 생성하지 않고 URL과 완료된 push를 보고한 뒤 중단한다. 여전히 없을 때만 준비한 제목과 본문으로 Draft를 생성한다.
5. `기존 Draft` 경로에서는 열린 요청이 정확히 하나이며 같은 ID·open·Draft이고 source repository와 branch·target이 같은지, remote head SHA가 push한 local `HEAD`와 같은지 확인한다. 원격 본문이 사전 점검에서 읽은 본문과 달라졌으면 다른 사람의 수정을 덮지 않고 push까지만 보고한 뒤 중단한다.
6. 기존 Draft 본문 수정안이 있으면 고정한 target repository/project와 ID에 파일로 본문만 전달한다. GitHub는 `gh pr edit <number> -R <target-repository> --body-file <body-file>`, GitLab은 `glab api -X PUT "projects/<encoded-target-project>/merge_requests/<iid>" -F "description=@<body-file>" --silent`를 사용한다. 제목·Draft 상태·리뷰어·라벨은 유지한다.
7. 생성 또는 갱신 뒤 URL·Draft 상태·source·target·remote head SHA와 본문 반영 여부를 다시 확인한다.
8. Draft를 보장할 수 없으면 일반 PR/MR로 대체하지 않는다. push가 거절되면 force push하지 않으며, 원격 단계가 실패하면 이미 완료된 commit·push 상태를 정확히 보고한다.

## 중단

다음 상황에서는 완료된 안전한 로컬 변경을 임의로 되돌리지 않고 현재 상태와 다음 행동을 보고한다.

- git 충돌, secret·credential·개인정보 정황
- base, 플랫폼, 인증 또는 해당 경로에 필요한 Draft 생성·본문 편집 기능을 확인할 수 없음
- default branch, 현재 branch의 열린 일반 PR/MR 또는 여러 열린 리뷰 요청
- 기존 Draft의 source repository가 `origin`과 다르거나 상태·source·target·본문·remote head가 실행 중 바뀌어 안전하게 갱신할 수 없음
- detached HEAD이거나 base가 같은 branch의 원격 추적 ref를 가리킴
- baseline 또는 최종 검증 실패 원인을 파악할 수 없음
- 심각한 셀프 리뷰 finding, 분리할 수 없는 무관한 변경
- submodule, 대형 바이너리, 원인 없는 생성물·lockfile, 무관한 대량 삭제
- 실행 중 리뷰 범위가 외부에서 바뀜

하위 단계가 자체 백업·복원을 제공하면 그 계약만 사용한다. 단계가 성공한 뒤 후속 단계에서 멈췄다면 사용자 변경을 보호하기 위해 전체 흐름을 자동 rollback하지 않는다.

## 보고

```text
출항 계획 | 출항 완료 | 출항 중단

범위
- base/head:
- 변경 요약:

정리
- trim:
- 제거한 저가치 테스트:
- annotate:

커밋
- <예정 message | hash message | 새 커밋 없음>

검증
- <명령>: <결과>
- 생략: <이유>

Draft PR/MR
- 동작: 새 Draft 생성 | 기존 Draft 본문 갱신
- 생성: 예정·완료 | 생략 (기존 Draft)
- 제목: <새 제목 | 기존 제목 유지>
- 본문: <전체 본문 | 변경 절과 body diff | 변경 없음>
- URL:

남은 리스크
- <내용 | 없음>
```

중단했으면 실행하지 않은 후속 단계와 이미 생긴 로컬·원격 상태를 함께 적는다.
