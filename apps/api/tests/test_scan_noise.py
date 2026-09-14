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


def test_toml_credential_files_are_skipped(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "credentials.toml").write_text('token = "secret"\n', encoding="utf-8")
    (tmp_path / "secrets.toml").write_text('api_key = "secret"\n', encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.languages == {"Python": 1}


def test_environment_variants_and_key_material_are_skipped(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / ".env.staging").write_text("API_KEY=secret\n", encoding="utf-8")
    (tmp_path / "server.pem").write_text("PRIVATE KEY\n", encoding="utf-8")
    (tmp_path / "server.key").write_text("PRIVATE KEY\n", encoding="utf-8")
    aws_dir = tmp_path / ".aws"
    aws_dir.mkdir()
    (aws_dir / "credentials").write_text("[default]\naws_secret_access_key=secret\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.languages == {"Python": 1}
