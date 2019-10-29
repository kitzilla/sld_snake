import re

from .base import ElemAbstract, ET, NAMESPACES


class Geometry(ElemAbstract):
    def __init__(self, source):
        self.source = None
        self._ogr = None
        self._etree = None

        gdal_available = False
        try:
            from .osgeo.utils import OgrWrapper
        except ImportError:
            pass
        else:
            gdal_available = True
            self._ogr = OgrWrapper(source)
            return
        root = self._parse_gml(source)
        self._etree = root

    @classmethod
    def wrap(klass, obj):
        if type(obj) == Geometry:
            return obj
        return Geometry(obj)

    @staticmethod
    def _parse_gml(source):
        if not isinstance(source, (str, ET.Element)):
            raise TypeError(f'Argument is not string: {repr(source)}')

        GML = NAMESPACES["gml"]  # http://www.opengis.net/gml
        source_original = source
        root = None
        if isinstance(source, str):
            wrapped = False
            mobj = re.search(r'<\s*([^< >]+:|)(MultiGeometry|(Multi)?(Point|LineString|Polygon|Curve|Surface))(\s.*?|)>', source)
            if mobj:
                prefix = mobj.group(1)[:-1]
                if prefix:
                    mobj2 = re.search(r'\sxmlns:' + re.escape(prefix) + '\s*=\s*["\'].*?["\']', source)
                    if mobj2 is None:
                        source = f'<root xmlns:{prefix}="{GML}">{source}</root>'
                        wrapped = True
                else:
                    mobj2 = re.search(r'\sxmlns\s*=\s*["\'].*?["\']', source)
                    if mobj2 is None:
                        source = f'<root xmlns="{GML}">{source}</root>'
                        wrapped = True
            try:
                root = ET.fromstring(source)
            except ET.ParseError:
                raise ValueError(f'Argument is not valid GML: {repr(source_original)}')
            else:
                if wrapped:
                    root = root[0]
        elif isinstance(source, ET.Element):
            root = source

        if not re.match(r'^{'+ GML +'}(MultiGeometry|Envelope|(Multi)?(Point|LineString|Polygon|Curve|Surface))$', root.tag):
            raise ValueError(f'Argument is not GML Geometry: {repr(source_original)}')
        return root

    def etree(self, config=None):
        if self._etree:
            return self._etree
        gml = self._ogr.gml2
        return self._parse_gml(gml)

    def simulate(self, *args, **kwargs):
        if self._ogr:
            return self._ogr
        raise ImportError('To simulate GML geometry, GDAL Python binding is needed to be installed.')
