#!/usr/bin/env python3

"""
Unit tests for transform.py
"""

from unittest import TestCase

from xml2mw.transform import to_mw


class TransformEdgeCases(TestCase):
    """Some general tests which do not fit into any 
    other category.
    """

    def test_empty_page(self):
        """A completely empty body should yield an empty generator."""
        page_body = ''
        expected = ''
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)


class TransformHeadings(TestCase):
    """TestCases for transformation of headings, which can only
    be at the beginning of lines.

    Note, that `to_mw()` returns a generator, so we need to
    consume it with e.g. `list()` or `'\n'.join()` to generate
    an actual result.
    """

    def test_various_headings(self):
        """Test transformation of heading markup."""
        page_body = 'h1. H1\nh2. H2\nh3. H3\nh4. H4\n'
        expected = '= H1 =\n== H2 ==\n=== H3 ===\n==== H4 ====\n'
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)

    def test_no_inline_headings(self):
        """Most markup which is currently implemented must be at the
        beginning of lines, i.e. a `h1. ` in the middle of a line
        should not be interpreted as heading markup.
        """
        page_body = 'h1. A Heading\n\nA line with h1. in it.\nA line with h3. in it.\n'
        expected = '= A Heading =\n\nA line with h1. in it.\nA line with h3. in it.\n'
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)


class TransformLists(TestCase):
    """Test cases for transformation of unordered and ordered lists.

    Note, that most of the list syntax is identical for confluence
    and mediawiki markup, so for many of these tests, `to_mw()`
    should actually be a no-op.
    Also note that because `to_mw()` returns a generator, we need
    to consume it with e.g. `list()` or `'\n'.join()` to generate
    an actual result.
    """

    def test_unordered_list_a(self):
        """There are two versions of unordered list items in
        confluence markup, this tests the `*` version.
        """
        page_body = 'Some text.\n* first item.\n* second item.\n'
        expected = 'Some text.\n* first item.\n* second item.\n'
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)
    
    def test_unordered_list_b(self):
        """There are two versions of unordered list items in
        confluence markup, this tests the `-` version.
        """
        page_body = 'Some text.\n- first item.\n- second item.\n'
        expected = 'Some text.\n* first item.\n* second item.\n'
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)
    
    def test_nested_unordered_lists_a(self):
        """Test nested unordered lists of type `*`, but not mixed ones."""
        page_body = 'Some text.\n* first level, first item\n** second level, first item\n** second level, second item\n* first level, second item\n'
        expected = 'Some text.\n* first level, first item\n** second level, first item\n** second level, second item\n* first level, second item\n'
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)
    
    def test_nested_unordered_lists_b(self):
        """Test nested unordered lists of type `-`, but not mixed ones."""
        page_body = 'Some text.\n- first level, first item\n-- second level, first item\n-- second level, second item\n- first level, second item\n'
        expected = 'Some text.\n* first level, first item\n** second level, first item\n** second level, second item\n* first level, second item\n'
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)
    
    def test_ordered_list(self):
        """Test if ordered list items are transformed correctly."""
        page_body = 'Some text.\n# first item\n# second item\n'
        expected = 'Some text.\n# first item\n# second item\n'
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)
    
    def test_nested_ordered_lists(self):
        """Test nested ordered lists, but not mixed ones."""
        page_body = 'Some text.\n# first, first\n## second, first\n## second, second\n# first, second\n'
        expected = 'Some text.\n# first, first\n## second, first\n## second, second\n# first, second\n'
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)

    def test_mixed_lists(self):
        """Ordered and unordered lists can be mixed."""
        page_body = '# first\n#* mixed\n#* list\n# for us\n'
        expected = '# first\n#* mixed\n#* list\n# for us\n'
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)
    
    def test_no_inline_ordered_lists(self):
        """Ordered lists must start at the beginning of a line."""
        page_body = 'Some text with # a pseudo list\nSome more ## fake lists\n'
        expected = 'Some text with # a pseudo list\nSome more ## fake lists\n'
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, expected)
    
    def test_no_inline_unordered_lists(self):
        """Unordered lists must start at the beginning of a line."""
        # Note: we don't test for unordered lists with `*`, because these
        # would indicate emphasis when not used at the beginning of the line.
        page_body = 'Some text with - a pseudo-list\nSome more -- fake lists.\n'
        # Should be a no-op.
        result = '\n'.join(to_mw(page_body))
        self.assertEqual(result, page_body)


