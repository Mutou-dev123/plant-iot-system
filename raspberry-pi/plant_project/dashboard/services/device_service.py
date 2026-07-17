# ==========================================
# デバイス管理サービス
# ==========================================

# ESP32デバイスの登録・取得を管理する
#
# ・deviceNameによるデバイス検索
# ・新規デバイス登録
# ・デバイス情報の取得

from dashboard.models import Device

class DeviceService:

    @staticmethod
    def get_or_create(device_name):

        device, created = Device.objects.get_or_create(
            device_name=device_name,

            # デフォルトのデータ取得間隔を300秒に設定
            defaults={
                "interval_seconds": 300
            }
        )

        return device