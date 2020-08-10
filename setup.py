from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='MSIS',
    version='1.0',
    packages=['python_code'],
    package_data={'MSIS': ['*', '*/*']},
    long_description=open(join(dirname(__file__), 'README.md')).read()
)