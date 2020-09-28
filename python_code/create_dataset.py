import scipy.constants as cs
import scipy.io
from pandas import DataFrame
import pandasql as ps
import numpy as np
import re
import logging
from jinja2 import Template


def check_param(param: str):
    pattern = re.compile('[T,M](([5-8][05])|(90))?$')
    if not pattern.match(param):
        logging.error(f'UNKNOWN PARAM {param}')
        exit(100)


def create_dataset(mat_file: str, param: str, sql_file_path: str, **kwargs) -> DataFrame:
    """
    Функция, генерирующая из .mat-файла датафрэйм для параметра, отбирая записи по условию
    :param mat_file: путь к .mat файлу
    :param param: какой параметр считаем (T или M)
    :param sql_file_path: путь к sql файлу
    :return: DataFrame
    """
    check_param(param)

    _T_NAMES = [f'T{i}' for i in range(50, 95, 5)]
    _M_NAMES = [f'M{i}' for i in range(50, 95, 5)]
    _CONDITIONS = ['year', 'month', 'day', 'hh', 'mm', 'latitude', 'longitude', 'SZA', 'F107', 'Ap']

    source_data = scipy.io.loadmat(mat_file)
    column_names = locals()[f'_{param}_NAMES'].copy() if len(param) == 1 else [param]
    logging.info(column_names)

    T = DataFrame(source_data['Temperature'], columns=_T_NAMES)
    P = DataFrame(source_data['Pressure'], columns=_M_NAMES)
    conditions = DataFrame(source_data['Conditions'], columns=_CONDITIONS)

    summary = conditions.join(T).dropna()
    logging.info(summary)

    if param[0] == 'M':
        summary = summary.join(P).dropna()
        logging.info(summary)
        for t, m in zip(_T_NAMES, _M_NAMES):
            summary[m] = np.log10(
                summary[m] / (summary[t] * cs.k) * 10 ** (-6))
        logging.info(summary)

    with open(sql_file_path, 'r') as sql_file:
        __query = Template(sql_file.read()).render(column_names=column_names,
                                                   n_round=0 if param[0] == 'T' else 2,
                                                   **kwargs)
        return ps.sqldf(__query, locals())
