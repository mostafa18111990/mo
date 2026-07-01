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

  # الموديولات الأساسية دائماً + وحدة العلامة التجارية لضبط بيانات الشركة
  BASE_MODULES="base,web,mail,saas_tenant_branding"

  # موديولات القطاع من env var (بدون base_accounting_kit لأنه يثبت آخراً)
  SECTOR_MODULES="${TENANT_MODULES:-account}"
  # احذف base_accounting_kit من القائمة الأولى
  FIRST_PHASE=$(echo "${SECTOR_MODULES}" | tr ',' '\n' | grep -v 'base_accounting_kit' | tr '\n' ',' | sed 's/,$//')

  # المرحلة الأولى: الموديولات الأساسية + موديولات القطاع
  ALL_FIRST="${BASE_MODULES},${FIRST_PHASE}"
  echo "Installing modules (phase 1): ${ALL_FIRST}"
  odoo --config=/etc/odoo/odoo.conf \
    --database="${TENANT_DB_NAME}" \
    --init="${ALL_FIRST}" \
    --without-demo=all \
    --stop-after-init

  # المرحلة الثانية: base_accounting_kit (يحتاج account مثبتاً أولاً)
  echo "Installing accounting kit (phase 2)..."
  odoo --config=/etc/odoo/odoo.conf \
    --database="${TENANT_DB_NAME}" \
    --init=base_accounting_kit \
    --without-demo=all \
    --stop-after-init

  echo "All modules installed successfully."
fi

exec odoo --config=/etc/odoo/odoo.conf "$@"
