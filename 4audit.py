
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from pprint import pprint
import re
import codecs
import json
from collections import OrderedDict, defaultdict

OSMFILE = './new-york_new-york.osm'

address_re = re.compile(r'^addr\:')
street_re = re.compile(r'^street')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
# zipcode_re = re.compile(r'[^0-9\-]', re.IGNORECASE)
gnis_re = re.compile(r'^gnis\:')


### expected street type
expected = ["Avenue", "Boulevard", "Broadway", "Circle", "Court", "Drive", \
            "Highway", "Lane", "Parkway", "Place", "Road", "Street", "Terrace", \
            "Way", "Square", "Trail",  "Commons", "West", "East", "South",\
             "North", "Park", "Promenade", "Turnpike", "Green", "Path",\
             "Plaza", "Extension", "Esplanade", 'Loop']

### street type conversion dictionary
mapping = { 'St'     : 'Street',
            'St.'    : 'Street',
            'street' : 'Street',
            'Street,': 'Street',
            'Rd'     : "Road",
            'Rd.'    : 'Road',
            'ROAD'   : 'Road',
            'road'   : 'Road',
            'Pkwy'   : 'Parkway',
            'Pky'    : 'Parkway',
            'Pl'     : 'Place',
            'Ln'     : 'Lane',
            'Hwy'    : 'Highway',
            'Dr'     : 'Drive',
            'Dr.'    : 'Drive',
            'Cir'    : 'Circle',
            'Blvd'   : 'Boulevard',
            'Blvd.'  : 'Boulevard',
            'ave'    : 'Avenue',
            'Ave'    : 'Avenue',
            'Ave.'   : 'Avenue',
            'Plz'    : 'Plaza',
            'Tpke'   : 'Turnpike',
            'Expy'   : 'Expressway',
            'WEST'   : 'West',
            'Hamilton': 'Hamilton Parkway',
            'Cir'    : 'Circle',
            'Ter'    : 'Terrace',
            'Ct'     : 'Court'}


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group().lower().title()
        if street_type not in expected and 'Avenue' not in street_name and 'Road' not in street_name:
            street_types[street_type].add(street_name)

# def audit_zipcode():
#     """ adds invalid zipcodes to a dict """
#     if not re.match(r'^\d{5}$', zipcode):
#         invalid_zipcodes[zipcode] += 1

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street"
            or elem.attrib['k'] == "tiger:name_type"
            or elem.attrib['k'] == "tiger:name_type_1"
            or elem.attrib['k'] == "tiger:name_type_2")

# def is_zipcode(elem):
#     """ returns if zip-code like """
#     return 'zip' in elem.attrib['k']


def audit(osmfile):
    osm_file = open(osmfile, "r")

    # initialize storage dictionary
    street_types = defaultdict(set)

    for _, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    elem.clear
    # pprint(dict(street_types))

    return street_types


def update_name(name, mapping):
    match = re.search(street_type_re, name)
    name = re.sub(street_type_re, mapping[match.group()],name)
    return name


def main():
    # call audit function and print data
    st_types = audit(OSMFILE)
    print "Dirty street types: "
    print ''
    pprint(dict(st_types))
    # pprint(zipcode_data)
    print ""
    print "Changes made: "
    print ''
    for st_type, ways in st_types.iteritems():

        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name

    # convert data to standard dicts
    street_data = dict(st_types)
    # zipcode_data = dict(zipcodes)

    # fix to JSON-read/writeable
    for key in street_data:
        street_data[key] = list(street_data[key])

    # dump data to JSON files
    json.dump(street_data, open(OSMFILE + '-street-audit.json', 'w'))
    # # json.dump(zipcode_data, open(OSMFILE + '-zipcode-audit.json', 'w'))

    # return data
    return street_data
    # return zipcode_data

if __name__ == "__main__":
    main()
