#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000/api/v1}"
FILE_PATH="${1:-/path/to/file.mp3}"

# 1) Upload
UPLOAD_RES=$(curl -s -F "file=@${FILE_PATH}" "${BASE_URL}/upload")
ID=$(echo "$UPLOAD_RES" | sed -E 's/.*"id":"?([^",}]+).*/\1/')

# 2) Transcript
curl -s "${BASE_URL}/transcript/${ID}"

# 3) Lead
curl -s -X POST "${BASE_URL}/lead" -H "Content-Type: application/json" -d "{\"id\":\"${ID}\",\"lead\":\"Sample lead...\"}"

# 4) Article
curl -s -X POST "${BASE_URL}/article" -H "Content-Type: application/json" -d "{\"id\":\"${ID}\"}"

# 5) Get article
curl -s "${BASE_URL}/article/${ID}"
