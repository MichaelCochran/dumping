'''
----------------------------------------------------------------------------
Library   : velociraptor
Package   : velociraptor.interfaces
Class     : ConfigManager.py
Engineers : Christian Westbrook, Steve Schifris
Abstract  : This class provides a programmatic interface to a configuration file.
----------------------------------------------------------------------------
'''

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
from typing import Any, ClassVar, Optional
from velociraptor.types.data_interface_config import JiraInterfaceConfig, JiraInterfaceSimConfig, SheetInterfaceConfig
from velociraptor.types.dictionary_convertible import DictionaryConvertible
from velociraptor.types.util import resolve_path

from velociraptor.types.field import DataTypeEnum, SimpleDisplayFormat, Field, JsonDisplayFormat, ListDisplayFormat, Metadata
from velociraptor.types.keyed_record_comparator import FieldComparisonPair, SorEnum
from velociraptor.types.keyed_record_comparison_updater import FieldUpdateResult

class DataInterfaceTypeEnum(Enum):
    JIRA = 0
    JIRA_SIM = 1
    SHEET = 2

@dataclass(kw_only=True)
class DataInterfaceConfig(DictionaryConvertible):
    id: str
    type: DataInterfaceTypeEnum
    config: Optional[Any] = None

    def _post_conversion(self, root_obj: 'Configuration'):
        # Deserialize complex objects
        if self.config is not None:
            if self.type == DataInterfaceTypeEnum.JIRA:
                self.config = JiraInterfaceConfig.convert(root_obj, **self.config)
                if not isinstance(self.config, JiraInterfaceConfig):
                    raise TypeError("Expected JiraInterfaceConfig")
                self.config.output_directory_path = resolve_path(root_obj.base_path, self.config.output_directory_path, root_obj.output_directory_path)
            elif self.type == DataInterfaceTypeEnum.JIRA_SIM:
                self.config : JiraInterfaceSimConfig = JiraInterfaceSimConfig.convert(root_obj, **self.config)
                if not isinstance(self.config, JiraInterfaceSimConfig):
                    raise TypeError("Expected JiraInterfaceConfig")
                self.config.data_directory_path = resolve_path(root_obj.base_path, self.config.data_directory_path, root_obj.data_directory_path)
                self.config.output_directory_path = resolve_path(root_obj.base_path, self.config.output_directory_path, root_obj.output_directory_path)
            elif self.type == DataInterfaceTypeEnum.SHEET:
                self.config : SheetInterfaceConfig = SheetInterfaceConfig.convert(root_obj, **self.config)
                if not isinstance(self.config, SheetInterfaceConfig):
                    raise TypeError("Expected JiraInterfaceConfig")
                self.config.data_directory_path = resolve_path(root_obj.base_path, self.config.data_directory_path, root_obj.data_directory_path)
            else:
                raise ValueError(f"Unsupported DataInterfaceConfig type: '{self.type.name}'")

            if self.id in root_obj.source_config_by_id_dict:
                raise ValueError(f"'id' ('{self.id}') must be unique among all data interfaces")
            else:
                root_obj.interface_config_by_id_dict[self.id] = self

@dataclass(kw_only=True)
class SourceConfig(DictionaryConvertible):
    id: str
    name: Optional[str] = None
    data_interface_id: Optional[str] = None

    def _pre_conversion(self, root_obj: 'Configuration'):
        # Default name to id
        if self.name is None:
            self.name = self.id

    def _post_conversion(self, root_obj: 'Configuration'):
        if self.id in root_obj.source_config_by_id_dict:
            raise ValueError(f"'id' ('{self.id}') must be unique among all sources")
        else:
            root_obj.source_config_by_id_dict[self.id] = self

        # Check that the referenced data_interface_id matches a known data interface
        if self.data_interface_id not in root_obj.interface_config_by_id_dict:
            raise ValueError(f"'data_interface_id' ('{self.data_interface_id}') does not match any known data interface")

@dataclass(kw_only=True)
class CompareSourceConfig(SourceConfig):
    pk_field_id: Optional[str] = None
    fk_field_id: Optional[str] = None

