# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

version = __import__('monero').__version__

setup(
    name = 'monero-python',
    version = version,
    description = 'A comprehensive Python module for handling Monero cryptocurrency',
    url = 'https://github.com/emesik/monero-python/',
    long_description = open('README.rst').read(),
    install_requires = open('requirements.txt', 'r').read().splitlines(),
    packages = find_packages('.', exclude=['tests']),
    include_package_data = True,
    author = 'Michał Sałaban',
    author_email = 'michal@salaban.info',
    license = 'BSD-3-Clause',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords = 'monero cryptocurrency',
    test_suite='tests',
)
