# ==========================================
# APIビュー
# ==========================================

# APIリクエストの受付とレスポンスの返却を管理する
#
# ・HTTPメソッドの確認
# ・サービス層の呼び出し
# ・JSONレスポンスの返却
# ・HTTPステータスコードの設定

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from dashboard.services.sensor_service import SensorService

from dashboard.models import Device, SensorLog

import re


# ==========================================
# センサーデータ受信API
# ==========================================
# ESP32からセンサーデータを受信し、
# SensorServiceへ処理を委譲する
@csrf_exempt
def receive_data(request):

    if request.method != "POST":
        return JsonResponse(
            {"status": "invalid_method"},
            status=405
        )

    try:

        result = SensorService.receive(request.body)

        return JsonResponse(result)

    except Exception as e:

        return JsonResponse(
            {
                "status": "error",
                "message": str(e)
            },
            status=400
        )


# ==========================================
# グラフデータ取得API
# ==========================================
# センサーログを取得し、
# グラフ表示用のJSONデータを返却する
def chart_data(request):

    logs = list(
        SensorLog.objects.all()[:20]
    )
    logs.reverse()

    data = {
        "labels": [
            timezone.localtime(log.measured_at).strftime("%H:%M:%S")
            for log in logs
        ],
        "temperature": [
            log.temperature
            for log in logs
        ],
        "humidity": [
            log.humidity
            for log in logs
        ],
        "moisture": [
            log.moisture
            for log in logs
        ],
    }

    return JsonResponse(data)


# ==========================================
# デバイス設定取得API
# ==========================================
def device_config(request):

    if request.method != "GET":
        return JsonResponse(
            {"status": "invalid_method"},
            status=405
        )

    mac_address = request.GET.get("macAddress", "").strip().upper()

    if not re.fullmatch(
        r"(?:[0-9A-F]{2}:){5}[0-9A-F]{2}",
        mac_address,
    ):
        return JsonResponse(
            {
                "status": "error",
                "message": "A valid macAddress query parameter is required."
            },
            status=400
        )

    device = Device.objects.filter(mac_address=mac_address).first()

    if device is None:
        return JsonResponse(
            {
                "status": "error",
                "message": "Device not found.",
            },
            status=404
        )

    return JsonResponse(
        {
            "config_version": device.config_version,
            "interval_seconds": device.interval_seconds,
            "sensors": {
                "dht": device.desired_dht_enabled,
                "soil": device.desired_soil_enabled,
                "light": device.desired_light_enabled,
            },
        }
    )