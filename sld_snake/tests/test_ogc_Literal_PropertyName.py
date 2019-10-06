import datetime
from pytest import approx

from ..ogc import Literal, PropertyName


def test_Literal():
    elem = Literal(' foo bar ')
    assert elem.xml(True) == '<ogc:Literal> foo bar </ogc:Literal>'
    assert elem.simulate(None) == ' foo bar '

    elem = Literal(datetime.datetime(1996, 3, 18, 19, 12, 25))
    assert elem.xml(True) == '<ogc:Literal>1996-03-18T19:12:25</ogc:Literal>'
    assert elem.simulate(None) == '1996-03-18T19:12:25'

    elem = Literal(True)
    assert elem.simulate(None) == 'true'

    elem = Literal(False)
    assert elem.simulate(None) == 'false'

    elem = Literal(None)
    assert elem.simulate(None) == ''

    elem = Literal(42)
    assert elem.simulate(None) == '42'

    elem = Literal(3.14)
    assert elem.simulate(None)[:4] == '3.14'


def test_PropertyName():
    data = {
        'geom_field': { 'type': 'Point', 'coordinates': [0, 0] },
        'string_field': ' foo bar ',
        'int_field': 13,
        'float_field': 1.4142,
        'date_field': datetime.date(2008, 4, 3),
        'datetime_field': datetime.datetime(2012, 12, 4, 13, 44, 25),
        'bool_field': True,
        'null_field': None,
    }
    elem = PropertyName('string_field')
    assert elem.xml(True) == '<ogc:PropertyName>string_field</ogc:PropertyName>'
    assert elem.simulate(data) == ' foo bar '
    
    elem = PropertyName('int_field')
    assert elem.xml(True) == '<ogc:PropertyName>int_field</ogc:PropertyName>'
    assert elem.simulate(data) == 13
    
    elem = PropertyName('float_field')
    assert elem.simulate(data) == approx(1.4142)
    
    elem = PropertyName('date_field')
    dt = elem.simulate(data)
    assert type(dt) == datetime.date
    assert (dt.year, dt.month, dt.day) == (2008, 4, 3)
    
    elem = PropertyName('datetime_field')
    dt = elem.simulate(data)
    assert (dt.year, dt.month, dt.day) == (2012, 12, 4)
    assert (dt.hour, dt.minute, dt.second) == (13, 44, 25)

    elem = PropertyName('bool_field')
    assert elem.simulate(data) is True
    
    elem = PropertyName('null_field')
    assert elem.simulate(data) is None
    
    
    