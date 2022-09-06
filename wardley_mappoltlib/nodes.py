"""
I could have a graph built from Nodes explicitly, but I can't be bothered
It's less effort to just code up the dfs search using keys and dicts in the
one place I need it
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union


ArrowDataType = Dict[str, float]


@dataclass(frozen=True)
class Arrow:
    """
    An arrow pointing away from a Node in a Wardley Map
    """
    evolution: float
    evolution_start: float
    type: str

    @classmethod
    def from_dict(cls, data: ArrowDataType, evolution_start):
        _data_to_modify = deepcopy(data)
        if "evolution_start" not in data:
            _data_to_modify["evolution_start"] = evolution_start
        return cls(**_data_to_modify)


NodeDataType = Dict[str, Union[str, float, List[str], List[ArrowDataType]]]


@dataclass
class Node:
    """
    A node in a Wardley Map
    """

    code: str
    title: str
    type: str
    visibility: float
    evolution: float
    dependencies: List[str] = field(default_factory=list)
    subcat: Optional[str] = None
    optional: bool = False
    arrows: List[Arrow] = field(default_factory=list)

    # these are things for exploring the tree
    children: List[Node] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: NodeDataType) -> Node:
        _data_to_modify = deepcopy(data)
        arrows: List[Arrow] = []
        if "arrows" in _data_to_modify:
            if arrows_data := _data_to_modify.pop("arrows"):
                arrows = [
                    Arrow.from_dict(
                        arrow_datum,
                        evolution_start=_data_to_modify["evolution"]
                    )
                    for arrow_datum in arrows_data
                ]
        return cls(**_data_to_modify, arrows=arrows)


def nodes_from_node_data(graph_data: List[NodeDataType]) -> list[Node]:
    """
    builds a node list from a graph_data dictionary
    """
    return list(Node.from_dict(gd) for gd in graph_data)


InterchangeDataType = Dict[str, Union[str, List[str]]]


@dataclass
class Interchange:
    """
    This represents the optional straight-replacement of alternate nodes.

    It is clearly from the same base type as Node, but not introducing a class
    heirarchy until I understand it a little better

    Interchanges containing interchanges are not a thing?
    """

    code: str
    title: str
    visibility: float
    # will be modified by plotting code
    evolution: float
    evolution_min: float
    evolution_max: float

    interchanges: List[Node]  # not a NodeGraph

    dependencies: List[str] = field(default_factory=list)

    subcat: Optional[str] = None
    optional: bool = False
    type: str = "interchange"
    arrows = []
    children = []

    @classmethod
    def from_node_graph(cls, code, title, interchange_codes: List[str], nodes: list[Node]) -> Interchange:
        if not interchange_codes:
            return None

        interchange_nodes: List[Node] = [
            node for node in nodes if node.code in interchange_codes
        ]
        visibility = interchange_nodes[0].visibility
        if not all(visibility == node.visibility for node in interchange_nodes):
            raise ValueError(
                "The visibility for the interchange nodes is not identical."
                "This is not valid.\n"
                f"Interchange codes {interchange_codes}"
            )
        ev_min: float = min(node.evolution for node in interchange_nodes)
        ev_max: float = max(node.evolution for node in interchange_nodes)

        # will be modified by plotting code
        evolution = (ev_min + ev_max)/2

        return cls(code, title, visibility, evolution, ev_min, ev_max, interchange_nodes)

    @classmethod
    def from_dict(cls, data: InterchangeDataType, nodes: list[Node]) -> Interchange:
        return cls.from_node_graph(data["code"], data["title"], data["interchanges"], nodes)


NodesType = list[Union[Node, Interchange]]


def build_node_graph(nodes: NodesType) -> None:
    """
    Updates the Nodes to have neighbours and children
    """
    code_node_map: Dict[str, Node] = {n.code: n for n in nodes}

    for a_node in nodes:
        for child_code in a_node.dependencies:
            child_node: Node = code_node_map[child_code]
            a_node.children.append(child_node)
