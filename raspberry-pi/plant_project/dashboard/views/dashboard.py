# ==========================================
# ダッシュボード画面ビュー
# ==========================================

from django.shortcuts import render
from django.utils import timezone

from dashboard.models import SensorLog


# ==========================================
# 環境判定
# ==========================================
def check_environment(label, value, minimum, maximum, unit):

    # センサーデータがない場合
    if value is None:
        return {
            "label": label,
            "value_display": "未計測",
            "status": "unmeasured",
            "message": f"{label}のデータを取得できていません。",
        }

    value_display = f"{value:.1f}{unit}"

    # しきい値が未設定の場合
    if minimum is None and maximum is None:
        return {
            "label": label,
            "value_display": value_display,
            "status": "unconfigured",
            "message": "しきい値未設定のため判定対象外です。",
        }

    # センサー値がしきい値（下限）を下回った場合
    if minimum is not None and value < minimum:
        message = (
            f"{label}が下限を下回っています。"
            f"現在値：{value_display}、"
            f"下限：{minimum:.1f}{unit}"
        )

        return {
            "label": label,
            "value_display": value_display,
            "status": "warning",
            "message": message,
        }

    # センサー値がしきい値（上限）を上回った場合
    if maximum is not None and value > maximum:
        message = (
            f"{label}が上限を超えています。"
            f"現在値：{value_display}、"
            f"上限：{maximum:.1f}{unit}"
        )

        return {
            "label": label,
            "value_display": value_display,
            "status": "warning",
            "message": message,
        }

    # センサー値がしきい値の範囲内の場合
    return {
        "label": label,
        "value_display": value_display,
        "status": "normal",
        "message": "設定されたしきい値の範囲内です。",
    }


# ==========================================
# ダッシュボード
# ==========================================
def index(request):

    latest_log = (
        SensorLog.objects
        .select_related("device__plant__plant_master")
        .first()
    )

    history_logs = list(
        SensorLog.objects.all()[:20]
    )
    history_logs.reverse()

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

    temp_data = []
    last_temp = None

    for log in history_logs:

        if log.temperature is not None:
            last_temp = log.temperature

        temp_data.append(last_temp)

    humidity_data = []
    last_humidity = None

    for log in history_logs:

        if log.humidity is not None:
            last_humidity = log.humidity

        humidity_data.append(last_humidity)

    moisture_data = [
        log.moisture
        for log in history_logs
    ]

    # ==========================
    # 環境判定・アラート
    # ==========================

    environment_statuses = []
    alerts = []
    plant_master = None

    # 植物マスタの取得
    if latest_log:
        plant = latest_log.device.plant

        if plant:
            plant_master = plant.plant_master

    # 植物マスタがない場合も判定カードを作成する
    if latest_log:

        # マスタがない場合はしきい値を None にする
        if plant_master:
            temperature_min = plant_master.optimal_temperature_min
            temperature_max = plant_master.optimal_temperature_max

            humidity_min = plant_master.optimal_humidity_min
            humidity_max = plant_master.optimal_humidity_max

            moisture_min = plant_master.optimal_moisture_min
            moisture_max = plant_master.optimal_moisture_max

        else:
            temperature_min = temperature_max = None
            humidity_min = humidity_max = None
            moisture_min = moisture_max = None

        sensor_settings = [
            (
                "温度",
                latest_log.temperature,
                temperature_min,
                temperature_max,
                "℃",
            ),
            (
                "湿度",
                latest_log.humidity,
                humidity_min,
                humidity_max,
                "%",
            ),
            (
                "土壌水分",
                latest_log.moisture,
                moisture_min,
                moisture_max,
                "%",
            ),
        ]

        for label, value, minimum, maximum, unit in sensor_settings:

            status = check_environment(
                label=label,
                value=value,
                minimum=minimum,
                maximum=maximum,
                unit=unit,
            )

            # マスタがない場合は、値を表示するが判定対象外にする
            if not plant_master and value is not None:
                status["status"] = "unconfigured"
                status["message"] = (
                    "植物マスタ未設定のため判定対象外です。"
                )

            environment_statuses.append(status)

            if status["status"] == "warning":
                alerts.append(status)

    # ==========================
    # テンプレートへ渡すデータ
    # ==========================

    context = {
        "latest": latest_log,
        "history": history_logs,
        "interval": interval_seconds,

        "time_labels": time_labels,
        "temp_data": temp_data,
        "humidity_data": humidity_data,
        "moisture_data": moisture_data,

        "plant_master": plant_master,
        "environment_statuses": environment_statuses,
        "alerts": alerts,
        "has_alerts": bool(alerts),
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )