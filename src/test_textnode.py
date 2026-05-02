import unittest

from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_init_no_url(self):
        text = "This is a text node"
        text_type = TextType.BOLD
        node = TextNode(text, text_type)
        self.assertEqual(node.text, text)
        self.assertEqual(node.text_type, text_type)
        self.assertEqual(node.url, None)

    def test_init_with_url(self):
        text = "This is a text node"
        text_type = TextType.LINK
        url = "example.com"
        node = TextNode(text, text_type, url)
        self.assertEqual(node.text, text)
        self.assertEqual(node.text_type, text_type)
        self.assertEqual(node.url, url)

    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_repr(self):
        text = "This is a text node"
        text_type = TextType.BOLD
        node = TextNode(text, text_type)
        self.assertEqual(str(node), f"TextNode({text}, {text_type.value}, None)")

    def test_not_eq(self):
        node = TextNode("This is a text node link!", TextType.LINK, "example.com")
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)


class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "")
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is bold", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold")

    def test_italic(self):
        node = TextNode("This is italic", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is italic")

    def test_code(self):
        node = TextNode("This is code", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is code")

    def test_link(self):
        node = TextNode("This is a link", TextType.LINK, "example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a link")
        self.assertEqual(html_node.props, {"href": "example.com"})

    def test_image(self):
        node = TextNode("This is an image", TextType.IMAGE, "example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props, {"src": "example.com", "alt": "This is an image"}
        )


if __name__ == "__main__":
    unittest.main()
