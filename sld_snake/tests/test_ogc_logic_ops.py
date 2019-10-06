import pytest
from ..ogc.logic_ops import LogicDict
from ..ogc import PropertyIsEqualTo, PropertyName


def test_LogicDict():
    prop = PropertyName('field')
    logic0 = PropertyIsEqualTo(prop, 1)
    logic1 = PropertyIsEqualTo(prop, 2)
    logic2 = PropertyIsEqualTo(prop, 3)
    
    logdic = LogicDict()
    logdic[0] = logic0
    logdic[1] = logic1
    logdic[2] = logic2
    
    assert list(logdic.keys()) == [0, 1, 2]
    assert list(logdic.values()) == [logic0, logic1, logic2]

    # LogicDict only accepts subclasses of LogicOpAbstract
    with pytest.raises(TypeError):
        logdic[3] = prop
    
    # Delete item that does not exist
    with pytest.raises(KeyError):
        del logdic[3]
    
    # Deletion should work like list.pop(i)
    del logdic[0]
    assert list(logdic.keys()) == [0, 1]
    assert list(logdic.values()) == [logic1, logic2]

    logdic[0] = logic0
    assert list(logdic.values()) == [logic0, logic2]

    del logdic[1]
    assert list(logdic.keys()) == [0]
    assert list(logdic.values()) == [logic0]
