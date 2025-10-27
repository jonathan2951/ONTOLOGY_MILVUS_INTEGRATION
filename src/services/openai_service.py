from src.startup import startup_manager
import logging

logger = logging.getLogger(__name__)


async def embed_text(texts, model="text-embedding-3-small"):
    """
    Convert raw text into embedding vectors using OpenAI embeddings.
    """
    if isinstance(texts, str):
        texts = [texts]  # Convert single string to list for consistency

    response = await startup_manager.openai_client.embeddings.create(
        input=texts, model=model
    )
    return [item.embedding for item in response.data]


async def search_doc(query: str, top_k: int, nprobe: int):
    """ "semantic search for document in collection"""
    logger.info(f"document: {query}")
    query_vector = await embed_text(texts=query)

    search_params = {"metric_type": "COSINE", "params": {"nprobe": nprobe}}

    # Single vector search
    res = await startup_manager.milvus_client.search(
        collection_name=startup_manager.milvus_collection,  # Replace with the actual name of your collection
        # Replace with your query vector
        data=query_vector,
        limit=top_k,
        search_params=search_params,  # Search parameters
        output_fields=["text"],
    )

    # print(f"{res=}")

    print(res[0])

    return res[0]
