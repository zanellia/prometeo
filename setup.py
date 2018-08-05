from setuptools import setup, find_packages

import prometeo

setup(name='prometeo',
   version='0.1',
   description='a prototyping and modelling tool for embedded optimization',
   url='http://github.com/zanellia/prometeo',
   author='Andrea Zanelli',
   license='LGPL',
   packages = find_packages(),
   zip_safe=False)
