import os
from setuptools import setup

setup(
    name = 'mss-chem',
    version = '0.0.1dev',
    author = 'Andreas Hilboll',
    author_email = 'hilboll@uni-bremen.de',
    description = ('CTM pre-processor for mss'),
    license = 'BSD',
    keywords = 'mss ctm forecast',
    url = 'http://mss-chem.readthedocs.io/',
    packages=['msschem', 'tests'],
    long_description=open('README.rst').read(),
    classifiers=[
            'Development Status :: 3 - Alpha',
            'Topic :: Scientific/Engineering :: Atmospheric Science',
            'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
            'netCDF4',
    ],
)
