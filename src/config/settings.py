import os
from typing import Optional


class Settings:
    """Application settings"""

    # API Configuration
    API_TITLE: str = "Ontology API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for generating ontology data and metadata"

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # MongoDB Configuration (these should be set via environment variables)
    MILVUS_CLIENT_URL: Optional[str] = os.getenv("MILVUS_CLIENT_URL")
    MILVUS_CLIENT_DATABASE: Optional[str] = os.getenv("MILVUS_CLIENT_DATABASE")
    MILVUS_CLIENT_COLLECTION: Optional[str] = os.getenv("MILVUS_CLIENT_COLLECTION")

    # OpenAI Configuration
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: Optional[str] = os.getenv("OPENAI_MODEL_LARGE")

    @classmethod
    def validate(cls) -> None:
        """Validate required settings"""
        required_vars = [
            "MILVUS_CLIENT_URL",
            "MILVUS_CLIENT_DATABASE",
            "MILVUS_CLIENT_COLLECTION",
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
        ]

        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )


# Create settings instance
settings = Settings()
