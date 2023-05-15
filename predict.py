import os

import easyocr
from PIL import Image

FIRST = False
PATH = 'base_dir'

if FIRST:
    os.mkdir(PATH)


def load_model_easyocr(
    model_directory: str,
    user_directory: str,
    recog_network: str
) -> easyocr.Reader:
    try:
        reader = easyocr.Reader(
            ['ru'],
            model_storage_directory=model_directory,
            user_network_directory=user_directory,
            recog_network=recog_network
        )
    except Exception as error:
        raise ValueError('При попытке загрузить модель easyocr возникла ошибка {error}'.format(error=error))
    return reader


if __name__ == '__main__':
    import easyocr

    reader = load_model_easyocr(
        'custom_EasyOCR/model',
        'custom_EasyOCR/user_network',
        'custom_example'
    )
    image = 'base_dir/result/date.jpg'
    result = reader.readtext(image)
    for r in result:
        print(r[1].lower())
    image = 'base_dir/result/city.jpg'
    result = reader.readtext(image)
    for r in result:
        print(r[1].lower())


