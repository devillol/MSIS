import matplotlib.pyplot as plt
from python_code.create_dataset import create_dataset
import argparse


def create_data_hist(param):
    df = create_dataset('data/data.mat', 'Temperature').groupby(param).size()
    xy = [(val, df[val]) for val in df.keys()]
    x, y = zip(*xy)

    _, ax = plt.subplots()
    ax.bar(x, y, align='center')
    ax.set_ylabel('num observations')
    ax.set_xlabel(param)
    plt.savefig(f'images/data_{param}.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--param', required=True)
    args = parser.parse_args()
    create_data_hist(args.param)
