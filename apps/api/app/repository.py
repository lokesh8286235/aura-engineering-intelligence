from __future__ import annotations

import os
from pathlib import Path

SKIP = {".git", "node_modules", ".venv", "venv", "dist", "build", "target", "__pycache__"}
SENSITIVE_FILENAMES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.test",
    ".envrc",
    ".netrc",
    ".npmrc",
    ".pypirc",
    ".git-credentials",
    "credentials.json",
    "credentials.yml",
    "credentials.yaml",
    "credentials.toml",
    "secrets.json",
    "secrets.yml",
    "secrets.yaml",
    "secrets.toml",
    "service-account.json",
    "service_account.json",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "id_dsa",
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
SENSITIVE_RELATIVE_PATHS = {
    (".aws", "credentials"),
    (".docker", "config.json"),
    (".config", "gcloud", "application_default_credentials.json"),
}
SUPPORTED = {".py", ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs", ".java", ".go", ".md", ".mdx", ".yaml", ".yml", ".json", ".toml"}


def _is_sensitive(path: Path) -> bool:
    name = path.name.lower()
    relative_parts = tuple(part.lower() for part in path.parts)
    return (
        name in SENSITIVE_FILENAMES
        or name.startswith(".env.")
        or path.suffix.lower() in SENSITIVE_SUFFIXES
        or any(relative_parts[-len(candidate):] == candidate for candidate in SENSITIVE_RELATIVE_PATHS)
    )


def _truncate_utf8(text: str, max_bytes: int) -> str:
    """Limit context by UTF-8 byte size without splitting a multibyte character."""
    data = text.encode("utf-8")
    if len(data) <= max_bytes:
        return text
    return data[:max_bytes].decode("utf-8", errors="ignore")


def build_context(repository: str, max_files: int = 200, max_file_bytes: int = 100_000) -> str:
    if max_files < 1:
        raise ValueError("max_files must be at least 1")
    if max_file_bytes < 1:
        raise ValueError("max_file_bytes must be at least 1")

    root = Path(repository).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("repository must be an existing directory")
    chunks: list[str] = []
    count = 0
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP and not (Path(current) / d).is_symlink()]
        for name in sorted(files):
            path = Path(current) / name
            if path.is_symlink() or path.suffix.lower() not in SUPPORTED or _is_sensitive(path):
                continue
            try:
                if path.stat().st_size > max_file_bytes:
                    continue
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "\x00" in text:
                continue
            relative = path.relative_to(root).as_posix()
            chunks.append(f"FILE: {relative}\n{_truncate_utf8(text, max_file_bytes)}")
            count += 1
            if count >= max_files:
                return "\n\n---\n\n".join(chunks)
    return "\n\n---\n\n".join(chunks)
