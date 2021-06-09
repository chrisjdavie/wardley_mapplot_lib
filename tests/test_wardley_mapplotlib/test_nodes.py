from copy import deepcopy
from unittest import TestCase

from wardley_mappoltlib.nodes import \
    Arrow, build_node_list, graph_from_node_list, Node


class MockNode(Node):

    def __init__(self, code, dependencies):
        super().__init__(
            code,
            "",
            "",
            dependencies,
            0.0,
            0.0,
            None
        )

    def __repr__(self):
        return self.code


class TestNode(TestCase):

    def setUp(self) -> None:
        self._data = {
            "code": "",
            "title": "",
            "type": "",
            "dependencies": [],
            "visibility": 0.0,
            "evolution": 0.0,
            "arrow": {
                "evolution": 1.0,
                "type": ""
            }
        }

    def test_arrow_builds(self):

        expected_arrow = Arrow(**self._data["arrow"])
        a_node = Node.from_dict(self._data)

        self.assertEqual(expected_arrow, a_node.arrow)

    def test_input_data_not_changed(self):

        data_copy = deepcopy(self._data)

        Node.from_dict(self._data)
        self.assertEqual(self._data, data_copy)

    def test_empty_arrow(self):

        self._data["arrow"] = {}
        a_node = Node.from_dict(self._data)

        self.assertEqual(a_node.arrow, None)


class TestBuildNodeList(TestCase):

    def test_one_item(self):

        data = [{
            "code": "PG",
            "title": "Power Grid",
            "type": "Customer",
            "dependencies": [
                "Turbine"
            ],
            "visibility": 0.5,
            "evolution": 3.5
        }]

        node_list = build_node_list(data)
        self.assertEqual(
            node_list[0], Node(**data[0], visibility_rescaled=0.5, arrow=None)
        )

    def test_two_items(self):

        data = [
            {
                "code": "PG",
                "title": "Power Grid",
                "type": "Customer",
                "dependencies": [
                    "Turbine"
                ],
                "visibility": 1.0,
                "evolution": 3.5
            }, {
                "code": "Turbine",
                "title": "Turbine",
                "type": "Node",
                "dependencies": [
                    "FPP"
                ],
                "visibility": 1.5,
                "evolution": 2.8
            }, {
                "code": "FPP",
                "title": "Fusion Power Plant",
                "type": "Node",
                "dependencies": [
                    "Laser",
                    "Targets"
                ],
                "visibility": 5.0,
                "evolution": 1.1
            }
        ]

        node_list = build_node_list(data)
        self.assertEqual(
            node_list[0], Node(**data[0], visibility_rescaled=1, arrow=None)
        )
        self.assertEqual(
            node_list[1], Node(
                **data[1], visibility_rescaled=0.875, arrow=None)
        )
        self.assertEqual(
            node_list[2], Node(**data[2], visibility_rescaled=0.0, arrow=None)
        )


class TestGraphFromNodeList(TestCase):

    def test_child_parent(self):

        parent = MockNode("A", ["B"])
        child = MockNode("B", [])

        graph_from_node_list([parent, child])

        self.assertIn(
            child, parent.children
        )

    def test_multiple_children(self):

        parent = MockNode("A", ["B", "C"])
        child_B = MockNode("B", [])
        child_C = MockNode("C", [])

        graph_from_node_list([child_B, parent, child_C])

        self.assertIn(
            child_B, parent.children
        )
        self.assertIn(
            child_C, parent.children
        )
