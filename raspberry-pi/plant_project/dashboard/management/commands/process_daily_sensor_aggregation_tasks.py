# ==========================================
# 日別集計管理コマンド
# ==========================================

# 手動用実行コマンド
# python manage.py process_daily_sensor_aggregation_tasks

import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError
from django.utils import timezone

from dashboard.models import DailySensorAggregationTask
from dashboard.services.daily_sensor_summary_service import (
    DailySensorSummaryService,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "未処理・失敗状態の日別集計タスクを実行します。"

    def handle(self, *args, **options):
        tasks = list(
            DailySensorAggregationTask.objects
            .filter(
                status__in=[
                    DailySensorAggregationTask.Status.PENDING,
                    DailySensorAggregationTask.Status.FAILED,
                ]
            )
            .select_related("device", "plant")
            .order_by("summary_date", "device_id", "plant_id")
        )

        succeeded = 0
        failed = 0

        for task in tasks:
            task.attempt_count += 1
            task.last_attempt_at = timezone.now()
            task.save(
                update_fields=[
                    "attempt_count",
                    "last_attempt_at",
                    "updated_at",
                ]
            )

            try:
                DailySensorSummaryService.aggregate_day(
                    task.device,
                    task.plant,
                    task.summary_date,
                )
            except DatabaseError as error:
                task.status = DailySensorAggregationTask.Status.FAILED
                task.last_error = str(error) or error.__class__.__name__
                task.save(update_fields=["status", "last_error", "updated_at"])

                logger.exception(
                    "日別集計に失敗しました: task_id=%s",
                    task.pk,
                )
                self.stderr.write(
                    self.style.ERROR(
                        f"タスク {task.pk} の集計に失敗しました: {task.last_error}"
                    )
                )
                failed += 1
                continue

            task.status = DailySensorAggregationTask.Status.COMPLETED
            task.last_error = ""
            task.save(update_fields=["status", "last_error", "updated_at"])
            succeeded += 1

        self.stdout.write(
            f"日別集計タスク: 成功 {succeeded} 件、失敗 {failed} 件"
        )

        if failed:
            raise CommandError(
                f"{failed} 件の集計に失敗しました。次回実行時に再試行されます。"
            )