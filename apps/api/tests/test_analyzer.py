from pathlib import Path

from app.analyzer import analyze_repository


def test_analyze_repository(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("import json\n\ndef hello():\n    return 'ok'\n", encoding="utf-8")
    (tmp_path / "test_main.py").write_text("def test_hello():\n    assert True\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert result.files == 2
    assert result.languages["Python"] == 2
    assert "json" in result.dependencies
    assert result.overall_score > 0


def test_test_detection_does_not_match_unrelated_substrings(tmp_path: Path) -> None:
    (tmp_path / "contest.py").write_text("value = 1\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert result.dimensions["testing"].score == 45.0
    assert result.dimensions["testing"].findings[0].severity == "high"


def test_test_detection_supports_conventional_spec_and_test_names(tmp_path: Path) -> None:
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "parser_spec.py").write_text("def parser_spec(): pass\n", encoding="utf-8")
    (tmp_path / "test.py").write_text("def test_root(): pass\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert result.dimensions["testing"].findings[0].severity == "info"
    assert "test_ratio=0.67" in result.dimensions["testing"].findings[0].evidence
