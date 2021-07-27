
from django.urls import path
from .views import misCount, getAccuracy, statusdetails, export_filtered

urlpatterns = [
    path('', misCount, name='miscount'),
    path('get_chart_month_compare/', getAccuracy , name='get_chart_month_compare'),
    path('StoreStatus/<int:pk>/List', statusdetails, name='statusdetails'),
    path('export_filtered/<int:pk>', export_filtered, name='export_filtered')
    # path('getAccuracy/', getAccuracy, name='get_accuracy'),
]
