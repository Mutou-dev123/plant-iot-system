# ==========================================
# 管理者用画面（SensorLog）
# ==========================================

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .base import DescriptiveModelAdmin
from ..models import SensorLog


# 計測ログを参照・絞り込みするための管理画面設定
@admin.register(SensorLog)
class SensorLogAdmin(DescriptiveModelAdmin):
    changelist_description = (
        "保存されたセンサー計測ログを閲覧できます。"
        "追加・編集・削除はできません。"
    )

    list_display = (
        "id",
        "device_link",
        "plant",
        "measured_at",
        "received_at",
        "temperature",
        "humidity",
        "moisture",
        "light",
    )

    # デバイス名や植物名でログを検索できるようにする
    search_fields = (
        "device__device_name",
        "plant__custom_name",
    )

    # デバイスで絞り込み、日付階層で計測日をたどれるようにする
    list_filter = ("device",)
    date_hierarchy = "measured_at"

    # 関連先を一覧表示時にまとめて読み込む
    list_select_related = ("device", "plant")

    # 新しい計測データを新しい順に表示する
    ordering = ("-measured_at",)

    # ログの追加・変更・削除を管理画面からできないようにする
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # デバイス名から、そのデバイスの管理画面詳細へ移動する
    @admin.display(description="測定デバイス")
    def device_link(self, obj):
        url = reverse(
            "admin:dashboard_device_change",
            args=[obj.device_id],
        )
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.device.device_name,
        )