from itertools import product

from ..ogc import PropertyName, Equals, Disjoint, Touches, Within, Overlaps, Crosses, Intersects, Contains
from .utils import flatten_xml


poly0 = 'Polygon((0 0, 5 0, 5 5, 0 5, 0 0))'
poly1 = 'Polygon((1 1, 5 1, 5 4, 1 4, 1 1))'  # Within poly0
poly2 = 'Polygon((5 3, 9 3, 9 7, 5 7, 5 3))'  # Touches poly0
poly3 = 'Polygon((6 0, 9 0, 9 5, 6 5, 6 0))'  # Disjoint with poly0
poly4 = 'Polygon((3 3, 7 3, 7 8, 3 8, 3 3))'  # Overlaps and Intersects poly0

line0 = 'LineString(0 0, 2 0, 7 0, 7 4)'  # Touches poly0
line1 = 'LineString(2 0, 4 0)'  # Within line0(?)
line2 = 'LineString(7 4, 3 4)'  # Touches line0, Crosses poly0
line3 = 'LineString(6 3, 9 3)'  # Crosses line0, Disjoint poly0
line4 = 'LineString(2 2, 4 5)'  # Disjoint line0, Within poly0

point0 = 'Point(4 0)'  # Within line0, Touches poly0
point1 = 'Point(7 4)'  # Touches line0, Disjoint poly0
point2 = 'Point(3 2)'  # Disjoint line0, Within poly0


def test_Equals(subtests):
    op = Equals('geom', poly0)

    assert op.xml(True) == flatten_xml(
        '''
        <ogc:Equals>
            <ogc:PropertyName>geom</ogc:PropertyName>
            <gml:Polygon>
                <gml:outerBoundaryIs>
                    <gml:LinearRing>
                        <gml:coordinates>0,0 5,0 5,5 0,5 0,0</gml:coordinates>
                    </gml:LinearRing>
                </gml:outerBoundaryIs>
            </gml:Polygon>
        </ogc:Equals>
        '''
    )
    assert op.simulate({ 'geom': poly0 }) is True

    for geom in [poly1, poly3, line0, line2, point0]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    # If data's crs is undefined, ignore geometry's crs
    # British national grid ((0, 0) is near Isles of Scilly)
    op.geometry = f'SRID=27700;{poly0}'
    assert op.simulate({ 'geom': poly0 }) is True

    # If data's crs is defined in both, consider it
    assert op.simulate({ 'geom': f'SRID=4326;{poly0}' }) is False

    op.geometry = line0
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:Equals>
            <ogc:PropertyName>geom</ogc:PropertyName>
            <gml:LineString>
                <gml:coordinates>0,0 2,0 7,0 7,4</gml:coordinates>
            </gml:LineString>
        </ogc:Equals>
        '''
    )
    op.simulate({ 'geom': line0 }) is True

    for geom in [poly0, poly2, line1, line3, point1]:
        with subtests.test("", geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op.geometry = f'SRID=27700;{line0}'
    assert op.simulate({ 'geom': f'SRID=4326;{line0}' }) is False


    op.geometry = point0
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:Equals>
            <ogc:PropertyName>geom</ogc:PropertyName>
            <gml:Point>
                <gml:coordinates>4,0</gml:coordinates>
            </gml:Point>
        </ogc:Equals>
        '''
    )


def test_Disjoint(subtests):
    op = Disjoint('geom', poly0)
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:Disjoint>
            <ogc:PropertyName>geom</ogc:PropertyName>
            <gml:Polygon>
                <gml:outerBoundaryIs>
                    <gml:LinearRing>
                        <gml:coordinates>0,0 5,0 5,5 0,5 0,0</gml:coordinates>
                    </gml:LinearRing>
                </gml:outerBoundaryIs>
            </gml:Polygon>
        </ogc:Disjoint>
        '''
    )
    for geom in [poly3, line3, point1]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is True

    for geom in [poly1, poly2, poly4, line0, line1, line2, point0]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op.geometry = line0
    assert op.simulate({ 'geom': poly1 }) is True
    assert op.simulate({ 'geom': line4 }) is True
    assert op.simulate({ 'geom': point2 }) is True

    for geom in [poly0, line1, line2, line3, point0, point1]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op.geometry = point0
    assert op.simulate({ 'geom': poly1 }) is True
    assert op.simulate({ 'geom': line2 }) is True
    assert op.simulate({ 'geom': point1 }) is True

    for geom in [poly0, line0, line1, point0]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False


def test_Touches(subtests):
    op = Touches('geom', poly0)

    assert op.simulate({ 'geom': poly2 }) is True
    assert op.simulate({ 'geom': line0 }) is True
    assert op.simulate({ 'geom': line1 }) is True
    assert op.simulate({ 'geom': point0 }) is True

    for geom in [poly0, poly1, poly3, poly4, line2, line3, line4, point1, point2]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op.geometry = line0
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:Touches>
            <ogc:PropertyName>geom</ogc:PropertyName>
            <gml:LineString>
                <gml:coordinates>0,0 2,0 7,0 7,4</gml:coordinates>
            </gml:LineString>
        </ogc:Touches>
        '''
    )
    assert op.simulate({ 'geom': poly0 }) is True
    assert op.simulate({ 'geom': line2 }) is True
    assert op.simulate({ 'geom': point1 }) is True

    for geom in [poly1, poly2, poly3, line0, line1, line3, point0, point2]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op.geometry = point0
    assert op.simulate({ 'geom': poly0 }) is True
    assert op.simulate({ 'geom': line1 }) is True

    for geom in [poly1, poly3, poly4, line0, line2, line3, point0, point1]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False


