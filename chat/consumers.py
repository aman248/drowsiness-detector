# chat/consumers.pyś
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import cv2
import dlib
from scipy.spatial import distance
from django.conf import settings
import base64
import numpy as np
class StreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.hog_face_detector = dlib.get_frontal_face_detector()
        self.dlib_facelandmark = dlib.shape_predictor("static/shape_predictor_68_face_landmarks.dat")
        self.q = Q(5)

    async def disconnect(self,close_code):
        pass

    async def receive(self,text_data):
        await self.new_method(text_data)

    async def new_method(self, text_data):
        im_bytes = base64.b64decode(text_data)
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.hog_face_detector(gray)
        if not faces:
            print('no face')
            self.q.add(0)
    
        for face in faces:

            face_landmarks = self.dlib_facelandmark(gray, face)
            leftEye = []
            rightEye = []

            for n in range(36,42):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                leftEye.append((x,y))

            for n in range(42,48):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                rightEye.append((x,y))


            left_ear = self.calculate_EAR(leftEye)
            right_ear = self.calculate_EAR(rightEye)

            EAR = (left_ear+right_ear)/2
            EAR = round(EAR,2)
            print(EAR)

            if EAR<0.26:
                self.q.add(1)
            else:
                self.q.add(0)

            if self.q.countValue(1) >= 4:
                await self.send('drowsy')
            else:
                await self.send('checking')

    def calculate_EAR(self,eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])
        ear_aspect_ratio = (A+B)/(2.0*C)
        return ear_aspect_ratio

        
class Q:
    def __init__(self,len):
        self.lis = [0]*len
        self.len = len
    def add(self,item):
        for i in range(1,self.len):
            self.lis[i-1] = self.lis[i]
        self.lis[self.len-1] = item
    def countValue(self,item):
        count = 0
        for i in self.lis:
            if i == item:
                count += 1
        return count
        


