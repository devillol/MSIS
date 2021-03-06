import click
from python_code.kde_builder import KdeBuilder
from pathlib import Path
import logging


@click.command()
@click.argument('param')
@click.option('--log-level', '-log', default='WARN')
@click.option('--y-param', '-y', default='h')
@click.option('--msis', is_flag=True)
@click.option('--season')
@click.option('--region')
@click.option('--sza')
@click.option('--f107')
def main(param, log_level, y_param, msis, **kwargs):
    """
    cli-утилита для запуска кода
    """
    __log_level = logging.getLevelName(log_level)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=__log_level)

    kde_builder = KdeBuilder(mat_file='data/data.mat', param=param, **kwargs)

    name_string = f'{"-".join([value for value in kwargs.values() if value])}'
    if msis:
        kde_builder.create_compare_plot(datafile=f'{Path(__file__).parent.absolute()}'
                                                 f'/data/{name_string}.txt',
                                        image_file=f'{Path(__file__).parent.absolute()}'
                                                   f'/images/msis/{param}-{name_string}.png')
    else:
        image_name = f'{Path(__file__).parent.absolute()}/images/by_{y_param}/{param}-{name_string}.png'

        kde_builder.create_plot(image_name, y_param=y_param)
    print(f'count of observations: {kde_builder.obs_count}')


if __name__ == '__main__':
    main()
