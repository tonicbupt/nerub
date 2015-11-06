# coding:utf-8

import os
from setuptools import setup, find_packages


NAME = 'nerub'
VERSION = '0.0.1'
DESCRIPTION = 'Nerub, the network builder'
AUTHOR = 'tonic'
AUTHOR_EMAIL = 'tonic@wolege.ca'
LICENSE = 'BSD'
URL = 'http://git.hunantv.com/platform/nerub'
KEYWORDS = 'docker macvlan network'
ENTRY_POINTS = {
    'console_scripts':['nerub=nerub.plugin:main',]
}
INSTALL_REQUIRES = [
    'gunicorn',
    'netaddr',
    'redis',
    'more_itertools',
    'flask',
]


here = os.path.abspath(os.path.dirname(__file__))


def read_long_description(filename):
    path = os.path.join(here, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return ''


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read_long_description('README.md'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    keywords=KEYWORDS,
    packages = find_packages(exclude=['tests.*', 'tests', 'examples.*', 'examples', 'scripts']),
    install_package_data=True,
    zip_safe=False,
    entry_points=ENTRY_POINTS,
    install_requires=INSTALL_REQUIRES,
)
