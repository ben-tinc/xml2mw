#!/usr/bin/env python3

"""
Unit tests for read_xml.py
"""

from unittest import TestCase

from lxml import etree

from xml2mw.read_xml import (
    denormalize,
    filter_most_recent,
    parse_page_data,
    parse_xml,
    retrieve_all_pages,
)

DUMMY_XML = """<hibernate-generic datetime="2018-03-04 23:31:58">
<object class="Page" package="com.atlassian.confluence.pages">
    <id name="id">32407574</id>
    <property name="position">7</property>
    <property name="parent" class="Page" package="com.atlassian.confluence.pages"><id name="id">21823489</id>
    </property>
    <collection name="children" class="java.util.Collection">
        <element class="Page" package="com.atlassian.confluence.pages"><id name="id">39550983</id></element>
    </collection>
    <property name="title"><![CDATA[ADHO Committee Appointments]]></property>
    <collection name="bodyContents" class="java.util.Collection">
        <element class="BodyContent" package="com.atlassian.confluence.core"><id name="id">32440342</id></element>
    </collection>
    <property name="version">83</property>
    <property name="creatorName"><![CDATA[adhosc]]></property>
    <property name="creationDate">2012-07-13 15:02:49.000</property>
    <property name="lastModifierName"><![CDATA[adhosc]]></property>
    <property name="lastModificationDate">2015-11-24 18:27:47.000</property>
    <property name="contentStatus"><![CDATA[current]]></property>
</object>
<object class="BodyContent" package="com.atlassian.confluence.core">
    <id name="id">32440342</id>
    <property name="body"><![CDATA[h2. This is a header
    This is the body.]]></property>
    <property name="content" class="Page" package="com.atlassian.confluence.pages"><id name="id">32407574</id></property>
</object>
</hibernate-generic>
"""

class TestDenormalize(TestCase):
    """TODO: Test cases for `denormalize()`."""


class TestParsePageData(TestCase):
    """TODO: Test cases for `parse_page_data()`."""


class TestFilter(TestCase):
    """Test cases for `filter_most_recent()`."""

    def setUp(self):
        # Two pages which only differ in lastModificationDate and ID.
        self.pages = {
            '32407574': {
                'bodyContents': '32440342',
                'children': '39550983',
                'contentStatus': 'current',
                'creationDate': '2012-07-13 15:02:49.000',
                'creatorName': 'adhosc',
                'id': '32407574',
                'lastModificationDate': '2015-11-24 18:27:47.000',
                'parent': '21823489',
                'position': '7',
                'title': 'ADHO Committee Appointments',
                'version': '83',
            },
            '999999999': {
                'bodyContents': '32440342',
                'children': '39550983',
                'contentStatus': 'current',
                'creationDate': '2012-07-13 15:02:49.000',
                'creatorName': 'adhosc',
                'id': '999999999',
                'lastModificationDate': '2015-11-24 18:27:53.000',
                'parent': '21823489',
                'position': '7',
                'title': 'ADHO Committee Appointments',
                'version': '83',
            },
        }

    def test_known_content(self):
        filtered = filter_most_recent(self.pages)
        self.assertEqual(len(filtered), 1)
        self.assertTrue('999999999' in filtered.keys())


class TestRetrieveAllPages(TestCase):
    """Test cases for `retrieve_all_pages()`."""

    def setUp(self):
        self.root = etree.fromstring(DUMMY_XML)

    def test_known_content(self):
        pages = retrieve_all_pages(self.root)
        self.assertEqual(len(pages), 1)
        self.assertTrue('32407574' in pages.keys())
        expected = {
            'bodyContents': '32440342',
            'children': '39550983',
            'contentStatus': 'current',
            'creationDate': '2012-07-13 15:02:49.000',
            'creatorName': 'adhosc',
            'id': '32407574',
            'lastModificationDate': '2015-11-24 18:27:47.000',
            'parent': '21823489',
            'position': '7',
            'title': 'ADHO Committee Appointments',
            'version': '83',
        }
        self.assertDictEqual(expected, pages['32407574'])
