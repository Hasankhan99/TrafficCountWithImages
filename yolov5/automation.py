# stream = open("/home/am/Documents/yolov5/DetectionByCams.py")
# # stream = open("/Documents/yolov5/DetectionByCams.py")
# read_file = stream.read()
# exec(read_file)
import schedule
import numpy as np
import argparse
import cv2 as cv
import os
import datetime
from datetime import date
import json
import threading
import glob
import requests
from datetime import timedelta
from detect import detect
import requests
import json
import torch, gc



check= False
def auto():
    global check
    check =True


if __name__ == "__main__":
    
    schedule.every().day.at('23:00').do(auto)
    while (True):
        schedule.run_pending()
        if check:

            stream = open("/home/am/Documents/yolov5/FinalDetectionByCams.py")

            read_file = stream.read()
            exec(read_file)
            check = False




