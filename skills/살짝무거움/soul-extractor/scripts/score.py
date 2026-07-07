#!/usr/bin/env python3
"""문체 점수표 항목 점수를 받아 총점과 등급을 재현 가능하게 계산한다.

완성도 항목 합과 일치도 항목 합은 모두 100점 만점이라 총점이 곧 백분율이다.
사용 예:
  python3 score.py completeness 16 14 24 8 15
  python3 score.py match 17 16 18 17 8 8
"""
import sys

GRADE = [
    (90, "바로 변환 가능"),
    (75, "사용 가능, 일부 어색함 가능"),
    (60, "짧은 글만 권장"),
    (0, "샘플 추가 요청"),
]


def main(argv):
    if len(argv) < 2 or argv[0] not in {"completeness", "match"}:
        print("usage: score.py {completeness|match} <항목점수>...", file=sys.stderr)
        return 2
    kind = argv[0]
    try:
        scores = [int(x) for x in argv[1:]]
    except ValueError:
        print("[error] 항목 점수는 정수여야 합니다.", file=sys.stderr)
        return 2
    total = sum(scores)
    if kind == "completeness":
        label = next(text for cut, text in GRADE if total >= cut)
        print(f"프로필 완성도: {total}% — {label}")
    else:
        print(f"스타일 일치도: {total}%")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