def test_Within(subtests):
    op = Within('geom', poly0)
    assert op.simulate({ 'geom': poly0 }) is True
    assert op.simulate({ 'geom': poly1 }) is True
    assert op.simulate({ 'geom': line4 }) is True
    assert op.simulate({ 'geom': point2 }) is True

    for geom in [poly2, poly3, poly4, line0, line1, line2, line3, point0, point1]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op.geometry = line0
    assert op.simulate({ 'geom': line0 }) is True
    assert op.simulate({ 'geom': line1 }) is True
    assert op.simulate({ 'geom': point0 }) is True

    for geom in [poly0, poly1, poly2, poly3, poly4, line2, line3, line4, point1, point2]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op.propertyName = 'shape'
    op.geometry = point0
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:Within>
            <ogc:PropertyName>shape</ogc:PropertyName>
            <gml:Point>
                <gml:coordinates>4,0</gml:coordinates>
            </gml:Point>
        </ogc:Within>
        '''
    )
    assert op.simulate({ 'shape': point0 }) is True

    for geom in [poly0, poly1, poly2, poly3, poly4, line0, line1, line2, line3, line4, point1, point2]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'shape': geom }) is False


def test_Overlaps(subtests):
    op = Overlaps('geom', poly0)
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:Overlaps>
            <ogc:PropertyName>geom</ogc:PropertyName>
            <gml:Polygon>
                <gml:outerBoundaryIs>
                    <gml:LinearRing>
                        <gml:coordinates>0,0 5,0 5,5 0,5 0,0</gml:coordinates>
                    </gml:LinearRing>
                </gml:outerBoundaryIs>
            </gml:Polygon>
        </ogc:Overlaps>
        '''
    )
    assert op.simulate({ 'geom': poly4 }) is True

    for geom in [poly0, poly1, poly2, poly3, line0, line1, line2, line3, line4, point0, point1, point2]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op.geometry = line0
    assert op.simulate({ 'geom': 'LineString(2 0, 7 0, 7 4, 8 3)' }) is True

    for geom in [poly0, poly1, poly2, poly3, poly4, line0, line1, line2, line3, line4, point0, point1, point2]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op.geometry = point0
    for geom in [poly0, poly1, poly2, poly3, poly4, line0, line1, line2, line3, line4, point0, point1, point2]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False


def test_Crosses(subtests):
    op = Crosses('geom', poly0)
    assert op.simulate({ 'geom': line2 }) is True

    for geom in [poly0, poly1, poly2, poly3, poly4, line0, line1, line3, line4, point0, point1, point2]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op = Crosses('geom', line0)
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:Crosses>
            <ogc:PropertyName>geom</ogc:PropertyName>
            <gml:LineString>
                <gml:coordinates>0,0 2,0 7,0 7,4</gml:coordinates>
            </gml:LineString>
        </ogc:Crosses>
        '''
    )
    assert op.simulate({ 'geom': poly2 }) is True
    assert op.simulate({ 'geom': poly3 }) is True
    assert op.simulate({ 'geom': line3 }) is True

    for geom in [poly0, poly1, poly4, line0, line1, line2, line4, point0, point1, point2]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False

    op.geometry = point0
    for geom in [poly0, poly1, poly2, poly3, poly4, line0, line1, line3, line4, point0, point1, point2]:
        with subtests.test(geom=geom):
            assert op.simulate({ 'geom': geom }) is False


def test_Contains(subtests):
    op = Contains('test', point0)
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:Contains>
            <ogc:PropertyName>test</ogc:PropertyName>
            <gml:Point>
                <gml:coordinates>4,0</gml:coordinates>
            </gml:Point>
        </ogc:Contains>
        '''
    )
    all_geoms = [poly0, poly1, poly2, poly3, poly4, line0, line1, line3, line4, point0, point1, point2]
    for geom1, geom2 in product(all_geoms, repeat=2):
        with subtests.test(geom1=geom1, geom2=geom2):
            within = Within('geom', geom1)
            assert Contains('g', geom2).simulate({ 'g': geom1 }) is Within('g', geom1).simulate({ 'g': geom2 })


def test_Intersects(subtests):
    op = Intersects('area', poly0)
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:Intersects>
            <ogc:PropertyName>area</ogc:PropertyName>
            <gml:Polygon>
                <gml:outerBoundaryIs>
                    <gml:LinearRing>
                        <gml:coordinates>0,0 5,0 5,5 0,5 0,0</gml:coordinates>
                    </gml:LinearRing>
                </gml:outerBoundaryIs>
            </gml:Polygon>
        </ogc:Intersects>
        '''
    )

    all_geoms = [poly0, poly1, poly2, poly3, poly4, line0, line1, line3, line4, point0, point1, point2]
    for geom1, geom2 in product(all_geoms, repeat=2):
        with subtests.test(geom1=geom1, geom2=geom2):
            disjoint = Disjoint('geom', geom1)
            intersects = Intersects('geom', geom1)
            data = { 'geom': geom2 }
            assert intersects.simulate(data) is not disjoint.simulate(data)








