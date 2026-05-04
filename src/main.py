import os
import shutil

from markdown import extract_title, markdown_to_html_node
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


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path) as f:
        contents = f.read()
    with open(template_path) as f:
        template = f.read()

    html = markdown_to_html_node(contents).to_html()
    title = extract_title(contents)

    page = template.replace("{{ Title }}", title).replace("{{ Content }}", html)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(page)


def main():
    build()

    project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
    content_index = os.path.join(project_root, "content", "index.md")
    template_html = os.path.join(project_root, "template.html")
    public_index = os.path.join(project_root, "public", "index.html")

    generate_page(
        from_path=content_index, template_path=template_html, dest_path=public_index
    )


if __name__ == "__main__":
    main()
