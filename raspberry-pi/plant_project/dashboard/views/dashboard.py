# ==========================================
# ダッシュボード画面ビュー
# ==========================================

from django.shortcuts import render

from dashboard.models import SensorLog


def index(request):

    latest_log = SensorLog.objects.order_by("-id").first()

    history_logs = list(
        SensorLog.objects.order_by("-id")[:20]
    )
    history_logs.reverse()

    if latest_log:
        interval_seconds = latest_log.device.interval_seconds
    else:
        interval_seconds = 300

    context = {
        "latest": latest_log,
        "history": history_logs,
        "interval": interval_seconds,
    }

    return render(
        request,
        "dashboard/index.html",
        context
    )