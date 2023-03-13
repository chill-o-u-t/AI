from PIL import Image
from pathlib import Path
import os


path = Path(__file__).parent / 'test'

if __name__ == '__main__':
    for file in os.listdir(path):
        print(file)
        obj1 = file.split('.')[0]
        obj2 = obj1.split('_')[1]
        if obj2 == 'series':
            print('1')
            image = Image.open(f'test/{file}')
            img = image.rotate(90, expand=True)
            img.save(f'test/__{file}')
