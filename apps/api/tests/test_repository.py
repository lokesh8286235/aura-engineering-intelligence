from pathlib import Path

from app.repository import build_context


def test_build_context_excludes_sensitive_files(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('safe')", encoding="utf-8")
    (tmp_path / ".env.staging").write_text("API_KEY=secret", encoding="utf-8")
    (tmp_path / "private.pem").write_text("PRIVATE KEY", encoding="utf-8")
    aws = tmp_path / ".aws"
    aws.mkdir()
    (aws / "credentials").write_text("aws_secret=secret", encoding="utf-8")

    context = build_context(str(tmp_path))

    assert "app.py" in context
    assert "API_KEY=secret" not in context
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
