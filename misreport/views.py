from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
from camsconfig.models import CamsData, MisTrafficCount, MainSetting, Market, ManualCount
from django.contrib import messages
from django import forms
from django.urls import reverse_lazy
import datetime
# from .forms import ManualCountForm
import json
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import xlwt
# from .admin import CamsDataResource, ManualCountResource
# from tablib import Dataset
import tablib
from import_export import resources
from django.core import serializers
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Sum, Value as defV
from django.db.models.functions import Coalesce
from camsconfig.views import getAllInfo
from camsconfig.admin import CamsDataResource

# Create your views here.


def export_filtered(request,pk):
    camsdata_resources = CamsDataResource()
    querySet = CamsData.objects.filter(current_status=pk)
    dataset = camsdata_resources.export(querySet)
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="FilteredStores.csv"'
    return response

def statusdetails(request,pk):
    storeStatusData = CamsData.objects.filter(current_status=pk)
    
    totalMarket = Market.objects.all().count()
    totalStores = CamsData.objects.all().count()
    
    totalAccurated = CamsData.objects.filter(current_status=2).count()
    accurateButNotConsistent = CamsData.objects.filter(current_status=3).count()
    NotAccurateduetoCameraangle = CamsData.objects.filter(current_status=4).count()
    accurateButStillCameraIssue = CamsData.objects.filter(current_status=5).count()

    # totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()

    context = {
        'totalMarket':totalMarket,
        'totalStores':totalStores,
        'currentpk':pk,
        'totalAccurated':totalAccurated,
        'accurateButNotConsistent':accurateButNotConsistent,
        'NotAccurateduetoCameraangle':NotAccurateduetoCameraangle,
        'accurateButStillCameraIssue':accurateButStillCameraIssue,
        'storeStatusData':storeStatusData
    }

  
    return render(request,'statusdetails.html', context)

@login_required
def misCount(request):
    date = datetime.datetime.now()
    a_date = datetime.date(int(str(date.year)), int(str(date.month)), int(str(date.day)))
    days = datetime.timedelta(1)

    new_date = a_date - days
    miscount_data = MisTrafficCount.objects.filter(date=new_date)
    market_list = Market.objects.all()

    totalMarket = Market.objects.all().count()
    totalStores = CamsData.objects.all().count()
    totalAccurated = CamsData.objects.filter(current_status=2).count()
    accurateButNotConsistent = CamsData.objects.filter(current_status=3).count()
    NotAccurateduetoCameraangle = CamsData.objects.filter(current_status=4).count()
    accurateButStillCameraIssue = CamsData.objects.filter(current_status=5).count()

    # totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()

    context = {
        'totalMarket':totalMarket,
        'totalStores':totalStores,

        'totalAccurated':totalAccurated,
        'accurateButNotConsistent':accurateButNotConsistent,
        'NotAccurateduetoCameraangle':NotAccurateduetoCameraangle,
        'accurateButStillCameraIssue':accurateButStillCameraIssue,

        'miscount_data': miscount_data,
        'market_list': market_list
    }
    
    return render(request, 'mis_report.html', context)


# def get_chart(request):
#     date = datetime.datetime.now()
#     a_date = datetime.date(int(str(date.year)), int(str(date.month)), int(str(date.day)))
#     days = datetime.timedelta(2)
#     new_date = a_date - days

#     extracted_data_start = []
#     extracted_data_end = []

#     marketid = request.GET.get('marketId')
#     startdate = request.GET.get('startdate')
#     enddate = request.GET.get('enddate')
#     status = ''
#     # print('==========DATE START==========', startdate)
#     # print('==========DATE END==========', enddate)
#     print('monthlu-==================',len(str(enddate).split('-')))
#     camsdata = CamsData.objects.filter(market=marketid)
#     for stores in camsdata:      
#         if len(str(startdate).split('-'))==2:
#             status = 'Monthly Comparision'
#             miscount_data = MisTrafficCount.objects.filter(store_uid=stores.pk, time='23', total_count__gt=0, date__startswith=startdate).aggregate(num_authors=Sum('total_count'))
#             extracted_data_start.append({
#                 'total_count': miscount_data['num_authors'],
#                 'store_name': stores.store_name,            
#             })
#         else:
#             status = 'Daily Comparision'
#             miscount_data = MisTrafficCount.objects.filter(store_uid=stores.pk, time='23', date=startdate)            
#             for i in miscount_data:
#                 # print(i.store_uid.store_name)
#                 extracted_data_start.append({
#                     'total_count': i.total_count,
#                     'store_name': i.store_uid.store_name,                
#                 })
    
