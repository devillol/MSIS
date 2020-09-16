import pandasql as ps
from pandas import DataFrame
import seaborn as sb
import matplotlib.pyplot as plt
from python_code.create_dataset import create_dataset


class KdeBuilder:
    """
    Класс для визуализации данных
    """

    def __init__(self, mat_file, param, **kwargs):
        self.__param = param  # Temperature or M
        self.__options = ','.join([value for value in kwargs.values() if value])  # условия фильтра
        self.__filter_expr = ' and '.join(
            [f"{key}='{value}'" for key, value in kwargs.items() if value])
        if not self.__filter_expr:
            self.__filter_expr = '1 = 1'
        # фильтруем данные
        self.__dataset = create_dataset(mat_file=mat_file, param=self.__param, filter_expr=self.__filter_expr)
        self.__obs_dataset = self.__generate_obs(self.__dataset)

    def __generate_obs(self, df: DataFrame) -> DataFrame:
        """
        Метод, герирующий датафрэйм из строчек высота-параметр
        :param df: фрэйм из строчек вида условия,параметр50-параметр90
        :return:
        """
        query = f'select 50 as h, {self.__param}50 as value from df '
        for i in range(55, 95, 5):
            query = query + f' union all select {i} as h, {self.__param}{i} as value from df '
        return ps.sqldf(query, locals())

    @property
    def obs_count(self):
        """
        :return: число наблюдений
        """
        return len(self.__dataset.index)

    def create_plot(self, file, x_label=None, y_label='Высота, км'):
        """
        Метод, строящий график
        :param file: куда сохранять файл
        :param x_label: подпись оси x
        :param y_label: подпись оси y
        :return:
        """
        ax = sb.kdeplot(self.__obs_dataset.value, self.__obs_dataset.h,
                        kernel="gau", cmap="Reds", cbar=True, shade=True, shade_lowest=False)
        if self.__param == 'Temperature':
            plt.xlim(200, 300)
        plt.ylim(50, 90)
        plt.title(f'{self.__param} \n {self.__options} \n {self.obs_count} observations')
        if x_label:
            ax.set_xlabel(x_label)
        else:
            ax.set_xlabel({
                              'Temperature': 'Temperature, K',
                              'M': 'Ln(M) * 10^14 см^(-3)'
                          }[self.__param])
        ax.set_ylabel(y_label)

        # разные цвета, чтобы различать легенды
        colors = ['g', 'b', 'm', 'y', 'aqua', 'orange', 'midnightblue', 'lime', 'olive']

        # до какого знака округляем mean и std
        n = 1 if self.__param == 'Temperature' else 4

        # для каждой высоты (с шагом 5 км) считаем mean и std
        means = self.__dataset.mean()
        stds = self.__dataset.std()
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
        plt.legend(loc='center left', bbox_to_anchor=(1.4, 0.5))
        plt.savefig(file, bbox_inches="tight")