@dataclass(kw_only=True)
class ComparisonConfig(DictionaryConvertible):
    sort_field_id: str
    reverse: bool

@dataclass(kw_only=True)
class Displayable(DictionaryConvertible):
    display: Optional[bool] = False
    display_index: Optional[int] = None

@dataclass(kw_only=True)
class ListDisplayFormatConfig(ListDisplayFormat, DictionaryConvertible):
    pass

class SimpleDisplayFormatConfig(SimpleDisplayFormat):
    def __init__(self, format_str: str):
        super().__init__(format_str)

class DisplayFormatConfig():
    @staticmethod
    def create_display_format_config(type: DataTypeEnum, kwargs: Any):
        if kwargs is None:
            return None
        return SimpleDisplayFormatConfig(kwargs)

@dataclass(kw_only=True)
class MetadataConfig(Metadata, DictionaryConvertible):
    # Change type to Any so that DictionaryConvertible does not automatically convert it
    # TODO Make DisplayFormatConfig self-converting?
    display_format: Optional[Any] = None
    list_display_format: Optional[ListDisplayFormatConfig] = None

@dataclass(kw_only=True)
class FieldConfig(Displayable):
    id: Optional[str] = None
    name: Optional[str] = None
    source_id: str
    data_id: str
    type: DataTypeEnum
    output_type: Optional[DataTypeEnum] = None
    metadata: Optional[MetadataConfig] = field(default_factory=dict)
    calculation: Optional[str] = None
    transform: Optional[str] = None
    updatable: Optional[bool] = None
    overwritable: Optional[bool] = None
    insertable: Optional[bool] = None

    def _pre_conversion(self, root_obj: 'Configuration'):
        # Default id to a concatenation of source_id and data_id
        if self.id is None:
            self.id = f"{self.source_id}:{self.data_id}"
        # Default name to id
        if self.name is None:
            self.name = self.id
        # Default updatable to field_update_default
        if self.updatable is None:
            self.updatable = root_obj.field_update_default
        # Default overwritable to field_overwrite_default
        if self.overwritable is None:
            self.overwritable = root_obj.field_overwrite_default
        # Default insertable to field_insert_default
        if self.insertable is None:
            self.insertable = root_obj.field_insert_default

    def _post_conversion(self, root_obj: 'Configuration'):
        if self.type == DataTypeEnum.FORMULA and self.metadata.value is None:
            raise ValueError(f"Fields of type '{DataTypeEnum.FORMULA.name}' must define metadata 'value'")

        display_type = self.output_type or self.type
        self.metadata.display_format = DisplayFormatConfig.create_display_format_config(display_type, self.metadata.display_format)

        # Map FieldConfig to Field
        field = Field(id=self.id, name=self.name, source_id=self.source_id,
                      data_id=self.data_id, type=self.type, output_type=self.output_type, metadata=self.metadata,
                      calculation=self.calculation, transform=self.transform,
                      updatable=self.updatable, overwritable=self.overwritable, insertable=self.insertable)

        # Check that the referenced source_id matches a known source
        if field.source_id not in root_obj.source_config_by_id_dict:
            raise ValueError(f"'source_id' ('{field.source_id}') does not match any known source")

        # Check for uniqueness of 'id'
        if field.id in root_obj.field_by_id_dict:
            raise ValueError(f"'id' ('{field.id}') must be unique among all fields")
        root_obj.field_by_id_dict[field.id] = field
        root_obj.field_by_id_dict_by_source_id_dict.setdefault(field.source_id, {})[field.id] = field

    def _post_root_conversion(self, root_obj: 'Configuration'):
        display_type = self.output_type or self.type

        if self.metadata.display_format is None:
            self.metadata.display_format = root_obj.display_format_defaults.get(display_type)

        # Default metadata excel_display_format to type-dependent value from excel_display_format_defaults
        if self.metadata.excel_display_format is None:
            self.metadata.excel_display_format = root_obj.excel_display_format_defaults.get(display_type)

        if self.metadata.list_display_format is None:
            self.metadata.list_display_format = root_obj.list_display_format_default

