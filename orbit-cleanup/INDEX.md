# orbit-cleanup Index

## 실행 파일

- `scripts/cleanup_issue.py`: list, classify, label, comment, close, memory update 실행기
- `scripts/classify.py`: DUP/BATCH/RESOLVED 판별 로직
- `scripts/memory_bridge.py`: orbit memory와 cleanup-log 갱신
- `scripts/test_cleanup_issue.py`: 회귀 테스트

## Agent 지침

- `agents/orchestrator.md`: 분류 결과를 action plan으로 병합하는 리드 cleaner
- `agents/DUP.md`: 중복 판별 검토
- `agents/BATCH.md`: 묶음 후보 검토
- `agents/RESOLVED.md`: 이미 해결된 이슈 검토

## References

- `references/classification-rules.md`: 분류별 신호와 confidence 기준
- `references/action-matrix.md`: 분류, confidence, action 매핑
- `references/safety-rules.md`: close 전 safety gate
- `references/comment-templates.md`: 정형 comment 템플릿
- `references/memory-schema.md`: memory 갱신 스키마
