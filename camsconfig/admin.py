from django.contrib import admin

# Register your models here.
from import_export import resources
from .models import CamsData, ManualCount


class CamsDataResource(resources.ModelResource):
    class Meta:
        model = CamsData



class ManualCountResource(resources.ModelResource):
    class Meta:
        model = ManualCount
        # fields = ('store_name','store_unique_id','store_channel','conf','thresh','snaps_path','number_of_snaps','hourly_api','total_api','device','time','market')
        # export_order = ('store_name','store_unique_id','store_channel','conf','thresh','snaps_path','number_of_snaps','hourly_api','total_api','device','time','market')
        # exclude = ('id',)
