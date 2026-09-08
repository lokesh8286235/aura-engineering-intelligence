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
