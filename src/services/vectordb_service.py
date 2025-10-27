from src.startup import startup_manager
from src.services.openai_service import search_doc
import logging

logger = logging.getLogger(__name__)


async def get_collection_from_database() -> list[str]:
    """returns all collections"""
    cols = await startup_manager.milvus_client.list_collections()
    return cols


async def get_collection_dimension():
    """returns the MilvusDB collection number of entities"""
    stats = await startup_manager.milvus_client.get_collection_stats(
        startup_manager.milvus_collection
    )
    return stats


async def get_entity(id: int):
    """returns the MilvusDB collection number of entities"""
    # Example: ID(s) you want to retrieve
    print(f"{id=}")
    result = await startup_manager.milvus_client.get(
        collection_name=startup_manager.milvus_collection, ids=[id]
    )
    return result


async def search_query(query: str, top_k: int, nprobe: int):
    """perform semantic search"""
    try:
        res = await search_doc(query=query, top_k=top_k, nprobe=nprobe)
        return res
    except Exception as e:
        logger.info(f"An error occurred when searching: {str(e)}")
        raise
