#!/bin/bash
set -euo pipefail

API_URL="${API_URL:-https://admin.myodoo.com/api}"
TOKEN="${TOKEN:?Set TOKEN env var}"
TENANT_ID="${1:?Usage: $0 <tenant_id>}"

curl -sS -X POST "$API_URL/tenants/$TENANT_ID/action" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"backup"}' \
  | python3 -m json.tool

echo "Backup queued for tenant $TENANT_ID"
