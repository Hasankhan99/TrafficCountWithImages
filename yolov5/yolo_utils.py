import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os
from datetime import date
import schedule
import requests
import json
import threading
import itertools

from collections import deque
from imutils.video import VideoStream
import imutils


person_pre=[]
first_loock = 0
count = 0
count_object = []
num = 0
total_count = []
temp_count = 0
clean_area = 0
temp_count_array =[]
temp_count_tem = 0
total_count_h = []
count_object_h=[]







def show_image(img):
    cv.imshow("Image", img)
    cv.waitKey(0)
    
def check_indexes(array):
    ret = False    
    for a, b in itertools.combinations(array, 2):
        if a<=b:
            ret = True
        else:
            return False
 

def draw_labels_and_boxes(img, boxes, confidences, classids, idxs, colors, labels):
    # If there are any detections
    global num
    num=0
    
    if len(idxs) > 0:
        global name
        global count
        global count_object_h
        global temp_count
        global clean_area
        global person_pre
        global total_count
        global temp_count_array
        global total_count_h
        temp_count=0
        global count_object
        for i in idxs.flatten():
            if labels[classids[i]]!='person':
                continue
            # Get the bounding box coordinates
            x, y = boxes[i][0], boxes[i][1]
            w, h = boxes[i][2], boxes[i][3]
            fh, fw = img.shape[:2]
            
            # Get the unique color for this class
            color = [int(c) for c in colors[classids[i]]]
            if labels[classids[i]]=='person':
                coords = list([x,y,w,h])
                num+=1
               
                # print('objects:{}, arrays:{} count:{}, prW:{}, prH:{} '.format(len(count_object), person_pre, count, person_w, person_h ))
                
                cv.rectangle(img, (x, y), (x+w, y+h), color, 2)
                text = "{}: {:4f}".format(labels[classids[i]], confidences[i])
               
    cv.putText(img, 'Current Counted: {}'.format(num), (210, 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    # cv.line(img, (170, 25), (220, 25), (0,0,255), 2)
    return img,num



def generate_boxes_confidences_classids(outs, height, width, tconf):
    boxes = []
    confidences = []
    classids = []

    for out in outs:
        for detection in out:
            #print (detection)
            #a = input('GO!')
            
            # Get the scores, classid, and the confidence of the prediction
            scores = detection[5:]
            classid = np.argmax(scores)
            confidence = scores[classid]
            
            # Consider only the predictions that are above a certain confidence level
            if confidence > tconf:
                # TODO Check detection
                box = detection[0:4] * np.array([width, height, width, height])
                centerX, centerY, bwidth, bheight = box.astype('int')

                # Using the center x, y coordinates to derive the top
                # and the left corner of the bounding box
                x = int(centerX - (bwidth / 2))
                y = int(centerY - (bheight / 2))

                # Append to list
                boxes.append([x, y, int(bwidth), int(bheight)])
                confidences.append(float(confidence))
                classids.append(classid)
                
    return boxes, confidences, classids

def infer_image(net, layer_names, height, width, img, colors, labels, confidence, threshold,
            boxes=None, confidences=None, classids=None, idxs=None, infer=True):
    
    if infer:
        # Contructing a blob from the input image
        blob = cv.dnn.blobFromImage(img, 1 / 255.0, (416, 416), 
                        swapRB=True, crop=False)

        # Perform a forward pass of the YOLO object detector
        net.setInput(blob)

        # Getting the outputs from the output layers
        start = time.time()
        outs = net.forward(layer_names)
        end = time.time()

        # Boxes

        # if FLAGS.show_time:
        # print ("[INFO] YOLOv3 took {:6f} seconds".format(end - start))

        
        # Generate the boxes, confidences, and classIDs
        boxes, confidences, classids = generate_boxes_confidences_classids(outs, height, width, confidence)
        
        # Apply Non-Maxima Suppression to suppress overlapping bounding boxes
        idxs = cv.dnn.NMSBoxes(boxes, confidences, confidence, threshold)

    if boxes is None or confidences is None or idxs is None or classids is None:
        raise '[ERROR] Required variables are set to None before drawing boxes on images.'
        
    # Draw labels and boxes on the image
    img,num= draw_labels_and_boxes(img, boxes, confidences, classids, idxs, colors, labels)

    return img, boxes, confidences, classids, idxs,num
