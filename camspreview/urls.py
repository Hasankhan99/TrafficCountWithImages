from django.urls import path

from . import views


urlpatterns = [
    path('', views.camspreviewindex, name='camspreviewindex')
]