# chat/consumers.py
from chat.views import Is_d
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import cv2
import dlib
from scipy.spatial import distance
import os 
import asyncio
from django.conf import settings
import threading
import base64
import numpy as np
class StreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.hog_face_detector = dlib.get_frontal_face_detector()
        self.dlib_facelandmark = dlib.shape_predictor("static/shape_predictor_68_face_landmarks.dat")

        self.i = 0
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
                await self.send('drowsy.....')
            else:
                await self.send('checking.....')
    def calculate_EAR(self,eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])
        ear_aspect_ratio = (A+B)/(2.0*C)
        return ear_aspect_ratio

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.check = True
        self.is_d = False

        await self.accept()
        self.t = threading.Thread(target=self.dece)
        self.t.start()

    async def disconnect(self, close_code):
        # Leave room group
        self.check = False
        self.t.join()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print(message)
        a = self.is_d
        if message == 'start':
            self.check = True
            self.dec()
            print('thread started')
        elif message == 'stop':
            self.check = False
            self.t.join()
        print(a)
        await self.send(text_data=json.dumps({
            'message': 'drowsy' + str(a)
        }))
    def calculate_EAR(self,eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])
        ear_aspect_ratio = (A+B)/(2.0*C)
        return ear_aspect_ratio
    async def dec(self):
        print('goooooooooooooooooo')
        await self.dece()
    async def dec2(self):
        print('dec2 started')
        await self.send(text_data=json.dumps({
            'message': 'welcome' + str(i)
        }))

    def dece(self):
        print('dece started')
        cap = cv2.VideoCapture(0)
        file_ = os.path.join(settings.BASE_DIR,"shape_predictor_68_face_landmarks.dat" )
        hog_face_detector = dlib.get_frontal_face_detector()
        dlib_facelandmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        while self.check:
            _, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = hog_face_detector(gray)
            for face in faces:

                face_landmarks = dlib_facelandmark(gray, face)
                leftEye = []
                rightEye = []

                for n in range(36,42):
                    x = face_landmarks.part(n).x
                    y = face_landmarks.part(n).y
                    leftEye.append((x,y))
                    next_point = n+1
                    if n == 41:
                        next_point = 36
                    x2 = face_landmarks.part(next_point).x
                    y2 = face_landmarks.part(next_point).y
                    cv2.line(frame,(x,y),(x2,y2),(0,255,0),1)

                for n in range(42,48):
                    x = face_landmarks.part(n).x
                    y = face_landmarks.part(n).y
                    rightEye.append((x,y))
                    next_point = n+1
                    if n == 47:
                        next_point = 42
                    x2 = face_landmarks.part(next_point).x
                    y2 = face_landmarks.part(next_point).y
                    cv2.line(frame,(x,y),(x2,y2),(0,255,0),1)

                left_ear = self.calculate_EAR(leftEye)
                right_ear = self.calculate_EAR(rightEye)

                EAR = (left_ear+right_ear)/2
                EAR = round(EAR,2)
                self.is_d = False
                if EAR<0.26:
                    cv2.putText(frame,"DROWSY",(20,100),
                        cv2.FONT_HERSHEY_SIMPLEX,3,(0,0,255),4)
                    cv2.putText(frame,"Are you Sleepy?",(20,400),
                        cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,255),4)
                    self.is_d = True