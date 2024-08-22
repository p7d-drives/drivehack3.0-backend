import cv2
import os

def GetFrameFromVideo(PathToVideo : str, PathToFrame : str) -> str:
    FrameName = os.path.splitext(os.path.basename(PathToVideo))[0]
    try:
        VideoCapture = cv2.VideoCapture(PathToVideo)
        success, image = VideoCapture.read()
        if not success:
            return ""
        cv2.imwrite(f"{PathToFrame}/{FrameName}.jpg", image)
        return f"{PathToFrame}/{FrameName}.jpg"
    except:
        return ""

if __name__ == "__main__":
    GetFrameFromVideo(input(), input())
