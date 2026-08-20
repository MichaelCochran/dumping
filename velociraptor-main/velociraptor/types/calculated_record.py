from velociraptor.types.evaluator import CalculationEvaluator
from velociraptor.types.field import Field
from velociraptor.types.record import Record

class CalculatedRecord(Record):
    def __init__(self, field_by_id_dict: dict[str, Field], record_by_source_id_dict: dict[str, Record]):
        self.__field_by_id_dict = field_by_id_dict
        self.__record_by_id_dict = record_by_source_id_dict
        self.__evaluator = CalculationEvaluator()
        self.__evaluator.update_value_function(self.__get_field_value)

    def __get_field_value(self, id: str):
        field = self.__field_by_id_dict[id]
        return  self.__record_by_id_dict[field.source_id].get_value(field)

    def get_value(self, field: Field):
        if field.calculation is not None:
            value = self.__evaluator.eval_field_calculation(field)

        if value is not None:
            value = self._wrap_value(field, value)

        return value