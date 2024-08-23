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

from stream import range_requests_response

import os

MODEL_RUN = ['/home/ninvoido/processor/venv/bin/python3', '/home/ninvoido/processor/lib.py', '--no-tqdm']

app = FastAPI(title='p7dtTrm AI')

templates = Jinja2Templates(directory="templates")

DEFAULTPATH = os.path.dirname(__file__)
PathToFrame = DEFAULTPATH + "/preview/"
VideoPath = DEFAULTPATH + "/video/"
JsonPath = DEFAULTPATH + "/json/"

OUT_SUFFIX = '.out.mp4'
OUT_JSON_SUFFIX = '.out.json'
LINES_JSON_SUFFIX = '.lines.json'

sessions = {'loaded-video': '/home/ninvoido/drivehack3.0-backend/video/drivehack-1-60s.mp4'}

@app.get("/api/video/watch")
async def video_endpoint(response: Response, request: Request, range: str = Header(None)):
    cookie = request.cookies.get("cookie")

    if cookie is None:
        return Response("No files uploaded", status_code=404)


    filename = Path(sessions[cookie])
    filesize = str(filename.stat().st_size)

    # return range_requests_response(request, file_path=filename, content_type='video/mp4')

    fp = open(filename, 'rb').read()
    return Response(content=fp, media_type='video/mp4')

    # WIDTH, HEIGHT = GetChunkSize(filename)
    # CHUNK_SIZE = WIDTH * HEIGHT

    # start, end = range.replace("bytes=", "").split("-")
    # start = int(start)
    # end = int(end) if end else start + CHUNK_SIZE
    # data = GetVideoFrame(filename, start, end)

    # headers = {
    #     'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
    #     'Accept-Ranges': 'bytes'
    # }

    # return Response(data, status_code=206, headers=headers,media_type="video/mp4")

@app.get("/api/video/watch/out")
async def output_video_endpoint(response: Response, request: Request, range: str = Header(None)):
    cookie = request.cookies.get("cookie")

    if cookie is None:
        return Response("No files uploaded", status_code=500)


    filename = Path(sessions[cookie] + OUT_SUFFIX)
    while True:
        try:
            filesize = str(filename.stat().st_size)
        except FileNotFoundError:
            await asyncio.sleep(0.5)
        else:
            break

    fp = open(filename, 'rb').read()

    return Response(content=fp, media_type='video/mp4')

    # WIDTH, HEIGHT = GetChunkSize(filename)
    # CHUNK_SIZE = WIDTH * HEIGHT

    # start, end = range.replace("bytes=", "").split("-")
    # start = int(start)
    # end = int(end) if end else start + CHUNK_SIZE
    # data = GetVideoFrame(filename, start, end)

    # headers = {
    #     'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
    #     'Accept-Ranges': 'bytes'
    # }

    # return Response(data, status_code=206, headers=headers,media_type="video/mp4")



@app.post("/api/video/upload")
async def Upload_video(response: Response, request: Request, file: Annotated[bytes, File()]):
    cookie = request.cookies.get("cookie")
    if (cookie is None):
        user_uuid = str(uuid4())
        sessions[user_uuid] = ""
        response.set_cookie(key = "cookie", value = user_uuid)
        cookie = user_uuid
    filename = VideoPath + RandomString()
    print(cookie)
    sessions[cookie] = filename
    print(filename)
    print(cookie)
    UploadedFile = open(filename, "wb")
    UploadedFile.write(file)
    UploadedFile.close()
    return "OK"



@app.get("/api/video/preview")
async def Preview_video(request: Request):
    cookie = request.cookies.get("cookie")
    if (cookie is None):
        return "No file uploaded"
    VideoFilePath = sessions[cookie]
    FramePath = GetFrameFromVideo(VideoFilePath, PathToFrame)
    PreviewFile = open(FramePath, "rb").read()
    return Response(content=PreviewFile, media_type="image/jpg")


@app.get("/api/video/data")
async def get_json_data(request: Request):
    cookie = request.cookies.get("cookie")
    if cookie is None:
        return "You haven't sent any files"
    # connect with ML model

    filename_json = sessions[cookie] + OUT_JSON_SUFFIX
    if not os.path.exists(filename_json):
        raise HTTPException(status_code=404)

    with open(filename_json) as fp:
        import json
        return json.load(fp)


@app.post("/api/render/lines")
async def set_zone_lines(request: Request, lines: Lines):
    cookie = request.cookies.get("cookie")
    print(lines.lines)
    if cookie is None:
        return "You haven't sent any files"
    X, Y = GetChunkSize(sessions[cookie])
    for i in range(len(lines.lines)):
        lines.lines[i]["start"] = [lines.lines[i]["start"][0] * X, lines.lines[i]["start"][1] * Y]
        lines.lines[i]["finish"] = [lines.lines[i]["finish"][0] * X, lines.lines[i]["finish"][1] * Y]
    print(lines.lines)

    # connect with ML model

    with open(sessions[cookie] + LINES_JSON_SUFFIX, 'w') as fp:
        import json
        json.dump(lines.lines, fp)  # ENSURE FORMAT

    filename_in = sessions[cookie]
    filename_out = filename_in + OUT_SUFFIX
    filename_json = filename_in + OUT_JSON_SUFFIX

    Popen(MODEL_RUN + ['-i', filename_in, '-o', filename_out, '-j', filename_json, '-L', sessions[cookie] + LINES_JSON_SUFFIX], shell=False)
    return 'ok'

@app.get("/api/video/get/{user_uuid}")
async def get_video_by_uuid(response: Response, user_uuid):
    response.set_cookie(key = "cookie", value = user_uuid)
    return RedirectResponse("/api/video/watch/out")


@app.get("/api/video/get_by_key/{user_key}")
async def get_video_by_uuid(response: Response, user_key):
    key = str(uuid4())
    sessions[key] = VideoPath + user_key + '.mp4'
    print(key)
    response.set_cookie(key = "cookie", value = key)
    return 'ok'
