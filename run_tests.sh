#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

LOG_DIR="$ROOT_DIR/test_logs"
mkdir -p "$LOG_DIR"

TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
LOG_FILE="$LOG_DIR/run_tests_${TIMESTAMP}.log"
LATEST_LOG="$LOG_DIR/run_tests_latest.log"

exec > >(tee -a "$LOG_FILE") 2>&1

FAILED=0

for test_file in "$ROOT_DIR"/tests/test_*.py; do
  echo ""
  echo "🧪 Running ${test_file#$ROOT_DIR/}"
  if ! python "$test_file"; then
    FAILED=1
    echo "❌ Failed: ${test_file#$ROOT_DIR/}" >&2
  fi
done

if [[ $FAILED -ne 0 ]]; then
  echo "\n❌ One or more tests failed." >&2
  cp -f "$LOG_FILE" "$LATEST_LOG"
  exit 1
fi

echo "\n✅ All tests passed."

cp -f "$LOG_FILE" "$LATEST_LOG"
