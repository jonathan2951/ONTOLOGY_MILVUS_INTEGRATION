# ONTOLOGY_MILVUS_INTEGRATION
this code connects to a Milvus instance and performs semantic searches

# VectorDB API v0.0.0

A clean, organized FastAPI service that performs semantic searches to a Milvus DB vectorDB collection with proper separation of concerns and RESTful API design.

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   or 
   uv sync
   ```

2. **Set environment variables**:
   ```bash
   export MILVUS_CLIENT_URL
   export MILVUS_CLIENT_DATABASE
   export MILVUS_CLIENT_COLLECTION
   export OPENAI_API_KEY
   export OPENAI_BASE_URL
   export OPENAI_MODEL
   ```

3. **Run the API**:
   ```bash
   uv run uvicorn src.app:app --reload  
   or
   python -m src.app
   or
   uvicorn src.app:app --reload 
   ```

 - Requirements to run locally with a (local) mongo DB instance
   ```bash
   brew services start mongodb/brew/mongodb-community
   ```

## 🏗️ Code Structure

```bash
├── docker-compose.yml
├── Dockerfile
├── infra
│   └── helm
│       ├── Chart.yaml
│       ├── templates
│       │   ├── _helpers.tpl
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       └── values.yaml
├── pyproject.toml
├── README.md
├── scripts
│   ├── __init__.py
│   ├── column_data_feeder.py
│   └── table_data_feeder.py
├── src
│   ├── api
│   │   ├── __init__.py
│   │   ├── routes
│   │   │   ├── __init__.py
│   │   │   └── vectordb.py
│   │   └── routes.py
│   ├── app.py
│   ├── config
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── models
│   │   ├── health_models.py
│   │   └── response_models.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── openai_service.py
│   │   └── vectordb_service.py
│   └── startup.py
├── tests
│   ├── __init__.py
│   └── test.py
└── uv.lock
```

## Script to feed data dictionaries to vectorDB

- `script/table_data_feeder.py`

The idea is to convert the data from the JSON file (retrieved from GCS) into text.
This paragraph is then encoded to a vectorDB using `openai "text-embedding-3-small"` embedding model, which has a dimension of 1536

### `Table` data example

note: not all columns are shown here for simplicity
```python
{'catalog': 'group_iii',
 'schema': 'silver',
 'table': 'group_iii_purchase_xlsx_g_3_p_order',
 'total_row_count': 16091,
 'columns': [{'column_name': 'Type',
   'column_type': 'string',
   'description': 'Type of order',
   'examples': ['Normal', 'Drop-Ship'],
   'number_of_rows': 16091,
   'null_rows': 0,
   'distinct_rows': 2},
  {'column_name': 'OrderNbr',
   'column_type': 'string',
   'description': 'Order number',
   'examples': ['PO0003954', 'PO0003953', 'PO0003952'],
   'number_of_rows': 16091,
   'null_rows': 0,
   'distinct_rows': 4517},
 ...],
 'description': "The 'group_iii_purchase_xlsx_g_3_p_order' table is owned by Group III and is sourced from an internal system. It covers data from various dates and contains information about purchase orders, including details such as order number, date, vendor, status, and quantities. This data is valuable for tracking purchase orders, analyzing vendor performance, and managing inventory levels.",
 'table_analysis': ["High cardinality in 'OrderNbr' and 'InventoryID' columns.",
  "Excessive nulls in 'PromisedOn'(0.19%) and 'ShipTo'(0.14%) columns."],
 'primary_key': ['OrderNbr', 'LineNbr'],
 'date_created': '2025-08-12 17:37:08'}
```

to 
```
table name:group_iii.silver.group_iii_purchase_xlsx_g_3_p_order
table description: The 'group_iii_purchase_xlsx_g_3_p_order' table is owned by Group III and is sourced from an internal system. It covers data from various dates and contains information about purchase orders, including details such as order number, date, vendor, status, and quantities. This data is valuable for tracking purchase orders, analyzing vendor performance, and managing inventory levels.
table analysis:High cardinality in 'OrderNbr' and 'InventoryID' columns.,Excessive nulls in 'PromisedOn'(0.19%) and 'ShipTo'(0.14%) columns.
columns available:Type,OrderNbr,Date,PromisedOn,Vendor,VendorName,Status,TotalOrderQty,OpenQuantity,CreatedBy,InventoryID,Description,Description_2,ShipTo,AccountName,OrderQty_2,QtyOnReceipts,ExtCost,UnitCost,LineNbr,BranchID,EntityType
```

### `column` data example
```python
{
    'catalog': 'group_iii',
    'schema': 'silver',
    'table': 'group_iii_purchase_xlsx_g_3_p_order',
    'total_row_count': 16091,
    'columns':
    [
        {
        'column_name': 'Type',
        'column_type': 'string',
        'description': 'Type of order',
        'examples': ['Normal', 'Drop-Ship'],
        'number_of_rows': 16091,
        'null_rows': 0,
        'distinct_rows': 2
        }
    ]
}
```

to text :
```
name: Type
type: string
description: Type of order
number_of_rows: 16091
examples: Normal,Drop-Ship
null_rows: 0
distinct_rows: 2
from table: group_iii.silver.group_iii_purchase_xlsx_g_3_p_order
```

### Procedure

1. retrieve data dictionaries from GCS
2. format each column for all tables
    - this results in 20651 columns and 760 tables
3. Create a `Milvus` Collection schema with 3 fields:
    - `id`: use as `PK`
    - `text`: the paragraph resulting from the formatting step
    - `embbedings`: the embedded text, i.e a 1536 array
4. add an index to the `embeddings` fields for fast retrieval. We use `COSINE` for semantic search

```py
index_params.add_index(
        field_name="embeddings",
        metric_type="COSINE",
        index_type="IVF_FLAT",
        index_name="vector_index",
        params={"nlist": 128},
    )
```
5. insert the data
Here we insert the data according the schema defined at step 3. Note that the fields in the data to insert should match the `Collection Schema`
```python
data_to_collection = [
        {
            "id": i,
            "embeddings": embeddings[i],
            "text": data_to_embed[i],
        }
        for i in range(len(data_to_embed))
    ]
```
6. flush the collection

After final entity is inserted, it is best to call flush to have no growing segments left in memory
- https://milvus.io/api-reference/pymilvus/v2.2.x/MilvusClient/Collection/flush().md
7. load the collection
6. test a semantic search
