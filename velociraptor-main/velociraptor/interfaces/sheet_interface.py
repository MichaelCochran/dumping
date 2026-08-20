'''
----------------------------------------------------------------------------
Library   : velociraptor
Package   : velociraptor.interfaces
Class     : SheetInterface.py
Engineers : Steve Schifris
Abstract  : This class provides an interface to read, write, and manupulate spreadsheets.
            The implementation relies heavily on pandas.read_excel and pandas.ExcelWriter.
            For more info, see
            https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html and
            https://pandas.pydata.org/docs/reference/api/pandas.ExcelWriter.html.
----------------------------------------------------------------------------
'''

from pathlib import Path
from typing import Any
import pandas as pd

from velociraptor.types.data_interface_config import SheetInterfaceConfig
from velociraptor.types.evaluator import CalculationEvaluator
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.record import Record
from velociraptor.types.data_interface import DataInterface

class SheetRowRecord(Record):

    @staticmethod
    def is_custom_data_id(data_id: str):
        return data_id.startswith("__")

    def __init__(self, data):
        self._data = data
        self._custom_data: dict[str, Any] = {}

    def __get_custom_value(self, field: Field):
        data_id = field.data_id
        try:
            value = self._custom_data[data_id]
        except Exception:
            raise ValueError(f"Error getting data_id '{data_id}':\ndata: {self._custom_data}")
        
        return value

    def __get_value_raw(self, field: Field):
        value = self._data[field.data_id]
        try:
            if pd.isnull(value):
                return None

            if field.type == DataTypeEnum.DATE:
                if type(value) is not pd.Timestamp:
                    raise TypeError("Type mismatch")
                value = value.to_pydatetime().date()
            elif field.type == DataTypeEnum.FORMULA:
                raise TypeError("Unsupported type")

            return value
        except Exception as e:
            print("Error getting value from Sheet row record:")
            print("value:", value)
            print("record:", self._data)
            print("field:", field)
            raise ValueError("Error getting value") from e

    def get_value(self, field: Field):
        if self.is_custom_data_id(field.data_id):
            value = self.__get_custom_value(field)
        else:
            value = self.__get_value_raw(field)

        if value is not None:
            value = self._wrap_value(field, value)

        return value

    def set_custom_value(self, field: Field, value: Any):
        self._custom_data[field.data_id] = value

    def get_values(self):
        return self._data

# Sheet is short for Spreadsheet. This interface enables reading from and writing to spreadsheets.
class SheetInterface(DataInterface):
    DEBUG_ON = False
    DEBUG_COMMON_ON = False

    ROW_NUM_FIELD = Field(data_id="__row_number", type=DataTypeEnum.NUMBER)

    def __init__(self, config: SheetInterfaceConfig):
        self._config = config

        # TODO: Make this command line overridable:
        sheet_file_name = self._config.input_file
        sheet_file_path = Path(config.data_directory_path) / sheet_file_name

        self._sheet_task_frame = pd.read_excel(sheet_file_path) # returns pandas.core.frame.DataFrame
        if config.query_string is not None:
            self._sheet_task_frame.query(config.query_string, inplace=True)

        # Example format of the returned row of type class 'pandas.core.series.Series:
        # row item:  nan , type(i): <class 'float'> or row item:  Lookahead-001 , type(i): <class 'str'>
        # row item:  SSWF_IAD-345 , type(i): <class 'str'>
        # row item:  Lookahead PI-01 , type(i): <class 'str'>
        # row item:  25.0 , type(i): <class 'float'>
        # row item:  0.5556 , type(i): <class 'float'>
        # row item:  2023-03-08 00:00:00 , type(i): <class 'pandas._libs.tslibs.timestamps.Timestamp'>
        # row item:  2023-06-07 00:00:00 , type(i): <class 'pandas._libs.tslibs.timestamps.Timestamp'>
        # row item:  2023-03-01 00:00:00 , type(i): <class 'pandas._libs.tslibs.timestamps.Timestamp'>
        # row item:  2023-06-01 00:00:00 , type(i): <class 'pandas._libs.tslibs.timestamps.Timestamp'>
        # row item:  NaT , type(i): <class 'pandas._libs.tslibs.nattype.NaTType'>
        # row item:  NaT , type(i): <class 'pandas._libs.tslibs.nattype.NaTType'>
        # row item:  NaT , type(i): <class 'pandas._libs.tslibs.nattype.NaTType'>
        # row item:  NaT , type(i): <class 'pandas._libs.tslibs.nattype.NaTType'>

        if (self.DEBUG_ON):
            print("\n***************** SHEET INTERFACE:\n")
            print("self._sheetTaskFrame len = ", len(self._sheet_task_frame))
            print("self._sheetTaskFrame type: ", type(self._sheet_task_frame))

# Gory detailed debugging to dump the type and value of every cell; uncomment if needed
#            print("\n\n****************SheetInterface rows\n")
#            for index, row in self._sheetTaskFrame.iterrows():
#                print("sheet index:", index, "; row type:", type(row))
#                print("sheet row:\n", row)
#                for i in row:
#                    print("row item: ", i, ", type(i):", type(i), "null:",
#                            (type(i) is float and math.isnan(i)) or (type(i) is pd._libs.tslibs.nattype.NaTType))
            print("****************SheetInterface rows done\n\n")

            self.print_sheet()  # prints an abbreviated matrix (some columns clipped)
            print("****************SheetInterface.printSheet() done\n\n")

    def get_records(self, fields: list[Field]) -> list[Record]:
        records: list[SheetRowRecord] = []
        for index, row in self._sheet_task_frame.iterrows():
            record = SheetRowRecord(row)
            record.set_custom_value(self.ROW_NUM_FIELD, index)
            records.append(record)

        field_by_id_dict = { x.id : x for x in fields}

        evaluator = CalculationEvaluator()
        evaluator.update_value_function(lambda id: record.get_value(field_by_id_dict[id]))
        for field in fields:
            if SheetRowRecord.is_custom_data_id(field.data_id) and field.calculation is not None:
                for record in records:
                    value = evaluator.eval_field_calculation(field)
                    record.set_custom_value(field, value)

        if (filter_expr:=self._config.filter) is not None:
            parsed_filter_expr = evaluator.parse(filter_expr)
            filtered_records: list[SheetRowRecord] = []
            for record in records:
                value = evaluator.eval(filter_expr, parsed_filter_expr)
                if value is False:
                    # Ignore records that do not pass the filter
                    pass
                elif value is not True:
                    raise Exception("Filter did not evaluate to a boolean")
                else:
                    filtered_records.append(record)
            return filtered_records
        else:
            return records

    def is_insert_supported(self) -> bool:
        return False

    def is_update_supported(self) -> bool:
        return False

    # Default printout of the raw format. Shows a subset of columns with elipses for the hidden ones.
    def print_sheet(self):
        print(self._sheet_task_frame)
