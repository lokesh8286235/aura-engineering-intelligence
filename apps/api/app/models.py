from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    repository: str = Field(min_length=1, description="Local repository path")
    max_files: int = Field(default=500, ge=1, le=10_000, strict=True)
    max_file_bytes: int = Field(default=512_000, ge=1_024, le=5_000_000, strict=True)

    @field_validator("repository")
    @classmethod
    def validate_repository(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("repository must not be blank")
        return value


class Finding(BaseModel):
    severity: str = Field(min_length=1)
    title: str = Field(min_length=1)
    detail: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)


class Dimension(BaseModel):
    score: float = Field(ge=0, le=100)
    findings: list[Finding] = Field(default_factory=list)

    @field_validator("score", mode="before")
    @classmethod
    def reject_boolean_score(cls, value: object) -> object:
        if isinstance(value, bool):
            raise ValueError("score must be a number, not a boolean")
        return value


class Analysis(BaseModel):
    repository: str = Field(min_length=1)
    files: int = Field(ge=0, strict=True)
    languages: dict[str, int]
    dependencies: list[str]
    dimensions: dict[str, Dimension]
    overall_score: float = Field(ge=0, le=100)
    generated_at: str = Field(min_length=1)

    @field_validator("repository")
    @classmethod
    def validate_repository(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("repository must not be blank")
        return value

    @field_validator("overall_score", mode="before")
    @classmethod
    def reject_boolean_overall_score(cls, value: object) -> object:
        if isinstance(value, bool):
            raise ValueError("overall_score must be a number, not a boolean")
        return value


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4_000)
    repository: str | None = None

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("question must contain at least 2 non-whitespace characters")
        return value

    @field_validator("repository")
    @classmethod
    def validate_repository(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("repository must not be blank")
        return value


class AskResponse(BaseModel):
    answer: str
    evidence: list[str]
    provider: str
