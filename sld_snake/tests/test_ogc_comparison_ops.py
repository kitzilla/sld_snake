import datetime
import pytest
import re
import sre_constants
from ..base import SLDConfig
from ..ogc import (
    PropertyIsEqualTo, PropertyIsNotEqualTo, PropertyIsGreaterThan, PropertyIsGreaterThanOrEqualTo, 
    PropertyIsLessThan, PropertyIsLessThanOrEqualTo, PropertyIsBetween, PropertyName, PropertyIsLike, PropertyIsNull
)
from ..ogc.comparison_ops import BinaryComparisonOp

from .utils import flatten_xml


data = {
    'geom_field': { 'type': 'Point',  'coordinates': [0, 0] },
    'string_field': ' foo bar ',
    'int_field': 13,
    'float_field': 1.4142,
    'date_field': datetime.date(2008, 4, 3),
    'datetime_field': datetime.datetime(2012, 12, 4, 13, 44, 25),
    'null_field': None,
    'zero_field': 0,
    'empty_field': '',
    'true_field': True,
    'false_field': False,
    'nan_field': float('nan')
}


def test_PropertyIsLike_pattern_to_regex():
    regex = PropertyIsLike._pattern_to_regex('abscdwesfgheijkee', 'w', 's', 'e')
    assert regex == r'^ab.cd.*sfgh\ijke$'
    
    # '\i' causes error for re but we leave it there
    with pytest.raises(sre_constants.error):
        re.match(regex, 'abccdsfghijke')

    regex = PropertyIsLike._pattern_to_regex('%rate!_!%!_(__!!)%', '%', '_', '!')
    assert regex == r'^.*rate_\%_\(..\!\).*$'
    assert re.match(regex, 'rate_%_(US!)') is not None
    assert re.match(regex, 'revised_rate_%_(JP!) inflation adjusted') is not None
    assert re.match(regex, 'revised_rate_%_(FRA) inflation adjusted') is None
    assert re.match(regex, 'revised_rate_%_(!)') is None

    regex = PropertyIsLike._pattern_to_regex(r'\* jo*n d.e\.\\w.s\\h\**e$', '*', '.', '\\')
    assert regex == r'^\*\ jo.*n\ d.e\.\\w.s\\h\*.*e\$$'
    assert re.match(regex, r'* john doe.\was\h*e$') is not None
    assert re.match(regex, r'* jon doe.\w?s\h*eeeee$') is not None
    assert re.match(regex, r'* jon de.\was\h*re$') is None
    assert re.match(regex, r'* jon dme.\was\h*re') is None


