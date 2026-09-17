import pytest
from pydantic import ValidationError

from app.models import Analysis, AnalyzeRequest, AskRequest, AskResponse, Dimension, Finding


def test_finding_evidence_lists_are_not_shared():
    first = Finding(severity="low", title="A", detail="A")
    second = Finding(severity="low", title="B", detail="B")

    first.evidence.append("file.py:1")

    assert first.evidence == ["file.py:1"]
    assert second.evidence == []


def test_finding_normalizes_text_and_evidence():
    finding = Finding(
        severity="  medium  ",
        title="  Missing test  ",
        detail="  Add coverage  ",
        evidence=["  app.py:10  ", "tests/test_app.py:20"],
    )

    assert finding.severity == "medium"
    assert finding.title == "Missing test"
    assert finding.detail == "Add coverage"
    assert finding.evidence == ["app.py:10", "tests/test_app.py:20"]


def test_finding_rejects_blank_text_and_evidence():
    with pytest.raises(ValidationError, match="finding text fields must not be blank"):
        Finding(severity="   ", title="Title", detail="Detail")

    with pytest.raises(ValidationError, match="finding text fields must not be blank"):
        Finding(severity="low", title="   ", detail="Detail")

    with pytest.raises(ValidationError, match="finding text fields must not be blank"):
        Finding(severity="low", title="Title", detail="   ")

    with pytest.raises(ValidationError, match="finding evidence must not contain blank values"):
        Finding(severity="low", title="Title", detail="Detail", evidence=["   "])


def test_dimension_findings_lists_are_not_shared():
    first = Dimension(score=90)
    second = Dimension(score=80)

    first.findings.append(Finding(severity="medium", title="A", detail="A"))

    assert len(first.findings) == 1
    assert second.findings == []


def test_dimension_rejects_boolean_score():
    with pytest.raises(ValidationError, match="score must be a number, not a boolean"):
        Dimension(score=True)


def test_analyze_request_enforces_file_limits():
    request = AnalyzeRequest(repository="/workspace", max_files=10, max_file_bytes=2048)

    assert request.max_files == 10
    assert request.max_file_bytes == 2048

    with pytest.raises(ValidationError):
        AnalyzeRequest(repository="/workspace", max_files=0)

    with pytest.raises(ValidationError):
        AnalyzeRequest(repository="/workspace", max_file_bytes=512)


def test_analyze_request_rejects_boolean_resource_limits():
    with pytest.raises(ValidationError):
        AnalyzeRequest(repository="/workspace", max_files=True)

    with pytest.raises(ValidationError):
        AnalyzeRequest(repository="/workspace", max_file_bytes=False)


def test_analyze_request_strips_repository_path():
    request = AnalyzeRequest(repository="  /workspace/project  ")

    assert request.repository == "/workspace/project"

    with pytest.raises(ValidationError, match="repository must not be blank"):
        AnalyzeRequest(repository="   ")


def test_ask_request_normalizes_optional_repository_path():
    request = AskRequest(question="What changed?", repository="  /workspace/project  ")

    assert request.repository == "/workspace/project"
    assert AskRequest(question="What changed?").repository is None

    with pytest.raises(ValidationError, match="repository must not be blank"):
        AskRequest(question="What changed?", repository="   ")


def test_ask_request_normalizes_and_rejects_blank_questions():
    request = AskRequest(question="  What changed?  ")

    assert request.question == "What changed?"

    with pytest.raises(ValidationError, match="question must contain at least 2 non-whitespace characters"):
        AskRequest(question="   ")

    with pytest.raises(ValidationError, match="question must contain at least 2 non-whitespace characters"):
        AskRequest(question=" x ")


def test_ask_request_enforces_question_length():
    request = AskRequest(question="What changed?")

    assert request.question == "What changed?"
    assert request.repository is None

    with pytest.raises(ValidationError):
        AskRequest(question="x")


def test_ask_response_normalizes_text_and_evidence():
    response = AskResponse(
        answer="  Architecture is healthy.  ",
        evidence=["  app.py:10  ", "tests/test_app.py:20"],
        provider="  claude  ",
    )

    assert response.answer == "Architecture is healthy."
    assert response.evidence == ["app.py:10", "tests/test_app.py:20"]
    assert response.provider == "claude"


