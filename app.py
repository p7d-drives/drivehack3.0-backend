from pathlib import Path
from fastapi import FastAPI
from fastapi import Request, Response
from fastapi import Header
from fastapi import UploadFile
from fastapi import File
from fastapi.templating import Jinja2Templates

from modules.GetFrameFromVideo import *
from modules.GetVideoFrame import *
from modules.ConvertLinesToArray import *

from models.models import *

from uuid import uuid4

from typing import Annotated

import cv2
import string

def RandomString():
    answer = ""
    for i in range(16):
        answer += random.choice(string.ascii_letters + string.digits)
    return answer + ".mp4"

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DEFAULTPATH = "/home/jtr1k/drivehack/drivehack-backend"
PathToFrame = DEFAULTPATH + "/preview/"
VideoPath = DEFAULTPATH + "/video/"
VideoCapture = cv2.VideoCapture(VideoPath + "SampleVideo_1280x720_20mb.mp4")
CHUNK_SIZE = VideoCapture.get(cv2.CAP_PROP_FRAME_WIDTH) * VideoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)
sessions = {} 

@app.get("/api/video/watch")
async def video_endpoint(request: Request, range: str = Header(None)):
    cookie = request.cookies.get("cookie")
    if cookie == None:
        return Response("No files uploaded", status_code=500)
    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE
    filename = sessions[cookie]
    filesize = str(filename.stat().st_size)
    data = GetVideoFrame(filename, start, end) 
    headers = {
        'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
        'Accept-Ranges': 'bytes'
    }
    return Response(data, status_code=206, headers=headers,media_type="video/mp4")

@app.post("/api/video/upload")
async def Upload(request: Request, file: Annotated[bytes, File()]):
    cookie = request.cookies.get("cookie")
    if (cookie == None):
        user_uuid = uuid4()
        sessions[user_uuid] = ""
        response.set_cookie(key = "cookie", value = user_uuid)
        return response
    filename = Path(VideoPath + RandomString())
    print("SVOZZZ")
    sessions[cookie] = filename
    UploadedFile = open(filename, "wb")
    UploadedFile.write(file)
    UploadedFile.close()



@app.get("/api/video/preview")
async def Preview(request: Request):
    cookie = request.cookies.get("cookie")
    FramePath = GetFrameFromVideo(VideoPath, PathToFrame)
    PreviewFile = open(FramePath, "rb").read()
    return Response(content=PreviewFile, media_type="image/jpg")

    
@app.post("/api/render/lines")
async def GetLines(lines: Lines):
    answer = ConvertLinesToArray(lines.lines)
    # connect with ML model
