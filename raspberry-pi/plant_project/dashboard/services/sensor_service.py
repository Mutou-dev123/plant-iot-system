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
from datetime import datetime

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

        # バリデーション
        ValidatorService.validate(data)

        # Device取得
        device = DeviceService.get_or_create(
            data["deviceName"]
        )

        # 日時変換
        measured_at = datetime.fromtimestamp(
            data["timestamp"],
            tz=timezone.get_current_timezone()
        )

        # ラズパイ受信日時
        received_at = timezone.now()

        # データ変換
        # 土壌水分（％）に変換
        moisture = ConversionService.calculate_moisture(
            data["soilRaw"]
        )

        # 光量スコアに変換
        light = ConversionService.calculate_light_score(
            data["lightRaw"]
        )

        # DB保存
        SensorLog.objects.create(
            device=device,
            measured_at=measured_at,
            received_at=received_at,
            soil_raw=data["soilRaw"],
            light_raw=data["lightRaw"],
            moisture=moisture,
            light=light,
            temperature=data["temperature"],
            humidity=data["humidity"]
        )

        return {
            "status": "success",
            "next_interval": device.interval_seconds
        }