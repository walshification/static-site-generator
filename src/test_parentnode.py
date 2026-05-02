import unittest

from leafnode import LeafNode
from parentnode import ParentNode


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_multiple_children(self):
        eldest_child_node = LeafNode("b", "an important value")
        middle_child_node = LeafNode("span", "another value")
        youngest_child_node = LeafNode("", "some value")
        parent_node = ParentNode(
            "div", [eldest_child_node, middle_child_node, youngest_child_node]
        )
        self.assertEqual(
            parent_node.to_html(),
            "<div><b>an important value</b><span>another value</span>some value</div>",
        )

    def test_to_html_with_mixed_nested_children(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        another_child_node = LeafNode("a", "some value")
        parent_node = ParentNode("div", [child_node, another_child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span><a>some value</a></div>",
        )

    def test_empty_tag(self):
        node = ParentNode(tag="", children=[LeafNode("", "some node")])
        self.assertRaises(ValueError, node.to_html)

    def test_no_children(self):
        node = ParentNode(tag="b", children=[])
        self.assertRaises(ValueError, node.to_html)

    def test_repr(self):
        tag = "a"
        children = [LeafNode("", "some node")]
        props = {"href": "https://www.example.com", "target": "_blank"}
        node = ParentNode(tag=tag, children=children, props=props)
        self.assertEqual(node.tag, tag)
        self.assertEqual(node.children, children)
        self.assertEqual(node.props, props)
        self.assertEqual(str(node), f"ParentNode({tag}, {children}, {props})")
