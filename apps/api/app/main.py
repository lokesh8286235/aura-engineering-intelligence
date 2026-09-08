from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import analyze_repository
from .models import Analysis, AnalyzeRequest, AskRequest, AskResponse
from .providers import LocalProvider
from .repository import build_context

app = FastAPI(title="AURA Engineering Intelligence API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
provider = LocalProvider()

@app.get("/v1/health")
def health() -> dict[str, str]:
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
