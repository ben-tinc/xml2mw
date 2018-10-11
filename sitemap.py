#!/usr/bin/env python3
#
# Filename: sitemap.py
# Copyright (C) 2018  Henning Gebhard

from anytree import Node, RenderTree


def build_sitemap(pages):
    """Build a tree of pages."""

    def _create_node(page, all_pages, parent):
        """Create nodes recursively until nodes have no children."""
        if not page: return

        current_title = page['title']
        current = Node(current_title, parent=parent)

        for child_id in page.get('children', '').split(','):
            child_page = all_pages.get(child_id)
            _create_node(child_page, all_pages, parent=current)

    rootNode = Node('/')
    toplevel = {k: v for k,v in pages.items() if not v.get('parent')}

    for page in toplevel.values():
        _create_node(page, pages, rootNode)

    return rootNode


def write_sitemap(rootNode, filename='sitemap.txt'):
    """Write visualization of sitemap to file."""
    s = []
    for pre, fill, node in RenderTree(rootNode):
        s.append("%s%s" % (pre, node.name))
    with open(filename, 'w') as sitemap:
        sitemap.write("\n".join(s))

