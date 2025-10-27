from dotenv import load_dotenv

# Load environment variables from .env file BEFORE any other imports, especially settings
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
import logging
from datetime import datetime, timezone
from .api.routes import api_router
from .config.settings import settings
from .startup import startup_manager
from .models.health_models import HealthResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan of the app"""
    await startup_manager.initialize_services()
    yield
    await startup_manager.shutdown_services()


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)


# Health check endpoint
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "message": "VectorDB semantic search API is running",
        "version": settings.API_VERSION,
    }


# MongoDB client readiness
@app.get("/readiness", description="Milvus client readiness")
async def readiness(response: Response) -> dict:
    try:
        response = await startup_manager.milvus_client.get_server_version()
        logger.info("Milvus connection successful!")
        response_data = {
            "status": "ready",
            "services_ready": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.API_VERSION,
            "milvus_version": response,
        }
        return response_data
    except Exception:
        logger.info("Server not available")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = {
            "status": "error",
            "services_ready": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.API_VERSION,
        }
        return HealthResponse(**response_data)


# Include the API router with all v1 endpoints
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    # Validate settings before starting
    settings.validate()
    print("here")
    uvicorn.run("src.app:app", host=settings.HOST, port=settings.PORT, reload=True)
