from pydantic import BaseModel, Field, ConfigDict


class HealthResponse(BaseModel):
    """Schema for basic health check response."""

    status: str = Field(description="Overall health status", examples=["ready"])
    services_ready: bool = Field(
        description="Services are ready or not", examples=[True]
    )
    timestamp: str = Field(
        description="ISO timestamp of the health check",
        examples=["2024-09-16T16:30:00Z"],
    )
    version: str = Field(description="API version", examples=["1.0.0"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ready",
                "services_ready": True,
                "timestamp": "2024-09-16T16:30:00Z",
                "version": "1.0.0",
            }
        }
    )
