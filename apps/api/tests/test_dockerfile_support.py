from pathlib import Path

from app.analyzer import analyze_repository


def test_dockerfile_variants_are_analyzed(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
    (tmp_path / "Dockerfile.prod").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    (tmp_path / "dockerfile.dev").write_text("FROM node:22\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 0 + 3
    assert result.languages["Dockerfile"] == 3
