from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .models import CamsData, MisTrafficCount, MainSetting, Market, ManualCount, StoresStatus
from django.contrib import messages
from django import forms
from django.urls import reverse_lazy
import datetime
from .forms import ManualCountForm
import json
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import xlwt
from .admin import CamsDataResource, ManualCountResource
# from tablib import      
import tablib
from import_export import resources
from django.core import serializers
from django.db.models import Q
import json 
# from searchableselect.widgets import SearchableSelect
# Create your views here.


# def export_stores_xls(request):
#     response = HttpResponse(content_type='application/ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="Stores.xls"'

#     wb = xlwt.Workbook(encoding='utf-8')
#     ws = wb.add_sheet('Stores')

#     # Sheet header, first row
#     row_num = 0

#     font_style = xlwt.XFStyle()
#     font_style.font.bold = True

#     columns = ['Store Name', 'Store UID', 'Store Channel', 'Confs', 'Thresh', 'Snaps Path', 'Date', 'Number of Snaps', 'Hourly Api', 'Total Api', 'Device','Time' , ]

#     for col_num in range(len(columns)):
#         ws.write(row_num, col_num, columns[col_num], font_style)

#     # Sheet body, remaining rows
#     font_style = xlwt.XFStyle()

#     rows = CamsData.objects.all().values_list('store_name', 'store_unique_id', 'store_channel', 'conf', 'thresh', 'snaps_path', 'date', 'number_of_snaps', 'hourly_api', 'total_api', 'device', 'time')
#     for row in rows:
#         row_num += 1
#         for col_num in range(len(row)):
#             ws.write(row_num, col_num, row[col_num], font_style)

#     wb.save(response)
#     return response

def change_status(request):
    ids = request.POST
    
    converted_ids = json.loads(ids['data'])
    for d in converted_ids:
        camsdata = CamsData.objects.get(pk=d)
        camsdata.status=ids['status']
        camsdata.save()
    
    return JsonResponse({'status':str(ids)})

def export_stores_xls(request):
    camsdata_resources = CamsDataResource()
    dataset = camsdata_resources.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stores.csv"'
    return response

def export_manual_xls(request):
    manual_resources = ManualCountResource()
    dataset = manual_resources.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="manualcount.csv"'
    return response

def import_stores_xls(request): 
    try:
        if request.method == 'POST':
            book_resource = resources.modelresource_factory(model=ManualCount)()
            new_stores = request.FILES['manualfile']
            dataset = tablib.Dataset().load(new_stores.read().decode(), format='csv', headers=True)
            result = book_resource.import_data(dataset, dry_run=True)
            messages.warning(request, 'Trying to imprt')

            if not result.has_errors():
                book_resource.import_data(dataset, dry_run=False)
                messages.success(request, 'Success Imported')
            else:
                messages.warning(request, 'Faild to import Data, due to. market ID, Data Exists')                
    except Exception as e:
        print(e)
    return HttpResponseRedirect(reverse_lazy('create_manual'))

def import_manual_xls(request):
    try:
        if request.method == 'POST':
            book_resource = resources.modelresource_factory(model=CamsData)()
            new_stores = request.FILES['storefile']
            dataset = tablib.Dataset().load(new_stores.read().decode(), format='csv', headers=True)
            result = book_resource.import_data(dataset, dry_run=True)
            messages.warning(request, 'Trying to imprt')

            if not result.has_errors():
                book_resource.import_data(dataset, dry_run=False)
                messages.success(request, 'Success Imported')
            else:
                messages.warning(request, 'Faild to import Data, due to. market ID, Data Exists')                
    except Exception as e:
        print(e)
    return HttpResponseRedirect(reverse_lazy('create_programconfig'))


