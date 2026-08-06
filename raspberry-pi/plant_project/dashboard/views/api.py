# ==========================================
# APIビュー
# ==========================================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from dashboard.services.sensor_service import SensorService

from dashboard.models import SensorLog

# データ受取
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

# グラフデータ
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