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

def setGlobalDate():
    global globalDate
    today = date.today() 
    yesterday = today - timedelta(days = 1) 

    current_hour = datetime.datetime.now().strftime("%H:%M:%S").split(':')[0]
    print(current_hour)
    if int(current_hour)<12: # PM
        globalDate = date.today().strftime('%Y-%m-%d') 
    else:
        today = date.today() 
        yesterday = today - timedelta(days = 1) 
        globalDate = yesterday.strftime('%Y-%m-%d')
# setGlobalDate()
# print(globalDate)


print('================================================',globalDate)
# date='2021-05-29'
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
    global current,Peoplecount,total,totalcount, today, yesterday,globalDate
   
    api_token = "http://3.18.96.94/DeepScienceApi/api/Surveillance/InsertStoreCountDataWithHour/"
    # today = date.today() 
    yesterday = today - timedelta(days = 1) 
    api_token=api_token + str('Store') + '/'   # store name 
    api_token=api_token + str(suid) + '/'          # store id 
    api_token=api_token + str(totalcount) + '/'          #  total in 
    api_token=api_token + str(totalcount) + '/'          # total out 
    api_token=api_token + str(globalDate) + '/'      #  Date 
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


alluid=[70143279,70143375,70143602,70143699,70143701,70144282,70144283,70144326,70144329,70144334,70144343,70144974,70144721,70144431,70144435,70144436,70144443,70144446,70144448,70144449,70144456,70144466,70144472,70144481,70144485,70144493,70144511,70144518,70144523,70144535,70144537,70144543,70144596,70144611,70144621,70144629,70144651,70144654,70144666,70144667,70144668,70144672,70144674,70144675,70144687,70144692,70144693,70144696,70144697,70144698,70144701,70144703,70144707,70144708,70144709,70144718,70144732,70144735,70144737,70144738,70144750,70144752,70144765,70144768,70144774,70144775,70144784,70144794,70144798,70144800,70144815,70144817,70144820,70144821,70144822,70144826,70144831,70144842,70144844,70144849,70144852,70144855,70144857,70144859,70144860,70144863,70144864,70144866,70144867,70144868,70144869,70144870,70144877,70144879,70144890,70144893,70144895,70144896,70144904,70144921,70144971,70144928,70144930,70144945,70144947,70144948,70144949,70144956,70144958,70144961,70144963,70145243,70145257,70145382,70145593,70145646,70145664,70145667,70152261,70152263,70152287,70152327,70152355,70152363,70152607,70153297,70153358,70153480,70153404,70153479,70155291,70155303,70155322,70155328,70155610,70155615,70155616,70158267,70158678,70158686,70158742,70159285,70159340,70159754,70159755,70159756,70159757,70159759,70159761,70160346,70160669,70160670,70161253,70161347,70162270,70162482,70162748,70162749,70162750,70162751,70163383,70164294,70164304,70164415,70164421,70164424,70164425,70164618,70164628,70164650,70164653,70164713,70164716,70164756,70164757,70164758,70164759,70164761,70164764,70164765,70164766,70164767,70164768,70164769,70164772,70164776,70164777,70164778,70164779,70164780,70164782,70164784,70144966,70145673,70144965,70144975,70144976,70144970,70144979,70144990]
allchennal=[1,2,4,3,3,4,2,1,1,2,2,3,3,1,1,1,3,3,4,3,1,1,1,2,4,3,3,4,3,1,3,2,3,1,4,1,2,1,2,3,1,1,3,3,2,3,2,4,2,1,2,2,4,4,2,2,2,2,1,2,1,3,2,1,1,3,1,3,2,4,1,1,2,1,3,1,2,2,2,3,3,3,3,3,3,4,3,2,2,4,2,2,1,1,2,3,4,4,1,2,1,1,2,2,4,4,2,3,4,2,2,2,1,1,3,4,1,3,2,1,2,1,1,2,3,2,1,2,1,2,3,4,2,3,4,3,2,1,3,1,1,3,1,2,1,1,1,2,1,2,1,1,2,3,3,2,1,1,2,1,3,2,4,4,1,1,3,1,1,2,3,2,2,3,4,4,1,1,1,3,1,1,4,1,3,1,1,3,3,1,1,2,1,3,4,2,2,1,2,2]