def test_PropertyIsLike():
    op = PropertyIsLike('string_field', '%f__ _ar%')
    assert op.pattern.text == '%f__ _ar%'
    assert op.wildCard == '%'  # Default
    assert op.singleChar == '_'  # Default
    assert op.escapeChar == '\\'  # Default
    assert op.matchCase is True  # Default
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsLike escapeChar="\\" singleChar="_" wildCard="%">
            <ogc:PropertyName>string_field</ogc:PropertyName>
            <ogc:Literal>%f__ _ar%</ogc:Literal>
        </ogc:PropertyIsLike>
        '''
    )
    assert op.simulate(data) is True

    op.pattern = '%F__ _ar '
    assert op.pattern.text == '%F__ _ar '
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsLike escapeChar="\\" singleChar="_" wildCard="%">
            <ogc:PropertyName>string_field</ogc:PropertyName>
            <ogc:Literal>%F__ _ar </ogc:Literal>
        </ogc:PropertyIsLike>
        '''
    )
    assert op.simulate(data) is False
    
    op.matchCase = False
    assert op.matchCase is False
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsLike escapeChar="\\" matchCase="false" singleChar="_" wildCard="%">
            <ogc:PropertyName>string_field</ogc:PropertyName>
            <ogc:Literal>%F__ _ar </ogc:Literal>
        </ogc:PropertyIsLike>
        '''
    )
    assert op.simulate(data) is True

    op.singleChar = 'o'
    assert op.singleChar == 'o'
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsLike escapeChar="\\" matchCase="false" singleChar="o" wildCard="%">
            <ogc:PropertyName>string_field</ogc:PropertyName>
            <ogc:Literal>%F__ _ar </ogc:Literal>
        </ogc:PropertyIsLike>
        '''
    )
    assert op.simulate(data) is False

    op.wildCard = 'm'
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsLike escapeChar="\\" matchCase="false" singleChar="o" wildCard="m">
            <ogc:PropertyName>string_field</ogc:PropertyName>
            <ogc:Literal>%F__ _ar </ogc:Literal>
        </ogc:PropertyIsLike>
        '''
    )
    op.escapeChar = '&'
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsLike escapeChar="&amp;" matchCase="false" singleChar="o" wildCard="m">
            <ogc:PropertyName>string_field</ogc:PropertyName>
            <ogc:Literal>%F__ _ar </ogc:Literal>
        </ogc:PropertyIsLike>
        '''
    )
    with pytest.raises(TypeError):
        # Operator overloading to PropertyName should be prevented
        op.propertyName /= 1
    
    op = PropertyIsLike('true_field', 'tr%')
    assert op.simulate(data) is True
    op.pattern = '__lse'
    assert op.simulate(data) is False
    op.propertyName = 'false_field'
    assert op.simulate(data) is True
    
    op = PropertyIsLike('float_field', '1_41%')
    assert op.simulate(data) is True
    
    op.pattern = '1.41____'
    assert op.simulate(data) is False

    op = PropertyIsLike('date_field', '20__-04%')
    assert op.simulate(data) is True
    op.pattern = '%T%'
    assert op.simulate(data) is False
    op.propertyName = 'datetime_field'
    assert op.simulate(data) is True
    
    

