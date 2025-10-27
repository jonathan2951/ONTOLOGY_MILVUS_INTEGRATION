# Routes package
from .vectordb import vectordb_router

# Create main API router with v1 prefix
from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers with tenant and schema path parameters
api_router.include_router(vectordb_router)
