#!/usr/bin/env python3
#
# Filename: mw_writer.py
# Copyright (C) 2018  Henning Gebhard

"""
Generate MediaWiki markup out of confluence markup.
"""

import re

# Some basic template strings
# The confluence -> mediawiki mapping is not a direct one
# to allow for some logic in an intermediate step.
MARKUP = {
    'h1': '= {} =',
    'h2': '== {} ==',
    'h3': '=== {} ===',
    'h4': '==== {} ====',
    # 'p': '<br />{}',
    'hr': '----{}',
    'uli': '* {}',
    'ulii': '** {}',
    'uliii': '*** {}',
    'oli': '# {}',
    'olii': '## {}',
    'oliii': '### {}',
}
CONFLUENCE_MU = {
    'h1. ': 'h1',
    'h2. ': 'h2',
    'h3. ': 'h3',
    'h4. ': 'h4',
    # '\n': 'p',
    '* ': 'uli',
    '- ': 'uli',   # alternate version
    '-- ': 'ulii',
    '--- ': 'uliii',
}
EMPHASIS = {
    '*': "'''",         # strong emphasis
    '_': "''",          # light emphasis
    '*_': "'''''",      # very strong emphasis
    '_*': "'''''",      # very strong emphasis (alternate)
}


def to_mw(body_content):
    """Parse string with confluence markup."""
    for line in body_content.split('\n'):
        possibly_changed = _transform_line_start(line)
        possibly_changed = _transform_inner_line(possibly_changed)

        # Either yield the freshly created result, or the original line.
        yield possibly_changed


def _transform_line_start(line):
    result = ''
    # Check if the beginning of the line is relevant.
    for confluence, tag in CONFLUENCE_MU.items():
        if line.startswith(confluence):
            rest = line.lstrip(confluence)
            line = __get_markup(tag, rest)
            result = line
            break
    return result or line


def _transform_inner_line(line):
    result = ''
    emphasis_pattern = re.compile(r'([\*_]+)(\S[^\*_]*)([\*_]+)')

    # Check if there is relevant markup anywhere in the line.
    for (start, content, end) in re.findall(emphasis_pattern, line):
        # start and end markup must match
        if start == end or start == end[::-1]:
            # If we don't have a replacement defined in EMPHASIS, do nothing.
            try:
                markup = EMPHASIS[start]
                replacement = '{}{}{}'.format(markup, content, markup)
                line = re.sub(emphasis_pattern, replacement, line, count=1)
                result = line
            except KeyError:
                continue
    return result or line


def __get_markup(tag, content=''):
    try:
        return MARKUP[tag].format(content)
    except KeyError:
        return ''
