import pandasql as ps
import seaborn as sb
import matplotlib.pyplot as plt


class KdeBuilder:
    def __init__(self, dataset, param, filter_expr='1=1'):
        self.param = param  # Temperature or M
        self.filter_expr = filter_expr
        self.dataset = ps.sqldf(f"select * from dataset where {filter_expr}", locals())
        self.obs_dataset = self.__generate_obs(self.dataset)

    def __generate_obs(self, dataset):
        query = f'select 50 as h, {self.param}50 as value from dataset '
        for i in range(55, 95, 5):
            query = query + f' union all select {i} as h, {self.param}{i} as value from dataset '
        return ps.sqldf(query, locals())

    def create_plot(self, file, x_label=None, y_label='Высота, км'):
        ax = sb.kdeplot(self.obs_dataset.value, self.obs_dataset.h,
                        kernel="gau", cmap="Reds", shade=True, shade_lowest=False)
        if self.param == 'Temperature':
            plt.xlim(200, 300)
        plt.ylim(50, 90)
        if x_label:
            ax.set_xlabel(x_label)
        else:
            ax.set_xlabel({
                              'Temperature': 'Temperature, K',
                              'M': 'Ln(M) * 10^14 см^(-3)'
                          }[self.param])
        ax.set_ylabel(y_label)
        means = self.dataset.mean()
        stds = self.dataset.std()
        mean = getattr(means, f'{self.param}50')
        std = getattr(stds, f'{self.param}50')

        plt.axvline(x=mean, ymin=0, ymax=0.03125)
        plt.axvline(x=mean - std, ymin=0, ymax=0.03125, linestyle='--')
        plt.axvline(x=mean + std, ymin=0, ymax=0.03125, linestyle='--')
        for i in range(7):
            mean = getattr(means, f'{self.param}{55 + (5 * i)}')
            std = getattr(stds, f'{self.param}{55 + (5 * i)}')

            plt.axvline(mean, ymin=0.03125 + (0.125 * i), ymax=0.03125 + (0.125 * (i + 1)))
            plt.axvline(mean - std, ymin=0.03125 + (0.125 * i), ymax=0.03125 + (0.125 * (i + 1)), linestyle='--')
            plt.axvline(mean + std, ymin=0.03125 + (0.125 * i), ymax=0.03125 + (0.125 * (i + 1)), linestyle='--')

        mean = getattr(means, f'{self.param}90')
        std = getattr(stds, f'{self.param}90')
        plt.axvline(x=mean, ymin=0.96875, ymax=1)
        plt.axvline(x=mean - std, ymin=0.96875, ymax=1, linestyle='--')
        plt.axvline(x=mean + std, ymin=0.96875, ymax=1, linestyle='--')
        plt.savefig(file)