import pandasql as ps
from pandas import DataFrame
import seaborn as sb
import matplotlib.pyplot as plt
from python_code.create_dataset import create_dataset
from pathlib import Path
import logging


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
        _SQL_FILES_BY_PARAM = {'h': f'{Path(__file__).parent.parent.absolute()}/sql/grouped.sql',
                               'latitude': f'{Path(__file__).parent.parent.absolute()}/sql/by_latitude.sql',
                               'month': f'{Path(__file__).parent.parent.absolute()}/sql/by_months.sql'}
        df = create_dataset(mat_file=self.__mat_file, param=self.__param,
                            sql_file_path=_SQL_FILES_BY_PARAM[y_param],
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

    def create_heatmap(self, image_file: str, y_param='h', y_lims=None, x_label=None, y_label=None, plt_tittle=None,
                       add_avg_std=False):
        """
        Метод, строящий график
        :param plt_tittle:
        :param y_param:
        :param y_lims:
        :param add_avg_std:
        :param image_file: куда сохранять файл
        :param x_label: подпись оси x
        :param y_label: подпись оси y
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
        fig.suptitle(
            f'{self.__param} \n {self.__options} \n {self.obs_count} observations'
            if not plt_tittle else f'{plt_tittle} \n {self.obs_count} observations', fontsize=20)

        sb.heatmap(normed_data, cmap="viridis", ax=ax[0])
        ax[0].invert_yaxis()

        ax[1].plot(aggregates['y'], aggregates['average'], label='average')
        ax[1].plot(aggregates['y'], aggregates['possible'], label='possible')

        _VAL_NAMES_BY_PARAM = {
            'T': 'Temperature, K',
            'M': 'Ln(M) * 10^14 см^(-3)'
        }
        _Y_NAMES_BY_PARAM = {
            'h': 'Высота, км',
            'latitude': 'Широта, deg',
            'month': 'Месяц'
        }
        ax[0].set_xlabel(_VAL_NAMES_BY_PARAM[self.__param[0]] if not x_label else x_label)
        ax[0].set_ylabel(_Y_NAMES_BY_PARAM[y_param] if not y_label else y_label)
        ax[1].set_xlabel(_Y_NAMES_BY_PARAM[y_param] if not y_label else y_label)
        ax[1].set_ylabel(_VAL_NAMES_BY_PARAM[self.__param[0]] if not x_label else x_label)

        """
        if y_param == 'h' and add_avg_std:
            self.__add_avg_std()"""
        plt.grid()
        plt.legend()

        plt.savefig(image_file,bbox_inches='tight', dpi=100)
        plt.close()

    def __add_avg_std(self):
        # разные цвета, чтобы различать легенды
        colors = ['g', 'b', 'm', 'y', 'aqua', 'orange', 'midnightblue', 'lime', 'olive']

        # до какого знака округляем mean и std
        n = 1 if self.__param == 'Temperature' else 4

        # для каждой высоты (с шагом 5 км) считаем mean и std
        means = self.means
        stds = self.stds
        mean = getattr(means, f'{self.__param}50')
        std = getattr(stds, f'{self.__param}50')

        plt.axvline(x=mean, ymin=0, ymax=0.03125,
                    label=f'h={50}\n mean={round(mean, n)}\n std={round(std, n)}', color=colors[0])
        plt.axvline(x=mean - std, ymin=0, ymax=0.03125, color=colors[0], linestyle='--')
        plt.axvline(x=mean + std, ymin=0, ymax=0.03125, color=colors[0], linestyle='--')
        for i in range(7):
            mean = getattr(means, f'{self.__param}{55 + (5 * i)}')
            std = getattr(stds, f'{self.__param}{55 + (5 * i)}')

            plt.axvline(mean, ymin=0.03125 + (0.125 * i), ymax=0.03125 + (0.125 * (i + 1)),
                        label=f'h={55 + (5 * i)}\n mean={round(mean, n)}\n std={round(std, n)}', color=colors[i + 1])
            plt.axvline(mean - std, ymin=0.03125 + (0.125 * i), ymax=0.03125 + (0.125 * (i + 1)),
                        color=colors[i + 1], linestyle='--')
            plt.axvline(mean + std, ymin=0.03125 + (0.125 * i), ymax=0.03125 + (0.125 * (i + 1)),
                        color=colors[i + 1], linestyle='--')

        mean = getattr(means, f'{self.__param}90')
        std = getattr(stds, f'{self.__param}90')
        plt.axvline(x=mean, ymin=0.96875, ymax=1,
                    label=f'h=90\n mean={round(mean, n)}\n std={round(std, n)}', color=colors[8])
        plt.axvline(x=mean - std, ymin=0.96875, ymax=1, color=colors[8], linestyle='--')
        plt.axvline(x=mean + std, ymin=0.96875, ymax=1, color=colors[8], linestyle='--')
