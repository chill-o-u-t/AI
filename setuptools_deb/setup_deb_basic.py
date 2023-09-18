"""Модуль с классом сборки простого deb-пакета."""

import os
import types
from distutils.cmd import Command
from distutils.dir_util import copy_tree, mkpath
from distutils.log import INFO
from distutils.util import get_platform
from shutil import copytree, ignore_patterns, rmtree
from subprocess import check_call  # noqa: S404

from setuptools_deb.utils import copy

# Набор констант с информацией о проекте (пример). Используются в методе инициализации
PROJECT_NAME = 'setuptools_deb'
PROJECT_AUTHOR = 'R&EC SPb ETU'
PROJECT_MAINTAINER = PROJECT_AUTHOR
PROJECT_VERSION = '0.0.1'
PROJECT_DEPENDS = ''
PROJECT_DESCRIPTION = 'Пакет расширения setuptools, реализующий сборку debian service пакетов'
PROJECT_EMAIL = 'info@nicetu.spb.ru'
PROJECT_URL = 'http://nicetu.spb.ru'
# Информация о пакетах (пример)
PROJECT_DEB_PACKAGE1 = 'example1'
PROJECT_DEB_PACKAGE2 = 'example2'
# Настройки путей (пример)
PACKAGE_DIR = './build/bdist.{0}/deb'.format(get_platform())
DIST_PATH = './dist'
DOMAIN_PATH = 'vko/nicetu/{0}'.format(PROJECT_NAME)
OPT_SYS_PATH = 'opt/{0}/{1}'.format(DOMAIN_PATH, PROJECT_NAME)
ETC_CONFIG_PATH = 'etc/{0}/{1}'.format(DOMAIN_PATH, PROJECT_NAME)
DESTINATION_PATH = '{0}/{1}'.format(PACKAGE_DIR, OPT_SYS_PATH)
PATHS_TO_CREATE = types.MappingProxyType({'./dist': 1, '{0}/DEBIAN'.format(PACKAGE_DIR): 2})
# Настройки копирования каталогов
IGNORE_PATTERNS = types.MappingProxyType({'*.pyc': 1, '__pycache__': 2, '.env': 3})

# Режим для mkpath()
MAKE_PATH_MODE = 0o755


def fix_record(file_path: str):
    """Вспомогательный метод исправления файла, вызываемый при копирования каталога venv.

    Args:
        file_path (str): имя и путь к файлу.
    """
    with open(file_path, 'r+', encoding='utf-8') as record_file:
        original_file = record_file.read()
        record_file.seek(0)
        for line in original_file.splitlines():
            if '__pycache__' not in line:
                record_file.write('{0}\n'.format(line))
                record_file.truncate()


def fix_records(dir_path: str):
    """Вспомогательный метод исправления папки, вызываемый при копирования каталога venv.

    Args:
        dir_path (str): имя и путь к папке.
    """
    for root, _dirs, files in os.walk(dir_path):
        for every_file in files:
            if every_file == 'RECORD':
                fix_record(os.path.join(root, every_file))


