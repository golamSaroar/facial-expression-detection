import cv2
from model import FacialExpressionModel
import numpy as np
import pafy
import base64
import io

facec = cv2.CascadeClassifier('app/artifact/haarcascade_frontalface_default.xml')
model = FacialExpressionModel("model.json", "app/artifact/model_weights.h5")
font = cv2.FONT_HERSHEY_SIMPLEX

def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

class VideoCamera(object):
    def __init__(self, video_id):
        if video_id is None:
            self.video = cv2.VideoCapture(0)
        else:
            url = "https://www.youtube.com/watch?v={}".format(video_id)
            vPafy = pafy.new(url)
            play = vPafy.getbest(preftype="mp4")
            self.video = cv2.VideoCapture(play.url)

    def __del__(self):
        self.video.release()

    # returns camera frames along with bounding boxes and predictions
    def get_frame(self):
        _, fr = self.video.read()
        gray_fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        faces = facec.detectMultiScale(gray_fr, 1.3, 5)

        for (x, y, w, h) in faces:
            fc = gray_fr[y:y+h, x:x+w]

            roi = cv2.resize(fc, (48, 48))
            pred = model.predict_emotion(roi[np.newaxis, :, :, np.newaxis])

            cv2.putText(fr, pred, (x, y), font, 1, (255, 255, 0), 2)
            cv2.rectangle(fr,(x,y),(x+w,y+h),(255,0,0),2)

        _, jpeg = cv2.imencode('.jpg', fr)
        return jpeg.tobytes()

class Image(object):
    def __init__(self, img, base64=False):
        if base64:
            self.image = data_uri_to_cv2_img(img)
        else:
            self.image = cv2.imread(img)

    def get_frame(self):
        gray_fr = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        faces = facec.detectMultiScale(gray_fr, 1.3, 5)

        for (x, y, w, h) in faces:
            fc = gray_fr[y:y+h, x:x+w]

            roi = cv2.resize(fc, (48, 48))
            pred = model.predict_emotion(roi[np.newaxis, :, :, np.newaxis])

            cv2.putText(self.image, pred, (x, y), font, 1, (255, 255, 0), 2)
            cv2.rectangle(self.image,(x,y),(x+w,y+h),(255,0,0),2)

        _, jpeg = cv2.imencode('.jpg', self.image)
        return io.BytesIO(jpeg)