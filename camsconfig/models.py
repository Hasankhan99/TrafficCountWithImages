from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
# Create your models here.

class Market(models.Model):
    market_name = models.CharField(max_length=100, unique=True)
    class Meta:
        db_table = 'market'

    def __str__(self):
        return self.market_name

    def get_absolute_url(self):
        return reverse_lazy('create_market')

class StoresStatus(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        db_table = 'storestatus'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('create_storestatus')


class CamsData(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100)
    store_unique_id = models.CharField(max_length=10, unique=True)
    store_channel = models.IntegerField()
    conf = models.IntegerField(default=25)
    thresh = models.IntegerField(default=45)
    snaps_path = models.TextField(default='/media/live/livedb/cams/Compliefile/C:/Store_Cam_picture/')
    date = models.DateField(auto_now=timezone.now().strftime('%Y-%m-%d'))
    number_of_snaps = models.IntegerField(default=6)
    hourly_api = models.BooleanField(default=True)
    total_api = models.BooleanField(default=True)
    device = models.CharField(max_length=4 ,choices=(('cpu', 'CPU'), (' ', 'GPU')), default=' ', null=False)
    time = models.IntegerField(default=9)
    current_status = models.ForeignKey(StoresStatus, on_delete=models.CASCADE, default=2)
    status = models.BooleanField('Active / Deactive',default=True)
    server_name = models.CharField(max_length=15, choices=[('Aiprod1', 'Aiprod1'),('Aiprod2', 'Aiprod2'),('Aiprod3', 'Aiprod3'),] , default='Aiprod2')
    class Meta:
        db_table = 'camsdata'

    def __str__(self):
        return self.store_name

    def get_absolute_url(self):
        return reverse_lazy('create_programconfig')

class MisTrafficCount(models.Model):
    store_uid = models.ForeignKey(CamsData, on_delete=models.CASCADE)
    total_count = models.IntegerField()
    hourly_count = models.IntegerField()
    time = models.CharField(max_length=10)
    date = models.CharField(max_length=20)
    conf = models.IntegerField()
    thresh = models.IntegerField()
    number_of_snaps = models.IntegerField()

    class Meta:
        db_table = 'mistrafficcount'

    def __str__(self):
        return self.store_uid.store_name

    def get_absolute_url(self):
        return reverse_lazy('index')


class MainSetting(models.Model):

    date_for_all_store = models.CharField(max_length=10)
    path_for_all_store = models.CharField(max_length=255, default='/media/live/livedb/cams/Compliefile/C:/Store_Cam_picture/')
    device = models.CharField(max_length=10, default='', choices=[('', 'GPU'), ('CPU', 'CPU')])
    source_weight = models.CharField(max_length=50, default='yolov5s.pt', choices=[('yolov5s.pt', 'yolov5s.pt'), ('yolov5m.pt', 'yolov5m.pt'), ('yolov5l.pt', 'yolov5l.pt'), ('yolov5x.pt', 'yolov5x.pt')])
    hourly_api_for_all_store_live = models.BooleanField(default=True)
    total_api_for_all_store_live = models.BooleanField(default=True)
    api_for_all_store_local = models.BooleanField(default=True)
    is_system_date = models.BooleanField(default=True)

    class Meta:
        db_table = 'mainsetting'

    def __str__(self):
        return self.date_for_all_store

    def get_absolute_url(self):
        return reverse_lazy('view_main_setting')

class ManualCount(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    store_name = models.ForeignKey(CamsData, on_delete=models.CASCADE)
    date = models.CharField(max_length=20)
    count = models.IntegerField()

    class Meta:
        db_table = 'manualcount'
        unique_together = (("store_name", "date"),)

    def __str__(self):
        return f'Total Count is {self.count} of {self.store_name.store_name} and market is {self.market.market_name} on Date {self.date}'

    def get_absolute_url(self):
        return reverse_lazy('create_manual')