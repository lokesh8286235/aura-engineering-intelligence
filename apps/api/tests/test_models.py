import pytest
from pydantic import ValidationError

from app.models import Analysis, AnalyzeRequest, AskRequest, Dimension, Finding


def test_finding_evidence_lists_are_not_shared():
    first = Finding(severity="low", title="A", detail="A")
    second = Finding(severity="low", title="B", detail="B")

    first.evidence.append("file.py:1")

    assert first.evidence == ["file.py:1"]
    assert second.evidence == []


def test_dimension_findings_lists_are_not_shared():
    first = Dimension(score=90)
    second = Dimension(score=80)

    first.findings.append(Finding(severity="medium", title="A", detail="A"))

    assert len(first.findings) == 1
    assert second.findings == []


def test_analyze_request_enforces_file_limits():
    request = AnalyzeRequest(repository="/workspace", max_files=10, max_file_bytes=2048)

    assert request.max_files == 10
    assert request.max_file_bytes == 2048

    with pytest.raises(ValidationError):
        AnalyzeRequest(repository="/workspace", max_files=0)

    with pytest.raises(ValidationError):
        AnalyzeRequest(repository="/workspace", max_file_bytes=512)


def test_ask_request_enforces_question_length():
    request = AskRequest(question="What changed?")

    assert request.question == "What changed?"
    assert request.repository is None

    with pytest.raises(ValidationError):
        AskRequest(question="x")


def test_analysis_scores_and_counts_stay_within_contract():
    dimension = Dimension(score=100)
    analysis = Analysis(
        repository="/workspace",
        files=0,
        languages={},
        dependencies=[],
        dimensions={"architecture": dimension},
        overall_score=0,
        generated_at="2026-09-09T00:00:00Z",
    )

    assert analysis.files == 0
    assert analysis.overall_score == 0

    with pytest.raises(ValidationError):
        Dimension(score=101)

    with pytest.raises(ValidationError):
        Dimension(score=-1)

    with pytest.raises(ValidationError):
        Analysis(
            repository="/workspace",
            files=-1,
            languages={},
            dependencies=[],
            dimensions={},
            overall_score=50,
            generated_at="2026-09-09T00:00:00Z",
        )

    with pytest.raises(ValidationError):
        Analysis(
            repository="/workspace",
            files=1,
            languages={},
            dependencies=[],
            dimensions={},
            overall_score=101,
            generated_at="2026-09-09T00:00:00Z",
        )
