# テスト対象：日別集計タスクを処理する管理コマンド
# 確認すること
# - 集計成功時の結果保存とタスクの完了
# - 集計失敗時のエラー記録と、次回実行時の再試行

from datetime import date
from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.db import OperationalError
from django.test import TestCase
from django.utils import timezone

from dashboard.models import (
    DailySensorAggregationTask,
    DailySensorSummary,
    Device,
    Plant,
    SensorLog,
)


class ProcessDailySensorAggregationTasksCommandTests(TestCase):

    def setUp(self):
        self.plant = Plant.objects.create(custom_name="コマンドテスト植物")
        self.device = Device.objects.create(
            device_name="command-test_device",
            plant=self.plant,
        )
        self.summary_date = date(2026, 11, 13)

        measured_at = timezone.make_aware(
            timezone.datetime(2026, 11, 13, 12, 0),
            timezone=timezone.get_current_timezone(),
        )
        SensorLog.objects.create(
            device=self.device,
            plant=self.plant,
            measured_at=measured_at,
            temperature=22.0,
        )
        self.task = DailySensorAggregationTask.objects.create(
            device=self.device,
            plant=self.plant,
            summary_date=self.summary_date,
        )

    # 集計に成功すると、結果を保存し、試行回数と日時を記録してタスクを完了する。
    def test_command_aggregates_and_marks_task_completed(self):
        call_command("process_daily_sensor_aggregation_tasks")

        self.task.refresh_from_db()
        summary = DailySensorSummary.objects.get(
            device=self.device,
            plant=self.plant,
            summary_date=self.summary_date,
        )

        self.assertEqual(
            self.task.status,
            DailySensorAggregationTask.Status.COMPLETED,
        )
        self.assertEqual(self.task.attempt_count, 1)
        self.assertIsNotNone(self.task.last_attempt_at)
        self.assertEqual(self.task.last_error, "")
        self.assertEqual(summary.temperature_avg, 22.0)

    # 一時的なDBエラーを記録し、次回の実行で同じタスクを再試行して完了する。
    def test_failed_task_is_recorded_and_retried_on_next_run(self):
        command_path = (
            "dashboard.management.commands."
            "process_daily_sensor_aggregation_tasks."
            "DailySensorSummaryService.aggregate_day"
        )

        with patch(command_path, side_effect=OperationalError("DB一時エラー")):
            with self.assertRaises(CommandError):
                call_command("process_daily_sensor_aggregation_tasks")

        self.task.refresh_from_db()
        self.assertEqual(
            self.task.status,
            DailySensorAggregationTask.Status.FAILED,
        )
        self.assertEqual(self.task.attempt_count, 1)
        self.assertIn("DB一時エラー", self.task.last_error)

        call_command("process_daily_sensor_aggregation_tasks")

        self.task.refresh_from_db()
        self.assertEqual(
            self.task.status,
            DailySensorAggregationTask.Status.COMPLETED,
        )
        self.assertEqual(self.task.attempt_count, 2)
        self.assertEqual(self.task.last_error, "")