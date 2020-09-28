import pandasql as ps
import pandas as pd
import numpy as np
from pandas import DataFrame
import seaborn as sb
import matplotlib.pyplot as plt
from python_code.create_dataset import create_dataset
from pathlib import Path
import logging

_VAL_NAMES_BY_PARAM = {
    'T': 'Temperature, K',
    'M': 'log(M)'
}
_Y_NAMES_BY_PARAM = {
    'h': 'Высота, км',
    'latitude': 'Широта, deg',
    'month': 'Месяц',
    'sza': 'Зенитный угол, deg',
    'f107': 'f107'
}


class KdeBuilder:
    """
    Класс для визуализации данных
    """

    def __init__(self, mat_file, param, **kwargs):
        self.__mat_file = mat_file
        self.__param = param  # Temperature or M
        self.__options = ','.join([value for value in kwargs.values() if value])  # условия фильтра
        self.__filter_expr = ' and '.join(
            [f"{key}='{value}'" for key, value in kwargs.items() if value])
        if not self.__filter_expr:
            self.__filter_expr = '1 = 1'

        self.__data_count = 0
        self.__means = None
        self.__stds = None

    def __generate_obs(self, y_param: str) -> DataFrame:
        """
        Метод, герирующий датафрэйм из строчек высота-параметр
        :return:
        """
        df = create_dataset(mat_file=self.__mat_file, param=self.__param,
                            sql_file_path=f'{Path(__file__).parent.parent.absolute()}/sql/by_{y_param}.sql',
                            filter_expr=self.__filter_expr)

        logging.info(df)
        self.__data_count = len(df.index)
        self.__means = df.mean()
        self.__stds = df.std()
        return df if y_param != 'h' else self.__generate_obs_for_h(df)

    def __generate_obs_for_h(self, input_df: DataFrame):
        query = f'select 50 as y, {self.__param}50 as value from input_df '
        for i in range(55, 95, 5):
            query = query + f' union all select {i} as y, {self.__param}{i} as value from input_df '
        return ps.sqldf(query, locals())

    @property
    def obs_count(self):
        """
        :return: число наблюдений
        """
        return self.__data_count

    @property
    def means(self):
        return self.__means

    @property
    def stds(self):
        return self.__stds

    def create_plot(self, image_file: str, y_param='h', x_label=None, y_label=None, plt_tittle=None):
        """
        Метод, строящий график распределения плотности вероятности и график  зависимости средних и вероятных
        величин от y_param
        :param image_file: куда сохранять файл
        :return:
        """
        obs_dataset = self.__generate_obs(y_param)
        logging.info(obs_dataset)
        counts_dataset = ps.sqldf("select y, value, cast(count(*) as float) as cnt from obs_dataset "
                                  "group by y, value")
        logging.info(counts_dataset)
        max_counts = counts_dataset.groupby("y").max()
        logging.info(max_counts)
        logging.info(counts_dataset)
        __normed_data = ps.sqldf("select a.y, a.value, a.cnt/b.cnt as cnt from counts_dataset as a "
                                 "left join max_counts b on a.y=b.y "
                                 "order by a.y desc")
        normed_data = __normed_data.pivot_table(index="y", columns="value",
                                                values="cnt",
                                                fill_value=0)

        logging.info(normed_data)

        aggregates = ps.sqldf("select obs.y, avg(obs.value) as average, avg(pos.value) as possible "
                              "from obs_dataset obs "
                              "inner join ("
                              "    select mc.y, cd.value from max_counts mc "
                              "    inner join counts_dataset cd "
                              "    on mc.y = cd.y and mc.cnt = cd.cnt) pos "
                              "on obs.y = pos.y "
                              "group by obs.y "
                              "order by obs.y ")

        logging.info(aggregates)

        fig, ax = plt.subplots(1, 2, gridspec_kw={
            'width_ratios': [2, 1]})
        fig.set_size_inches(20, 10)

        __param_tittle = f'{self.__param[0]} на высоте h = {self.__param[1:]} км' if len(
            self.__param) > 1 else self.__param

        fig.suptitle(f'{__param_tittle} \n {self.__options} \n {self.obs_count} observations'
                     if not plt_tittle else f'{plt_tittle} \n {self.obs_count} observations', fontsize=20)

        sb.heatmap(normed_data, cmap="viridis", ax=ax[0])
        ax[0].invert_yaxis()

        ax[1].plot(aggregates['y'], aggregates['average'], label='average')
        ax[1].plot(aggregates['y'], aggregates['possible'], label='possible')

        ax[0].set_xlabel(_VAL_NAMES_BY_PARAM[self.__param[0]] if not x_label else x_label)
        ax[0].set_ylabel(_Y_NAMES_BY_PARAM[y_param] if not y_label else y_label)
        ax[1].set_xlabel(_Y_NAMES_BY_PARAM[y_param] if not y_label else y_label)
        ax[1].set_ylabel(_VAL_NAMES_BY_PARAM[self.__param[0]] if not x_label else x_label)

        ax[1].minorticks_on()

        #  Определяем внешний вид линий основной сетки:
        ax[1].grid(which='major',
                   color='k')

        #  Определяем внешний вид линий вспомогательной
        #  сетки:
        ax[1].grid(which='minor',
                   color='k',
                   linestyle=':')

        plt.savefig(image_file, bbox_inches='tight', dpi=100)
        plt.close()

    def create_compare_plot(self, datafile, image_file):
        """
        Построение зависимостей от h среднего значения, наиболее вероятного и значения из модели MSIS
        :param datafile: файл с данными MSIS
        :param image_file: куда сохранять
        :return:
        """
        msis_df = pd.read_csv(datafile,
                              names=['h', 'N2', 'O2', 'T'],
                              dtype={'h': float, 'N2': float, 'O2': float, 'T': float})
        msis_df['M'] = np.log10((msis_df['N2'] + msis_df['O2']))
        obs_dataset = self.__generate_obs('h')
        logging.info(obs_dataset)
        counts_dataset = ps.sqldf("select y, value, cast(count(*) as float) as cnt from obs_dataset "
                                  "group by y, value")
        logging.info(counts_dataset)
        max_counts = counts_dataset.groupby("y").max()
        aggregates = ps.sqldf("select obs.y, avg(obs.value) as average, avg(pos.value) as possible "
                              "from obs_dataset obs "
                              "inner join ("
                              "    select mc.y, cd.value from max_counts mc "
                              "    inner join counts_dataset cd "
                              "    on mc.y = cd.y and mc.cnt = cd.cnt) pos "
                              "on obs.y = pos.y "
                              "group by obs.y "
                              "order by obs.y ")
        logging.info(max_counts)

        plt.plot(aggregates['y'], aggregates['average'], label='average')
        plt.plot(aggregates['y'], aggregates['possible'], label='possible')
        plt.plot(msis_df['h'], msis_df[self.__param], label='MSIS')
        plt.title(f'{self.__param} \n {self.__options} \n {self.obs_count} observations')
        plt.xlabel('h, км')
        plt.ylabel(_VAL_NAMES_BY_PARAM[self.__param])
        plt.minorticks_on()

        #  Определяем внешний вид линий основной сетки:
        plt.grid(which='major',
                   color='k')

        #  Определяем внешний вид линий вспомогательной
        #  сетки:
        plt.grid(which='minor',
                   color='k',
                   linestyle=':')
        plt.legend()

        plt.savefig(image_file, bbox_inches='tight', dpi=100)
        plt.close()
