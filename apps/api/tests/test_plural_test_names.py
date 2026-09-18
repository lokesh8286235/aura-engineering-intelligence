from pathlib import Path

from app.analyzer import analyze_repository


def test_analyzer_detects_plural_test_and_spec_filenames(tmp_path: Path):
    (tmp_path / "integration_tests.py").write_text("def test_api(): pass\n", encoding="utf-8")
    (tmp_path / "api_specs.py").write_text("def test_contract(): pass\n", encoding="utf-8")
    (tmp_path / "production.py").write_text("x = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert not any(finding.title == "No test files detected" for finding in result.dimensions["testing"].findings)
