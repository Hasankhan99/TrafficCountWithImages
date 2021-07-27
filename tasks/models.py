from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import pytz
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Projects(models.Model):
    project_name = models.CharField(max_length=50)
    initiated_date = models.DateField('Request Date')
    start_date = models.DateField()
    expected_date = models.DateField()
    complete_date = models.DateField()
    # status = models.IntegerField('Status (from 0 to 100 %)' )
    # progress = models.CharField(max_length=50, 
    #     choices=[
    #         ('Pending','Pending'),
    #         ('In Process','In Process'),
    #         ('Done','Done')
    #     ]
    # )
    details = models.TextField()

    class Meta:
        db_table = 'projects'
        ordering = ['-id']

    def __str__(self):
        return self.project_name

    def get_absolute_url(self):
        return reverse_lazy('projects_create')

class Assignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.ForeignKey(Projects, on_delete=models.CASCADE)
    assign_date = models.DateField(null=True)
    move_date = models.DateField(null=True)
    status = models.CharField(max_length=50, 
        choices=[
            ('0','Pending'),
            ('1','Approved')
        ],
        default='0'
    )
    details = models.TextField()

    class Meta:
        db_table = 'assignment'
        ordering = ['-id']

    def __str__(self):
        return self.project_name.project_name

    def get_absolute_url(self):
        return reverse_lazy('assignment_create')



class ProjectStatus(models.Model):
    project = models.ForeignKey(Projects, related_name='project_status', on_delete=models.CASCADE)
    user = models.IntegerField(blank=True, null=True )
    progress = models.IntegerField('Status (from 0 to 100 %)', default=0, blank=True)
    status = models.CharField(max_length=50, 
        choices=[
            ('Pending','Pending'),
            ('In Process','In Process'),
            ('Done','Done')
        ],
        default='Pending', blank=True
    )
    active_status = models.IntegerField(default=0)
    date_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'projectstatus'
        get_latest_by = 'date_time'

    def __str__(self):
        return self.project

@receiver(post_save, sender=Projects)
def create_or_update_projectstatus(sender, instance, created, **kwargs):
    if created:
        dt = ProjectStatus.objects.create(project=instance)
        dt.save()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_messages')
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} to {}'.format(self.sender.username, self.receiver.username)

class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    send_date = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    class Meta:
        db_table = 'messages'

    def __str__(self):
        return self.details

    def get_absolute_url(self):
        return reverse_lazy('taskdetail')