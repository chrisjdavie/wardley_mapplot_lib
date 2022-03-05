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


class NodeGraph(list[Node]):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._rescale()
        self._build_graph()

    @classmethod
    def from_node_data(cls, graph_data: List[NodeDataType]) -> NodeGraph:
        """
        builds a node list from a graph_data dictionary
        """
        return cls(Node.from_dict(gd) for gd in graph_data)

    def _build_graph(self) -> None:
        """
        Updates the Nodes to have neighbours and children
        """
        code_node_map: Dict[str, Node] = {n.code: n for n in self}

        for a_node in self:
            for child_code in a_node.dependencies:
                child_node: Node = code_node_map[child_code]
                a_node.children.append(child_node)
