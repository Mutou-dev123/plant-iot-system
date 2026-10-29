from django.urls import path

from .views import dashboard
from .views import plants
from .views import devices
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
    # 育成植物管理
    # ==========================================

    # 一覧
    path(
        "plants/",
        plants.plant_list,
        name="plant_list",
    ),

    # 作成
    path(
        "plants/create/",
        plants.plant_create,
        name="plant_create",
    ),
    
    # 詳細
    path(
        "plants/<int:plant_id>/",
        plants.plant_detail,
        name="plant_detail",
    ),

    # 編集
    path(
        "plants/<int:plant_id>/edit/",
        plants.plant_edit,
        name="plant_edit",
    ),

    # 削除
    path(
        "plants/<int:plant_id>/delete/",
        plants.plant_delete,
        name="plant_delete",
    ),

    # ==========================================
    # デバイス管理
    # ==========================================
    
    # 一覧
    path(
        "devices/",
        devices.device_list,
        name="device_list",
    ),

    # 作成
    path(
        "devices/create",
        devices.device_create,
        name="device_create",
    ),

    # 詳細
    path(
        "devices/<int:device_id>/",
        devices.device_detail,
        name="device_detail",
    ),

    # 編集
    path(
        "devices/<int:device_id>/edit/",
        devices.device_edit,
        name="device_edit",
    ),

    # 削除
    path(
        "devices/<int:device_id>/delete/",
        devices.device_delete,
        name="device_delete",
    ),

    # ==========================================
    # API
    # ==========================================

    path(
        "api/receive",
        api.receive_data,
        name="api_receive_data",
    ),

    path(
        "api/device_config/applied/",
        api.report_applied_config,
        name="api_report_applied_config",
    ),

    path(
        "api/chart-data/",
        api.chart_data,
        name="api_chart_data",
    ),

    path(
        "api/device_config/",
        api.device_config,
        name="api_device_config",
    )
]