from pathlib import Path

from app.analyzer import analyze_repository


def test_graphql_files_are_included_in_language_inventory(tmp_path: Path):
    (tmp_path / "schema.graphql").write_text("type Query { health: String }\n", encoding="utf-8")
    (tmp_path / "operations.gql").write_text("query Health { health }\n", encoding="utf-8")

    result = analyze_repository(str(tmp_path))

    assert result.files == 2
    assert result.languages == {"GraphQL": 2}
