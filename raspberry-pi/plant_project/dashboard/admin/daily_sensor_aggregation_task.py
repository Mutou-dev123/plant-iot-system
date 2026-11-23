# ==========================================
# 管理者用画面（DailySensorAggregationTask）
# ==========================================

from urllib.parse import urlencode

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
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
        "status_badge",
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

    # 処理状態を文字と色で表示する
    @admin.display(description="処理状態")
    def status_badge(self, obj):
        colors = {
            "pending": "#9a6700",
            "failed": "#b42318",
            "completed": "#067647",
        }
        color = colors.get(obj.status, "#555555")

        # 状態名も文字で表示し、色だけに頼らない
        return format_html(
            '<strong style="color: {};">{}</strong>',
            color,
            obj.get_status_display(),
        )

    # 失敗タスクに絞った一覧へのリンクをテンプレートに渡す
    def changelist_view(self, request, extra_context=None):
        failed_tasks_url = reverse(
            "admin:dashboard_dailysensoraggregationtask_changelist"
        )
        failed_tasks_url += "?" + urlencode({"status__exact": "failed"})

        context = {
            **(extra_context or {}),
            "failed_tasks_url": failed_tasks_url,
        }
        return super().changelist_view(request, extra_context=context)