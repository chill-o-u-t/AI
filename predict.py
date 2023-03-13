import os

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
) -> object:
    try:
        reader = easyocr.Reader(
            ['ru'],
            model_storage_directory=model_directory,
            user_network_directory=user_directory,
            recog_network=recog_network
        )
    except Exception as error:
        raise 'При попытке загрузить модель easyocr возникла ошибка {error}'.format(error=error)
    return reader


def check_image(image_path: str) -> str:
    name, expansion = image_path.split('.')
    if expansion != 'jpg':
        image = Image.open(PATH / image_path).convert('RGB')
        image.save(f'{PATH}/{name}.jpg')
        os.remove(f'{PATH}/{image_path}')
        return f'{name}.jpg'
    return image_path


def get_images_after_yolo(yolo_objects, image_path: str) -> None:
    os.mkdir(f'{PATH}/result')
    image = Image.open(image_path)
    for obj in yolo_objects.values:
        extracted_image = image.crop(
            (int(obj[0]), int(obj[1]), int(obj[2]), int(obj[3]))
        )
        extracted_image.save(f'{PATH}/result/{obj[4]}.jpg')


def rotate_image() -> None:
    image = Image.open(f'{PATH}/result/series.jpg')
    img = image.rotate(90, expand=True)
    img.save(f'{PATH}/result/_series')
    os.remove(f'{PATH}/result/series.jpg')


def get_text_from_image(image_file: str, reader: easyocr.Reader):
    return reader.readtext(image_file)


def get_text(reader: easyocr.Reader) -> dict:
    result = {}
    for file in os.listdir(f'{PATH}/result'):
        result[f'{file.split(".")[0]}'] = get_text_from_image(
            f'{PATH}/result/{file}',
            reader=reader
        )
    return result


def main():
    model = load_model_yolo('test', 'test')
    reader = load_model_easyocr(
        'test', 'test', 'test'
    )
    img_path = ''
    img_path = check_image(img_path)
    try:
        yolo_objects = model.predict(f'{PATH}/{img_path}')
    except Exception as error:
        raise f'{error}'
    get_images_after_yolo(yolo_objects, img_path)
    rotate_image()
    result = get_text(reader)
    print(result)





