from django.db import models

# ==============================
# 日別集計状態管理 (DailySensorAggregationTask)
# ==============================
# センサーデータの日別集計実施の管理を行う。
class DailySensorAggregationTask(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "未処理"
        FAILED = "failed", "失敗"
        COMPLETED = "completed", "完了"

    device = models.ForeignKey(
        "dashboard.Device",
        on_delete=models.PROTECT,
        related_name="daily_sensor_aggregation_tasks",
        verbose_name="デバイス",
    )
    plant = models.ForeignKey(
        "dashboard.Plant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="daily_sensor_aggregation_tasks",
        verbose_name="育成植物",
    )
    summary_date = models.DateField(verbose_name="集計日")

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="処理状態"
    )
    attempt_count = models.PositiveIntegerField(
        default=0,
        verbose_name="試行回数",
    )
    last_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="完了日時",
    )
    last_error = models.TextField(
        blank=True,
        default="",
        verbose_name="最終エラー",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        db_table = "daily_sensor_aggregation_tasks"
        ordering = ["summary_date", "device_id"]
        verbose_name = "日別集計タスク"
        verbose_name_plural = "日別集計タスク"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "plant", "summary_date"],
                condition=models.Q(plant__isnull=False),
                name="uniq_dat_device_plant_date",
            ),
            models.UniqueConstraint(
                fields=["device", "summary_date"],
                condition=models.Q(plant__isnull=True),
                name="uniq_dat_device_date_no_plant",
            ),
        ]

    def __str__(self):
        plant_name = self.plant.custom_name if self.plant_id else "植物未設定"
        return f"{self.summary_date} - {self.device.device_name} - {plant_name}"