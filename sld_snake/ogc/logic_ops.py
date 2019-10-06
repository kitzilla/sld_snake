from collections import OrderedDict

from .base import OgcAbstract


class LogicOpAbstract(OgcAbstract):
    def __and__(self, other):
        return And(self, other)

    def __rand__(self, other):
        return And(other, self)

    def __or__(self, other):
        return Or(self, other)
        
    def __ror__(self, other):
        return Or(other, self)
        
    def __invert__(self):
        return Not(self)


class LogicDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, item):
        if not isinstance(item, LogicOpAbstract):
            raise TypeError(f'{repr(item)} is neither of logic (And, Or, Not) nor comparison (eg. PropertyIsEqualTo, Intersects)')
        super().__setitem__(key, item)

    def __delitem__(self, key):
        if key not in self:
            super().__delitem__(key)  # raise exception from super class
        else:
            newkey = 0
            for oldkey in self.keys():
                if oldkey == key:
                    continue
                if oldkey != newkey:
                    self[newkey] = self[oldkey]
                newkey += 1
            super().__delitem__(oldkey)


class LogicOp(LogicOpAbstract):
    def __init__(self):
        super().__init__()
        self.children = LogicDict()
        self.conditions = self.children  # alias


class UnaryLogicOp(LogicOp):
    def __init__(self, condition):
        super().__init__()
        self.conditions[0] = condition
        

class BinaryLogicOp(LogicOp):
    def __init__(self, condition0, condition1, *extra_logics):
        super().__init__()
        self.conditions[0] = condition0
        self.conditions[1] = condition1

        for i, logic in enumerate(extra_logics, 2):
            self.conditions[i] = logic

    def append_condition(self, condition):
        self.conditions[len(self.conditions)] = condition

    def prepend_condition(self, condition):
        new_lst = [(0, condition)]
        for i, cond in enumerate(self.conditions.values(), 1):
            new_lst += [(i, cond)]
        self.conditions = OrderedDict(new_lst)
        self.children = self.conditions


class Not(UnaryLogicOp):
    tagName = 'Not'
    def simulate(self, data):
        return not self.conditions[0].simulate(data)

    def __invert__(self):
        return self.conditions[0]


class And(BinaryLogicOp):
    tagName = 'And'
    
    def simulate(self, data):
        return all(cond.simulate(data) is True for cond in self.conditions.values())
        
    def __and__(self, other):
        if type(other) == And:
            for cond in other.conditions.values():
                self.__and__(cond)
        else:
            self.append_condition(other)
        return self

    def __rand__(self, other):
        self.prepend_condition(other)
        return self
        

class Or(BinaryLogicOp):
    tagName = 'Or'

    def simulate(self, data):
        return any(cond.simulate(data) is True for cond in self.conditions.values())

    def __or__(self, other):
        if type(other) == Or:
            for cond in other.conditions.values():
                self.__or__(cond)
        else:
            self.append_condition(other)
        return self

    def __ror__(self, other):
        self.prepend_condition(other)
        return self


