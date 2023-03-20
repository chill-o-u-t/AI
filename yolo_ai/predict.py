import os
from pathlib import Path

from models import Yolov4
from PIL import Image


def prepare_to_easyocr(model):
    dir = Path(__file__).parent
    for img in os.listdir(dir / 'prepare_images'):
        if img.split('.')[1] == 'jpg':
            result = model.predict(f'prepare_images/{img}')
            extract_obj_from_image(result, img)


def extract_obj_from_image(result, image_path):
    image = Image.open(f'prepare_images/{image_path}')
    for obj in result.values:
        extracted_image = image.crop(
            (int(obj[0]), int(obj[1]), int(obj[2]), int(obj[3]))
        )
        extracted_image.save(f'test/{image_path.split(".")[0]}_{obj[4]}.jpg')


if __name__ == '__main__':
    model = Yolov4(weight_path='yolov4-obj_best.weights',
                   class_name_path='classes.txt')
    image_path = 'obj174.jpg'
    result = model.predict(image_path)
    #prepare_to_easyocr(model=model)

