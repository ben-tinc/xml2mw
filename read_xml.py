#!/usr/bin/env python3
#
# Filename: read_xml.py
# Copyright (C) 2018  Henning Gebhard

"""
Read XML export from a confluence wiki instance and try
to recreate the page contents.
"""

from datetime import datetime

from lxml import etree


class RetrievalError(RuntimeError):
    """Indicates that some necessary data could not be retrieved from the XML."""


def read(filepath):
    """Facade and main entry point to the module. Retrieves all pages of an XML export.

    - Reads and parses a xml file.
    - Retrieves all page data.
    - Filters all but the most recent pages.
    - Acquires linked content of the pages.
    """
    try:
        root = parse_xml(filepath)
        pages = retrieve_all_pages(root)
        pages = filter_most_recent(pages)
        pages = denormalize(root, pages)
    except:
        print("Could not execute read_xml.read().")

    return pages


def denormalize(root, pages):
    """Merge content like 'bodyContents' or links, which are stored in separate
    elements in the XML, with their respective page data.
    """
    for page_id, page_data in pages.items():
        # Retrieve bodyContents element.
        page_data['body'] = _get_body_content(root, page_data['bodyContents'])
    return pages


def filter_most_recent(pages):
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
            this_date = datetime.strptime(values['lastModificationDate'], dt_format)
            other_date = datetime.strptime(other['lastModificationDate'], dt_format)

            if other_date < this_date:
                recent_pages[identifier] = values

    # Build list of recent page ids.
    recent_ids = [value['id'] for value in recent_pages.values()]
    # Filter the original pages so only the most recent remain.
    filtered = {k: v for k, v in pages.items() if k in recent_ids}

    return filtered


def parse_page_data(elem, root):
    """Given a page element, retrieve its page data.

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
            elif name == 'parent':
                data['parent'] = child.find('id').text
        # Collection elements can be 'children', 'bodyContents',
        # 'outgoingLinks', 'referralLinks' or something irrelevant for us.
        if child.tag == 'collection':
            relevant = ['children', 'bodyContents', 'outgoingLinks', 'referralLinks']
            if name in relevant:
                # All collections contain element tags with class "Page",
                # "BodyContent", "ReferralLinks" a.s.o. Each of these
                # contain an id tag with the id as text.
                ids = _unpack_collection(child)
                data[name] = ",".join(ids)
    return data


def parse_xml(path):
    """Build etree from filepath and return its root element."""
    tree = etree.parse(path)
    return tree.getroot()


def retrieve_all_pages(root):
    """Build pages from xml tree."""
    pages = {}
    for element in root.findall('object[@class="Page"]'):
        page = parse_page_data(element, root)
        if page:
            pages[page['id']] = page
    return pages


def _get_body_content(root, obj_ids):
    """Helper function to retrieve text of BodyContent objects for a given id."""
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


def _include_current_pages(children):
    """Helper function to decide wether there is at least one current
    page in `children`.
    """
    return len([c for c in children if _is_current_page(c)]) != 0


def _is_current_page(elem):
    """Helper function to check if a given page element states that `contentStatus`
    is `current`.
    """
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
