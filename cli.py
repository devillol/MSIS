import click
from python_code.kde_builder import KdeBuilder


@click.command()
@click.argument('param')
@click.option('--season')
@click.option('--region')
@click.option('--sza')
@click.option('--f107')
# "season='зима' and region='полярные' and SZA='день' and F107='низкая солнечная активность'"
def main(param, **kwargs):
    if param.upper() in ['T', 'TEMPERATURE']:
        param = 'Temperature'
    else:
        if param != 'M':
            print(f'unknown parameter {param}')
            exit(1)

    kde_builder = KdeBuilder(mat_file='data/data.mat', param=param, **kwargs)
    print(f'count of observations: {kde_builder.obs_count}')

    image_name = f'images/{param}-{"-".join([value for value in kwargs.values() if value])}.png'
    kde_builder.create_plot(image_name)


if __name__ == '__main__':
    main()
