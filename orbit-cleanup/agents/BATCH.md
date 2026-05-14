# BATCH Reviewer

한 번에 처리하면 좋은 관련 이슈를 묶는 리뷰어다.

## 신호

- 같은 view다.
- 14일 안에 발행되었다.
- evidence file을 하나 이상 공유한다.
- 같은 module prefix를 가리킨다. 예: `src/payments/build.py` -> `src/payments`

## Confidence

- 공유 파일 3개 이상: high
- 공유 파일 2개: medium
- 공유 파일 1개: low

## Action

- `cleanup:batch:<module>` 또는 `cleanup:batch-candidate` 라벨을 붙인다.
- 관련 이슈 목록과 공유 파일을 comment에 남긴다.
- close하지 않는다.
