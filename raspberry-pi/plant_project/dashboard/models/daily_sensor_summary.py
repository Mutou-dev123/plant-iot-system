from django.db import models

# ==============================
# 日別集計 (DailySensorSummary)
# ==============================
# センサーデータの日別集計を行う。
class DailySensorSummary(models.Model):

    device = models.ForeignKey(
        "dashboard.Device",
        on_delete=models.PROTECT,
        related_name="daily_sensor_summaries",
        verbose_name="デバイス",
    )
    plant = models.ForeignKey(
        "dashboard.Plant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="daily_sensor_summaries",
        verbose_name="育成植物",
    )
    summary_date = models.DateField(verbose_name="集計日")

    temperature_avg = models.FloatField(null=True, blank=True, verbose_name="気温平均")
    temperature_max = models.FloatField(null=True, blank=True, verbose_name="気温最大")
    temperature_min = models.FloatField(null=True, blank=True, verbose_name="気温最小")
    temperature_count = models.PositiveIntegerField(default=0, verbose_name="気温有効件数")

    humidity_avg = models.FloatField(null=True, blank=True, verbose_name="湿度平均")
    humidity_max = models.FloatField(null=True, blank=True, verbose_name="湿度最大")
    humidity_min = models.FloatField(null=True, blank=True, verbose_name="湿度最小")
    humidity_count = models.PositiveIntegerField(default=0, verbose_name="湿度有効件数")

    moisture_avg = models.FloatField(null=True, blank=True, verbose_name="土壌水分平均")
    moisture_max = models.FloatField(null=True, blank=True, verbose_name="土壌水分最大")
    moisture_min = models.FloatField(null=True, blank=True, verbose_name="土壌水分最小")
    moisture_count = models.PositiveIntegerField(default=0, verbose_name="土壌水分有効件数")

    light_avg = models.FloatField(null=True, blank=True, verbose_name="光量平均")
    light_max = models.FloatField(null=True, blank=True, verbose_name="光量最大")
    light_min = models.FloatField(null=True, blank=True, verbose_name="光量最小")
    light_count = models.PositiveIntegerField(default=0, verbose_name="光量有効件数")

    log_count = models.PositiveIntegerField(default=0, verbose_name="対象ログ件数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        db_table = "daily_sensor_summaries"
        ordering = ["-summary_date", "device_id"]
        verbose_name = "日別集計"
        verbose_name_plural = "日別集計"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "plant", "summary_date"],
                condition=models.Q(plant__isnull=False),
                name="uniq_dss_device_plant_date",
            ),
            models.UniqueConstraint(
                fields=["device", "summary_date"],
                condition=models.Q(plant__isnull=True),
                name="uniq_dss_device_date_no_plant",
            ),
        ]

    def __str__(self):
        plant_name = self.plant.custom_name if self.plant_id else "植物未設定"
        return f"{self.summary_date} - {self.device.device_name} - {plant_name}"