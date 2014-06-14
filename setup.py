from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='wafer',
      version=version,
      description="game server framework",
      long_description="""\
game server framework""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='twisted mysql',
      author='leecrest',
      author_email='281042207@qq.com',
      license='wafer',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	  include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
		  "twisted",
		  "zope.interface",
		  "DBUtils",
		  "MySQL-python"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
