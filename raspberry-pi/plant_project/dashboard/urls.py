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
    # 育成植物管理
    # ==========================================

    # 一覧
    path(
        "plants/",
        plants.index,
        name="plant_list",
    ),

    # 作成
    path(
        "plants/create/",
        plants.create,
        name="plant_create",
    ),
    
    # 詳細
    path(
        "plants/<int:plant_id>/",
        plants.detail,
        name="plant_detail",
    ),

    # 編集
    path(
        "plants/<int:plant_id>/edit/",
        plants.edit,
        name="plant_edit",
    ),

    # 削除
    path(
        "plants/<int:plant_id>/delete/",
        plants.delete,
        name="plant_delete",
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