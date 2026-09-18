from pathlib import Path

from app.analyzer import analyze_repository


def test_envrc_is_excluded_from_analysis(tmp_path: Path) -> None:
    (tmp_path / ".envrc").write_text('export API_TOKEN="secret"\n', encoding="utf-8")
    (tmp_path / "app.py").write_text("print('ok')\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert ".envrc" not in [signal.path for signal in result.signals]
    assert result.files == 1
    assert result.languages == {"Python": 1}