def test_PropertyIsNull():
    op = PropertyIsNull('null_field')
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsNull>
            <ogc:PropertyName>null_field</ogc:PropertyName>
        </ogc:PropertyIsNull>
        '''
    )
    assert op.simulate(data) is True
    assert op.propertyName.text == 'null_field'

    op.propertyName = PropertyName('empty_field')
    assert op.propertyName.text == 'empty_field'
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsNull>
            <ogc:PropertyName>empty_field</ogc:PropertyName>
        </ogc:PropertyIsNull>
        '''
    )
    assert op.simulate(data) is False

    op.propertyName = 'zero_field'
    assert op.propertyName.text == 'zero_field'
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsNull>
            <ogc:PropertyName>zero_field</ogc:PropertyName>
        </ogc:PropertyIsNull>
        '''
    )
    assert op.simulate(data) is False
    
    with pytest.raises(TypeError):
        # Operator overloading to PropertyName should be prevented
        op.propertyName += 1
    
    op = PropertyIsNull('false_field')
    assert op.simulate(data) is False
    
    op = PropertyIsNull('nan_field')
    assert op.simulate(data) is False

    op = PropertyIsNull('string_field')
    assert op.simulate(data) is False

    comp = PropertyIsNull('float_field')
    assert comp.simulate(data) is False


def test_BinaryComparisonOp():
    prop = PropertyName('int_field')
    op = BinaryComparisonOp(prop, 13)

    assert op.simulate(data) == 0
    
    op = BinaryComparisonOp(prop, '  13  ')
    assert op.simulate(data) == 0

    op = BinaryComparisonOp(prop, '13.0001')
    assert op.simulate(data) == -1
    
    op.expr1 = 12.999
    assert op.simulate(data) == 1

    op.expr0 *= 2
    op.expr1 = 26
    assert op.simulate(data) == 0

    op.expr0 = PropertyName('float_field')
    assert op.simulate(data) == -1
    op.expr1 = 1.4142
    assert op.simulate(data) == 0

    op.expr0 = PropertyName('date_field')
    with pytest.raises(ValueError):   # Strings that cannot be parsed to datetime raise exception
        op.simulate(data)

    op.expr1 = datetime.date(2008, 4, 3)
    assert op.simulate(data) == 0
    
    op.expr1 = '2008-04-03'
    assert op.simulate(data) == 0

    op.expr1 = '2008-04-03T00:00:00'
    assert op.simulate(data) == 0

    op.expr1 = '2008-04-03T01:00:00'
    assert op.simulate(data) == -1
        
    op.expr0 = PropertyName('datetime_field')
    assert op.simulate(data) == 1
    
    op.expr1 = datetime.datetime(2012, 12, 4, 13, 44, 25)
    assert op.simulate(data) == 0
    
    op.expr1 = '2012-12-04T13:44:25.000'
    assert op.simulate(data) == 0

    op.expr1 = '2012-12-04T11:14:25-02:30'
    assert op.simulate(data) == 0
    
    op.expr1 = '2012-12-04T11:14:25.000-02:00'
    assert op.simulate(data) == 1
    
    op.expr0 = PropertyName('true_field')  # True is evaluated as 1
    with pytest.raises(ValueError):
        op.simulate(data)
    
    op.expr1 = 'true'
    assert op.simulate(data) == 0  # 'true' (with not spaces around) is evaluated as 1

    op.expr1 = 'true '
    with pytest.raises(ValueError):
        op.simulate(data)  # 'true ' (with a trailing space) raises exception
    
    op.expr1 = 1.8
    assert op.simulate(data) == 0 # 1.8 is evaluated as 1

    op.expr1 = 2
    assert op.simulate(data) == -1

    op.expr1 = 0
    assert op.simulate(data) == 1
    
    
    op.expr0 = PropertyName('false_field')  # False is evaluated as 0
    assert op.simulate(data) == 0

    op.expr1 = 0.5
    assert op.simulate(data) == 0   # 0.5 is evaluated as 0

    op.expr1 = -0.5
    assert op.simulate(data) == 0   # -0.5 is evaluated as 0

    op.expr1 = -1.5
    assert op.simulate(data) == 1   # -1.5 is evaluated as -1

    op.expr1 = 'false'
    assert op.simulate(data) == 0   # 'false' (with not spaces around) is evaluated as 0

    op.expr1 = ' false'
    with pytest.raises(ValueError):
        op.simulate(data)  # ' false' (with a leading space) raises exception

    op.expr1 = 'true'
    assert op.simulate(data) == -1


def test_PropertyIsEqualTo(mocker):
    prop = PropertyName('int_field')
    op = PropertyIsEqualTo(prop, 13)
    
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsEqualTo>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:Literal>13</ogc:Literal>
        </ogc:PropertyIsEqualTo>
        '''
    )
    assert op.simulate(data) is True
    
    op = PropertyIsEqualTo(prop, '  13  ')
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsEqualTo>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:Literal>  13  </ogc:Literal>
        </ogc:PropertyIsEqualTo>
        '''
    )
    assert op.simulate(data) is True
    
    op.expr0 *= 2
    op.expr1 = 26
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsEqualTo>
            <ogc:Mul>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>2</ogc:Literal>
            </ogc:Mul>
            <ogc:Literal>26</ogc:Literal>
        </ogc:PropertyIsEqualTo>
        '''
    )
    assert op.simulate(data) is True

    op.expr0 = PropertyName('float_field')
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsEqualTo>
            <ogc:PropertyName>float_field</ogc:PropertyName>
            <ogc:Literal>26</ogc:Literal>
        </ogc:PropertyIsEqualTo>
        '''
    )
    assert op.simulate(data) is False
        
    mock_simulate = mocker.patch.object(BinaryComparisonOp, 'simulate')
    mock_simulate.return_value = 0
    assert op.simulate(data) is True

    mock_simulate.return_value = 1
    assert op.simulate(data) is False
    
    mock_simulate.return_value = -1
    assert op.simulate(data) is False
    

def test_PropertyIsNotEqualTo(mocker):
    prop = PropertyName('int_field')
    op = PropertyIsNotEqualTo(prop, 13)
    
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsNotEqualTo>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:Literal>13</ogc:Literal>
        </ogc:PropertyIsNotEqualTo>
        '''
    )
    op = PropertyIsNotEqualTo(prop, '  13  ')
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsNotEqualTo>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:Literal>  13  </ogc:Literal>
        </ogc:PropertyIsNotEqualTo>
        '''
    )
    op = PropertyIsNotEqualTo(prop, '13.01')

    op.expr0 *= 2
    op.expr1 = 26
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsNotEqualTo>
            <ogc:Mul>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>2</ogc:Literal>
            </ogc:Mul>
            <ogc:Literal>26</ogc:Literal>
        </ogc:PropertyIsNotEqualTo>
        '''
    )
    op.expr0 = PropertyName('float_field')
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsNotEqualTo>
            <ogc:PropertyName>float_field</ogc:PropertyName>
            <ogc:Literal>26</ogc:Literal>
        </ogc:PropertyIsNotEqualTo>
        '''
    )
    mock_simulate = mocker.patch.object(BinaryComparisonOp, 'simulate')
    mock_simulate.return_value = 0
    assert op.simulate(data) is False

    mock_simulate.return_value = 1
    assert op.simulate(data) is True
    
    mock_simulate.return_value = -1
    assert op.simulate(data) is True


def test_PropertyIsGreaterThan(mocker):
    prop = PropertyName('int_field')
    op = PropertyIsGreaterThan(prop, 13)
    
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsGreaterThan>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:Literal>13</ogc:Literal>
        </ogc:PropertyIsGreaterThan>
        '''
    )
    op.expr1 += 2
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsGreaterThan>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:Add>
                <ogc:Literal>13</ogc:Literal>
                <ogc:Literal>2</ogc:Literal>
            </ogc:Add>
        </ogc:PropertyIsGreaterThan>
        '''
    )
    mock_simulate = mocker.patch.object(BinaryComparisonOp, 'simulate')
    mock_simulate.return_value = 0
    assert op.simulate(data) is False

    mock_simulate.return_value = 1
    assert op.simulate(data) is True
    
    mock_simulate.return_value = -1
    assert op.simulate(data) is False
    

def test_PropertyIsGreaterThanOrEqualTo(mocker):
    prop = PropertyName('int_field')
    op = PropertyIsGreaterThanOrEqualTo(prop, 13)
    
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsGreaterThanOrEqualTo>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:Literal>13</ogc:Literal>
        </ogc:PropertyIsGreaterThanOrEqualTo>
        '''
    )
    op.expr0 -= 3
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsGreaterThanOrEqualTo>
            <ogc:Sub>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>3</ogc:Literal>
            </ogc:Sub>
            <ogc:Literal>13</ogc:Literal>
        </ogc:PropertyIsGreaterThanOrEqualTo>
        '''
    )
    mock_simulate = mocker.patch.object(BinaryComparisonOp, 'simulate')
    mock_simulate.return_value = 0
    assert op.simulate(data) is True

    mock_simulate.return_value = 1
    assert op.simulate(data) is True
    
    mock_simulate.return_value = -1
    assert op.simulate(data) is False
    
    
def test_PropertyIsLessThan(mocker):
    prop = PropertyName('int_field')
    op = PropertyIsLessThan(prop, 13)
    
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsLessThan>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:Literal>13</ogc:Literal>
        </ogc:PropertyIsLessThan>
        '''
    )
    op.expr0 /= 3
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsLessThan>
            <ogc:Div>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>3</ogc:Literal>
            </ogc:Div>
            <ogc:Literal>13</ogc:Literal>
        </ogc:PropertyIsLessThan>
        '''
    )
    mock_simulate = mocker.patch.object(BinaryComparisonOp, 'simulate')
    mock_simulate.return_value = 0
    assert op.simulate(data) is False

    mock_simulate.return_value = 1
    assert op.simulate(data) is False
    
    mock_simulate.return_value = -1
    assert op.simulate(data) is True
    
    
def test_PropertyIsLessThanOrEqualTo(mocker):
    prop = PropertyName('int_field')
    op = PropertyIsLessThanOrEqualTo(prop, 13)
    
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsLessThanOrEqualTo>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:Literal>13</ogc:Literal>
        </ogc:PropertyIsLessThanOrEqualTo>
        '''
    )
    op.expr0 *= -1
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsLessThanOrEqualTo>
            <ogc:Mul>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>-1</ogc:Literal>
            </ogc:Mul>
            <ogc:Literal>13</ogc:Literal>
        </ogc:PropertyIsLessThanOrEqualTo>
        '''
    )
    mock_simulate = mocker.patch.object(BinaryComparisonOp, 'simulate')
    mock_simulate.return_value = 0
    assert op.simulate(data) is True

    mock_simulate.return_value = 1
    assert op.simulate(data) is False
    
    mock_simulate.return_value = -1
    assert op.simulate(data) is True


def test_PropertyIsBetween():
    op = PropertyIsBetween(PropertyName('int_field'), 13, 16)
    
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsBetween>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:LowerBoundary>
                <ogc:Literal>13</ogc:Literal>
            </ogc:LowerBoundary>
            <ogc:UpperBoundary>
                <ogc:Literal>16</ogc:Literal>
            </ogc:UpperBoundary>
        </ogc:PropertyIsBetween>
        '''
    )
    assert op.simulate(data) is True  # 13 <= 13 <= 16
    
    op.lowerBoundary += 0.001
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsBetween>
            <ogc:PropertyName>int_field</ogc:PropertyName>
            <ogc:LowerBoundary>
                <ogc:Add>
                    <ogc:Literal>13</ogc:Literal>
                    <ogc:Literal>0.001</ogc:Literal>
                </ogc:Add>
            </ogc:LowerBoundary>
            <ogc:UpperBoundary>
                <ogc:Literal>16</ogc:Literal>
            </ogc:UpperBoundary>
        </ogc:PropertyIsBetween>
        '''
    )
    assert op.simulate(data) is False  # 13.001 <= 13 <= 16
    
    op.expr0 = PropertyName('float_field')
    op.lowerBoundary = -1
    op.upperBoundary /= 10
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsBetween>
            <ogc:PropertyName>float_field</ogc:PropertyName>
            <ogc:LowerBoundary>
                <ogc:Literal>-1</ogc:Literal>
            </ogc:LowerBoundary>
            <ogc:UpperBoundary>
                <ogc:Div>
                    <ogc:Literal>16</ogc:Literal>
                    <ogc:Literal>10</ogc:Literal>
                </ogc:Div>
            </ogc:UpperBoundary>
        </ogc:PropertyIsBetween>
        '''
    )
    assert op.simulate(data) is True  # -1 <= 1.4142 <= 1.6
    
    op.upperBoundary -= 0.3
    assert op.xml(True) == flatten_xml(
        '''
        <ogc:PropertyIsBetween>
            <ogc:PropertyName>float_field</ogc:PropertyName>
            <ogc:LowerBoundary>
                <ogc:Literal>-1</ogc:Literal>
            </ogc:LowerBoundary>
            <ogc:UpperBoundary>
                <ogc:Sub>
                    <ogc:Div>
                        <ogc:Literal>16</ogc:Literal>
                        <ogc:Literal>10</ogc:Literal>
                    </ogc:Div>
                    <ogc:Literal>0.3</ogc:Literal>
                </ogc:Sub>
            </ogc:UpperBoundary>
        </ogc:PropertyIsBetween>
        '''
    )
    assert op.simulate(data) is False  # -1 <= 1.4142 <= 1.3


