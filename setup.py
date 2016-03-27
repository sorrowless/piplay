#!/usr/bin/env python
from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), 'r') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt'), 'r') as f:
    required_packages = f.read()

setup(name='piplay',
      version='0.1',

      author="Stanislaw Bogatkin",
      author_email="sbog@sbog.ru",

      description="Piplay is just another player",
      long_description=long_description,
      url='https://github.com/sorrowless/piplay',
      keywords="player",
      license="GPL",

      packages=['piplay'],
      install_requires=required_packages,

      package_data={
          '': ['requirements.txt', 'README.md'],
      },

      entry_points={
          'console_scripts': [
              'piplay=piplay.player:main',
          ],
      })