class TransformEmphasis(TestCase):
    """TestCases for transformations of emphasis, which can occur anywhere
    in a line.

    Note, that `to_mw()` returns a generator, so we need to
    consume it with e.g. `list()` or `'\n'.join()` to generate
    an actual result.
    """

    def test_light_emphasis(self):
        """This type of emphasis is normally rendered as cursive text."""
        known_items = [
            ("text with _inline emphasis_ and more text", "text with ''inline emphasis'' and more text"),
            ("_emphasis at the beginning_ and more text", "''emphasis at the beginning'' and more text"),
            ("emphasis with following _non-white-space_, and text", "emphasis with following ''non-white-space'', and text"),
        ]
        for page_body, expected in known_items:
            result = '\n'.join(to_mw(page_body))
            self.assertEqual(result, expected)
    
    def test_strong_emphasis(self):
        """This type of emphasis is normally rendered as bold text."""
        known_items = [
            ("text with *inline emphasis* and more text", "text with '''inline emphasis''' and more text"),
            ("*emphasis at the beginning* and more text", "'''emphasis at the beginning''' and more text"),
            ("emphasis with following *non-white-space*, and text", "emphasis with following '''non-white-space''', and text"),
        ]
        for page_body, expected in known_items:
            result = '\n'.join(to_mw(page_body))
            self.assertEqual(result, expected)
    
    def test_very_strong_emphasis(self):
        """This type of emphasis is normally rendered as both bold and
        cursive text.
        """
        known_items = [
            ("text with *_inline emphasis_* and more text", "text with '''''inline emphasis''''' and more text"),
            ("*_emphasis at the beginning_* and more text", "'''''emphasis at the beginning''''' and more text"),
            ("emphasis with following *_non-white-space_*, and text", "emphasis with following '''''non-white-space''''', and text"),
            ("text with _*inline emphasis*_ and more text", "text with '''''inline emphasis''''' and more text"),
            ("_*emphasis at the beginning*_ and more text", "'''''emphasis at the beginning''''' and more text"),
            ("emphasis with following _*non-white-space*_, and text", "emphasis with following '''''non-white-space''''', and text"),
        ]
        for page_body, expected in known_items:
            result = '\n'.join(to_mw(page_body))
            self.assertEqual(result, expected)


class TransformLinks(TestCase):
    """TestCases for links, both internal wiki links as well as
    external links.
    """
    def test_internal_link(self):
        """An internal link without special label text."""
        lines = [
            ('A line with a [PageLink] in it.\n' ,'A line with a [[PageLink]] in it.\n'),
            ('This line ends with [PageLink].\n', 'This line ends with [[PageLink]].\n'),
            ('[PageLink] at the start.\n', '[[PageLink]] at the start.\n'),
        ]
        for confluence, mediawiki in lines:
            result = '\n'.join(to_mw(confluence))
            self.assertEqual(result, mediawiki)

    def test_internal_link_with_anchor(self):
        """An internal link without special label text but with anchor element."""
        lines = [
            ('A line with a [PageLink#anchor] in it.\n' ,'A line with a [[PageLink#anchor]] in it.\n'),
            ('This line ends with [PageLink#anchor].\n', 'This line ends with [[PageLink#anchor]].\n'),
            ('[PageLink#anchor] at the start.\n', '[[PageLink#anchor]] at the start.\n'),
        ]
        for confluence, mediawiki in lines:
            result = '\n'.join(to_mw(confluence))
            self.assertEqual(result, mediawiki)

    def test_internal_link_with_label(self):
        """An internal link with custom label text."""
        lines = [
            ('A line with a [My Label|PageLink#anchor] in it.\n' ,'A line with a [[PageLink#anchor|My Label]] in it.\n'),
            ('This line ends with [My Label|PageLink#anchor].\n', 'This line ends with [[PageLink#anchor|My Label]].\n'),
            ('[My Label|PageLink#anchor] at the start.\n', '[[PageLink#anchor|My Label]] at the start.\n'),
        ]
        for confluence, mediawiki in lines:
            result = '\n'.join(to_mw(confluence))
            self.assertEqual(result, mediawiki)

    def test_external_link(self):
        """An external link. In this specific case, `to_mw()` should
        be a no-op.
        """
        lines = [
            ('A line with a [https://example.com/page#anchor] in it.\n' ,'A line with a [https://example.com/page#anchor] in it.\n'),
            ('This line ends with [https://example.com/page#anchor].\n', 'This line ends with [https://example.com/page#anchor].\n'),
            ('[https://example.com/page#anchor] at the start.\n', '[https://example.com/page#anchor] at the start.\n'),
        ]
        for confluence, mediawiki in lines:
            result = '\n'.join(to_mw(confluence))
            self.assertEqual(result, mediawiki)
    
    def test_external_link_with_label(self):
        """An external link with custom label text. Contrary to the version without label,
        the syntax of mediawiki and confluence differs slightly.
        """
        lines = [
            ('A line with a [My Label|https://example.com/page#anchor] in it.\n' ,'A line with a [https://example.com/page#anchor My Label] in it.\n'),
            ('This line ends with [My Label|https://example.com/page#anchor].\n', 'This line ends with [https://example.com/page#anchor My Label].\n'),
            ('[My Label|https://example.com/page#anchor] at the start.\n', '[https://example.com/page#anchor My Label] at the start.\n'),
        ]
        for confluence, mediawiki in lines:
            result = '\n'.join(to_mw(confluence))
            self.assertEqual(result, mediawiki)
