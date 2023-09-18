"""Модуль с классом сборки сервисного deb-пакета."""

import os
from distutils.log import INFO
from distutils.util import get_platform
from shutil import rmtree
from subprocess import check_call  # noqa: S404
from setuptools_deb.setup_deb_basic import BuildDebPackageBasic, copy
import types


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
PROJECT_DEB_PACKAGE1_COPY_INI = True
PROJECT_DEB_PACKAGE2 = 'example2'
PROJECT_DEB_PACKAGE2_COPY_INI = False
# Настройки путей (пример)
PACKAGE_DIR = './build/bdist.{0}/deb'.format(get_platform())
DIST_PATH = './dist'
DOMAIN_PATH = 'vko/nicetu/{0}'.format(PROJECT_NAME)
OPT_SYS_PATH = 'opt/{0}/{1}'.format(DOMAIN_PATH, PROJECT_NAME)
ETC_CONFIG_PATH = 'etc/{0}/{1}'.format(DOMAIN_PATH, PROJECT_NAME)
DESTINATION_PATH = '{0}/{1}'.format(PACKAGE_DIR, OPT_SYS_PATH)
PATHS_TO_CREATE = types.MappingProxyType({'./dist': 1, '{0}/DEBIAN'.format(PACKAGE_DIR): 2})
SERVICE_NAME = 'custom_example'
# Настройки копирования каталогов и файлов
IGNORE_PATTERNS = types.MappingProxyType({'*.pyc': 1, '__pycache__': 2, '.env': 3})


class BuildDebPackageService(BuildDebPackageBasic):
    """Класс сборки сервисного deb-пакета.

    Использовать в setup.py путем наследования c обязательным переопределением метода initialize_options().
    Если нужно расширить алгоритм сборки, можно переопределить методы run_extra_before_make() и run_extra_after_make(),
    выполняемые соответственно до и после сборки конкретных пакетов.
    При необходимости можно полностью переопределить верхний метод сборки run().

    Attributes:
        service_packages (list): Список сервисных пакетов, заполняется через метод add_service_package_info().
        service_name (str): Наименование сервиса.
    """

    def __init__(self, dist):
        """Конструктор."""
        self.service_packages = []
        self.service_name = ''
        super().__init__(dist)

    def initialize_options(self):
        """Метод инициализации.

        Raises:
            RuntimeError: метод должен быть переопределен в наследнике под реальный проект.
        """
        # Пример инициализации. Информация о проекте
        self.project_info['name'] = PROJECT_NAME
        self.project_info['author'] = PROJECT_AUTHOR
        self.project_info['maintainer'] = PROJECT_MAINTAINER
        self.project_info['version'] = PROJECT_VERSION
        self.project_info['depends'] = PROJECT_DEPENDS
        self.project_info['description'] = PROJECT_DESCRIPTION
        # Добавление информации о пакетах
        self.add_service_package_info(PROJECT_DEB_PACKAGE1, PROJECT_DEB_PACKAGE1_COPY_INI)
        self.add_service_package_info(PROJECT_DEB_PACKAGE2, PROJECT_DEB_PACKAGE2_COPY_INI)
        # Установка путей
        self.paths['package'] = PACKAGE_DIR
        self.paths['dist'] = DIST_PATH
        self.paths['opt_sys'] = OPT_SYS_PATH
        self.paths['etc_config'] = ETC_CONFIG_PATH
        self.paths['destination'] = DESTINATION_PATH
        self.paths_to_create = PATHS_TO_CREATE
        # Настройки копирования папок из корня проекта
        self.ignores = IGNORE_PATTERNS
        # Настройка сервисных опций
        self.service_name = SERVICE_NAME
        # Это лишь пример. Метод необходимо переопределить в реальном проекте
        raise RuntimeError(
            'method initialize_options() must be overriden in subclass %s'
            % self.__class__,
        )

    def add_basic_package_info(self, pack_name: str):
        """Добавить информацию о базовом пакете.

        Raises:
            RuntimeError: метод не используется в сервисном классе.
        """
        raise RuntimeError(
            'method add_service_package_info() must be used instead of add_basic_package_info()',
        )

    def add_service_package_info(self, package_name: str, option_copy_ini: bool):
        """Добавить информацию о сервисном пакете.

        Args:
            package_name (str): Имя пакета.
            option_copy_ini (bool): Опция копирования ini-файла.
        """
        self.service_packages.append([package_name, option_copy_ini])

    def finalize_options(self):
        """Завершение инициализции. При необходимости - переопределить в наследнике."""

    def run(self):
        """Запуск сборки. При необходимости - переопределить в наследнике."""
        # создание нужной структуры папок
        self.prepare_structure()
        # копирование сервисных файлов из корня проекта
        self.copy_service_files()
        # копирование каталогов из корня проекта
        self.copy_project_dirs()
        # выполнение дополнительных команд перед сборкой пакетов
        self.run_extra_before_make()
        # сборка пакетов
        for deb_pac in self.service_packages:
            self.make_service_package(deb_pac[0], deb_pac[1])
        # выполнение дополнительных команд после сборкой пакетов
        self.run_extra_after_make()
        # чистка перед завершением
        rmtree('./build')

    def copy_service_files(self):
        """Копирование файлов .service, .conf и .logrotate в папку сборки."""
        self.announce('Copying service files', level=INFO)
        file_name = '{0}.service'.format(self.service_name)
        if os.path.exists(file_name):
            copy(file_name, to_dir='{0}/lib/systemd/system/'.format(self.paths['package']))
        file_name = '{0}.conf'.format(self.service_name)
        if os.path.exists(file_name):
            copy(file_name, to_dir='{0}/etc/rsyslog.d/'.format(self.paths['package']))
        file_name = '{0}.logrotate'.format(self.service_name)
        if os.path.exists(file_name):
            copy(
                file_name,
                to_file='{0}/etc/logrotate.d/{1}'.format(self.paths['package'], self.service_name),
            )

    def make_service_package(self, package_name: str = None, copy_ini_file: bool = False):
        """Сборка сервисного пакета.

        Args:
            package_name (str): Имя пакета.
            copy_ini_file (bool): Опция копирования ini-файла.
        """
        self.announce('Making service package', level=INFO)
        if copy_ini_file:
            self.copy_package_ini(package_name)
        if package_name:
            self.write_control_file('{0}-{1}'.format(self.project_info['name'], package_name))
        else:
            with open(
                '{0}/{1}/config.py'.format(self.paths['package'], self.paths['opt_sys']),
                'w',
                encoding='utf-8',
            ) as result_file:
                result_file.write('WITH_DB = False')
            self.write_control_file(self.project_info['name'])
        check_call(['fakeroot', 'dpkg-deb', '--build', self.paths['package'], self.paths['dist']])  # noqa: S603, S607
