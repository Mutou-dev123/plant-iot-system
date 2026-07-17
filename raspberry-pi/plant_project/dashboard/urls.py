from django.urls import path
from . import views

urlpatterns = [
    # ダッシュボード
    path('', views.index, name='index'),

    # ESP32からのデータ受け取り用API
    path('api/receive', views.api_receive_data, name='api_receive_data'),
]