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
    context = []
    decoded_data, res = await get_images()

    img = Image.open(decoded_data)
    img.crop((1000, 200, 1700, 330)).save('tempdata/surname.jpg')
    img.crop((900, 370, 1750, 460)).save('tempdata/name.jpg')
    img.crop((900, 460, 1750, 560)).save('tempdata/secondname.jpg')
    img.crop((1800, 200, 1950, 1000)).rotate(90, expand=True).save('tempdata/series.jpg')

    for file in os.listdir('tempdata'):
        result_ = reader.readtext(f'tempdata/{file}')
        res_ = ''
        for digit in result_:
            #print(digit[1].lower())
            res_ += digit[1].lower()
        context.append(res_)
        #os.remove(f'tempdata/{file}')
    print(context)
    tmp = res[:70]
    tmp += '{'
    temp = res.split('{')[2].split(',')
    for i in range(4):
        tmp += f'{temp[i]},'
    tmp += f'"The passport number from MRZ":"{context[3]}",'
    tmp += f'"National Name": "{context[3]} {context[0]} {context[1]}",'
    for i in range(7, len(temp)):
        tmp += f'{temp[i]},'
    result = tmp[0:-1]
    print(result)

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='localhost', port=92, debug=True)
