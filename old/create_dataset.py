import scipy.constants as cs
import pandas as pd
import pandasql as ps
import numpy as np
conditions = pd.read_csv('Conditions.csv', sep=',', header=None,
                      names=['year', 'month', 'day', 'hh', 'mm', 'shirota', 'dolg', 'SZA', 'F107', 'Ap'])

t_names = [f'Temperature{i}' for i in range(50, 95, 5)]
n_names = [f'N{i}' for i in range(50, 95, 5)]
T = pd.read_csv('Temperature.csv', sep=',', header=None,
                names=t_names)
P = pd.read_csv('Pressure.csv', sep=',', header=None,
                names=n_names)
summary = conditions.join(T).join(P).dropna()
for i in range(50, 95, 5):
    summary['P{}'.format(str(i))] = np.log(summary['P{}'.format(str(i))]/(summary['T{}'.format(str(i))] * cs.k) * 10**(-6))

query = f'''
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
    end SZA'''

for t in t_names:
    query = query + f', {t}'
for n in n_names:
        query = query + f', {p}'
    query = query + '''
    from summary
    where
         F107 is not null
        and SZA is not null
        and shirota is not null
        and month is not null
    '''
T = ps.sqldf(query, locals())
T.to_csv('all_obs.csv', index=False)



