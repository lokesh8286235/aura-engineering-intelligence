from pathlib import Path

from app.analyzer import analyze_repository


def test_frontend_markup_and_stylesheet_variants_are_classified(tmp_path: Path) -> None:
    (tmp_path / "legacy.htm").write_text("<main>Hello</main>\n", encoding="utf-8")
    (tmp_path / "theme.scss").write_text("$gap: 1rem;\nmain { gap: $gap; }\n", encoding="utf-8")
    (tmp_path / "theme.sass").write_text("main\n  display: grid\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 3
    assert result.languages == {"HTML": 1, "CSS": 2}
