# ==========================================
# 日別集計タスク表示コマンド
# ==========================================

# 手動用実行コマンド
# obserleaf_manage daily_sensor_aggregation_status

from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand
from django.db.models import Count, Min, Q
from django.utils import timezone

from dashboard.models import DailySensorAggregationTask


class Command(BaseCommand):
    help = "昨日以前の日別集計タスクの状態と直近のエラーを表示します。"

    def handle(self, *args, **options):
        # 集計実行コマンドと同じ日本時間の境界を使う。
        today = timezone.localdate(timezone=ZoneInfo("Asia/Tokyo"))
        tasks = DailySensorAggregationTask.objects.filter(summary_date__lt=today)
        statuses = DailySensorAggregationTask.Status
        pending = Q(status=statuses.PENDING)

        # 状態別の件数と最も古い未処理日をまとめて取得する。
        summary = tasks.aggregate(
            pending_count=Count("pk", filter=pending),
            failed_count=Count("pk", filter=Q(status=statuses.FAILED)),
            completed_count=Count("pk", filter=Q(status=statuses.COMPLETED)),
            oldest_pending_date=Min("summary_date", filter=pending),
        )
        self.stdout.write(
            f"日別集計タスク（日本時間で昨日以前）: "
            f"未処理 {summary['pending_count']} 件、"
            f"失敗 {summary['failed_count']} 件、"
            f"完了 {summary['completed_count']} 件"
        )
        if summary["oldest_pending_date"] is not None:
            self.stdout.write(f"最も古い未処理日: {summary['oldest_pending_date']}")

        # 現在失敗中のタスクを、最後に施行した順に最大5件表示する。
        failed_tasks = (
            tasks.filter(status=statuses.FAILED)
            .select_related("device", "plant")
            .order_by("-last_attempt_at", "-pk")[:5]
        )
        for task in failed_tasks:
            error = task.last_error or "記録なし"
            self.stdout.write(f"失敗: {task} | エラー: {error}")