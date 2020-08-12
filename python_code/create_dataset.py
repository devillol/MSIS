import scipy.constants as cs
import scipy.io
import pandas as pd
import pandasql as ps
import numpy as np


def create_dataset(mat_file):
    source_data = scipy.io.loadmat(mat_file)
    t_names = [f'Temperature{i}' for i in range(50, 95, 5)]
    m_names = [f'M{i}' for i in range(50, 95, 5)]

    T = pd.DataFrame(source_data['Temperature'],
                     columns=t_names)
    P = pd.DataFrame(source_data['Pressure'],
                     columns=m_names)
    conditions = pd.DataFrame(source_data['Conditions'],
                              columns=['year', 'month', 'day', 'hh', 'mm', 'shirota', 'dolg', 'SZA', 'F107', 'Ap'])

    summary = conditions.join(T).join(P).dropna()

    for i in range(50, 95, 5):
        summary[f'M{i}'] = np.log(
            summary[f'M{i}'] / (summary[f'Temperature{i}'] * cs.k) * 10 ** (-6) * 10 ** (-14))

    query = '''
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
    , case when F107 < 110 then 'низкая солнечная активность'
        when F107 > 150 then 'высокая солнечная активность'
        else 'средняя солнечная активность'
    end F107
    , case when SZA < 60 then 'день'
        when SZA > 100 then 'ночь'
        else 'сумерки'
    end SZA
    '''
    for t in t_names:
        query = query + f', {t}'
    for m in m_names:
        query = query + f', {m}'
    query = query + '''
    from summary
    where
         F107 is not null
        and SZA is not null
        and shirota is not null
        and month is not null
    '''
    return ps.sqldf(query, locals())
