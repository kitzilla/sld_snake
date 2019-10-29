
from ..utils import parseDouble

from .base import Expression
from .mixins import TwoExpressionMixin


class BinaryOperator(Expression, TwoExpressionMixin):
    # expr0 - from TwoExpressionMixin
    # expr1 - from TwoExpressionMixin

    def __init__(self, expr0, expr1):
        super().__init__()
        self.expr0 = expr0
        self.expr1 = expr1

    def simulate(self, *args, **kwargs):
        val0 = parseDouble(self.expr0.simulate(*args, **kwargs))
        val1 = parseDouble(self.expr1.simulate(*args, **kwargs))
        return val0, val1


class Add(BinaryOperator):
    def simulate(self, *args, **kwargs):
        val0, val1 = super().simulate(*args, **kwargs)
        return val0 + val1


class Sub(BinaryOperator):
    def simulate(self, *args, **kwargs):
        val0, val1 = super().simulate(*args, **kwargs)
        return val0 - val1


class Mul(BinaryOperator):
    def simulate(self, *args, **kwargs):
        val0, val1 = super().simulate(*args, **kwargs)
        return val0 * val1


class Div(BinaryOperator):
    def simulate(self, *args, **kwargs):
        val0, val1 = super().simulate(*args, **kwargs)

        try:
            return val0 / val1
        except ZeroDivisionError:
            return float('inf')
