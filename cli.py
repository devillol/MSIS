import click
from python_code.kde_builder import KdeBuilder
from python_code.create_dataset import check_param
from pathlib import Path
import logging

@click.command()
@click.argument('param')
@click.option('--log-level', '-log', default='WARN')
@click.option('--y-param', '-y', default='h')
@click.option('--season')
@click.option('--region')
@click.option('--sza')
@click.option('--f107')
def main(param, log_level, y_param, **kwargs):
    """
    cli-утилита для запуска кода
    """
    __log_level = logging.getLevelName(log_level)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=__log_level)

    kde_builder = KdeBuilder(mat_file='data/data.mat', param=param, **kwargs)

    image_name = f'{Path(__file__).parent.absolute()}/images/by_{y_param}/{param}-'\
                 f'{"-".join([value for value in kwargs.values() if value])}.png'
    kde_builder.create_heatmap(image_name, y_param=y_param, add_avg_std=(y_param == 'h'))
    print(f'count of observations: {kde_builder.obs_count}')


if __name__ == '__main__':
    main()
