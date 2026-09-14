from app.graph import Edge, Node, RepositoryGraph


def test_graph_serialization_is_deterministic():
    graph = RepositoryGraph()
    graph.add_node(Node(id="z", kind="module", label="z"))
    graph.add_node(Node(id="a", kind="module", label="a"))
    graph.connect("z", "a", "imports")
    graph.connect("a", "z", "imports")

    assert graph.to_dict() == {
        "nodes": [
            {"id": "a", "kind": "module", "label": "a"},
            {"id": "z", "kind": "module", "label": "z"},
        ],
        "edges": [
            {"source": "a", "target": "z", "relation": "imports"},
            {"source": "z", "target": "a", "relation": "imports"},
        ],
    }


def test_graph_deduplicates_identical_edges():
    graph = RepositoryGraph()
    graph.add_node(Node(id="a", kind="module", label="a"))
    graph.add_node(Node(id="b", kind="module", label="b"))

    graph.connect("a", "b", "imports")
    graph.connect("a", "b", "imports")

    assert graph.edges == [Edge("a", "b", "imports")]
