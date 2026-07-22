from django.db import models
from django.utils import timezone


# ==============================
# 1. 植物マスタ (PlantMaster)
# ==============================
# システムに登録されている植物の図鑑データ。ユーザーが追加することも可能。
# 植物ごとに適切な温度や湿度の情報を記録する
class PlantMaster(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="種類名")
    target_light_score = models.FloatField(default=30000.0, verbose_name="目標日照スコア(1日)")

    # 適正値
    optimal_temp_max = models.FloatField(null=True, blank=True, verbose_name="適正温度(上限)")
    optimal_temp_min = models.FloatField(null=True, blank=True, verbose_name="適正温度(下限)")

    class Meta:
        db_table = 'plant_master'

    def __str__(self):
        return self.name
    

# ==============================
# 2. 育成植物 (MyPlant)
# ==============================
# ユーザーが実際に育てている植物
class MyPlant(models.Model):

    # マスタから種類が消されても、自分の植物データは残るようにする
    plant_master = models.ForeignKey(PlantMaster, on_delete=models.SET_NULL, null=True, verbose_name="ベースとなる植物種類")

    custom_name = models.CharField(max_length=100, default="新しい植物", verbose_name="植物名")
    start_date = models.DateField(default=timezone.now, verbose_name="栽培開始日")

    class Meta:
        db_table = 'my_plant'

    def __str__(self):
        return self.custom_name
    

# ==============================
# 3. デバイス設定 (Device)
# ==============================
# ESP32を一機ごとの設定を管理する。
class Device(models.Model):

    # どの植物に対応しているか
    my_plant = models.ForeignKey(MyPlant, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="観測対象の植物")

    # ESP固有の名称
    device_name = models.CharField(max_length=50, unique=True, verbose_name="デバイス識別名")
    interval_seconds = models.IntegerField(default=300, verbose_name="計測間隔(秒)")

    class Meta:
        db_table = 'device'

    def __str__(self):
        return f"{self.device_name} (間隔: {self.interval_seconds}秒)"
    

# ==============================
# 4. センサーログ (SensorLog)
# ==============================
# 毎回の計測データ。植物ではなく「どのデバイスが測ったか」に紐づける。
class SensorLog(models.Model):

    # デバイスが削除されたら、そのデバイスのログも一緒に消す設定
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name="測定デバイス")

    # ESP32で計測した日時
    measured_at = models.DateTimeField(
        verbose_name="計測日時"
    )

    # Raspberry Piで受信した日時
    received_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="受信日時"
    )

    # --- センサー生データ ---
    soil_raw = models.IntegerField(null=True, blank=True, verbose_name="土壌水分(生)")
    light_raw = models.IntegerField(null=True, blank=True, verbose_name="光量(生)")

    # --- 画面表示用整形済みデータ ---
    moisture = models.FloatField(null=True, blank=True, verbose_name="土壌水分(%)")
    light = models.FloatField(null=True, blank=True, verbose_name="光量スコア(0-100)")
    temperature= models.FloatField(null=True, blank=True, verbose_name="温度(℃)")
    humidity = models.FloatField(null=True, blank=True, verbose_name="湿度(%)")

    class Meta:
        db_table = 'sensor_logs'

    def __str__(self):
        return (
            f"{self.device.device_name}"
            f" - {self.measured_at.strftime('%Y-%m-%d %H:%M')}"
        )