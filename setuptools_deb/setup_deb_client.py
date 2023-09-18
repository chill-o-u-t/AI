"""Модуль с классом сборки клиентского deb-пакета."""

import os
from distutils.log import INFO
from distutils.util import get_platform
from distutils.dir_util import mkpath
from shutil import rmtree
from pathlib import Path
from subprocess import check_call  # noqa: S404
from setuptools_deb.setup_deb_basic import BuildDebPackageBasic, MAKE_PATH_MODE
import types


# Набор констант с информацией о проекте (пример). Используются в методе инициализации
PROJECT_NAME = 'setuptools_deb'
PROJECT_AUTHOR = 'R&EC SPb ETU'
PROJECT_MAINTAINER = PROJECT_AUTHOR
PROJECT_VERSION = '0.0.1'
PROJECT_DEPENDS = ''
PROJECT_DESCRIPTION = 'Пакет расширения setuptools, реализующий сборку debian client пакетов'
PROJECT_EMAIL = 'info@nicetu.spb.ru'
PROJECT_URL = 'http://nicetu.spb.ru'
# Информация о пакетах (пример)
PROJECT_DEB_PACKAGE1 = 'pack-01'
PROJECT_DEB_PACKAGE1_RU_NAME = 'ПК 1'
PROJECT_DEB_PACKAGE1_WIN_TITLE = 'Программный комплекс 1'
PROJECT_DEB_PACKAGE2 = 'pack-02'
PROJECT_DEB_PACKAGE2_RU_NAME = 'ПК 2'
PROJECT_DEB_PACKAGE2_WIN_TITLE = 'Программный комплекс 2'
# Настройки путей (пример)
PACKAGE_DIR = './build/bdist.{0}/deb'.format(get_platform())
DIST_PATH = './dist'
DOMAIN_PATH = 'vko/nicetu/{0}'.format(PROJECT_NAME)
OPT_SYS_PATH = 'opt/{0}/{1}'.format(DOMAIN_PATH, PROJECT_NAME)
ETC_CONFIG_PATH = 'etc/{0}/{1}'.format(DOMAIN_PATH, PROJECT_NAME)
DESTINATION_PATH = '{0}/{1}'.format(PACKAGE_DIR, OPT_SYS_PATH)
PATHS_TO_CREATE = types.MappingProxyType({'./dist': 1, '{0}/DEBIAN'.format(PACKAGE_DIR): 2})
DESKTOP_MAKE_PATHS = types.MappingProxyType(
    {
        'usr/share/fly-wm/startmenu/vko': 1,
        'usr/share/applications': 2,
        'usr/share/fly-wm/Desktops/Desktop1': 3,
    },
)
CATEGORY_NAME = 'VKO'
CATEGORY_RU_NAME = 'ВКО'
CATEGORY_PATHS = types.MappingProxyType(
    {
        'usr/share/fly-wm/startmenu': 1,
        'usr/share/applications': 2,
    },
)
# Настройки копирования каталогов
IGNORE_PATTERNS = types.MappingProxyType({'*.pyc': 1, '__pycache__': 2, '.env': 3})


