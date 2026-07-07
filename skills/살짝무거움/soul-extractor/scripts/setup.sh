#!/usr/bin/env bash
# soul-extractor 런타임 데이터 디렉터리를 보장한다.
set -uo pipefail
base="${HOME}/.soul-extractor"
mkdir -p "$base/profiles"
echo "준비됨: $base/profiles"