@dataclass(kw_only=True)
class FieldPairConfig(Displayable):
    id: Optional[str] = None
    left_field_id: str
    right_field_id: str
    sor: SorEnum #TODO SOR should be optional for future comparison (non-update) use cases
    display: Optional[bool] = True

    def _post_conversion(self, root_obj: 'Configuration'):
        if root_obj.left_source.id not in root_obj.field_by_id_dict_by_source_id_dict:
            raise ValueError(f"There are no fields defined for 'left_source' ('{root_obj.left_source.id}')")
        if self.left_field_id not in root_obj.field_by_id_dict_by_source_id_dict[root_obj.left_source.id]:
            raise ValueError(f"Field 'id' ('{self.left_field_id}') does not match any known field for source_id ('{root_obj.left_source.id}')")
        left_field = root_obj.field_by_id_dict_by_source_id_dict[root_obj.left_source.id][self.left_field_id]

        if root_obj.right_source.id not in root_obj.field_by_id_dict_by_source_id_dict:
            raise ValueError(f"There are no fields defined for 'right_source' ('{root_obj.right_source.id}')")
        if self.right_field_id not in root_obj.field_by_id_dict_by_source_id_dict[root_obj.right_source.id]:
            raise ValueError(f"Field 'id' ('{self.right_field_id}') does not match any known field for source_id ('{root_obj.right_source.id}')")
        right_field = root_obj.field_by_id_dict_by_source_id_dict[root_obj.right_source.id][self.right_field_id]

        if self.id is None:
            self.id = f"{left_field.id}-{right_field.id}"

        # Map FieldPairConfig to FieldComparisonPair
        field_pair = FieldComparisonPair(self.id,
                                         left_field,
                                         right_field,
                                         self.sor)
        if field_pair.id in root_obj.field_pair_by_id_dict:
            raise ValueError(f"'id' ('{field_pair.id}') must be unique among all field pairs")
        else:
            root_obj.field_pair_by_id_dict[field_pair.id] = field_pair

@dataclass
class DefaultPathConfiguration:
    default_base_directory_path: Path
    default_data_directory: str
    default_output_directory: str

class DisplayFormatDefaultConfig(dict[DataTypeEnum, Any], DictionaryConvertible):
    def _post_conversion(self, root_obj: DictionaryConvertible):
        display_format_dict = {}
        for k, v in self.items():
            k = DataTypeEnum[k]
            display_format_dict[k] = DisplayFormatConfig.create_display_format_config(k, v)

        self.clear()
        self.update(display_format_dict)