#     # END DATA_
#     for stores in camsdata:
#         if len(str(enddate).split('-'))==2:
#             print('monthlu-==================',len(str(enddate).split('-')))
#             miscount_data = MisTrafficCount.objects.filter(store_uid=stores.pk, time='23', total_count__gt=0, date__startswith=enddate).aggregate(num_authors=Sum('total_count'))
#             extracted_data_end.append({
#                 'total_count': miscount_data['num_authors'],
#                 'store_name': stores.store_name,            
#             })
#         else:
#             miscount_data = MisTrafficCount.objects.filter(store_uid=stores.pk, time='23', date=enddate)            
#             for i in miscount_data:
#                 # print(i.store_uid.store_name)
#                 extracted_data_end.append({
#                     'total_count': i.total_count,
#                     'store_name': i.store_uid.store_name,  
                                  
#                 })

#     # GETTING MAX VALUE
#     max_value = 0
#     for i in extracted_data_start:
#         if max_value < int(i['total_count']):
#             max_value = int(i['total_count'])

#     # print(len(extracted_data_start)) 

#     context = {
#         'extracted_data_start': extracted_data_start,
#         'extracted_data_end': extracted_data_end,
#         'status': status
#     }

#     return JsonResponse(context)


def getAccuracy(request):
    date = datetime.datetime.now()
    a_date = datetime.date(int(str(date.year)), int(str(date.month)), int(str(date.day)))
    days = datetime.timedelta(2)
    new_date = a_date - days

    extracted_data_start = []
    extracted_data_end = []

    marketid = request.GET.get('marketId')
    startdate = request.GET.get('startdate')
    enddate = request.GET.get('enddate')
    status = ''
    
    print('monthlu-==================',len(str(enddate).split('-')))
    camsdata = CamsData.objects.filter(market=marketid)
    for stores in camsdata:      
        if len(str(startdate).split('-'))==2:
            status = 'Monthly Comparision'
            miscount_data = MisTrafficCount.objects.filter(store_uid=stores.pk, time='23', total_count__gt=0, date__startswith=startdate).aggregate(num_authors=Coalesce(Sum('total_count'), defV(0)))
            manualCountData = ManualCount.objects.filter(store_name=stores.pk, count__gt=0, date__startswith=startdate).aggregate(totalCount=Coalesce(Sum('count'), defV(0)))
            extracted_data_start.append({
                'total_count': miscount_data['num_authors'],
                'store_name': stores.store_name,
                'manual_count': manualCountData['totalCount']
                            
            })
        else:
            status = 'Daily Comparision'
            miscount_data = MisTrafficCount.objects.filter(store_uid=stores.pk, time='23', date=startdate)   
            manualCountData = ManualCount.objects.filter(store_name=stores.pk, count__gt=0, date=startdate).aggregate(totalCount=Coalesce(Sum('count'),defV(0)))
                    
            for i in miscount_data:
                # print(i.store_uid.store_name)
                extracted_data_start.append({
                    'total_count': i.total_count,
                    'store_name': i.store_uid.store_name,  
                    'manual_count': manualCountData['totalCount']              
                })
    
    # END DATA_
    for stores in camsdata:
        if len(str(enddate).split('-'))==2:
            print('monthlu-==================',len(str(enddate).split('-')))
            miscount_data = MisTrafficCount.objects.filter(store_uid=stores.pk, time='23', total_count__gt=0, date__startswith=enddate).aggregate(num_authors=Coalesce(Sum('total_count'), defV(0)))
            manualCountData = ManualCount.objects.filter(store_name=stores.pk, count__gt=0, date__startswith=enddate).aggregate(totalCount=Coalesce(Sum('count'),  defV(0)))
            
            extracted_data_end.append({
                'total_count': miscount_data['num_authors'],
                'store_name': stores.store_name,   
                'manual_count': manualCountData['totalCount']         
            })
        else:
            miscount_data = MisTrafficCount.objects.filter(store_uid=stores.pk, time='23', date=enddate) 
            manualCountData = ManualCount.objects.filter(store_name=stores.pk, count__gt=0, date=enddate).aggregate(totalCount=Coalesce(Sum('count'), defV(0)))
                       
            for i in miscount_data:
                # print(i.store_uid.store_name)
                extracted_data_end.append({
                    'total_count': i.total_count,
                    'store_name': i.store_uid.store_name,
                    'manual_count': manualCountData['totalCount']    
                                  
                })


    # print(len(extracted_data_start)) 

    context = {
        'extracted_data_start': extracted_data_start,
        'extracted_data_end': extracted_data_end,
        'status': status
    }

    return JsonResponse(context)