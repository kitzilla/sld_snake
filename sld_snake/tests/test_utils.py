import datetime
# from dateutil import tz
import math
from pytest import raises, approx


from ..utils import parseDouble, stringify, parseDate


def test_parseDouble():
    # Java parseDouble accepts 'NaN'
    assert math.isnan(parseDouble('NaN')) is True
    assert math.isnan(parseDouble(' +NaN')) is True
    assert math.isnan(parseDouble('  -NaN   ')) is True

    # 'nan' which is understood by Python float() should not be accepted
    with raises(ValueError):
        parseDouble('nan')

    # Java parseDouble accepts 'Infinity'
    inf_pos = parseDouble(' +Infinity  ')
    assert math.isinf(inf_pos) is True
    assert inf_pos > 0

    inf_neg = parseDouble(' -Infinity  ')
    assert math.isinf(inf_neg) is True
    assert inf_neg < 0
    
    # 'inf', 'INF', 'InF' etc which are understood by Python float() should not be accepted
    with raises(ValueError):
        parseDouble('inf')
        
    with raises(ValueError):
        parseDouble('INF')

    assert parseDouble('3.14159') == approx(3.14159)
    assert parseDouble(' -3.5E+4  ') == approx(-35000)    
    
    # Thousand separators are not understood as part of number in GeoServer (Java)
    with raises(ValueError):
        parseDouble('1,024')

    with raises(ValueError):
        parseDouble('42 is the answer')


def test_parseDate():
    date = datetime.date(2014, 6, 15)
    dt = parseDate(date)
    assert (dt.year, dt.month, dt.day) == (2014, 6, 15)

    assert (dt.hour, dt.minute, dt.second, dt.microsecond) == (0, 0, 0, 0)
    dt = parseDate('2011-03-01T15:23:45-01:00')
    assert (dt.year, dt.month, dt.day) == (2011, 3, 1)
    assert (dt.hour, dt.minute, dt.second, dt.microsecond) == (15, 23, 45, 0)
    assert dt.tzinfo.utcoffset(None).total_seconds() == -3600
    
    dt = parseDate('1974-09-24T01:14:29.560+02:30')
    assert (dt.year, dt.month, dt.day) == (1974, 9, 24)
    assert (dt.hour, dt.minute, dt.second, dt.microsecond) == (1, 14, 29, 560 * 1000)
    assert dt.tzinfo.utcoffset(None).total_seconds() == 9000

    dt = parseDate('2000-02-28T02:48:27.854+02')
    assert (dt.year, dt.month, dt.day) == (2000, 2, 28)
    assert (dt.hour, dt.minute, dt.second, dt.microsecond) == (2, 48, 27, 854 * 1000)
    assert dt.tzinfo.utcoffset(None).total_seconds() == 7200

    dt = parseDate('2004-11-08T09:02:00.000Z')
    assert (dt.year, dt.month, dt.day) == (2004, 11, 8)
    assert (dt.hour, dt.minute, dt.second, dt.microsecond) == (9, 2, 0, 0)
    assert dt.tzinfo is None

    dt = parseDate('2004-12-31T20:12:33.015')
    assert (dt.year, dt.month, dt.day) == (2004, 12, 31)
    assert (dt.hour, dt.minute, dt.second, dt.microsecond) == (20, 12, 33, 15 * 1000)
    assert dt.tzinfo is None

    dt = parseDate('2034-07-13')
    assert (dt.year, dt.month, dt.day) == (2034, 7, 13)
    assert (dt.hour, dt.minute, dt.second, dt.microsecond) == (0, 0, 0, 0)
    assert dt.tzinfo is None


def test_stringify():
    assert stringify('foo') == 'foo'
    assert stringify(True) == 'true'
    assert stringify(False) == 'false'
    assert stringify(None) == ''
    assert stringify(float('nan')) == 'NaN'
    assert stringify(float('+inf')) == 'Infinity'    
    assert stringify(float('-inf')) == '-Infinity'
    
    assert stringify(3.14159)[:7] == '3.14159'
    
    dt = parseDate('2011-03-01T15:23:45-01:00')
    assert stringify(dt) == '2011-03-01T15:23:45-01:00'
    
    dt = parseDate('2004-12-31T20:12:33.015')
    assert stringify(dt) == '2004-12-31T20:12:33.015'

    
    