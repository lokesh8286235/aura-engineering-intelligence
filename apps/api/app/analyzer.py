from __future__ import annotations

import ast
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .models import Analysis, Dimension, Finding

SUPPORTED = {".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".json", ".yaml", ".yml", ".toml"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "target", "__pycache__"}
LANGUAGES = {".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript", ".java": "Java", ".go": "Go", ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML"}


def _looks_binary(path: Path) -> bool:
    """Return True when the first 8 KiB contains a NUL byte."""
    try:
        with path.open("rb") as handle:
            return b"\x00" in handle.read(8192)
    except OSError:
        return True


def _files(root: Path, limit: int, max_bytes: int) -> list[Path]:
    found: list[Path] = []
    for current, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d.lower() not in SKIP_DIRS and not (Path(current) / d).is_symlink())
        for name in sorted(names):
            path = Path(current) / name
            if path.suffix.lower() not in SUPPORTED or path.is_symlink():
                continue
            try:
                if path.stat().st_size <= max_bytes and not _looks_binary(path):
                    found.append(path)
            except OSError:
                continue
            if len(found) >= limit:
                return found
    return found


def _is_test_file(path: Path) -> bool:
    """Identify conventional test/spec files without substring false positives."""
    parts = [part.lower() for part in path.parts]
    stem = path.stem.lower()
    return (
        any(part in {"test", "tests", "spec", "specs"} for part in parts)
        or stem in {"test", "spec"}
        or stem.startswith("test_")
        or stem.endswith("_test")
        or stem.startswith("spec_")
        or stem.endswith("_spec")
    )


def _python_imports(text: str) -> list[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    values: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            values.append(node.module.split(".")[0])
    return values


def _read_text(path: Path, max_bytes: int) -> str | None:
    """Read at most max_bytes, protecting against files growing after scanning."""
    try:
        with path.open("rb") as handle:
            data = handle.read(max_bytes + 1)
    except OSError:
        return None
    if len(data) > max_bytes or b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def analyze_repository(repository: str, max_files: int = 500, max_file_bytes: int = 512_000) -> Analysis:
    if max_files <= 0:
        raise ValueError("max_files must be greater than zero")
    if max_file_bytes <= 0:
        raise ValueError("max_file_bytes must be greater than zero")

    root = Path(repository).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError("repository must be an existing directory")

    paths = _files(root, max_files, max_file_bytes)
    languages = Counter()
    dependencies: Counter[str] = Counter()
    total_lines = 0
    test_files = 0
    docs_files = 0
    config_files = 0

    for path in paths:
        text = _read_text(path, max_file_bytes)
        if text is None:
            continue
        ext = path.suffix.lower()
        languages[LANGUAGES[ext]] += 1
        relative = path.relative_to(root).as_posix()
        lower = relative.lower()
        if _is_test_file(path.relative_to(root)):
            test_files += 1
        if path.name.lower().startswith(("readme", "contributing", "changelog")) or "/docs/" in f"/{lower}/":
            docs_files += 1
        if ext in {".json", ".yaml", ".yml", ".toml"}:
            config_files += 1
        total_lines += len(text.splitlines())
        if ext == ".py":
            dependencies.update(_python_imports(text))
        elif path.name in {"package.json", "pyproject.toml", "go.mod"}:
            for token in text.replace('"', " ").replace("'", " ").split():
                if "/" in token and len(token) < 120:
                    dependencies[token.strip(",;:[]")]+=1

    file_count = len(paths)
    test_ratio = test_files / max(file_count, 1)
    docs_ratio = docs_files / max(file_count, 1)
    config_ratio = config_files / max(file_count, 1)
    findings: dict[str, Dimension] = {}

    test_score = min(100.0, 45 + test_ratio * 220)
    test_findings = []
    if test_files == 0:
        test_findings.append(Finding(severity="high", title="No test files detected", detail="AURA could not identify repository tests in the analyzed file set."))
    else:
        test_findings.append(Finding(severity="info", title="Test surface detected", detail=f"Detected {test_files} likely test files among {file_count} analyzed files.", evidence=[f"test_ratio={test_ratio:.2f}"]))
    findings["testing"] = Dimension(score=round(test_score, 1), findings=test_findings)

    docs_score = min(100.0, 55 + docs_ratio * 180)
    docs_findings = [Finding(severity="info", title="Documentation signal", detail=f"Detected {docs_files} documentation-oriented files.", evidence=[f"docs_ratio={docs_ratio:.2f}"])]
    findings["documentation"] = Dimension(score=round(docs_score, 1), findings=docs_findings)

    config_score = min(100.0, 50 + config_ratio * 150)
    findings["configuration"] = Dimension(score=round(config_score, 1), findings=[Finding(severity="info", title="Configuration inventory", detail=f"Detected {config_files} configuration/data definition files.")])

    size_score = 100.0 if total_lines == 0 else max(35.0, 100 - max(0, total_lines - 10_000) / 500)
    findings["maintainability"] = Dimension(score=round(size_score, 1), findings=[Finding(severity="info", title="Repository size", detail=f"Analyzed approximately {total_lines:,} lines across {file_count} files.")])

    overall = round(sum(d.score for d in findings.values()) / len(findings), 1)
    return Analysis(repository=str(root), files=file_count, languages=dict(languages), dependencies=[name for name, _ in dependencies.most_common(30)], dimensions=findings, overall_score=overall, generated_at=datetime.now(timezone.utc).isoformat())
