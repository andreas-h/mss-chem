from setuptools import setup

VERSION = '0.1'


def write_version_py(filename='msschem/_version.py'):
    with open(filename, 'w') as fd:
        fd.write('__version__ = {}'.format(VERSION))


# TODO update setup metadata
# FIXME check installation with pip

setup(
    name = 'mss-chem',
    version = VERSION,
    author = 'Andreas Hilboll',
    author_email = 'hilboll@uni-bremen.de',
    description = ('CTM pre-processor for mss'),
    license = 'MIT',
    keywords = 'mss ctm forecast',
    url = 'http://mss-chem.readthedocs.io/',
    packages=['msschem', 'tests'],
    long_description=open('README.rst').read(),
    classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Topic :: Scientific/Engineering :: Atmospheric Science',
            'License :: OSI Approved :: MIT License',
    ],
    install_requires=['netCDF4', 'numpy', 'pandas'],
    entry_points=dict(
        console_scripts=['msschem-dl = msschem.runner:main'],
    ),
)