@dataclass(kw_only=True)
class Configuration(DictionaryConvertible):
    schema_version: float
    data_directory_path: Optional[str] = None
    output_directory_path: Optional[str] = None
    output_file_name: str
    field_update_default: Optional[bool] = False
    field_overwrite_default: Optional[bool] = False
    field_insert_default: Optional[bool] = False
    display_format_defaults: Optional[DisplayFormatDefaultConfig] = field(default_factory=DisplayFormatDefaultConfig)
    excel_display_format_defaults: Optional[dict[DataTypeEnum, str]] = field(default_factory=dict)
    list_display_format_default: Optional[ListDisplayFormatConfig] = None
    data_interfaces: list[DataInterfaceConfig]
    left_source: CompareSourceConfig
    right_source: CompareSourceConfig
    fields: list[FieldConfig]
    field_pairs: list[FieldPairConfig]
    comparison: ComparisonConfig

    _CALCULATED_SOURCE_ID: ClassVar[str] = "__calculated"
    _CALCULATED_SOURCE_NAME: ClassVar[str] = "Calculated"
    base_path: Path = field(init=False)

    interface_config_by_id_dict: dict[str, DataInterfaceConfig] = field(init=False, default_factory=dict)

    calculated_source: SourceConfig = field(init=False)
    source_config_by_id_dict: dict[str, SourceConfig] = field(init=False, default_factory=dict)

    field_by_id_dict: dict[str, Field] = field(init=False, default_factory=dict)
    field_by_id_dict_by_source_id_dict: dict[str, dict[str, Field]] = field(init=False, default_factory=dict)

    field_pair_by_id_dict: dict[str, FieldComparisonPair] = field(init=False, default_factory=dict)

    display_field_list: list[Field | FieldComparisonPair] = field(init=False, default_factory=list)

    def _pre_root_conversion(self, ref_obj: DefaultPathConfiguration):
        if self.schema_version != 5:
            raise ValueError(f"Unsupported schema version: {self.schema_version}")

        self.base_path = ref_obj.default_base_directory_path
        self.data_directory_path = resolve_path(self.base_path, self.data_directory_path, ref_obj.default_data_directory)
        self.output_directory_path = resolve_path(self.base_path, self.output_directory_path, ref_obj.default_output_directory)

    def _pre_conversion(self, root_obj: 'Configuration'):
        self.calculated_source = SourceConfig(id=self._CALCULATED_SOURCE_ID, name=self._CALCULATED_SOURCE_NAME)
        self.source_config_by_id_dict[self.calculated_source.id] = self.calculated_source

    def _post_conversion(self, root_obj: 'Configuration'):
        displayable_with_index_list = list[Displayable]()
        for displayable in self.fields + self.field_pairs:
            if displayable.display is True:
                if displayable.display_index is None:
                    if isinstance(displayable, FieldConfig):
                        self.display_field_list.append(self.field_by_id_dict[displayable.id])
                    elif isinstance(displayable, FieldPairConfig):
                        self.display_field_list.append(self.field_pair_by_id_dict[displayable.id])
                    else:
                        raise ValueError(f"Unsupported displayable type: {type(displayable)})")
                else:
                    displayable_with_index_list.append(displayable)

        # Sort display fields by index and insert at the appropriate index of the main list
        # Disallow duplicate indices for insertion simplicity; duplicates have a cumulative effect
        displayable_with_index_list.sort(key=lambda x: x.display_index)
        displayable_previous_index = -1
        for displayable in displayable_with_index_list:
            display_index = displayable.display_index
            if display_index < 0:
                raise ValueError(f"'display_index' ({display_index}) cannot be negative")
            elif display_index == displayable_previous_index:
                raise ValueError(f"'display_index' ({display_index}) must be unique")
            else:
                if isinstance(displayable, FieldConfig):
                    self.display_field_list.insert(display_index, self.field_by_id_dict[displayable.id])
                elif isinstance(displayable, FieldPairConfig):
                    self.display_field_list.insert(display_index, self.field_pair_by_id_dict[displayable.id])
                else:
                    raise ValueError(f"Unsupported displayable type: {type(displayable)}")
                displayable_previous_index = display_index

    def _post_root_conversion(self, root_obj: 'Configuration'):
        self.display_format_defaults.setdefault(DataTypeEnum.PERCENT, SimpleDisplayFormat("{0:.0%}"))
        self.display_format_defaults.setdefault(DataTypeEnum.JSON, JsonDisplayFormat())
        
        self.excel_display_format_defaults.setdefault(DataTypeEnum.PERCENT, "0%")

        if self.list_display_format_default is None:
            self.list_display_format_default = ListDisplayFormat(item_delimiter=", ")

