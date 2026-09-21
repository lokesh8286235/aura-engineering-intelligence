from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_can_execute_with_its_model_and_language_definitions(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 2
    assert result.languages == {"Python": 1, "Markdown": 1}
    assert result.overall_score > 0
