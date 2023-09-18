#!/usr/bin/env python3

import os
from distutils.core import setup

from sphinx.setup_command import BuildDoc  # noqa: WPS433

from setuptools_deb.setup_deb_service import BuildDebPackageBasic

PROJECT_NAME = 'passport_scanner'
PROJECT_VERSION = '1.0.0'
PROJECT_RELEASE_DATE = '18.09.2023'
# https://www.debian.org/doc/debian-policy/ch-relationships.html
PROJECT_DEPENDS = ', '.join((
    'some-lib (= 2.1.0)',
    'python3-all', 'python3-six', 'python3-pyqt5',
))
PROJECT_AUTHOR = 'Ivan Morozov'
PROJECT_DESCRIPTION = 'Software tool for processing radio waves measurements'
PROJECT_EMAIL = 'info@nicetu.spb.ru'
PROJECT_URL = 'http://nicetu.spb.ru'
PROJECT_ACTIVE_NAME_RU = 'ПС ОРСИ (АУТ и УФЦ) '
PROJECT_PASSIVE_NAME_RU = 'ПС ОРСИ (ПУТ)'

setup_file = 'setup.py'
setup(
    name=PROJECT_NAME,
    version=PROJECT_VERSION,
    description=PROJECT_DESCRIPTION,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_EMAIL,
    url=PROJECT_URL,
    cmdclass={
        'bdist_deb': BuildDebPackageBasic,
        'doc': BuildDoc,
    },
    packages=[PROJECT_NAME],
    command_options={
        'bdist_deb': {
            'name': (setup_file, PROJECT_NAME),
            'version': (setup_file, PROJECT_VERSION),
            'description': (setup_file, PROJECT_DESCRIPTION),
            'depends': (setup_file, PROJECT_DEPENDS),
        },
        'doc': {
            'project': (setup_file, PROJECT_NAME),
            'version': (setup_file, PROJECT_VERSION),
            'release': (setup_file, PROJECT_VERSION),
            'source_dir': (setup_file, os.path.join(os.path.dirname(__file__), 'doc')),
        },
    },
)
