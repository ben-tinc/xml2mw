#!/usr/bin/env python3

"""
Unit tests for transform.py
"""

from unittest import TestCase

from transform import to_mw


class TransformToMW(TestCase):
    """TestCases for transformation to media wiki markup.

    Note, that `to_mw()` returns a generator, so we need to
    consume it with e.g. `list()` or `'\n'.join()` to generate
    an actual result.
    """

    def test_empty_page(self):
        """A completely empty body should yield an empty generator."""
        page_body = ''
        result = '\n'.join(to_mw(page_body))
        expected = ''
        self.assertEqual(result, expected)

    def test_various_headings(self):
        """Test transformation of heading markup."""
        page_body = 'h1. H1\nh2. H2\nh3. H3\nh4. H4\n'
        result = '\n'.join(to_mw(page_body))
        expected = '= H1 =\n== H2 ==\n=== H3 ===\n==== H4 ====\n'
        self.assertEqual(result, expected)

    def test_inline_markup(self):
        """The markup which is currently implemented must be at the
        beginning of lines, i.e. a `h1. ` in the middle of a line
        should not be interpreted as heading markup.
        """
        page_body = 'h1. A Heading\n\nA line with h1. in it.\n'
        result = '\n'.join(to_mw(page_body))
        expected = '= A Heading =\n\nA line with h1. in it.\n'
        self.assertEqual(result, expected)
