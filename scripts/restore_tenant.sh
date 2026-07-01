#!/bin/bash
set -euo pipefail

DUMP_FILE="${1:?Usage: $0 <dump_file> <db_name> <db_user>}"
DB_NAME="${2:?}"
DB_USER="${3:?}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"

echo "Restoring $DUMP_FILE to $DB_NAME on $DB_HOST..."
PGPASSWORD="${PGPASSWORD:?Set PGPASSWORD}" pg_restore \
  -h "$DB_HOST" -p "$DB_PORT" \
  -U "$DB_USER" -d "$DB_NAME" \
  --no-owner --role="$DB_USER" \
  -v "$DUMP_FILE"
echo "Restore complete."
