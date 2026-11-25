# テスト対象：センサー推移サービス
# 確認すること
# - 1時間の10分区間、欠損値、有効な計測が1件の場合の実測時刻
# - 長期間表示における日別集計値の加重平均と、日本時間の当日分の除外

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.test import TestCase

from dashboard.models import DailySensorSummary, Device, SensorLog
from dashboard.services.sensor_trend_service import get_sensor_trends


class SensorTrendServiceTests(TestCase):

    def setUp(self):
        self.device = Device.objects.create(device_name="sensor-trend-device")
        self.japan_tz = ZoneInfo("Asia/Tokyo")

    # 1時間分を10分ずつ集計し、欠損区間と単一計測の実測時刻を保持する。
    def test_hourly_buckets_keep_gaps_and_single_measurement_times(self):
        start = datetime(2026, 11, 13, 12, tzinfo=self.japan_tz)

        # 10分・30分ちょうどの計測は次の区間に入り、60分ちょうどの計測は対象外になる。
        for minute, temperature in ((10, 23), (30, 20), (39, 24), (60, 99)):
            SensorLog.objects.create(
                device=self.device,
                measured_at=start + timedelta(minutes=minute),
                temperature=temperature,
            )

        result = get_sensor_trends("1h", now=start + timedelta(hours=1))

        self.assertEqual(
            result["boundaries"],
            [(start + timedelta(minutes=n)).isoformat() for n in range(0, 61, 10)],
        )
        series, = result["series"]
        self.assertEqual(series["device_id"], self.device.pk)
        self.assertEqual(series["temperature"], [None, 23, None, 22, None, None])

        measured_at = start + timedelta(minutes=10)
        times = series["measurement_times"]["temperature"]

        # UTCと日本時間のように表記が異なる場合も、同じ時点がどうかを比較する。
        self.assertEqual(datetime.fromisoformat(times[1]), measured_at)
        self.assertEqual(times[:1] + times[2:], [None] * 5)
        self.assertEqual(series["humidity"], [None] * 6)

    # 長期間表示では日平均を有効件数で重み付けし、日本時間の当日分を除外する。
    def test_yearly_buckets_weight_daily_summary_by_valid_count(self):
        now = datetime(2026, 11, 13, 12, tzinfo=self.japan_tz)
        for days_ago, average, count in ((2, 10, 1), (1, 30, 3), (0, 99, 10)):
            DailySensorSummary.objects.create(
                device=self.device,
                summary_date=now.date() - timedelta(days=days_ago),
                temperature_avg=average,
                temperature_count=count,
            )

        result = get_sensor_trends("1y", now=now)

        series, = result["series"]

        # 前日までの2日分から (10 × 1 + 30 × 3) ÷ 4 = 25 を求める。
        self.assertEqual(series["temperature"], [None] * 11 + [25])
        self.assertEqual(series["humidity"], [None] * 12)