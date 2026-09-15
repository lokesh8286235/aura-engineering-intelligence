from pathlib import Path

from app.repository import build_context


def test_build_context_skips_generated_and_cache_directories(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('safe')\n", encoding="utf-8")

    for dirname in (".next", ".turbo", ".cache", ".pytest_cache", "coverage", ".terraform"):
        generated = tmp_path / dirname
        generated.mkdir()
        (generated / "generated.py").write_text("print('noise')\n", encoding="utf-8")

    context = build_context(str(tmp_path))

    assert "FILE: app.py" in context
    for dirname in (".next", ".turbo", ".cache", ".pytest_cache", "coverage", ".terraform"):
        assert f"FILE: {dirname}/generated.py" not in context
