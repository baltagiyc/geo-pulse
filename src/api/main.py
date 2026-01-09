"""FastAPI application main file."""

from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.routes import debug, health

load_dotenv()

app = FastAPI(
    title="GEO Pulse API",
    description="API for GEO (Generative Engine Optimization) brand auditing",
    version="0.1.0",
)

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(debug.router, prefix="/api")
