import numpy as np
import argparse
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
from detect_local import detect
total=[0]
totalcount=0
total_h=[0]
totalcount_h=0
result=0
result_h=0
b=0
paths=[]
current=[0]
current_h=[0]
Peoplecount=[0]
Peoplecount_h=[0]

import requests
import json
import torch, gc
import sqlite3

today = date.today() 
yesterday = today - timedelta(days = 1) 

def localDB(storuid,totalcounts, totalcounts_h, Hour, status=False):  
    global current_h,Peoplecount_h,total_h,totalcount_h,check
    global current,Peoplecount,total,totalcount
    conn = sqlite3.connect('2021_02_10.db')
    print("Opened database successfully")

    conn.execute('CREATE TABLE  IF NOT EXISTS TEST(ID INTEGER PRIMARY KEY AUTOINCREMENT, storeuid TEXT,totalcount TEXT, hourlycount  TEXT, time TEXT, date TEXT)')
    print("Table created successfully")

    if status:
        conn.execute('insert into TEST (storeuid,totalcount,hourlycount,time,date) values ("'+str(storuid)+'","'+str(totalcounts)+'","'+str(totalcounts_h)+'","'+str(Hour)+'", "'+str(yesterday)+'")')
    
    else:
        conn.execute('insert into TEST (storeuid,totalcount,hourlycount,time,date) values ("'+str(storuid)+'","0","'+str(totalcounts_h)+'","'+str(Hour)+'", "'+str(yesterday)+'")')
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
    current_h.clear()
    current_h=[0]
    total_h.clear()
    total_h=[0]
    Peoplecount_h.clear()
    Peoplecount_h=[0]
    print('Hourly API CALLED')


def grandtotal():
    global total,current,totalcount,totalcount_h, total_h, current_h
    current.append(max(total))
    current_h.append(max(total))
    total.clear()
    total_h.clear()
    total=[0]
    total_h=[0]
    x=current[-1]
    y=current[-2]
    time=datetime.datetime.now()
    nowtime=time.strftime("%H:%M:%S")
     
    if x>y and y>0:
        count=(x-y)
        print("Add",count)
        # if count <6:
        Peoplecount.append(count)
        Peoplecount_h.append(count)
          # print(nowtime)
    else:
        print("No Change")
        # print(nowtime)
        pass
    #  print(sum(Peoplecount))
    totalcount_h=sum(Peoplecount_h)
    totalcount=sum(Peoplecount)
    #  print(totalcount)

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
    api_token=api_token + str('2021-02-10') + '/'      #  Date 
    api_token=api_token + str('23')           # total out 
    
    headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(api_token)}
    def get_result():
     #    while True:
           
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
        
        totalcount=0
        current.clear()
        current=[0]
        total.clear()
        total=[0]
        Peoplecount.clear()
        Peoplecount=[0]
        #centro=()
        # down1 = 0
        # # up2=0
        # down2=0
        
        #X=0
        #Y=0

    else:
        #print("API:",api_token)
        print('[!] Request Failed')



#------------------HourlyAPI Start--------------------------#
def Hourly_API_Call(suid,Hour):
    global current_h,Peoplecount_h,total_h,totalcount_h,check, today, yesterday

    api_token = "http://3.18.96.94/DeepScienceApi/api/Surveillance/InsertStoreCountDataWithHour/"
    # today = date.today() 
    yesterday = today - timedelta(days = 1) 
    api_token=api_token + str('Store') + '/'   # store name 
    api_token=api_token + str(suid) + '/'          # store id 
    api_token=api_token + str(totalcount_h) + '/'          #  total in 
    api_token=api_token + str(totalcount_h) + '/'          # total out 
    api_token=api_token + str('2021-02-10')+ '/'      #  Date 
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
        current_h.clear()
        current_h=[0]
        total_h.clear()
        total_h=[0]
        Peoplecount_h.clear()
        Peoplecount_h=[0]
        
    else:
        #print("API:",api_token)
        print('[!] Request Failed')




