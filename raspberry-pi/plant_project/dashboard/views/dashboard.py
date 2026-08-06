# ==========================================
# ダッシュボード画面ビュー
# ==========================================

from django.shortcuts import render
from django.utils import timezone

from dashboard.models import SensorLog


def index(request):

    latest_log = SensorLog.objects.first()

    history_logs = list(
        SensorLog.objects.all()[:20]
    )
    history_logs.reverse()

    for log in history_logs:
        print(log.measured_at)

    if latest_log:
        interval_seconds = latest_log.device.interval_seconds
    else:
        interval_seconds = 300

    # ==========================
    # グラフ用データ
    # ==========================

    time_labels = [
        timezone.localtime(log.measured_at).strftime("%H:%M:%S")
        for log in history_logs
    ]

    temp_data = [
        log.temperature
        for log in history_logs
    ]

    humidity_data = [
        log.humidity
        for log in history_logs
    ]

    moisture_data = [
        log.moisture
        for log in history_logs
    ]

    context = {
        "latest": latest_log,
        "history": history_logs,
        "interval": interval_seconds,

        "time_labels": time_labels,
        "temp_data": temp_data,
        "humidity_data": humidity_data,
        "moisture_data": moisture_data,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )