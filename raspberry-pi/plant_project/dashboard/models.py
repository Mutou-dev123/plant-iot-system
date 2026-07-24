from django.db import models
from django.utils import timezone


# ==============================
# 1. 植物マスタ (PlantMaster)
# ==============================
# システムに登録されている植物の図鑑データ。ユーザーが追加することも可能。
# 植物ごとに適切な温度や湿度の情報を記録する
class PlantMaster(models.Model):

    # 【基本情報】
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="植物名"
    )
    description = models.TextField(
        blank=True,
        verbose_name="植物説明"
    )

    # 【適正温度】
    optimal_temperature_min = models.FloatField(
        null=True,
        blank=True,
        verbose_name="適正温度（下限 ℃）"
    )

    optimal_temperature_max = models.FloatField(
        null=True,
        blank=True,
        verbose_name="適正温度（上限 ℃）"
    )

    # 【適正湿度】
    optimal_humidity_min = models.FloatField(
        null=True,
        blank=True,
        verbose_name="適正湿度（下限 %）"
    )

    optimal_humidity_max = models.FloatField(
        null=True,
        blank=True,
        verbose_name="適正湿度（上限 %）"
    )

    # 【適正土壌水分】
    optimal_moisture_min = models.FloatField(
        null=True,
        blank=True,
        verbose_name="適正土壌水分（下限 %）"
    )

    optimal_moisture_max = models.FloatField(
        null=True,
        blank=True,
        verbose_name="適正土壌水分（上限 %）"
    )

    # 【適正光量】
    optimal_light_min = models.FloatField(
        null=True,
        blank=True,
        verbose_name="適正光量スコア（下限）"
    )

    optimal_light_max = models.FloatField(
        null=True,
        blank=True,
        verbose_name="適正光量スコア（上限）"
    )

    # 【必要光量】
    target_light_score = models.FloatField(
        default=30000.0,
        verbose_name="目標日照スコア（1日）"
    )

    class Meta:
        db_table = "plant_master"
        verbose_name = "植物マスタ"
        verbose_name_plural = "植物マスタ"

    # ※1 verbose_nameを設定すると、管理者画面やエラーメッセージなどで
    #     指定した文字列で表示が可能になる。

    # ※2 verbose_name_pluralは英語圏などでの複数形を指す。
    #     日本語なので、単数と統一

    def __str__(self):
        return self.name
    

# ==============================
# 2. 育成植物 (Plant)
# ==============================
# ユーザーが実際に育てている植物
class Plant(models.Model):

    # 【植物マスタ】
    plant_master = models.ForeignKey(
        PlantMaster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="植物種類"
    )

    # 【ユーザーがつけた名前】
    custom_name = models.CharField(
        max_length=100,
        default="新しい植物",
        verbose_name="植物名"
    )

    # 【栽培開始日】
    start_date = models.DateField(
        default=timezone.now,
        verbose_name="栽培開始日"
    )

    class Meta:
        db_table = "plant"
        verbose_name = "育成植物"
        verbose_name_plural = "育成植物"

    def __str__(self):
        return self.custom_name
    

# ==============================
# 3. デバイス設定 (Device)
# ==============================
# ESP32を一機ごとの設定を管理する。
class Device(models.Model):

    # 【接続先植物（未登録可）】
    plant = models.ForeignKey(
        Plant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
        verbose_name="観測対象の植物"
    )

    # ※ related_nameをつけると、
    #    plant.device_set.all()をplant.devices.all()のように書ける。

    # 【ESPの識別名】
    device_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="デバイス名"
    )

    # 【ESPの一意な識別ID】
    device_uuid = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="デバイスUUID"
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

    class Meta:
        db_table = "device"
        verbose_name = "デバイス"
        verbose_name_plural = "デバイス"

    def __str__(self):
        return self.device_name
    

# ==============================
# 4. センサーログ (SensorLog)
# ==============================
# 毎回の計測データ。植物ではなく「どのデバイスが測ったか」に紐づける。
class SensorLog(models.Model):

    # 【測定デバイス】
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        verbose_name="測定デバイス"
    )

    # 【ESP32で計測した日時】
    measured_at = models.DateTimeField(
        verbose_name="計測日時"
    )

    # 【Raspberry Piで受信した日時】
    received_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="受信日時"
    )

    # 【土壌水分生データ】
    soil_raw = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="土壌水分(生)"
    )

    # 【光量生データ】
    light_raw = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="光量(生)"
    )

    # 【土壌水分】
    moisture = models.FloatField(
        null=True,
        blank=True,
        verbose_name="土壌水分(%)"
    )

    # 【光量スコア】
    light = models.FloatField(
        null=True,
        blank=True,
        verbose_name="光量スコア"
    )

    # 【温度】
    temperature= models.FloatField(
        null=True,
        blank=True,
        verbose_name="温度(℃)"
    )

    # 【湿度】
    humidity = models.FloatField(
        null=True,
        blank=True,
        verbose_name="湿度(%)"
    )

    class Meta:
        db_table = "sensor_logs"
        ordering = ["-measured_at"]
        verbose_name="センサーログ"
        verbose_name_plural="センサーログ"

    def __str__(self):
        return (
            f"{self.device.device_name}"
            f" - {self.measured_at.strftime('%Y-%m-%d %H:%M')}"
        )