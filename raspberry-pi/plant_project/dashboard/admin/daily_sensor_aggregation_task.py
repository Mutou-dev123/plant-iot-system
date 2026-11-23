# ==========================================
# 管理者用画面（DailySensorAggregationTask）
# ==========================================

from django.contrib import admin
from .base import DescriptiveModelAdmin
from ..models import DailySensorAggregationTask


# 日別集計タスクの状態を確認する管理画面
@admin.register(DailySensorAggregationTask)
class DailySensorAggregationTaskAdmin(DescriptiveModelAdmin):
    changelist_description = (
        "未処理・失敗など集計処理の状態を管理します。"
    )

    list_display = (
        "summary_date",
        "device",
        "plant",
        "status",
        "attempt_count",
        "last_attempt_at",
        "updated_at",
    )
    list_filter = ("status", "device")
    search_fields = ("device__device_name", "plant__custom_name")
    date_hierarchy = "summary_date"
    list_select_related = ("device", "plant")
    ordering = ("-summary_date", "device__device_name")

    # タスクはセンサー受信処理と管理コマンドが扱うため、画面からは変更しない
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False