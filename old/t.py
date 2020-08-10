import scipy.io as sio
import pandas as pd
import pandasql as ps
import matplotlib.pyplot as plt
import seaborn as sb

import matplotlib.colors as col
import numpy as np
import xlwt

all_obs = pd.read_csv('all_obs.csv')
filteredDs = all_obs[(all_obs.region == 'полярные') &
                     (all_obs.season == 'зима')  & (all_obs.SZA == 'ночь') & (all_obs.F107 == 'средняя солнечная активность')]


def generateQueryObs(param,ds, rename_param='F'):
    queryTemp = 'select 50 as h, {}50 as {} from {} '.format(param, rename_param, ds)
    for i in range(55, 95, 5):
        queryTemp = queryTemp + ' union all select {0} as h, {1}{0} as {2} from {3} '.format(i, param, rename_param, ds)
    return queryTemp


query = generateQueryObs('T', 'filteredDs', 'Temp')
T_list = ps.sqldf(query, locals())

ax = sb.kdeplot(T_list.Temp, T_list.h, shade=True, cbar=True, shade_lowest=False, cmap="Reds")
plt.xlim(200, 300)
plt.ylim(50, 90)
ax.set_xlabel('Температура, К')
ax.set_ylabel('Высота, км')

T_means = filteredDs.mean()
T_std = filteredDs.std()
mean = T_means.T50
std = T_std.T50
plt.axvline(x=mean, ymin=0, ymax=0.03125)
plt.axvline(x=mean - std, ymin=0, ymax=0.03125, linestyle='--')
plt.axvline(x=mean + std, ymin=0, ymax=0.03125, linestyle='--')
for i in range(7):
    mean = T_means['T{}'.format(55 + (5 * i))]
    std = T_std['T{}'.format(55 + (5 * i))]
    plt.axvline(mean, ymin=0.03125+(0.125*i), ymax=0.03125+(0.125*(i + 1)))
    plt.axvline(mean - std, ymin=0.03125 + (0.125 * i), ymax=0.03125 + (0.125 * (i + 1)), linestyle='--')
    plt.axvline(mean + std, ymin=0.03125 + (0.125 * i), ymax=0.03125 + (0.125 * (i + 1)), linestyle='--')
mean = T_means.T90
std = T_std.T90
plt.axvline(x=mean, ymin=0.96875, ymax=1)
plt.axvline(x=mean - std, ymin=0.96875, ymax=1, linestyle='--')
plt.axvline(x=mean + std, ymin=0.96875, ymax=1, linestyle='--')
plt.show()

