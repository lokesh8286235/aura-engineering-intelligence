from pathlib import Path

from app.analyzer import analyze_repository


def test_requirements_manifest_contributes_python_dependencies(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text(
        "fastapi==0.115.0\n"
        "pydantic>=2.0\n"
        "pytest; python_version >= '3.12'\n"
        "uvicorn[standard] @ https://example.com/packages/uvicorn.whl\n"
        "--index-url https://example.com/simple\n"
        "# comment\n",
        encoding="utf-8",
    )

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.languages == {"Requirements": 1}
    assert result.dependencies == ["fastapi", "pydantic", "pytest", "uvicorn[standard]"]
