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


class BinarySpatialOp(SpatialOp, PropertyNameMixin):
    def __init__(self, propety_name, geometry):
        super().__init__()
        self.propertyName = propety_name
        self.geometry = geometry

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
        ogr0 = self._simulate_wrapper(self.propertyName, *args, **kwargs)
        ogr1 = self._simulate_wrapper(self.geometry, *args, **kwargs)
        srs0 = ogr0.spatial_ref
        srs1 = ogr1.spatial_ref
        if not (srs0 is None or srs1 is None):
            if not srs0.IsSame(srs1):
                ogr1 = ogr1.transform_to(srs0)

        return ogr0, ogr1


class Equals(BinarySpatialOp):
    def simulate(self, *args, **kwargs):
        ogr0, ogr1 = super().simulate(*args, **kwargs)
        return ogr0.equals(ogr1)


class Disjoint(BinarySpatialOp):
    def simulate(self, *args, **kwargs):
        ogr0, ogr1 = super().simulate(*args, **kwargs)
        return ogr0.disjoint(ogr1)


class Touches(BinarySpatialOp):
    def simulate(self, *args, **kwargs):
        ogr0, ogr1 = super().simulate(*args, **kwargs)
        return ogr0.touches(ogr1)


class Within(BinarySpatialOp):
    def simulate(self, *args, **kwargs):
        ogr0, ogr1 = super().simulate(*args, **kwargs)
        return ogr0.within(ogr1)


class Overlaps(BinarySpatialOp):
    def simulate(self, *args, **kwargs):
        ogr0, ogr1 = super().simulate(*args, **kwargs)
        return ogr0.overlaps(ogr1)


class Crosses(BinarySpatialOp):
    def simulate(self, *args, **kwargs):
        ogr0, ogr1 = super().simulate(*args, **kwargs)
        return ogr0.crosses(ogr1)


class Intersects(BinarySpatialOp):
    def simulate(self, *args, **kwargs):
        ogr0, ogr1 = super().simulate(*args, **kwargs)
        return ogr0.intersects(ogr1)


class Contains(BinarySpatialOp):
    def simulate(self, *args, **kwargs):
        ogr0, ogr1 = super().simulate(*args, **kwargs)
        return ogr0.contains(ogr1)
