import datetime
import math
from pytest import approx, raises

from ..ogc import Add, Sub, Mul, Div, Literal, PropertyName


data = {
    'geom_field': { 'type': 'Point',  'coordinates': [0, 0] },
    'string_field': ' foo bar ',
    'int_field': 13,
    'float_field': 1.4142,
    'date_field': datetime.date(2008, 4, 3),
    'datetime_field': datetime.datetime(2012, 12, 4, 13, 44, 25),
    'bool_field': True,
    'null_field': None,
}

def test_Add():
    lit1 = Literal(2)
    lit2 = Literal(' 3 ')
    add = Add(lit1, lit2)
    assert add.xml(True) == '<ogc:Add><ogc:Literal>2</ogc:Literal><ogc:Literal> 3 </ogc:Literal></ogc:Add>'
    assert add.simulate(data) == approx(5)

    add = Add(27, 85)
    assert add.xml(True) == '<ogc:Add><ogc:Literal>27</ogc:Literal><ogc:Literal>85</ogc:Literal></ogc:Add>'
    assert add.simulate(data) == approx(112)

    prop = PropertyName('int_field')
    add = Add(prop, 12)

    assert add.xml(True) == '<ogc:Add><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>12</ogc:Literal></ogc:Add>'
    assert add.simulate(data) == approx(25)

    prop = PropertyName('float_field')
    add = Add(prop, 3.34)
    assert add.simulate(data) == approx(1.4142 + 3.34)

    prop = PropertyName('null_field')
    add = Add(prop, 2.5)
    assert math.isnan(add.simulate(data)) is True

    prop = PropertyName('datetime_field')
    add = Add(prop, 10)
    with raises(TypeError):
        add.simulate(data)

    prop = PropertyName('bool_field')
    add = Add(prop, 10)
    with raises(TypeError):
        add.simulate(data)

    prop = PropertyName('string_field')
    add = Add(prop, 10)
    with raises(ValueError):
        add.simulate(data)


def test_addition_overloading():
    prop = PropertyName('int_field')
    add = prop + 1
    assert type(prop) == PropertyName
    assert type(add) == Add
    assert add.xml(True) == '<ogc:Add><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>1</ogc:Literal></ogc:Add>'

    add = 1 + prop
    assert type(prop) == PropertyName
    assert type(add) == Add
    assert add.xml(True) == '<ogc:Add><ogc:Literal>1</ogc:Literal><ogc:PropertyName>int_field</ogc:PropertyName></ogc:Add>'

    prop += 12
    assert type(prop) == Add
    assert prop.xml(True) == '<ogc:Add><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>12</ogc:Literal></ogc:Add>'


def test_Sub():
    lit1 = Literal(2)
    lit2 = Literal(' 3 ')
    sub = Sub(lit1, lit2)
    assert sub.xml(True) == '<ogc:Sub><ogc:Literal>2</ogc:Literal><ogc:Literal> 3 </ogc:Literal></ogc:Sub>'
    assert sub.simulate(data) == approx(-1)

    sub = Sub(96, 85)
    assert sub.xml(True) == '<ogc:Sub><ogc:Literal>96</ogc:Literal><ogc:Literal>85</ogc:Literal></ogc:Sub>'
    assert sub.simulate(data) == approx(11)

    prop = PropertyName('int_field')
    sub = Sub(prop, 6)
    assert sub.xml(True) == '<ogc:Sub><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>6</ogc:Literal></ogc:Sub>'
    assert sub.simulate(data) == approx(7)

    prop = PropertyName('float_field')
    sub = Sub(prop, 3.34)
    assert sub.simulate(data) == approx(1.4142 - 3.34)

    prop = PropertyName('null_field')
    sub = Sub(prop, 2.5)
    assert math.isnan(sub.simulate(data)) is True

    prop = PropertyName('datetime_field')
    sub = Sub(prop, 10)
    with raises(TypeError):
        sub.simulate(data)

    prop = PropertyName('bool_field')
    sub = Sub(prop, 10)
    with raises(TypeError):
        sub.simulate(data)

    prop = PropertyName('string_field')
    sub = Sub(prop, 10)
    with raises(ValueError):
        sub.simulate(data)


def test_subtraction_overloading():
    prop = PropertyName('int_field')
    sub = prop - 1
    assert type(prop) == PropertyName
    assert type(sub) == Sub
    assert sub.xml(True) == '<ogc:Sub><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>1</ogc:Literal></ogc:Sub>'

    sub = 1 - prop
    assert type(prop) == PropertyName
    assert type(sub) == Sub
    assert sub.xml(True) == '<ogc:Sub><ogc:Literal>1</ogc:Literal><ogc:PropertyName>int_field</ogc:PropertyName></ogc:Sub>'

    prop -= 12
    assert type(prop) == Sub
    assert prop.xml(True) == '<ogc:Sub><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>12</ogc:Literal></ogc:Sub>'