class ConfigManager:

    # TODO: https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/-/issues/13
    # In the future, make these part of config
    COLOR_BLUE_GRAY = "C5D9F1"
    COLOR_DARK_BLUE = "538DD5"
    COLOR_GRAY = "BFBFBF"
    COLOR_PINK = "FF1493"
    COLOR_GREEN = "5CB800"
    COLOR_LIGHT_BLUE = "00B0F0"
    COLOR_LIGHT_GREEN = "92D050"
    COLOR_ORANGE = "FFC000"
    COLOR_PURPLE = "B1A0C7"
    COLOR_RED = "FF0000"
    COLOR_YELLOW = "FFFF00"

    FIELD_COMPARISON_UPDATE_COLOR_MAP = {
        FieldUpdateResult.NO_UPDATE: ("no fill", None),
        FieldUpdateResult.LEFT_UPDATED: ("blue", COLOR_LIGHT_BLUE),
        FieldUpdateResult.LEFT_INFORMED: ("dark blue", COLOR_DARK_BLUE),
        FieldUpdateResult.LEFT_NOT_OVERWRITTEN: ("purple", COLOR_PURPLE),
        FieldUpdateResult.LEFT_UPDATE_FAILED: ("pink", COLOR_PINK),
        FieldUpdateResult.RIGHT_UPDATED: ("green", COLOR_GREEN),
        FieldUpdateResult.RIGHT_INFORMED: ("yellow", COLOR_YELLOW),
        FieldUpdateResult.RIGHT_NOT_OVERWRITTEN: ("orange", COLOR_ORANGE),
        FieldUpdateResult.RIGHT_UPDATE_FAILED: ("red", COLOR_RED)
    }

    @staticmethod
    def dict_raise_on_duplicates(ordered_pairs):
        """Reject duplicate keys."""
        d = {}
        for k, v in ordered_pairs:
            if k in d:
                raise ValueError(f"Duplicate key: {k}")
            else:
                d[k] = v
        return d

    def __init__(self, base_directory_path: Path, config_file_path: Path):
        self._config_file_path = config_file_path
        path_config = DefaultPathConfiguration(base_directory_path, 'data/', 'output/')
        self._config = Configuration.convert(None, path_config, **json.load(open(self._config_file_path), object_pairs_hook=ConfigManager.dict_raise_on_duplicates))

    # Return list of user inputs as 2-item lists [name, value].
    # The first item in the list will be the column headers.
    def get_user_input_list(self):
        user_input_info = [["User Input", "Input Value"],
                           ["Config file", self._config_file_path],
                           ["Field Update Default", self._config.field_update_default],
                           ["Field Overwrite Default", self._config.field_overwrite_default]]

        return user_input_info

    def get_interface_config_by_id(self, id: str) -> DataInterfaceConfig:
        return self._config.interface_config_by_id_dict[id]

    def get_data_interface_config_list(self) -> list[DataInterfaceConfig]:
        return [x for x in self._config.interface_config_by_id_dict.values()]

    def get_left_source_config(self):
        return self._config.left_source

    def get_right_source_config(self):
        return self._config.right_source

    def get_calculated_source_config(self):
        return self._config.calculated_source

    #TODO: Make this configurable
    # Return a list containing the color name and value associated with the status.
    # status must be a value from CompareResultsEnum in CompareEnums.py.
    def get_field_color_info_from_status(self, status: FieldUpdateResult):
        return self.FIELD_COMPARISON_UPDATE_COLOR_MAP[status]

    def get_left_record_not_found_color_info(self):
        return ("blue-gray", self.COLOR_BLUE_GRAY)

    def get_right_record_not_found_color_info(self):
        return ("gray", self.COLOR_GRAY)

    def get_data_directory_path(self) -> Path:
        return Path(self._config.data_directory_path)

    def get_output_directory_path(self) -> Path:
        return Path(self._config.output_directory_path)

    def get_output_file_name(self, extension: str):
        ts = datetime.now()
        time_stamp = ts.strftime("%Y-%m-%d_%H%M%S_")
        file_name = time_stamp + self._config.output_file_name + "." + extension
        return self.get_output_directory_path() / file_name

    def get_source_config_by_id(self, id: str) -> SourceConfig:
        return self._config.source_config_by_id_dict[id]

    def get_field_list_by_source_id(self, source_id: str) -> list[Field]:
        return [x for x in self._config.field_by_id_dict_by_source_id_dict[source_id].values()]

    def get_field_by_id_dict(self) -> dict[str, Field]:
        return self._config.field_by_id_dict

    def get_field_by_id(self, id: str) -> Field:
        return self._config.field_by_id_dict[id]

    def get_field_pair_by_id(self, id) -> dict[str, FieldComparisonPair]:
        return self._config.field_pair_by_id_dict[id]

    def get_field_pair_list(self) -> list[FieldComparisonPair]:
        return [x for x in self._config.field_pair_by_id_dict.values()]

    def get_display_field_list(self) -> list[Field | FieldComparisonPair]:
        return self._config.display_field_list

    def get_comparison_config(self) -> ComparisonConfig:
        return self._config.comparison
