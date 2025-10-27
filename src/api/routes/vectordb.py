from fastapi import APIRouter, HTTPException, status
from src.models.response_models import Entity, SearchEntity, ResponseEntities
from src.services.vectordb_service import (
    get_collection_dimension,
    get_entity,
    get_collection_from_database,
    search_query,
)
import logging

logger = logging.getLogger(__name__)

vectordb_router = APIRouter(
    prefix="/vectordb",
    tags=["Vector DB"],
)


@vectordb_router.get("/health", description="health check")
async def root() -> dict[str, str]:
    logger.info("Hello from vectordb router")
    return {"msg": "Hello from vectordb router"}


@vectordb_router.get("/collections", description="return all the collections")
async def get_collections() -> dict:
    logger.info(f"retrieving all collections")
    try:
        cols = await get_collection_from_database()
        logger.info(f"{cols=}")
        return {"collections": cols}
    except Exception as e:
        logger.error(f"Error in retrieving all collections from MilvusDB: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in retrieving all collections from MilvusDB",
        )


@vectordb_router.get(
    "/collection_dimension", description="return the collection number of entity"
)
async def get_number_entity() -> dict:
    logger.info(f"retrieving collection dimension")
    try:
        num_entities = await get_collection_dimension()
        logger.info(f"{num_entities=}")
        return num_entities
    except Exception as e:
        logger.error(f"Error in retrieving MilvusDB collection dimension: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error in retrieving MilvusDB collection dimension",
        )


@vectordb_router.post("/get_entity")
async def retrieve_entity(input: Entity):
    print(f"{input}")
    input_id = input.id
    logger.info(f"retrieving entity {input_id} from collection")
    try:
        entity = await get_entity(id=input_id)
        logger.info(f"{entity=}")
        return entity
    except Exception as e:
        logger.error(f"Error in retrieving entity {input_id} from collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in retrieving entity {input_id} from collection",
        )


@vectordb_router.post("/search_doc")
async def search_entity(input: SearchEntity) -> ResponseEntities:
    print(f"{input}")
    input_query = input.query
    input_top_k = input.top_k
    input_nprobe = input.nprobe
    logger.info(f"searching entity {input_query} from collection")
    try:
        entity = await search_query(
            query=input_query, top_k=input_top_k, nprobe=input_nprobe
        )
        logger.info(f"{entity=}")
        return {"responses": entity}
    except Exception as e:
        logger.error(f"Error in search entity {input_query} from collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in searching entity {input_query} from collection",
        )
