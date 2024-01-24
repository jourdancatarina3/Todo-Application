from setuptools import setup, find_packages

setup(
    name='sileo',
    version='0.0.1',
    packages=find_packages(),
    url='channelfix.com',
    license='commercial property',
    author='Chris Statzer',
    author_email='chris.statzer@gmail.com',
    description='A REST framework for django.',
    install_requires=['django==1.11.22'],
)
