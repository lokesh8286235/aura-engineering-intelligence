from pathlib import Path

from app.analyzer import analyze_repository


def test_generated_cache_and_coverage_directories_are_skipped(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")
    for dirname in (".cache", ".parcel-cache", ".tox", ".nox", "coverage", "htmlcov"):
        generated = tmp_path / dirname
        generated.mkdir()
        (generated / "generated.py").write_text("generated = True\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.languages == {"Python": 1}
