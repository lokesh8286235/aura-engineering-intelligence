from pathlib import Path

from app.analyzer import analyze_repository


def test_test_detection_ignores_non_source_test_like_files(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "fixture.test.json").write_text('{"ok": true}\n', encoding="utf-8")
    (tmp_path / "notes.spec.md").write_text("# Fixture notes\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 3
    assert result.dimensions["testing"].score == 45.0
    assert result.dimensions["testing"].findings[0].severity == "high"
