# AURA — Autonomous Engineering Intelligence

> **A production-oriented engineering intelligence platform that turns a software repository into an explainable model of architecture, dependencies, and engineering health.**

AURA is an independent systems project focused on a hard problem: giving engineers useful repository-level answers while keeping the analysis bounded, deterministic where possible, and grounded in repository evidence.

## The problem

Large codebases contain architecture knowledge implicitly—in files, imports, tests, configuration, documentation, and conventions. AURA makes those signals queryable instead of relying on a model to guess the structure.

## Architecture

```text
                         ┌─────────────────────────┐
                         │       Next.js UI        │
                         │ health / repository UX  │
                         └────────────┬────────────┘
                                      │ HTTP
                         ┌────────────▼────────────┐
                         │       FastAPI API       │
                         │ analyze · health · ask  │
                         └───────┬─────────┬───────┘
                                 │         │
                    ┌────────────▼───┐ ┌──▼────────────────┐
                    │ Repository     │ │ Intelligence      │
                    │ Analyzer       │ │ / provider layer  │
                    └───────┬────────┘ └───────────────────┘
                            │
                    ┌───────▼────────┐
                    │ Evidence model │
                    │ + dimensions   │
                    └────────────────┘
```

## What is implemented

- **Multi-language repository analysis** — Python, TypeScript/JavaScript, Java, Go, and common configuration/documentation files.
- **Dependency extraction** — Python imports and package/module signals are collected into a bounded dependency inventory.
- **Engineering health model** — testing, documentation, configuration, and maintainability dimensions are scored independently.
- **Explainable findings** — dimensions contain findings and evidence rather than an opaque aggregate alone.
- **Bounded ingestion** — configurable file-count and file-size limits protect analysis from pathological repositories.
- **Security-aware traversal** — symlink traversal is rejected and common credential/configuration artifacts are excluded.
- **Typed API** — FastAPI request/response models define the service contract.
- **Provider isolation** — model-assisted answers sit behind a replaceable provider interface.
- **Next.js + TypeScript dashboard foundation** for presenting repository intelligence.

## Engineering decisions

| Decision | Rationale |
|---|---|
| Deterministic repository analysis first | Establish a debuggable source of truth before model inference. |
| Evidence attached to findings | Engineers can inspect why a score or risk exists. |
| Bounded file ingestion | Prevent resource-heavy or pathological repository scans. |
| Sensitive-file exclusion | Avoid feeding common credentials/config secrets into analysis. |
| Provider abstraction | Keep AI integration replaceable and testable. |
| Versioned API contracts | Make future ingestion and intelligence layers easier to evolve. |

## Security boundary

The analyzer skips unsupported, binary, oversized, sensitive, generated, dependency, and symlinked paths before they enter the analysis set. API limits currently allow up to **10,000 files** and **5 MB per file**, with lower defaults for normal requests.

This is deliberately defense-in-depth: input limits, path filtering, deterministic traversal, and provider isolation reduce the amount of untrusted repository data that can reach downstream reasoning.

## API

### `GET /v1/health`

Returns service health and version information.

### `POST /v1/analyze`

```json
{
  "repository": "/workspace/example",
  "max_files": 500,
  "max_file_bytes": 512000
}
```

### `POST /v1/ask`

Accepts an engineering question and can build repository context before passing it to the configured provider.

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

## Engineering loop

```text
Repository
   ↓
Bounded ingestion
   ↓
Deterministic evidence
   ↓
Health / architecture signals
   ↓
Optional retrieval + model reasoning
   ↓
Answer with evidence
   ↓
Evaluate and improve
```

The core design principle is simple: **AI should explain engineering evidence, not replace it.**

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
