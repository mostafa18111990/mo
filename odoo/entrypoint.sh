#!/bin/bash
set -e

# Wait for PostgreSQL
until pg_isready -h "${TENANT_DB_HOST}" -p "${TENANT_DB_PORT:-5432}" -U "${TENANT_DB_USER}"; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Render config from template
envsubst < /etc/odoo/odoo.conf.template > /etc/odoo/odoo.conf

# Detect first boot (empty database)
DB_EXISTS=$(psql "postgresql://${TENANT_DB_USER}:${TENANT_DB_PASSWORD}@${TENANT_DB_HOST}:${TENANT_DB_PORT:-5432}/${TENANT_DB_NAME}" \
  -tc "SELECT 1 FROM information_schema.tables WHERE table_name='ir_module_module'" 2>/dev/null | tr -d '[:space:]')

if [ "${DB_EXISTS}" != "1" ]; then
  echo "First boot: initializing database ${TENANT_DB_NAME}..."
  # Install base modules then accounting kit
  odoo --config=/etc/odoo/odoo.conf \
    --database="${TENANT_DB_NAME}" \
    --init=base,web,mail,account,account_accountant \
    --without-demo=all \
    --stop-after-init

  echo "Installing accounting kit..."
  exec odoo --config=/etc/odoo/odoo.conf \
    --database="${TENANT_DB_NAME}" \
    --init=base_accounting_kit \
    --without-demo=all \
    --stop-after-init
fi

exec odoo --config=/etc/odoo/odoo.conf "$@"
