# テスト対象：日別集計タスクを処理する管理コマンド
# 確認すること
# - 集計成功時の結果保存とタスクの完了
# - 集計失敗時のエラー記録と、次回実行時の再試行

from datetime import date, datetime, timedelta, timezone as datetime_timezone
from io import StringIO
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


class DailySensorAggregationStatusCommandTests(TestCase):

    # 当日分を除外し、状態別件数・最古の未処理日・直近5件の失敗を表示する。
    def test_reports_past_tasks_and_five_latest_failures(self):
        # UTCでは11月12日、日本時間では11月13日の時点を使う。
        now = datetime(2026, 11, 12, 15, 30, tzinfo=datetime_timezone.utc)
        today = date(2026, 11, 13)
        device = Device.objects.create(device_name="aggregation-status-device")
        status = DailySensorAggregationTask.Status

        for days_ago, task_status in (
            (0, status.PENDING),
            (1, status.PENDING),
            (2, status.COMPLETED),
            (3, status.PENDING),
        ):
            DailySensorAggregationTask.objects.create(
                device=device,
                summary_date=today - timedelta(days=days_ago),
                status=task_status,
            )

        # 集計日と試行日時の順序を変え、試行日時で並ぶことを確認する。
        for days_ago, hours_ago in enumerate((6, 2, 5, 1, 4, 3), start=4):
            DailySensorAggregationTask.objects.create(
                device=device,
                summary_date=today - timedelta(days=days_ago),
                status=status.FAILED,
                last_attempt_at=now - timedelta(hours=hours_ago),
                last_error=f"error-{hours_ago}",
            )

        output = StringIO()
        with patch("django.utils.timezone.now", return_value=now):
            call_command("daily_sensor_aggregation_status", stdout=output)

        lines = output.getvalue().splitlines()
        self.assertIn("未処理 2 件、失敗 6 件、完了 1 件", lines[0])
        self.assertIn("最も古い未処理日: 2026-11-10", lines[1])
        error_lines = [line for line in lines if line.startswith("失敗:")]
        self.assertEqual(
            [line.rsplit("エラー: ", 1)[1] for line in error_lines],
            [f"error-{hours_ago}" for hours_ago in range(1, 6)],
        )