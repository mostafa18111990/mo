#!/bin/bash
set -euo pipefail

API_URL="${API_URL:-https://admin.myodoo.com/api}"
TOKEN="${TOKEN:?Set TOKEN env var}"
SLUG="${1:?Usage: $0 <slug> <display_name> <plan_code>}"
DISPLAY_NAME="${2:?}"
PLAN_CODE="${3:-starter}"

curl -sS -X POST "$API_URL/tenants" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"slug\":\"$SLUG\",\"display_name\":\"$DISPLAY_NAME\",\"plan_code\":\"$PLAN_CODE\"}" \
  | python3 -m json.tool
