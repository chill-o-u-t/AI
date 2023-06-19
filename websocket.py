import base64
import json
from io import BytesIO

import websockets


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
        await websocket.send(
            message=json.dumps(
                {
                    'Type': 'Response',
                    'Command': 'Set',
                    'Operand': 'TakePhoto',
                    'Param': 0
                }
            ),
        )
        res: str = await websocket.recv()
        decoded_data = BytesIO(base64.b64decode(res.split(':')[-1]))
        return decoded_data
