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

        # 現在時刻取得
        timestamp = data.get("timestamp")

        # JSONバリデーション
        ValidatorService.validate(data)

        # Device取得
        device = DeviceService.get_or_create(
            data["deviceName"]
        )

        # データ変換
        moisture = ConversionService.calculate_moisture(
            data["soilRaw"]
        )

        light = ConversionService.calculate_light_score(
            data["lightRaw"]
        )

        # DB保存
        SensorLog.objects.create(
            device=device,
            timestamp=timestamp or timezone.now(),
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