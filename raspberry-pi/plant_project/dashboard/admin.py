# 管理画面

from django.contrib import admin
from.models import PlantMaster, Plant, Device, SensorLog

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

# ==============================
# 2. デバイス (Device)
# ==============================
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):

    list_display = (
        "device_name",
        "mac_address",
        "plant",
        "communication_status",
        "interval_seconds",
        "desired_dht_enabled",
        "desired_soil_enabled",
        "desired_light_enabled",
        "config_version",
        "applied_config_version",
        "last_seen_at",
    )

    search_fields = (
        "device_name",
        "mac_address",
        "ip_address",
    )

    list_filter = (
        "plant",
        "desired_dht_enabled",
        "desired_soil_enabled",
        "desired_light_enabled",
    )

    ordering = ("device_name",)
    list_select_related = ("plant",)

    readonly_fields = (
        "device_uuid",
        "mac_address",
        "ip_address",
        "firmware_version",
        "reported_dht_enabled",
        "reported_soil_enabled",
        "reported_light_enabled",
        "config_version",
        "applied_config_version",
        "last_seen_at",
        "communication_status",
    )

    fieldsets = (
        ("基本情報", {
            "fields": (
                "device_name",
                "plant",
                "device_uuid",
                "mac_address",
            ),
        }),
        ("ネットワーク・ファームウェア", {
            "fields": (
                "ip_address",
                "wifi_ssid",
                "firmware_version",
            ),
        }),
        ("希望設定（Raspberry Pi側）", {
            "fields": (
                "interval_seconds",
                "desired_dht_enabled",
                "desired_soil_enabled",
                "desired_light_enabled",
            ),
        }),
        ("ESP32からの報告・通信状態", {
            "fields": (
                "reported_dht_enabled",
                "reported_soil_enabled",
                "reported_light_enabled",
                "config_version",
                "applied_config_version",
                "communication_status",
                "last_seen_at",
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        config_fields = {
            "interval_seconds",
            "desired_dht_enabled",
            "desired_soil_enabled",
            "desired_light_enabled",
        }

        if change:
            previous_version = (
                Device.objects
                .only("config_version")
                .get(pk=obj.pk)
                .config_version
            )

            config_changed = bool(
                config_fields.intersection(form.changed_data)
            )

            obj.config_version = (
                previous_version + 1
                if config_changed
                else previous_version
            )

        super().save_model(request, obj, form, change)