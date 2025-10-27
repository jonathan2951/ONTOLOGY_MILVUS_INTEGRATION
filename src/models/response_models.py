from pydantic import BaseModel, Field


class Entity(BaseModel):
    """model to hold an input ID for a Milvus Collection"""

    id: int = Field(description="the ID of the entity")


class SearchEntity(BaseModel):
    """model to hold a user query"""

    query: str = Field(description="the string of character to search")
    top_k: int = Field(
        default=3, description="the number of semantic search matches", ge=1, le=10
    )
    nprobe: int = Field(
        default=10, description="the nprobe params in the searhc parameters"
    )


class ResponseEntity(BaseModel):
    id: int = Field(description="the id")
    distance: float = Field(description="metric")
    entity: dict[str, str] = Field(description="the text output of the search")


class ResponseEntities(BaseModel):
    responses: list[ResponseEntity]
