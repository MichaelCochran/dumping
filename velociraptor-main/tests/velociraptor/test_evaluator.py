from datetime import date
import unittest

from velociraptor.types.evaluator import CalculationEvaluator, Evaluator, TransformEvaluator
from velociraptor.types.field import DataTypeEnum, Field

class TestEvaluator(unittest.TestCase):
    def setUp(self):
        test_list = [1,4,None]
        self.evaluator = Evaluator()
        self.evaluator.update_name("test_list", test_list)

        self.calculation_evaluator = CalculationEvaluator()
        self.calculation_evaluator.update_name("test_list", test_list)

        self.transform_evaluator = TransformEvaluator()
        self.transform_evaluator.update_name("test_list", test_list)

    def test_eval_min(self):
        assert(self.evaluator.eval("min(test_list)") == 1)

    def test_eval_max(self):
        assert(self.evaluator.eval("max(test_list)") == 4)

    def test_eval_sum(self):
        assert(self.evaluator.eval("sum(test_list)") == 5)

    def test_eval_count(self):
        assert(self.evaluator.eval("count(test_list)") == 2)

    def test_eval_avg(self):
        assert(self.evaluator.eval("avg(test_list)") == 2.5)

    def test_update_function(self):
        with self.assertRaises(Exception):
            self.evaluator.eval("myfunc()")
        self.evaluator.update_function("myfunc", lambda x: x + 1)
        assert(self.evaluator.eval("myfunc(1)") == 2)
        self.evaluator.update_function("myfunc", lambda x: x + 2)
        assert(self.evaluator.eval("myfunc(1)") == 3)

    def test_update_name(self):
        with self.assertRaises(Exception):
            self.evaluator.eval("myname")
        self.evaluator.update_name("myname", 5)
        assert(self.evaluator.eval("myname") == 5)
        self.evaluator.update_name("myname", 6)
        assert(self.evaluator.eval("myname") == 6)

    def test_parse(self):
        parsed = self.evaluator.parse("min(test_list)")
        assert(self.evaluator.eval(None, parsed) == 1)

    def test_eval_field_calculation(self):
        field = Field(data_id="data_id", type=DataTypeEnum.ANY, calculation="min(test_list)")
        assert(self.calculation_evaluator.eval_field_calculation(field) == 1)
        assert(self.calculation_evaluator.eval(None, field.parsed_calculation) == 1)

    def test_eval_field_calculation_value(self):
        self.calculation_evaluator.update_value_function(lambda x: 50 if x == 'a' else None)
        assert(self.calculation_evaluator.eval("value('a')") == 50)

    def test_eval_field_calculation_none_value(self):
        self.calculation_evaluator.update_value_function(lambda x: 50 if x == 'a' else None)
        assert(self.calculation_evaluator.eval("value('b')") == None)
        assert(self.calculation_evaluator.eval("value('a') + value('b')") == None)

    def test_eval_field_transform(self):
        self.transform_evaluator.update_self_value("something")
        field = Field(data_id="data_id", type=DataTypeEnum.ANY, transform="max(test_list)")
        assert(self.transform_evaluator.eval_field_transform(field) == 4)
        assert(self.transform_evaluator.eval(None, field.parsed_transform) == 4)

    def test_eval_field_transform_self(self):
        self.transform_evaluator.update_self_value("something")
        field = Field(data_id="data_id", type=DataTypeEnum.ANY, transform="self + ' else'")
        assert(self.transform_evaluator.eval_field_transform(field) == "something else")
        assert(self.transform_evaluator.eval(None, field.parsed_transform) == "something else")

    def test_eval_field_transform_none_self(self):
        field = Field(data_id="data_id", type=DataTypeEnum.ANY, transform="max(self)")
        assert(self.transform_evaluator.eval_field_transform(field) == None)
        assert(self.transform_evaluator.eval(None, field.parsed_transform) == None)

    def test_eval_date(self):
        self.transform_evaluator.update_self_value(1)
        field = Field(data_id="data_id", type=DataTypeEnum.NUMBER, transform="timedelta(days=self) + date(2024, 3, 1)")
        assert(self.transform_evaluator.eval_field_transform(field) == date(2024, 3, 2))

    def test_eval_timedelta(self):
        self.transform_evaluator.update_self_value(date(2024, 3, 1))
        field = Field(data_id="data_id", type=DataTypeEnum.DATE, transform="self + timedelta(days=1)")
        assert(self.transform_evaluator.eval_field_transform(field) == date(2024, 3, 2))
