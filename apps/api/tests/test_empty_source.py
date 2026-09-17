from pathlib import Path

from app.analyzer import analyze_repository


def test_empty_source_file_is_reported_as_maintainability_finding(tmp_path: Path):
    (tmp_path / "empty.py").write_text("", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    dimension = result.dimensions["maintainability"]
    finding = next(item for item in dimension.findings if item.title == "Empty source files detected")

    assert result.files == 1
    assert result.languages["Python"] == 1
    assert finding.evidence == ["empty.py"]
    assert dimension.score == 99.0