@login_required
def index(request):    
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse_lazy('taskuser'))
    request.session['userpk'] = request.user.pk    
    date = datetime.datetime.now()
    a_date = datetime.date(int(str(date.year)), int(str(date.month)), int(str(date.day)))
    days = datetime.timedelta(2)

    new_date = a_date - days
    miscount_data = MisTrafficCount.objects.filter(time='23')
    # print(miscount_data)


    # GETTING MARKET LIST
    market_list = Market.objects.all()
    # for i in miscount_data:
    #     # print(i.total_count)
    #     extracted_dat.append({
    #         'total_count': i.total_count,
    #         'store_name': i.store_uid.store_name
    #     })
    totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
    context = {
        'miscount_data': miscount_data,
         'market_list': market_list,
         'totalMarket':totalMarket,
         'totalStores':totalStores,
         'totalAccurated':totalAccurated,
         'totalNoneAccurated':totalNoneAccurated,
    }
    return render(request, 'index.html', context)

def getAllInfo():
    totalMarket = Market.objects.all().count()
    totalStores = CamsData.objects.all().count()
    totalAccurated = CamsData.objects.filter(current_status=2).count()
    totalNoneAccurated = CamsData.objects.filter(~Q(current_status=2)).count()

    # print('Accurated: {}, None Accurated: {}'.format(totalAccurated, totalNoneAccurated))
    return totalMarket, totalStores, totalAccurated, totalNoneAccurated

def get_chart(request):
    date = datetime.datetime.now()
    a_date = datetime.date(int(str(date.year)), int(str(date.month)), int(str(date.day)))
    days = datetime.timedelta(2)
    new_date = a_date - days

    extracted_dat = []

    marketid = request.GET.get('market')
    date_selected = request.GET.get('date')
    print(date_selected)
    # get market stores
    camsdata = CamsData.objects.filter(market=marketid)
    for stores in camsdata:
        miscount_data = MisTrafficCount.objects.filter(store_uid=stores.pk, time='23', date=date_selected)  
        # print(miscount_data)  
        for i in miscount_data:
            # print(i.store_uid.store_name)
            extracted_dat.append({
                'total_count': i.total_count,
                'store_name': i.store_uid.store_name,
            
            })

    # GETTING MAX VALUE
    max_value = 0
    for i in extracted_dat:
        if max_value < int(i['total_count']):
            max_value = int(i['total_count'])

    print(len(extracted_dat)) 

    context = {
        'extracted_dat': extracted_dat,
        'max_value': max_value
    }

    return JsonResponse(context)

def getStoreByMarket(request):
    marketid = request.GET.get('marketid')

    # get market stores
    StoresByMarket = []
    marketStores = CamsData.objects.filter(market=marketid)

    for store in marketStores:
        StoresByMarket.append({
            'pk': store.pk,
            'store_name':store.store_name
        })
    context = {
        'StoresByMarket':StoresByMarket
    }

    return JsonResponse(context)


