from calendar import monthrange
from collections import defaultdict
from datetime import datetime, time

from django.db.models import Avg, Case, F, IntegerField, Q, Sum, When
from django.db.models.functions import NullIf
from django.utils import timezone

from dashboard.models import DailySensorSummary, SensorLog
from dashboard.sensor_trend_periods import CalendarMonths, TREND_PERIODS
from dashboard.services.daily_sensor_summary_service import JAPAN_TZ


METRICS = ("temperature", "humidity", "moisture", "light")


def _subtract_interval(end_at, interval, steps=1):
    if isinstance(interval, CalendarMonths):
        # 基準日の「日」を使い、移動先に同じ日がない場合は月末に揃える。
        year, month_index = divmod(
            end_at.year * 12 + end_at.month - 1 - interval.count * steps, 12
        )
        month = month_index + 1
        day = min(end_at.day, monthrange(year, month)[1])
        return end_at.replace(year=year, month=month, day=day)

    return end_at - interval * steps


def _period_boundaries(period, now):
    end_at = timezone.localtime(now, JAPAN_TZ)
    if period.use_daily_summary:
        # 日別集計を使う期間は、日本時間の前日分までを含める。
        end_at = datetime.combine(end_at.date(), time.min, tzinfo=JAPAN_TZ)

    start_at = _subtract_interval(end_at, period.duration)
    boundaries = [end_at]

    # 終点からさかのぼり、最初の区間は選択期間の開始日時で切る。
    while boundaries[-1] > start_at:
        boundary = _subtract_interval(end_at, period.bucket_size, len(boundaries))
        boundaries.append(max(start_at, boundary))

    return boundaries[::-1]


def _weighted_average(metric):
    avg_field = f"{metric}_avg"
    count_field = f"{metric}_count"
    valid = Q(**{f"{avg_field}__isnull": False, f"{count_field}__gt": 0})

    # 項目ごとに、日平均 × 有効件数の合計を有効件数の合計で割る。
    weighted_sum = Sum(F(avg_field) * F(count_field), filter=valid)
    total_count = Sum(count_field, filter=valid)
    return weighted_sum / NullIf(total_count, 0)


def get_sensor_trends(period_key, *, now=None):
    period = TREND_PERIODS[period_key]
    boundaries = _period_boundaries(
        period, now if now is not None else timezone.now()
    )

    if period.use_daily_summary:
        queryset = DailySensorSummary.objects.all()
        time_field = "summary_date"
        limits = [boundary.date() for boundary in boundaries]
        averages = {metric: _weighted_average(metric) for metric in METRICS}
    else:
        queryset = SensorLog.objects.all()
        time_field = "measured_at"
        limits = boundaries
        averages = {metric: Avg(metric) for metric in METRICS}

    # 開始を含み、終了を含まない。区間の境界にある計測は次の区間に入る。
    rows = (
        queryset.filter(
            **{f"{time_field}__gte": limits[0], f"{time_field}__lt": limits[-1]}
        )
        .annotate(
            bucket=Case(
                *(
                    When(**{f"{time_field}__lt": stop}, then=index)
                    for index, stop in enumerate(limits[1:])
                ),
                output_field=IntegerField(),
            )
        )
        .values("device_id", "plant_id", "bucket")
        .annotate(**averages)
        .order_by("device_id", "plant_id", "bucket")
    )

    # 横軸を全グラフで共有できるよう、欠損区間も None で残す。
    bucket_count = len(boundaries) - 1
    by_observation = defaultdict(
        lambda: {metric: [None] * bucket_count for metric in METRICS}
    )
    for row in rows:
        values = by_observation[row["device_id"], row["plant_id"]]
        for metric in METRICS:
            values[metric][row["bucket"]] = row[metric]

    return {
        "boundaries": [boundary.isoformat() for boundary in boundaries],
        "series": [
            {"device_id": device_id, "plant_id": plant_id, **values}
            for (device_id, plant_id), values in by_observation.items()
        ],
    }