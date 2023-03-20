import os
from datetime import time

import easyocr
from yolo_ai.models import Yolov4
from PIL import Image

FIRST = False
PATH = 'base_dir'

if FIRST:
    os.mkdir(PATH)


def load_model_yolo(model_path: str, classes_path: str) -> Yolov4:
    try:
        model = Yolov4(
            weight_path=model_path,
            class_name_path=classes_path
            # weight_path='yolov4-obj_best.weights',
            # class_name_path='classes.txt'
        )
    except Exception as error:
        raise 'При попытке загрузить модель yolov4 возникла ошибка {error}'.format(error=error)
    return model


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


def check_image(image_path: str) -> str:
    name, expansion = image_path.split('.')
    if expansion != 'jpg':
        image = Image.open(f'{PATH}/{image_path}').convert('RGB')
        image.save(f'{PATH}/{name}.jpg')
        os.remove(f'{PATH}/{image_path}')
        return f'{name}.jpg'
    return image_path


def get_images_after_yolo(yolo_objects, image_path: str) -> None:
    os.mkdir(f'{PATH}/result')
    image = Image.open(f'{PATH}/{image_path}')
    for obj in yolo_objects.values:
        extracted_image = image.crop(
            (int(obj[0]), int(obj[1]), int(obj[2]), int(obj[3]))
        )
        extracted_image.save(f'{PATH}/result/{obj[4]}.jpg')


def rotate_image() -> None:
    image = Image.open(f'{PATH}/result/series.jpg')
    img = image.rotate(90, expand=True)
    img.save(f'{PATH}/result/_series.jpg')
    os.remove(f'{PATH}/result/series.jpg')


def get_text_from_image(image_file: str, reader: easyocr.Reader):
    return reader.readtext(image_file)


def get_text(reader: easyocr.Reader) -> dict:
    result = {}
    for file in os.listdir(f'{PATH}/result'):
        text = get_text_from_image(
            f'{PATH}/result/{file}',
            reader=reader
        )
        result[f'{file.split(".")[0]}'] = [r[1] + ' ' for r in text]
    return result


def main():
    model = load_model_yolo(
        model_path='models/yolov4-obj_best.weights',
        classes_path='classes.txt'
    )
    reader = load_model_easyocr(
        'custom_EasyOCR/model',
        'custom_EasyOCR/user_network',
        'custom_example'
    )
    img_path = 'obj1422.jpg'
    img_path = check_image(img_path)
    try:
        yolo_objects = model.predict(f'{PATH}/{img_path}')
        print(yolo_objects)
    except Exception as error:
        raise ValueError(f'{error}')
    get_images_after_yolo(yolo_objects, img_path)
    rotate_image()
    result = get_text(reader)
    for key, value in result.items():
        print(key, value)


if __name__ == '__main__':
    main()
    """reader = load_model_easyocr(
        'custom_EasyOCR/model',
        'custom_EasyOCR/user_network',
        'custom_example'
    )
    image = 'nmyxiC2S1gc.jpg'
    result = reader.readtext(image)
    for r in result:
        print(r[1])"""


