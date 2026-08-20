from abc import abstractmethod
from datetime import date
from enum import IntEnum
from typing import Any, Optional
from velociraptor.types.evaluator import TransformEvaluator
from velociraptor.types.field import DataTypeEnum, DisplayFormat, Field, ListDisplayFormat
import json
import re

class UpdateValueResult(IntEnum):
    SUCCESS = 0
    FAILURE = 1

# Define wrappers for each DataTypeEnum to customize initialization and string formatting

class Wrapper():
    def __init__(self, value, **kwargs):
        self._display_format: Optional[DisplayFormat] = kwargs.get("display_format", None)

    def __str__(self):
        if self._display_format is None:
            return super().__str__()
        else:
            return self._display_format.format(self)

class Date(Wrapper, date):
    def __new__(cls, value: date, **kwargs):
        return super().__new__(Date, value.year, value.month, value.day)

class String(Wrapper, str):
    def __new__(cls, value: str, **kwargs):
        return str.__new__(String, value)

class Number(Wrapper, float):
    def __new__(cls, value: float, **kwargs):
        return float.__new__(Number, value)

class IMSHours(Wrapper, float):
    def __new__(cls, value: str, **kwargs):
        # Add '?' after ',' to make comma optional and | after 'hours?' to make hrs/hours optional
        if not (result:=re.search(r'^(\d{1,3})((?:,\d{3})*)(\.\d+)?( hrs?| hours?)$', value)):
            raise ValueError(f"Value does not match IMSHours pattern: '{value}'")
        value = ''.join(filter(None, result.groups()[:3])).replace(',', '')
        return float.__new__(IMSHours, value)

class IMSChargeNumber(Wrapper, str):
    def __new__(cls, value: str, **kwargs):
        if len(result:=value.split('+')) < 2:
            raise ValueError(f"Value does not match IMSChargeNumber pattern: '{value}'")
        value = result[-1]
        return str.__new__(IMSChargeNumber, value)

class JiraKey(Wrapper, tuple[str, int]):
    def __new__(cls, value: str, **kwargs):
        try:
            k, n = value.split("-", 1)
            n = int(n)
        except:
            k = value
            n = None
        return tuple[str, int].__new__(JiraKey, (k, n))

    def __init__(self, value: str, **kwargs):
        super().__init__(value, **kwargs)
        self.__string_value = value

    def __str__(self):
        if self._display_format is None:
            return self.__string_value
        else:
            return super().__str__()

class Percent(Wrapper, float):
    def __new__(cls, value: float, **kwargs):
        return float.__new__(Percent, value)

class Formula(Wrapper, str):
    def __new__(cls, value: str, **kwargs):
        return str.__new__(Formula, value)

class Boolean(Wrapper):
    def __new__(cls, value: bool, **kwargs):
        if value is not True and value is not False:
            raise ValueError("Boolean must be True or False")
        return value

class Json(Wrapper):
    def __new__(cls, value: str, **kwargs):
        return json.loads(value)

class List(Wrapper, list):
    def __new__(cls, value: list, **kwargs):
        return list.__new__(List)

    def __init__(self, value: list, **kwargs):
        super().__init__(value, **kwargs)
        self._list_display_format: Optional[ListDisplayFormat] = kwargs.get("list_display_format", None)
        self.extend(value)

    def __str__(self):
        if self._list_display_format is None:
            return super().__str__()
        else:
            return self._list_display_format.format(self)

class Record:
    # Get value as python type
    # Return value types based on type:
    # DATE ==> date
    # STRING ==> str
    # NUMBER ==> float
    # IMS_HOURS ==> float
    # IMS_CHARGE_NUMBER ==> str
    # JIRA_KEY ==> str
    # PERCENT ==> float
    # FORMULA ==> string
    # BOOLEAN ==> bool
    # JSON ==> Any
    # ANY ==> Any
    @abstractmethod
    def get_value(self, field: Field):
        raise NotImplementedError

    _evaluator = TransformEvaluator()

    @staticmethod
    def __convert_value(type: DataTypeEnum, value: Any, **kwargs):
        match type:
            case DataTypeEnum.DATE:
                return Date(value, **kwargs)
            case DataTypeEnum.STRING:
                return String(value, **kwargs)
            case DataTypeEnum.NUMBER:
                return Number(value, **kwargs)
            case DataTypeEnum.IMS_HOURS:
                return IMSHours(value, **kwargs)
            case DataTypeEnum.IMS_CHARGE_NUMBER:
                return IMSChargeNumber(value, **kwargs)
            case DataTypeEnum.JIRA_KEY:
                return JiraKey(value, **kwargs)
            case DataTypeEnum.PERCENT:
                return Percent(value, **kwargs)
            case DataTypeEnum.FORMULA:
                return Formula(value, **kwargs)
            case DataTypeEnum.BOOLEAN:
                return Boolean(value, **kwargs)
            case DataTypeEnum.JSON:
                return Json(value, **kwargs)
            case DataTypeEnum.ANY:
                return value
            case _:
                raise TypeError("Unsupported type")

    @staticmethod
    def _wrap_value(field: Field, value: Any):
        try:
            if value is not None and field.transform is not None:
                Record._evaluator.update_self_value(value)
                value = Record._evaluator.eval_field_transform(field)

            value_type = field.output_type or field.type
            kwargs = {
                'display_format': field.metadata.display_format,
                'list_display_format': field.metadata.list_display_format
            }
            if isinstance(value, list):
                value = List([Record.__convert_value(value_type, x, **kwargs) for x in value], **kwargs)
            else:
                value = Record.__convert_value(value_type, value, **kwargs)

            return value

        except Exception as e:
            raise ValueError(f"Error wrapping field:\nvalue: {value}\nfield: {field}") from e

    @abstractmethod
    def update_value(self, field: Field, value: any) -> UpdateValueResult:
        raise NotImplementedError

    # No guaranteed interface: for DataInterface use
    @abstractmethod
    def get_values(self):
        raise NotImplementedError

    # No guaranteed interface: for DataInterface use
    @abstractmethod
    def get_updated_values(self):
        raise NotImplementedError

# TODO Specialize to specific interfaces and combine logic with "update_value()" as necessary
NewRecord = list[tuple[Field, Any]]
