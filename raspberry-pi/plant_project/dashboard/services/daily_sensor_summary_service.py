# ==========================================
# 日別集計サービス
# ==========================================

# センサーデータの項目を平均・最大・最小を算出する
#
# ・
# ・
# ・

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import Avg, Count, Max, Min

from dashboard.models import DailySensorSummary, SensorLog

JAPAN_TZ = ZoneInfo("Asia/Tokyo")


class DailySensorSummaryService:

    @staticmethod
    @transaction.atomic
    def aggregate_day(device, plant, summary_date):
        start_at = datetime.combine(
            summary_date,
            time.min,
            tzinfo=JAPAN_TZ,
        )
        end_at = start_at + timedelta(days=1)

        logs = SensorLog.objects.filter(
            device=device,
            plant=plant,
            measured_at__gte=start_at,
            measured_at__lt=end_at,
        )

        stats = logs.aggregate(
            log_count=Count("pk"),

            temperature_avg=Avg("temperature"),
            temperature_max=Max("temperature"),
            temperature_min=Min("temperature"),
            temperature_count=Count("temperature"),

            humidity_avg=Avg("humidity"),
            humidity_max=Max("humidity"),
            humidity_min=Min("humidity"),
            humidity_count=Count("humidity"),

            moisture_avg=Avg("moisture"),
            moisture_max=Max("moisture"),
            moisture_min=Min("moisture"),
            moisture_count=Count("moisture"),

            light_avg=Avg("light"),
            light_max=Max("light"),
            light_min=Min("light"),
            light_count=Count("light"),
        )

        if stats["log_count"] == 0:
            return None

        log_count = stats.pop("log_count")

        summary, _ = DailySensorSummary.objects.update_or_create(
            device=device,
            plant=plant,
            summary_date=summary_date,
            defaults={
                **stats,
                "log_count": log_count,
            },
        )

        return summary