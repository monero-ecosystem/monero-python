#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    readme = f.read()

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name = "monero-python",
    version = "0.0.1",
    description = "A comprehensive Python module for handling the Monero cryptocurrency.",
    long_description=readme,
    url = "https://github.com/emesik/monero-python",
    keywords = "monero",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD 3-Clause License"
    ],
    license = "BSD-3-Clause"
)
