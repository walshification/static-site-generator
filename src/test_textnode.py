import unittest

from textnode import TextNode, TextType


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


if __name__ == "__main__":
    unittest.main()
