from unittest import TestCase

from parameterized import parameterized

from wardley_mappoltlib.linearised_route import linearise_graph
from wardley_mappoltlib.nodes import Node, graph_from_node_list


class MockNode(Node):

    def __init__(self, code, dependencies):
        super().__init__(
            code,
            "",
            "",
            dependencies,
            0.0,
            0.0
        )

    def __repr__(self):
        return self.code


class TestGraphToLiner(TestCase):

    @parameterized.expand(
        [
            ("single node A", [("A", [])], ["A"]),
            ("single node B", [("B", [])], ["B"]),
            (
                "single dependecy",
                [
                    ("A", ["B"]),
                    ("B", [])
                ],
                ["A", "B", "A"]
            ),
            (
                "two children",
                [
                    ("A", ["B", "C"]),
                    ("B", []),
                    ("C", [])
                ],
                ["A", "B", "A", "C", "A"]
            ),
            (
                "two parents",
                [
                    ("A", ["C"]),
                    ("B", ["C"]),
                    ("C", [])
                ],
                ["A", "C", "B", "C", "A"]
            ),
            (
                "circular dependency",
                [
                    ("A", ["B"]),
                    ("B", ["A"])
                ],
                ["A", "B", "A"]
            ),
            (
                "triangle - ensure all edges",
                [
                    ("A", ["B"]),
                    ("B", ["C"]),
                    ("C", ["A"])
                ],
                ["A", "B", "C", "A"]

            )
        ]
    )
    def test(self, name, code_deps, expected_codes):

        node_list = [MockNode(code, deps) for code, deps in code_deps]
        graph_from_node_list(node_list)
        code_node_map = {n.code: n for n in node_list}
        expected_route = [
            code_node_map[code] for code in expected_codes
        ]

        self.assertEqual(
            linearise_graph(node_list),
            expected_route
        )
