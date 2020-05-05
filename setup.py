from setuptools import setup, find_packages, dist

class BinaryDistribution(dist.Distribution):
    def has_ext_modules(foo):
        return True

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='prometeo-dsl',
    version='0.0.3',
    python_requires='>=3.6, <=3.9',
    description='Python-to-C transpiler and domain specific language for embedded high-performance computing',
    url='http://github.com/zanellia/prometeo',
    author='Andrea Zanelli',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='LGPL',
    packages = find_packages(),
    entry_points={'console_scripts': ['pmt=prometeo.__main__:console_entry']},
    install_requires=[
        'astpretty',
        'strip_hints',
        'astunparse',
        'numpy',
        'scipy',
        'multipledispatch',
        'pyparsing',
        'casadi==3.5.1',
        'jinja2'
    ],
    package_data={'': \
        ['lib/prometeo/libcpmt.so', \
        'lib/blasfeo/libblasfeo.so', \
        'include/prometeo/*', \
        'include/blasfeo/*']},
    include_package_data=True,
    zip_safe=False,
    distclass=BinaryDistribution
)
