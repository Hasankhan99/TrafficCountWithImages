from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from .models import Projects, Assignment, Messages, ProjectStatus
from .forms import MessagesForm
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Max
from websocket.connection import WebSocket
from datetime import timezone, datetime, timedelta
import pytz
# Create your views here.

# START IMPORT LIBRARY TO SEND EMAIL.
import smtplib, ssl
from smtplib import SMTPException
# END IMPORT LIBRARY TO SEND EMAIL.

def sendMail():  
   smtp_server = 'smtp.gmail.com'
   port = 465
   sender = 'your gmail id'
   password = 'your gmail password'
   receiver ='masoodazhar60@gmail.com'
   message = ('Hello, i am from python sendMail function!')
   # print(st) 
   context = ssl.create_default_context()
   with smtplib.SMTP_SSL(smtp_server, port,context=context) as server:
      server.login(sender,password)
      server.sendmail(sender,receiver,message)
      print('Email has been sent!')

def taskdetail(request, pk):
    # userid = userid if request.user.is_superuser else request.user.pk
    projectDetail = Projects.objects.get(pk=pk)
    messagesDetials = Messages.objects.filter(project=pk)
    status_list = ['Pending','In Process','Done']
    progress_list = [i for i in range(101)]
    projectAssignedDetail = ProjectStatus.objects.filter(project=pk).last()
    proMessages = Messages.objects.filter(project=pk)
    current_user = Messages.objects.filter(project=pk).first()
    context = {
        'projectDetail': projectDetail, 
        'messagesDetials': messagesDetials, 
        'status_list': status_list,
        'progress_list': progress_list,
        'room_name': str(pk),
        'projectAssignedDetail': projectAssignedDetail,
        'proMessages': proMessages,
        'current_user': current_user
    }

    return render(request,'taskdetails.html', context)

def progress_task(request):
    projectid = request.POST.get('projectid')
    userid = request.POST.get('userid')
    val = request.POST.get('val')
    varify = request.POST.get('varify')
    print(projectid,userid,val,varify, '===============')
    end = 0
    if varify == 'status':
        try:
            project = ProjectStatus.objects.select_for_update().filter(project=projectid, user=userid).latest('date_time')
            project.status=val
            project.save()
            end = True
        except Exception as ex:
            end = 0
    else:
        try:
            project = ProjectStatus.objects.select_for_update().filter(project=projectid, user=userid).latest('date_time')
            project.progress=val
            project.save()
            end = True
        except:
            end = 0
    print(end)
    return JsonResponse({'data': end})

class TasksIndex(TemplateView):
    template_name = 'tasksIndex.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super(TasksIndex, self).get_context_data(**kwargs)
        context['projects'] = Projects.objects.all()
        users = User.objects.filter(~Q(is_superuser=1))
        allProjects = []
        for user in users:
            projects = Assignment.objects.filter(user=user.pk).count()
            # projectpk = Assignment.objects.filter(user=user.pk)
            # completedProjects = ProjectStatus.objects.filter(user=user.pk, progress__gt=99).count()
            # inProcessProjects = ProjectStatus.objects.filter(user=user.pk, progress__lt=99).count()
            allProjects.append({
                'pk': user.pk,
                'username': user.username,
                'numOfPro': projects,
                # 'completedProjects': completedProjects,
                # 'inProcessProjects': inProcessProjects
            })
        context['users'] = allProjects
        return context

def sendMessage(request):
    time = str(datetime.now()).split('.')[0]
    local = pytz.timezone("America/Los_Angeles")
    naive = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    time = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    msg = ''
    projectpk = request.POST.get('project')
    userpk = request.POST.get('user')
    print('from api===================',request.session.get('userpk'))
    print('loggedin===================',request.user.pk)
    if request.method == 'POST':
        form = MessagesForm(request.POST)
        if form.is_valid():
            checkTime = Messages.objects.filter(send_date__contains=time)
            # if userpk==request.user.pk:
            if len(checkTime)<1:
                # print('after===================',userpk)
                form.save()
                msg = 'saved'
        else:
            msg = form.errors
    else:
        msg = 'there is an error!'
    
    messageDict = []
    allMessages = Messages.objects.filter(project=projectpk)
    for msgd in allMessages:
        messageDict.append({
            'message': msgd.details,
            'user': msgd.user.pk
        })
    context = {
        'data':messageDict
    }
    # return HttpResponseRedirect(reverse_lazy('taskdetail', kwargs={'pk':projectpk}))
    return JsonResponse(context)
    
def tasks(request,userid=0):
    userid = userid if request.user.is_superuser else request.user.pk
    tasks = Assignment.objects.filter(user=userid)
    taskList = []
    projectstatus_active = ProjectStatus.objects.filter(user=userid, active_status=1)
    projectstatus_inactive = ProjectStatus.objects.filter(user=userid, active_status=0)
    for task in tasks:
        projectsProgressObj = ProjectStatus.objects.filter(user=userid, project=task.project_name).aggregate(max=Max('progress'))
        projectStatus = ProjectStatus.objects.filter(user=userid, project=task.project_name).last()
        taskList.append({
            'project_name': task.project_name,
            'progress': projectsProgressObj['max'],
            'status': projectStatus.status 
        })
        
    context = {
        'tasks': tasks,
        'projectstatus_active': projectstatus_active,
        'projectstatus_inactive': projectstatus_inactive,
        'taskList':taskList
    }
    return render(request,'tasks.html', context)