def test_AND_overloading():
    op1 = PropertyIsEqualTo(PropertyName('int_field'), 13)  # True
    op2 = PropertyIsLike(PropertyName('string_field'), '%foo%')   # True
    op3 = PropertyIsLessThan(PropertyName('float_field'), 1.4)  # False
    op4 = PropertyIsNull(PropertyName('null_field'))  # True
    op5 = PropertyIsGreaterThan(PropertyName('date_field'), '2000-01-01')  # True
    
    and1 = op1 & op2
    
    assert and1.xml(True) == flatten_xml(
        '''
        <ogc:And>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>13</ogc:Literal>
            </ogc:PropertyIsEqualTo>
            <ogc:PropertyIsLike escapeChar="\\" singleChar="_" wildCard="%">
                <ogc:PropertyName>string_field</ogc:PropertyName>
                <ogc:Literal>%foo%</ogc:Literal>
            </ogc:PropertyIsLike>
        </ogc:And>
        '''
    )
    assert and1.simulate(data) is True

    and1 &= op3
    assert and1.xml(True) == flatten_xml(
        '''
        <ogc:And>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>13</ogc:Literal>
            </ogc:PropertyIsEqualTo>
            <ogc:PropertyIsLike escapeChar="\\" singleChar="_" wildCard="%">
                <ogc:PropertyName>string_field</ogc:PropertyName>
                <ogc:Literal>%foo%</ogc:Literal>
            </ogc:PropertyIsLike>
            <ogc:PropertyIsLessThan>
                <ogc:PropertyName>float_field</ogc:PropertyName>
                <ogc:Literal>1.4</ogc:Literal>
            </ogc:PropertyIsLessThan>
        </ogc:And>
        '''
    )
    assert and1.simulate(data) is False
    
    and2 = op4 & op5
    assert and2.xml(True) == flatten_xml(
        '''
        <ogc:And>
            <ogc:PropertyIsNull>
                <ogc:PropertyName>null_field</ogc:PropertyName>
            </ogc:PropertyIsNull>
            <ogc:PropertyIsGreaterThan>
                <ogc:PropertyName>date_field</ogc:PropertyName>
                <ogc:Literal>2000-01-01</ogc:Literal>
            </ogc:PropertyIsGreaterThan>
        </ogc:And>
        '''
    )
    assert and2.simulate(data) is True
    
    and2 &= and1
    assert and2.xml(True) == flatten_xml(
        '''
        <ogc:And>
            <ogc:PropertyIsNull>
                <ogc:PropertyName>null_field</ogc:PropertyName>
            </ogc:PropertyIsNull>
            <ogc:PropertyIsGreaterThan>
                <ogc:PropertyName>date_field</ogc:PropertyName>
                <ogc:Literal>2000-01-01</ogc:Literal>
            </ogc:PropertyIsGreaterThan>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>13</ogc:Literal>
            </ogc:PropertyIsEqualTo>
            <ogc:PropertyIsLike escapeChar="\\" singleChar="_" wildCard="%">
                <ogc:PropertyName>string_field</ogc:PropertyName>
                <ogc:Literal>%foo%</ogc:Literal>
            </ogc:PropertyIsLike>
            <ogc:PropertyIsLessThan>
                <ogc:PropertyName>float_field</ogc:PropertyName>
                <ogc:Literal>1.4</ogc:Literal>
            </ogc:PropertyIsLessThan>
        </ogc:And>
        '''
    )
    
    
