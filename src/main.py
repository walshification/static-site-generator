import os
import shutil

from textnode import TextNode, TextType


def build():
    project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
    static_dir = os.path.join(project_root, "static")
    public_dir = os.path.join(project_root, "public")

    if os.path.exists(public_dir):
        shutil.rmtree(public_dir)
    os.makedirs(public_dir)

    for dirpath, _, filenames in os.walk(static_dir):
        rel = os.path.relpath(dirpath, static_dir)
        dst_dir = os.path.join(public_dir, rel)
        os.makedirs(dst_dir, exist_ok=True)
        for filename in filenames:
            src = os.path.join(dirpath, filename)
            dst = os.path.join(dst_dir, filename)
            print(f"Copying {src} -> {dst}")
            shutil.copy(src, dst)


def main():
    build()
    text_node = TextNode(
        "This is some anchor text", TextType.LINK, "https://www.boot.dev"
    )
    print(text_node)


if __name__ == "__main__":
    main()
