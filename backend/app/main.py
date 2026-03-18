"""
Context Bharat — FastAPI Backend
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import libraries, docs, keys, health, admin
from app.api.v1 import snippets, offline, cookbooks, sdkgen, testgen, openapigen, starters, workflows, features
from app.api.v1 import integrations, compliance, errors, community
from app.core.config import settings
from app.core.database import engine
from app.core.feature_flags import flags


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    flags.log_status()
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Context Bharat API",
    description="AI-ready documentation for Indian APIs and developer tools",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — allow MCP clients and frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(libraries.router, prefix="/v1")
app.include_router(docs.router, prefix="/v1")
app.include_router(keys.router, prefix="/v1")
# P0+P1: Developer Accelerators
app.include_router(snippets.router, prefix="/v1")
app.include_router(offline.router, prefix="/v1")
app.include_router(cookbooks.router, prefix="/v1")
app.include_router(sdkgen.router, prefix="/v1")
app.include_router(testgen.router, prefix="/v1")
app.include_router(openapigen.router, prefix="/v1")
app.include_router(starters.router, prefix="/v1")
app.include_router(workflows.router, prefix="/v1")
app.include_router(features.router, prefix="/v1")
# P2: Integrations & Community
app.include_router(integrations.router, prefix="/v1")
app.include_router(compliance.router, prefix="/v1")
app.include_router(errors.router, prefix="/v1")
app.include_router(community.router, prefix="/v1")
# Admin panel
app.include_router(admin.router, prefix="/v1")
