# ==========================================
# 管理者用画面（DailySensorSummary）
# ==========================================

from django.contrib import admin
from .base import DescriptiveModelAdmin
from ..models import DailySensorSummary


# 日別集計の一覧と平均値を設定する
@admin.register(DailySensorSummary)
class DailySensorSummaryAdmin(DescriptiveModelAdmin):
    changelist_description = (
        "センサー計測ログから自動生成される集計結果です。"
    )

    list_display = (
        "summary_date",
        "device",
        "plant",
        "log_count",
        "temperature_avg_display",
        "humidity_avg_display",
        "moisture_avg_display",
        "light_avg_display",
        "updated_at",
    )
    list_filter = ("summary_date", "device", "plant")
    search_fields = ("device__device_name", "plant__custom_name")
    date_hierarchy = "summary_date"
    list_select_related = ("device", "plant")
    ordering = ("-summary_date", "device__device_name")

    # 値が未計測の場合も一覧で判別できるようにする
    @admin.display(description="気温平均")
    def temperature_avg_display(self, obj):
        return "—" if obj.temperature_avg is None else f"{obj.temperature_avg:.1f}"

    @admin.display(description="湿度平均")
    def humidity_avg_display(self, obj):
        return "—" if obj.humidity_avg is None else f"{obj.humidity_avg:.1f}"

    @admin.display(description="土壌水分平均")
    def moisture_avg_display(self, obj):
        return "—" if obj.moisture_avg is None else f"{obj.moisture_avg:.1f}"

    @admin.display(description="光量平均")
    def light_avg_display(self, obj):
        return "—" if obj.light_avg is None else f"{obj.light_avg:.1f}"

    # 集計結果を管理画面から追加・変更・削除できないようにする
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False