def test_OR_overloading():
    op1 = PropertyIsEqualTo(PropertyName('int_field'), 13)  # True
    op2 = PropertyIsLike(PropertyName('string_field'), '___foo%')   # False
    op3 = PropertyIsLessThan(PropertyName('float_field'), 1.4)  # False
    op4 = PropertyIsNull(PropertyName('null_field'))  # True
    op5 = PropertyIsGreaterThan(PropertyName('date_field'), '2011-01-01')  # False
    
    or1 = op3 | op5
    
    assert or1.xml(True) == flatten_xml(
        '''
        <ogc:Or>
            <ogc:PropertyIsLessThan>
                <ogc:PropertyName>float_field</ogc:PropertyName>
                <ogc:Literal>1.4</ogc:Literal>
            </ogc:PropertyIsLessThan>
            <ogc:PropertyIsGreaterThan>
                <ogc:PropertyName>date_field</ogc:PropertyName>
                <ogc:Literal>2011-01-01</ogc:Literal>
            </ogc:PropertyIsGreaterThan>
        </ogc:Or>
        '''
    )
    assert or1.simulate(data) is False

    or1 |= op1
    assert or1.xml(True) == flatten_xml(
        '''
        <ogc:Or>
            <ogc:PropertyIsLessThan>
                <ogc:PropertyName>float_field</ogc:PropertyName>
                <ogc:Literal>1.4</ogc:Literal>
            </ogc:PropertyIsLessThan>
            <ogc:PropertyIsGreaterThan>
                <ogc:PropertyName>date_field</ogc:PropertyName>
                <ogc:Literal>2011-01-01</ogc:Literal>
            </ogc:PropertyIsGreaterThan>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>13</ogc:Literal>
            </ogc:PropertyIsEqualTo>
        </ogc:Or>
        '''
    )
    assert or1.simulate(data) is True
    
    or2 = op2 | op4
    assert or2.xml(True) == flatten_xml(
        '''
        <ogc:Or>
            <ogc:PropertyIsLike escapeChar="\\" singleChar="_" wildCard="%">
                <ogc:PropertyName>string_field</ogc:PropertyName>
                <ogc:Literal>___foo%</ogc:Literal>
            </ogc:PropertyIsLike>
            <ogc:PropertyIsNull>
                <ogc:PropertyName>null_field</ogc:PropertyName>
            </ogc:PropertyIsNull>
        </ogc:Or>
        '''
    )
    assert or2.simulate(data) is True
    
    or2 |= or1
    assert or2.xml(True) == flatten_xml(
        '''
        <ogc:Or>
            <ogc:PropertyIsLike escapeChar="\\" singleChar="_" wildCard="%">
                <ogc:PropertyName>string_field</ogc:PropertyName>
                <ogc:Literal>___foo%</ogc:Literal>
            </ogc:PropertyIsLike>
            <ogc:PropertyIsNull>
                <ogc:PropertyName>null_field</ogc:PropertyName>
            </ogc:PropertyIsNull>
            <ogc:PropertyIsLessThan>
                <ogc:PropertyName>float_field</ogc:PropertyName>
                <ogc:Literal>1.4</ogc:Literal>
            </ogc:PropertyIsLessThan>
            <ogc:PropertyIsGreaterThan>
                <ogc:PropertyName>date_field</ogc:PropertyName>
                <ogc:Literal>2011-01-01</ogc:Literal>
            </ogc:PropertyIsGreaterThan>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>13</ogc:Literal>
            </ogc:PropertyIsEqualTo>
        </ogc:Or>
        '''
    )


def test_INVERT_overloading():
    op1 = PropertyIsEqualTo(PropertyName('int_field'), 13)  # True
    
    not1 = ~op1
    
    assert not1.xml(True) == flatten_xml(
        '''
        <ogc:Not>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>int_field</ogc:PropertyName>
                <ogc:Literal>13</ogc:Literal>
            </ogc:PropertyIsEqualTo>
        </ogc:Not>
        '''
    )
    assert not1.simulate(data) is False
    
    not2 = ~not1
    
    assert not2 is op1
    assert not2.simulate(data) is True
