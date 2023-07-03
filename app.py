import os
import base64
from io import BytesIO

from PIL import Image
from flask import Flask, request, jsonify
# from flasgger import Swagger


from easyocr import Reader

app = Flask(__name__)

# swagger = Swagger(app, template_file='test.json')


@app.route('/echo', methods=['POST'])
def echo():
    reader = Reader(
        ['ru'],
        model_storage_directory='custom_EasyOCR/model',
        user_network_directory='custom_EasyOCR/user_network',
        recog_network='custom_example'
    )
    context = {}
    decoded_data = BytesIO(base64.b64decode(request.data['data']))
    img = Image.open(decoded_data)
    img.crop((1000, 350, 2100, 600)).save('tempdata/surname.jpg')
    img.crop((1150, 600, 2100, 700)).save('tempdata/name.jpg')
    img.crop((1150, 700, 2100, 800)).save('tempdata/secondname.jpg')
    img.crop((1050, 800, 1300, 900)).save('tempdata/gender.jpg')
    img.crop((1430, 800, 1950, 900)).save('tempdata/bdate.jpg')
    img.crop((2100, 400, 2300, 1300)).rotate(90, expand=True).save('tempdata/series.jpg')
    for file in os.listdir('tempdata'):
        result = reader.readtext(f'tempdata/{file}')
        res = ''
        for digit in result:
            res += digit[1].lower()
        context += {str(file.split('.')[0]): res}
        os.remove(f'tempdata/{file}')
    buffered = BytesIO()
    img.crop((250, 400, 1000, 1200)).save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    context['image'] = img_str
    return jsonify(context)


if __name__ == '__main__':
    app.run(host='localhost', port=90, debug=True)
