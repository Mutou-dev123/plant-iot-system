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
#
# ※このサービスを中心に他のサービスを動かす

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from django.utils import timezone

from django.db import transaction

from dashboard.models import SensorLog, DailySensorAggregationTask
from .device_service import DeviceService           # デバイス管理
from .conversion_service import ConversionService   # センサーデータ変換
from .validator_service import ValidatorService     # バリデーションサービス

JAPAN_TZ = ZoneInfo("Asia/Tokyo")


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
        device = DeviceService.get_or_create(data)

        # 日時変換
        measured_at = datetime.fromtimestamp(
            data["timestamp"],
            tz=timezone.get_current_timezone()
        )

        # ラズパイ受信日時
        received_at = timezone.now()


        # ==========================================
        # センサーデータの取得
        # ==========================================

        # DHTセンサー
        if data["dhtEnabled"]:
            temperature = data["temperature"]
            humidity = data["humidity"]
        else:
            temperature = None
            humidity = None
        
        # 土壌水分センサー
        if data["soilEnabled"]:
            soil_raw = data["soilRaw"]
        else:
            soil_raw = None

        # 光センサー
        if data["lightEnabled"]:
            light_raw = data["lightRaw"]
        else:
            light_raw = None


        # ==========================================
        # データ変換
        # ==========================================

        # 土壌水分（％）に変換
        moisture = (
            None
            if data["soilRaw"] is None
            else ConversionService.calculate_moisture(data["soilRaw"])
        )

        # 光量スコアに変換
        light = (
            None
            if data["lightRaw"] is None
            else ConversionService.calculate_light_score(data["lightRaw"])
        )

        plant = device.plant
        summary_date = timezone.localdate(measured_at, timezone=JAPAN_TZ)

        # ==========================================
        # DB保存
        # ==========================================
        with transaction.atomic():
            SensorLog.objects.create(
                device=device,
                plant=plant,
                measured_at=measured_at,
                received_at=received_at,
                soil_raw=soil_raw,
                light_raw=light_raw,
                moisture=moisture,
                light=light,
                temperature=temperature,
                humidity=humidity
            )

            DailySensorAggregationTask.objects.update_or_create(
                device=device,
                plant=plant,
                summary_date=summary_date,
                defaults={
                    "status": DailySensorAggregationTask.Status.PENDING,
                    "last_error": "",
                },
            )

            # 最終通信日時を更新
            device.last_seen_at = received_at
            device.save(update_fields=["last_seen_at"])

        return {
            "status": "success",
            "next_interval": device.interval_seconds
        }