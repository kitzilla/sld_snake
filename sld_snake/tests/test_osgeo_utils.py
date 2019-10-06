import json
import pytest
import re
import xml.etree.ElementTree as ET

from ..osgeo.utils import OgrWrapper


def test_OgrWrapper_OgrWrapper():
    geojson1 = {
        'type': 'Point',
        'coordinates': [11, 13],
    }
    wrapper = OgrWrapper(geojson1)
    assert wrapper._ogr.GetPointCount() == 1

    wrapper = OgrWrapper(json.dumps(geojson1))
    assert wrapper._ogr.GetX(0) == 11

    geojson2 = {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': [[11, 13], [15, 17]],
        },
        'properties': {
            'field1': 10,
            'field2': 'test point',
        },
    }
    wrapper = OgrWrapper(geojson2)
    assert wrapper._ogr.GetPointCount() == 2
    
    wrapper = OgrWrapper(json.dumps(geojson2))
    assert wrapper._ogr.GetX(1) == 15

    # FeatureCollection is not acceptable
    geojson3 = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [11, 13],
                },
                'properties': {
                    'field1': 10,
                },
            },
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [15, 17],
                },
                'properties': {
                    'field1': 11,
                },
            }
        ]
    }
    with pytest.raises(ValueError):
        wrapper = OgrWrapper(geojson3)

    wkt = '  SRID=27700;MULTIPOINT (10 40, 40 30)  '
    wrapper = OgrWrapper(wkt)
    assert wrapper._ogr.GetGeometryCount() == 2
    assert wrapper._ogr.GetSpatialReference().GetAuthorityCode(None) == '27700'

    
    gml2 = '''
    <gml:Polygon>
        <gml:outerBoundaryIs>
            <gml:LinearRing>
                <gml:coordinates>0,0 100,0 100,100 0,100 0,0</gml:coordinates>
            </gml:LinearRing>
        </gml:outerBoundaryIs>
    </gml:Polygon>
    '''
    wrapper = OgrWrapper(gml2)
    assert wrapper._ogr.GetGeometryRef(0).GetPointCount() == 5

    gml3 = '''
    <gml:LineString>
        <gml:posList srsDimension="2">45.67 88.56 55.56 89.44</gml:posList>
    </gml:LineString >
    '''
    wrapper = OgrWrapper(gml3)
    assert wrapper._ogr.GetPointCount() == 2
    
    
    root = ET.fromstring('''
    <gml:Polygon  xmlns:gml="http://www.opengis.net/gml" >
        <gml:outerBoundaryIs>
            <gml:LinearRing>
                <gml:coordinates>0,0 100,0 100,100 0,100 0,0</gml:coordinates>
            </gml:LinearRing>
        </gml:outerBoundaryIs>
    </gml:Polygon>
    ''')
    wrapper = OgrWrapper(root)
    assert wrapper._ogr.GetGeometryRef(0).GetPointCount() == 5
    
    root = ET.fromstring('''
    <gml:Polygen  xmlns:gml="http://www.opengis.net/gml" >
        <gml:outerBoundaryIs>
            <gml:LinearRing>
                <gml:coordinates>0,0 100,0 100,100 0,100 0,0</gml:coordinates>
            </gml:LinearRing>
        </gml:outerBoundaryIs>
    </gml:Polygen>
    ''')
    with pytest.raises(ValueError):
        wrapper = OgrWrapper(root)
    
    
def test_OgrWrapper_gml2():
    wrapper = OgrWrapper('POLYGON ((35 10, 45 45, 15 40, 10 20, 35 10),(20 30, 35 35, 30 20, 20 30))', 3857)
    assert wrapper.gml2 == re.sub(
        r'>\s+<',
        '><',
        '''
<gml:Polygon srsName="EPSG:3857">
    <gml:outerBoundaryIs>
        <gml:LinearRing>
            <gml:coordinates>35,10 45,45 15,40 10,20 35,10</gml:coordinates>
        </gml:LinearRing>
    </gml:outerBoundaryIs>
    <gml:innerBoundaryIs>
        <gml:LinearRing>
            <gml:coordinates>20,30 35,35 30,20 20,30</gml:coordinates>
        </gml:LinearRing>
    </gml:innerBoundaryIs>
</gml:Polygon>
        '''.strip()
    )
    print(wrapper.gml3)
    
    
def test_OgrWrapper_gml3():
    wrapper = OgrWrapper('MULTIPOLYGON (((30 20, 45 40, 10 40, 30 20)), ((15 5, 40 10, 10 20, 5 10, 15 5)))', 3857)
    
    # It seems GML3 does not work properly in SLD
    assert wrapper.gml3 == re.sub(
        r'>\s+<',
        '><',
        '''
<gml:MultiSurface srsName="EPSG:3857">
    <gml:surfaceMember>
        <gml:Polygon>
            <gml:exterior>
                <gml:LinearRing>
                    <gml:posList>30 20 45 40 10 40 30 20</gml:posList>
                </gml:LinearRing>
            </gml:exterior>
        </gml:Polygon>
    </gml:surfaceMember>
    <gml:surfaceMember>
        <gml:Polygon>
            <gml:exterior>
                <gml:LinearRing>
                    <gml:posList>15 5 40 10 10 20 5 10 15 5</gml:posList>
                </gml:LinearRing>
            </gml:exterior>
        </gml:Polygon>
    </gml:surfaceMember>
</gml:MultiSurface>
        '''.strip()
    )