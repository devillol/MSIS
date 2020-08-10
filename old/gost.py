import scipy.io as sio
import pandas as pd
import pandasql as ps
import matplotlib.pyplot as plt
import seaborn as sb

import matplotlib.colors as col
import numpy as np
import xlwt

all_obs = pd.read_csv('all_obs.csv')
filteredDs = all_obs[(all_obs.region == 'экваториальные') &
                     (all_obs.season == 'лето')  & (all_obs.SZA == 'день') & (all_obs.F107 == 'низкая солнечная активность')]


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
Teor = []
f = open('noaa.txt')
for line in f:
    Teor.append(float(line))

plt.axvline(x=Teor[0], ymin=0, ymax=0.03125)

for i in range(7):
    plt.axvline(Teor[i + 1], ymin=0.03125+(0.125*i), ymax=0.03125+(0.125*(i + 1)))

plt.axvline(x=Teor[8], ymin=0.96875, ymax=1)
plt.show()