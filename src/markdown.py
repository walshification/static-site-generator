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
