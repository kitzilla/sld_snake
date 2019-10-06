from collections import OrderedDict
import re
import xml.etree.ElementTree as ET

from .utils import stringify

NAMESPACES = {
    'ogc': 'http://www.opengis.net/ogc',
    'sld': 'http://www.opengis.net/sld',
    'gml': 'http://www.opengis.net/gml',
}

for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


class SLDConfig:
    GEOSERVER_POSTGIS = 'geoserver_postgis'
    GEOSERVER_SLD_INLINE_FEATURE = 'geoserver_inline'
    SLD1 = 1
    SLD2 = 2

    def __init__(self, simulating=GEOSERVER_POSTGIS, sld_ver=SLD1):
        self.sld_ver = None 
        if sld_ver in (self.SLD1, self.SLD2):
            self.sld_ver = sld_ver
        else:
            raise ValueError(f'sld_ver is illegal: {repr(sld_ver)}')
        
        self.zero_length_string_is_null = False
        
        if simulating == self.GEOSERVER_POSTGIS:
            self._configure_for_geoserver_postgis()
        elif simulating == self.GEOSERVER_SLD_INLINE_FEATURE:
            self._configure_for_geoserver_inline_feature()

    def _configure_for_geoserver_postgis(self):
        pass
    
    def _configure_for_geoserver_inline_feature(self):
        self.zero_length_string_is_null = True


class ElemAbstract:
    def __init__(self):
        self.text = None
        self.children = OrderedDict()
        self.attrib = {}
        self.NAMESPACES = NAMESPACES.copy()

    def validate(self):
        pass

    def etree(self, config=None):
        uri = self.NAMESPACES[self.nameSpace]
        elem = ET.Element(f"{{{uri}}}{self.tagName}", attrib=self.attrib)

        if self.children:
            for child in self.children.values():
                elem.append(child.etree(config))
        elif self.text:
            elem.text = self.text

        return elem

    def xml(self, no_xmlns=False, config=None):
        self.validate()
        xml = ET.tostring(self.etree(config), encoding='utf-8').decode()
        if no_xmlns:
            inside_tag = False
            xml2 = ''
            buffer = ''
            for c in xml:
                if c == '<':
                    inside_tag = True
                    buffer = ''
                    xml2 += c
                elif c == '>':
                    inside_tag = False
                    xml2 += re.sub(r' xmlns:.+?=".+?"', '', buffer)
                    xml2 += c
                else:
                    if inside_tag:
                        buffer += c
                    else:
                        xml2 += c
            xml = xml2
        return xml
