#!/usr/bin/env python
"""The setup script."""

from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()


requirements = ['paramiko', 'bottle']


setup(author="Roman Dobosz, Szymon Datko",
      author_email='gryf73@gmail.com',
      python_requires='>=3.6',
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: English',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7'],
      description="Ferrit is a fake gerrit server for testing purposes",
      entry_points={'console_scripts': ['ferrit=ferrit.service:main']},
      install_requires=requirements,
      license="BSD license",
      long_description=readme,
      include_package_data=True,
      keywords='ferrit',
      name='ferrit',
      packages=find_packages(include=['ferrit', 'ferrit.*']),
      test_suite='tests',
      url='https://github.com/gryf/ferrit',
      version='0.0.1',
      zip_safe=False)
