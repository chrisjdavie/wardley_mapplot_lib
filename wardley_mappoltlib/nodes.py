"""
I could have a graph built from Nodes explicitly, but I can't be bothered
It's less effort to just code up the dfs search using keys and dicts in the
one place I need it
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Union


@dataclass
class Node:
    """
    A node in a Wardley Map
    """

    code: str
    title: str
    type: str
    dependencies: List[str]
    visibility: float
    evolution: float

    visibility_rescaled: float = -1.0

    # these are things for exploring the tree
    children: List[Node] = field(default_factory=list)


def build_node_list(
    graph_data: List[Dict[str, Union[str, float, List[str]]]]
) -> List[Node]:
    """
    builds a node list from a graph_data dictionary
    """
    node_list = [Node(**gd) for gd in graph_data]
    if len(node_list) == 1:
        node_list[0].visibility_rescaled = node_list[0].visibility
        return node_list

    vis_min = min([n.visibility for n in node_list])
    vis_max = max([n.visibility for n in node_list])
    scale_factor = vis_max - vis_min
    for node in node_list:
        node.visibility_rescaled = (
            scale_factor - (node.visibility - vis_min))/scale_factor
    return node_list


def graph_from_node_list(all_nodes: List[Node]) -> None:
    """
    Updates the Nodes to have neighbours and children
    """
    code_node_map: Dict[str, Node] = {n.code: n for n in all_nodes}

    for a_node in all_nodes:
        for child_code in a_node.dependencies:
            child_node: Node = code_node_map[child_code]
            a_node.children.append(child_node)
