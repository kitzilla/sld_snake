from ..utils import stringify, parseDouble, parseBool, parseDate
from .base import OgcAbstract, Expression, PropertyName, Literal
from .logic_ops import LogicOpAbstract
from .mixins import OneExpressionMixin, TwoExpressionMixin, PropertyNameMixin, MatchCaseMixin, OneExpressionOverloading
import datetime
import re


class ComparisonOps(LogicOpAbstract):
    pass


class BinaryComparisonOp(ComparisonOps, TwoExpressionMixin, MatchCaseMixin):
    def __init__(self, expr0, expr1, matchCase=None):
        super().__init__()

        self.expr0 = expr0
        self.expr1 = expr1

        self.matchCase = matchCase

    @staticmethod
    def _compare_values(val1, val2):
        if type(val1) != type(val2):
            raise ValueError(f'Comparing mismatching types "{type(val1)} vs {type(val2)}"')

        if val1 is None and val2 is None:
            return 0

            if isinstance(val1, str) and not self.matchCase:
                val1 = val1.lower()
                val2 = val2.lower()

        if type(val1) == datetime.datetime and type(val2) == datetime.datetime:
            # Python can't directly compare offset-naive (tzinfo=None) and offset-aware (tzinfo=something)
            # datetime objects, whilst GeoServer can. We add UTC timezone to naive objects to make them
            # comparable
            if val1.tzinfo is None and val2.tzinfo is not None:
                val1 = val1.replace(tzinfo=datetime.timezone.utc)
            elif val1.tzinfo is not None and val2.tzinfo is None:
                val2 = val2.replace(tzinfo=datetime.timezone.utc)

        if val1 == val2:
            return 0
        elif val1 > val2:
            return 1
        return -1  # val1 < val2

    def simulate(self, *args, **kwargs):
        val1 = self.expr0.simulate(*args, **kwargs)
        val2 = self.expr1.simulate(*args, **kwargs)

        try:
            val1 = parseDouble(val1)
            val2 = parseDouble(val2)
        except (ValueError, TypeError):
            if type(val1) != type(val2):
                if type(val1) in (datetime.datetime, datetime.date) or type(val2) in (datetime.datetime, datetime.date):
                    val1 = parseDate(val1)
                    val2 = parseDate(val2)

                elif type(val1) == bool:
                    val1 = int(val1)
                    if type(val2) == str:
                        val2 = { 'true': 1, 'false': 0 }.get(val2.lower(), val2)
                    if type(val2) in (int, bool):
                        val2 = int(val2)
                    else:
                        val2 = int(parseDouble(val2))

                elif type(val2) == bool:
                    val2 = int(val2)
                    if type(val1) == str:
                        val1 = { 'true': 1, 'false': 0 }.get(val1.lower(), val1)
                    if type(val1) in (int, bool):
                        val1 = int(val1)
                    else:
                        val1 = int(parseDouble(val1))

            if type(val1) != type(val2):
                val1 = stringify(val1)
                val2 = stringify(val2)

        return self._compare_values(val1, val2)


class PropertyIsEqualTo(BinaryComparisonOp):
    tagName = 'PropertyIsEqualTo'

    def simulate(self, *args, **kwargs):
        return super().simulate(*args, **kwargs) == 0


class PropertyIsNotEqualTo(BinaryComparisonOp):
    tagName = 'PropertyIsNotEqualTo'

    def simulate(self, *args, **kwargs):
        return super().simulate(*args, **kwargs) != 0

class PropertyIsGreaterThan(BinaryComparisonOp):
    tagName = 'PropertyIsGreaterThan'

    def simulate(self, *args, **kwargs):
        return super().simulate(*args, **kwargs) > 0


class PropertyIsLessThan(BinaryComparisonOp):
    tagName = 'PropertyIsLessThan'

    def simulate(self, *args, **kwargs):
        return super().simulate(*args, **kwargs) < 0


class PropertyIsGreaterThanOrEqualTo(BinaryComparisonOp):
    tagName = 'PropertyIsGreaterThanOrEqualTo'

    def simulate(self, *args, **kwargs):
        return super().simulate(*args, **kwargs) >= 0


class PropertyIsLessThanOrEqualTo(BinaryComparisonOp):
    tagName = 'PropertyIsLessThanOrEqualTo'

    def simulate(self, *args, **kwargs):
        return super().simulate(*args, **kwargs) <= 0


