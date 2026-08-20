import os
import unittest
from enum import Enum, IntEnum
from typing import Optional

from dataclasses import asdict, dataclass
from velociraptor.types.dictionary_convertible import DictionaryConvertible

class MyEnum(Enum):
    A = 1
    B = 2
    C = 3

class MyIntEnum(IntEnum):
    ONE = 1,
    TWO = 2,
    THREE = 3

@dataclass(kw_only=True)
class DictionaryConvertibleTestClass(DictionaryConvertible):
    my_string: Optional[str] = "Test"
    my_bool: Optional[bool] = False
    my_int: Optional[int] = 9
    my_enum: Optional[MyEnum] = MyEnum.A
    my_intenum: Optional[MyIntEnum] = MyIntEnum.ONE

    def to_dict(self):
        dict = asdict(self)
        del dict["_tree_nodes"]
        return dict

    def __eq__(self, other: 'DictionaryConvertibleTestClass'):
        return (self.my_string == other.my_string and
                self.my_bool == other.my_bool and
                self.my_int == other.my_int and
                self.my_enum == other.my_enum and
                self.my_intenum == other.my_intenum)

class TestDictionaryConvertible(unittest.TestCase):
    def setup_method(self, method):
        self.test_obj = DictionaryConvertibleTestClass()
        self.test_obj_env = DictionaryConvertibleTestClass(my_string = "{$my_string}", my_bool="{$my_bool}", my_int="{$my_int}", my_enum="{$my_enum}", my_intenum="{$my_intenum}")
        os.environ["my_string"] = self.test_obj.my_string
        os.environ["my_bool"] = str(self.test_obj.my_bool)
        os.environ["my_int"] = str(self.test_obj.my_int)
        os.environ["my_enum"] = self.test_obj.my_enum.name
        os.environ["my_intenum"] = self.test_obj.my_intenum.name

    def test_convert(self):
        test_dict = self.test_obj.to_dict()
        actual = DictionaryConvertibleTestClass.convert(**test_dict)
        assert(actual == self.test_obj)

    def test_convert_env(self):
        test_dict = self.test_obj_env.to_dict()
        actual = DictionaryConvertibleTestClass.convert(**test_dict)
        assert(actual == self.test_obj)

    def test_string_bool(self):
        test_dict = self.test_obj.to_dict()
        test_dict["my_bool"] = str(self.test_obj.my_bool)
        actual = DictionaryConvertibleTestClass.convert(**test_dict)
        assert(actual == self.test_obj)

    def test_string_bool_env(self):
        test_dict_env = self.test_obj_env.to_dict()
        os.environ["my_bool"] = str(self.test_obj.my_bool)
        actual = DictionaryConvertibleTestClass.convert(**test_dict_env)
        assert(actual == self.test_obj)

    def test_bad_string_bool(self):
        test_dict = self.test_obj.to_dict()
        test_dict["my_bool"] = "fleas"
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict)

    def test_bad_string_bool_env(self):
        test_dict_env = self.test_obj_env.to_dict()
        os.environ["my_bool"] = "fleas"
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict_env)

    def test_int_bool(self):
        test_dict = self.test_obj.to_dict()
        test_dict["my_bool"] = 0
        actual = DictionaryConvertibleTestClass.convert(**test_dict)
        assert(actual == self.test_obj)

        test_dict["my_bool"] = 1
        self.test_obj.my_bool = True
        actual = DictionaryConvertibleTestClass.convert(**test_dict)
        assert(actual == self.test_obj)

    def test_string_int(self):
        test_dict = self.test_obj.to_dict()
        test_dict["my_int"] = str(self.test_obj.my_int)
        actual = DictionaryConvertibleTestClass.convert(**test_dict)
        assert(actual == self.test_obj)

    def test_string_int_env(self):
        test_dict_env = self.test_obj_env.to_dict()
        os.environ["my_int"] = str(self.test_obj.my_int)
        actual = DictionaryConvertibleTestClass.convert(**test_dict_env)
        assert(actual == self.test_obj)

    def test_bad_string_int(self):
        test_dict = self.test_obj.to_dict()
        test_dict["my_int"] = "9b"
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict)

    def test_bad_string_int_env(self):
        test_dict_env = self.test_obj_env.to_dict()
        os.environ["my_int"] = "9b"
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict_env)

    def test_string_enum(self):
        test_dict = self.test_obj.to_dict()
        test_dict["my_enum"] = self.test_obj.my_enum.name
        actual = DictionaryConvertibleTestClass.convert(**test_dict)
        assert(actual == self.test_obj)

    def test_string_enum_env(self):
        test_dict_env = self.test_obj_env.to_dict()
        os.environ["my_enum"] = self.test_obj.my_enum.name
        actual = DictionaryConvertibleTestClass.convert(**test_dict_env)
        assert(actual == self.test_obj)

    def test_bad_string_enum(self):
        test_dict = self.test_obj.to_dict()
        test_dict["my_enum"] = "D"
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict)

    def test_bad_string_enum_env(self):
        test_dict_env = self.test_obj_env.to_dict()
        os.environ["my_enum"] = "D"
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict_env)

    def test_string_int_enum(self):
        test_dict = self.test_obj.to_dict()
        test_dict["my_intenum"] = "ONE"
        actual = DictionaryConvertibleTestClass.convert(**test_dict)
        assert(actual == self.test_obj)

        test_dict["my_intenum"] = 1
        actual = DictionaryConvertibleTestClass.convert(**test_dict)
        assert(actual == self.test_obj)

    def test_string_int_enum_env(self):
        test_dict_env = self.test_obj_env.to_dict()
        os.environ["my_intenum"] = "ONE"
        actual = DictionaryConvertibleTestClass.convert(**test_dict_env)
        assert(actual == self.test_obj)

        # It is assumed for Enums (IntEnum or otherwise) that a string value
        # should be interpreted as the enum name and not the enum value
        os.environ["my_intenum"] = "1"
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict_env)

    def test_bad_string_int_enum(self):
        test_dict = self.test_obj.to_dict()

        test_dict["my_enum"] = "FOUR"
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict)

        test_dict["my_enum"] = 4
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict)

    def test_bad_string_int_enum_enum(self):
        test_dict_env = self.test_obj_env.to_dict()

        test_dict_env["my_enum"] = "FOUR"
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict_env)

        test_dict_env["my_enum"] = "4"
        with self.assertRaises(Exception):
            DictionaryConvertibleTestClass.convert(**test_dict_env)
