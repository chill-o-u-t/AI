from PIL import Image

from pathlib import Path
import os


if __name__ == '__main__':
    path = Path(__file__).parent / 'prepare_images'
    for file in os.listdir(path):
        img = Image.open(path / file).convert('RGB')
        name = file.split('.')[0]
        img.save(f'{path}/{name}.jpg')
