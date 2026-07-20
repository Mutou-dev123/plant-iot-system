# ==========================================
# センサーデータサービス
# ==========================================

# ESP32から受信したデータの処理を管理する
#
# ・JSONデータの受信
# ・データのバリデーション
# ・Deviceの取得・登録
# ・データの変換
# ・データベースへの保存

# ※このサービスを中心に他のサービスを動かす

import json

from django.utils import timezone

from dashboard.models import SensorLog
from .device_service import DeviceService           # デバイス管理
from .conversion_service import ConversionService   # センサーデータ変換
from .validator_service import ValidatorService     # バリデーションサービス

class SensorService:

    @staticmethod
    def receive(request_body):
        
        # JSON読み込み
        data = json.loads(request_body)

        print("===== Receive =====")
        print(data)

        return {
            "status": "success",
            "next_interval": 300
        }