# 管理画面

from django.contrib import admin
from django.core.exceptions import ValidationError

from.models import (
    PlantMaster,
    Plant,
    Device,
    SensorLog
)

# ==============================
# 1. 植物マスタ (PlantMaster)
# ==============================
@admin.register(PlantMaster)
class PlantMasterAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "temperature_range",
        "humidity_range",
        "moisture_range",
        "light_range",
        "target_light_score",
    )

    search_fields = ("name",)
    ordering = ("name",)

    fieldsets = (
        ("🌱 基本情報", {
            "fields": (
                "name",
                "description",
            ),
        }),

        ("🌡️ 適正温度", {
            "fields": (
                ("optimal_temperature_max", "optimal_temperature_min"),
            ),
        }),

        ("💧 適正湿度", {
            "fields": (
                ("optimal_humidity_max", "optimal_humidity_min"),
            ),
        }),

        ("🌿 適正土壌水分", {
            "fields": (
                ("optimal_moisture_max", "optimal_moisture_min"),
            ),
        }),

        ("☀️ 光量", {
            "fields": (
                ("optimal_light_max", "optimal_light_min"),
                "target_light_score",
            ),
        }),
    )

    # ------------------------
    # 一覧表示用
    # ------------------------
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


@admin.register(SensorLog)
class SensorLogAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "device",
        "measured_at",
        "received_at",
        "temperature",
        "humidity",
        "moisture",
        "light",
    )

    ordering = ("-measured_at",)

admin.site.register(Plant)
admin.site.register(Device)