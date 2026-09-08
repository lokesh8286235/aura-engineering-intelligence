from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelAnswer:
    text: str
    evidence: list[str]
    provider: str


class IntelligenceProvider(ABC):
    @abstractmethod
    def answer(self, question: str, context: str) -> ModelAnswer:
        raise NotImplementedError


class LocalProvider(IntelligenceProvider):
    """Deterministic provider used for development and tests."""

    def answer(self, question: str, context: str) -> ModelAnswer:
        evidence = [line for line in context.splitlines() if line.strip()][:5]
        return ModelAnswer(
            text=(f"I can analyze this engineering question once repository context is indexed. "
                  f"Question received: {question}"),
            evidence=evidence or ["No indexed repository evidence available."],
            provider="local",
        )
