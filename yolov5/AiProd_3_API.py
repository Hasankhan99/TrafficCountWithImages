import numpy as np
# import argparse
import cv2 as cv
# import time
import os
# from yolo_utils import infer_image, show_image
# import schedule
import datetime
from datetime import date
import json
import threading
import glob
import requests
from datetime import timedelta
from modify_detect import detect
total=[0]
totalcount=0
totalcount_h=0
current=[0]
Peoplecount=[0]
Peoplecount_h=[0]
globalDate = ''

import requests
import json
# import torch, gc
import sqlite3

import time
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadImages
from utils.general import check_img_size, non_max_suppression, scale_coords, xyxy2xywh, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, time_synchronized


from dbConnection import selectAllStores, getMainSetting, create_connection, CheckPreData, ErrorLog

globalDate = '2021-06-01'

def setGlobalDate():
    global globalDate
    today = date.today() 
    yesterday = today - timedelta(days = 1) 
    globalDate = date.today().strftime('%Y-%m-%d') 

    current_hour = datetime.datetime.now().strftime("%H:%M:%S").split(':')[0]
    if int(current_hour)<12: # PM
        globalDate= date.today().strftime('%Y-%m-%d') 
    else:
        today = date.today() 
        yesterday = today - timedelta(days = 1) 
        globalDate = yesterday.strftime('%Y-%m-%d')



print('================================================',globalDate)
def localDB(storuid,totalcounts, totalcounts_h, Hour, status=False):  
    global current_h,Peoplecount_h,total_h,totalcount_h,check
    global current,Peoplecount,total,totalcount
    conn = sqlite3.connect('20210330_50.db')
    print("Opened database successfully")

    conn.execute('CREATE TABLE  IF NOT EXISTS TEST(ID INTEGER PRIMARY KEY AUTOINCREMENT, storeuid TEXT,totalcount TEXT, hourlycount  TEXT, time TEXT, date TEXT)')
    print("Table created successfully")

    if status:
        # conn.execute('insert into TEST (storeuid,totalcount,hourlycount,time,date) values ("'+str(storuid)+'","'+str(totalcounts)+'","'+str(totalcounts_h)+'","'+str(Hour)+'", "'+str(yesterday)+'")')
        conn.execute('insert into TEST (storeuid,totalcount,hourlycount,time,date) values ("'+str(storuid)+'","'+str(totalcounts)+'","'+str(totalcounts_h)+'","'+str(Hour)+'", "20210121")')
    
    else:
        # conn.execute('insert into TEST (storeuid,totalcount,hourlycount,time,date) values ("'+str(storuid)+'","0","'+str(totalcounts_h)+'","'+str(Hour)+'", "'+str(yesterday)+'")')
        conn.execute('insert into TEST (storeuid,totalcount,hourlycount,time,date) values ("'+str(storuid)+'","0","'+str(totalcounts_h)+'","'+str(Hour)+'", "20210121")')
    conn.commit()
    conn.close()
    # TOTAL COUNT
    if status:
        totalcount=0
        current.clear()
        current=[0]
        total.clear()
        total=[0]
        Peoplecount.clear()
        Peoplecount=[0]
        print('TOTAL API CALLED')

    # HOURLY
    totalcount_h=0
    Peoplecount_h.clear()
    Peoplecount_h=[0]
    print('Hourly API CALLED')


def grandtotal():
    global total,current,totalcount,totalcount_h
    current.append(max(total))
    total.clear()
    total=[0]

    x=current[-1]
    y=current[-2]
     
    if x>y  and y>0:
        count=(x-y)
        print("Add",count)
        Peoplecount.append(count)
        Peoplecount_h.append(count)
    else:
        print("No Change")
    totalcount_h=sum(Peoplecount_h)
    totalcount=sum(Peoplecount)

check=''

def API_Call(suid):
    global current,Peoplecount,total,totalcount, today, yesterday
   
    api_token = "http://3.18.96.94/DeepScienceApi/api/Surveillance/InsertStoreCountDataWithHour/"
    # today = date.today() 
    yesterday = today - timedelta(days = 1) 
    api_token=api_token + str('Store') + '/'   # store name 
    api_token=api_token + str(suid) + '/'          # store id 
    api_token=api_token + str(totalcount) + '/'          #  total in 
    api_token=api_token + str(totalcount) + '/'          # total out 
    api_token=api_token + str(date) + '/'      #  Date 
    api_token=api_token + str('23')           # total out 
    
    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(api_token)}
    def get_result():           
        response = requests.post(api_token, headers=headers)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None
                
    fetch_result = get_result()
    if fetch_result is not None:
        #print("API:",api_token)
        print("Here's your info: ")
        for k, v in fetch_result.items():
            print('{0}:{1}'.format(k, v))

        Peoplecount.clear()
        Peoplecount=[0]
        
    else:
        #print("API:",api_token)
        print('[!] Request Failed')

#------------------HourlyAPI Start--------------------------#

