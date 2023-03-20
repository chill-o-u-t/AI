import base64
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post('/image')
async def image_to_text(image: str = Body(...)):
    binary_image = base64.b64decode(image)
    text = ''
    return JSONResponse(content={"text": text})
