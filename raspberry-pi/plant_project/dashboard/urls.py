from django.urls import path

from .views import dashboard
from .views import plants
from .views import api

urlpatterns = [

    # ==========================================
    # ダッシュボード
    # ==========================================

    path(
        "",
        dashboard.index,
        name="dashboard",
    ),

    # ==========================================
    # 植物管理
    # ==========================================

    path(
        "plants/",
        plants.index,
        name="plant_list",
    ),

    # ==========================================
    # デバイス管理
    # ==========================================
    
    #path(
    #    "devices/",
    #    devices.index,
    #    name="devices",
    #),

    # ==========================================
    # API
    # ==========================================

    path(
        "api/receive",
        api.receive_data,
        name="api_receive_data",
    ),
]