class PropertyIsLike(ComparisonOps, PropertyNameMixin, MatchCaseMixin):
    tagName = 'PropertyIsLike'
    def __init__(self, propertyname, pattern, wildCard='%', singleChar='_', escapeChar='\\', matchCase=None):
        super().__init__()
        self.propertyName = propertyname
        self.pattern = pattern
        self.wildCard = wildCard
        self.singleChar = singleChar
        self.escapeChar = escapeChar

        if len({wildCard, singleChar, escapeChar}) < 3:
            raise self.IllegalValue(f'wildCard, singleChar and escapeChar must different from each other!')
            
        self.matchCase = matchCase
        self.validate()

    @staticmethod    
    def _pattern_to_regex(pattern, wildCard, singleChar, escapeChar):    
        convert = {
            'WC': ('.*', re.escape(wildCard)),
            'SC': ('.', re.escape(singleChar)),
        }
        chars = []
        for c in pattern:
            if c == wildCard:
                chars += ['WC']
            elif c == singleChar:
                chars += ['SC']
            elif c == escapeChar:
                chars += ['EC']
            else:
                chars += [re.escape(c)]

        N = len(chars)
        for i in range(0, N - 1):
            if chars[i] == 'EC' and chars[i + 1] == 'EC':
                chars[i] = re.escape(escapeChar)
                chars[i + 1] = ''

        for i in range(N):
            if chars[i] in ('SC', 'WC'):
                if i > 0 and chars[i - 1] == 'EC':
                    chars[i - 1] = ''
                    chars[i] = convert[chars[i]][1]
                else:
                    chars[i] = convert[chars[i]][0]
        regex = ''
        for c in chars:
            if c == 'ECEC':
                regex += '\\\\'
            elif c == 'EC':
                regex += '\\'
            else:
                regex += c
        regex = '^' + regex + '$'
        return regex

    def _validate_and_set(self, char, argname):
        if not isinstance(char, str):
            raise TypeError(f'You cannot set {repr(char)} to {argname}. It must be a single character (string).')

        if len(char) != 1:
            raise ValueError(f'You cannot set {repr(char)} to {argname}. It must be a single character.')

        self.attrib[argname] = char
        
    def validate(self):
        if self.wildCard == self.singleChar:
            raise ValueError('wildCard and singleChar are identical ({repr{self.wildCard}}). They must be different.')

        if self.wildCard == self.escapeChar:
            raise ValueError('wildCard and escapeChar are identical ({repr{self.wildCard}}). They must be different.')

        if self.singleChar == self.escapeChar:
            raise ValueError('singleChar and escapeChar are identical ({repr{self.singleChar}}). They must be different.')
    
    @property
    def regex(self):
        self.validate()
        return self._pattern_to_regex(self.pattern.text, self.wildCard, self.singleChar, self.escapeChar)
    
    @property
    def wildCard(self):
        return self.attrib.get('wildCard', None)

    @wildCard.setter
    def wildCard(self, value):
        self._validate_and_set(value, 'wildCard')
        
    @property
    def singleChar(self):
        return self.attrib.get('singleChar', None)

    @singleChar.setter
    def singleChar(self, value):
        self._validate_and_set(value, 'singleChar')
        
    @property
    def escapeChar(self):
        return self.attrib.get('escapeChar', None)

    @escapeChar.setter
    def escapeChar(self, value):
        self._validate_and_set(value, 'escapeChar')

    @property
    def pattern(self):
        return self.children.get('pattern', None)

    @pattern.setter
    def pattern(self, value):
        if isinstance(value, str):
            value = Literal(value)

        if not isinstance(value, Literal):
            raise TypeError(f'You cannot set {repr(value)} to pattern. It must be string or Literal object')

        self.children['pattern'] = value

    def simulate(self, data, config=None):
        flags = 0
        if not self.matchCase:
            flags = re.I
        match = re.match(self.regex, stringify(self.propertyName.simulate(data, config)), flags)
        return match is not None


# Known problem: In GeoServer, PropertyIsNull is True for empty strings ('') when applied to inline features
# but False to spatial databases.
# The behaviour for inline features is coded in GeoServer but the latter depends on how the source DB treats 
# empty strings against SQL 'WHERE column IS NULL'
class PropertyIsNull(ComparisonOps, PropertyNameMixin):
    tagName = 'PropertyIsNull'

    def __init__(self, propertyname):
        super().__init__()
        self.propertyName = propertyname

    def simulate(self, data, config=None):
        val = self.propertyName.simulate(data)
        return val is None


class PropertyIsBetweenBoundary(OgcAbstract, OneExpressionMixin, OneExpressionOverloading):
    def __init__(self, expr):
        super().__init__()
        self.expr0 = expr

    def simulate(self, *args, **kwargs):
        return self.expr0.simulate(*args, **kwargs)


class LowerBoundary(PropertyIsBetweenBoundary):
    tagName = 'LowerBoundary'


class UpperBoundary(PropertyIsBetweenBoundary):
    tagName = 'UpperBoundary'


class PropertyIsBetween(ComparisonOps, OneExpressionMixin):
    tagName = 'PropertyIsBetween'
    
    def __init__(self, expr, lower_bounadry, upper_boundary):
        super().__init__()
        self.expr0 = expr
        self.lowerBoundary = lower_bounadry
        self.upperBoundary = upper_boundary
        
    def simulate(self, *args, **kwargs):
        test1 = PropertyIsGreaterThanOrEqualTo(self.expr0, self.lowerBoundary.expr0)
        test2 = PropertyIsLessThanOrEqualTo(self.expr0, self.upperBoundary.expr0)

        return test1.simulate(*args, **kwargs) and test2.simulate(*args, **kwargs)
        
    def _set_boundary(self, expr, klass):
        index = klass.tagName

        if isinstance(expr, klass):
            self.children[index] = obj
        else:
            self.children[index] = klass(expr)

    @property
    def lowerBoundary(self):
        return self.children.get(LowerBoundary.tagName, None)

    @lowerBoundary.setter
    def lowerBoundary(self, expr):
        self._set_boundary(expr, LowerBoundary)

    @property
    def upperBoundary(self):
        return self.children.get(UpperBoundary.tagName, None)

    @upperBoundary.setter
    def upperBoundary(self, expr):
        self._set_boundary(expr, UpperBoundary)
