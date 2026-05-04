import enum
import re
from typing import Tuple

from htmlnode import HTMLNode
from parentnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node


IMG_PATTERN = re.compile(r"\!\[([^\]]*)\]\(([^\)]*)\)")
LINK_PATTERN = re.compile(r"(?<!!)\[([^\]]*)\]\(([^\)]*)\)")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    split_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            split_nodes.append(old_node)
            continue

        parts = old_node.text.split(delimiter)
        if len(parts) == 1:
            split_nodes.append(TextNode(parts[0], TextType.TEXT))
            continue

        if len(parts) % 2 == 0:
            raise ValueError(f"missing closing tag in text: {old_node.text}")

        for i, part in enumerate(parts):
            if part:
                if i % 2 == 0:
                    split_nodes.append(TextNode(part, TextType.TEXT))
                else:
                    split_nodes.append(TextNode(part, text_type))

    return split_nodes


def split_nodes_image(old_nodes):
    split_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            split_nodes.append(old_node)
            continue

        images = extract_markdown_images(old_node.text)
        if not images:
            split_nodes.append(old_node)
            continue

        text = old_node.text
        for image_alt, image_src in images:
            sections = text.split(f"![{image_alt}]({image_src})", 1)
            if sections[0]:
                split_nodes.append(TextNode(text=sections[0], text_type=TextType.TEXT))

            split_nodes.append(
                TextNode(text=image_alt, text_type=TextType.IMAGE, url=image_src)
            )
            text = sections[1]

        if text:
            split_nodes.append(TextNode(text=text, text_type=TextType.TEXT))

    return split_nodes


def split_nodes_link(old_nodes):
    split_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            split_nodes.append(old_node)
            continue

        links = extract_markdown_links(old_node.text)
        if not links:
            split_nodes.append(old_node)
            continue

        text = old_node.text
        for link_text, link_url in links:
            sections = text.split(f"[{link_text}]({link_url})", 1)
            if sections[0]:
                split_nodes.append(TextNode(text=sections[0], text_type=TextType.TEXT))

            split_nodes.append(
                TextNode(text=link_text, text_type=TextType.LINK, url=link_url)
            )
            if len(sections) > 1:
                text = sections[1]
            else:
                text = ""

        if text:
            split_nodes.append(TextNode(text=text, text_type=TextType.TEXT))

    return split_nodes


def extract_markdown_images(text: str) -> list[Tuple[str, str]]:
    return re.findall(IMG_PATTERN, text)


def extract_markdown_links(text: str) -> list[Tuple[str, str]]:
    return re.findall(LINK_PATTERN, text)


def text_to_textnodes(text: str) -> list[TextNode]:
    text_nodes = [TextNode(text=text, text_type=TextType.TEXT)]
    for delimiter, text_type in (
        ("**", TextType.BOLD), ("_", TextType.ITALIC), ("`", TextType.CODE)
    ):
        text_nodes = split_nodes_delimiter(text_nodes, delimiter, text_type)

    text_nodes = split_nodes_image(text_nodes)
    text_nodes = split_nodes_link(text_nodes)

    return text_nodes


def markdown_to_blocks(markdown: str) -> list[str]:
    return [stripped for block in markdown.split("\n\n") if (stripped := block.strip())]


class BlockType(enum.StrEnum):
    PARAGRAPH = enum.auto()
    HEADING = enum.auto()
    CODE = enum.auto()
    QUOTE = enum.auto()
    UNORDERED_LIST = enum.auto()
    ORDERED_LIST = enum.auto()


HEADING_PATTERN = re.compile(r"^\#{1,6}\s")
CODE_PATTERN = re.compile(r"^```\n[\s\S]+\n```$")


def block_to_block_type(block: str) -> BlockType:
    if re.match(HEADING_PATTERN, block):
        return BlockType.HEADING
    elif re.fullmatch(CODE_PATTERN, block):
        return BlockType.CODE
    elif all(line.startswith(">") for line in block.split("\n")):
        return BlockType.QUOTE
    elif all(line.startswith("- ") for line in block.split("\n")):
        return BlockType.UNORDERED_LIST
    elif all(
        line.startswith(f"{i}. ") for i, line in enumerate(block.split("\n"), start=1)
    ):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def text_to_children(text: str) -> list[HTMLNode]:
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]


def markdown_to_html_node(markdown: str) -> HTMLNode:
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)

        match (block_type):
            case BlockType.HEADING:
                hashes, text = block.split(" ", maxsplit=1)
                tag = f"h{len(hashes)}"
                child_nodes = text_to_children(text)
                html_nodes.append(ParentNode(tag, children=child_nodes))

            case BlockType.PARAGRAPH:
                text = block.replace("\n", " ")
                html_nodes.append(ParentNode("p", text_to_children(text)))

            case BlockType.QUOTE:
                stripped = " ".join(
                    [line.lstrip(">").strip() for line in block.split("\n")]
                )
                html_nodes.append(ParentNode("blockquote", text_to_children(stripped)))

            case BlockType.CODE:
                stripped = block.removeprefix("```\n").removesuffix("```")
                code = ParentNode(
                    "code", [text_node_to_html_node(TextNode(stripped, TextType.TEXT))]
                )
                pre = ParentNode("pre", [code])
                html_nodes.append(pre)

            case BlockType.UNORDERED_LIST:
                items = [
                    ParentNode("li", text_to_children(line[2:]))
                    for line in block.split("\n")
                ]
                ul = ParentNode("ul", items)
                html_nodes.append(ul)

            case BlockType.ORDERED_LIST:
                items = [
                    ParentNode("li", text_to_children(line.split(". ", maxsplit=1)[1]))
                    for line in block.split("\n")
                ]
                ol = ParentNode("ol", items)
                html_nodes.append(ol)

            case _:
                raise ValueError(f"unknown block type: {block_type}")

    return ParentNode("div", html_nodes)


def extract_title(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("no h1 header found in markdown")
