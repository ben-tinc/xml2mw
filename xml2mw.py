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

from os.path import abspath, basename, dirname, join, normpath

import read_xml
from sitemap import build_sitemap, write_sitemap
from write_markup import write_mediawiki

# Modify this to suit your needs.
XML_PATH = "./data"           # path to folder which contains your 'entities.xml' export file
OUT_PATH = "./output/sc/"     # where to store the results

# Do NOT modify this.
BASE_PATH = dirname(abspath(__file__))
TEMPLATE_PATH = join(BASE_PATH, "templates")
PLAIN_TEMPLATE = join(TEMPLATE_PATH, "plain_template.txt")
MEWI_TEMPLATE = join(TEMPLATE_PATH, "mw_template.txt")


def main():
    """Run the actual script"""
    # Retrieve all the page data from XML export file.
    pages = read_xml.read(join(BASE_PATH, 'entities.xml'))

    # Generate a sitemap visualization of the tree structure of the pages.
    sitemap_root = build_sitemap(pages)
    write_sitemap(sitemap_root, "sitemap.txt")

    # Write markup output files.
    write_mediawiki(pages, OUT_PATH, MEWI_TEMPLATE)


if __name__ == "__main__":
    main()
