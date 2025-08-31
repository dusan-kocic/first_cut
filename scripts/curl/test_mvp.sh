#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${BASE_URL:-http://localhost:8000/api/v1}"
FILE_PATH="${1:-/path/to/file.mp3}"
UPLOAD_RES=$(curl -s -F "file=@${FILE_PATH}" "${BASE_URL}/upload")
ID=$(echo "$UPLOAD_RES" | sed -E 's/.*"id":"?([^",}]+).*/\1/')
curl -s "${BASE_URL}/transcript/${ID}" > /dev/null
curl -s -X POST "${BASE_URL}/lead" -H "Content-Type: application/json" -d "{\"id\":\"${ID}\",\"lead\":\"Sample lead...\"}" > /dev/null
POST_ARTICLE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE_URL}/article" -H "Content-Type: application/json" -d "{\"id\":\"${ID}\"}")
if [ "$POST_ARTICLE" != "202" ]; then echo "Expected 202 from POST /article, got $POST_ARTICLE"; exit 1; fi
ATTEMPTS=30
SLEEP_SECS=2
for i in $(seq 1 $ATTEMPTS); do
  RES=$(curl -s "${BASE_URL}/article/${ID}")
  STATUS=$(echo "$RES" | sed -E 's/.*"status":"?([^",}]+).*/\1/')
  if [ "$STATUS" = "article_ready" ]; then echo "$RES"; exit 0; fi
  sleep $SLEEP_SECS
done
echo "Article not ready after $((ATTEMPTS*SLEEP_SECS))s"
exit 1
