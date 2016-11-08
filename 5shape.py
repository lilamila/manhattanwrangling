#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shapes the raw OSM data into a format that looks like:

{
"id": "2406124091",
"type: "node",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}


Imports functions from the audit module to clean/update the data.
Processes 2 top level tags: "node" and "way"
All attributes of "node" and "way" are turned into regular key/value pairs, except:
    - attributes in the CREATED array added under a key "created"
    - attributes for latitude and longitude added to a "pos" array,
      for use in geospacial indexing.
- if second level tag "k" value contains problematic characters, it is ignored
- if second level tag "k" value starts with "addr:", it is added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", it is processed like any other tag
- if there is a second ":" that separates the type/direction of a street,
  the tag is ignored and subtags are compiled into one tag.
- ignores gnis tags

"""
import xml.etree.cElementTree as ET
from pprint import pprint
import re
import codecs
import json
from collections import OrderedDict
# use __import__ to import module that begins with an int
audit = __import__('4audit')

OSMFILE = './new-york_new-york.osm'

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

address_re = re.compile(r'^addr\:')
street_re = re.compile(r'^street')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
zipcode_re = re.compile(r'[^0-9\-]', re.IGNORECASE)
gnis_re = re.compile(r'^gnis\:')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
position_attributes = ['lat', 'lon']

ZIPCODES = ['addr:postcode', 'tiger:zip_left', 'tiger:zip_left_1', 'tiger:zip_left_2',
    'tiger:zip_left_3', 'tiger:zip_left_4', 'tiger:zip_right', 'tiger:zip_right_1',
    'tiger:zip_right_2', 'tiger:zip_right_3', 'tiger:zip_right_4']


def shape_element(element):
    node = {}
    address = {}

    if element.tag == "node" or element.tag == "way":
        # populate tag type
        node['type'] = element.tag

        # parse through attributes
        for attribute in element.attrib:
            if attribute in CREATED:
                if 'created' not in node:
                    node['created'] = {}
                node['created'][attribute] = element.get(attribute)
            elif attribute in position_attributes:
                continue
            else:
                node[attribute] = element.get(attribute)

        # populate position
        if 'lat' in element.attrib and 'lon' in element.attrib:
            node['pos'] = [float(element.get('lat')), float(element.get('lon'))]

        # parse second-level tags
        for second in element:

            #populate `node_refs`
            if second.tag == 'nd':
                if 'node_refs' not in node:
                    node['node_refs'] = []
                if 'ref' in second.attrib:
                    node['node_refs'].append(second.get('ref'))

            # pass non-tag elements and elements without `k` or `v`
            if second.tag != 'tag'\
            or 'k' not in second.attrib\
            or 'v' not in second.attrib:
                continue

            # populate k-v pairs
            k = second.get('k')
            v = second.get('v')

            # skip any gnis tags
            if gnis_re.search(k):
                continue

            # skip problem characters
            if problemchars.search(k):
                continue

            # extract zipcodes
            if k in ZIPCODES:
                node['zipcode'] = v
                k.replace(k, 'zipcode')


            # parse and strip address values from k-v pairs
            if address_re.search(k):
                key = k.replace('addr:', '')
                address[key] = v
                continue

            # catch all tag attributes
            if k not in node:
                node[k] = v


        # compile address
        if address:
            node['address'] = {}
            street = None
            street_unjoin = {}
            street_dict = ['prefix', 'name', 'type']
            # parse through address objects
            for key in address:
                val = address[key]
                if key == 'street':
                    street = val
                elif 'street:' in key:
                    street_unjoin[key.replace('street:', '')] = val
                else:
                    node['address'][key] = val
            # assign street or fallback to compile street_unjoin(ed)
            if street:
                node['address']['street'] = street
            elif len(street_unjoin) > 0:
                node['address']['street'] = ' '.join([street_unjoin[key] for key in street_dict])
        return node
    else:
        return None


### function for writing the cleaned data into a json file
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def main():
    process_map(OSMFILE)
    print "Check to see if JSON file created successfully"
    # pprint(data)

if __name__ == "__main__":
    main()