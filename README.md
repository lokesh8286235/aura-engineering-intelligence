# AURA — Autonomous Engineering Intelligence

> **Architecture intelligence from source code: dependencies, structure, health, and evidence.**

AURA is an independent systems project focused on a narrower question than generic repository analysis:

> **Can software architecture be reconstructed from repository evidence well enough to make engineering structure queryable?**

The current implementation establishes the analysis foundation. More autonomous reasoning is deliberately roadmap work, not something this README pretends is already solved.

## The problem

Architecture knowledge is usually implicit in files, imports, tests, configuration, documentation, and conventions. AURA extracts those structural signals into an explainable model rather than asking a language model to guess the architecture.

```text
Source tree
    │
    ▼
Bounded ingestion
    │
    ├── language inventory
    ├── dependency signals
    ├── test / documentation signals
    └── configuration signals
    │
    ▼
Architecture + health model
    │
    ▼
Evidence-backed findings
    │
    └──────► optional provider / repository Q&A
```

## What is actually implemented

- Multi-language repository inventory covering Python, TypeScript/JavaScript, Java, Go, and common configuration/documentation files.
- Dependency extraction for Python imports and package/module signals.
- Independent engineering-health dimensions for testing, documentation, configuration, and maintainability.
- Explainable findings with evidence instead of an opaque aggregate score.
- Bounded ingestion with configurable file-count and file-size limits.
- Security-aware traversal that rejects symlinks and excludes common credential/configuration artifacts.
- Typed FastAPI request/response contracts.
- Next.js + TypeScript dashboard foundation.
- Provider abstraction for model-assisted repository questions.

## Architecture

```text
                         ┌──────────────────────┐
                         │      Next.js UI      │
                         │ repository / health  │
                         └──────────┬───────────┘
                                    │ HTTP
                         ┌──────────▼───────────┐
                         │      FastAPI API     │
                         │ analyze · ask · health│
                         └───────┬───────┬───────┘
                                 │       │
                    ┌────────────▼──┐ ┌─▼────────────────┐
                    │ Repository    │ │ Provider layer   │
                    │ analyzer      │ │ optional AI      │
                    └──────┬────────┘ └──────────────────┘
                           │
                    ┌──────▼────────┐
                    │ Evidence +    │
                    │ health model  │
                    └───────────────┘
```

## Security boundary

The analyzer and repository-context builder filter unsupported, binary, oversized, sensitive, generated, dependency, and symlinked paths before they enter the analysis set. API limits currently allow up to **10,000 files** and **5 MB per file**, with lower defaults for normal requests.

The intent is defense in depth: bounded inputs, path filtering, deterministic traversal, and provider isolation reduce the amount of untrusted repository data that can reach downstream reasoning.

## API

### `GET /v1/health`

Returns service health and version information. Responses are marked `Cache-Control: no-store` so monitoring clients and intermediaries do not reuse stale health results.

### `POST /v1/analyze`

```json
{
  "repository": "/workspace/example",
  "max_files": 500,
  "max_file_bytes": 512000
}
```

### `POST /v1/ask`

Accepts an engineering question, builds repository context, and can pass that context to the configured provider.

## Quick start

### API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

For a deployed frontend, configure allowed browser origins with `AURA_CORS_ORIGINS` as a comma-separated list. It defaults to `http://localhost:3000` for local development.

```bash
export AURA_CORS_ORIGINS="https://app.example.com,https://staging.example.com"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

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

## Engineering principle

```text
Structure first
      ↓
Evidence second
      ↓
Reasoning third
      ↓
Automation last
```

AI should explain repository evidence, not replace the source of truth.

## Roadmap

- [x] Multi-language repository inventory
- [x] Dependency extraction
- [x] Explainable health dimensions
- [x] Bounded and security-aware ingestion
- [x] FastAPI + Next.js foundation
- [ ] Symbol-level architecture graph
- [ ] Architecture drift detection
- [ ] PR risk and change-impact analysis
- [ ] Hybrid retrieval and reranking
- [ ] Repository investigation agents
- [ ] OpenTelemetry instrumentation
- [ ] Versioned AI evaluation datasets
- [ ] Production deployment hardening

## Status

**Active independent build.** Current work prioritizes structural analysis, security boundaries, evaluation, and explainability before adding more autonomous behavior.

## License

MIT
