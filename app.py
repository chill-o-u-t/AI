import os

from PIL import Image
from flask import Flask, request, jsonify
from flasgger import Swagger


from easyocr import Reader
from websocket import get_images

app = Flask(__name__)

swagger = Swagger(app, template_file='test.json')


@app.route('/echo', methods=['GET'])
async def echo():
    reader = Reader(
        ['ru'],
        model_storage_directory='custom_EasyOCR/model',
        user_network_directory='custom_EasyOCR/user_network',
        recog_network='custom_example'
    )
    context = {}
    decoded_data = await get_images()
    img = Image.open(decoded_data)
    img.crop((1000, 350, 2100, 600)).save('tempdata/surname.jpg')
    img.crop((1150, 600, 2100, 700)).save('tempdata/name.jpg')
    img.crop((1150, 700, 2100, 800)).save('tempdata/secondname.jpg')
    img.crop((1050, 800, 1300, 900)).save('tempdata/gender.jpg')
    img.crop((1430, 800, 1950, 900)).save('tempdata/bdate.jpg')
    img.crop((1130, 880, 2150, 1220)).save('tempdata/city.jpg')
    # todo: borders of series, rotate it
    img.crop((0, 0, 10, 10)).save('tempdata/series.jpg')
    for file in os.listdir('tempdata'):
        result = reader.readtext(f'tempdata/{file}')
        res = ''
        for digit in result:
            res += digit[1].lower()
        context += {str(file.split('.')[0]): res}
        os.remove(f'tempdata/{file}')
        print(context)
    return jsonify(context)


if __name__ == '__main__':
    app.run(host='localhost', port=92, debug=True)
