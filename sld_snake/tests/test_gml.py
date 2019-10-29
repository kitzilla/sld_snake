import json
import pytest
import re
import xml.etree.ElementTree as ET

from ..gml import Geometry



def test_Geometry_parse_gml():

    # Typical GML (no xmlns)
    gml2 = '''
    <gml:Polygon>
        <gml:outerBoundaryIs>
            <gml:LinearRing>
                <gml:coordinates>0,0 100,0 100,100 0,100 0,0</gml:coordinates>
            </gml:LinearRing>
        </gml:outerBoundaryIs>
    </gml:Polygon>
    '''
    root = Geometry._parse_gml(gml2)
    assert root.tag == '{http://www.opengis.net/gml}Polygon'

    # GML with no prefix
    gml3 = '''
    <LineString>
        <posList srsDimension="2">45.67 88.56 55.56 89.44</posList>
    </LineString >
    '''
    root = Geometry._parse_gml(gml3)
    assert root.tag == '{http://www.opengis.net/gml}LineString'

    # GML with different prefix (no xmlns)
    gml4 = '''
    <ns0:Polygon srsName="EPSG:3857">
        <ns0:outerBoundaryIs>
            <ns0:LinearRing>
                <ns0:coordinates>35,10 45,45 15,40 10,20 35,10</ns0:coordinates>
            </ns0:LinearRing>
        </ns0:outerBoundaryIs>
        <ns0:innerBoundaryIs>
            <ns0:LinearRing>
                <ns0:coordinates>20,30 35,35 30,20 20,30</ns0:coordinates>
            </ns0:LinearRing>
        </ns0:innerBoundaryIs>
    </ns0:Polygon>
    '''
    root = Geometry._parse_gml(gml4)
    assert root.tag == '{http://www.opengis.net/gml}Polygon'

    # GML with wrong(?) xmlns (illegal)
    gml5 = '''
    <gml:Polygon xmlns:gml="http://example.com/gml">
        <gml:outerBoundaryIs>
            <gml:LinearRing>
                <gml:coordinates>0,0 100,0 100,100 0,100 0,0</gml:coordinates>
            </gml:LinearRing>
        </gml:outerBoundaryIs>
    </gml:Polygon>
    '''
    with pytest.raises(ValueError):
        Geometry._parse_gml(gml5)

    # GML with xmlns which is surrounded by whitespaces (illegal)
    gml6 = '''
    <Point xmlns=" http://www.opengis.net/gml  " id="p21" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
        <coordinates>45.67, 88.56</coordinates>
    </Point>
    '''
    with pytest.raises(ValueError):
        root = Geometry._parse_gml(gml6)

    elem = ET.fromstring(gml6)
    with pytest.raises(ValueError):
        Geometry._parse_gml(elem)

    gml7 = '''
    <Point xmlns="http://www.opengis.net/gml" id="p21" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
        <coordinates>45.67, 88.56</coordinates>
    </Point>
    '''
    root = Geometry._parse_gml(gml7)
    assert root.tag == '{http://www.opengis.net/gml}Point'

    elem = ET.fromstring(gml7)
    root = Geometry._parse_gml(elem)
    assert root.tag == '{http://www.opengis.net/gml}Point'

    envelope1 = '''
    <gml:Envelope xmlns:gml="http://www.opengis.net/gml">
        <gml:lowerCorner>12.03 44.32</gml:lowerCorner>
        <gml:upperCorner>22.34 52.39</gml:upperCorner>
    </gml:Envelope>
    '''
    root = Geometry._parse_gml(envelope1)
    assert root.tag == '{http://www.opengis.net/gml}Envelope'




# def test_OgrWrapper_gml2():
    # wrapper = OgrWrapper('POLYGON ((35 10, 45 45, 15 40, 10 20, 35 10),(20 30, 35 35, 30 20, 20 30))', 3857)
    # assert wrapper.gml2 == re.sub(
        # r'>\s+<',
        # '><',
        # '''
# <gml:Polygon srsName="EPSG:3857">
    # <gml:outerBoundaryIs>
        # <gml:LinearRing>
            # <gml:coordinates>35,10 45,45 15,40 10,20 35,10</gml:coordinates>
        # </gml:LinearRing>
    # </gml:outerBoundaryIs>
    # <gml:innerBoundaryIs>
        # <gml:LinearRing>
            # <gml:coordinates>20,30 35,35 30,20 20,30</gml:coordinates>
        # </gml:LinearRing>
    # </gml:innerBoundaryIs>
# </gml:Polygon>
        # '''.strip()
    # )
    # print(wrapper.gml3)


# def test_OgrWrapper_gml3():
    # wrapper = OgrWrapper('MULTIPOLYGON (((30 20, 45 40, 10 40, 30 20)), ((15 5, 40 10, 10 20, 5 10, 15 5)))', 3857)

    # # It seems GML3 does not work properly in SLD
    # assert wrapper.gml3 == re.sub(
        # r'>\s+<',
        # '><',
        # '''
# <gml:MultiSurface srsName="EPSG:3857">
    # <gml:surfaceMember>
        # <gml:Polygon>
            # <gml:exterior>
                # <gml:LinearRing>
                    # <gml:posList>30 20 45 40 10 40 30 20</gml:posList>
                # </gml:LinearRing>
            # </gml:exterior>
        # </gml:Polygon>
    # </gml:surfaceMember>
    # <gml:surfaceMember>
        # <gml:Polygon>
            # <gml:exterior>
                # <gml:LinearRing>
                    # <gml:posList>15 5 40 10 10 20 5 10 15 5</gml:posList>
                # </gml:LinearRing>
            # </gml:exterior>
        # </gml:Polygon>
    # </gml:surfaceMember>
# </gml:MultiSurface>
        # '''.strip()
    # )