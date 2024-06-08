# -*- coding: utf-8 -*-
import os
import sys
__DIR__ = os.path.abspath(os.path.dirname(__file__))
import codecs
from setuptools import setup
from setuptools.command.test import test as TestCommand
import demeter


def read(filename):
    """Read and return `filename` in root dir of project and return string"""
    return codecs.open(os.path.join(__DIR__, filename), 'r', 'utf-8', errors='ignore').read()


install_requires = read("requirements.txt").split()
long_description = read('README.rst')


setup(
    name="demeter_lib",
    version=demeter.__version__,
    url='https://github.com/shemic/demeter',
    license='MIT License',
    author='Rabin',
    author_email='2934170@qq.com',
    description=('A simple framework based on Tornado'),
    long_description=long_description,
    packages=['demeter'],
    install_requires = install_requires,
    #tests_require=['pytest'],
    #cmdclass = {'test': install},
    include_package_data=True,
    package_data = {},
    data_files=[
        # Populate this with any files config files etc.
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ]
)