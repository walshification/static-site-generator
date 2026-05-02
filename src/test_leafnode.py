import unittest

from leafnode import LeafNode


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")


    def test_tag_with_props(self):
        node = LeafNode(
            tag="a",
            value="a link",
            props={"href": "https://www.example.com", "target": "_blank"},
        )
        self.assertEqual(
            node.to_html(),
            '<a href="https://www.example.com" target="_blank">a link</a>',
        )

    def test_empty_value(self):
        node = LeafNode(tag="p", value="")
        self.assertRaises(ValueError, node.to_html)

    def test_empty_tag_renders_value(self):
        node = LeafNode(tag="", value="some value")
        self.assertEqual(node.to_html(), node.value)

    def test_repr(self):
        tag = "a"
        value = "a link"
        props = {"href": "https://www.example.com", "target": "_blank"}
        node = LeafNode(tag=tag, value=value, props=props)
        self.assertEqual(node.tag, tag)
        self.assertEqual(node.value, value)
        self.assertEqual(node.props, props)
        self.assertEqual(str(node), f"LeafNode({tag}, {value}, {props})")
