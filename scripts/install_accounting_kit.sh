#!/bin/bash
# Install base_accounting_kit on all active tenants or a specific one
set -euo pipefail

API_URL="${API_URL:-https://admin.myodoo.com/api}"
TOKEN="${TOKEN:?Set TOKEN env var}"
TENANT_ID="${1:-all}"

install_on_tenant() {
  local id=$1
  echo "Installing accounting kit on tenant $id..."
  docker exec "odoo-$(docker inspect --format='{{index .Config.Labels "saas.slug"}}' \
    $(docker ps -q --filter "label=saas.tenant_id=$id"))" \
    odoo -d "$(docker inspect --format='{{range .Config.Env}}{{if eq (index (split . "=") 0) "TENANT_DB_NAME"}}{{index (split . "=") 1}}{{end}}{{end}}' \
    $(docker ps -q --filter "label=saas.tenant_id=$id"))" \
    -i base_accounting_kit --stop-after-init 2>&1
  echo "Done tenant $id"
}

if [ "$TENANT_ID" = "all" ]; then
  echo "Installing on all active tenants..."
  for container in $(docker ps -q --filter "label=saas.tenant_id"); do
    TENANT=$(docker inspect --format='{{index .Config.Labels "saas.tenant_id"}}' "$container")
    DB=$(docker inspect --format='{{range .Config.Env}}{{println .}}{{end}}' "$container" | grep TENANT_DB_NAME | cut -d= -f2)
    SLUG=$(docker inspect --format='{{index .Config.Labels "saas.slug"}}' "$container")
    echo "Installing on $SLUG (DB: $DB)..."
    docker exec "$container" odoo -d "$DB" -i base_accounting_kit --stop-after-init
    echo "Done: $SLUG"
  done
else
  install_on_tenant "$TENANT_ID"
fi

echo "Accounting kit installation complete."
