from pathlib import Path

from app.repository import build_context


def test_build_context_excludes_sensitive_files(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('safe')", encoding="utf-8")
    (tmp_path / ".env.staging").write_text("API_KEY=secret", encoding="utf-8")
    (tmp_path / ".envrc").write_text("export TOKEN=secret", encoding="utf-8")
    (tmp_path / ".npmrc").write_text("//registry.example/:_authToken=secret", encoding="utf-8")
    (tmp_path / ".git-credentials").write_text("https://user:secret@example.com", encoding="utf-8")
    (tmp_path / "id_rsa").write_text("PRIVATE KEY", encoding="utf-8")
    (tmp_path / "private.pem").write_text("PRIVATE KEY", encoding="utf-8")
    aws = tmp_path / ".aws"
    aws.mkdir()
    (aws / "credentials").write_text("aws_secret=secret", encoding="utf-8")

    context = build_context(str(tmp_path))

    assert "app.py" in context
    assert "API_KEY=secret" not in context
    assert "export TOKEN=secret" not in context
    assert "_authToken=secret" not in context
    assert "user:secret@example.com" not in context
    assert "PRIVATE KEY" not in context
    assert "aws_secret=secret" not in context


def test_build_context_does_not_follow_symlinked_directories(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "leaked.py").write_text("LEAKED_SECRET = 'do-not-ingest'", encoding="utf-8")

    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "app.py").write_text("print('safe')", encoding="utf-8")
    (repository / "linked").symlink_to(outside, target_is_directory=True)

    context = build_context(str(repository))

    assert "app.py" in context
    assert "leaked.py" not in context
    assert "do-not-ingest" not in context


def test_build_context_skips_binary_like_files(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('safe')", encoding="utf-8")
    (tmp_path / "binary.py").write_bytes(b"print('prefix')\x00PRIVATE_BINARY_DATA")

    context = build_context(str(tmp_path))

    assert "app.py" in context
    assert "binary.py" not in context
    assert "PRIVATE_BINARY_DATA" not in context


def test_build_context_skips_metadata_dirs_case_insensitively(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('safe')", encoding="utf-8")
    metadata = tmp_path / ".GIT"
    metadata.mkdir()
    (metadata / "config.py").write_text("SHOULD_NOT_BE_INGESTED = True", encoding="utf-8")

    context = build_context(str(tmp_path))

    assert "app.py" in context
    assert "config.py" not in context
    assert "SHOULD_NOT_BE_INGESTED" not in context


def test_build_context_skips_invalid_utf8_files(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('safe')", encoding="utf-8")
    (tmp_path / "invalid.py").write_bytes(b"print('prefix')\xffINVALID_UTF8_DATA")

    context = build_context(str(tmp_path))

    assert "app.py" in context
    assert "invalid.py" not in context
    assert "INVALID_UTF8_DATA" not in context


def test_build_context_respects_byte_limit_with_multibyte_text(tmp_path: Path) -> None:
    content = "print('😀' * 100)"
    (tmp_path / "unicode.py").write_text(content, encoding="utf-8")

    context = build_context(str(tmp_path), max_file_bytes=12)
    body = context.split("\n", 1)[1]

    assert len(body.encode("utf-8")) <= 12
    assert body == "print('😀'"
