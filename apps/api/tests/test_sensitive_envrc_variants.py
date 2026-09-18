from pathlib import Path

from app.analyzer import analyze_repository


def test_envrc_variants_are_excluded_from_analysis(tmp_path: Path) -> None:
    (tmp_path / ".envrc.local").write_text("export API_TOKEN=should-not-be-read\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.languages == {"Python": 1}
    assert result.dependencies == []
