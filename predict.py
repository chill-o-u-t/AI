import base64
import os
from io import BytesIO

from PIL import Image
from easyocr import Reader

import easyocr

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
    reader = Reader(
        ['ru'],
        model_storage_directory='custom_EasyOCR/model',
        user_network_directory='custom_EasyOCR/user_network',
        recog_network='custom_example'
    )
    context = {}
    img = Image.open('base_dir/IMG_20230510_205422.jpg')
    img.crop((1000, 350, 2100, 600)).save('tempdata/surname.jpg')
    img.crop((1150, 600, 2100, 700)).save('tempdata/name.jpg')
    img.crop((1150, 700, 2100, 800)).save('tempdata/secondname.jpg')
    img.crop((1050, 800, 1300, 900)).save('tempdata/gender.jpg')
    img.crop((1430, 800, 1950, 900)).save('tempdata/bdate.jpg')
    img.crop((2100, 400, 2300, 1300)).rotate(90, expand=True).save('tempdata/id.jpg')
    for file in os.listdir('tempdata'):
        result = reader.readtext(f'tempdata/{file}')
        res = ''
        for digit in result:
            res += digit[1].lower()
        context[str(file.split('.')[0])] = res
        os.remove(f'tempdata/{file}')
    buffered = BytesIO()
    img.crop((250, 400, 1000, 1200)).save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    context['image'] = img_str

    print(context)


