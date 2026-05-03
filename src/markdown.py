import re
from typing import Tuple

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


def extract_markdown_images(text: str) -> list[Tuple[str, str]]:
    return re.findall(IMG_PATTERN, text)


def extract_markdown_links(text: str) -> list[Tuple[str, str]]:
    return re.findall(LINK_PATTERN, text)
