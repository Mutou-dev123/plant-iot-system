# ==========================================
# 管理者用画面（Device）
# ==========================================

from urllib.parse import urlencode

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .base import DescriptiveModelAdmin
from ..models import Device


# デバイス情報と設定の管理画面を設定する
@admin.register(Device)
class DeviceAdmin(DescriptiveModelAdmin):
    changelist_description = (
        "ESP32デバイスの状態と設定を管理します。"
        "設定項目を変更すると、設定バージョンが更新されます。"
    )

    list_display = (
        "device_name",
        "mac_address",
        "plant",
        "communication_status_display",
        "sensor_log_link",
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
        "reported_dht_enabled_display",
        "reported_soil_enabled_display",
        "reported_light_enabled_display",
        "config_version",
        "applied_config_version",
        "last_seen_at",
        "communication_status",
        "sensor_log_link",
    )

    fieldsets = (
        ("基本情報", {
            "fields": (
                "device_name",
                "plant",
                "device_uuid",
                "mac_address",
                "sensor_log_link",
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
                "reported_dht_enabled_display",
                "reported_soil_enabled_display",
                "reported_light_enabled_display",
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

    # 通信状態の見出しを日本語にする
    @admin.display(description="通信状態")
    def communication_status_display(self, obj):
        return obj.communication_status

    # ESP32から報告されたセンサー状態を日本語で表示する
    @admin.display(description="温湿度センサー状態", boolean=True)
    def reported_dht_enabled_display(self, obj):
        return obj.reported_dht_enabled

    @admin.display(description="土壌水分センサー状態", boolean=True)
    def reported_soil_enabled_display(self, obj):
        return obj.reported_soil_enabled

    @admin.display(description="光量センサー状態", boolean=True)
    def reported_light_enabled_display(self, obj):
        return obj.reported_light_enabled

    # 一覧から、このDeviceの計測ログへ移動できるようにする
    @admin.display(description="計測ログ")
    def sensor_log_link(self, obj):
        url = reverse("admin:dashboard_sensorlog_changelist")
        query = urlencode({"device__id__exact": obj.pk})
        return format_html('<a href="{}?{}">ログを見る</a>', url, query)

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