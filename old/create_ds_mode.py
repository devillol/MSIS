import scipy.constants as cs
import pandas as pd
import pandasql as ps
import numpy as np
conditions = pd.read_csv('Conditions.csv', sep=',', header=None,
                      names=['year', 'month', 'day', 'hh', 'mm', 'shirota', 'dolg', 'SZA', 'F107', 'Ap'])
T = pd.read_csv('Temperature.csv', sep=',', header=None,
                names=['T50', 'T55', 'T60', 'T65', 'T70', 'T75', 'T80', 'T85', 'T90'])
P = pd.read_csv('Pressure.csv', sep=',', header=None,
                names=['P50', 'P55', 'P60', 'P65', 'P70', 'P75', 'P80', 'P85', 'P90'])
summary = conditions.join(T).join(P).dropna()
for i in range(50, 95, 5):
    summary['P{}'.format(str(i))] = np.log(summary['P{}'.format(str(i))]/(summary['T{}'.format(str(i))] * cs.k) * 10**(-6) \
                                    * 10**(-14))

query = '''
    select 
    case when month in (12)
            then 'зима'
        when month in (3) 
             then 'весна'
        when month in (6) 
             then 'лето'
        when month in (9)
             then 'осень'
    end season
    , case when abs(shirota) > 60 then 'полярные'
          when abs(shirota) < 30 then 'экваториальные'
         when abs(shirota) >=30 and abs(shirota) <= 60 then 'средние'
    end region
    , case when F107 < 110 then 'низкая солнечная активность'
        when F107 > 150 then 'высокая солнечная активность'
        when F107 >=110 and F107 <=150 then 'средняя солнечная активность'
    end F107
    , case when SZA < 60 then 'день'
        when SZA > 100 then 'ночь'
    end SZA
    ,T50, T55, T60, T65, T70, T75, T80, T85, T90
    ,P50 as N50, P55  as N55, P60 as N60, P65 as N65 
    ,P70 as N70, P75 as N75, P80 as N80, P85 as N85, P90 as N90
    from summary
    where
         F107 is not null
        and SZA is not null
        and shirota is not null
        and month is not null
        and Ap <= 9
    '''
T = ps.sqldf(query, locals())
T.to_csv('all_obs.csv', index=False)