# alluid=[70143236,70144247,70144378,70144402,70144429,70144773,70144444,70144779,70150265,70144488,70144517,70144524,70144542,70150332,70144561,70144572,70160626,70163234,70144587,70152357,70144655,70152377,70144743,70158260,70144783,70144986,70144463,70144807,70144803,70144545,70144886,70144906,70144907,70144913,70144916,70144919,70144920,70144922,70144924,70144925,70144926,70144927,70144599,70164787,70153286,70153478,70164786,70144612,70144811,70144874,70164390,70164423,70164627,70144438,70144447,70144991,70144972,70162755,70164781,70164775,70143412,70164762,70143680,70144387,70164749,70144428,70164590,70144433,70164409,70163249,70161317,70161259,70158748,70158683,70158274,70155611,70155417,70153307,70153280,70152278,70151352,70145672,70145668,70145666,70145661,70145403,70145398,70145394,70145392,70145391,70145388,70145380,70145313,70145273,70144959,70144957,70144954,70144953,70144946,70144943,70144939,70144938,70144937,70144935,70144932,70144931,70144929,70144908,70144900,70144899,70144898,70144894,70144892,70144889,70144888,70144885,70144881,70144875,70144854,70144853,70144847,70144837,70144836,70144834,70144833,70144832,70144830,70144814,70144813,70144812,70144810,70144809,70144808,70144802,70144434,70144454,70144455,70144464,70144465,70144487,70144508,70144515,70144533,70144586,70144639,70144644,70144645,70144662,70144702,70144769,70144776,70144785,70144787,70144789,70144796,70143272,70155348,70144576,70164605,70158397,70158268,70155314,70144496,70144536,70144623,70145379,70144985,70144941,70144978,70162753,70144944,70145665,70159764,70144973,70150401,70144969,70144977,70150402,70144967,70164755,70153373,70164685,70158271,70159763,70164492,70144571,70144793,70143301,70150333]
# allchennal=[1,4,4,1,2,2,1,3,2,3,1,1,1,3,1,2,4,1,4,3,3,3,1,1,2,1,2,2,1,3,2,4,1,2,1,3,3,3,2,3,4,2,1,4,1,2,3,2,1,4,2,2,2,4,1,1,1,4,2,1,2,3,2,2,1,1,2,1,2,1,2,1,1,1,4,1,1,1,2,3,4,4,1,1,1,1,2,1,1,4,1,4,2,2,3,1,1,3,1,3,3,2,2,4,2,1,2,2,1,1,3,2,2,2,3,1,1,1,1,3,2,1,1,2,1,1,3,1,1,1,3,2,1,1,1,2,4,1,2,2,4,1,3,1,4,3,1,1,1,2,1,2,3,1,1,1,3,4,1,1,2,4,2,2,2,3,1,2,2,1,1,1,1,2,1,4,1,1,1,3,2,2,4,2,1,2,1,2,1]
print(len(alluid))    
print(len(allchennal))    

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


    for store in range(len(alluid)):
        
        ab+=1
        Stuid=str(alluid[store])
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
        # /run/user/1001/gvfs/smb-share:server=172.16.16.8,share=store_cams_picture/70144429
        CUDA_LAUNCH_BLOCKING=1
        # source='/run/user/1001/gvfs/smb-share:server=10.0.0.53,share=store_cams_picture/'+str(alluid[store])+'/'+str(allchennal[store])+'/'+str(globalDate.replace('-','')+'/')
        source='/run/user/1001/gvfs/smb-share:server=10.0.0.53,share=store_cams_picture/'+str(alluid[store])+'/'+str(allchennal[store])+'/20210601/'
        # source='/media/shared53/70144854/3/20210528/'
        weights= 'yolov5s.pt'
        iou_thres = 0.25

        conf_thres =0.45
        imgsz = 640
        device =''

        if not os.path.exists(source):
            print('Path Does Not Exists \n', source)
            continue

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
                # print('=============================================API CALLED============================================')
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