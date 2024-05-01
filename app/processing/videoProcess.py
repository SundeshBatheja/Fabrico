import cv2
import pandas as pd
from ultralytics import YOLO
import cvzone
import numpy as np
from app.processing.tracker import *
import math
import os

def video_detection(video):
    cap = cv2.VideoCapture(video)
    model = YOLO('app/processing/best.pt')
    my_file = open("app/processing/coco.txt", "r")
    data = my_file.read()
    class_list = data.split("\n")

    count = 0

    tracker = Tracker()
    tracker1 = Tracker()
    tracker2 = Tracker()
    cy1 = 280
    cy2 = 250
    offset = 8
    upcar = {}
    downcar = {}
    countercarup = []
    countercardown = []
    downbus = {}
    counterbusdown = []
    upbus = {}
    counterbusup = []
    downtruck = {}
    countertruckdown = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        if count % 3 != 0:
            continue
        frame = cv2.resize(frame, (300, 500))

        results = model.predict(frame)
        a = results[0].boxes.data
        px = pd.DataFrame(a).astype("float")

        list = []
        list1 = []
        list2 = []
        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]
            if 'hole' in c:
                list.append([x1, y1, x2, y2])
            elif 'stain' in c:
                list1.append([x1, y1, x2, y2])
            elif 'line' in c:
                list2.append([x1, y1, x2, y2])

        bbox_idx = tracker.update(list)
        for bbox in bbox_idx:
            x3, y3, x4, y4, id1 = bbox
            cx3 = int(x3 + x4) // 2
            cy3 = int(y3 + y4) // 2
            if cy1 < (cy3 + offset) and cy1 > (cy3 - offset):
                upcar[id1] = (cx3, cy3)
            if id1 in upcar:
                if cy2 < (cy3 + offset) and cy2 > (cy3 - offset):
                    cv2.circle(frame, (cx3, cy3), 4, (255, 0, 0), -1)
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 255), 2)
                    cvzone.putTextRect(frame, f'{id1}', (x3, y3), 1, 1)
                    if countercarup.count(id1) == 0:
                        countercarup.append(id1)

            if cy2 < (cy3 + offset) and cy2 > (cy3 - offset):
                downcar[id1] = (cx3, cy3)
            if id1 in downcar:
                if cy2 < (cy3 + offset) and cy2 > (cy3 - offset):
                    cv2.circle(frame, (cx3, cy3), 4, (255, 0, 255), -1)
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 0), 2)
                    cvzone.putTextRect(frame, f'{id1}', (x3, y3), 1, 1)
                    if countercardown.count(id1) == 0:
                        countercardown.append(id1)

        cv2.line(frame, (1, cy1), (300, cy1), (0, 255, 0), 2)
        cv2.line(frame, (3, cy2), (300, cy2), (0, 0, 255), 2)
        cvzone.putTextRect(frame, f'Holes : {len(countercardown)}', (50, 160), 1, 1)
        cvzone.putTextRect(frame, f'Stains : {len(countercardown)}', (50, 130), 1, 1)
        cvzone.putTextRect(frame, f'Lines : {len(countercardown)}', (200, 160), 1, 1)
        cvzone.putTextRect(frame, f'Knots : {len(countercardown)}', (200, 130), 1, 1)

        yield frame
        yield len(countercardown)

    cap.release()