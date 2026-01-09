"""FastAPI application main file."""

from fastapi import FastAPI

from src.api.routes import health

app = FastAPI(
    title="GEO Pulse API",
    description="API for GEO (Generative Engine Optimization) brand auditing",
    version="0.1.0",
)

# Include routers
app.include_router(health.router)
