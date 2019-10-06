from ..utils import stringify
from .base import Expression, PropertyName


class OneExpressionMixin:
    @property
    def expr0(self):
        return self.children[0]

    @expr0.setter
    def expr0(self, expr):
        self.children[0] = Expression.wrap(expr)


class OneExpressionOverloading:
    def __iadd__(self, other):
        self.expr0 += other
        return self.expr0

    def __isub__(self, other):
        self.expr0 -= other
        return self.expr0

    def __imul__(self, other):
        self.expr0 *= other
        return self.expr0

    def __itruediv__(self, other):
        self.expr0 /= other
        return self.expr0


class TwoExpressionMixin(OneExpressionMixin):
    @property
    def expr1(self):
        return self.children[1]

    @expr1.setter
    def expr1(self, expr):
        self.children[1] = Expression.wrap(expr)
        
        
class PropertyNameMixin:
    @property
    def propertyName(self):
        return self.children.get('propertyName', None)
        
    @propertyName.setter
    def propertyName(self, property_name):
        if isinstance(property_name, str):
            property_name = PropertyName(property_name)

        if not isinstance(property_name, PropertyName):
            raise TypeError(f'You cannot set {repr(property_name)} to property_name. It must be string or PropertyName object')

        self.children['propertyName'] = property_name


class MatchCaseMixin:
    @property
    def matchCase(self):
        text = self.attrib.get('matchCase', 'true')
        return text != 'false'

    @matchCase.setter
    def matchCase(self, value):
        wrapped = None
        if value is None:
            if 'matchCase' in self.attrib:
                del self.attrib['matchCase']
            return

        if type(value) == bool:
            wrapped = stringify(value)
        if str(value).lower() in ['true', '1']:
            wrapped = 'true'
        if str(value).lower() in ['false', '0']:
            wrapped = 'false'

        if wrapped is None:
            raise ValueError(f'You cannot set {repr(value)} to matchCase. It must be boolean, "true", "false", 1 or 0.')

        self.attrib['matchCase'] = wrapped
