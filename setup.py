from setuptools import setup, find_packages

import prometeo

setup(name='prometeo',
   version='0.1',
   description='a prototyping and modelling tool for embedded optimization',
   url='http://github.com/zanellia/prometeo',
   author='Andrea Zanelli',
   license='LGPL',
   packages = find_packages(),
   install_requires=[
      'astpretty',
      'numpy',
      'scipy',
   ],
   package_data={'': [
       'cprmt/prmt_mat_blasfeo_wrapper.h',
       'cprmt/prmt_heap.h',
       ]},
   zip_safe=False)
