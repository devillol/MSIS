import scipy.constants as cs
import scipy.io
from pandas import DataFrame
import pandasql as ps
import numpy as np
from jinja2 import Template


def create_dataset(mat_file: str, param: str, filter_expr='1 = 1') -> DataFrame:
    """
    Функция, генерирующая из .mat-файла датафрэйм для параметра, отбирая записи по условию
    :param mat_file: путь к .mat файлу
    :param param: какой параметр считаем (Temperature или M)
    :param filter_expr: условие
    :return: DataFrame
    """
    source_data = scipy.io.loadmat(mat_file)
    t_names = [f'Temperature{i}' for i in range(50, 95, 5)]
    m_names = [f'M{i}' for i in range(50, 95, 5)]

    T = DataFrame(source_data['Temperature'],
                  columns=t_names)
    P = DataFrame(source_data['Pressure'],
                  columns=m_names)
    conditions = DataFrame(source_data['Conditions'],
                           columns=['year', 'month', 'day', 'hh', 'mm', 'shirota', 'dolg', 'SZA', 'F107', 'Ap'])

    summary = conditions.join(T).dropna() if param == 'Temperature' else conditions.join(T).join(P).dropna()

    if param == 'M':
        for i in range(50, 95, 5):
            summary[f'M{i}'] = np.log(
                summary[f'M{i}'] / (summary[f'Temperature{i}'] * cs.k) * 10 ** (-6) * 10 ** (-14))

    query = Template('''
    select * from (
    select 
    case when month in (11, 12, 1) and shirota > 0 
            or month in (5, 6, 7) and shirota < 0 then 'зима'
        when month in (2, 3, 4) and shirota > 0
            or month in (8, 9, 10) and shirota < 0 then 'весна'
        when month in (5, 6, 7) and shirota > 0 
            or month in (11, 12, 1) and shirota < 0 then 'лето'
        when month in (8, 9, 10) and shirota > 0
            or month in (2, 3, 4) and shirota < 0 then 'осень'
    end season
    , case when abs(shirota) > 60 then 'полярные'
          when abs(shirota) < 30 then 'экваториальные'
         else 'средние'
    end region
    , case when F107 < 100 then 'низкаяСА'
        when F107 > 150 then 'высокаяСА'
        else 'средняяСА'
    end F107
    , case when SZA < 60 then 'день'
        when SZA > 100 then 'ночь'
        else 'сумерки'
    end SZA
    {%- for col_name in column_names %}
    , {{col_name}}
    {%- endfor %}
    from summary
    ) t where {{filter_query}}
    ''').render(column_names=t_names if param == 'Temperature' else m_names,
                filter_query=filter_expr)
    return ps.sqldf(query, locals())
