#!/usr/bin/env python3
#
# xml2mw.py
#
# Copyright (C) 2018  Henning Gebhard

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Recreate mediawiki markup pages from a confluence xml export directory.
"""

from datetime import datetime
from os.path import abspath, basename, dirname, join, normpath

from lxml import etree

# Modify this to suit your needs.
XML_PATH = "./data"                 # path to your xml export
OUT_PATH = "./output/sc/"            # where to store the results

# Do NOT modify this.
BASE_PATH = dirname(abspath(__file__))
TEMPLATE_PATH = join(BASE_PATH, "templates")
PLAIN_TEMPLATE = join(TEMPLATE_PATH, "plain_template.txt")
HTML_TEMPLATE = join(TEMPLATE_PATH, "html_template.txt")
MEWI_TEMPLATE = join(TEMPLATE_PATH, "mw_template.txt")


class RetrievalError(RuntimeError):
    """Some necessary data could not be retrieved from the XML."""


def parse(path):
    """Build etree from filepath and return its root."""
    tree = etree.parse(path)
    return tree.getroot()


def parse_page_data(elem, root):
    """Given a page element, create a page object.

    An element of class "Page" has several children with important
    semantics for our use case:

        - 'id' tag with numeric id value as text
        - 'collection' tag with name attrib 'children'
        - 'collection' tag with name attrib 'bodyContents'
        - 'collection' tag with name attrib 'outgoingLinks'
        - 'collection' tag with name attrib 'referralLinks'
        - 'property' tag with name attrib 'title' and the page title as text
        - 'property' tag with name attrib 'creationDate' and date as text
        - 'property' tag with name attrib 'lastModificationDate' and date as text
        - 'property' tag with name attrib 'creatorName' with username as text
        - 'property' tag with name attrib 'contentStatus', with e.g. "current" as text
    """
    children = elem.getchildren()
    # Create no page if there is no contentStatus that is exactly "current".
    # It seems like there are actually no top level page objects that do not
    # have that trait, but we check for it anyway just to be sure.
    if not _include_current_pages(children):
        return {}
    data = {}

    for child in children:
        name = child.attrib.get('name', '')
        # Check for some common child elements.
        if child.tag == 'id':
            data['id'] = child.text
        # Property elements can be 'creatorName', 'creationDate',
        # 'lastModificationDate', 'title' or something else we are
        # not interested in.
        if child.tag == 'property':
            relevant = ['creatorName', 'creationDate', 'lastModificationDate', 'title', 'position', 'version', 'contentStatus']
            if name in relevant:
                data[name] = child.text
        # Collection elements can be 'children', 'bodyContents',
        # 'outgoingLinks', 'referralLinks' or something irrelevant for us.
        if child.tag == 'collection':
            relevant = ['children', 'bodyContents', 'outgoingLinks', 'referralLinks']
            if name in relevant:
                # Do stuff with these collections...
                # All collections contain element tags with class "Page",
                # "BodyContent", "ReferralLinks" a.s.o. Each of these
                # contain an id tag with the id as text.
                ids = _unpack_collection(child)
                data[name] = ",".join(ids)
                # if name == 'bodyContents':
                #     data['body'] = _get_body_content(root, data[name])
    return data


def build_pages(root):
    """Build pages from xml tree."""
    pages = {}
    for element in root.findall('object[@class="Page"]'):
        page = parse_page_data(element, root)
        if page:
            pages[page['id']] = page
    return pages


def filter_pages(pages):
    """When one or more pages have the same title and creationDate, only
    use the one with the most recent lastModificationDate.
    """
    # Build a hash map of recent pages to look up.
    recent_pages = {}
    for key, values in pages.items():
        identifier = "{}#{}".format(values['title'], values['creationDate'])
        other = recent_pages.get(identifier, None)
        # If there is no other page, use the current page.
        if other is None:
            recent_pages[identifier] = values
        # Else check which version is the most recent.
        # We don't use confluences version number directly, but instead the
        # lastModificationDate, as it seems to be the most robust way.
        else:
            dt_format = "%Y-%m-%d %H:%M:%S.%f"
            other_date = datetime.strptime(other['lastModificationDate'], dt_format)
            this_date = datetime.strptime(values['lastModificationDate'], dt_format)
            if other_date < this_date:
                recent_pages[identifier] = values

    # Build list of recent page ids.
    recent_ids = [value['id'] for value in recent_pages.values()]
    # Filter the original pages so only the most recent remain.
    filtered = {k: v for k, v in pages.items() if k in recent_ids}

    return filtered


def denormalize(root, pages):
    """Merge content like 'bodyContents' or links, which are stored in separate
    elements in the XML, with their respective page data.
    """
    for page_id, page_data in pages.items():
        # Retrieve bodyContents element.
        page_data['body'] = _get_body_content(root, page_data['bodyContents'])
    return pages


def write_markup(pages, path, template):
    """Write a markup file for each page recovered from the XML."""
    with open(template) as tmpl_file:
        tmpl = tmpl_file.read()

    for page_id, page_data in pages.items():
        body = page_data.get('body', '')
        filename = page_data.get('title', '') + '_' + str(page_id) + '.txt'
        filepath = join(path, filename)
        d = {
            'body': body,
            'title': filename,
            'version': page_data.get('version'),
            'current': page_data.get('contentStatus'),
            'created': page_data.get('creationDate'),
            'latest_mod': page_data.get('lastModificationDate'),
            'position': page_data.get('position'),
        }
        filecontent = tmpl.format(**d)

        with open(filepath, 'w') as outfile:
            outfile.write(filecontent)


def _include_current_pages(children):
    return len([c for c in children if _is_current_page(c)]) != 0


def _is_current_page(elem):
    return elem.attrib.get('name', '') == 'contentStatus' and elem.text == 'current'


def _unpack_collection(elem):
    """All collections contain element tags with class "Page",
    "BodyContent", "ReferralLinks" a.s.o. Each of these
    contain an id tag with the id as text.

    Return a list of these ids.
    """
    ids = []
    for element in elem.getchildren():
        for _id in element.getchildren():
            ids.append(_id.text)
    return ids


def _get_body_content(root, obj_ids):
    """Retrieve text of BodyContent objects for a given id."""
    # <object class="BodyContent" package="com.atlassian.confluence.core">
    body_text = []
    for obj_id in obj_ids.split(","):
        query = './/object[@class="BodyContent"]/id[text()="{}"]'.format(obj_id)
        id_element = root.xpath(query)

        if not len(id_element):
            msg = "BodyContent with id {} not found.".format(obj_id)
            raise RetrievalError(msg)

        body = id_element[0].getparent().find('property[@name="body"]')

        try:
            body_text.append(body.text)
        except AttributeError:
            msg = "No actual body element found for {}".format(obj_id)
            raise RetrievalError(msg)

    return "\n".join(body_text)


def main():
    """Run the actual script"""
    root = parse(join(XML_PATH, "entities.xml"))
    pages = build_pages(root)
    print("Built %s pages." % len(pages))
    pages = filter_pages(pages)
    print("%s pages after filtering." % len(pages))
    pages = denormalize(root, pages)
    print("%s pages after denormalization." % len(pages))
    write_markup(pages, OUT_PATH, PLAIN_TEMPLATE)


if __name__ == "__main__":
    main()