class CreateProgramConfig(LoginRequiredMixin ,CreateView):
    template_name = 'config.html'
    model = CamsData
    fields = '__all__'
    login_url = reverse_lazy('login')
   
    def form_valid(self, form):
        form = super().form_valid(form)
        messages.success(self.request, 'Data has been saved successfully!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        return form
    
    def get_form(self, **kwargs):
        form = super(CreateProgramConfig, self).get_form(**kwargs)
        # form.fields['date'].widget = forms.TextInput(attrs={'type':'date'}) 
        # form.fields['market'].widget = SearchableSelect(model='CamsData.market', search_field='market_name', limit=10) 
        # form.fields['market'].required = False

        # form.fields['current_status'].widget=forms.SelectField(label='sadadadsad')
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(CreateProgramConfig, self).get_context_data(**kwargs)
        context['serverprod1Stores'] = CamsData.objects.filter(server_name='Aiprod1')
        context['serverprod2Stores'] = CamsData.objects.filter(server_name='Aiprod2')
        context['serverprod3Stores'] = CamsData.objects.filter(server_name='Aiprod3')
        totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
        context['totalMarket'] = totalMarket
        context['totalStores'] = totalStores
        context['totalAccurated'] = totalAccurated
        context['totalNoneAccurated'] = totalNoneAccurated
        allStoresOn = CamsData.objects.filter(status=1).count()
        allStoresOff = CamsData.objects.filter(status=0).count()
        context['allStoresOn'] = allStoresOn
        context['allStoresOff'] = allStoresOff

        # SERVER BASE ON OFF PRODCUTION 1
        server1DataCountTotal = CamsData.objects.filter(server_name='Aiprod1').count()
        context['server1DataCountTotal'] = server1DataCountTotal
        server1DataCountOn = CamsData.objects.filter(status=1, server_name='Aiprod1').count()
        context['server1DataCountOn'] = server1DataCountOn
        server1DataCountOff = CamsData.objects.filter(status=0, server_name='Aiprod1').count()
        context['server1DataCountOff'] = server1DataCountOff

        # SERVER BASE ON OFF PRODCUTION 2
        server2DataCountTotal = CamsData.objects.filter(server_name='Aiprod2').count()
        context['server2DataCountTotal'] = server2DataCountTotal
        server2DataCountOn = CamsData.objects.filter(status=1, server_name='Aiprod2').count()
        context['server2DataCountOn'] = server2DataCountOn
        server2DataCountOff = CamsData.objects.filter(status=0, server_name='Aiprod2').count()
        context['server2DataCountOff'] = server2DataCountOff

        # SERVER BASE ON OFF PRODCUTION 3
        server3DataCountTotal = CamsData.objects.filter(server_name='Aiprod3').count()
        context['server3DataCountTotal'] = server3DataCountTotal
        server3DataCountOn = CamsData.objects.filter(status=1, server_name='Aiprod3').count()
        context['server3DataCountOn'] = server3DataCountOn
        server3DataCountOff = CamsData.objects.filter(status=0, server_name='Aiprod3').count()
        context['server3DataCountOff'] = server3DataCountOff

        return context

class UpdateProgramConfig(LoginRequiredMixin, UpdateView):
    template_name = 'config.html'
    model = CamsData
    fields = '__all__'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form = super().form_valid(form)
        messages.success(self.request, 'Data has been Modified successfully!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        print('============================')
        return form
    
    def get_form(self, **kwargs):
        form = super(UpdateProgramConfig, self).get_form(**kwargs)
        # form.fields['date'].widget = forms.TextInput(attrs={'type':'date'}) 
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateProgramConfig, self).get_context_data(**kwargs)
        context['config_data'] = CamsData.objects.all()
        totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
        context['totalMarket'] = totalMarket
        context['totalStores'] = totalStores
        context['totalAccurated'] = totalAccurated
        context['totalNoneAccurated'] = totalNoneAccurated
        context['edit_form'] = True
        return context

class DeleteProgramConfig(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    template_name = 'camsdata_confirm_delete.html'
    model = CamsData
    success_url = reverse_lazy('create_programconfig')
    success_message = "Data has been Deleted successfully!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteProgramConfig, self).delete(request, *args, **kwargs)
    
# STARTS STORES STATUS ON

class CreateStoreStatus(LoginRequiredMixin ,CreateView):
    template_name = 'storestatus.html'
    model = StoresStatus
    fields = '__all__'
    login_url = reverse_lazy('login')
   
    def form_valid(self, form):
        form = super().form_valid(form)
        messages.success(self.request, 'Data has been saved successfully!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        print('============================')
        return form
    
    def get_form(self, **kwargs):
        form = super(CreateStoreStatus, self).get_form(**kwargs)
        # form.fields['date'].widget = forms.TextInput(attrs={'type':'date'}) 
        # form.fields['date'].required = False
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(CreateStoreStatus, self).get_context_data(**kwargs)
        context['store_data'] = StoresStatus.objects.all()
        totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
        context['totalMarket'] = totalMarket
        context['totalStores'] = totalStores
        context['totalAccurated'] = totalAccurated
        context['totalNoneAccurated'] = totalNoneAccurated
        return context

class UpdateStoreStatus(LoginRequiredMixin, UpdateView):
    template_name = 'storestatus.html'
    model = StoresStatus
    fields = '__all__'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form = super().form_valid(form)
        messages.success(self.request, 'Data has been Modified successfully!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        print('============================')
        return form
    
    def get_form(self, **kwargs):
        form = super(UpdateStoreStatus, self).get_form(**kwargs)
        # form.fields['date'].widget = forms.TextInput(attrs={'type':'date'}) 
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateStoreStatus, self).get_context_data(**kwargs)
        context['store_data'] = StoresStatus.objects.all()
        totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
        context['totalMarket'] = totalMarket
        context['totalStores'] = totalStores
        context['totalAccurated'] = totalAccurated
        context['totalNoneAccurated'] = totalNoneAccurated
        context['edit_form'] = True
        return context

class DeleteStoreStatus(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    template_name = 'storestatus_confirm_delete.html'
    model = StoresStatus
    success_url = reverse_lazy('create_storestatus')
    success_message = "Data has been Deleted successfully!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteStoreStatus, self).delete(request, *args, **kwargs)


# MANUAL COINT STARTS HERE
class CreateManualCount(LoginRequiredMixin ,CreateView):
    template_name = 'manualcount.html'
    model = ManualCount
    # fields = '__all__'
    form_class = ManualCountForm
    login_url = reverse_lazy('login')
   
    def get(self, *args, **kwargs):
        form = self.form_class()
        manual_data = ManualCount.objects.all()
        totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
        context = {
            'totalMarket':totalMarket,
            'totalStores':totalStores,
            'totalAccurated':totalAccurated,
            'totalNoneAccurated':totalNoneAccurated,
            'form': form, 
            'manual_data': manual_data
        }
        return render(self.request, self.template_name,context)

    def post(self, *args, **kwargs):
        manual_data = ManualCount.objects.all()
        if self.request.is_ajax and self.request.method == "POST":
            form = self.form_class(self.request.POST)
            if form.is_valid():
                instance = form.save()
                # ser_instance = serializers.serialize('json', [ instance, ])
                # send to client side.
                data = serializers.serialize('json', self.get_queryset())
                return JsonResponse({"manual_data": data, 'status': 'success'})
            else:
                return JsonResponse({"error": form.errors, 'status': 'error'})

        return JsonResponse({"error": ""})

    # def form_valid(self, form):
    #     form = super().form_valid(form)
    #     messages.success(self.request, 'Data has been saved successfully!')
    #     return form

    # def form_invalid(self, form):
    #     form = super().form_invalid(form)
    #     print('============================')
    #     return form
    
    # def get_form(self, **kwargs):
    #     form = super(CreateManualCount, self).get_form(**kwargs)
    #     form.fields['date'].widget = forms.TextInput(attrs={'type':'date'}) 
    #     # form.fields['date'].required = False
    #     return form

    # def get_context_data(self, *args, **kwargs):
    #     context = super(CreateManualCount, self).get_context_data(**kwargs)
    #     context['manual_data'] = ManualCount.objects.all()
    #     return context

class UpdateManualCount(LoginRequiredMixin, UpdateView):
    template_name = 'manualcount.html'
    model = ManualCount
    fields = '__all__'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form = super().form_valid(form)
        messages.success(self.request, 'Data has been Modified successfully!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        print('============================')
        return form
    
    def get_form(self, **kwargs):
        form = super(UpdateManualCount, self).get_form(**kwargs)
        form.fields['date'].widget = forms.TextInput(attrs={'type':'date'}) 
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateManualCount, self).get_context_data(**kwargs)
        context['manual_data'] = ManualCount.objects.all()
        totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
        context['totalMarket'] = totalMarket
        context['totalStores'] = totalStores
        context['totalAccurated'] = totalAccurated
        context['totalNoneAccurated'] = totalNoneAccurated
        context['edit_form'] = True
        return context

class DeleteManualCount(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    template_name = 'manualcount_confirm_delete.html'
    model = ManualCount
    success_url = reverse_lazy('create_manual')
    success_message = "Data has been Deleted successfully!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteManualCount, self).delete(request, *args, **kwargs)


# Market Starts header

class CreateMarket(LoginRequiredMixin ,CreateView):
    template_name = 'market.html'
    model = Market
    fields = '__all__'
    login_url = reverse_lazy('login')
   
    def form_valid(self, form):
        form = super().form_valid(form)
        messages.success(self.request, 'Data has been saved successfully!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        print('============================')
        return form
    
    def get_form(self, **kwargs):
        form = super(CreateMarket, self).get_form(**kwargs)
        # form.fields['date'].widget = forms.TextInput(attrs={'type':'date'}) 
        # form.fields['date'].required = False
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(CreateMarket, self).get_context_data(**kwargs)
        totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
        context['totalMarket'] = totalMarket
        context['totalStores'] = totalStores
        context['totalAccurated'] = totalAccurated
        context['totalNoneAccurated'] = totalNoneAccurated
        context['market_data'] = Market.objects.all()
        return context

class UpdateMarket(LoginRequiredMixin, UpdateView):
    template_name = 'market.html'
    model = Market
    fields = '__all__'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form = super().form_valid(form)
        messages.success(self.request, 'Data has been Modified successfully!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        print('============================')
        return form
    
    def get_form(self, **kwargs):
        form = super(UpdateMarket, self).get_form(**kwargs)
        # form.fields['date'].widget = forms.TextInput(attrs={'type':'date'}) 
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateMarket, self).get_context_data(**kwargs)
        context['market_data'] = Market.objects.all()
        totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
        context['totalMarket'] = totalMarket
        context['totalStores'] = totalStores
        context['totalAccurated'] = totalAccurated
        context['totalNoneAccurated'] = totalNoneAccurated
        context['edit_form'] = True
        return context

class DeleteMarket(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    template_name = 'market_confirm_delete.html'
    model = Market
    success_url = reverse_lazy('create_market')
    success_message = "Data has been Deleted successfully!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteMarket, self).delete(request, *args, **kwargs)




class ViewMainSetting(LoginRequiredMixin, ListView):
    template_name = 'mainsetting.html'
    model = MainSetting
    fields = '__all__'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form = super().form_valid(form)
        messages.success(self.request, 'Data has been Modified successfully!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        print('============================')
        return form
    
    def get_form(self, **kwargs):
        form = super(ViewMainSetting, self).get_form(**kwargs)
        form.fields['date_for_all_store'].widget = forms.TextInput(attrs={'type':'date'}) 
        form.fields['device'].required = False;
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(ViewMainSetting, self).get_context_data(**kwargs)
        context['market_data'] = Market.objects.all()
        totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
        context['totalMarket'] = totalMarket
        context['totalStores'] = totalStores
        context['totalAccurated'] = totalAccurated
        context['totalNoneAccurated'] = totalNoneAccurated
        context['MainSetting'] = MainSetting.objects.all()
        context['edit_form'] = False
        return context


class UpdateMainSetting(LoginRequiredMixin, UpdateView):
    template_name = 'mainsetting.html'
    model = MainSetting
    fields = '__all__'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form = super().form_valid(form)
        messages.success(self.request, 'Data has been Modified successfully!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        print('============================')
        return form
    
    def get_form(self, **kwargs):
        form = super(UpdateMainSetting, self).get_form(**kwargs)
        form.fields['date_for_all_store'].widget = forms.TextInput(attrs={'type':'date'}) 
        form.fields['device'].required = False;
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateMainSetting, self).get_context_data(**kwargs)
        context['market_data'] = Market.objects.all()
        totalMarket, totalStores, totalAccurated, totalNoneAccurated = getAllInfo()
        context['totalMarket'] = totalMarket
        context['totalStores'] = totalStores
        context['totalAccurated'] = totalAccurated
        context['totalNoneAccurated'] = totalNoneAccurated
        context['MainSetting'] = MainSetting.objects.all()
        context['edit_form'] = True
        return context