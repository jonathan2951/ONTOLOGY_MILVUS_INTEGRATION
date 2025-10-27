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
