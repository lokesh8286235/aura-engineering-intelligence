from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import analyze_repository
from .models import Analysis, AnalyzeRequest, AskRequest, AskResponse
from .providers import LocalProvider
from .repository import build_context

app = FastAPI(title="AURA Engineering Intelligence API", version="0.2.0")


def _cors_origins() -> list[str]:
    """Return configured browser origins, rejecting wildcard credentials access."""
    raw_origins = os.getenv("AURA_CORS_ORIGINS", "http://localhost:3000")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    if "*" in origins:
        raise ValueError("AURA_CORS_ORIGINS must list specific origins; '*' is not allowed with credentials")
    return origins or ["http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
provider = LocalProvider()

@app.get("/v1/health")
def health(response: Response) -> dict[str, str]:
    """Report service health without allowing intermediaries to cache it."""
    response.headers["Cache-Control"] = "no-store"
    return {"status": "ok", "service": "aura-api", "version": "0.2.0"}

@app.post("/v1/analyze", response_model=Analysis)
def analyze(request: AnalyzeRequest) -> Analysis:
    try:
        return analyze_repository(request.repository, request.max_files, request.max_file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/v1/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        context = build_context(request.repository) if request.repository else ""
        result = provider.answer(request.question, context)
        return AskResponse(answer=result.text, evidence=result.evidence, provider=result.provider)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
