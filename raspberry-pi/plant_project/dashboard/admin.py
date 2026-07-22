# 管理画面

from django.contrib import admin

from.models import (
    PlantMaster,
    MyPlant,
    Device,
    SensorLog
)

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

admin.site.register(PlantMaster)
admin.site.register(MyPlant)
admin.site.register(Device)