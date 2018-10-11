#!/usr/bin/env python3
#
# mw_writer.py
# Copyright (C) 2018  Henning Gebhard

"""
Generate MediaWiki markup out of confluence markup.
"""

# Some basic template strings
MARKUP = {
    'h1': '# {}',
    'h2': '## {}',
    'h3': '### {}',
    'h4': '#### {}',
    'p': '\n{}',
    'hr': '----{}',
    'uli': ' * {}',
    'oli': ' 1. {}',
}

CONFLUENCE_MU = {
    'h1. ': 'h1',
    'h2. ': 'h2',
    'h3. ': 'h3',
    'h4. ': 'h4',
    '\n': 'p',
    '* ': 'uli',
}


def to_mw(body_content):
    """Parse string with confluence markup."""
    for line in body_content.split('\n'):
        result = ''
        # Check if the beginning of the line is relevant.
        for confluence, tag in CONFLUENCE_MU.items():
            if line.startswith(confluence):
                rest = line.lstrip(confluence)
                result = __get_markup(tag, rest)
                break
        # Either yield the freshly created result, or the original line.
        yield result or line


def __get_markup(tag, content=''):
    try:
        return MARKUP[tag].format(content)
    except KeyError:
        return ''