# labels = open('yolov3-coco/coco-labels').read().strip().split('\n')
# config= 'yolov3-coco/yolov3.cfg'
# weights= 'yolov3-coco/yolov3.weights'
# confidence = 0.4
# threshold = 0.3
# Intializing colors to represent each label uniquely
# colors = np.random.randint(0, 255, size=(len(labels), 3), dtype='uint8')

# Load the weights and configutation to form the pretrained YOLOv3 model
# net = cv.dnn.readNetFromDarknet(config, weights)

# # Get the output layer names of the model
# layer_names = net.getLayerNames()
# layer_names = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]


def logic():
    global today, yesterday
    ab=0

    Stuid=""
    Hour=''
    index=0

    YesturdaysplitedDate = str(yesterday).split('-')
    MergeYesturdaySplitedDate = YesturdaysplitedDate[0] + YesturdaysplitedDate[1] + YesturdaysplitedDate[2]


    # surpath=['70144820','70144543','70144773','70144769','70144800','70144802','70144329','70144537','70144511','70158267','70144776','70144775','70144774','70144794',   '70144821','70144842','70144961','70144979']
    # surche=[2,2,3,3,1,2,1,2,3,1,1,3,1,3,1,2,2,2]
    # 70144446,70144463,70160670,70144945,70144946,70144948,70153479,70153480,70144947,70144949,70153373,70144508,70144701,70144768,70144784,70145380,70145382,70145646,70145664,70164628,70164772,70144675,70144879,70162748,70162749,70162750,70162751,70164304,70164415,70164425,70164590,70164653,70164775,70164780,70144466,70144655,70144692,70144852,70153404,70145273,70145593,70145667,70145668,70145673,70144864,70144866,70144867,70144868,70144869,70144870,70144928,70155303,70155322,70155610,70155611,70164778,70144326,70144329,70144343,70144537,70144543,70144721,70144737,70144769,70144773,70144774,70144775,70144776,70144794,70144800,70144802,70144820,70144821,70144822,70144842,70144961,70144974,70144979 compted with date of 8 feb
    surpath =[70144446,70144463,70160670,70144945,70144946,70144948,70153479,70153480,70144947,70144949,70153373,70144508,70144701,70144768,70144784,70145380,70145382,70145646,70145664,70164628,70164772,70144675,70144879,70162748,70162749,70162750,70162751,70164304,70164415,70164425,70164590,70164653,70164775,70164780,70144466,70144655,70144692,70144852,70153404,70145273,70145593,70145667,70145668,70145673,70144864,70144866,70144867,70144868,70144869,70144870,70144928,70155303,70155322,70155610,70155611,70164778,70144326,70144329,70144343,70144537,70144543,70144721,70144737,70144769,70144773,70144774,70144775,70144776,70144794,70144800,70144802,70144820,70144821,70144822,70144842,70144961,70144974,70144979,70145665,70158267,70144511,70144809,70164492,70144334,70164618,70144738,70144941,70164685,70144933,70144929,70144859,70164776,70144935,70164766,70164779,70144860,70164768,70144857,70164777,70164769,70144930,70164782,70144493,70144890,70144958,70144896,70144693,70144709,70155616,70144750,70144703,70144831,70144863,70144849,70144854,70144855,70144536,70144645,70144687,70144817,70164650,70164749,70144787,70144792,70144797,70144826,70144779,70144788,70144449,70144572,70144662,70144889,70144893,70144975,70144977,70144477,70144434,70144697,70144814,70144651,70144708,70144904,70144898,70144953,70144812,70144888,70144895,70164716,70144939,70144938]
    surche = [3,2,1,2,1,3,2,2,4,2,3,3,2,1,2,4,1,4,2,1,3,3,1,2,1,1,1,4,4,3,2,3,3,1,1,3,3,3,1,2,3,3,1,1,3,2,2,4,2,2,1,3,2,2,1,3,1,1,2,3,2,3,1,3,3,1,3,1,3,1,2,2,1,3,2,2,3,2,2,1,3,1,2,2,1,1,2,2,1,2,3,1,4,1,1,3,4,3,1,1,2,2,3,4,4,4,2,4,2,1,2,1,4,3,3,3,3,2,3,4,2,1,4,1,4,3,3,4,1,2,2,2,3,2,2,1,2,1,1,1,4,3,3,3,2,3,4,2,3,1]


    # surpath=['70144820','70144543','70144773','70144769','70144800','70144802','70144329','70144537','70144511','70158267','70144776','70144775','70144774','70144794']
    # surche=[2,2,3,3,1,2,1,2,3,1,1,3,1,3]


    # surpath=['70144775']
    # surche=['3']
    sbkarasta=[]
    Stuid=''
    for rasta in range(len(surpath)):
        # path33="/media/hk/hk/cams/Compliefile/C:/Store_Cam_picture/"+str(surpath[rasta])+"/"+str(surche[rasta])+"/"+MergeYesturdaySplitedDate+"/*.jpg"
        path33="/media/live/livedb/cams/Compliefile/C:/Store_Cam_picture/"+str(surpath[rasta])+"/"+str(surche[rasta])+"/20210210/*.jpg"

        # path33="/media/hk/hk/cams/Compliefile/C:/Store_Cam_picture/"+str(surpath[rasta])+"/"+str(surche[rasta])+"/20210104/*.jpg"
        sbkarasta.append([path33,str(surpath[rasta])])


    for path555, suid in sbkarasta:
        ab+=1

        Stuid=suid
        print(suid)
        t=9
        for file in sorted(glob.glob(str(path555))):
            timming=file.split(' ')[1]
            index+=1
                
           
            num = detect(False, file, opt.augment, opt.classes, opt.agnostic_nms)
            if num>0:
            # if num not in total:
                total.append(num)
                total_h.append(num)

            # if len(total)>2:
            #     if total[-2]<total[-1] and total[-1]>0:
            #         count=total[-1]-total[-2]
            #         totalCount.append(count)
            # if len(total_h)>2:
            #     if total_h[-2]<total_h[-1]:
            #         count_h=total_h[-1]-total_h[-2]
            #         totalCount_h.append(count_h)
            check=str(t)
            # print('i m In')
            if len(check)>1:
                Hour=(check+"_")
                
                
            else:
                Hour=("0"+check+'_')
                
            # print(Hour,timming)
            # print(Stuid)
            
            if index==5:
                if Hour in timming:
                    print(Hour,timming)

                else:
                    # print("one hour")
                    Hourly_API_Call(Stuid,check)
                    localDB(Stuid,totalcount, totalcount_h, check, False)
                    # print('houly==========')
                    # grandtotal()
                    t+=1
                # print('calling grandtotal')
                grandtotal()
                index=0
            print('Total Count:{}'.format(totalcount))

            # cv.putText(frame,f'Total Count: {sum(Peoplecount)} ',(10,20),cv.FONT_HERSHEY_SIMPLEX,0.6,(116, 17, 0),2)
            # print("Total Count",sum(Peoplecount))
            # print("Total Hourly Count",sum(Peoplecount_h))
            # cv.imshow("Snaps",frame)
            # cv.waitKey(1)
        print(ab,"Store(s) Complete!!!!!!!!!!!!!!!!!!!!!")
        # API_Call(Stuid)
        localDB(Stuid,totalcount, totalcount_h, '23', True)
        Peoplecount.clear()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('--weights', nargs='+', type=str, default='yolov5s.pt', help='model.pt path(s)')
    # parser.add_argument('--source', type=str, default='data/images', help='source')  # file/folder, 0 for webcam
    # parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    # parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
    # parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
    # parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    # parser.add_argument('--view-img', action='store_true', help='display results')
    # parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    # parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    # parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    opt = parser.parse_args()
    print(opt)
    gc.collect()
    torch.cuda.empty_cache()
    # with torch.no_grad():
    #     # if opt.update:  # update all models (to fix SourceChangeWarning)
    #     #     for opt.weights in ['yolov5s.pt', 'yolov5m.pt', 'yolov5l.pt', 'yolov5x.pt']:
    #     #         detect()
    #     #         strip_optimizer(opt.weights)
    #     else:
    logic()