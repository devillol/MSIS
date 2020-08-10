from python_code.create_dataset import create_dataset
from python_code.kde_builder import KdeBuilder

data = create_dataset('data/data.mat')

kde_builder = KdeBuilder(data, 'Temperature', "season='зима' and region='средние' and SZA='день'")
kde_builder.create_plot('images/temperature-зима-средние-день.png')

kde_builder = KdeBuilder(data, 'Temperature', "season='зима' and region='средние' and SZA='ночь'")
kde_builder.create_plot('images/temperature-зима-средние-ночь.png')

kde_builder = KdeBuilder(data, 'Temperature', "season='зима' and region='полярные'")
kde_builder.create_plot('images/temperature-зима-полярные.png')

kde_builder = KdeBuilder(data, 'Temperature', "season='лето' and region='полярные'")
kde_builder.create_plot('images/temperature-лето-полярные.png')
