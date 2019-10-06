from collections import OrderedDict
import datetime
from itertools import product
import re

from ..base import ElemAbstract
from ..utils import stringify, parseDouble, parseDate


NoneType = None.__class__


OGC = 'http://www.opengis.net/ogc'


class OgcAbstract(ElemAbstract):
    nameSpace = 'ogc'

    class UnsupportedDataType(Exception):
        pass

    class IllegalValue(Exception):
        pass

    class BadFeatureError(Exception):
        pass


class Expression(OgcAbstract):
    class NonNumericError(Exception):
        pass
        
    def __init__(self):
        super().__init__()

    @classmethod
    def wrap(klass, obj):
        if isinstance(obj, Expression):
            return obj
        elif isinstance(obj, (int, float, bool, str, datetime.datetime, datetime.date, None.__class__)):
            return Literal(obj)
        raise TypeError(f'{repr(obj)} is not a valid expression object')

    def __add__(self, other):
        from .binary_ops import Add
        return Add(self, other)

    def __radd__(self, other):
        from .binary_ops import Add
        return Add(other, self)

    def __sub__(self, other):
        from .binary_ops import Sub
        return Sub(self, other)

    def __rsub__(self, other):
        from .binary_ops import Sub
        return Sub(other, self)

    def __mul__(self, other):
        from .binary_ops import Mul
        return Mul(self, other)
        
    def __rmul__(self, other):
        from .binary_ops import Mul
        return Mul(other, self)

    def __truediv__(self, other):
        from .binary_ops import Div
        return Div(self, other)

    def __rtruediv__(self, other):
        from .binary_ops import Div
        return Div(other, self)


class Literal(Expression):
    class CannotCastError(Exception):
        pass

    tagName = 'Literal'
    
    def __init__(self, obj):
        super().__init__()
        self.text = stringify(obj)

    def simulate(self, *args, **kwargs):
        return self.text


class PropertyName(Expression):
    tagName = 'PropertyName'

    def __init__(self, property_name):
        super().__init__()

        if not isinstance(property_name, str):
            raise TypeError('property_name must be string!')

        self.text = property_name

    def simulate(self, data, config=None):
        if not isinstance(data, (dict, OrderedDict)):
            raise TypeError('data must be dict or collections.OrderedDict instance.')

        if self.text not in data:
            raise ValueError(f'data doesn\'t have key "{self.text}"')

        return data[self.text]


