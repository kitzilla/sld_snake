import json
from osgeo import ogr, osr
import re

from ..base import ET


class OgrWrapper:
    def __init__(self, source, epsg=None):
        self.source = source
        self.epsg = epsg
        if type(source) == ogr.Geometry:
            self._ogr = source
        else:
            self._ogr = self.to_ogr()

    @property
    def epsg(self):
        return self._epsg

    @epsg.setter
    def epsg(self, value):
        if value is None:
            self._epsg = None
            return

        if type(value) != int:
            raise TypeError('epsg must be int')

        srs = osr.SpatialReference()
        if srs.ImportFromEPSG(value) != 0:
            raise ValueError(f'GDAL could not resolve EPSG {value}. Is this a valid EPSG code?')
        self._epsg = value

    def to_ogr(self, source=None):
        if source is None:
            source = self.source

        geom = None
        if isinstance(source, dict):
            if not 'coordinates' in source:
                if 'features' in source:
                    raise ValueError(f'FeatureCollection {repr(source)} cannot be converted to a single OGR Geometry')
                    
                if 'geometry' in source:
                    source = source['geometry']
                else:
                    raise ValueError(f'{repr(source)} doesn\'t look like a valid GeoJSON')
            geom_str = json.dumps(source)
            geom = ogr.CreateGeometryFromJson(geom_str)
            if geom is None:
                raise ValueError(f'Failed to convert {repr(source)} to OGR Geometry')

        elif isinstance(source, str):
            try:
                jsn = json.loads(source)
            except json.JSONDecodeError:
                pass
            else:
                return self.to_ogr(jsn)
            wkt = source
            m = re.match(r'\s*SRID=(\d*)\s*;(.*)$', wkt)  # Extended WKT
            if m:
                if self.epsg is None:
                    self.epsg = int(m.group(1))  # epsg provided to constructor supersedes
                wkt = m.group(2)
            geom = ogr.CreateGeometryFromWkt(wkt)

            if geom is None:
                geom = ogr.CreateGeometryFromGML(source)
            if geom is None:
                raise ValueError(f'{repr(source)} doesn\'t look like neither of GeoJSON, WKT nor GML')

        elif isinstance(source, ET.Element):
            xml = ET.tostring(source, encoding='utf-8').decode()
            try:
                return self.to_ogr(xml)
            except ValueError:
                raise ValueError(f'{repr(source)} is not representing a valid GML')

        else:
            raise TypeError(f'{repr(source)} cannot be converted to OGR Geometry' )

        if type(self.epsg) == int:
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(self.epsg)
            geom.AssignSpatialReference(srs)
        return geom

    @property
    def gml2(self):
        return self._ogr.ExportToGML()
    
    @property
    def gml3(self):
        return self._ogr.ExportToGML(options=['FORMAT=GML3', 'GML3_LONGSRS=NO'])
    
    @classmethod
    def wrap(klass, obj):
        if isinstance(obj, OgrWrapper):
            return obj
        return klass(obj)
    
    def intersects(self, other):
        other = self.wrap(other)
        return self._ogr.Intersects(other._ogr)
    
    def disjoint(self, other):
        other = self.wrap(other)
        return self._ogr.Disjoint(other._ogr)
        
    def touches(self, other):
        other = self.wrap(other)
        return self._ogr.Touches(other._ogr)
        
    def equals(self, other):
        other = self.wrap(other)
        return self._ogr.Equals(other._ogr)
        
    def crosses(self, other):
        other = self.wrap(other)
        return self._ogr.Crosses(other._ogr)
        
    def contains(self, other):
        other = self.wrap(other)
        return self._ogr.Contains(other._ogr)
        
    def within(self, other):
        other = self.wrap(other)
        return self._ogr.Within(other._ogr)
        
    def overlaps(self, other):
        other = self.wrap(other)
        return self._ogr.Overlaps(other._ogr)
