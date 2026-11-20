# テスト対象：日別集計サービス
# 確認すること
# - 欠損を含む計測値の集計と、センサーごとの有効件数
# - 再集計時の更新と、対象日にログがない場合の扱い

from datetime import date

from django.test import TestCase
from django.utils import timezone

from dashboard.models import DailySensorSummary, Device, Plant, SensorLog
from dashboard.services.daily_sensor_summary_service import DailySensorSummaryService


class DailySensorSummaryServiceTests(TestCase):

    def setUp(self):
        self.plant = Plant.objects.create(custom_name="集計対象植物")
        self.device = Device.objects.create(
            device_name="aggregation-test-device",
            plant=self.plant,
            measured_at=timezone.make_aware(
                timezone.datetime(2026, 11, 13, 1, 0),
                timezone=timezone.get_current_timezone(),
            ),
            temperature=20.0,
            humidity=50.0,
            moisture=None,
            light=100.0,
        )
        SensorLog.objects.create(
            device=self.device,
            plant=self.plant,
            measured_at=timezone.make_aware(
                timezone.datetime(2026, 11, 13, 2, 0),
                timezone=timezone.get_current_timezone(),
            ),
            temperature=24.0,
            humidity=None,
            moisture=60.0,
            light=200.0,
        )

        summary = DailySensorSummaryService.aggregate_day(
            self.device,
            self.plant,
            self.summary_date,
        )

        self.assertEqual(summary.log_count, 2)

        self.assertAlmostEqual(summary.temperature_avg, 22.0)
        self.assertEqual(summary.temperature_min, 20.0)
        self.assertEqual(summary.temperature_max, 24.0)
        self.assertEqual(summary.temperature_count, 2)

        self.assertEqual(summary.humidity_avg, 50.0)
        self.assertEqual(summary.humidity_count, 1)

        self.assertEqual(summary.moisture_avg, 60.0)
        self.assertEqual(summary.moisture_count, 1)

        self.assertAlmostEqual(summary.light_avg, 150.0)
        self.assertEqual(summary.light_count, 2)

    # ログ追加後に再集計すると、同じ集計レコードの値と件数が更新される。
    def test_recalculating_updates_existing_summary(self):
        SensorLog.objects.create(
            device=self.device,
            plant=self.plant,
            measured_at=timezone.make_aware(
                timezone.datetime(2026, 11, 13, 1, 0),
                timezone=timezone.get_current_timezone(),
            ),
            temperature=20.0,
        )

        first_summary = DailySensorSummaryService.aggregate_day(
            self.device,
            self.plant,
            self.summary_date,
        )

        SensorLog.objects.create(
            device=self.device,
            plant=self.plant,
            measured_at=timezone.make_aware(
                timezone.datetime(2026, 11, 13, 2, 0),
                timezone=timezone.get_current_timezone(),
            ),
            tempeature=24.0,
        )

        second_summary = DailySensorSummaryService.aggregate_day(
            self.device,
            self.plant,
            self.summary_date,
        )

        self.assertEqual(first_summary.pk, second_summary.pk)
        self.assertEqual(DailySensorSummary.objects.count(), 1)
        self.assertAlmostEqual(second_summary.temperature_avg, 22.0)
        self.assertEqual(second_summary.temperature_count, 2)

    # 対象日にログがなければ、集計結果を保存せずに None を返す。
    def test_returns_none_when_day_has_no_logs(self):
        summary = DailySensorSummaryService.aggregate_day(
            self.device,
            self.plant,
            self.summary_date,
        )

        self.assertIsNone(summary)
        self.assertFalse(DailySensorSummary.objects.exists())