def test_ask_response_rejects_blank_text_and_evidence():
    with pytest.raises(ValidationError, match="response text fields must not be blank"):
        AskResponse(answer="   ", evidence=[], provider="claude")

    with pytest.raises(ValidationError, match="response text fields must not be blank"):
        AskResponse(answer="Answer", evidence=[], provider="   ")

    with pytest.raises(ValidationError, match="response evidence must not contain blank values"):
        AskResponse(answer="Answer", evidence=["   "], provider="claude")


def test_analysis_normalizes_repository_path():
    analysis = Analysis(
        repository="  /workspace/project  ",
        files=0,
        languages={},
        dependencies=[],
        dimensions={},
        overall_score=0,
        generated_at="2026-09-09T00:00:00Z",
    )

    assert analysis.repository == "/workspace/project"

    with pytest.raises(ValidationError, match="repository must not be blank"):
        Analysis(
            repository="   ",
            files=0,
            languages={},
            dependencies=[],
            dimensions={},
            overall_score=0,
            generated_at="2026-09-09T00:00:00Z",
        )


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
            dimensions={},
            dependencies=[],
            overall_score=50,
            generated_at="2026-09-09T00:00:00Z",
        )

    with pytest.raises(ValidationError):
        Analysis(
            repository="/workspace",
            files=1,
            languages={},
            dimensions={},
            dependencies=[],
            overall_score=101,
            generated_at="2026-09-09T00:00:00Z",
        )


def test_analysis_rejects_boolean_file_count():
    with pytest.raises(ValidationError):
        Analysis(
            repository="/workspace",
            files=True,
            languages={},
            dependencies=[],
            dimensions={},
            overall_score=50,
            generated_at="2026-09-09T00:00:00Z",
        )


def test_analysis_rejects_boolean_overall_score():
    with pytest.raises(ValidationError, match="overall_score must be a number, not a boolean"):
        Analysis(
            repository="/workspace",
            files=0,
            languages={},
            dependencies=[],
            dimensions={},
            overall_score=True,
            generated_at="2026-09-09T00:00:00Z",
        )


def test_analysis_normalizes_language_names():
    analysis = Analysis(
        repository="/workspace",
        files=1,
        languages={"  Python  ": 10},
        dependencies=[],
        dimensions={},
        overall_score=100,
        generated_at="2026-09-09T00:00:00Z",
    )

    assert analysis.languages == {"Python": 10}


def test_analysis_rejects_invalid_language_counts():
    base = dict(
        repository="/workspace",
        files=1,
        dependencies=[],
        dimensions={},
        overall_score=100,
        generated_at="2026-09-09T00:00:00Z",
    )

    with pytest.raises(ValidationError):
        Analysis(**base, languages={"Python": -1})

    with pytest.raises(ValidationError):
        Analysis(**base, languages={"Python": True})

    with pytest.raises(ValidationError):
        Analysis(**base, languages={"   ": 1})


def test_analysis_rejects_duplicate_normalized_language_names():
    base = dict(
        repository="/workspace",
        files=1,
        dependencies=[],
        dimensions={},
        overall_score=100,
        generated_at="2026-09-09T00:00:00Z",
    )

    with pytest.raises(ValidationError, match="language names must be unique after trimming"):
        Analysis(**base, languages={"Python": 10, " Python ": 5})


def test_analysis_normalizes_dependencies():
    analysis = Analysis(
        repository="/workspace",
        files=1,
        languages={},
        dependencies=["  fastapi  ", "pydantic"],
        dimensions={},
        overall_score=100,
        generated_at="2026-09-09T00:00:00Z",
    )

    assert analysis.dependencies == ["fastapi", "pydantic"]


def test_analysis_rejects_blank_or_duplicate_dependencies():
    base = dict(
        repository="/workspace",
        files=1,
        languages={},
        dimensions={},
        overall_score=100,
        generated_at="2026-09-09T00:00:00Z",
    )

    with pytest.raises(ValidationError, match="dependencies must not contain blank values"):
        Analysis(**base, dependencies=["fastapi", "   "])

    with pytest.raises(ValidationError, match="dependencies must be unique after trimming"):
        Analysis(**base, dependencies=["fastapi", " fastapi "])


def test_analyzer_rejects_boolean_resource_limits(tmp_path: Path):
    with pytest.raises(ValueError, match="max_files must be between 1 and 10000"):
        analyze_repository(str(tmp_path), max_files=True)

    with pytest.raises(ValueError, match="max_file_bytes must be between 1 and 5000000"):
        analyze_repository(str(tmp_path), max_file_bytes=False)
