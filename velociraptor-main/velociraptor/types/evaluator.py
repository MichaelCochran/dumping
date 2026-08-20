from ast import stmt
from collections.abc import Iterable
from datetime import date, timedelta
import statistics
from typing import Any, Callable, Optional
import simpleeval
from simpleeval import SimpleEval

from velociraptor.types.field import Field

EvalStatement = stmt

class NoneValueError(Exception):
    pass

class Evaluator:
    @staticmethod
    def __aggregate_list(value: Iterable, func: Callable[[Any], Any], empty_set_value=None):
        if not isinstance(value, Iterable):
            raise ValueError("Must be iterable")
        value = list(filter(lambda x: x is not None, value))
        if len(value) == 0:
            return empty_set_value
        else:
            return func(value)

    def __init__(self):
        functions = simpleeval.DEFAULT_FUNCTIONS.copy()
        functions.update(min=lambda x: self.__aggregate_list(x, min),
                         max=lambda x: self.__aggregate_list(x, max),
                         sum=lambda x: self.__aggregate_list(x, sum),
                         count=lambda x: self.__aggregate_list(x, len, 0),
                         avg=lambda x: self.__aggregate_list(x, statistics.mean),
                         date=date,
                         timedelta=timedelta)

        names = simpleeval.DEFAULT_NAMES.copy()
        #names.update(...)

        operators = simpleeval.DEFAULT_OPERATORS.copy()
        # operators.update(...)

        self._eval = SimpleEval(functions=functions, names=names, operators=operators)

    def update_function(self, func_name: str, func: Any):
        self._eval.functions.update([(func_name, func)])

    def update_name(self, name: str, value: Any):
        self._eval.names.update([(name, value)])

    def eval(self, expr: Any, previously_parsed: Optional[Any] = None) -> Any:
        return self._eval.eval(expr, previously_parsed)

    def parse(self, expr: Any):
        return self._eval.parse(expr)

class CalculationEvaluator(Evaluator):
    class ValueFunction:
        def __init__(self, func: Optional[Any]):
            self.func = func

        def get_value(self, *args):
            value = self.func(*args)
            if value is None:
                raise NoneValueError
            return value

    def __init__(self):
        super().__init__()
        self.__value_function = CalculationEvaluator.ValueFunction(None)
        self.update_function('value', self.__value_function.get_value)

    def update_value_function(self, value_function: Any):
        self.__value_function.func = value_function

    def eval(self, expr: Any, previously_parsed: Any | None = None) -> Any:
        try:
            value = super().eval(expr, previously_parsed)
        except NoneValueError:
            return None
        return value
    
    def eval_field_calculation(self, field: Field) -> Any:
        if field.parsed_calculation is None:
            field.parsed_calculation = self._eval.parse(field.calculation)
        return self.eval(field.calculation, field.parsed_calculation)

class TransformEvaluator(Evaluator):
    def __init__(self):
        super().__init__()

    def update_self_value(self, self_value: Any):
        self.update_name('self', self_value)

    def eval(self, expr: Any, previously_parsed: Any | None = None) -> Any:
        if self._eval.names.get('self') is None:
            return None
        return super().eval(expr, previously_parsed)

    def eval_field_transform(self, field: Field) -> Any:
        if field.parsed_transform is None:
            field.parsed_transform = self._eval.parse(field.transform)
        return self.eval(field.transform, field.parsed_transform)
