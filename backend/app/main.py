from fastapi import FastAPI

from app.api import tools
from app.api import pricing as pricing_api
from app.api import overlap as overlap_api
from app.api import negotiation as negotiation_api

from app.db import Base, engine
from app.models import pricing as pricing_model


# Create database tables if they don't already exist
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(title="SaaSOptima")


# Register API routes
app.include_router(tools.router)
app.include_router(pricing_api.router)
app.include_router(overlap_api.router)
app.include_router(negotiation_api.router)


# Health check
@app.get("/api/health")
def health_check():
    return {"status": "ok"}