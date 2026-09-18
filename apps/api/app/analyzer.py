from __future__ import annotations

import ast
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SUPPORTED = {".py", ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs", ".java", ".go", ".graphql", ".gql", ".html", ".htm", ".css", ".scss", ".sass", ".json", ".yaml", ".yml", ".toml", ".md", ".mdx"}
SOURCE_EXTENSIONS = {".py", ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs", ".java", ".go", ".graphql", ".gql", ".html", ".htm", ".css", ".scss", ".sass"}
SKIP_DIRS = {".git", ".terraform", ".turbo", ".vercel", ".cache", ".parcel-cache", "node_modules", ".venv", "venv", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".nox", "coverage", "htmlcov", "dist", "build", "target", "__pycache__"}
SENSITIVE_FILENAMES = {".env", ".env.local", ".env.development", ".env.production", ".env.test", ".envrc", ".netrc", ".npmrc", ".pypirc", ".git-credentials", "credentials.json", "credentials.yml", "credentials.yaml", "credentials.toml", "secrets.json", "secrets.yml", "secrets.yaml", "secrets.toml", "service-account.json", "service_account.json", "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"}
SENSITIVE_RELATIVE_PATHS = {(".aws", "credentials"), (".docker", "config.json"), (".config", "gcloud", "application_default_credentials.json")}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
MAX_FILE_BYTES = 5_000_000


def _is_sensitive(path: Path) -> bool:
    name = path.name.lower()
    relative_parts = tuple(part.lower() for part in path.parts)
    return (name in SENSITIVE_FILENAMES or name.startswith(".env.") or path.suffix.lower() in SENSITIVE_SUFFIXES or any(relative_parts[-len(candidate):] == candidate for candidate in SENSITIVE_RELATIVE_PATHS))


def _files(root: Path, limit: int, max_bytes: int) -> tuple[list[tuple[Path, str]], bool]:
    """Return bounded, validated text once and report whether traversal was truncated."""
    found: list[tuple[Path, str]] = []
    for current, dirs, names in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d.lower() not in SKIP_DIRS and not (Path(current) / d).is_symlink())
        for name in sorted(names):
            path = Path(current) / name
            if (path.suffix.lower() not in SUPPORTED and path.name.lower() != "dockerfile" and not path.name.lower().startswith("dockerfile.")) or path.is_symlink() or _is_sensitive(path):
                continue
            try:
                text = _read_text(path, max_bytes)
            except OSError:
                continue
            if text is None:
                continue
            found.append((path, text))
            if len(found) > limit:
                return found[:limit], True
    return found, False


def _is_test_file(path: Path) -> bool:
    """Identify conventional test/spec files without substring false positives."""
    parts = [part.lower() for part in path.parts]
    stem = path.stem
    lower_stem = stem.lower()
    pascal_test = stem.startswith("Test") and len(stem) > 4 and stem[4].isupper()
    return (any(part in {"test", "tests", "spec", "specs", "__tests__"} for part in parts) or lower_stem in {"test", "spec"} or lower_stem.startswith("test_") or pascal_test or lower_stem.endswith("_test") or lower_stem.startswith("spec_") or lower_stem.endswith("_spec") or lower_stem.endswith(".test") or lower_stem.endswith(".spec"))


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
    """Read at most max_bytes, protecting against growth and binary data."""
    with path.open("rb") as handle:
        data = handle.read(max_bytes + 1)
    if len(data) > max_bytes or b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def analyze_repository(repository: str, max_files: int = 500, max_file_bytes: int = 512_000) -> Analysis:
    if type(max_files) is not int or not 1 <= max_files <= 10_000:
        raise ValueError("max_files must be between 1 and 10000")
    if type(max_file_bytes) is not int or not 1 <= max_file_bytes <= MAX_FILE_BYTES:
        raise ValueError(f"max_file_bytes must be between 1 and {MAX_FILE_BYTES}")
    root = Path(repository).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError("repository must be an existing directory")
    paths, truncated = _files(root, max_files, max_file_bytes)
    languages = Counter()
    dependencies: Counter[str] = Counter()
    total_lines = 0
    test_files = 0
    docs_files = 0
    config_files = 0
    empty_source_files: list[str] = []
    for path, text in paths:
        ext = path.suffix.lower()
        kind = "Dockerfile" if path.name.lower() == "dockerfile" or path.name.lower().startswith("dockerfile.") else LANGUAGES[ext]
        languages[kind] += 1
        relative = path.relative_to(root).as_posix()
        lower = relative.lower()
        if _is_test_file(path.relative_to(root)):
            test_files += 1
        if ext in {".md", ".mdx"} or path.name.lower().startswith(("readme", "contributing", "changelog")) or "/docs/" in f"/{lower}/":
            docs_files += 1
        if ext in {".json", ".yaml", ".yml", ".toml"}:
            config_files += 1
        total_lines += len(text.splitlines())
        if (ext in SOURCE_EXTENSIONS or kind == "Dockerfile") and not text.strip():
            empty_source_files.append(relative)
        if ext == ".py":
            dependencies.update(_python_imports(text))
        elif path.name.lower() in {"package.json", "pyproject.toml", "go.mod"}:
            for token in text.replace('"', " ").replace("'", " ").split():
                if "/" in token and len(token) < 120:
                    dependencies[token.strip(",;:[]")]+=1
    file_count = len(paths)
    test_ratio = test_files / max(file_count, 1)
    docs_ratio = docs_files / max(file_count, 1)
    config_ratio = config_files / max(file_count, 1)
    findings: dict[str, Dimension] = {}
    if file_count == 0:
        empty_finding = Finding(severity="high", title="No analyzable files detected", detail="AURA could not analyze any supported, valid text files in the repository. Quality scores are therefore set to zero rather than implying evidence that was not observed.", evidence=["files=0"])
        findings["testing"] = Dimension(score=0.0, findings=[empty_finding])
        findings["documentation"] = Dimension(score=0.0, findings=[empty_finding])
        findings["configuration"] = Dimension(score=0.0, findings=[empty_finding])
        findings["maintainability"] = Dimension(score=0.0, findings=[empty_finding])
        overall = 0.0
    else:
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
        maintainability_findings = [Finding(severity="info", title="Repository size", detail=f"Analyzed approximately {total_lines:,} lines across {file_count} files.")]
        if empty_source_files:
            maintainability_findings.append(Finding(severity="low", title="Empty source files detected", detail=f"Detected {len(empty_source_files)} source files containing no code.", evidence=empty_source_files[:8]))
            size_score = max(0.0, size_score - min(10.0, len(empty_source_files)))
        if truncated:
            maintainability_findings.append(Finding(severity="info", title="Analysis scan truncated", detail=f"The file scan stopped after the configured max_files limit of {max_files} valid files.", evidence=[f"max_files={max_files}"]))
            size_score = max(0.0, size_score - 10.0)
        findings["maintainability"] = Dimension(score=round(size_score, 1), findings=maintainability_findings)
        overall = round(sum(d.score for d in findings.values()) / len(findings), 1)
    return Analysis(repository=str(root), files=file_count, languages=dict(languages), dependencies=[name for name, _ in dependencies.most_common(30)], dimensions=findings, overall_score=overall, generated_at=datetime.now(timezone.utc).isoformat())