class BuildDebPackageClient(BuildDebPackageBasic):  # noqa: WPS214, WPS230
    """Класс сборки клиентского deb-пакета.

    Использовать в setup.py путем наследования c обязательным переопределением метода initialize_options().
    Если нужно расширить алгоритм сборки, можно переопределить методы run_extra_before_make() и run_extra_after_make(),
    выполняемые соответственно до и после сборки конкретных пакетов.
    При необходимости можно полностью переопределить верхний метод сборки run().

    Attributes:
        client_packages (list): Список клиентских пакетов, заполняется через метод add_client_package_info().
        make_paths (list): Список путей, куда необходимо записать desktop-файл.
        category_paths (list): Список путей, где необходимо создать категорию и записать desktop-файл.
        category_name (str): Наименование категории.
        category_ru_name (str): Русскоязычное наименование категории.
    """

    def __init__(self, dist):
        """Конструктор."""
        self.client_packages = []
        self.make_paths = []
        self.category_paths = []
        self.category_name = ''
        self.category_ru_name = ''
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
        self.add_client_package_info(
            PROJECT_DEB_PACKAGE1,
            PROJECT_DEB_PACKAGE1_RU_NAME,
            PROJECT_DEB_PACKAGE1_WIN_TITLE,
        )
        self.add_client_package_info(
            PROJECT_DEB_PACKAGE2,
            PROJECT_DEB_PACKAGE2_RU_NAME,
            PROJECT_DEB_PACKAGE2_WIN_TITLE,
        )
        # Установка путей
        self.paths['package'] = PACKAGE_DIR
        self.paths['dist'] = DIST_PATH
        self.paths['opt_sys'] = OPT_SYS_PATH
        self.paths['etc_config'] = ETC_CONFIG_PATH
        self.paths['destination'] = DESTINATION_PATH
        self.paths_to_create = PATHS_TO_CREATE
        # Настройки копирования папок из корня проекта
        self.ignores = IGNORE_PATTERNS
        # Настройка клиентских опций
        self.make_paths = DESKTOP_MAKE_PATHS
        self.category_name = CATEGORY_NAME
        self.category_ru_name = CATEGORY_RU_NAME
        self.category_paths = CATEGORY_PATHS
        # Это лишь пример. Метод необходимо переопределить в реальном проекте
        raise RuntimeError(
            'method initialize_options() must be overriden in subclass %s'
            % self.__class__,
        )

    def add_basic_package_info(self, pack_name: str):
        """Добавить информацию о базовом пакете.

        Raises:
            RuntimeError: метод не используется в клиентском классе.
        """
        raise RuntimeError(
            'method add_client_package_info() must be used instead of add_basic_package_info()',
        )

    def add_client_package_info(self, package_name: str, package_ru_title: str, package_ru_title_long: str):
        """Добавить информацию о клиентском пакете.

        Args:
            package_name (str): Наименование пакета.
            package_ru_title (str): Краткое наименование пакета на русском.
            package_ru_title_long (str): Полное наименование пакета на русском.
        """
        self.client_packages.append([package_name, package_ru_title, package_ru_title_long])

    def finalize_options(self):
        """Завершение инициализции. При необходимости - переопределить в наследнике."""

    def run(self):
        """Запуск сборки. При необходимости - переопределить в наследнике."""
        # создание нужной структуры папок
        self.prepare_structure()
        # копирование каталогов из корня проекта
        self.copy_project_dirs()
        # выполнение дополнительных команд перед сборкой пакетов
        self.run_extra_before_make()
        # сборка пакетов
        for deb_pac in self.client_packages:
            self.make_client_package(deb_pac[0], deb_pac[1], deb_pac[2])
        # выполнение дополнительных команд после сборкой пакетов
        self.run_extra_after_make()
        # чистка перед завершением
        rmtree('./build')

    def make_client_package(self, package_name: str, ru_title: str, main_window_title: str):
        """Сборка клиентского пакета.

        Args:
            package_name (str): Наименование пакета.
            ru_title (str): Краткое наименование пакета на русском.
            main_window_title (str): Имя заголовочного файла.
        """
        self.announce('Making client package with category', level=INFO)
        if main_window_title:
            self.write_title_file(main_window_title)
        self.write_control_file('{0}-{1}'.format(self.project_info['name'], package_name))
        for desktop_cat in self.category_paths:
            self.write_desktop_category(self.category_name, self.category_ru_name, desktop_cat)
            self.write_desktop_file(
                self.project_info['name'],
                ru_title,
                '{0}/{1}'.format(desktop_cat, self.category_name),
            )
        for desktop_path in self.make_paths:
            self.write_desktop_file(self.project_info['name'], ru_title, desktop_path)
        check_call(['fakeroot', 'dpkg-deb', '--build', self.paths['package'], self.paths['dist']])  # noqa: S603, S607

    def write_title_file(self, main_window_title: str):
        """Запись заголовочного файла.

        Args:
            main_window_title (str): Имя заголовочного файла.
        """
        self.announce('Writing title file', level=INFO)
        with open('etc/main_window_title.py.in', encoding='utf-8') as template_file:
            template = template_file.read()
            res = template.format(main_window_title=main_window_title)
            main_window_title = '{0}/{1}/main_window_title.py'.format(self.paths['package'], self.paths['opt_sys'])
            mkpath(str(Path(main_window_title).parent), verbose=True, mode=MAKE_PATH_MODE)
            with open(main_window_title, 'w', encoding='utf-8') as result_file:
                result_file.write(res)

    def write_desktop_file(self, name: str, ru_name: str, desktop_path: str):
        """Запись desktop-файла.

        Args:
            name (str): Имя файла, так же попадает в поле Name файла .desktop.
            ru_name (str): Имя на русском, попадает в поле Name[ru] файла .desktop.
            desktop_path (str): Относительный путь к файлу.
        """
        self.announce('Writing desktop file', level=INFO)
        desktop_filename = '{0}/{1}/{2}.desktop'.format(self.paths['package'], desktop_path, name)
        os.makedirs(os.path.dirname(desktop_filename), exist_ok=True)
        with open(desktop_filename, 'w', encoding='utf-8') as desktop_file:
            desktop_file.writelines(
                '{0}\n'.format(line) for line in (
                    '[Desktop Entry]',
                    'Encoding=UTF-8',
                    'Name={0}'.format(name),
                    'Name[ru]={0}'.format(ru_name),
                    'Comment={0}'.format(self.project_info['description']),
                    'MimeType=application',
                    'Type=Application',
                    'Terminal=false',
                    'Categories=Utility',
                    'Exec=/{0}/{1}/venv/bin/python -B -m {1}'.format(self.paths['opt_sys'], self.project_info['name']),
                    'Path=/{0}'.format(self.paths['opt_sys']),
                    'Icon=/usr/share/icons/hicolor/48x48/apps/{0}.png'.format(self.project_info['name']),
                )
            )

    def write_desktop_category(self, name: str, ru_name: str, desktop_path: str):
        """Создание папки для категории.

        Args:
            name (str): Имя папки, так же попадает в поле Name файла .directory.
            ru_name (str): Имя на русском, попадает в поле Name[ru] файла .directory.
            desktop_path (str): Относительный путь к папке.
        """
        self.announce('Writing desktop category', level=INFO)
        desktop_category = '{0}/{1}/{2}/.directory'.format(self.paths['package'], desktop_path, name.lower())
        os.makedirs(os.path.dirname(desktop_category), exist_ok=True)
        with open(desktop_category, 'w', encoding='utf-8') as desktop_file:
            desktop_file.writelines(
                '{0}\n'.format(line) for line in (
                    '[Desktop Entry]',
                    'Name={0}'.format(name),
                    'Name[ru]={0}'.format(ru_name),
                    'Type=Directory',
                    'Icon=folder',
                )
            )
