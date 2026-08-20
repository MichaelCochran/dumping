'''
----------------------------------------------------------------------------
Library   : velociraptor
Package   : velociraptor.interfaces
Class     : SheetWriterInterface.py
Engineers : Steve Schifris
Abstract  : This class provides an interface to write workbook spreadsheets.
            The implementation relies heavily on pandas.ExcelWriter.
            For more info, see
            https://pandas.pydata.org/docs/reference/api/pandas.ExcelWriter.html.
            Also see https://openpyxl.readthedocs.io/en/stable/ amd
              https://realpython.com/openpyxl-excel-spreadsheets-python.
----------------------------------------------------------------------------
'''

import string
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import PatternFill, Font
from openpyxl.styles.borders import Border, Side, BORDER_MEDIUM
from openpyxl.comments import Comment

from velociraptor.types.config_manager import ConfigManager

# Sheet is short for Spreadsheet. This interface enables reading from and writing to spreadsheets.
class SheetWriterInterface:

    # Each sheet uses these keys in a map; sheet name and value are required; others are optional
    SHEET_NAME_KEY = "sheetName"
    VALUES_KEY = "values"       # list of rows which is each a list of field values
    HEADERS_KEY = "headers"     # None or list of column headers
    COLORS_KEY = "colors"       # None or list of [col, row, color] where col & row are zero-based
    BOLD_KEY = "bold"           # None or list of [col, row] (zero-based)
    COMMENTS_KEY = "comments"   # None or list of [col, row, comment] (zero-based)
    COLUMN_WIDTHS_KEY = "column_widths" # None or list of tuple[column index, width] (zero-based)
    HAS_FILTER = "has_filter"   # True or False; defaults to False & only applies if headers exist
    FREEZE_TOP_ROW = "freeze"   # True or False, defaults to False & only applies if headers exist
    HIDDEN_COLS_KEY = "hidden_columns"  # None or list of column indexes (zero-based)
    BORDERS_KEY = "borders"     # None or list of [col, row] where col & row are zero-based
    NUMBER_FORMATS_KEY = "number_formats" # None or list of tuple[column index, number format] (zero-based)

    def __init__(self, config_mgr: ConfigManager):
        self._config_mgr = config_mgr

    # Returns the Excel cell ID associated with colIndex and rowIndex.
    # All indexes are zero-based while Excel rows are one-based and columns are letter-based,
    # so col 0, row 0 returns A1; 0,1 returns A2; 1,2 returns B3; etc.
    def get_cell_id(self, col_index, row_index):
        col_num = col_index + 1
        col_id = ""
        while col_num > 0:
            last_index = int((col_num - 1) % 26)
            col_id = string.ascii_uppercase[last_index] + col_id
            if (col_num <= 26):
                col_num = 0
            else: col_num = int((col_num - last_index - 1) / 26)
        return col_id + str(row_index + 1)


    # userInputInfo is a 2D list of rows/cols with user inputs that will be included in the output file for reference.
    # fileName is the base fileName to which a date/time prefix and .xlsx extension will be added.
    # sheetList is a list of maps each containing the 5 _KEY values listed near the top of the file, specifically
    # each sheet consists of:
    # * name: string name of the spreadsheet within the workbook
    # * headers: list of string column headers
    # * values: 2-D list of rows and columns for each cell within each row
    # * colors: list of lists where each row consists of column index, row index, and color  #TODO is this right?
    # * comments: same as colors but each commens is itself a list of the comment text and user name ("velociraptor")
    # Note: Colors and comments column and row indexes are zero-based, so 0,0 is cell A1 in Excel.
    def create_output_workbook(self, sheet_file_path, sheet_list):

        writer = pd.ExcelWriter(sheet_file_path, engine='openpyxl')

        for sheet_map in sheet_list:
            sheet_name = sheet_map[self.SHEET_NAME_KEY]
            values = sheet_map[self.VALUES_KEY]
            headers = sheet_map.get(self.HEADERS_KEY)
            colors = sheet_map.get(self.COLORS_KEY)
            bold = sheet_map.get(self.BOLD_KEY)
            comments = sheet_map.get(self.COMMENTS_KEY)
            column_widths = sheet_map.get(self.COLUMN_WIDTHS_KEY)
            has_filter = sheet_map.get(self.HAS_FILTER)
            freeze = sheet_map.get(self.FREEZE_TOP_ROW)
            hidden_columns = sheet_map.get(self.HIDDEN_COLS_KEY)
            borders = sheet_map.get(self.BORDERS_KEY)
            number_formats = sheet_map.get(self.NUMBER_FORMATS_KEY)

            if (headers is not None and len(headers) > 0):
                df = pd.DataFrame(values, columns=headers)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                df = pd.DataFrame(values)
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

            sheet: Worksheet = writer.sheets[sheet_name]

            if headers is not None and len(headers) > 0:
                if freeze:
                    sheet.freeze_panes ="A2"
                if has_filter:
                    sheet.auto_filter.ref = sheet.dimensions

            if colors is not None:
                for c in colors:
                    cell_id = self.get_cell_id(c[0], c[1])
                    sheet[cell_id].fill = PatternFill("solid", c[2])

            if bold is not None:
                bold_font = Font(bold=True)
                for b in bold:
                    cell_id = self.get_cell_id(b[0], b[1])
                    sheet[cell_id].font = bold_font

            if comments is not None:
                for c in comments:
                    cell_id = self.get_cell_id(c[0], c[1])
                    sheet[cell_id].comment = Comment(c[2], "Velociraptor")

            if column_widths is not None:
                for w in column_widths:
                    cell_id = self.get_cell_id(w[0], 0)
                    column_id = cell_id[:-1]  # strip off the row number in the last character
                    sheet.column_dimensions[column_id].width = w[1]

            if hidden_columns is not None:
                for h in hidden_columns:
                    cell_id = self.get_cell_id(h, 0)
                    column_id = cell_id[:-1]  # strip off the row number in the last character
                    sheet.column_dimensions[column_id].hidden = True

            if borders is not None:
                thin_border = Border(
                    left=Side(border_style=BORDER_MEDIUM, color='00000000'),
                    right=Side(border_style=BORDER_MEDIUM, color='00000000'),
                    top=Side(border_style=BORDER_MEDIUM, color='00000000'),
                    bottom=Side(border_style=BORDER_MEDIUM, color='00000000')
                )
                for b in borders:
                    cell_id = self.get_cell_id(b[0], b[1])
                    sheet[cell_id].border = thin_border

            if number_formats is not None:
                for n in number_formats:
                    cell_id = self.get_cell_id(n[0], 0)
                    column_id = cell_id[:-1]  # strip off the row number in the last character
                    # Must iterate through each cell due to limitation of the Excel file format:
                    # https://openpyxl.readthedocs.io/en/stable/styles.html
                    for cell in sheet[column_id]:
                        cell.number_format = n[1]

        writer.close()
