import base64
import os
from io import BytesIO

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpclient
from PIL import Image

from easyocr import Reader


class WebSocketProxyHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        target_url = 'ws://localhost:91/echo'
        self.http_client = tornado.httpclient.AsyncHTTPClient()
        self.ws_client = tornado.websocket.websocket_connect(target_url, callback=self.on_ws_connect)

    async def on_ws_connect(self, future):
        self.ws = await future
        await self.listen()

    def on_message(self, message):
        self.ws.write_message(message)

    def on_close(self):
        self.ws.close()

    async def listen(self):
        reader = Reader(
            ['ru'],
            model_storage_directory='custom_EasyOCR/model',
            user_network_directory='custom_EasyOCR/user_network',
            recog_network='custom_example'
        )
        while True:
            message = await self.ws.read_message()

            if message is None:
                self.close()
                break
            if message == '{"Type":"Reply","Command":"Get","Operand":"Base64Image","Param":17,"Succeeded":"Y","Result":""}':
                context = []
                msg = await self.ws.read_message()
                r = msg.split(':')
                f = r[-5]
                decoded_data = BytesIO(base64.b64decode(f[18:]))

                await self.write_message(msg)
                res = await self.ws.read_message()

                img = Image.open(decoded_data)
                img.crop((1000, 200, 1700, 330)).save('tempdata/surname.jpg')
                img.crop((900, 370, 1750, 460)).save('tempdata/name.jpg')
                img.crop((900, 460, 1750, 560)).save('tempdata/secondname.jpg')
                img.crop((1800, 200, 1950, 1000)).rotate(90, expand=True).save('tempdata/series.jpg')

                for file in os.listdir('tempdata'):
                    result_ = reader.readtext(f'tempdata/{file}')
                    res_ = ''
                    for digit in result_:
                        res_ += digit[1].lower()
                    context.append(res_)
                    os.remove(f'tempdata/{file}')

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
                await self.write_message(result)
            else:
                await self.write_message(message)


class WebSocketProxyApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'', WebSocketProxyHandler),
        ]
        super().__init__(handlers)


if __name__ == '__main__':
    app = WebSocketProxyApplication()
    app.listen(90)  # изменить порт на 91
    tornado.ioloop.IOLoop.current().start()
