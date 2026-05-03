import unittest

from markdown import (
    BlockType,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    markdown_to_blocks,
    markdown_to_html_node,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
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


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` and "
            "an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a "
            "[link](https://boot.dev)"
        )
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_only_bold(self):
        text = "This is **bold text** with nothing else"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold text", TextType.BOLD),
                TextNode(" with nothing else", TextType.TEXT),
            ],
            nodes,
        )

    def test_only_italic(self):
        text = "This is _italic text_ with nothing else"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic text", TextType.ITALIC),
                TextNode(" with nothing else", TextType.TEXT),
            ],
            nodes,
        )

    def test_only_code(self):
        text = "This is `code` with nothing else"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" with nothing else", TextType.TEXT),
            ],
            nodes,
        )

    def test_only_image(self):
        text = (
            "This is an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) "
            "with nothing else"
        )
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" with nothing else", TextType.TEXT),
            ],
            nodes,
        )

    def test_only_link(self):
        text = "This is a [boot dot dev link](https://boot.dev) with nothing else"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is a ", TextType.TEXT),
                TextNode("boot dot dev link", TextType.LINK, "https://boot.dev"),
                TextNode(" with nothing else", TextType.TEXT),
            ],
            nodes,
        )

    def test_multiple_bolds(self):
        text = "This is **bold text** with **one** more"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold text", TextType.BOLD),
                TextNode(" with ", TextType.TEXT),
                TextNode("one", TextType.BOLD),
                TextNode(" more", TextType.TEXT),
            ],
            nodes,
        )

    def test_multiple_italics(self):
        text = "This is _italic text_ with _one_ more"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic text", TextType.ITALIC),
                TextNode(" with ", TextType.TEXT),
                TextNode("one", TextType.ITALIC),
                TextNode(" more", TextType.TEXT),
            ],
            nodes,
        )

    def test_multiple_codes(self):
        text = "This is `code` with `one` more"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" with ", TextType.TEXT),
                TextNode("one", TextType.CODE),
                TextNode(" more", TextType.TEXT),
            ],
            nodes,
        )

    def test_multiple_images(self):
        text = (
            "This is an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) "
            "with ![one](https://i.imgur.com/zjjcJKZ.png) more"
        )
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" with ", TextType.TEXT),
                TextNode("one", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" more", TextType.TEXT),
            ],
            nodes,
        )

    def test_multiple_links(self):
        text = (
            "This is a [boot dot dev link](https://boot.dev) with "
            "[one](https://example.com) more"
        )
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is a ", TextType.TEXT),
                TextNode("boot dot dev link", TextType.LINK, "https://boot.dev"),
                TextNode(" with ", TextType.TEXT),
                TextNode("one", TextType.LINK, "https://example.com"),
                TextNode(" more", TextType.TEXT),
            ],
            nodes,
        )

    def test_empty_string(self):
        nodes = text_to_textnodes("")
        self.assertListEqual([TextNode("", TextType.TEXT)], nodes)

    def test_adjacent(self):
        nodes = text_to_textnodes("Here's a **bold **[link](https://boot.dev)")
        self.assertListEqual(
            [
                TextNode("Here's a ", TextType.TEXT),
                TextNode("bold ", TextType.BOLD),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_ending(self):
        nodes = text_to_textnodes("This ends **boldly**")
        self.assertListEqual(
            [
                TextNode("This ends ", TextType.TEXT),
                TextNode("boldly", TextType.BOLD),
            ],
            nodes,
        )


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                (
                    "This is another paragraph with _italic_ text and `code` here\n"
                    "This is the same paragraph on a new line"
                ),
                "- This is a list\n- with items",
            ],
        )

    def test_excessive_blank_lines(self):
        md = """
This is **bolded** paragraph



This is another paragraph with _italic_ text and `code` here
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here"
            ],
        )

    def test_excess_whitespace(self):
        md = """
                           This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here\t
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here"
            ],
        )

    def test_single_block(self):
        md = """
This is **bolded** paragraph
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is **bolded** paragraph"])

    def test_just_whitespace(self):
        md = """
\t
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])


class TestBlockToBlockType(unittest.TestCase):
    def test_heading(self):
        self.assertEqual(BlockType.HEADING, block_to_block_type("### Some Heading"))

    def test_code(self):
        self.assertEqual(BlockType.CODE, block_to_block_type("```\nsome code()\n```"))

    def test_quote(self):
        self.assertEqual(BlockType.QUOTE, block_to_block_type(">some\n>quote"))

    def test_unordered_list(self):
        self.assertEqual(
            BlockType.UNORDERED_LIST, block_to_block_type("- some\n- list")
        )

    def test_ordered_list(self):
        self.assertEqual(
            BlockType.ORDERED_LIST, block_to_block_type("1. some\n2. list")
        )

    def test_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("some random text"))

    def test_invalid_heading_too_many_hashes(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("####### womp"))

    def test_invalid_heading_no_space(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("#womp"))

    def test_code_invalid_missing_closing_ticks(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("```womp"))

    def test_code_multiline(self):
        md = """```
def whatever():
    return "blah"
```"""
        self.assertEqual(BlockType.CODE, block_to_block_type(md))

    def test_quote_invalid_only_some_lines_are_quotes(self):
        self.assertEqual(
            BlockType.PARAGRAPH, block_to_block_type(">some\n>quote\nnot a quote")
        )

    def test_unordered_list_invalid_missing_space_after_dash(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("-some\n-list"))

    def test_unordered_list_invalid_missing_dash(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("- some\nlist"))

    def test_ordered_list_invalid_wrong_start(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("2. some\n3. list"))

    def test_ordered_list_invalid_non_incrementing(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("1. some\n1. list"))

    def test_ordered_list_invalid_off_in_middle(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("1. a\n2. b\n4. c"))

    def test_ordered_list_invalid_missing_end(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("1. a\n2. b\nc"))

    def test_quote_with_no_space(self):
        self.assertEqual( BlockType.QUOTE, block_to_block_type(">some\n>list"))


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            (
                "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p>"
                "<p>This is another paragraph with <i>italic</i> text and "
                "<code>code</code> here</p></div>"
            ),
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            (
                "<div><pre><code>This is text that _should_ remain\nthe **same** even "
                "with inline stuff\n</code></pre></div>"
            ),
        )

    def test_heading_levels(self):
        for level in range(1, 7):
            with self.subTest(level=level):
                hashes = "#" * level
                md = f"{hashes} Heading {level}"
                node = markdown_to_html_node(md)
                self.assertEqual(
                    node.to_html(),
                    f"<div><h{level}>Heading {level}</h{level}></div>",
                )

    def test_heading_with_inline_markdown(self):
        md = "## Hello **world**"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><h2>Hello <b>world</b></h2></div>",
        )

    def test_paragraph_multiline(self):
        md = "Line one\nLine two\nLine three"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><p>Line one Line two Line three</p></div>",
        )

    def test_paragraph_mixed_inline(self):
        md = "**bold**, _italic_, and `code`"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><p><b>bold</b>, <i>italic</i>, and <code>code</code></p></div>",
        )

    def test_quote_multiline(self):
        md = ">line one\n>line two\n>line three"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><blockquote>line one line two line three</blockquote></div>",
        )

    def test_code_block_no_inline_parsing(self):
        md = "```\n_italics_ and **bold** stay literal\n```"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><pre><code>_italics_ and **bold** stay literal\n</code></pre></div>",
        )

    def test_unordered_list_with_inline(self):
        md = "- **bold** item\n- _italic_ item"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ul><li><b>bold</b> item</li><li><i>italic</i> item</li></ul></div>",
        )

    def test_ordered_list_with_inline(self):
        md = "1. **bold** first\n2. _italic_ second"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ol><li><b>bold</b> first</li><li><i>italic</i> second</li></ol></div>",
        )

    def test_mixed_document(self):
        md = (
            "# Title\n\n"
            "Some **bold** paragraph.\n\n"
            "- Item one\n"
            "- Item **two**\n\n"
            "```\n"
            "code _literal_\n"
            "```"
        )
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            (
                "<div>"
                "<h1>Title</h1>"
                "<p>Some <b>bold</b> paragraph.</p>"
                "<ul><li>Item one</li><li>Item <b>two</b></li></ul>"
                "<pre><code>code _literal_\n</code></pre>"
                "</div>"
            ),
        )

    def test_whitespace_only(self):
        # markdown_to_blocks returns [] for whitespace-only input, so
        # ParentNode("div", []) has no children and to_html() raises ValueError.
        with self.assertRaises(ValueError):
            markdown_to_html_node("   \n\t\n   ").to_html()

    def test_quote_with_inline(self):
        md = "> Wisdom from **Boots**: _learn_ daily"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            (
                "<div>"
                "<blockquote>Wisdom from <b>Boots</b>: <i>learn</i> daily</blockquote>"
                "</div>"
            ),
        )
