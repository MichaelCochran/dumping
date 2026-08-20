from copy import deepcopy
from pathlib import Path
from typing import ClassVar
import unittest
from velociraptor.types.field import DataTypeEnum, JsonDisplayFormat, ListDisplayFormat, SimpleDisplayFormat
from velociraptor.types.keyed_record_comparator import SorEnum

from velociraptor.types.config_manager import Configuration, DefaultPathConfiguration, JiraInterfaceConfig, SheetInterfaceConfig, DataInterfaceTypeEnum, SimpleDisplayFormatConfig

class TestConfigManager(unittest.TestCase):

    def setup_method(self, method):
        self.test_dict = {
            "schema_version": 5,
            "output_file_name": "output",
            "field_update_default": True,
            "field_overwrite_default": True,
            "field_insert_default": True,
            "data_interfaces": [
                {
                    "id": "left_interface_id",
                    "type": "SHEET",
                    "config": {
                        "input_file": "left_input_file",
                        "query_string": "left_query_string"
                    }
                },
                {
                    "id": "right_interface_id",
                    "type": "JIRA",
                    "config": {
                        "server": "right_server",
                        "jql_string": "right_jql_string",
                        "ca_bundle": "myfile",
                        "token": "mytoken"
                    }
                }
            ],
            "left_source": {
                "id": "left_source_id",
                "name": "left_name",
                "data_interface_id": "left_interface_id",
                "pk_field_id": "left_source_id:left_pk",
                "fk_field_id": "left_source_id:left_fk",
            },
            "right_source": {
                "id": "right_source_id",
                "name": "right_name",
                "data_interface_id": "right_interface_id",
                "pk_field_id": "right_source_id:right_pk",
                "fk_field_id": "right_source_id:right_fk",
            },
            "fields": [
                {
                    "id": "left_field_1",
                    "name": "Left Field 1",
                    "source_id": "left_source_id",
                    "data_id": "field_1l",
                    "type": "NUMBER",
                    "output_type": "DATE",
                    "metadata":
                        {
                            "value": "metadata_value_1",
                            "excel_display_format": "metadata_value_3",
                        },
                    "updatable": False,
                    "overwritable": False,
                    "insertable": False,
                    "display": True,
                    "display_index": 5
                },
                {
                    "source_id": "right_source_id",
                    "data_id": "field_1r",
                    "type": "DATE"
                },
                {
                    "source_id": "left_source_id",
                    "data_id": "field_2l",
                    "type": "PERCENT"
                },
                {
                    "source_id": "right_source_id",
                    "data_id": "field_2r",
                    "type": "JIRA_KEY"
                }
            ],
            "field_pairs": [
                {
                    "id": "field_pair_1",
                    "left_field_id": "left_field_1",
                    "right_field_id": "right_source_id:field_1r",
                    "sor": "LEFT",
                    "display": False,
                    "display_index": 6
                },
                {
                    "left_field_id": "left_source_id:field_2l",
                    "right_field_id": "right_source_id:field_2r",
                    "sor": "RIGHT"
                },
                {
                    "left_field_id": "left_field_1",
                    "right_field_id": "right_source_id:field_2r",
                    "sor": "NO_SOR"
                },
            ],
            "comparison": {
                "sort_field_id": "sort_field",
                "reverse": False
            }
        }

    NOT_A_MATCH: ClassVar[str] = "ThisIsAJunkStringThatMatchesNothing"
    path_config: ClassVar[DefaultPathConfiguration] = DefaultPathConfiguration(Path(__file__).parents[1].absolute(), 'data/', 'output/')

    def convert(self, **kwargs):
        return Configuration.convert(None, self.path_config, **kwargs)

    def test_basic_configuration(self):
        config = self.convert(**self.test_dict)

        assert(config.schema_version == 5)
        assert(config.output_file_name == "output")
        assert(config.field_update_default == True)
        assert(config.field_overwrite_default == True)
        assert(config.field_insert_default == True)

        assert(len(config.data_interfaces) == 2)

        assert(config.data_interfaces[0].id == "left_interface_id")
        assert(config.data_interfaces[0].type == DataInterfaceTypeEnum.SHEET)
        assert(isinstance(config.data_interfaces[0].config, SheetInterfaceConfig))
        assert(config.data_interfaces[0].config.input_file == "left_input_file")
        assert(config.data_interfaces[0].config.query_string == "left_query_string")

        assert(config.data_interfaces[1].id == "right_interface_id")
        assert(config.data_interfaces[1].type == DataInterfaceTypeEnum.JIRA)
        assert(isinstance(config.data_interfaces[1].config, JiraInterfaceConfig))
        assert(config.data_interfaces[1].config.server == "right_server")
        assert(config.data_interfaces[1].config.jql_string == "right_jql_string")

        assert(config.left_source.id == "left_source_id")
        assert(config.left_source.name == "left_name")
        assert(config.left_source.pk_field_id == "left_source_id:left_pk")
        assert(config.left_source.fk_field_id == "left_source_id:left_fk")

        assert(config.right_source.id == "right_source_id")
        assert(config.right_source.name == "right_name")
        assert(config.right_source.pk_field_id == "right_source_id:right_pk")
        assert(config.right_source.fk_field_id == "right_source_id:right_fk")

        assert(len(config.fields) == 4)

        assert(config.fields[0].id == "left_field_1")
        assert(config.fields[0].name == "Left Field 1")
        assert(config.fields[0].source_id == "left_source_id")
        assert(config.fields[0].data_id == "field_1l")
        assert(config.fields[0].type == DataTypeEnum.NUMBER)
        assert(config.fields[0].updatable == False)
        assert(config.fields[0].overwritable == False)
        assert(config.fields[0].insertable == False)
        assert(config.fields[0].display == True)
        assert(config.fields[0].display_index == 5)

        assert(config.fields[1].source_id == "right_source_id")
        assert(config.fields[1].data_id == "field_1r")
        assert(config.fields[1].type == DataTypeEnum.DATE)

        assert(config.fields[2].source_id == "left_source_id")
        assert(config.fields[2].data_id == "field_2l")
        assert(config.fields[2].type == DataTypeEnum.PERCENT)

        assert(config.fields[3].source_id == "right_source_id")
        assert(config.fields[3].data_id == "field_2r")
        assert(config.fields[3].type == DataTypeEnum.JIRA_KEY)

        assert(len(config.field_pairs) == 3)

        assert(config.field_pairs[0].id == "field_pair_1")
        assert(config.field_pairs[0].left_field_id == "left_field_1")
        assert(config.field_pairs[0].right_field_id == "right_source_id:field_1r")
        assert(config.field_pairs[0].sor == SorEnum.LEFT)
        assert(config.field_pairs[0].display == False)
        assert(config.field_pairs[0].display_index == 6)

        assert(config.field_pairs[1].left_field_id == "left_source_id:field_2l")
        assert(config.field_pairs[1].right_field_id == "right_source_id:field_2r")
        assert(config.field_pairs[1].sor == SorEnum.RIGHT)

        assert(config.field_pairs[2].left_field_id == "left_field_1")
        assert(config.field_pairs[2].right_field_id == "right_source_id:field_2r")
        assert(config.field_pairs[2].sor == SorEnum.NO_SOR)

        assert(config.comparison.sort_field_id == "sort_field")
        assert(config.comparison.reverse == False)

        assert(len(config.fields) == len(config.field_by_id_dict))
        for field_config in config.fields:
            assert(field_config.id in config.field_by_id_dict)
            field = config.field_by_id_dict[field_config.id]
            assert(field_config.id == field.id)
            assert(field_config.name == field.name)
            assert(field_config.source_id == field.source_id)
            assert(field_config.data_id == field.data_id)
            assert(field_config.type == field.type)
            assert(field_config.metadata == field.metadata)
            assert(field_config.updatable == field.updatable)
            assert(field_config.overwritable == field.overwritable)
            assert(field_config.insertable == field.insertable)
        assert(config.field_by_id_dict)

    def test_configuration_deserialization(self):
        config_dict = self.test_dict

        config_dict["field_update_default"] = False
        config = self.convert(**self.test_dict)
        assert(config.field_update_default == False)

        config_dict["field_overwrite_default"] = False
        config = self.convert(**self.test_dict)
        assert(config.field_overwrite_default == False)

        config_dict["field_insert_default"] = False
        config = self.convert(**self.test_dict)
        assert(config.field_insert_default == False)

    def test_display_format_defaults(self):
        config_dict = self.test_dict

        config_dict["display_format_defaults"] = { "DATE": "{0:%m/%d/%Y}", "PERCENT": "{0:.0%}" }
        config = self.convert(**self.test_dict)
        assert(DataTypeEnum.DATE in config.display_format_defaults)
        assert(config.display_format_defaults[DataTypeEnum.DATE] == SimpleDisplayFormat("{0:%m/%d/%Y}"))
        assert(DataTypeEnum.PERCENT in config.display_format_defaults)
        assert(config.display_format_defaults[DataTypeEnum.PERCENT] == SimpleDisplayFormat("{0:.0%}"))


        # Test that display_format_defaults can be partially defined and
        # that ConfigManager will fill in defaults for the missing elements
        config_dict["display_format_defaults"] = { "DATE": "{0:%m/%d/%Y}" }
        config = self.convert(**self.test_dict)
        assert(DataTypeEnum.DATE in config.display_format_defaults)
        assert(config.display_format_defaults[DataTypeEnum.DATE] == SimpleDisplayFormat("{0:%m/%d/%Y}"))
        assert(DataTypeEnum.PERCENT in config.display_format_defaults)
        assert(config.display_format_defaults[DataTypeEnum.PERCENT] == SimpleDisplayFormat("{0:.0%}"))
        assert(DataTypeEnum.JSON in config.display_format_defaults)
        assert(config.display_format_defaults[DataTypeEnum.JSON] == JsonDisplayFormat())
        assert(config.list_display_format_default == ListDisplayFormat(item_delimiter=", "))

    def test_excel_display_format_defaults(self):
        config_dict = self.test_dict

        config_dict["excel_display_format_defaults"] = { "DATE": "yyyy-mm-dd", "PERCENT": "0.00%" }
        config = self.convert(**self.test_dict)
        assert(DataTypeEnum.DATE in config.excel_display_format_defaults)
        assert(config.excel_display_format_defaults[DataTypeEnum.DATE] == "yyyy-mm-dd")
        assert(DataTypeEnum.PERCENT in config.excel_display_format_defaults)
        assert(config.excel_display_format_defaults[DataTypeEnum.PERCENT] == "0.00%")


        # Test that excel_display_format_defaults can be partially defined and
        # that ConfigManager will fill in defaults for the missing elements
        config_dict["excel_display_format_defaults"] = { "DATE": "yyyy-mm-dd" }
        config = self.convert(**self.test_dict)
        assert(DataTypeEnum.DATE in config.excel_display_format_defaults)
        assert(config.excel_display_format_defaults[DataTypeEnum.DATE] == "yyyy-mm-dd")
        assert(DataTypeEnum.PERCENT in config.excel_display_format_defaults)
        assert(config.excel_display_format_defaults[DataTypeEnum.PERCENT] == "0%")

    def test_interface_config_type_mismatch(self):
        interface_config_dict = self.test_dict["data_interfaces"][0]

        config = self.convert(**self.test_dict)
        assert(config.data_interfaces[0].type == DataInterfaceTypeEnum.SHEET)
        assert(isinstance(config.data_interfaces[0].config, SheetInterfaceConfig))

        interface_config_dict["type"] = "JIRA"
        with self.assertRaises(Exception):
            self.convert(**self.test_dict)

    def test_interface_config_duplicate_id(self):
        interface_config_dict = self.test_dict["data_interfaces"][0]

        config = self.convert(**self.test_dict)
        assert(config.data_interfaces[0].id != config.data_interfaces[1].id)

        interface_config_dict["id"] = config.right_source.id
        with self.assertRaises(Exception):
            self.convert(**self.test_dict)

    def test_source_config_default_name(self):
        source_config_dict = self.test_dict["left_source"]

        config = self.convert(**self.test_dict)
        assert(config.left_source.name != config.left_source.id)

        del source_config_dict["name"]
        config = self.convert(**self.test_dict)
        assert(config.left_source.name == config.left_source.id)

    def test_source_config_duplicate_id(self):
        source_config_dict = self.test_dict["left_source"]

        config = self.convert(**self.test_dict)
        assert(config.left_source.id != config.right_source.id)

        source_config_dict["id"] = config.right_source.id
        with self.assertRaises(Exception):
            self.convert(**self.test_dict)

    def test_source_config_no_interface_id_match(self):
        source_config_dict = self.test_dict["left_source"]

        source_config_dict["data_interface_id"] = self.NOT_A_MATCH

        with self.assertRaises(Exception):
            self.convert(**self.test_dict)

    def test_field_config_default_id(self):
        field_config_dict = self.test_dict["fields"][0]
        expected = "left_source_id:field_1l"

        config = self.convert(**self.test_dict)
        assert(config.fields[0].id != expected)

        del field_config_dict["id"]
        
        # Remove field pairs that match the deleted id for this test
        self.test_dict["field_pairs"] = []

        config = self.convert(**self.test_dict)
        assert(config.fields[0].id == expected)

    def test_field_config_default_name_with_id(self):
        field_config_dict = self.test_dict["fields"][0]

        config = self.convert(**self.test_dict)
        assert(config.fields[0].name != config.fields[0].id)

        del field_config_dict["name"]

        config = self.convert(**self.test_dict)
        assert(config.fields[0].name == config.fields[0].id)

    def test_field_config_default_name_without_id(self):
        field_config_dict = self.test_dict["fields"][0]

        del field_config_dict["name"]

        config = self.convert(**self.test_dict)
        assert(config.fields[0].name == config.fields[0].id)

        del field_config_dict["id"]

        # Remove field pairs that match the deleted id for this test
        self.test_dict["field_pairs"] = []

        config = self.convert(**self.test_dict)
        assert(config.fields[0].name == config.fields[0].id)

    def test_field_config_formula_type_no_value(self):
        field_config_dict = self.test_dict["fields"][1]
        field_config_dict["type"] = DataTypeEnum.FORMULA.name
        with self.assertRaises(Exception):
            self.convert(**self.test_dict)

        field_config_dict["metadata"] = { "value": "myvalue" }
        config = self.convert(**self.test_dict)
        assert(config.fields[1].metadata.value == "myvalue")

    def test_field_config_default_date_display_format(self):
        config_dict = self.test_dict
        config_dict["display_format_defaults"] = { "DATE": "{0:%m/%d/%Y}" }

        field_config_dict = self.test_dict["fields"][1]
        assert(field_config_dict["type"] == DataTypeEnum.DATE.name)
        assert("metadata" not in field_config_dict)

        config = self.convert(**self.test_dict)
        assert(DataTypeEnum.DATE in config.display_format_defaults)
        assert(config.fields[1].metadata.display_format == config.display_format_defaults[DataTypeEnum.DATE])

        # Default not set and previous value retained when there is a display_format defined
        field_config_dict["metadata"] = { "display_format": "myformat" }
        config = self.convert(**self.test_dict)
        assert(config.fields[1].metadata.display_format == SimpleDisplayFormat("myformat"))

    def test_field_config_default_date_excel_display_format(self):
        config_dict = self.test_dict
        config_dict["excel_display_format_defaults"] = { "DATE": "yyyy-mm-dd" }

        field_config_dict = self.test_dict["fields"][1]
        assert(field_config_dict["type"] == DataTypeEnum.DATE.name)
        assert("metadata" not in field_config_dict)

        config = self.convert(**self.test_dict)
        assert(DataTypeEnum.DATE in config.excel_display_format_defaults)
        assert(config.fields[1].metadata.excel_display_format == config.excel_display_format_defaults[DataTypeEnum.DATE])

        # Default not set and previous value retained when there is a excel_display_format defined
        field_config_dict["metadata"] = { "excel_display_format": "myformat" }
        config = self.convert(**self.test_dict)
        assert(config.fields[1].metadata.excel_display_format == "myformat")

    def test_field_config_output_type_default_date_excel_display_format(self):
        config_dict = self.test_dict
        config_dict["excel_display_format_defaults"] = { "DATE": "yyyy-mm-dd" }

        field_config_dict = self.test_dict["fields"][1]
        field_config_dict["type"] = DataTypeEnum.FORMULA.name
        field_config_dict["output_type"] = DataTypeEnum.DATE.name
        field_config_dict["metadata"] = { "value": "myvalue" }

        config = self.convert(**self.test_dict)
        assert(DataTypeEnum.DATE in config.excel_display_format_defaults)
        assert(config.fields[1].metadata.excel_display_format == config.excel_display_format_defaults[DataTypeEnum.DATE])

        # Default not set and previous value retained when there is a excel_display_format defined
        field_config_dict["metadata"] = { "value": "myvalue", "excel_display_format": "myformat" }
        config = self.convert(**self.test_dict)
        assert(config.fields[1].metadata.excel_display_format == "myformat")

    def test_field_config_default_updatable(self):
        config_dict = self.test_dict

        del config_dict["fields"][0]["updatable"]

        config_dict["field_update_default"] = False
        config = self.convert(**self.test_dict)

        assert(config.field_update_default == False)
        assert(config.fields[0].updatable == False)
        assert(config.field_by_id_dict[config.fields[0].id].updatable == False)

        config_dict["field_update_default"] = True
        config = self.convert(**self.test_dict)

        assert(config.field_update_default == True)
        assert(config.fields[0].updatable == True)
        assert(config.field_by_id_dict[config.fields[0].id].updatable == True)

    def test_field_config_default_overwritable(self):
        config_dict = self.test_dict

        del config_dict["fields"][0]["overwritable"]

        config_dict["field_overwrite_default"] = False
        config = self.convert(**self.test_dict)

        assert(config.field_overwrite_default == False)
        assert(config.fields[0].overwritable == False)
        assert(config.field_by_id_dict[config.fields[0].id].overwritable == False)

        config_dict["field_overwrite_default"] = True
        config = self.convert(**self.test_dict)
        assert(config.field_overwrite_default == True)
        assert(config.fields[0].overwritable == True)
        assert(config.field_by_id_dict[config.fields[0].id].overwritable == True)

    def test_field_config_default_insertable(self):
        config_dict = self.test_dict

        del config_dict["fields"][0]["insertable"]

        config_dict["field_insert_default"] = False
        config = self.convert(**self.test_dict)
        assert(config.field_insert_default == False)
        assert(config.fields[0].insertable == False)
        assert(config.field_by_id_dict[config.fields[0].id].insertable == False)

        config_dict["field_insert_default"] = True
        config = self.convert(**self.test_dict)
        assert(config.field_insert_default == True)
        assert(config.fields[0].insertable == True)
        assert(config.field_by_id_dict[config.fields[0].id].insertable == True)

    def test_field_config_default_display(self):
        field_config_dict = self.test_dict["fields"][0]

        del field_config_dict["display"]
        config = self.convert(**self.test_dict)

        assert(config.fields[0].display == False)

    def test_field_config_no_source_id_match(self):
        field_config_dict = self.test_dict["fields"][0]

        field_config_dict["source_id"] = self.NOT_A_MATCH

        with self.assertRaises(Exception):
            self.convert(**self.test_dict)

    def test_field_config_duplicate_data_id(self):
        field_config_dict_2 = self.test_dict["fields"][2]

        # Build a field duplicate with index 2 but with a unique id
        field_config_dict_new = deepcopy(field_config_dict_2)
        field_config_dict_new["id"] = field_config_dict_2["data_id"] + "_new"
        self.test_dict["fields"].append(field_config_dict_new)

        # Test no exception is raised when there are duplicate data_ids with different source_ids
        config = self.convert(**self.test_dict)
        assert(len(config.fields) == 5)

        # Test index 2 and 4 (new) have the same source_id and data_id but different ids
        assert(config.fields[2].id != config.fields[4].id)
        assert(config.fields[2].source_id == config.fields[4].source_id)
        assert(config.fields[2].data_id == config.fields[4].data_id)

    def test_field_config_duplicate_id(self):
        field_config_dict_0 = self.test_dict["fields"][0]
        field_config_dict_1 = self.test_dict["fields"][1]

        # Test index 0 has an id and index 1 does not
        assert(field_config_dict_0.get("id") is not None)
        assert(field_config_dict_1.get("id") is None)

        # Test index 0 and 1 have different source_ids and data_ids to begin with
        assert(field_config_dict_0["source_id"] != field_config_dict_1["source_id"])
        assert(field_config_dict_0["data_id"] != field_config_dict_1["data_id"])

        # Now assign index 1 the id of index 0 so they are the same
        field_config_dict_1["id"] = field_config_dict_0["id"]

        # Test exception is raised when there are duplicate ids
        with self.assertRaises(Exception):
            self.convert(**self.test_dict)

    def test_field_pair_config_default_id(self):
        config_dict = self.test_dict
        expected = "left_field_1-right_source_id:field_1r"

        config = self.convert(**self.test_dict)
        assert(config.field_pairs[0].id != expected)

        del config_dict["field_pairs"][0]["id"]

        config = self.convert(**self.test_dict)
        assert(config.field_pairs[0].id == expected)

    def test_field_pair_config_default_display(self):
        field_pair_config_dict = self.test_dict["field_pairs"][0]

        del field_pair_config_dict["display"]
        config = self.convert(**self.test_dict)

        assert(config.field_pairs[0].display == True)

    def test_field_pair_no_fields_for_left_source(self):
        config_dict = self.test_dict

        for field_config_dict in config_dict["fields"]:
            field_config_dict["source_id"] = config_dict["right_source"]["id"]

        with self.assertRaises(Exception):
            self.convert(**self.test_dict)

    def test_field_pair_no_fields_for_right_source(self):
        config_dict = self.test_dict
        for field_config_dict in config_dict["fields"]:
            field_config_dict["source_id"] = config_dict["left_source"]["id"]

        with self.assertRaises(Exception):
            self.convert(**self.test_dict)

    def test_field_pair_no_left_field_id_match(self):
        config_dict = self.test_dict

        assert(config_dict["fields"][0]["source_id"] == config_dict["left_source"]["id"])

        config_dict["fields"][0]["id"] = self.NOT_A_MATCH
        with self.assertRaises(Exception):
            self.convert(**self.test_dict)

    def test_field_pair_no_right_field_id_match(self):
        config_dict = self.test_dict

        assert(config_dict["fields"][1]["source_id"] == config_dict["right_source"]["id"])

        config_dict["fields"][1]["id"] = self.NOT_A_MATCH
        with self.assertRaises(Exception):
            self.convert(**self.test_dict)
