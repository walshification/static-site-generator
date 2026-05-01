import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_init(self):
        tag = "a"
        value = "a link"
        props = {"href": "https://www.example.com", "target": "_blank"}
        node = HTMLNode(tag=tag, value=value, props=props)
        self.assertEqual(node.tag, tag)
        self.assertEqual(node.value, value)
        self.assertEqual(node.props, props)

    def test_props_to_html(self):
        node = HTMLNode(props={"href": "https://www.example.com", "target": "_blank"})
        self.assertEqual(
            node.props_to_html(), ' href="https://www.example.com" target="_blank"'
        )

    def test_repr(self):
        tag = "a"
        value = "a link"
        props = {"href": "https://www.example.com", "target": "_blank"}
        node = HTMLNode(tag=tag, value=value, props=props)
        self.assertEqual(node.tag, tag)
        self.assertEqual(node.value, value)
        self.assertEqual(node.props, props)
        self.assertEqual(str(node), f"HTMLNode({tag}, {value}, None, {props})")


if __name__ == "__main__":
    unittest.main()
