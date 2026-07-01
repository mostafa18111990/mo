#!/bin/bash
set -euo pipefail

EMAIL="${1:?Usage: $0 <email> <password>}"
PASSWORD="${2:?}"

# Generate bcrypt hash using Python
HASH=$(python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('$PASSWORD'))")

PGPASSWORD="${POSTGRES_PASSWORD:?}" psql \
  -h "${POSTGRES_HOST:-localhost}" \
  -U "${POSTGRES_USER:-saas_admin}" \
  -d "${POSTGRES_DB:-saas_control}" \
  -c "INSERT INTO users (email, hashed_password, role, is_active)
      VALUES ('$EMAIL', '$HASH', 'super_admin', true)
      ON CONFLICT (email) DO UPDATE SET role='super_admin', hashed_password='$HASH';"

echo "Super admin $EMAIL created/updated."
