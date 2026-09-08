from __future__ import annotations

from pathlib import Path

SKIP = {".git", "node_modules", ".venv", "venv", "dist", "build", "target", "__pycache__"}


def build_context(repository: str, max_files: int = 200, max_file_bytes: int = 100_000) -> str:
    root = Path(repository).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("repository must be an existing directory")
    chunks: list[str] = []
    count = 0
    for current, dirs, files in __import__("os").walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP and not (Path(current) / d).is_symlink()]
        for name in sorted(files):
            path = Path(current) / name
            if path.is_symlink() or path.suffix.lower() not in {".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".md", ".yaml", ".yml", ".json"}:
                continue
            try:
                if path.stat().st_size > max_file_bytes:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            relative = path.relative_to(root).as_posix()
            chunks.append(f"FILE: {relative}\n{text[:max_file_bytes]}")
            count += 1
            if count >= max_files:
                return "\n\n---\n\n".join(chunks)
    return "\n\n---\n\n".join(chunks)
