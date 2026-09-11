# 기존 Draft 본문 갱신

현재 branch에 열린 Draft가 정확히 하나 있을 때 읽는다. 생성 경로로 전환하지 않고 같은 요청의 본문만 갱신한다.

## 대상 고정

사전 점검에서 다음을 기록한다.

- 대상 repository/project와 PR 번호 또는 MR IID, URL
- open·Draft 상태, source repository와 branch, target branch
- remote head SHA, 제목, 원본 본문

source repository가 실제 push할 저장소와 같고 source branch가 현재 branch인지 확인한다. 같은 branch 이름의 다른 fork이거나 push가 해당 Draft head를 갱신하지 않는 구조라면 중단한다. target branch가 사용자 지시나 기여 규칙과 충돌해도 먼저 해소한다.

조회와 본문 편집에 필요한 CLI/API 및 인증이 있는지 확인한다. 기존 Draft의 제목·상태·리뷰어·라벨은 변경하지 않는다.

## 본문 준비

- `<!-- ship:managed:start -->`와 `<!-- ship:managed:end -->`가 정확히 한 쌍이면 그 사이만 전체 리뷰 범위에 맞게 교체한다.
- 두 marker가 모두 없으면 새 관리 블록을 원본 본문 끝에 추가한다. 원본 내용은 그대로 보존한다.
- marker가 중복되거나 짝이 맞지 않으면 자동 수정하지 않는다.
- 관리 블록 밖의 issue 링크·체크리스트·수동 안내·사용자 작성 내용은 위치와 내용을 보존한다.
- 이전 본문에 낡은 설명이 남아 관리 블록과 충돌하면 먼저 그 차이를 드러낸다. 사용자 내용을 보존하면서 해결할 수 없는 모순은 자동 갱신하지 않는다.
- 현재 본문과 수정안이 같으면 본문 쓰기를 생략한다.

원격 변경 전에 Draft URL, 본문에서 바뀌는 내용과 수정 후 본문을 준비한다. 계획 요청이면 body diff와 결과를 보여주고 끝낸다. 실행 요청이면 핵심 변경을 알린 뒤 계속한다.

## Push와 갱신

1. push 직전에 같은 source/head의 열린 요청을 다시 조회한다. 정확히 하나의 같은 ID이고 open·Draft인지, source repository·branch·target·remote head SHA·본문이 snapshot과 같은지 확인한다. 달라졌으면 원격 변경을 멈춘다.
2. CLI 인증을 사용할 수 있는 HTTPS 경로로 확인한 저장소의 현재 branch만 push한다. 거절되면 force push하지 않는다.
3. push 후 같은 ID·open·Draft·source·target과 remote head SHA를 확인한다. SHA는 push한 로컬 HEAD와 같아야 한다.
4. 원격 본문이 snapshot과 다르면 다른 사람의 수정을 덮지 않고 완료된 push까지만 보고한다.
5. 수정안이 있으면 고정한 repository/project와 ID에 파일로 본문만 전달한다.

```bash
gh pr edit <number> -R <target-repository> --body-file <body-file>
glab api -X PUT "projects/<encoded-target-project>/merge_requests/<iid>" -F "description=@<body-file>" --silent
```

6. URL·Draft 상태·source·target·remote head SHA와 준비한 본문 반영을 다시 확인한다. 실패하면 이미 완료된 상태와 갱신하지 못한 내용을 보고한다.

기존 요청이 사라지거나 권한·상태·대상이 달라지면 새 요청을 생성하거나 다른 요청을 수정하지 않는다.
