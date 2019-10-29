import json
from osgeo import ogr, osr
import re

from ..base import ET


class OgrWrapper:
    def __init__(self, source, srid=None):
        self.source = source
        self._ogr = None

        if type(source) == ogr.Geometry:
            self._ogr = source
        else:
            self._ogr = self._to_ogr(source, srid)

    @staticmethod
    def _to_ogr(source, srid=None):
        geom = None
        if isinstance(source, dict):
            # GeoJSON
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
                # GeoJSON string
                return OgrWrapper._to_ogr(jsn, srid)

            wkt = source
            m = re.match(r'\s*SRID=(\d*)\s*;(.*)$', wkt)  # Extended WKT
            if m:
                srid = int(m.group(1))
                wkt = m.group(2)
            # Try WKT
            geom = ogr.CreateGeometryFromWkt(wkt)

            if geom is None:
                geom = ogr.CreateGeometryFromGML(source)
            if geom is None:
                raise ValueError(f'{repr(source)} doesn\'t look like neither of GeoJSON, WKT nor GML')

        elif isinstance(source, ET.Element):
            xml = ET.tostring(source, encoding='utf-8').decode()
            try:
                return OgrWrapper._to_ogr(xml)
            except ValueError:
                raise ValueError(f'{repr(source)} is not representing a valid GML')

        else:
            raise TypeError(f'{repr(source)} cannot be converted to OGR Geometry' )

        if srid is not None:
            OgrWrapper._set_srs(geom, srid)

        return geom

    @staticmethod
    def _create_srs(srid):
        if type(srid) != int:
            raise TypeError('srid is not integer')

        srs = osr.SpatialReference()
        if srs.ImportFromEPSG(srid) != 0:
            raise ValueError(f'GDAL could not resolve EPSG {srid}. Is this a valid EPSG code?')
        return srs

    @staticmethod
    def _set_srs(geom, srid):
        if type(geom) != ogr.Geometry:
            raise TypeError('geom is not ogr.Geometry object')
        srs = OgrWrapper._create_srs(srid)
        geom.AssignSpatialReference(srs)

    def transform_to(self, srs):
        if type(srs) != osr.SpatialReference:
            raise ValueError('srs is not osr.SpatialReference instance')

        srs_from = self.spatial_ref
        if srs_from is None:
            srs_from = self._create_srs(srid=4326)

        copy = OgrWrapper(self.source, None)
        transform = osr.CoordinateTransformation(srs_from, srs)
        copy._ogr.Transform(transform)
        return copy

    @property
    def spatial_ref(self):
        return self._ogr.GetSpatialReference()

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
