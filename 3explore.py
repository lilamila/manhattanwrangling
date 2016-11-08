#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Explores the contents of the tags and their keys.
"""
from collections import defaultdict
from pprint import pprint
import re
import json
import xml.etree.cElementTree as ET

# use __import__ to import module that begins with an int
parse = __import__('2parse')

OSMFILE = './small_sample.osm'


def examine_tags(osmfile, item_limit):
    # call 2parse count_tags method to pull sorted list of top tags
    _, tag_keys = parse.count_tags(osmfile)
    # list comprehension for producing a list of tag_keys in string format
    tag_keys = [tag_key[0] for tag_key in tag_keys]
    # print "Examining tag keys: {}".format(tag_keys)

    # open osm file
    osm_file = open(osmfile, "r")

    # initialize data with default set data structure
    data = defaultdict(set)

    # iterate through elements
    for _, elem in ET.iterparse(osm_file, events=("start",)):
        # check if the element is a node or way
        if elem.tag == "node" or elem.tag == "way":
            # iterate through children matching `tag`
            for tag in elem.iter("tag"):
                # skip if does not contain key-value pair
                if 'k' not in tag.attrib or 'v' not in tag.attrib:
                    continue
                key = tag.get('k')
                val = tag.get('v')
                # add to set if keys to explore set is below the item limit
                if key in tag_keys and len(data[key]) < item_limit:
                    data[key].add(val)
    return data

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        key = element.get('k')
        # print "Key name: ", key
        if lower.search(key):
           keys['lower'] += 1
        elif lower_colon.search(key):
            keys['lower_colon'] += 1
        elif problemchars.search(key):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1
    return keys


def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys


def main():
    keys = process_map(OSMFILE)

    # call examine_tags function
    tag_data = dict(examine_tags(OSMFILE, item_limit=15))

    # pretty print
    pprint(tag_data)

    # call key_types function
    print "Examine key character types (for MongoDB normalization/appropriateness): "
    print pprint(keys)



if __name__ == "__main__":
    main()