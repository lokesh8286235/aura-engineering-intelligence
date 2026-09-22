from pathlib import Path

from app.analyzer import analyze_repository


def test_protocol_buffers_files_are_counted_as_source(tmp_path: Path) -> None:
    (tmp_path / "events.proto").write_text(
        'syntax = "proto3";\nmessage Event { string id = 1; }\n',
        encoding="utf-8",
    )

    result = analyze_repository(str(tmp_path))

    assert result.files == 1
    assert result.source_files == 1
    assert result.languages == {"Protocol Buffers": 1}
    assert not any(r.message == "No source-code files detected" for r in result.risks)
