from abc import abstractmethod
from enum import Enum
import json
from typing import Any, Optional

'''
----------------------------------------------------------------------------
Library   : velociraptor
Package   : velociraptor.interfaces
Class     : FieldMappingConfig.py
Engineers : Steve Schifris
Abstract  : This class encapsulates the field names and underlying configuration.
            Some references to Jira and Sheet have been maintained for simplicity.
----------------------------------------------------------------------------
'''
from dataclasses import dataclass, field

class DataTypeEnum(Enum):
    # Enum for the data types supported by velociraptor for field comparison.
    DATE = 1
    STRING = 2
    NUMBER = 3
    IMS_HOURS = 4
    IMS_CHARGE_NUMBER = 5
    JIRA_KEY = 6
    PERCENT = 7
    FORMULA = 8
    BOOLEAN = 9
    JSON = 10
    ANY = 99

class DisplayFormat():
    @abstractmethod
    def format(value: Any) -> str:
        pass

class SimpleDisplayFormat(DisplayFormat):
    def __init__(self, format_str: str):
        self.__format_str = format_str

    def format(self, value):
        return self.__format_str.format(value)

    def __eq__(self, other: 'SimpleDisplayFormat'):
        if isinstance(other, SimpleDisplayFormat):
            return self.__format_str == other.__format_str
        else:
            return NotImplemented

class JsonDisplayFormat(DisplayFormat):
    def format(self, value):
        return json.dumps(value)

    def __eq__(self, other: 'JsonDisplayFormat'):
        if isinstance(other, JsonDisplayFormat):
            return True
        else:
            return NotImplemented

@dataclass(kw_only=True)
class ListDisplayFormat(DisplayFormat):
    list_prefix: Optional[str] = ""
    list_suffix: Optional[str] = ""
    item_prefix: Optional[str] = ""
    item_delimiter: Optional[str] = ""
    item_suffix: Optional[str] = ""

    def format(self, value: Any) -> str:
        # Check if iterable
        return \
            self.list_prefix + \
            self.item_delimiter.join([f"{self.item_prefix}{x}{self.item_suffix}" for x in value]) + \
            self.list_suffix

    def __eq__(self, other: 'ListDisplayFormat'):
        if isinstance(other, ListDisplayFormat):
            return \
                self.list_prefix == other.list_prefix and \
                self.list_suffix == other.list_suffix and \
                self.item_prefix == other.item_prefix and \
                self.item_delimiter == other.item_delimiter and \
                self.item_suffix == other.item_suffix
        else:
            return NotImplemented

@dataclass(kw_only=True)
class Metadata:
    value: Optional[Any] = None
    display_format: Optional[DisplayFormat] = None
    excel_display_format: Optional[str] = None
    list_display_format: Optional[ListDisplayFormat] = None

@dataclass(kw_only=True)
class Field:
    id: str = "No Id"
    name: str = "No Name"
    source_id: str = "No Source"
    data_id: str
    type: DataTypeEnum
    output_type: Optional[DataTypeEnum] = None
    metadata: Metadata = field(default_factory=Metadata)
    calculation: Optional[str] = None
    parsed_calculation: Any = None
    transform: Optional[str] = None
    parsed_transform: Any = None
    updatable: bool = False
    overwritable: bool = False
    insertable: bool = False
