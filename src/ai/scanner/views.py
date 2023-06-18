import os


from PIL import Image
from io import BytesIO
import base64

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from starlette import status

from.easyocr import Reader


class PageTwo(APIView):
    def get(self, request):
        reader = Reader(
            ['ru'],
            model_storage_directory='custom_EasyOCR/model',
            user_network_directory='custom_EasyOCR/user_network',
            recog_network='custom_example'
        )
        context = ''
        if request.method == 'GET':
            try:
                img = Image.open(BytesIO(base64.b64decode(request.data)))
            except Exception as error:
                raise f'{error}'
            img.crop((1000, 350, 2100, 600)).save('tempdata/surname.jpg')
            img.crop((1150, 600, 2100, 700)).save('tempdata/name.jpg')
            img.crop((1150, 700, 2100, 800)).save('tempdata/secondname.jpg')
            img.crop((1050, 800, 1300, 900)).save('tempdata/gender.jpg')
            img.crop((1430, 800, 1950, 900)).save('tempdata/bdate.jpg')
            img.crop((1130, 880, 2150, 1220)).save('tempdata/city.jpg')
            for file in os.listdir('tempdata'):
                result = reader.readtext(f'tempdata/{file}')
                for digit in result:
                    context += digit[1].lower()
                context += '\n'
                os.remove(f'tempdata/{file}')
            content = {'text': context}
            return Response(content, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


"""class PageThree(APIView):
    def post(self, request):
        reader = Reader(
            ['ru'],
            model_storage_directory='custom_EasyOCR/model',
            user_network_directory='custom_EasyOCR/user_network',
            recog_network='custom_example'
        )
        context = ''
        if request.method == 'POST':
            img = Image.open(BytesIO(base64.b64decode(request.data)))
            img.crop((100, 550, 2150, 950)).save('ufms/surname.jpg')
            img.crop((480, 900, 1050, 1100)).save('tempdata/idate.jpg')
            img.crop((1400, 900, 1850, 1000)).save('tempdata/code.jpg')
            img.crop((2100, 600, 2300, 1500)).rotate(90, expand=True).save('tempdata/gender.jpg')
            for file in os.listdir('tempdata'):
                result = reader.readtext(f'tempdata/{file}')
                for digit in result:
                    context += digit[1].lower()
                context += '\n'
                os.remove(f'tempdata/{file}')
            content = {'text': context}
            return Response(content, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)"""
