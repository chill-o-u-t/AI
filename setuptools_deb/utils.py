"""Вспомогательные функции."""
from distutils.dir_util import mkpath
from pathlib import Path
from shutil import copy2


def copy(what, *, to_file=None, to_dir=None, mode=0o755):
    """Копирование с созданием директорий.

    Args:
        what: копируемый файл
        to_file: путь, включая новое имя файла
        to_dir: путь, куда файл скопировать
        mode: права на промежуточные директории
    """
    if to_file and to_dir:
        raise ValueError('Недопустимо использование множественного определения назначения')
    if not (to_file or to_dir):
        raise ValueError('Отсутствует определение назначения')

    if to_file:
        base_dir = str(Path(to_file).parent)
    else:
        base_dir = to_dir
    mkpath(base_dir, verbose=True, mode=mode)
    copy2(what, to_file or to_dir)
