from django.contrib import admin
from django.urls import path, include
from .views import (
    index,
    CreateProgramConfig,
    UpdateProgramConfig,
    DeleteProgramConfig,
    get_chart,
    ViewMainSetting,
    UpdateMainSetting,
    export_stores_xls,
    import_stores_xls,
    CreateMarket,
    UpdateMarket,
    DeleteMarket,
    CreateStoreStatus,
    UpdateStoreStatus,
    DeleteStoreStatus,
    CreateManualCount,
    UpdateManualCount,
    DeleteManualCount,
    getStoreByMarket,    
    export_manual_xls,
    import_manual_xls,
    change_status
)

urlpatterns = [
    path('', index, name='index'),
    path('programconfig/', CreateProgramConfig.as_view(), name='create_programconfig'),
    path('programconfig/<int:pk>/edit', UpdateProgramConfig.as_view(), name='update_programconfig'),
    path('programconfig/<int:pk>/delete', DeleteProgramConfig.as_view(), name='delete_programconfig'),

    path('market/', CreateMarket.as_view(), name='create_market'),
    path('market/<int:pk>/edit', UpdateMarket.as_view(), name='update_market'),
    path('market/<int:pk>/delete', DeleteMarket.as_view(), name='delete_market'),

    path('storestatus/', CreateStoreStatus.as_view(), name='create_storestatus'),
    path('storestatus/<int:pk>/edit', UpdateStoreStatus.as_view(), name='update_storestatus'),
    path('storestatus/<int:pk>/delete', DeleteStoreStatus.as_view(), name='delete_storestatus'),

    path('manual/', CreateManualCount.as_view(), name='create_manual'),
    path('manual/<int:pk>/edit', UpdateManualCount.as_view(), name='update_manual'),
    path('manual/<int:pk>/delete', DeleteManualCount.as_view(), name='delete_manual'),

    path('get_chart/', get_chart, name='get_chart'),
    path('main_setting/ChangeDataForAllStores/View', ViewMainSetting.as_view(), name='view_main_setting'),
    path('main_setting/<int:pk>/ChangeDataForAllStores', UpdateMainSetting.as_view(), name='main_setting'),

    path('exportstores/', export_stores_xls , name='exportstores'),
    path('importstores/', import_stores_xls , name='importstores'),

    path('exportmanual/', export_manual_xls , name='exportmanual'),
    path('importmanual/', import_manual_xls , name='importmanual'),
    path('getstorebymarket/', getStoreByMarket , name='getstorebymarket'),
    path('change_statusss/', change_status, name='change_statuss')
]