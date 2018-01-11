import pandas as pd
import xlrd
from datetime import datetime


def read_excel_create_array(data_source2):
    """
    获取建仓日的矩阵
    :return: array
    """
    return pd.read_excel(data_source2, 'Sheet1', index_col=None)


def get_excel_date(data_source1):
    """
    获取全部交易日期
    :return: list
    """
    date_list = []
    book = xlrd.open_workbook(data_source1)
    sheet_1 = book.sheet_by_name('Sheet1')
    for cell in sheet_1.row(0):
        date_list.append(datetime(*xlrd.xldate_as_tuple(cell.value, 0)).strftime('%Y-%m-%d'))
    return date_list


def get_create_day(data_source2):
    """
    获取建仓日
    :return: list
    """
    date_list = []
    book = xlrd.open_workbook(data_source2)
    sheet_1 = book.sheet_by_name('Sheet1')
    for cell in sheet_1.row(0):
        date_list.append(datetime(*xlrd.xldate_as_tuple(cell.value, 0)).strftime('%Y-%m-%d'))
    return date_list
