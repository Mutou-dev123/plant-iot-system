from django.db import models
from django.utils import timezone
import uuid

# ==============================
# 3. デバイス設定 (Device)
# ==============================
# ESP32を一機ごとの設定を管理する。
class Device(models.Model):

    # 【接続先植物（未登録可）】
    plant = models.ForeignKey(
        "dashboard.Plant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
        verbose_name="観測対象の植物"
    )

    # ※ related_nameをつけると、
    #    plant.device_set.all()をplant.devices.all()のように書ける。

    # 【ESP32の識別名】
    device_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="デバイス名"
    )

    # 【ESP32の一意な識別ID】
    device_uuid = models.CharField(
        max_length=100,
        unique=True,
        default=uuid.uuid4,
        verbose_name="デバイスUUID"
    )

    # 【ESP32の物理識別子】
    mac_address = models.CharField(
        max_length=17,
        unique=True,
        null=True,
        blank=True,
        verbose_name="MACアドレス"
    )

    # 【最後にESP32から受信した情報】
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IPアドレス"
    )
    firmware_version = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="ファームウェアバージョン"
    )

    # 【SSID】
    wifi_ssid = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Wi-Fi SSID"
    )

    # 【計測間隔】
    interval_seconds = models.PositiveIntegerField(
        default=300,
        verbose_name="計測間隔（秒）"
    )

    # ESP32が報告したセンサー状態
    # nullは「未報告」を表す
    reported_dht_enabled = models.BooleanField(null=True, blank=True)
    reported_soil_enabled = models.BooleanField(null=True, blank=True)
    reported_light_enabled = models.BooleanField(null=True, blank=True)

    # Raspberry Pi側がESP32に適用させたいセンサー設定
    desired_dht_enabled = models.BooleanField(
        default=True,
        verbose_name="温湿度センサー有効"
    )
    desired_soil_enabled = models.BooleanField(
        default=True,
        verbose_name="土壌水分センサー有効"
    )
    desired_light_enabled = models.BooleanField(
        default=True,
        verbose_name="光センサー有効"
    )

    # 設定を変更するために更新する版番号
    config_version = models.PositiveIntegerField(
        default=1,
        verbose_name="設定バージョン",
    )

    # ESP32から最後に報告された適用済み設定の版番号
    # nullは「まだ適用報告を受けていない」
    applied_config_version = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="適用済み設定バージョン"
    )

    # 【最終通信日時】
    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="最終通信日時"
    )

    class Meta:
        db_table = "device"
        verbose_name = "デバイス"
        verbose_name_plural = "デバイス"

    # 【通信状況】
    @property
    def communication_status(self):
        
        """ 最終通信日時と計測間隔から通信状態を判定する """

        # 一度も通信していない
        if self.last_seen_at is None:
            return "未通信"

        # 判定時間：計測間隔の3倍
        timeout_seconds = max(self.interval_seconds * 3, 60)

        # 最終通信からの経過時間
        elapsed = (timezone.now() - self.last_seen_at).total_seconds()

        if elapsed <= timeout_seconds:
            return "通信確認済み"

        return "通信未確認"

    def __str__(self):
        return self.device_name
