from pathlib import Path

from app.analyzer import analyze_repository


def test_package_json_uses_declared_dependency_sections_only(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        '{\n'
        '  "scripts": {"build": "./scripts/build", "docs": "https://example.com/docs"},\n'
        '  "dependencies": {"react": "^19.0.0", "@scope/ui": "^1.0.0"},\n'
        '  "devDependencies": {"vitest": "^3.0.0"}\n'
        '}\n',
        encoding="utf-8",
    )

    result = analyze_repository(str(tmp_path))

    assert result.dependencies == ["@scope/ui", "react", "vitest"]
    assert "./scripts/build" not in result.dependencies
    assert "https://example.com/docs" not in result.dependencies


def test_pyproject_and_go_mod_dependencies_are_parsed_from_manifests(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        "dependencies = [\"httpx>=0.28\", \"pydantic\"]\n"
        "[tool.poetry.dependencies]\npython = \"^3.12\"\nrich = \"^13.0\"\n",
        encoding="utf-8",
    )
    (tmp_path / "go.mod").write_text(
        "module example.com/service\n\n"
        "go 1.24\n\n"
        "require (\n"
        "    github.com/stretchr/testify v1.9.0\n"
        "    golang.org/x/sync v0.15.0 // indirect\n"
        ")\n",
        encoding="utf-8",
    )

    result = analyze_repository(str(tmp_path))

    assert set(result.dependencies) == {
        "httpx",
        "pydantic",
        "rich",
        "github.com/stretchr/testify",
        "golang.org/x/sync",
    }
    assert "example.com/service" not in result.dependencies
