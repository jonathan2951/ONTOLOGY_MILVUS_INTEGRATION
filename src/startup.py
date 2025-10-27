from typing import Dict, Any
from pymilvus import AsyncMilvusClient
from openai import AsyncOpenAI
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class StartupManager:
    """
    Manages the startup process for the data observability API.
    """

    def __init__(self):
        self.milvus_client = None
        self.milvus_database = None
        self.milvus_collection = None
        self.openai_client = None
        self.openai_model = None
        self.startup_complete = False

    async def initialize_services(self) -> Dict[str, Any]:
        """Initialize all services in the correct order.

        Returns:
            Summary of startup process
        """
        try:
            await self._initialize_milvus_client()
            await self._initialize_openai_client()
            self.startup_complete = True
            logger.info("✅ Ontology Generation API initialization complete!")

            return {
                "status": "success",
                "message": "All services initialized successfully",
            }

        except Exception as e:
            logger.error(f"❌ Startup failed: {e}")
            raise

    async def _initialize_milvus_client(self) -> None:
        try:
            self.milvus_client = AsyncMilvusClient(uri=settings.MILVUS_CLIENT_URL)
            self.milvus_database = settings.MILVUS_CLIENT_DATABASE
            self.milvus_collection = settings.MILVUS_CLIENT_COLLECTION

            # Test connection
            logger.info("trying to connect to Milvusdb ...")
            await self.milvus_client.get_server_version()
            logger.info("✅ Milvusdb connection established")

        except Exception as e:
            logger.error(f"❌ Milvusdb connection failed: {e}")
            raise

    async def _initialize_openai_client(self):
        try:
            self.openai_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )
            self.openai_model = settings.OPENAI_MODEL
            logger.info("✅ openai connection established")
        except Exception as e:
            logger.error(f"❌ openai connection failed: {e}")
            raise

    async def shutdown_services(self) -> None:
        """
        Shutdown all services.
        """
        logger.info("🔄 Shutting down Ontology Generation API...")

        # Close mongodb connection if it exists
        if hasattr(self, "milvus_client") and self.milvus_client is not None:
            try:
                await self.milvus_client.close()
            except Exception as e:
                logger.warning(f"⚠️  Error closing MilvusDB connection: {e}")

        # Close mongodb connection if it exists
        if hasattr(self, "openai_client") and self.openai_client is not None:
            try:
                await self.openai_client.close()
            except Exception as e:
                logger.warning(f"⚠️  Error closing openai client: {e}")


# Global startup manager instance
startup_manager = StartupManager()
