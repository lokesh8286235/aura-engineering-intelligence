from app.models import Dimension, Finding


def test_finding_evidence_lists_are_not_shared():
    first = Finding(severity="low", title="A", detail="A")
    second = Finding(severity="low", title="B", detail="B")

    first.evidence.append("file.py:1")

    assert first.evidence == ["file.py:1"]
    assert second.evidence == []


def test_dimension_findings_lists_are_not_shared():
    first = Dimension(score=90)
    second = Dimension(score=80)

    first.findings.append(Finding(severity="medium", title="A", detail="A"))

    assert len(first.findings) == 1
    assert second.findings == []
