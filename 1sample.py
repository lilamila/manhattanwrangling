""" code to convert osm file to smaller sample osm file"""

import xml.etree.ElementTree as ET

OSM_FILE = "./new-york_new-york.osm"
SAMPLE_FILE = "new-york_mini.osm"


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every nth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % 10 == 0: # change number after modulo to get different sample.osm characteristics
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')