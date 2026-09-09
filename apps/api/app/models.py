from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    repository: str = Field(min_length=1, description="Local repository path")
    max_files: int = Field(default=500, ge=1, le=5000)
    max_file_bytes: int = Field(default=512_000, ge=1_024, le=5_000_000)


class Finding(BaseModel):
    severity: str = Field(min_length=1)
    title: str = Field(min_length=1)
    detail: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)


class Dimension(BaseModel):
    score: float = Field(ge=0, le=100)
    findings: list[Finding] = Field(default_factory=list)


class Analysis(BaseModel):
    repository: str = Field(min_length=1)
    files: int = Field(ge=0)
    languages: dict[str, int]
    dependencies: list[str]
    dimensions: dict[str, Dimension]
    overall_score: float = Field(ge=0, le=100)
    generated_at: str = Field(min_length=1)


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4_000)
    repository: str | None = None


class AskResponse(BaseModel):
    answer: str
    evidence: list[str]
    provider: str