class BuildDebPackageBasic(Command):  # noqa: WPS214
    """Класс сборки простого deb-пакета.

    Использовать в setup.py путем наследования c обязательным переопределением метода initialize_options().
    Если нужно расширить алгоритм сборки, можно переопределить методы run_extra_before_make() и run_extra_after_make(),
    выполняемые соответственно до и после сборки конкретных пакетов.
    При необходимости можно полностью переопределить верхний метод сборки run().

    Attributes:
        project_info (dict): Словарь с данными о проекте. Содержит следующие элементы:
            name: наименование.
            author: автор.
            maintainer: сопровождающий.
            version: версия.
            depends: перечисление зависимостей через запятую.
            description: краткое описание.

        paths (dict): Словарь с настройками путей. Содержит следующие элементы:
            package: рабочий каталог для сборки.
            destination: путь, куда будут складываться необходимые файлы для сборвки пакетов.
            dist: выходной путь для собранных пакетов.
            opt_sys: путь к папке пакета после установки.
            etc_config: путь к конфигурационным файлам после установки.

        basic_packages (list): Список базовых пакетов, заполняется через метод add_basic_package_info().
        paths_to_create (list): Список путей, которые необходимо создать перед копированием файлов для пакетов.
        ignores (list): Список игнорируемых шаблонов при копировании каталогов.
    """

    # 1) bdist_deb --help
    # полное / сокращение (некоторые недоступны) / описание
    user_options = [
        ('name=', None, 'Имя проекта'),
        ('author=', 'a', 'Автор проекта'),
        ('version=', 'V', 'Версия проекта'),
        ('depends=', 'D', 'Зависимости проекта'),
        ('description=', 'd', 'Описание проекта'),
        ('package=', 'p', 'Варианты поставки. Разделитель - запятая.'),
        ('destination=', None, 'Размещение в системе'),
        # по наличию флага
        ('no-clear', 'N', 'Отключение очистки файлов сборки'),
    ]
    # список строк из user_options
    boolean_options = [
        'no-clear',
    ]

    def __init__(self, dist):
        """Конструктор."""
        self.project_info = {
            'name': '',
            'author': '',
            'maintainer': '',
            'version': '',
            'depends': '',
            'description': '',
        }
        self.paths = {
            'package': '',
            'dist': '',
            'opt_sys': '',
            'etc_config': '',
            'destination': '',
        }
        self.basic_packages = []
        self.paths_to_create = []
        self.ignores = []
        super().__init__(dist)

    # 2) command_options
    # command has no such option <option-from-user_options>
    def initialize_options(self):
        """Инициализация опций, поддерживаемых командой.

        См. cmd.py для подробностей.
        """
        self.name = None
        self.author = None
        self.version = None
        self.depends = None
        self.description = None
        self.package = None
        self.destination = None
        self.no_clear = False

        # Пример инициализации. Информация о проекте
        self.project_info['name'] = PROJECT_NAME
        self.project_info['author'] = PROJECT_AUTHOR
        self.project_info['maintainer'] = PROJECT_MAINTAINER
        self.project_info['version'] = PROJECT_VERSION
        self.project_info['depends'] = PROJECT_DEPENDS
        self.project_info['description'] = PROJECT_DESCRIPTION
        # Установка путей
        self.paths['package'] = PACKAGE_DIR
        self.paths['dist'] = DIST_PATH
        self.paths['opt_sys'] = OPT_SYS_PATH
        self.paths['etc_config'] = ETC_CONFIG_PATH
        self.paths['destination'] = DESTINATION_PATH
        self.paths_to_create = PATHS_TO_CREATE
        # Настройки копирования папок из корня проекта
        self.ignores = IGNORE_PATTERNS

    def add_basic_package_info(self, package_name: str):
        """Добавить информацию о базовом пакете.

        Args:
            package_name (str): Имя пакета.
        """
        self.announce('Добавление пакета {}'.format(package_name), level=INFO)
        self.basic_packages.append(package_name)

    def finalize_options(self):
        """Завершение инициализации.

        См. cmd.py для подробностей.
        """
        default_options = {
            'name': None,
            'author': PROJECT_AUTHOR,
            'version': None,
            'depends': '',
            'description': None,
        }
        for option, default in default_options.items():
            # если установлено пользователем
            if getattr(self, option):
                self.announce('{0}={1}'.format(option, default))
            else:
                if default is None:
                    raise RuntimeError('Обязательный параметр <{0}> не указан'.format(option))
                self.announce('Установка значения по умолчанию {0}={1}'.format(option, default), level=INFO)
                setattr(self, option, default)

        # пока используется словарь
        for ready_option in default_options:
            option_value = getattr(self, ready_option)
            self.project_info.update({ready_option: option_value})

        # TODO: костыль
        if self.destination:
            self.paths['destination'] = '{0}/{1}'.format(PACKAGE_DIR, self.destination)
        else:
            self.paths['destination'] = '{0}/opt/{1}'.format(PACKAGE_DIR, self.project_info['name'])

        if self.package:  # значение после возможного изменения пользователем
            packages = self.package

            if isinstance(self.package, str):
                packages = self.package.split(',')

            for package in packages:
                self.add_basic_package_info(package)

    def run(self):
        """Запуск сборки. При необходимости - переопределить в наследнике."""
        # создание нужной структуры папок
        self.prepare_structure()
        # копирование каталогов из корня проекта
        self.copy_project_dirs()
        # выполнение дополнительных команд перед сборкой пакетов
        self.run_extra_before_make()
        # сборка пакетов
        for package_name in self.basic_packages:
            self.make_package(package_name)
        if not self.basic_packages:
            self.make_package()
        # выполнение дополнительных команд после сборкой пакетов
        self.run_extra_after_make()

        if not self.no_clear:
            # чистка перед завершением
            rmtree('./build')

    def run_extra_before_make(self):
        """Выполнить дополнительные команды перед сборкой пакетов. При необходимости - переопределить в наследнике."""

    def run_extra_after_make(self):
        """Выполнить дополнительные команды после сборкой пакетов. При необходимости - переопределить в наследнике."""

    def prepare_structure(self):
        """Подготовка. Создание необходимых путей."""
        self.announce('Prepare structure', level=INFO)
        if os.path.exists(self.paths['package']):
            rmtree(self.paths['package'])
        for path in self.paths_to_create:
            os.makedirs(path, exist_ok=True)
            os.chmod(path, MAKE_PATH_MODE)

    def copy_package_ini(self, package_name: str):
        """Копирование ini-файла пакета.

        Args:
            package_name (str): Имя пакета.
        """
        copy(
            '{0}.ini'.format(package_name),
            to_file='{0}/{1}/{2}/{2}.ini'.format(
                self.paths['package'],
                self.paths['etc_config'],
                self.project_info['name'],
            ),
        )

    def copy_project_dirs(self):
        """Копирование каталогов debian, venv и папки с исходниками в папку для сборки."""
        self.announce('Copying project dirs', level=INFO)
        if os.path.exists('./debian'):
            copy_tree('./debian', '{0}/DEBIAN/'.format(self.paths['package']))
        copytree(
            src=self.project_info['name'],
            dst=self.paths['destination'],
            ignore=ignore_patterns(*self.ignores),
        )
        if os.path.exists('./venv'):
            venv_destination = '{0}/venv'.format(self.paths['destination'])
            copytree(
                src='./venv',
                dst=venv_destination,
                ignore=ignore_patterns(*self.ignores),
                symlinks=True,
            )
            fix_records(venv_destination)

    def make_package(self, package_name: str = ''):
        """Сборка простого пакета.

        Args:
            package_name (str): Имя пакета.
        """
        package = self.project_info['name']
        if package_name:
            package += '-{0}'.format(package_name)

        self.announce('Сборка пакета <{}>'.format(package), level=INFO)
        self.write_control_file(package)

        self.build()

    def build(self):
        """Сборка подготовленной директории в deb."""
        # dist папка должна быть создана заранее
        check_call(['fakeroot', 'dpkg-deb', '--build', self.paths['package'], self.paths['dist']])  # noqa: S603, S607

    def write_control_file(self, name: str):
        """Запись control-файла.

        Args:
            name (str): Имя файла, собранное на основе имени проекта и имени пакета.
        """
        self.announce('Writing control file: <{0}>'.format(name), level=INFO)
        control_filename = '{0}/DEBIAN/control'.format(self.paths['package'])
        base_dir = '{0}/DEBIAN'.format(self.paths['package'])
        mkpath(base_dir, verbose=True, mode=MAKE_PATH_MODE)
        with open(control_filename, 'w', encoding='utf-8') as control_file:
            control_file.writelines(
                '{0}\n'.format(line) for line in (
                    'Package: {0}'.format(name.replace('_', '-')),
                    'Version: {0}'.format(self.project_info['version']),
                    'Section: main',
                    'Architecture: amd64',
                    'Depends: {0}'.format(self.project_info['depends']),
                    'Maintainer: {0}'.format(self.project_info['maintainer']),
                    'Description: {0}'.format(self.project_info['description']),
                )
            )
        os.chmod(control_filename, MAKE_PATH_MODE)
