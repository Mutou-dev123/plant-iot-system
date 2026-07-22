# ==========================================
# APIビュー
# ==========================================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from dashboard.services.sensor_service import SensorService


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