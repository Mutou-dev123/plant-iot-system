from django.db import models
from django.utils import timezone

# ==============================
# 4. センサーログ (SensorLog)
# ==============================
# 毎回の計測データ。植物ではなく「どのデバイスが測ったか」に紐づける。
class SensorLog(models.Model):

    # 【測定デバイス】
    device = models.ForeignKey(
        "dashboard.Device",
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