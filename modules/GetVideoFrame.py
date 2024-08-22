import cv2

def GetVideoFrame(VideoPath, start, end):
    with open(VideoPath, "rb") as video:
        video.seek(start)
        data = video.read(int(end) - int(start))
        return data


def GetChunkSize(PathToFile):
    VideoCapture = cv2.VideoCapture(PathToFile)
    WIDTH = VideoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
    HEIGHT = VideoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return [WIDTH, HEIGHT]