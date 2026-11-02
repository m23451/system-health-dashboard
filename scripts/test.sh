#!/usr/bin/env bash
# Usage: smoke_test.sh <base_url>
set -euo pipefail
BASE_URL="${1:?Usage: smoke_test.sh <base_url>}"

for path in /health /version /metrics; do
  echo "Checking ${BASE_URL}${path}"
  curl -fsS --retry 5 --retry-delay 2 --retry-connrefused "${BASE_URL}${path}" > /dev/null
  echo "  OK"
done
echo "Smoke test passed for ${BASE_URL}"
