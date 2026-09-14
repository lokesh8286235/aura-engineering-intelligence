from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Node:
    id: str
    kind: str
    label: str


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    relation: str


@dataclass
class RepositoryGraph:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def connect(self, source: str, target: str, relation: str) -> None:
        if source in self.nodes and target in self.nodes:
            edge = Edge(source, target, relation)
            if edge not in self.edges:
                self.edges.append(edge)

    def to_dict(self) -> dict:
        """Return a stable representation for APIs, snapshots, and evaluation."""
        return {
            "nodes": [self.nodes[node_id].__dict__ for node_id in sorted(self.nodes)],
            "edges": [
                edge.__dict__
                for edge in sorted(
                    self.edges,
                    key=lambda item: (item.source, item.target, item.relation),
                )
            ],
        }
