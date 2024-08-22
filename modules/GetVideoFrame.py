
def GetVideoFrame(VideoPath, start, end):
    with open(VideoPath, "rb") as video:
        video.seek(start)
        data = video.read(int(end) - int(start))
        return data