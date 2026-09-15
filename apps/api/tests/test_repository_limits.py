from pathlib import Path

import pytest

from app.repository import build_context


@pytest.mark.parametrize(
    ("max_files", "max_file_bytes", "message"),
    [
        (0, 100_000, "max_files must be at least 1"),
        (1, 0, "max_file_bytes must be at least 1"),
    ],
)
def test_build_context_rejects_non_positive_limits(
    tmp_path: Path, max_files: int, max_file_bytes: int, message: str
) -> None:
    (tmp_path / "app.py").write_text("print('safe')", encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        build_context(str(tmp_path), max_files=max_files, max_file_bytes=max_file_bytes)
