from setuptools import setup
import os
import sys

_here = os.path.abspath(os.path.dirname(__file__))

if sys.version_info[0] < 3:
    with open(os.path.join(_here, 'README.MD')) as f:
        long_description = f.read()
else:
    with open(os.path.join(_here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

version = {}
with open(os.path.join(_here, 'ergoFACE', 'version.py')) as f:
    exec(f.read(), version)

setup(
    name='ergoFace',
    version=version['__version__'],
    description='Hardware & Software interface for Daum Ergobike 8008 TRS',
    long_description=long_description,
    author='Michael Weizinger',
    author_email='weinzmi@gmail.com',
    url='https://github.com/weinzmi/ergoFACE',
    license='TBD',
    include_package_data=True,
    packages=['ergoFACE'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7'],
    )
