from typing import FrozenSet, List, Optional, Set

from wardley_mappoltlib.nodes import Node, graph_from_node_list


def linearise_graph(graph_data: List[Node]) -> List[Node]:
    """
    Builds a linearised route through the graph, so that all edges are
    explored.

    This tracks back to the zeroth node, and it doesn't need to - it's 
    needlessly going over those final edges. I could tidy it up, if I think
    about edges. Might do, but it's valid without
    """

    route: List[Node] = []
    visited_nodes: Set[str] = set()
    visited_edges: Set[FrozenSet[str]] = set()

    def find_route(this_node: Node, caller: Optional[Node]) -> None:
        route.append(this_node)

        if this_node.code not in visited_nodes:
            visited_nodes.add(this_node.code)
            # allows backwards tracking
            this_node.first_caller = caller
        if caller:
            edge: FrozenSet[str] = frozenset((this_node.code, caller.code))
            visited_edges.add(edge)

        # visiting unvisited nodes
        for neigh in this_node.neighbours:
            edge: FrozenSet[str] = frozenset((this_node.code, neigh.code))
            if neigh.code not in visited_nodes or edge not in visited_edges:
                return find_route(neigh, this_node)

        # once all the neighbours have been explored, track backwards
        # through the graph to find other places to visit
        if this_node.first_caller:
            return find_route(this_node.first_caller, this_node)

    find_route(graph_data[0], None)

    return route
