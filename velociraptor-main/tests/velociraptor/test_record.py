from datetime import date
import unittest
from velociraptor.types.field import DataTypeEnum, Field, SimpleDisplayFormat
from velociraptor.types.record import Boolean, Date, IMSChargeNumber, IMSHours, JiraKey, Percent, List, Json, Record

class TestDataType(unittest.TestCase):

    def test_jirakey(self):
        key1 = JiraKey("KEY-11")
        key2 = JiraKey("KEY-2")
        keybad = JiraKey("KEY2")

        assert(str(key1) == "KEY-11")
        assert(str(key2) == "KEY-2")

        assert (key1 > key2)
        assert (keybad > key2)

    def test_ims_hours(self):
        with self.assertRaises(ValueError):
            IMSHours("1")

        assert(IMSHours("1 hr") == 1)

        assert(IMSHours("1 hrs") == 1)

        assert(IMSHours("1 hour") == 1)

        assert(IMSHours("1 hours") == 1)

        assert(IMSHours("10 hours") == 10)

        assert(IMSHours("100 hours") == 100)

        assert(IMSHours("1,000 hours") == 1000)

        assert(IMSHours("10,000 hours") == 10000)

        assert(IMSHours("100,000 hours") == 100000)

        assert(IMSHours("1,000,000 hours") == 1000000)

        with self.assertRaises(ValueError):
            IMSHours("1,0 hours")

        with self.assertRaises(ValueError):
            IMSHours("10, hours")

        with self.assertRaises(ValueError):
            IMSHours("10,0 hours")

        with self.assertRaises(ValueError):
            IMSHours("1000 hours")

        with self.assertRaises(ValueError):
            IMSHours("10000 hours")

        with self.assertRaises(ValueError):
            IMSHours("100000 hours")

        with self.assertRaises(ValueError):
            IMSHours("1,000000 hours")

        with self.assertRaises(ValueError):
            IMSHours("1000000 hours")

        with self.assertRaises(ValueError):
            IMSHours("1000000hours")

        with self.assertRaises(ValueError):
            IMSHours("1000000 hours ")

        with self.assertRaises(ValueError):
            IMSHours("1000000 hoursa")

    def test_ims_charge_number(self):
        assert(IMSChargeNumber("LMB-1312-G1A+700LMBGNDC2L") == "700LMBGNDC2L") # Only observed pattern on one program

    def test_date(self):
        test_date = date(2023, 12, 31)
        assert(Date(test_date) == test_date)
        assert(str(Date(test_date, display_format=SimpleDisplayFormat("{0:%Y-%m-%d}"))) == "2023-12-31")
        test_date2 = date(2024, 1, 1)
        assert(Date(test_date) < Date(test_date2))

    def test_boolean(self):
        assert(Boolean(True) == True)
        assert(Boolean(False) == False)
        with self.assertRaises(ValueError):
            Boolean(5)
        assert(Boolean(True))
        assert(not Boolean(False))

    def test_list(self):
        assert(List([1,2,3]) == [1,2,3])

    def test_percent(self):
        assert(Percent(5.67) == 5.67)

    def test_json(self):
        assert(Json('{"dict1": {"key1":3,"key2":"a"}}') == {"dict1":{"key1":3,"key2":"a"}})
        assert(Json('[{"dict1": {"key1":3,"key2":"a"}}]') == [{"dict1":{"key1":3,"key2":"a"}}])

    def test_wrap_value_string_list_one_element(self):
        test_string_list = ["b"]
        test_string = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.STRING, transform="min(self)"), test_string_list)
        assert(test_string == "b")

    def test_wrap_value_string_value(self):
        test_string_value = "b"
        test_string = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.STRING, transform="min(self)"), test_string_value)
        assert(test_string == "b")

    def test_wrap_value_string_list_min_none(self):
        test_string_list = ["a", "b", "c", None]
        test_string = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.STRING, transform="min(self)"), test_string_list)
        assert(test_string == "a")

    def test_wrap_value_string_list_count_none(self):
        test_string_list = ["a", "b", "c", None]
        test_string = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.NUMBER, transform="count(self)"), test_string_list)
        assert(test_string == 3)

    def test_wrap_value_string_list_count_empty(self):
        test_string_list = []
        test_string = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.NUMBER, transform="count(self)"), test_string_list)
        assert(test_string == 0)

    def test_wrap_value_string_list_count_empty_none(self):
        test_string_list = [None]
        test_string = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.NUMBER, transform="count(self)"), test_string_list)
        assert(test_string == 0)

    def test_wrap_value_string_list_min(self):
        test_string_list = ["a", "b", "c"]
        test_string = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.STRING, transform="min(self)"), test_string_list)
        assert(test_string == "a")

    def test_wrap_value_string_list_max(self):
        test_string_list = ["a", "b", "c"]
        test_string = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.STRING, transform="max(self)"), test_string_list)
        assert(test_string == "c")

    def test_wrap_value_date_list_count(self):
        test_date_list = [date(2023, 12, 29), date(2023, 12, 30), date(2023, 12, 31)]
        length = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.NUMBER, transform="count(self)"), test_date_list)
        assert(length == 3)

    def test_wrap_value_date_list_min(self):
        test_date_list = [date(2023, 12, 29), date(2023, 12, 30), date(2023, 12, 31)]
        test_date = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.DATE, transform="min(self)"), test_date_list)
        assert(test_date == date(2023, 12, 29))

    def test_wrap_value_date_list_max(self):
        test_date_list = [date(2023, 12, 29), date(2023, 12, 30), date(2023, 12, 31)]
        test_date = Record._wrap_value(Field(data_id="data_id", type=DataTypeEnum.DATE, transform="max(self)"), test_date_list)
        assert(test_date == date(2023, 12, 31))