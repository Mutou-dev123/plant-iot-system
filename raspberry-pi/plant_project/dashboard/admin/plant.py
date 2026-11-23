# ==========================================
# 管理者用画面（Plant）
# ==========================================

from django.contrib import admin
from dashboard.models import Plant
from .base import DescriptiveModelAdmin


# 育成植物の一覧と検索・絞り込み設定をする
@admin.register(Plant)
class PlantAdmin(DescriptiveModelAdmin):
    changelist_description = (
        "育成植物を管理します。"
        "アーカイブ済みの植物も確認できます。"
    )

    list_display = (
        "custom_name",
        "plant_master",
        "start_date",
        "is_archived",
    )
    search_fields = (
        "custom_name",
        "plant_master__name",
    )
    list_filter = (
        "is_archived",
        "plant_master",
    )
    list_select_related = ("plant_master",)
    ordering = ("custom_name",)