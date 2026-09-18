from pathlib import Path

from app.analyzer import analyze_repository


def test_pascal_case_test_files_are_detected(tmp_path: Path) -> None:
    (tmp_path / "TestParser.py").write_text("def test_parse(): pass\n", encoding="utf-8")
    (tmp_path / "parser.py").write_text("def parse(): pass\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.dimensions["testing"].findings[0].severity == "info"
    assert result.dimensions["testing"].findings[0].evidence == ["test_ratio=0.50"]


def test_lowercase_words_starting_with_test_are_not_false_positives(tmp_path: Path) -> None:
    (tmp_path / "testing.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "contest.py").write_text("value = 2\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.dimensions["testing"].score == 45.0
    assert result.dimensions["testing"].findings[0].severity == "high"
