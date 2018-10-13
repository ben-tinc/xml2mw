#!/usr/bin/env python3

"""
Unit tests for sitemap.py
"""

from unittest import TestCase

from xml2mw.sitemap import build_sitemap


class TestBuildSitemap(TestCase):
    """Test cases for the creation of a sitemap."""

    def test_empty_page_dict(self):
        """No pages, no sitemap."""
        pages = {}
        root_node = build_sitemap(pages)
        # `root_node` should be both root and leaf ie. the tree is empty.
        self.assertTrue(root_node.is_root)
        self.assertTrue(root_node.is_leaf)

    def test_flat_page_dict(self):
        """Test creation of sitemap with only toplevel pages."""
        pages = {
            '1': {'title': '1', 'id': '1'},
            '2': {'title': '2', 'id': '2'},
            '3': {'title': '3', 'id': '3'},
        }
        root_node = build_sitemap(pages)
        self.assertFalse(root_node.is_leaf)
        self.assertEqual(len(root_node.descendants), 3)
        self.assertEqual(len(root_node.children), 3)

    def test_deep_page_dict(self):
        """Test creation of sitemap with nested pages."""
        pages = {
            '1': {'title': '1', 'id': '1', 'children': '2,3'},
            '2': {'title': '2', 'id': '2', 'children': '4', 'parent': '1'},
            '3': {'title': '3', 'id': '3', 'parent': '1'},
            '4': {'title': '4', 'id': '4', 'parent': '2'},
        }
        root_node = build_sitemap(pages)
        self.assertFalse(root_node.is_leaf)
        self.assertEqual(len(root_node.children), 1)
        self.assertEqual(len(root_node.descendants), 4)

    def test_pages_without_title(self):
        """Sitemap creation should fail when pages have not title."""
        pages = {
            '1': {'id': '1', 'children': '2,3'},
            '2': {'id': '2', 'children': '4', 'parent': '1'},
            '3': {'id': '3', 'parent': '1'},
            '4': {'id': '4', 'parent': '2'},
        }
        self.assertRaises(KeyError, build_sitemap, pages)
