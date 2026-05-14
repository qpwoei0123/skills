# Classification Rules

이 문서는 `scripts/classify.py`의 판단 기준을 설명한다.

## 대상 이슈

본문에 현재 orbit footer가 있는 이슈만 처리한다.

```text
<!-- orbit-fingerprint: pipeline:<repo>:<VIEW>:f-xxxxxxxx -->
```

legacy footer는 orbit publish migration에는 쓰지만 cleanup 자동 close 근거로는 쓰지 않는다.

## DUP

High confidence:

- 같은 fingerprint가 둘 이상이다.
- 같은 view, 같은 evidence file:line, 제목 token Jaccard가 0.85 이상이다.
- `known_findings[fingerprint].alias_of`가 존재한다.

정본은 가장 오래된 이슈다. 사본만 close 후보가 된다.

## BATCH

조건:

- 같은 view
- 14일 이내 발행
- evidence file을 하나 이상 공유
- module prefix가 같음

Confidence:

- 공유 파일 3개 이상: high
- 공유 파일 2개: medium
- 공유 파일 1개: low

BATCH는 close하지 않는다.

## RESOLVED

신호:

- evidence 파일이 현재 checkout에 없다.
- 이슈 번호를 참조한 merged PR이 있다.
- 관련 파일에 신규 test/spec이 추가되었다.

Confidence:

- evidence 부재 + merged PR 참조: high
- evidence 부재 또는 merged PR 참조 단독: medium
- test/spec 추가 단독: low

High만 close 후보가 된다.