def ar_tasks(request, pk):
    tasks = Assignment.objects.filter(pk=pk)
    userpk = Assignment.objects.get(pk=pk)
    tasks.update(status='1')
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse_lazy('taskadmin', kwargs={'userid':userpk.user.pk}))
    else:
        return HttpResponseRedirect(reverse_lazy('taskuser'))


# STARTS STORES STATUS ON
class CreateProjects(LoginRequiredMixin ,CreateView):
    template_name = 'projects.html'
    model = Projects
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
        form = super(CreateProjects, self).get_form(**kwargs)
        form.fields['initiated_date'].widget = forms.TextInput(attrs={'type':'date'}) 
        form.fields['start_date'].widget = forms.TextInput(attrs={'type':'date'}) 
        form.fields['expected_date'].widget = forms.TextInput(attrs={'type':'date'}) 
        form.fields['complete_date'].widget = forms.TextInput(attrs={'type':'date'}) 
        # form.fields['status'].widget = forms.TextInput(attrs={'type':'number'}) 
        # form.fields['date'].required = False
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(CreateProjects, self).get_context_data(**kwargs)
        context['projects'] = Projects.objects.all()
        return context

class UpdateProjects(LoginRequiredMixin, UpdateView):
    template_name = 'projects.html'
    model = Projects
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
        form = super(UpdateProjects, self).get_form(**kwargs)
        form.fields['initiated_date'].widget = forms.TextInput(attrs={'type':'date'}) 
        form.fields['start_date'].widget = forms.TextInput(attrs={'type':'date'}) 
        form.fields['expected_date'].widget = forms.TextInput(attrs={'type':'date'}) 
        form.fields['complete_date'].widget = forms.TextInput(attrs={'type':'date'}) 
        # form.fields['status'].widget = forms.TextInput(attrs={'type':'number'}) 
        # form.fields['date'].required = False
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateProjects, self).get_context_data(**kwargs)
        context['projects'] = Projects.objects.all()
        context['edit_form'] = True
        return context

class DeleteProjects(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    template_name = 'projects_confirm_delete.html'
    model = Projects
    success_url = reverse_lazy('projects_create')
    success_message = "Data has been Deleted successfully!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteProjects, self).delete(request, *args, **kwargs)


# STARTS Assignment
class CreateAssignment(LoginRequiredMixin ,CreateView):
    template_name = 'assignments.html'
    model = Assignment
    fields = '__all__'
    login_url = reverse_lazy('login')
   
    def form_valid(self, form):
        form = super().form_valid(form)
        projectid = self.request.POST.get('project_name')
        projectstatus = ProjectStatus.objects.filter(project=projectid)
        projectstatus.update(user=self.request.POST.get('user'))
        messages.success(self.request, 'Data has been saved successfully!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        print('============================')
        return form
    
    def get_form(self, **kwargs):
        form = super(CreateAssignment, self).get_form(**kwargs)
        form.fields['assign_date'].widget = forms.TextInput(attrs={'type':'date'}) 
        form.fields['move_date'].required = False
        form.fields['assign_date'].required = False
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(CreateAssignment, self).get_context_data(**kwargs)
        context['assignments'] = Assignment.objects.all()
        # context['edit_form'] = True
        context['users'] = User.objects.all()
        return context

class UpdateAssignment(LoginRequiredMixin, UpdateView):
    template_name = 'assignments.html'
    model = Assignment
    fields = '__all__'
    login_url = reverse_lazy('login')
   
    def form_valid(self, form):
        form = super().form_valid(form)

        projectid = self.request.POST.get('project_name')
        userid = self.request.POST.get('user')
        # GET THE PROJECT OLD STATUS IF EXISTS.
        try:
            oldProStatus = ProjectStatus.objects.filter(project=projectid).last()
            print('===============',oldProStatus.progress)
            psCreate = ProjectStatus.objects.create(project=oldProStatus.project, user=userid, status=oldProStatus.status, progress=oldProStatus.progress)
            psCreate.save()
            messages.success(self.request, 'Data has been saved successfully!')

        except Exception as ex:
            pass
            messages.warning(self.request, 'There is an issue. project has nat been assigned before. plase add new. or select assigned one!')
        return form

    def form_invalid(self, form):
        form = super().form_invalid(form)
        print('============================')
        return form
    
    def get_form(self, **kwargs):
        form = super(UpdateAssignment, self).get_form(**kwargs)
        form.fields['assign_date'].widget = forms.TextInput(attrs={'type':'date'}) 
         # form.fields['date'].required = False
        form.fields['move_date'].required = False
        form.fields['assign_date'].required = False
        return form

    def get_context_data(self, *args, **kwargs):
        context = super(UpdateAssignment, self).get_context_data(**kwargs)
        context['assignments'] = Assignment.objects.all()
        context['edit_form'] = True
        context['users'] = User.objects.all()
        return context

class DeleteAssignment(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    template_name = 'assignments_confirm_delete.html'
    model = Assignment
    success_url = reverse_lazy('assignment_create')
    success_message = "Data has been Deleted successfully!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteAssignment, self).delete(request, *args, **kwargs)

