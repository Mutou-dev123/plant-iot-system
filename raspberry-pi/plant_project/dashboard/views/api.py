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

import re, json


# ==========================================
# データ受信API
# ==========================================

# ESP32からセンサーデータを受信し、
# SensorServiceへ処理を委譲するAPI
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

# ESP32の適用バージョンを受け取るAPI
@csrf_exempt
def report_applied_config(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": "invalid_method"},
            status=405,
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON."},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"status": "error", "message": "JSON object required."},
            status=400,
        )

    mac_address = data.get("macAddress")
    version = data.get("applied_config_version")

    if (
        not isinstance(mac_address, str)
        or re.fullmatch(
            r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}",
            mac_address.strip(),
        ) is None
    ):
        return JsonResponse(
            {"status": "error", "message": "Invalid macAddress"},
            status=400,
        )

    if type(version) is not int or version <= 0:
        return JsonResponse(
            {
                "status": "error",
                "message": "applied_config_version must be a positive integer.",
            },
            status=400,
        )

    mac_address = mac_address.strip().upper()
    device = Device.objects.filter(mac_address=mac_address).first()

    if device is None:
        return JsonResponse(
            {"status": "error", "message": "Device not found."},
            status=404,
        )

    if version > device.config_version:
        return JsonResponse(
            {
                "status": "error",
                "message": "Reported version is newer than the desired config.",
            },
            status=409,
        )

    # 古い報告が遅れて届いても、保存済みの版を巻き戻さない
    if (
        device.applied_config_version is None
        or version >= device.applied_config_version
    ):
        device.applied_config_version = version
        device.save(update_fields=["applied_config_version"])

    return JsonResponse(
        {
            "status": "recorded",
            "applied_config_version": device.applied_config_version,
            "config_version": device.config_version,
            "up_to_date": (
                device.applied_config_version == device.config_version
            ),
        }
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