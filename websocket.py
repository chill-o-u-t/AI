import base64
import json
import asyncio
from io import BytesIO

import websockets
from PIL import Image


async def get_images():
    uri = 'ws://127.0.0.1:91/echo'
    async with websockets.connect(uri) as websocket:
        await websocket.send(
            message=json.dumps(
                {
                    'Type': 'Response',
                    'Command': 'Get',
                    'Operand': 'Base64Image',
                    'Param': 17
                }
            ),
        )
        res = await websocket.recv()
        print(res)
        res = await websocket.recv()
        r = res.split(':')
        f = r[-5]
        res: str = await websocket.recv()
        tmp = res[:70]
        tmp += '{'
        temp = res.split('{')[2].split(',')
        for i in range(4):
            tmp += f'{temp[i]},'
        tmp += f'"The passport number from MRZ":"[]",'
        tmp += f'"National Name": "[] [] []",'
        for i in range(7, len(temp)):
            tmp += f'{temp[i]},'
        result = tmp[0:-1]

        dd = BytesIO(base64.b64decode(f[18:]))
        return dd, res


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(get_images())
