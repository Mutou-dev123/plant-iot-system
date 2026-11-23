# ==========================================
# 管理者用画面（PlantMaster）
# ==========================================

from django.contrib import admin
from django.db.models import Q
from .base import DescriptiveModelAdmin
from ..models import PlantMaster


class RangeSetupFilter(admin.SimpleListFilter):
    # 管理画面のフィルタ欄に表示する名前
    title = "適正範囲の設定状況"
    parameter_name = "range_setup"

    # 判定対象になる4種類の適正範囲の上下限
    range_fields = (
        "optimal_temperature_min",
        "optimal_temperature_max",
        "optimal_humidity_min",
        "optimal_humidity_max",
        "optimal_moisture_min",
        "optimal_moisture_max",
        "optimal_light_min",
        "optimal_light_max",
    )

    def lookups(self, request, model_admin):
        # フィルタ欄の選択肢を返す
        return (
            ("complete", "すべて設定済み"),
            ("partial", "一部設定"),
            ("none", "未設定"),
        )

    def queryset(self, request, queryset):
        # 各上下限に値が入っている条件と、未入力の条件を作る
        all_filled = Q()
        any_filled = Q()
        all_empty = Q()

        for field in self.range_fields:
            all_filled &= Q(**{f"{field}__isnull": False})
            any_filled |= Q(**{f"{field}__isnull": False})
            all_empty &= Q(**{f"{field}__isnull": True})

        # 8項目すべてに値がある植物だけを表示する
        if self.value() == "complete":
            return queryset.filter(all_filled)

        # 値が一つ以上あり、8項目すべては埋まっていない植物を表示する
        if self.value() == "partial":
            return queryset.filter(any_filled).exclude(all_filled)

        # 8項目すべてが未入力の植物だけを表示する
        if self.value() == "none":
            return queryset.filter(all_empty)

        # フィルタが選択されていない場合は一覧をそのまま返す
        return queryset


# 植物マスタの一覧と編集画面を設定する
@admin.register(PlantMaster)
class PlantMasterAdmin(DescriptiveModelAdmin):
    changelist_description = (
        "植物のしきい値を管理します。"
        "しきい値の設定状況で絞り込むことが可能です。"
    )

    list_display = (
        "name",
        "temperature_range",
        "humidity_range",
        "moisture_range",
        "light_range",
        "target_light_score",
    )
    search_fields = ("name",)

    # 適正範囲の入力状況で一覧を絞り込む
    list_filter = (RangeSetupFilter,)

    ordering = ("name",)

    fieldsets = (
        ("🌱 基本情報", {
            "fields": ("name", "description"),
        }),
        ("🌡️ 適正温度", {
            "fields": (("optimal_temperature_max", "optimal_temperature_min"),),
        }),
        ("💧 適正湿度", {
            "fields": (("optimal_humidity_max", "optimal_humidity_min"),),
        }),
        ("🌿 適正土壌水分", {
            "fields": (("optimal_moisture_max", "optimal_moisture_min"),),
        }),
        ("☀️ 光量", {
            "fields": (
                ("optimal_light_max", "optimal_light_min"),
                "target_light_score",
            ),
        }),
    )

    # 一覧で適性範囲を読みやすく表示する
    @admin.display(description="🌡️ 温度 (℃)")
    def temperature_range(self, obj):
        if obj.optimal_temperature_min is None or obj.optimal_temperature_max is None:
            return "―"
        return f"{obj.optimal_temperature_min} ～ {obj.optimal_temperature_max}"

    @admin.display(description="💧 湿度 (%)")
    def humidity_range(self, obj):
        if obj.optimal_humidity_min is None or obj.optimal_humidity_max is None:
            return "―"
        return f"{obj.optimal_humidity_min} ～ {obj.optimal_humidity_max}"

    @admin.display(description="🌿 土壌水分 (%)")
    def moisture_range(self, obj):
        if obj.optimal_moisture_min is None or obj.optimal_moisture_max is None:
            return "―"
        return f"{obj.optimal_moisture_min} ～ {obj.optimal_moisture_max}"

    @admin.display(description="☀️ 光量")
    def light_range(self, obj):
        if obj.optimal_light_min is None or obj.optimal_light_max is None:
            return "―"
        return f"{obj.optimal_light_min} ～ {obj.optimal_light_max}"