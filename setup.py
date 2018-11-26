import os
import sys

from setuptools import find_packages, setup

setup(
    name = 'hexrd_shared',
    author = 'HEXRD developers',
    description = 'works in progress related to HEXRD',
    classifiers = [
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        ],
    packages = find_packages(),
    )
