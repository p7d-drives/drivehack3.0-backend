from pathlib import Path
from fastapi import FastAPI
from fastapi import Request, Response, HTTPException
from fastapi import Header
from fastapi.responses import RedirectResponse 
from fastapi import File
from fastapi.templating import Jinja2Templates

from subprocess import Popen

from modules.GetFrameFromVideo import *
from modules.GetVideoFrame import *
from modules.ConvertLinesToArray import *
from modules.GenerateRandomString import *

from models.models import *

from uuid import uuid4

from typing import Annotated

import os

MODEL_RUN = ['/home/ninvoido/processor/venv/bin/python3', '/home/ninvoido/processor/lib.py', '--no-tqdm']

app = FastAPI()

templates = Jinja2Templates(directory="templates")

DEFAULTPATH = os.path.dirname(__file__)
PathToFrame = DEFAULTPATH + "/preview/"
VideoPath = DEFAULTPATH + "/video/"
JsonPath = DEFAULTPATH + "/json/"

sessions = {}

@app.get("/api/video/watch")
async def video_endpoint(response: Response, request: Request, range: str = Header(None)):
    cookie = request.cookies.get("cookie")

    if cookie is None:
        return Response("No files uploaded", status_code=500)


    filename = sessions[cookie]
    filesize = str(filename.stat().st_size)

    WIDTH, HEIGHT = GetChunkSize(filename)
    CHUNK_SIZE = WIDTH * HEIGHT

    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE
    data = GetVideoFrame(filename, start, end)

    headers = {
        'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
        'Accept-Ranges': 'bytes'
    }

    return Response(data, status_code=206, headers=headers,media_type="video/mp4")

@app.post("/api/video/upload")
async def Upload(response: Response, request: Request, file: Annotated[bytes, File()]):
    cookie = request.cookies.get("cookie")
    if (cookie is None):
        user_uuid = str(uuid4())
        sessions[user_uuid] = ""
        response.set_cookie(key = "cookie", value = user_uuid)
        cookie = user_uuid
    filename = Path(VideoPath + RandomString())
    print(cookie)
    sessions[cookie] = filename
    print(filename)
    print(cookie)
    UploadedFile = open(filename, "wb")
    UploadedFile.write(file)
    UploadedFile.close()
    return "OK"



@app.get("/api/video/preview")
async def Preview(request: Request):
    cookie = request.cookies.get("cookie")
    if (cookie is None):
        return "No file uploaded"
    VideoFilePath = sessions[cookie]
    FramePath = GetFrameFromVideo(VideoFilePath, PathToFrame)
    PreviewFile = open(FramePath, "rb").read()
    return Response(content=PreviewFile, media_type="image/jpg")


@app.get("/api/video/data")
async def get_data(request: Request):
    cookie = request.cookies.get("cookie")
    if cookie is None:
        return "You haven't sent any files"
    # connect with ML model

    filename_json = cookie + '.out.json'
    if not os.path.exists(filename_json):
        raise HTTPException(status_code=404)

    with open(filename_json) as fp:
        import json
        return json.load(fp)


@app.post("/api/render/lines")
async def GetLines(request: Request, lines: Lines):
    cookie = request.cookies.get("cookie")
    print(lines.lines)
    if cookie is None:
        return "You haven't sent any files"
    answer = ConvertLinesToArray(lines.lines)
    print(answer)
    # connect with ML model

    with open(cookie + '.lines.json', 'w') as fp:
        import json
        json.dump(lines, fp)  # ENSURE FORMAT

    filename_in = cookie
    filename_out = cookie + '.out'
    filename_json = cookie + '.out.json'

    Popen(MODEL_RUN + ['-i', filename_in, '-o', VideoPath + '/' + os.path.basename(filename_out), '-j', JsonPath + '/' + os.path.basename(filename_json), '-L', cookie + '.lines.json'], shell=False)

    return 'ok'

@app.get("/api/video/get/{user_uuid}")
async def ChangeCookie(response: Response, user_uuid):
    response.set_cookie(key = "cookie", value = user_uuid)
    return RedirectResponse("http://127.0.0.1/api/video/watch")
