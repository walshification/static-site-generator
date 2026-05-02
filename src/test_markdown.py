import unittest

from markdown import split_nodes_delimiter
from textnode import TextNode, TextType


class TestMarkdown(unittest.TestCase):
    def test_code(self):
        old_node = TextNode("This has `code blocks` in it", TextType.TEXT)
        nodes = split_nodes_delimiter([old_node], "`", TextType.CODE)

        self.assertEqual(nodes[0].text, "This has ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "code blocks")
        self.assertEqual(nodes[1].text_type, TextType.CODE)
        self.assertEqual(nodes[2].text, " in it")
        self.assertEqual(nodes[2].text_type, TextType.TEXT)

    def test_bold(self):
        old_node = TextNode("This has **bold text** in it", TextType.TEXT)
        nodes = split_nodes_delimiter([old_node], "**", TextType.BOLD)

        self.assertEqual(nodes[0].text, "This has ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "bold text")
        self.assertEqual(nodes[1].text_type, TextType.BOLD)
        self.assertEqual(nodes[2].text, " in it")
        self.assertEqual(nodes[2].text_type, TextType.TEXT)

    def test_italic(self):
        old_node = TextNode("This has _emphasized text_ in it", TextType.TEXT)
        nodes = split_nodes_delimiter([old_node], "_", TextType.ITALIC)

        self.assertEqual(nodes[0].text, "This has ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "emphasized text")
        self.assertEqual(nodes[1].text_type, TextType.ITALIC)
        self.assertEqual(nodes[2].text, " in it")
        self.assertEqual(nodes[2].text_type, TextType.TEXT)

    def test_starting_tag(self):
        old = TextNode("`code` and more text", TextType.TEXT)
        nodes = split_nodes_delimiter([old], "`", TextType.CODE)
        self.assertEqual(
            nodes,
            [
                TextNode("code", TextType.CODE),
                TextNode(" and more text", TextType.TEXT),
            ],
        )

    def test_ending_tag(self):
        old = TextNode("some text and `code`", TextType.TEXT)
        nodes = split_nodes_delimiter([old], "`", TextType.CODE)
        self.assertEqual(
            nodes,
            [
                TextNode("some text and ", TextType.TEXT),
                TextNode("code", TextType.CODE),
            ],
        )

    def test_multiple(self):
        old = TextNode("A `first` then B `second` then C", TextType.TEXT)
        nodes = split_nodes_delimiter([old], "`", TextType.CODE)
        self.assertEqual(
            nodes,
            [
                TextNode("A ", TextType.TEXT),
                TextNode("first", TextType.CODE),
                TextNode(" then B ", TextType.TEXT),
                TextNode("second", TextType.CODE),
                TextNode(" then C", TextType.TEXT),
            ],
        )

    def test_passthrough(self):
        old = TextNode("already coded", TextType.CODE)
        nodes = split_nodes_delimiter([old], "`", TextType.CODE)
        self.assertEqual(nodes, [TextNode("already coded", TextType.CODE)])

    def test_passthrough_mixed(self):
        nodes = [
            TextNode("already bold", TextType.BOLD),
            TextNode("plain `code` here", TextType.TEXT),
        ]
        result = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("already bold", TextType.BOLD),
                TextNode("plain ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" here", TextType.TEXT),
            ],
        )

    def test_unmatched_tag(self):
        nodes = [TextNode("plain `code here", TextType.TEXT)]
        with self.assertRaises(ValueError):
            split_nodes_delimiter(nodes, "`", TextType.CODE)

    def test_no_tag(self):
        nodes = [TextNode("plain text here", TextType.TEXT)]
        self.assertEqual(
            split_nodes_delimiter(nodes, "`", TextType.CODE),
            nodes,
        )

    def test_multiple_mixed(self):
        nodes = [TextNode("A **first** then B _second_ then C", TextType.TEXT)]
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        self.assertEqual(
            nodes,
            [
                TextNode("A ", TextType.TEXT),
                TextNode("first", TextType.BOLD),
                TextNode(" then B ", TextType.TEXT),
                TextNode("second", TextType.ITALIC),
                TextNode(" then C", TextType.TEXT),
            ],
        )
