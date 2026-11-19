from django.shortcuts import render

from dashboard.forms import SensorTrendFilterForm
from dashboard.models import Device, Plant
from dashboard.sensor_trend_periods import DEFAULT_TREND_PERIOD, TREND_PERIODS
from dashboard.services.sensor_trend_service import METRICS, get_sensor_trends


def daily_summary_list(request):
    template_name = "daily_summaries/daily_summary_list.html"
    form = SensorTrendFilterForm(
        {"period": request.GET.get("period", DEFAULT_TREND_PERIOD)}
    )

    if not form.is_valid():
        return render(request, template_name, {"form": form}, status=400)

    period_key = form.cleaned_data["period"]
    trends = get_sensor_trends(period_key)
    trends["use_daily_summary"] = TREND_PERIODS[period_key].use_daily_summary
    
    devices = Device.objects.order_by("device_name")

    # 選択期間に記録された植物名をまとめて取得する。
    plant_ids = {
        series["plant_id"]
        for series in trends["series"]
        if series["plant_id"] is not None
    }
    plant_names = dict(
        Plant.objects.filter(pk__in=plant_ids).values_list("pk", "custom_name")
    )

    devices_with_data = set()
    for series in trends["series"]:
        series["plant_name"] = plant_names.get(series["plant_id"], "植物未設定")

        # 0も有効な計測値として扱う。
        if any(value is not None for metric in METRICS for value in series[metric]):
            devices_with_data.add(series["device_id"])
    

    return render(
        request,
        template_name,
        {
            "form": form,
            "devices": devices,
            "devices_with_data": devices_with_data,
            "trends": trends,
        },
    )