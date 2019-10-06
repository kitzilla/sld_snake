from ..gml import Geometry

from .base import PropertyName
from .logic_ops import LogicOpAbstract
from .mixins import PropertyNameMixin


class SpatialOp(LogicOpAbstract, PropertyNameMixin):
    @staticmethod
    def _simulate_wrapper(elem, *args, **kwargs):
        if type(elem) == Geometry:
            return elem.simulate(*args, **kwargs)
        result = elem.simulate(*args, **kwargs)
        geom = Geometry.wrap(result)
        return geom.simulate(*args, **kwargs)


class BinarySpatialOp(SpatialOp):
    def __init__(self, propety_name, geometry):
        self.propetyName = propety_name
    
    @property
    def geometry(self):
        return self.children['geometry']
    
    @geometry.setter
    def geometry(self, value):
        if type(value) == PropertyName:
            self.children['geometry'] = value
        else:
            self.children['geometry'] = Geometry.wrap(value)
            
    def simulate(self, *args, **kwargs):
        ogr0 = self._simulate_wrapper(self.propetyName)
        ogr1 = self._simulate_wrapper(self.geometry)
        return ogr0, ogr1
    
    
    