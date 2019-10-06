from ..base import ElemAbstract


def test_ElemAbstract_xml():
    class Foo(ElemAbstract):
        nameSpace = 'ogc'
        tagName = 'Foo'
        
    class Bar(ElemAbstract):
        nameSpace = 'sld'
        tagName = 'Bar'

    class Ash(ElemAbstract):
        nameSpace = 'sld'
        tagName = 'Ash'
    
    elem = Foo()
    assert elem.xml() == '<ogc:Foo xmlns:ogc="http://www.opengis.net/ogc" />'
    assert elem.xml(no_xmlns=True) == '<ogc:Foo />'
    
    non_ascii1 = 'Mußt\' es eben leiden. Röslein, Röslein, Röslein roth'
    elem.text = non_ascii1
    assert elem.xml(no_xmlns=True) == '<ogc:Foo>Mußt\' es eben leiden. Röslein, Röslein, Röslein roth</ogc:Foo>'

    non_ascii2 = '折られてあわれ　清らの色香 永久にあせぬ　紅におう'
    elem.text = non_ascii2
    assert elem.xml(no_xmlns=True) == '<ogc:Foo>折られてあわれ　清らの色香 永久にあせぬ　紅におう</ogc:Foo>'
    
    elem.text = None
    elem.children['bar'] = Bar()
    elem.children['ash'] = Ash()
    assert elem.xml(True) == '<ogc:Foo><sld:Bar /><sld:Ash /></ogc:Foo>'
    
    