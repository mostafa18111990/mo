from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from .config import get_settings
from .core.logging import setup_logging
from .api import auth, tenants, plans, billing, admin, monitoring, webhooks, sectors

setup_logging()
settings = get_settings()

app = FastAPI(
    title="Odoo SaaS Control Panel",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://{settings.admin_domain}",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["tenants"])
app.include_router(plans.router, prefix="/api/plans", tags=["plans"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(sectors.router, prefix="/api/sectors", tags=["sectors"])

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
