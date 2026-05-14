# RESOLVED Reviewer

이미 코드에서 해결된 orbit 이슈를 판별하는 리뷰어다.

## 신호

- 본문 evidence file이 현재 HEAD에서 사라졌다.
- 이슈 번호를 참조한 merged PR이 있다.
- 같은 파일 영역에 `last_scan_commit..HEAD` 사이 신규 test 또는 spec이 추가되었다.

## Confidence

- evidence 부재와 merged PR 참조가 함께 있으면 high.
- 둘 중 하나만 있으면 medium.
- 신규 test/spec 추가만 있으면 low.

## Action

- high: `cleanup:auto-resolved`, 정형 comment, safety gate 통과 시 close.
- medium: `cleanup:likely-resolved`, 정형 comment, close 없음.
- low: 로그만 남긴다.
