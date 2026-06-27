import os
import yaml
import logging
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def write_tenant_config(slug: str, subdomain: str):
    domain = settings.domain
    fqdn = f"{subdomain}.{domain}"
    config = {
        "http": {
            "routers": {
                f"tenant-{slug}": {
                    "rule": f"Host(`{fqdn}`)",
                    "entrypoints": ["websecure"],
                    "tls": {"certResolver": "le"},
                    "service": f"tenant-{slug}",
                    "middlewares": ["security@file", "ratelimit@file", "compress@file"],
                }
            },
            "services": {
                f"tenant-{slug}": {
                    "loadBalancer": {
                        "servers": [{"url": f"http://odoo-{slug}:8069"}]
                    }
                }
            }
        }
    }
    path = os.path.join(settings.traefik_dynamic_dir, f"{slug}.yml")
    os.makedirs(settings.traefik_dynamic_dir, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    logger.info("Written Traefik config for %s → %s", slug, fqdn)


def remove_tenant_config(slug: str):
    path = os.path.join(settings.traefik_dynamic_dir, f"{slug}.yml")
    if os.path.exists(path):
        os.remove(path)
        logger.info("Removed Traefik config for %s", slug)
