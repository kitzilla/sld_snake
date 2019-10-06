import os
from lxml import etree
import xml.etree.ElementTree as ET

if __name__ == "__main__":
    curdir = os.path.dirname(__file__)
    tree = ET.parse(os.path.join(curdir, "test.sld") )
    root = tree.getroot()
    # print(root.nsmap)
    print(root.find('.//{http://www.opengis.net/se}NamedLayer'))