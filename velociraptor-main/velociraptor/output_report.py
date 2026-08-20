import re
from typing import Optional
from velociraptor.types.keyed_record_comparison_updater import KeyedRecordUpdate, KeyedRecordUpdateResult
from velociraptor.interfaces.sheet_writer_interface import SheetWriterInterface
from velociraptor.types.config_manager import ConfigManager
from velociraptor.types.keyed_record_comparator import FieldComparisonPair, FieldComparisonResult, SorEnum
from velociraptor.types.keyed_record_comparison_updater import FieldUpdateResult
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.record import Record

DEFAULT_WIDTH = 16
DATE_WIDTH = 16
STRING_WIDTH = 16

class OutputReport:
    def __init__(self, config_mgr: ConfigManager):
        self.__config_mgr = config_mgr
        self.__headers = []
        self.__field_to_col_dict: dict[Field, int] = {}
        self.__data_rows = []
        self.__color_cells_old = [] # Deprecated
        self.__color_cells = []
        self.__border_cells = []
        self.__num_formats = []
        self.__merged_comments = []
        self.__widths: list[tuple[int, int]] = []
        self.__merged_hidden: list[int] = []
        self.__swi = SheetWriterInterface(self.__config_mgr)

    def __process_column(self, field: Field, col_idx: int):
        self.__headers.append(field.name)

        width = DEFAULT_WIDTH
        if field.type is DataTypeEnum.DATE:
            width = DATE_WIDTH
        elif field.type is DataTypeEnum.STRING:
            width = STRING_WIDTH
        self.__widths.append([col_idx, width])

        # Apply number format if it is defined
        if field.metadata.excel_display_format is not None:
            self.__num_formats.append((col_idx, field.metadata.excel_display_format))

        self.__field_to_col_dict[field.id] = col_idx

    def __get_formula_value(self, field: Field, row_idx: int):
        return re.sub('{{(.*?)}}', lambda m: self.__swi.get_cell_id(self.__field_to_col_dict[m.group(1)], row_idx), field.metadata.value)

    def generate_report(self, updates: list[KeyedRecordUpdate], calculated_records: list[Optional[Record]], display_fields: list[Field | FieldComparisonPair], left_name: str, right_name: str):
        col_idx = 0
        for display_field in display_fields:
            if isinstance(display_field, Field):
                self.__process_column(display_field, col_idx)
                col_idx += 1

            elif isinstance(display_field, FieldComparisonPair):
                self.__process_column(display_field.left_field, col_idx)
                if display_field.sor != SorEnum.LEFT:
                    self.__merged_hidden.append(col_idx)
                col_idx += 1

                self.__process_column(display_field.right_field, col_idx)
                if display_field.sor != SorEnum.RIGHT:
                    self.__merged_hidden.append(col_idx)
                col_idx += 1

            else:
                raise Exception

        # TODO make configurably displayed and add to "Calculated"
        self.__headers.append("Changes")

        row_idx = 1 # Skip header
        calculated_record_idx = 0
        for update in updates:
            data_row = []
            col_idx = 0
            left_record = update.matched_pair.l_record.record
            right_record = update.matched_pair.r_record.record
            calculated_record = calculated_records[calculated_record_idx]
            calculated_record_idx = calculated_record_idx + 1

            # Check for left or right empty records and determine entire row color if appropriate
            row_color_info = None # color info is a tuple[str, str] containing [0] a human-readable color name and [1] the rgb hex code
            if left_record is None:
                row_color_info = self.__config_mgr.get_left_record_not_found_color_info()
            elif right_record is None:
                row_color_info = self.__config_mgr.get_right_record_not_found_color_info()

            # SheetWriterInterface (ExcelWriter) understands python types, so use get_value()
            for display_field in display_fields:
                if isinstance(display_field, Field):
                    if display_field.source_id == self.__config_mgr.get_left_source_config().id:
                        data_row.append(left_record.get_value(display_field) if left_record is not None else "NOT FOUND")
                    elif display_field.source_id == self.__config_mgr.get_right_source_config().id:
                        data_row.append(right_record.get_value(display_field) if right_record is not None else "NOT FOUND")
                    elif display_field.source_id == self.__config_mgr.get_calculated_source_config().id:
                        if display_field.type == DataTypeEnum.FORMULA:
                            data_row.append(self.__get_formula_value(display_field, row_idx) if left_record is not None and right_record is not None else "")
                        else:
                            data_row.append(calculated_record.get_value(display_field) if calculated_record is not None else None)
                    else:
                        raise Exception
                    if row_color_info is not None:
                        self.__color_cells_old.append([col_idx, row_idx, row_color_info[1]])
                        self.__color_cells.append([col_idx, row_idx, row_color_info[1]])
                    col_idx += 1

                elif isinstance(display_field, FieldComparisonPair):
                    # Add both the left and right values in cells for comparison fields
                    l_cell_old_source = None
                    r_cell_old_source = None
                    old_rf = None

                    l_cell_color_info = r_cell_color_info = row_color_info
                    l_cell_color_info_old = r_cell_color_info_old = row_color_info # Deprecated

                    if left_record is None:
                        data_row.append("NOT FOUND")
                        # If the missing record is the SOR and the field is not the primary key, fetch the old source and record information for the report
                        if display_field.sor == SorEnum.LEFT and display_field.left_field.data_id != self.__config_mgr.get_left_source_config().pk_field_id:
                            l_cell_old_source = right_name # Old right data written in left cell comment
                            old_rf = display_field.get_record_field(update.matched_pair, False)
                    else:
                        data_row.append(left_record.get_value(display_field.left_field))

                    if right_record is None:
                        data_row.append("NOT FOUND")
                        # If the missing record is the SOR and the field is not the primary key, fetch the old source and record information for the report
                        if display_field.sor == SorEnum.RIGHT and display_field.right_field.data_id != self.__config_mgr.get_right_source_config().pk_field_id:
                            r_cell_old_source = left_name # Old left data written in right cell comment
                            old_rf = display_field.get_record_field(update.matched_pair, False)
                    else:
                        data_row.append(right_record.get_value(display_field.right_field))

                    if left_record is not None and right_record is not None:
                        field_update = update.field_updates[display_field.id]

                        if (field_update.result == FieldUpdateResult.LEFT_UPDATED or
                            field_update.result == FieldUpdateResult.RIGHT_UPDATED):
                            l_cell_color_info = self.__config_mgr.get_field_color_info_from_status(FieldUpdateResult.RIGHT_UPDATED)
                            r_cell_color_info = self.__config_mgr.get_field_color_info_from_status(FieldUpdateResult.RIGHT_UPDATED)
                        elif (field_update.result == FieldUpdateResult.LEFT_UPDATE_FAILED or
                            field_update.result == FieldUpdateResult.RIGHT_UPDATE_FAILED):
                            l_cell_color_info = self.__config_mgr.get_field_color_info_from_status(FieldUpdateResult.RIGHT_UPDATE_FAILED)
                            r_cell_color_info = self.__config_mgr.get_field_color_info_from_status(FieldUpdateResult.RIGHT_UPDATE_FAILED)
                        elif (field_update.result == FieldUpdateResult.LEFT_INFORMED or
                            field_update.result == FieldUpdateResult.LEFT_NOT_OVERWRITTEN or
                            field_update.result == FieldUpdateResult.RIGHT_INFORMED or
                            field_update.result == FieldUpdateResult.RIGHT_NOT_OVERWRITTEN):
                            l_cell_color_info = self.__config_mgr.get_field_color_info_from_status(FieldUpdateResult.RIGHT_NOT_OVERWRITTEN)
                            r_cell_color_info = self.__config_mgr.get_field_color_info_from_status(FieldUpdateResult.RIGHT_NOT_OVERWRITTEN)
                        elif (field_update.comparison.result == FieldComparisonResult.FAIL or
                            field_update.comparison.result == FieldComparisonResult.LEFT_ONLY or
                            field_update.comparison.result == FieldComparisonResult.RIGHT_ONLY):
                            l_cell_color_info = self.__config_mgr.get_field_color_info_from_status(FieldUpdateResult.RIGHT_INFORMED)
                            r_cell_color_info = self.__config_mgr.get_field_color_info_from_status(FieldUpdateResult.RIGHT_INFORMED)

                        if (field_update.result == FieldUpdateResult.LEFT_INFORMED or
                            field_update.result == FieldUpdateResult.LEFT_NOT_OVERWRITTEN or
                            field_update.result == FieldUpdateResult.LEFT_UPDATED or
                            field_update.result == FieldUpdateResult.LEFT_UPDATE_FAILED):
                            r_cell_old_source = left_name # Old left data written in right cell comment
                            old_rf = display_field.get_record_field(update.matched_pair, False)
                            self.__border_cells.append((col_idx + 1, row_idx))
                            r_cell_color_info_old = self.__config_mgr.get_field_color_info_from_status(field_update.result)
                        elif (field_update.result == FieldUpdateResult.RIGHT_INFORMED or
                            field_update.result == FieldUpdateResult.RIGHT_NOT_OVERWRITTEN or
                            field_update.result == FieldUpdateResult.RIGHT_UPDATED or
                            field_update.result == FieldUpdateResult.RIGHT_UPDATE_FAILED):
                            l_cell_old_source = right_name # Old right data written in left cell comment
                            old_rf = display_field.get_record_field(update.matched_pair, False)
                            self.__border_cells.append((col_idx, row_idx))
                            l_cell_color_info_old = self.__config_mgr.get_field_color_info_from_status(field_update.result)

                    if old_rf is not None:
                        old_value = str(old_rf.record.get_value(old_rf.field)) or "<empty>"
                    if l_cell_old_source is not None:
                        self.__merged_comments.append((col_idx, row_idx, "Old " + l_cell_old_source + " value: \n" + old_value))
                    if r_cell_old_source is not None:
                        self.__merged_comments.append((col_idx + 1, row_idx, "Old " + r_cell_old_source + " value: \n" + old_value))

                    if l_cell_color_info is not None:
                        self.__color_cells.append([col_idx, row_idx, l_cell_color_info[1]])
                    if r_cell_color_info is not None:
                        self.__color_cells.append([col_idx + 1, row_idx, r_cell_color_info[1]])
                    # Deprecated
                    if l_cell_color_info_old is not None:
                        self.__color_cells_old.append([col_idx, row_idx, l_cell_color_info_old[1]])
                    if r_cell_color_info_old is not None:
                        self.__color_cells_old.append([col_idx + 1, row_idx, r_cell_color_info_old[1]])

                    col_idx += 2

                else:
                    raise Exception

            if (update.result == KeyedRecordUpdateResult.LEFT_NOT_FOUND or
                update.result == KeyedRecordUpdateResult.RIGHT_NOT_FOUND):
                data_row.append("Not found")
            elif update.result == KeyedRecordUpdateResult.NEITHER_CHANGED:
                data_row.append("Neither")
            elif update.result == KeyedRecordUpdateResult.LEFT_CHANGED:
                data_row.append(right_name) # "Left SOR changed" means changes need to be effected in the right interface
            elif update.result == KeyedRecordUpdateResult.RIGHT_CHANGED:
                data_row.append(left_name) # "Right SOR changed" means changes need to be effected in the left interface
            elif update.result == KeyedRecordUpdateResult.BOTH_CHANGED:
                data_row.append("Both")
            else:
                raise Exception

            self.__data_rows.append(data_row)
            row_idx += 1

        output_sheets_list = []

        output_sheets_list.append(self.__get_legend_sheet(self.__config_mgr.get_user_input_list(), left_name, right_name))
        output_sheets_list.append({self.__swi.SHEET_NAME_KEY: "Merged",
                                self.__swi.VALUES_KEY: self.__data_rows, self.__swi.COLORS_KEY: self.__color_cells_old, # Change to 'color_cells' when ready to use new color scheme
                                self.__swi.HEADERS_KEY: self.__headers, self.__swi.COMMENTS_KEY: self.__merged_comments,
                                self.__swi.COLUMN_WIDTHS_KEY: self.__widths,
                                self.__swi.FREEZE_TOP_ROW: True, self.__swi.HAS_FILTER: True, self.__swi.HIDDEN_COLS_KEY: self.__merged_hidden,
                                self.__swi.BORDERS_KEY: None, self.__swi.NUMBER_FORMATS_KEY: self.__num_formats})
        output_sheets_list.append({self.__swi.SHEET_NAME_KEY: "Interleaved",
                                self.__swi.VALUES_KEY: self.__data_rows, self.__swi.COLORS_KEY: self.__color_cells_old, # Change to 'color_cells' when ready to use new color scheme
                                self.__swi.HEADERS_KEY: self.__headers, self.__swi.COMMENTS_KEY: None,
                                self.__swi.COLUMN_WIDTHS_KEY: self.__widths,
                                self.__swi.FREEZE_TOP_ROW: True, self.__swi.HAS_FILTER: True, self.__swi.HIDDEN_COLS_KEY: None,
                                self.__swi.BORDERS_KEY: None, self.__swi.NUMBER_FORMATS_KEY: self.__num_formats})
        output_sheets_list.append({self.__swi.SHEET_NAME_KEY: "New Interleaved",
                                self.__swi.VALUES_KEY: self.__data_rows, self.__swi.COLORS_KEY: self.__color_cells,
                                self.__swi.HEADERS_KEY: self.__headers, self.__swi.COMMENTS_KEY: None,
                                self.__swi.COLUMN_WIDTHS_KEY: self.__widths,
                                self.__swi.FREEZE_TOP_ROW: True, self.__swi.HAS_FILTER: True, self.__swi.HIDDEN_COLS_KEY: None,
                                self.__swi.BORDERS_KEY: self.__border_cells, self.__swi.NUMBER_FORMATS_KEY: self.__num_formats})

        self.__swi.create_output_workbook(self.__config_mgr.get_output_file_name("xlsx"), output_sheets_list)

    def __get_legend_sheet(self, user_input_info, left_name: str, right_name: str):
        FIELD_UPDATE_COLOR_MAP = {
            FieldUpdateResult.NO_UPDATE: "No difference found",
            FieldUpdateResult.LEFT_UPDATED: left_name + " updated from " + right_name,
            FieldUpdateResult.LEFT_INFORMED: left_name + " informed (not updated) by " + right_name,
            FieldUpdateResult.LEFT_NOT_OVERWRITTEN: left_name + " informed (not overwritten) by " + right_name,
            FieldUpdateResult.LEFT_UPDATE_FAILED: left_name + " failed to update",
            FieldUpdateResult.RIGHT_UPDATED: right_name + " updated from " + left_name,
            FieldUpdateResult.RIGHT_INFORMED: right_name + " informed (not updated) by " + left_name,
            FieldUpdateResult.RIGHT_NOT_OVERWRITTEN: right_name + " informed (not overwritten) by " + left_name,
            FieldUpdateResult.RIGHT_UPDATE_FAILED: right_name + " failed to update",
        }

        output_values = []
        output_colors = []
        output_bold = [[0,0], [1,0]]

        output_values.append(["Fill Color Meaning"])
        row_index = len(output_values)

        # TODO: Filter to only the legend colors used. No Issue written.
        for status in FieldUpdateResult:
            color_info = self.__config_mgr.get_field_color_info_from_status(status)
            output_values.append([color_info[0], FIELD_UPDATE_COLOR_MAP[status]])
            if (color_info[1] is not None):
                output_colors.append([0, row_index, color_info[1]])
            row_index += 1

        color_info = self.__config_mgr.get_left_record_not_found_color_info()
        output_values.append([color_info[0], "Matching " + left_name + " item not found"])
        output_colors.append([0, row_index, color_info[1]])
        row_index += 1
        color_info = self.__config_mgr.get_right_record_not_found_color_info()
        output_values.append([color_info[0], "Matching " + right_name + " item not found"])
        output_colors.append([0, row_index, color_info[1]])
        row_index += 1

        output_values.append(["", ""])

        row_index = len(output_values)
        output_bold.append([0, row_index])
        output_bold.append([1, row_index])

        for row in user_input_info:
            output_values.append(row)

        return {self.__swi.SHEET_NAME_KEY: "Legend",
                self.__swi.VALUES_KEY: output_values,
                self.__swi.COLORS_KEY: output_colors,
                self.__swi.BOLD_KEY: output_bold,
                self.__swi.COLUMN_WIDTHS_KEY: [[0, 16], [1, 40]]}
