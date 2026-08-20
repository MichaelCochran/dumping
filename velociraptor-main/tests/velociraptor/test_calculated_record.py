from typing import Any
import unittest

from velociraptor.types.calculated_record import CalculatedRecord
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.record import Record

class RecordStub(Record):
    def __init__(self, values: dict[str, Any]):
        self.__values = values

    def get_value(self, field: Field):
        return self.__values[field.data_id]

class TestCaculated(unittest.TestCase):
    def setUp(self):
        field1a = Field(id='field1a', source_id='1', data_id='a', type=DataTypeEnum.NUMBER)
        field1b = Field(id='field1b', source_id='1', data_id='b', type=DataTypeEnum.NUMBER)
        field2a = Field(id='field2a', source_id='2', data_id='a', type=DataTypeEnum.NUMBER)
        field2b = Field(id='field2b', source_id='2', data_id='b', type=DataTypeEnum.NUMBER)
        record_1 = RecordStub({'a': 1, 'b': 2})
        record_2 = RecordStub({'a': 3, 'b': 4})
        self.field_by_id_dict = {'field1a': field1a, 'field1b': field1b, 'field2a': field2a, 'field2b': field2b}
        self.record_by_source_id_dict = {'1': record_1, '2': record_2}

    def test1(self):
        calculated_record = CalculatedRecord(self.field_by_id_dict, self.record_by_source_id_dict)
        field = Field(data_id="test", type=DataTypeEnum.NUMBER, calculation="value('field1a') + value('field2b')")
        assert(calculated_record.get_value(field) == 5)

    def test2(self):
        calculated_record = CalculatedRecord(self.field_by_id_dict, self.record_by_source_id_dict)
        field = Field(data_id="test", type=DataTypeEnum.NUMBER, calculation="value('field2a') - value('field1b')")
        assert(calculated_record.get_value(field) == 1)