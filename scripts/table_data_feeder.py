from google.cloud import storage
from google.oauth2.service_account import Credentials
from pymilvus import MilvusClient
from pymilvus import DataType
import os
import json
from openai import OpenAI

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed_text(texts, model="text-embedding-3-small"):
    """
    Convert raw text into embedding vectors using OpenAI embeddings.
    """
    if isinstance(texts, str):
        texts = [texts]  # Convert single string to list for consistency

    response = openai_client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]


def get_embedding(text: str, model: str = "text-embedding-3-small"):
    """convert string to vector embedding

    Args:
        text (str): _description_
        model (str, optional): _description_. Defaults to "text-embedding-3-small".

    Returns:
        _type_: _description_
    """
    resp = openai_client.embeddings.create(model=model, input=text)
    return resp.data[0].embedding


def download_all_files_from_bucket(bucket_name: str, folder_prefix: str) -> list[dict]:
    """Downloads all data dictionaries files from GCS bucket

    Args:
        bucket_name (_type_): _description_

    Returns:
        list[dict]: _description_
    """
    # GCS credentials
    credentials = Credentials.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    folder_prefix = "tenants/group_iii/silver/data_dict"
    storage_client = storage.Client(credentials=credentials)
    buckets = storage_client.list_buckets()

    for bucket in buckets:
        print(bucket.name)

    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=folder_prefix)
    blob_list = list(blobs)

    print(f"Total blobs found: {len(blob_list)}")

    blobs = []

    for blob in blob_list:
        try:
            content = blob.download_as_string()
            # Decode the string and parse it as JSON
            json_data = json.loads(content)
            blobs.append(json_data)
        except Exception as e:
            print(f"failed to download {blob.name} with {e}")

    return blobs


def make_column_context(inputs: list[dict]) -> list[str]:
    """parse data dictionaries and format column data

    Args:
        inputs (list[dict]): _description_

    Returns:
        str: _description_
    """
    res = []
    for datadict in inputs:
        for col in datadict.get("columns"):
            examples = col.get("examples")
            vals = ",".join([str(x) if x is not None else "None" for x in examples])
            ctx: str = ""
            ctx += f"""
            name: {col["column_name"]}
            type: {col["column_type"]}
            description: {col["description"]}
            number_of_rows: {col["number_of_rows"]}
            examples: {vals}
            null_rows: {col["null_rows"]}
            distinct_rows: {col["distinct_rows"]}
            from table: {datadict["catalog"]}.{datadict["schema"]}.{datadict["table"]}
            """
            res.append(ctx)
    return res


if __name__ == "__main__":
    bucket_name = "data-platform-intermediate-outputs"

    # load data dictionaries
    folder_prefix = "tenants/group_iii/silver/data_dict"
    inputs = download_all_files_from_bucket(
        bucket_name=bucket_name, folder_prefix=folder_prefix
    )
    print("All files downloaded successfully!")

    data_to_embed = make_column_context(inputs=inputs["data"])

    # convert to vector embeddings
    embeddings = [get_embedding(data) for data in data_to_embed]

    # create a client
    client = MilvusClient(uri="http://localhost:19530")

    try:
        collections = client.list_collections()
        print(f"Successfully connected to Milvus. Collections: {collections}")
    except Exception as e:
        print(f"Failed to connect to Milvus or retrieve collections: {e}")

    collection_name = "data_dictionary_columns"

    # 1. create schema
    schema = MilvusClient.create_schema(
        auto_id=False,  # will create ID manually
        enable_dynamic_field=True,  # allows you to insert entities with flexible, evolving structures
    )

    # 2. Add fields to schema
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    # schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True)
    # auto_id = True means we don't have to add it by hand when inserting into collection
    # https://milvus.io/docs/primary-field.md
    schema.add_field(
        field_name="embeddings", datatype=DataType.FLOAT_VECTOR, dim=1536
    )  # should be the same dimension of the embedding model
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)

    # 3. Create collection
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
    )

    # 4.1. Set up the index parameters
    index_params = MilvusClient.prepare_index_params()

    # 4.2. Add an index on the vector field.
    index_params.add_index(
        field_name="embeddings",
        metric_type="COSINE",
        index_type="IVF_FLAT",
        index_name="vector_index",
        params={"nlist": 128},
    )

    # 4.3. Create an index file
    client.create_index(
        collection_name=collection_name,
        index_params=index_params,
        sync=True,  # Whether to wait for index creation to complete before returning. Defaults to True.
    )

    # 5. inserting data
    data_to_collection = [
        {
            "id": i,
            "embeddings": embeddings[i],
            "text": data_to_embed[i],
        }
        for i in range(len(data_to_embed))
    ]

    print(
        "Data has",
        len(data_to_collection),
        "entities, each with fields: ",
        data_to_collection[0].keys(),
    )
    print("Vector dim:", len(data_to_collection[0]["embeddings"]))

    res = client.insert(collection_name="data_dictionary", data=data_to_collection)

    # After final entity is inserted, it is best to call flush to have no growing segments left in memory
    # https://milvus.io/api-reference/pymilvus/v2.2.x/MilvusClient/Collection/flush().md
    client.flush(collection_name=collection_name)

    # load the collection to make it available
    client.load_collection(collection_name=collection_name)

    # testing
    query: str = "OrderNbr"
    query_vector = embed_text(texts=query)

    # search parameters should use the same parameters as for when the index was creatied
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 50}}
    top_k = 5

    # Single vector search
    res = client.search(
        collection_name=collection_name,  # Replace with the actual name of your collection
        # Replace with your query vector
        data=query_vector,
        search_params=search_params,  # Search parameters
        limit=top_k,
        output_fields=["text"],  # only return the text, not the whole vector embeddings
    )

    for i, hits in enumerate(res):
        for hit in hits:
            print(f"entity: {hit.entity.get('text')}")
            print(f"distance: {hit.get('distance')}")
            print("####\n")
