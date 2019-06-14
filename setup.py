from setuptools import setup, find_packages

import prometeo

setup(name='prometeo',
   version='0.1',
   python_requires='>=3.6, <3.7',
   description='a prototyping and modelling tool for embedded optimization',
   url='http://github.com/zanellia/prometeo',
   author='Andrea Zanelli',
   license='LGPL',
   packages = find_packages(),
   entry_points={'console_scripts': ['pmt=prometeo.__main__:console_entry']},
   install_requires=[
      'astpretty',
      'numpy',
      'scipy',
      'multipledispatch',
      'mypy'
   ],
   zip_safe=False)
