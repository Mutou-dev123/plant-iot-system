# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

# python manage.py inspectdb > dashboard/models.py
# 上記のコマンドで SensorLogs と SystemSettings を自動生成

# センサーログモデル
class SensorLogs(models.Model):
    id = models.AutoField(primary_key=True)

    timestamp = models.TextField()
    moisture = models.FloatField()
    temperature = models.FloatField(blank=True, null=True)
    humidity = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor_logs'

# システム設定モデル
class SystemSettings(models.Model):
    id = models.AutoField(primary_key=True)

    interval_seconds = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'system_settings'
