# AURA — Autonomous Engineering Intelligence

A production-oriented engineering intelligence platform that turns a software repository into a living, queryable model of architecture, dependencies, risks, and operational health.

## First release

- **FastAPI** service with typed request/response models
- Repository analysis for Python, TypeScript/JavaScript, Java, Go, and common config files
- Dependency extraction and architecture metrics
- Deterministic engineering health scoring with explainable findings
- Provider-agnostic intelligence interface
- **Next.js + TypeScript** dashboard starter
- Docker Compose for local development
- CI for backend tests and frontend validation

## Architecture

```text
                         ┌─────────────────────────┐
                         │       Next.js UI        │
                         │  repo health / insights │
                         └────────────┬────────────┘
                                      │ HTTP
                         ┌────────────▼────────────┐
                         │       FastAPI API       │
                         │ analysis · health · ask │
                         └───────┬─────────┬───────┘
                                 │         │
                    ┌────────────▼───┐ ┌──▼────────────────┐
                    │ Repository     │ │ Intelligence      │
                    │ Analyzer       │ │ / provider layer  │
                    └───────┬────────┘ └───────────────────┘
                            │
                    ┌───────▼────────┐
                    │ Graph + metrics│
                    │ deterministic   │
                    └────────────────┘
```

## Quick start

### API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs`.

### Web

```bash
cd apps/web
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

## API

`POST /v1/analyze`

```json
{
  "repository": "/workspace/example",
  "max_files": 500,
  "max_file_bytes": 512000
}
```

The analyzer requires both limits to be positive. The API model accepts `max_files` from 1 to 5,000 and `max_file_bytes` from 1,024 to 5,000,000 bytes. Unsupported extensions, symlinks, ignored directories, oversized files, and files detected as binary are skipped before analysis. File traversal is deterministic so scan-limit results are reproducible.

`GET /v1/health` returns service health. `POST /v1/ask` provides a provider-agnostic engineering question interface.

## Design principles

1. **Evidence before inference.** Metrics are computed from repository artifacts, not invented by an LLM.
2. **Provider isolation.** Model calls live behind a narrow interface so the core platform is testable without an API key.
3. **Explainable scores.** Every health dimension has findings and evidence.
4. **Incremental evolution.** Analyzer contracts are compatible with future GitHub ingestion, embeddings, knowledge graphs, agents, evaluations, and observability.
5. **Security by default.** The API applies file-count and file-size limits and refuses symlink traversal.

## Roadmap

- GitHub App ingestion and webhook-driven re-indexing
- PostgreSQL + pgvector retrieval
- Code symbol graph and architecture drift detection
- PR risk analysis
- Debug / security / performance / test agents
- OpenTelemetry traces and evaluation datasets
- Multi-tenant authentication and RBAC
