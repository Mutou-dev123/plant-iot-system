# テスト対象：日別集計結果と日別集計タスクのモデル
# 確認すること
# - 日別レコードの重複制約と、参照先の削除保護
# - 新しい集計タスクの初期状態

from datetime import date, timedelta
from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.utils import timezone

from dashboard.models import (
    DailySensorAggregationTask,
    DailySensorSummary,
    Device,
    Plant,
)


class DailySensorSummaryModelTests(TestCase):

    def setUp(self):
        self.plant = Plant.objects.create(custom_name="集計テスト植物")
        self.device = Device.objects.create(
            device_name="summary-test-device",
            plant=self.plant,
        )
        self.summary_date = date(2026, 11, 13)

    def _create_summary(self, **kwargs):
        return DailySensorSummary.objects.create(
            device=self.device,
            summary_date=self.summary_date,
            **kwargs,
        )

    # 同じデバイス・植物・日付の集計結果を2件作ると、重複エラーになる。
    def test_prevents_duplicate_summary_for_same_device_plant_and_date(self):
        self._create_summary(plant=self.plant)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._create_summary(plant=self.plant)

    # 植物が未割当でも、同じデバイス・日付の集計結果は1件に制限される。
    def test_prevents_duplicate_unassigned_summary_for_same_device_and_date(self):
        self._create_summary()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._create_summary()

    # 同じ日付の植物未割当の集計結果でも、デバイスが異なれば保存できる。
    def test_allows_unassigned_summaries_for_different_devices(self):
        self._create_summary()

        other_device = Device.objects.create(
            device_name="another-summary-device",
        )

        DailySensorSummary.objects.create(
            device=other_device,
            summary_date=self.summary_date,
        )

        self.assertEqual(DailySensorSummary.objects.count(), 2)

    # 集計結果が参照しているデバイスと植物は、どちらも削除が拒否される。
    def test_protects_device_and_plant_with_summary_from_delection(self):
        self._create_summary(plant=self.plant)

        with self.assertRaises(ProtectedError):
            self.device.delete()

        with self.assertRaises(ProtectedError):
            self.plant.delete()


class DailySensorAggregationTaskModelTests(TestCase):

    def setUp(self):
        self.plant = Plant.objects.create(
            custom_name="集計タスク用植物",
        )
        self.device = Device.objects.create(
            device_name="aggregation-task-test-device",
            plant=self.plant,
        )
        self.summary_date = date(2026, 11, 16)

    def _create_task(self, **kwargs):
        return DailySensorAggregationTask.objects.create(
            device=self.device,
            summary_date=self.summary_date,
            **kwargs,
        )

    # 作成直後のタスクは未処理で、試行回数は0、試行日時とエラーは空になる。
    def test_new_task_starts_as_pending(self):
        task = self._create_task(plant=self.plant)

        self.assertEqual(
            task.status,
            DailySensorAggregationTask.Status.PENDING,
        )
        self.assertEqual(task.attempt_count, 0)
        self.assertIsNone(task.last_attempt_at)
        self.assertEqual(task.last_error, "")

    # 同じデバイス・植物・日付の集計タスクを2件作ると、重複エラーになる。
    def test_prevents_duplicate_task_for_same_device_plant_and_date(self):
        self._create_task(plant=self.plant)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._create_task(plant=self.plant)

    # 植物が未割当でも、同じデバイス・日付の集計タスクは1件に制限される。
    def test_prevents_duplicate_unassigned_task_for_same_device_and_date(self):
        self._create_task()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._create_task()

    # 同じ日付の植物未割当のタスクでも、デバイスが異なれば保存できる。
    def test_allows_unassigned_tasks_for_different_devices(self):
        self._create_task()

        another_device = Device.objects.create(
            device_name="another-aggregation-task-device",
        )
        DailySensorAggregationTask.objects.create(
            device=another_device,
            summary_date=self.summary_date,
        )

        self.assertEqual(
            DailySensorAggregationTask.objects.count(),
            2,
        )

    # 集計タスクが参照しているデバイスと植物は、どちらも削除が拒否される。
    def test_protects_device_and_plant_with_task_from_deletion(self):
        self._create_task(plant=self.plant)

        with self.assertRaises(ProtectedError):
            self.device.delete()

        with self.assertRaises(ProtectedError):
            self.plant.delete()


class DeviceCommunicationStatusTests(TestCase):

    def setUp(self):
        self.device = Device.objects.create(
            device_name="communication-status-device",
        )
        self.now = timezone.now()

    # 最終通信日時が未設定のデバイスは「未通信」と判定される。
    def test_returns_not_communicated_when_last_seen_is_missing(self):
        self.device.last_seen_at = None

        self.assertEqual(
            self.device.communication_status,
            "未通信",
        )

    # 判定時間と同じ経過時間なら「通信確認済み」と判定される。
    def test_returns_communicated_at_timeout_boundary(self):
        self.device.interval_seconds = 30
        self.device.last_seen_at = self.now - timedelta(seconds=60)

        with patch("dashboard.models.device.timezone.now", return_value=self.now):
            self.assertEqual(
                self.device.communication_status,
                "通信確認済み",
            )

    # 判定時間を1秒経過すると「通信未確認」と判定される。
    def test_returns_not_communicated_after_timeout(self):
        self.device.interval_seconds = 30
        self.device.last_seen_at = self.now - timedelta(seconds=61)

        with patch("dashboard.models.device.timezone.now", return_value=self.now):
            self.assertEqual(
                self.device.communication_status,
                "通信未確認",
            )

    # 計測間隔が短い場合も、判定時間には最低60秒が適用される。
    def test_uses_minimum_timeout_of_sixty_seconds(self):
        self.device.interval_seconds = 10
        self.device.last_seen_at = self.now - timedelta(seconds=60)

        with patch("dashboard.models.device.timezone.now", return_value=self.now):
            self.assertEqual(
                self.device.communication_status,
                "通信確認済み",
            )