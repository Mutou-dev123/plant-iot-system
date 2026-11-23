# ==========================================
# 管理者用画面（Device）
# ==========================================

from django.contrib import admin
from ..models import Device


# デバイス情報と設定の管理画面を設定する
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "device_name",
        "mac_address",
        "plant",
        "communication_status_display",
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
        ("希望設定（Raspberry Pi 側）", {
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

    # Device専用の削除確認画面を使う
    delete_confirmation_template = (
        "admin/dashboard/device/delete_confirmation.html"
    )

    def delete_view(self, request, object_id, extra_context=None):
        # 関連するセンサーログも削除されることを確認画面に伝える
        context = {
            **(extra_context or {}),
            "sensor_log_delete_warning": (
                "このデバイスを削除すると、関連するセンサーログも削除されます。"
            ),
        }
        return super().delete_view(
            request,
            object_id,
            extra_context=context,
        )

    @admin.display(description="通信状態")
    def communication_status_display(self, obj):
        return obj.communication_status

    def save_model(self, request, obj, form, change):

        # 設定項目が変わった場合だけ設定バージョンを加算する
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