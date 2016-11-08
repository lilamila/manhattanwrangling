#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Processes the map file and finds out what and how many tags there are.
Returns a dictionary with the tag name as the key and number of times this tag can be encountered in the map as value.

"""
import xml.etree.cElementTree as ET
import pprint
import re
import operator

OSMFILE = './small_sample.osm'


def count_tags(filename, limit=-1):
    # create dict objects
    tag_count = {}
    tag_keys = {}

    #iterate through elements
    for event, elem in ET.iterparse(filename, events=("start",)):
        # add to count
        counter(elem.tag, tag_count)

        if elem.tag == 'tag' and 'k' in elem.attrib:
            counter(elem.get('k'), tag_keys)

        if limit > 0 and counter >= limit:
            break

    # produces a sorted-by-decreasing list of tag key-count pairs
    tag_keys = sorted(tag_keys.items(), key=operator.itemgetter(1))[::-1]
    return tag_count, tag_keys

def counter(elem, dictionary):
    if elem in dictionary:
        dictionary[elem] += 1
    else:
        dictionary[elem] = 1


def main():
    """main function"""
    tags, tag_keys = count_tags(OSMFILE)
    print "TAGS:"
    pprint.pprint(tags)
    print ""
    print "KEYS:"
    pprint.pprint(tag_keys)


if __name__ == "__main__":
    main()