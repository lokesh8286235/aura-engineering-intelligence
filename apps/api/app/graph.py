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
        return {
            "nodes": [node.__dict__ for node in self.nodes.values()],
            "edges": [edge.__dict__ for edge in self.edges],
        }
