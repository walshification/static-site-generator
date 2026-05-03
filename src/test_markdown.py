import unittest

from markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
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


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_markdown_images(self):
        matches = extract_markdown_images(
            "This has one ![image](https://i.imgur.com/zjjcJKZ.png) "
            "and ![another image](https://i.imgur.com/asdf.png)"
        )
        self.assertListEqual(
            [
                ("image", "https://i.imgur.com/zjjcJKZ.png"),
                ("another image", "https://i.imgur.com/asdf.png"),
            ],
            matches,
        )


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://example.com)"
        )
        self.assertListEqual([("link", "https://example.com")], matches)

    def test_extract_multiple_markdown_links(self):
        matches = extract_markdown_links(
            "This has one [link](https://i.imgur.com/zjjcJKZ.png) "
            "and [another link](https://i.imgur.com/asdf.png)"
        )
        self.assertListEqual(
            [
                ("link", "https://i.imgur.com/zjjcJKZ.png"),
                ("another link", "https://i.imgur.com/asdf.png"),
            ],
            matches,
        )

    def test_extract_markdown_links_ignores_images(self):
        matches = extract_markdown_links(
            "This has an ![image](https://example.com/img.png) but no links"
        )
        self.assertListEqual([], matches)


class TextSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_no_images(self):
        node = TextNode("This is text with no image", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [TextNode("This is text with no image", TextType.TEXT)], new_nodes
        )

    def test_starting_image(self):
        node = TextNode(
            "![This](https://i.imgur.com/zjjcJKZ.png) starts with an image",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" starts with an image", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_ending_image(self):
        node = TextNode(
            "This ends with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This ends with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_non_image(self):
        node = TextNode("bold stuff", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("bold stuff", TextType.BOLD)], new_nodes)


class TextSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://i.imgur.com/zjjcJKZ.png) and another [second link](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_no_links(self):
        node = TextNode("This is text with no link", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [TextNode("This is text with no link", TextType.TEXT)], new_nodes
        )

    def test_starting_link(self):
        node = TextNode(
            "[This](https://i.imgur.com/zjjcJKZ.png) starts with a link",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" starts with a link", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_ending_link(self):
        node = TextNode(
            "This ends with a [link](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This ends with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_non_link(self):
        node = TextNode("bold stuff", TextType.BOLD)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([TextNode("bold stuff", TextType.BOLD)], new_nodes)
