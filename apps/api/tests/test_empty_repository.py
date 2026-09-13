from pathlib import Path

from app.analyzer import analyze_repository


def test_empty_repository_is_reported_as_unanalyzable(tmp_path: Path) -> None:
    result = analyze_repository(str(tmp_path))

    assert result.files == 0
    assert result.languages == {}
    assert result.dependencies == []
    assert result.overall_score == 0.0
    assert all(dimension.score == 0.0 for dimension in result.dimensions.values())
    assert all(dimension.findings[0].severity == "high" for dimension in result.dimensions.values())
    assert all("files=0" in dimension.findings[0].evidence for dimension in result.dimensions.values())