def Hourly_API_Call(suid,Hour, date):
    global Peoplecount_h,totalcount_h     

    api_token = "http://3.18.96.94/DeepScienceApi/api/Surveillance/InsertStoreCountDataWithHour/"
    # today = date.today() 
    # yesterday = today - timedelta(days = 1) 
    api_token=api_token + str('Store') + '/'   # store name 
    api_token=api_token + str(suid) + '/'          # store id 
    api_token=api_token + str(totalcount_h) + '/'          #  total in 
    api_token=api_token + str(totalcount_h) + '/'          # total out 
    api_token=api_token + str(date)+ '/'      #  Date 
    api_token=api_token + str(Hour)      #  Date 

    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(api_token)}

    def get_result():
        while True:
            try: 
                response = requests.post(api_token, headers=headers)
                if response.status_code == 200:
                    CheckPreData(suid,date,'/home/live/Documents/st_api_program_ui/db.sqlite3')
                    return json.loads(response.content.decode('utf-8'))
                    
                break 
            except:
                print ("Something went wrong(3)!")
    fetch_result = get_result()

    if fetch_result is not None:
        print("API:",api_token)
        print("Here's your info: ")
        for k, v in fetch_result.items():
            print('{0}:{1}'.format(k, v))
        totalcount_h=0
        Peoplecount_h.clear()
        Peoplecount_h=[0]
    else:
        print('[!] Request Failed')

def Check_dir(path):
    try:
        if not os.listdir(path):
            print("Directory is empty")
            os.system('echo %s|sudo -S %s' % ('mobilelink@1', 'mount -a'))
            time.sleep(5)
            Check_dir(path)
        else:
            print("Directory found")
    except:  
        print("Server Down")
        Check_dir(path) 

def logic():
    global today, yesterday,globalDate
    setGlobalDate()

    # currentDate = time.strftime("%m-%d-%Y")
    ab=0
    Stuid=""
    Hour=''
    index=0
    # YesturdaysplitedDate = str(today).split('-')
    # MergeYesturdaySplitedDate = YesturdaysplitedDate[0] + YesturdaysplitedDate[1] + YesturdaysplitedDate[2]
    
    # DB STARTS HERE
    database = r"/home/live/Documents/st_api_program_ui/db.sqlite3"

    # create a database connection
    conn = create_connection(database)

    with conn:
        mainSetting = getMainSetting(conn, 3) 
        # Check_dir(mainSetting[5])
        stores = selectAllStores(conn, globalDate, 'Aiprod3')
        if not mainSetting['is_system_date']:
            globalDate = mainSetting['date_for_all_store']
        for storeDataObj in stores:
            
            ab+=1
            Stuid=str(storeDataObj['store_unique_id'])
            t=9
            # Creaing ErrorLog
            # if os.path.exists(str(mainSetting[5])):
            #     pass
            # else:
            #     ErrorLog('Global Path is missing',globalDate, database)
            # for file in sorted():
            #     timming=file.split(' ')[1]
            #     index+=1 
                
            # START
            CUDA_LAUNCH_BLOCKING=1
            source=str(mainSetting['path_for_all_store'])+str(storeDataObj['store_unique_id'])+'/'+str(storeDataObj['store_channel'])+'/'+globalDate.replace('-','')+'/'
            # source=''+str(storeDataObj['store_unique_id'])+'/'+str(storeDataObj['store_channel'])+'/20210601/'
            # source='/media/shared53/70144854/3/20210528/'
            print('=============================',source)
            weights= str(mainSetting['source_weight'])
            iou_thres = float('0.'+str(storeDataObj['thresh']))
            conf_thres = float('0.'+str(storeDataObj['conf']))
            imgsz = 640
            device = str(mainSetting['device'])

            set_logging()
            device = select_device(device)
            half = device.type != 'cpu'  # half precision only supported on CUDA

            # Load model
            model = attempt_load(weights, map_location=device)  # load FP32 model
            imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size
            if half:
                model.half()  # to FP16

            # Set Dataloader

            try:
                dataset = LoadImages(source, img_size=imgsz)
            except Exception as ex:
                continue
            
            # Get names and colors
            names = model.module.names if hasattr(model, 'module') else model.names
            colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

            # Run inference
            t0 = time.time()
            img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
            _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once
            for path, img, im0s, vid_cap in dataset:
                timming=path.split(' ')[1]
                index+=1
                num=0
                img = torch.from_numpy(img).to(device)
                img = img.half() if half else img.float()  # uint8 to fp16/32
                img /= 255.0  # 0 - 255 to 0.0 - 1.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)

                # Inference
                t1 = time_synchronized()
                pred = model(img,False)[0]

                # Apply NMS
                pred = non_max_suppression(pred, conf_thres, iou_thres, classes=0, agnostic=False)
                t2 = time_synchronized()

                # Process detections
                for i, det in enumerate(pred):  # detections per image
                    p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)

                    p = Path(p)  # to Path
                    s += '%gx%g ' % img.shape[2:]  # print string
                    gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                    if len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                        # Print results
                        for c in det[:, -1].unique():
                            n = (det[:, -1] == c).sum()  # detections per class
                            s += f'{n} {names[int(c)]}s, '  # add to string

                        # Write results
                        for *xyxy, conf, cls in reversed(det):
                            if names[int(cls)] == 'person':
                                # print(names[int(cls)])
                                num +=1
                                label = f'{names[int(cls)]} {conf:.2f}'
                                plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)
                                
            # return num

            # END

                if num>0:
                    total.append(num)
                    
                check=str(t)

                if len(check)>1:
                    Hour=(check+"_")
                        
                else:
                    Hour=("0"+check+'_')

                if Hour in timming:
                    print(Hour,timming)

                else:
                    Hourly_API_Call(Stuid,check,globalDate)
                    t+=1
                if index==6:
                    grandtotal()
                    index=0
                        
                print('Total Count:{}'.format(totalcount))
                print('Total Stores Complete:{}'.format(ab))

                # API_Call(Stuid)
            localDB(Stuid,totalcount, totalcount_h, '23', True)
            Peoplecount.clear()
logic()