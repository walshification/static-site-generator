from typing import Optional, Sequence

from htmlnode import HTMLNode


class ParentNode(HTMLNode):
    def __init__(
        self, tag: str, children: Sequence[HTMLNode], props: Optional[dict[str, str]] = None
    ):
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self):
        if not self.tag:
            raise ValueError("all parent nodes must have a tag")

        if not self.children:
            raise ValueError("all parent nodes must have at least one child")

        content = [f"<{self.tag}{self.props_to_html()}>"]
        for child in self.children:
            content.append(child.to_html())

        content.append(f"</{self.tag}>")

        return "".join(content)

    def __repr__(self):
        return f"ParentNode({self.tag}, {self.children}, {self.props})"
