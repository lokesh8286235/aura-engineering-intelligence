from datetime import datetime
from pathlib import Path

import pytest

from app.analyzer import analyze_repository


def test_analyze_repository(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("import json\n\ndef hello():\n    return 'ok'\n", encoding="utf-8")
    (tmp_path / "test_main.py").write_text("def test_hello():\n    assert True\n", encoding="utf-8")
    result = analyze_repository(str(tmp_path))
    assert result.files == 2
    assert result.languages["Python"] == 2
    assert "json" in result.dependencies
    assert result.overall_score > 0


def test_generated_at_is_utc_iso8601(tmp_path: Path) -> None:
    result = analyze_repository(str(tmp_path))

    timestamp = datetime.fromisoformat(result.generated_at)

    assert timestamp.tzinfo is not None
    assert timestamp.utcoffset().total_seconds() == 0


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


def test_file_scan_is_deterministic_when_max_files_limits_results(tmp_path: Path) -> None:
    (tmp_path / "z_module.py").write_text("value = 'z'\n", encoding="utf-8")
    (tmp_path / "a_module.py").write_text("value = 'a'\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path), max_files=1)

    assert result.files == 1
    assert result.languages == {"Python": 1}
    assert result.dimensions["maintainability"].findings[0].detail.endswith("across 1 files.")


def test_binary_files_do_not_consume_scan_limit(tmp_path: Path) -> None:
    (tmp_path / "a_binary.py").write_bytes(b"print('ok')\x00binary")
    (tmp_path / "b_source.py").write_text("value = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path), max_files=1)

    assert result.files == 1
    assert result.languages == {"Python": 1}
    assert result.dimensions["maintainability"].findings[0].detail.endswith("across 1 files.")


def test_analyzer_reads_each_candidate_file_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from app import analyzer

    (tmp_path / "a.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("value = 2\n", encoding="utf-8")
    original = analyzer._read_text
    calls: list[Path] = []

    def record_read(path: Path, max_bytes: int) -> str | None:
        calls.append(path)
        return original(path, max_bytes)

    monkeypatch.setattr(analyzer, "_read_text", record_read)

    result = analyze_repository(str(tmp_path))

    assert result.files == 2
    assert calls == [tmp_path / "a.py", tmp_path / "b.py"]


def test_analyze_repository_rejects_non_positive_limits(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="max_files must be greater than zero"):
        analyze_repository(str(tmp_path), max_files=0)
    with pytest.raises(ValueError, match="max_file_bytes must be greater than zero"):
        analyze_repository(str(tmp_path), max_file_bytes=0)


def test_analyze_repository_rejects_excessive_file_limit(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="max_files must be less than or equal to 10000"):
        analyze_repository(str(tmp_path), max_files=10_001)


def test_analyze_repository_rejects_excessive_file_size(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="max_file_bytes must be less than or equal to 5000000"):
        analyze_repository(str(tmp_path), max_file_bytes=5_000_001)


def test_file_that_grows_during_scan_is_excluded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from app import analyzer

    path = tmp_path / "app.py"
    path.write_text("x = 1\n", encoding="utf-8")
    original = analyzer._read_text

    def grow_then_read(target: Path, max_bytes: int) -> str | None:
        target.write_bytes(b"x" * (max_bytes + 1))
        return original(target, max_bytes)

    monkeypatch.setattr(analyzer, "_read_text", grow_then_read)

    result = analyze_repository(str(tmp_path))

    assert result.files == 0
    assert result.languages == {}


def test_file_that_becomes_binary_during_scan_is_excluded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from app import analyzer

    path = tmp_path / "app.py"
    path.write_text("x = 1\n", encoding="utf-8")
    original = analyzer._read_text

    def become_binary(target: Path, max_bytes: int) -> str | None:
        target.write_bytes(b"x = 1\x00binary")
        return original(target, max_bytes)

    monkeypatch.setattr(analyzer, "_read_text", become_binary)

    result = analyze_repository(str(tmp_path))

    assert result.files == 0
    assert result.languages == {}


def test_invalid_utf8_files_are_not_analyzed(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_bytes(b"x = 1\n\xff\xfe\xfa")

    result = analyze_repository(str(tmp_path))

    assert result.files == 0
    assert result.languages == {}


def test_ignored_directories_are_case_insensitive(tmp_path: Path) -> None:
    ignored = tmp_path / "Node_Modules"
    ignored.mkdir()
    (ignored / "dependency.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("value = 2\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.languages == {"Python": 1}


def test_dependency_manifest_detection_is_case_insensitive(tmp_path: Path) -> None:
    (tmp_path / "PACKAGE.JSON").write_text('{"dependencies": {"@scope/library": "^1.0.0"}}\n', encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert "@scope/library" in result.dependencies


def test_sensitive_credential_manifests_are_not_analyzed(tmp_path: Path) -> None:
    (tmp_path / "credentials.json").write_text('{"token": "secret"}\n', encoding="utf-8")
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.languages == {"Python": 1}
    assert "secret" not in result.dependencies
