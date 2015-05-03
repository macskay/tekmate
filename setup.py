#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup

setup(name="tekmate",
      version="0.0.1",
      description="Tekmate - Stargate-Based RPG",
      author="Max",
      packages=['tekmate'],
      license="GPLv3",
      url="https://github.com/mkli90/tekmate",
      package_data={
          'tmz': ['LICENSE']
      },
      classifiers=[
          "Development Status :: 1 - Planning",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Natural Language :: English",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Topic :: Games/Entertainment",
          "Topic :: Software Development :: Libraries",
      ],
)
