#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('README.rst') as f:
    readme = f.read()

setup(
    name='chainload',
    version="1.4",
    description='Load a value from an environmental variable, YAML/JSON file, or default to a provided value.',
    long_description=readme,
    author='Tristan Fisher',
    author_email='code@tristanfisher.com',
    url='http://github.com/tristanfisher/chainload',
    packages=['chainload'],
    package_data={'': ['LICENSE']},
    license='Apache 2.0',
    classifiers=(
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
    ),
    install_requires=['PyYAML>=3.11'],
    tests_require=['nose']
)
