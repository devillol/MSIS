from python_code.create_dataset import create_dataset
from python_code.kde_builder import KdeBuilder

data = create_dataset('data/data.mat')
kde_builder = KdeBuilder(data, 'M', "season='лето' and region='средние' and SZA='день' and F107='низкая солнечная активность'")
kde_builder.create_plot('images/M-лето-средние-день-низкаяСА.png')