def test_Mul():
    lit1 = Literal(2)
    lit2 = Literal(' 3 ')
    mul = Mul(lit1, lit2)
    assert mul.xml(True) == '<ogc:Mul><ogc:Literal>2</ogc:Literal><ogc:Literal> 3 </ogc:Literal></ogc:Mul>'
    assert mul.simulate(data) == approx(6)

    mul = Mul(96, 85)
    assert mul.xml(True) == '<ogc:Mul><ogc:Literal>96</ogc:Literal><ogc:Literal>85</ogc:Literal></ogc:Mul>'
    assert mul.simulate(data) == approx(8160)

    prop = PropertyName('int_field')
    mul = Mul(prop, 6)
    assert mul.xml(True) == '<ogc:Mul><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>6</ogc:Literal></ogc:Mul>'
    assert mul.simulate(data) == approx(78)

    prop = PropertyName('float_field')
    mul = Mul(prop, 3.34)
    assert mul.simulate(data) == approx(1.4142 * 3.34)

    prop = PropertyName('null_field')
    mul = Mul(prop, 2.5)
    assert math.isnan(mul.simulate(data)) is True

    prop = PropertyName('datetime_field')
    mul = Mul(prop, 10)
    with raises(TypeError):
        mul.simulate(data)

    prop = PropertyName('bool_field')
    mul = Mul(prop, 10)
    with raises(TypeError):
        mul.simulate(data)

    prop = PropertyName('string_field')
    mul = Mul(prop, 10)
    with raises(ValueError):
        mul.simulate(data)


def test_multiply_overloading():
    prop = PropertyName('int_field')
    mul = prop * 1
    assert type(prop) == PropertyName
    assert type(mul) == Mul
    assert mul.xml(True) == '<ogc:Mul><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>1</ogc:Literal></ogc:Mul>'

    mul = 1 * prop
    assert type(prop) == PropertyName
    assert type(mul) == Mul
    assert mul.xml(True) == '<ogc:Mul><ogc:Literal>1</ogc:Literal><ogc:PropertyName>int_field</ogc:PropertyName></ogc:Mul>'

    prop *= 12
    assert type(prop) == Mul
    assert prop.xml(True) == '<ogc:Mul><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>12</ogc:Literal></ogc:Mul>'


def test_Div():
    lit1 = Literal(2)
    lit2 = Literal(' 3 ')
    div = Div(lit1, lit2)
    assert div.xml(True) == '<ogc:Div><ogc:Literal>2</ogc:Literal><ogc:Literal> 3 </ogc:Literal></ogc:Div>'
    assert div.simulate(data) == approx(2/3)

    div = Div(96, 0)
    assert div.xml(True) == '<ogc:Div><ogc:Literal>96</ogc:Literal><ogc:Literal>0</ogc:Literal></ogc:Div>'
    assert math.isinf(div.simulate(data)) is True

    prop = PropertyName('int_field')
    div = Div(prop, 6)
    assert div.xml(True) == '<ogc:Div><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>6</ogc:Literal></ogc:Div>'
    assert div.simulate(data) == approx(13 / 6)

    prop = PropertyName('float_field')
    div = Div(prop, 3.34)
    assert div.simulate(data) == approx(1.4142 / 3.34)

    prop = PropertyName('null_field')
    div = Div(prop, 2.5)
    assert math.isnan(div.simulate(data)) is True

    prop = PropertyName('datetime_field')
    div = Div(prop, 10)
    with raises(TypeError):
        div.simulate(data)

    prop = PropertyName('bool_field')
    div = Div(prop, 10)
    with raises(TypeError):
        div.simulate(data)

    prop = PropertyName('string_field')
    div = Div(prop, 10)
    with raises(ValueError):
        div.simulate(data)


def test_division_overloading():
    prop = PropertyName('int_field')
    div = prop / 5
    assert type(prop) == PropertyName
    assert type(div) == Div
    assert div.xml(True) == '<ogc:Div><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>5</ogc:Literal></ogc:Div>'

    div = 5 / prop
    assert type(prop) == PropertyName
    assert type(div) == Div
    assert div.xml(True) == '<ogc:Div><ogc:Literal>5</ogc:Literal><ogc:PropertyName>int_field</ogc:PropertyName></ogc:Div>'

    prop /= 12
    assert type(prop) == Div
    assert prop.xml(True) == '<ogc:Div><ogc:PropertyName>int_field</ogc:PropertyName><ogc:Literal>12</ogc:Literal></ogc:Div>'
